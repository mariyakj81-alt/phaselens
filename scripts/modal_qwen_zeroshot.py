# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module.
"""Modal class that would run the zero-shot model on one B300.

``python -m scripts.qwen_zeroshot`` refuses a placeholder id before it imports
this module. The local entrypoint below also refuses before any ``.remote``
call. ``Qwen/Qwen3.8-27B`` is allowed. Any other placeholder id still exits
here, before Modal is asked to start the app. ``--help`` on
``scripts.qwen_zeroshot`` does not import this module.

The image spec is not built by importing this file. ``gpu`` is the string from
``qwen_config.GPU`` (``B300``), passed through to ``@app.cls``.
"""

from __future__ import annotations

import importlib.util
import sys
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
GPU = _cfg.GPU

app = modal.App(_cfg.APP_NAME)

# CPU image build. The B300 request is on the class, not on pip_install.
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "torch",
    "transformers",
    "accelerate",
)


@app.cls(
    image=image,
    gpu=GPU,
    timeout=_cfg.TIMEOUT_S,
    startup_timeout=_cfg.STARTUP_TIMEOUT_S,
    memory=_cfg.MEMORY_MIB,
    scaledown_window=_cfg.SCALEDOWN_WINDOW_S,
    max_containers=_cfg.MAX_CONTAINERS,
)
class QwenZeroShot:
    """One warm container. The first call loads weights; later calls reuse them.

    Weight download stays inside ``generate`` so it is covered by the input
    timeout rather than the shorter container startup limit.
    """

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
        self._ensure_model(model_id)
        texts: list[str] = []
        for prompt in prompts:
            try:
                texts.append(self._one(str(prompt), int(max_new_tokens), float(temperature)))
            except Exception as exc:
                # A bad generation becomes unparsed text. The local scorer
                # counts that file wrong and the rest of the batch continues.
                texts.append(f"GENERATION_ERROR: {type(exc).__name__}: {exc}")
        return texts

    def _ensure_model(self, model_id: str) -> None:
        if getattr(self, "_model_id", None) == model_id and getattr(self, "model", None) is not None:
            return
        import torch
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = _load_causal_model(model_id, torch)
        model.eval()
        self.tokenizer = tokenizer
        self.model = model
        self._model_id = model_id

    def _one(self, prompt: str, max_new_tokens: int, temperature: float) -> str:
        import torch

        messages = [{"role": "user", "content": prompt}]
        template_kwargs = {"tokenize": False, "add_generation_prompt": True}
        try:
            rendered = self.tokenizer.apply_chat_template(
                messages,
                enable_thinking=False,
                **template_kwargs,
            )
        except TypeError:
            rendered = self.tokenizer.apply_chat_template(messages, **template_kwargs)
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


@app.local_entrypoint()
def main() -> None:
    """Refuse a placeholder before any remote call.

    Prefer ``python -m scripts.qwen_zeroshot``, which exits before importing
    this module when the model id is still a placeholder.
    """
    cfg = _load_config()
    if cfg.model_id_is_placeholder():
        raise SystemExit(cfg.placeholder_refusal_message())
    repo = str(Path(__file__).resolve().parent.parent)
    sys.path[:] = [repo, *[entry for entry in sys.path if entry != repo]]
    from scripts.qwen_zeroshot import run_modal

    raise SystemExit(run_modal(already_running=True))


# `modal run` imports this module and only then starts the app, which contacts
# the Modal API. A placeholder id exits here, before that. Qwen/Qwen3.8-27B
# does not. `python -m scripts.qwen_zeroshot --help` does not import this file.
if _cfg.model_id_is_placeholder():
    raise SystemExit(_cfg.placeholder_refusal_message())
