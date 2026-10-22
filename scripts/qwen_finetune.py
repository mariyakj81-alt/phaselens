# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.qwen_finetune).
"""Fine-tune Qwen on data/train, then score the adapter on data/test.

One epoch of LoRA supervised fine-tuning on Modal, one B300. Train files are
the 316 canonical spectra in data/train. The prompt is the mode card plus the
peak list. The completion is the gold JSON (position and canonical label, no
source). The test folder is not trained on.

The adapter is kept as the current model only when both test headline
fractions are at least the step 7 fractions. This script still writes both
score files either way.

Run from the repo root::

    py -3.12 -m scripts.qwen_finetune
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.label_norm import canonical_label  # noqa: E402
from scripts.make_prompt import build_prompt, gold_labels, load_card_text  # noqa: E402
from scripts.qwen_config import (  # noqa: E402
    BATCH_SIZE,
    MAX_NEW_TOKENS,
    OUTPUTS_DIR,
    SCORES_JSON,
    TEMPERATURE,
    TRAIN_DIR,
    ZERO_SHOT_MODEL_ID,
    is_test_record,
    model_id_is_placeholder,
    placeholder_refusal_message,
)
from scripts.qwen_zeroshot import _prediction_record, build_test_rows  # noqa: E402
from scripts.score_assignment import load_prediction_jsonl, score_records, write_scores  # noqa: E402
from scripts.score_checked import compare_headlines, load_json  # noqa: E402

STEP7_JSON = OUTPUTS_DIR / "step7_scores.json"
STEP8_SUMMARY = OUTPUTS_DIR / "step8_summary.json"
STEP9_PREDICTIONS = OUTPUTS_DIR / "step9_predictions.jsonl"
STEP9_CHECKED = OUTPUTS_DIR / "step9_checked.jsonl"
STEP9_SCORES = OUTPUTS_DIR / "step9_scores.json"
STEP9_LAYERS = OUTPUTS_DIR / "step9_layers.jsonl"
STEP9_LAYER_SUMMARY = OUTPUTS_DIR / "step9_layer_summary.json"
STEP9_TRAIN = OUTPUTS_DIR / "step9_train_result.json"
STEP9_ADAPTER = OUTPUTS_DIR / "step9_adapter"
EXPECTED_TRAIN = 316
RANKS = (16, 8, 4)
LEARNING_RATE = 1e-4
EPOCHS = 1


def _completion(spectrum: dict) -> str:
    rows = []
    for item in gold_labels(spectrum):
        position = item.get("position_cm-1")
        label = item.get("label")
        if position is None or label is None:
            continue
        rows.append({"position_cm-1": position, "label": canonical_label(str(label))})
    return json.dumps(rows, ensure_ascii=False, indent=2)


def build_train_examples(train_dir: Path = TRAIN_DIR) -> list[dict]:
    if not train_dir.is_dir():
        raise SystemExit(f"train directory not found: {train_dir}")
    paths = sorted(path for path in train_dir.glob("*.json") if path.is_file() and " " not in path.name)
    examples = []
    for path in paths:
        spectrum = json.loads(path.read_text(encoding="utf-8"))
        context = spectrum.get("context") if isinstance(spectrum.get("context"), dict) else {}
        if is_test_record(context.get("material"), context.get("mode_card"), context.get("laser_nm")):
            raise SystemExit(f"refusing to train on held-out file {path.name}")
        prompt = build_prompt(spectrum, load_card_text(context.get("mode_card")))
        for forbidden in ("answers", "known_artifact", "shift_cm-1"):
            if forbidden in prompt:
                raise SystemExit(f"{path.name} prompt contains {forbidden!r}")
        examples.append({"file": path.name, "prompt": prompt, "completion": _completion(spectrum)})
    if len(examples) != EXPECTED_TRAIN:
        raise SystemExit(f"expected {EXPECTED_TRAIN} train files, found {len(examples)}")
    return examples


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
    temporary.replace(path)


def _is_oom(exc: BaseException) -> bool:
    text = f"{type(exc).__name__}: {exc}".lower()
    return "out of memory" in text or "outofmemory" in text


def _usable_prediction(record: dict) -> bool:
    text = record.get("raw_model_text")
    return isinstance(text, str) and bool(text) and not text.startswith("GENERATION_ERROR")


def _already_scored() -> bool:
    if not STEP9_SCORES.is_file() or not STEP9_TRAIN.is_file():
        return False
    scores = load_json(STEP9_SCORES)
    trained = load_json(STEP9_TRAIN)
    step9 = scores.get("step9")
    if not trained.get("completed") or not isinstance(step9, dict):
        return False
    headline = step9.get("headline")
    return isinstance(headline, dict) and "mode_exact" in headline and "artifact_exact" in headline


def _run_module(module: str, extra: list[str]) -> None:
    command = [sys.executable, "-m", module, *extra]
    print(" ".join(command), flush=True)
    completed = subprocess.run(command, cwd=str(_REPO_ROOT), check=False)
    if completed.returncode != 0:
        raise SystemExit(f"{module} exited {completed.returncode}")


def _download_adapter() -> str | None:
    """Copy the adapter off the volume when the CLI can do it. None if it stays remote."""
    if STEP9_ADAPTER.exists() and any(STEP9_ADAPTER.iterdir()):
        return str(STEP9_ADAPTER.relative_to(_REPO_ROOT)).replace("\\", "/")
    STEP9_ADAPTER.mkdir(parents=True, exist_ok=True)
    command = [
        "modal",
        "volume",
        "get",
        "--force",
        "phaselens-qwen-adapter",
        "adapter",
        str(STEP9_ADAPTER),
    ]
    print(" ".join(command), flush=True)
    completed = subprocess.run(command, cwd=str(_REPO_ROOT), check=False)
    if completed.returncode != 0:
        print("adapter download failed; weights remain on Modal volume phaselens-qwen-adapter", flush=True)
        return None
    return str(STEP9_ADAPTER.relative_to(_REPO_ROOT)).replace("\\", "/")


def _train(examples: list[dict], *, retrain: bool = False) -> dict:
    from scripts.modal_qwen_finetune import app, QwenFineTune

    with app.run():
        status = QwenFineTune().train_status.remote()
    if not retrain and isinstance(status, dict) and status.get("completed"):
        print(f"adapter already trained at rank {status.get('rank')}; not starting another run", flush=True)
        _write_json(STEP9_TRAIN, status)
        return status
    last_error = "training did not start"
    for rank in RANKS:
        print(f"starting LoRA rank {rank}", flush=True)
        try:
            with app.run():
                status = QwenFineTune().train.remote(
                    examples,
                    ZERO_SHOT_MODEL_ID,
                    rank,
                    LEARNING_RATE,
                    EPOCHS,
                )
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(last_error, flush=True)
            if _is_oom(exc) and rank != RANKS[-1]:
                print(f"out of memory at rank {rank}; retrying at a lower rank", flush=True)
                continue
            _write_json(STEP9_TRAIN, {"completed": False, "error": last_error, "rank": rank})
            raise SystemExit(last_error) from exc
        if isinstance(status, dict) and status.get("completed"):
            _write_json(STEP9_TRAIN, status)
            print(f"train loss {status.get('train_loss')}", flush=True)
            return status
        last_error = json.dumps(status, ensure_ascii=False) if isinstance(status, dict) else str(status)
        print(last_error, flush=True)
        if rank == RANKS[-1]:
            break
    payload = {"completed": False, "error": last_error}
    _write_json(STEP9_TRAIN, payload)
    raise SystemExit(last_error)


def _generate_test(rows: list[dict]) -> None:
    from scripts.modal_qwen_finetune import app, QwenFineTune

    existing: dict[str, dict] = {}
    if STEP9_PREDICTIONS.is_file():
        for record in load_prediction_jsonl(STEP9_PREDICTIONS):
            name = record.get("file")
            if isinstance(name, str) and _usable_prediction(record):
                existing[name] = record
    todo = [row for row in rows if row["file"] not in existing]
    print(f"test generate {len(todo)} remaining, {len(existing)} already saved", flush=True)
    if not todo:
        ordered = [existing[row["file"]] for row in rows]
        _write_jsonl(STEP9_PREDICTIONS, ordered)
        return
    with app.run():
        worker = QwenFineTune()
        step = max(1, BATCH_SIZE)
        for start in range(0, len(todo), step):
            batch = todo[start : start + step]
            texts = worker.generate.remote(
                [row["prompt"] for row in batch],
                ZERO_SHOT_MODEL_ID,
                MAX_NEW_TOKENS,
                TEMPERATURE,
            )
            if not isinstance(texts, list) or len(texts) != len(batch):
                raise SystemExit(f"fine-tuned model returned an unexpected batch at {batch[0]['file']}")
            for row, text in zip(batch, texts):
                existing[row["file"]] = _prediction_record(row, text if isinstance(text, str) else str(text))
            ordered = [existing[row["file"]] for row in rows if row["file"] in existing]
            _write_jsonl(STEP9_PREDICTIONS, ordered)
            print(f"test predictions {len(ordered)}/{len(rows)}", flush=True)
    missing = [row["file"] for row in rows if row["file"] not in existing]
    if missing:
        raise SystemExit(f"missing test predictions, first {missing[0]}")
    _write_jsonl(STEP9_PREDICTIONS, [existing[row["file"]] for row in rows])


def _write_step9_scores(train_result: dict, adapter_local: str | None) -> dict:
    if not STEP7_JSON.is_file():
        raise SystemExit(f"step 7 scores not found: {STEP7_JSON}")
    records = load_prediction_jsonl(STEP9_CHECKED)
    if len(records) != 184:
        raise SystemExit(f"step 9 checked file has {len(records)} lines, expected 184")
    step9 = score_records(records)
    step5 = load_json(SCORES_JSON)
    step7_payload = load_json(STEP7_JSON)
    step7 = step7_payload.get("step7")
    if not isinstance(step7, dict):
        raise SystemExit("step 7 scores file has no step7 object")
    comparison = compare_headlines(step9, step7)
    layer_summary = load_json(STEP9_LAYER_SUMMARY) if STEP9_LAYER_SUMMARY.is_file() else None
    step8_summary = load_json(STEP8_SUMMARY) if STEP8_SUMMARY.is_file() else None
    kept = comparison["both_greater_or_equal"]
    payload = {
        "headline_split": "test",
        "step5": step5,
        "step7": step7,
        "step9": step9,
        "comparison_step9_vs_step7": comparison,
        "step8_layer": step8_summary,
        "step9_layer": layer_summary,
        "fine_tune": {
            "kept": kept,
            "beat_step7_on_both": comparison["both_strictly_greater"],
            "current_model": (
                "fine-tuned LoRA adapter"
                if kept
                else "step 7 zero-shot Qwen plus the checker"
            ),
            "hyperparameters": train_result,
            "adapter_volume": "phaselens-qwen-adapter",
            "adapter_remote_path": "/adapter",
            "adapter_local": adapter_local,
        },
        "notes": (
            "Headline is the test set. step9 scores the fine-tuned model after the same "
            "checker loop used in step 6 (one retry, failures left unassigned). "
            "The adapter is the current model only when both test headline fractions "
            "are greater than or equal to step 7."
        ),
    }
    write_scores(payload, STEP9_SCORES)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LoRA fine-tune Qwen on data/train and score data/test.")
    parser.add_argument(
        "--retrain",
        action="store_true",
        help="Train again even if step 9 already scored. Replaces step 9 prediction, check, layer, and score files.",
    )
    args = parser.parse_args(argv)
    if model_id_is_placeholder():
        print(placeholder_refusal_message(), file=sys.stderr)
        return 1
    if not args.retrain and _already_scored():
        print("step 9 already trained and scored; not starting another training run", flush=True)
        print(f"scores {STEP9_SCORES}", flush=True)
        print("Pass --retrain to train again. That replaces the step 9 prediction and score files.", flush=True)
        return 0
    if not STEP7_JSON.is_file():
        raise SystemExit(f"step 7 scores not found: {STEP7_JSON}. Run the checker and score_checked first.")
    examples = build_train_examples()
    print(f"train examples {len(examples)}", flush=True)
    train_result = _train(examples, retrain=args.retrain)
    if args.retrain:
        for path in (STEP9_PREDICTIONS, STEP9_CHECKED, STEP9_LAYERS, STEP9_LAYER_SUMMARY):
            if path.is_file():
                path.unlink()
    rows = build_test_rows()
    if len(rows) != 184:
        raise SystemExit(f"expected 184 test prompts, found {len(rows)}")
    _generate_test(rows)
    _run_module(
        "scripts.run_checker",
        [
            "--predictions",
            str(STEP9_PREDICTIONS),
            "--output",
            str(STEP9_CHECKED),
            "--backend",
            "finetuned",
        ],
    )
    _run_module(
        "scripts.layer_readout",
        [
            "--checked",
            str(STEP9_CHECKED),
            "--jsonl",
            str(STEP9_LAYERS),
            "--summary",
            str(STEP9_LAYER_SUMMARY),
        ],
    )
    adapter_local = _download_adapter()
    payload = _write_step9_scores(train_result, adapter_local)
    comparison = payload["comparison_step9_vs_step7"]
    print(
        "step9 vs step7 "
        f"mode {comparison['mode_exact_fraction_new']} vs {comparison['mode_exact_fraction_old']} "
        f"artifact {comparison['artifact_exact_fraction_new']} vs {comparison['artifact_exact_fraction_old']}",
        flush=True,
    )
    print(f"current model: {payload['fine_tune']['current_model']}", flush=True)
    print(f"wrote {STEP9_SCORES}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
