# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module.
"""LoRA supervised fine-tune of Qwen/Qwen3.8-27B on one Modal B300.

Prompt-completion SFT for one epoch. The base weights stay frozen. The adapter
is written to the Modal volume ``phaselens-qwen-adapter`` at ``/adapter``.

Importing this module contacts Modal to declare the volume. The local
orchestrator is ``python -m scripts.qwen_finetune``.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import modal


def _load_config():
    path = Path(__file__).resolve().parent / "qwen_config.py"
    spec = importlib.util.spec_from_file_location("phaselens_qwen_config_file", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cfg = _load_config()

APP_NAME = "phaselens-qwen-finetune"
VOLUME_NAME = "phaselens-qwen-adapter"
ADAPTER_DIR = "/vol/adapter"
CACHE_DIR = "/vol/hf"
MAX_SEQ_CAP = 32768

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch",
    "transformers",
    "accelerate",
    "peft",
).env(
    {
        "HF_HOME": CACHE_DIR,
        "HF_HUB_CACHE": CACHE_DIR + "/hub",
        "TOKENIZERS_PARALLELISM": "false",
        "WANDB_DISABLED": "true",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    }
)


def _from_pretrained(cls, model_id: str, torch_module):
    try:
        return cls.from_pretrained(model_id, dtype=torch_module.bfloat16, device_map="auto")
    except TypeError:
        return cls.from_pretrained(model_id, torch_dtype=torch_module.bfloat16, device_map="auto")


def _load_causal_model(model_id: str, torch_module):
    import transformers

    errors: list[str] = []
    for cls_name in ("AutoModelForCausalLM", "AutoModelForImageTextToText"):
        cls = getattr(transformers, cls_name, None)
        if cls is None:
            errors.append(f"{cls_name}: not in this transformers build")
            continue
        try:
            return _from_pretrained(cls, model_id, torch_module)
        except Exception as exc:
            errors.append(f"{cls_name}: {type(exc).__name__}: {exc}")
    raise RuntimeError("could not load model\n" + "\n".join(errors))


def _render(tokenizer, messages: list[dict], add_generation_prompt: bool) -> str:
    kwargs = {"tokenize": False, "add_generation_prompt": add_generation_prompt}
    try:
        return tokenizer.apply_chat_template(messages, enable_thinking=False, **kwargs)
    except TypeError:
        return tokenizer.apply_chat_template(messages, **kwargs)


def _find_completion_start(full_ids: list[int], completion_ids: list[int]) -> int | None:
    if not completion_ids or len(full_ids) < len(completion_ids):
        return None
    width = len(completion_ids)
    start = None
    last = len(full_ids) - width
    for index in range(last + 1):
        if full_ids[index : index + width] == completion_ids:
            start = index
    return start


def _tokenize_pair(tokenizer, prompt: str, completion: str, cap: int) -> dict | None:
    messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": completion}]
    full_text = _render(tokenizer, messages, add_generation_prompt=False)
    full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
    completion_ids = tokenizer(completion, add_special_tokens=False)["input_ids"]
    truncated = False
    if len(full_ids) > cap:
        full_ids = full_ids[-cap:]
        truncated = True
    start = _find_completion_start(full_ids, completion_ids)
    if start is None:
        return None
    labels = list(full_ids)
    for index in range(start):
        labels[index] = -100
    if all(label == -100 for label in labels):
        return None
    return {
        "input_ids": full_ids,
        "attention_mask": [1] * len(full_ids),
        "labels": labels,
        "truncated": truncated,
        "length": len(full_ids),
    }


def _target_modules(model) -> list[str]:
    names = {module_name.split(".")[-1] for module_name, _ in model.named_modules()}
    wanted = [name for name in ("q_proj", "k_proj", "v_proj", "o_proj") if name in names]
    if wanted:
        return wanted
    raise RuntimeError("no attention LoRA modules found on this model")


@app.cls(
    image=image,
    gpu=_cfg.GPU,
    timeout=21600,
    startup_timeout=_cfg.STARTUP_TIMEOUT_S,
    memory=_cfg.MEMORY_MIB,
    scaledown_window=_cfg.SCALEDOWN_WINDOW_S,
    max_containers=_cfg.MAX_CONTAINERS,
    volumes={"/vol": volume},
)
class QwenFineTune:
    """One warm container. Train writes the adapter; generate reloads it."""

    @modal.method()
    def train_status(self) -> dict | None:
        volume.reload()
        path = Path(ADAPTER_DIR) / "phaselens_train.json"
        if not path.is_file():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None

    @modal.method()
    def train(
        self,
        examples: list[dict],
        model_id: str,
        rank: int,
        learning_rate: float,
        epochs: int,
    ) -> dict:
        import torch
        from peft import LoraConfig, TaskType, get_peft_model
        from torch.utils.data import Dataset
        from transformers import AutoTokenizer, Trainer, TrainingArguments

        if not isinstance(examples, list) or not examples:
            raise ValueError("examples must be a non-empty list")
        Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        rows = []
        skipped = 0
        truncated = 0
        lengths: list[int] = []
        for example in examples:
            prompt = example.get("prompt")
            completion = example.get("completion")
            if not isinstance(prompt, str) or not isinstance(completion, str):
                skipped += 1
                continue
            tokenized = _tokenize_pair(tokenizer, prompt, completion, MAX_SEQ_CAP)
            if tokenized is None:
                skipped += 1
                continue
            if tokenized.pop("truncated"):
                truncated += 1
            lengths.append(int(tokenized.pop("length")))
            rows.append(tokenized)
        if not rows:
            raise RuntimeError("every training example was skipped during tokenization")
        print(
            f"train examples {len(rows)} skipped {skipped} truncated {truncated} "
            f"tokens min {min(lengths)} max {max(lengths)}",
            flush=True,
        )
        try:
            volume.commit()
            print("committed tokenizer cache", flush=True)
        except Exception as exc:
            print(f"tokenizer cache commit failed: {type(exc).__name__}: {exc}", flush=True)

        model = _load_causal_model(model_id, torch)
        model.config.use_cache = False
        try:
            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        except TypeError:
            model.gradient_checkpointing_enable()
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
        targets = _target_modules(model)
        lora = LoraConfig(
            r=int(rank),
            lora_alpha=int(rank) * 2,
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=targets,
        )
        model = get_peft_model(model, lora)
        if hasattr(model, "print_trainable_parameters"):
            model.print_trainable_parameters()
        try:
            volume.commit()
            print("committed weight cache", flush=True)
        except Exception as exc:
            print(f"weight cache commit failed: {type(exc).__name__}: {exc}", flush=True)

        class _Rows(Dataset):
            def __init__(self, items: list[dict]):
                self.items = items

            def __len__(self) -> int:
                return len(self.items)

            def __getitem__(self, index: int) -> dict:
                return self.items[index]

        def _collate(features: list[dict]) -> dict:
            return {
                "input_ids": torch.tensor([features[0]["input_ids"]], dtype=torch.long),
                "attention_mask": torch.tensor([features[0]["attention_mask"]], dtype=torch.long),
                "labels": torch.tensor([features[0]["labels"]], dtype=torch.long),
            }

        arg_kwargs = {
            "output_dir": "/tmp/phaselens-lora",
            "per_device_train_batch_size": 1,
            "gradient_accumulation_steps": 4,
            "num_train_epochs": float(epochs),
            "learning_rate": float(learning_rate),
            "lr_scheduler_type": "cosine",
            "warmup_ratio": 0.03,
            "bf16": True,
            "gradient_checkpointing": True,
            "gradient_checkpointing_kwargs": {"use_reentrant": False},
            "logging_steps": 10,
            "logging_first_step": True,
            "save_strategy": "no",
            "report_to": "none",
            "remove_unused_columns": False,
            "optim": "adamw_torch",
            "max_grad_norm": 1.0,
            "dataloader_num_workers": 0,
            "dataloader_pin_memory": False,
            "seed": 0,
        }
        dropped: list[str] = []
        while True:
            try:
                args = TrainingArguments(**arg_kwargs)
                break
            except TypeError as exc:
                message = str(exc)
                marker = "unexpected keyword argument "
                if marker not in message:
                    raise
                name = message.split(marker, 1)[1].strip().strip("'\"")
                if name not in arg_kwargs:
                    raise
                arg_kwargs.pop(name)
                dropped.append(name)
                if name == "warmup_ratio":
                    arg_kwargs["warmup_steps"] = 8
                if len(dropped) > 12:
                    raise
        if dropped:
            print("TrainingArguments dropped " + ", ".join(dropped), flush=True)
        trainer_kwargs = {
            "model": model,
            "args": args,
            "train_dataset": _Rows(rows),
            "data_collator": _collate,
        }
        try:
            trainer = Trainer(**trainer_kwargs, processing_class=tokenizer)
        except TypeError:
            trainer = Trainer(**trainer_kwargs, tokenizer=tokenizer)
        trained = trainer.train()
        loss = float(getattr(trained, "training_loss", 0.0))
        adapter_path = Path(ADAPTER_DIR)
        if adapter_path.exists():
            for child in adapter_path.iterdir():
                if child.is_file():
                    child.unlink()
        adapter_path.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(ADAPTER_DIR)
        tokenizer.save_pretrained(ADAPTER_DIR)
        summary = {
            "completed": True,
            "method": "lora_sft",
            "model_id": model_id,
            "gpu": _cfg.GPU,
            "max_containers": _cfg.MAX_CONTAINERS,
            "app_name": APP_NAME,
            "adapter_volume": VOLUME_NAME,
            "adapter_remote_path": ADAPTER_DIR,
            "rank": int(rank),
            "lora_alpha": int(rank) * 2,
            "lora_dropout": 0.05,
            "target_modules": targets,
            "epochs": int(epochs),
            "learning_rate": float(learning_rate),
            "batch_size": 1,
            "gradient_accumulation_steps": 4,
            "effective_batch_size": 4,
            "max_seq_cap": MAX_SEQ_CAP,
            "n_examples": len(rows),
            "n_skipped": skipped,
            "n_truncated": truncated,
            "tokens_min": min(lengths),
            "tokens_max": max(lengths),
            "train_loss": loss,
            "gradient_checkpointing": True,
        }
        (adapter_path / "phaselens_train.json").write_text(
            json.dumps(summary, indent=2) + "\n",
            encoding="utf-8",
        )
        volume.commit()
        print(f"adapter saved rank {rank} loss {loss:.6f}", flush=True)
        return summary

    @modal.method()
    def generate(
        self,
        prompts: list[str],
        model_id: str,
        max_new_tokens: int,
        temperature: float,
    ) -> list[str]:
        if not isinstance(prompts, list):
            raise TypeError("prompts must be a list")
        volume.reload()
        self._ensure_model(model_id)
        texts: list[str] = []
        for prompt in prompts:
            try:
                texts.append(self._one(str(prompt), int(max_new_tokens), float(temperature)))
            except Exception as exc:
                texts.append(f"GENERATION_ERROR: {type(exc).__name__}: {exc}")
        return texts

    def _ensure_model(self, model_id: str) -> None:
        if getattr(self, "_model_id", None) == model_id and getattr(self, "model", None) is not None:
            return
        Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
        adapter = Path(ADAPTER_DIR) / "adapter_config.json"
        if not adapter.is_file():
            raise RuntimeError(f"adapter not found at {ADAPTER_DIR}")
        import torch
        from peft import PeftModel
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        base = _load_causal_model(model_id, torch)
        model = PeftModel.from_pretrained(base, ADAPTER_DIR)
        model.eval()
        self.tokenizer = tokenizer
        self.model = model
        self._model_id = model_id

    def _one(self, prompt: str, max_new_tokens: int, temperature: float) -> str:
        import torch

        messages = [{"role": "user", "content": prompt}]
        rendered = _render(self.tokenizer, messages, add_generation_prompt=True)
        inputs = self.tokenizer(rendered, return_tensors="pt")
        inputs = {key: value.to("cuda") for key, value in inputs.items()}
        generate_kwargs = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
        }
        if temperature > 0:
            generate_kwargs["temperature"] = temperature
        with torch.inference_mode():
            output = self.model.generate(**inputs, **generate_kwargs)
        new_tokens = output[0, inputs["input_ids"].shape[1] :]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)
