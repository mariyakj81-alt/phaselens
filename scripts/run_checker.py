# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.run_checker).
"""Run the checker on prediction JSONL and retry each failure once on Modal.

Step 6 reads ``outputs/step5_predictions.jsonl``, checks every test file, and
writes ``outputs/step6_checked.jsonl``. Files that already passed, and files
whose one retry already finished, are left as they are so a crashed retry
does not call the model again for them.

The checker sees peaks, the mode card, and context metadata. It does not see
gold answers. Gold is copied from the prediction line only so the scorer can
join later.

``--audit`` counts failures and does not call Modal or write the output.

Run from the repo root::

    py -3.12 -m scripts.run_checker --audit
    py -3.12 -m scripts.run_checker
    py -3.12 -m scripts.run_checker --predictions outputs/step9_predictions.jsonl --output outputs/step9_checked.jsonl --backend finetuned
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.checker import check_assignment, retry_prompt, rules_for  # noqa: E402
from scripts.make_prompt import build_prompt, load_card_text  # noqa: E402
from scripts.qwen_config import (  # noqa: E402
    BATCH_SIZE,
    MAX_NEW_TOKENS,
    PREDICTIONS_JSONL,
    TEMPERATURE,
    TEST_DIR,
    ZERO_SHOT_MODEL_ID,
    model_id_is_placeholder,
    placeholder_refusal_message,
)
from scripts.qwen_zeroshot import coerce_parsed_labels, parse_model_output  # noqa: E402
from scripts.score_assignment import load_prediction_jsonl  # noqa: E402

CHECKED_JSONL = _REPO_ROOT / "outputs" / "step6_checked.jsonl"


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
    temporary.replace(path)


def _load_finished(path: Path) -> dict[str, dict]:
    if not path.is_file():
        return {}
    finished: dict[str, dict] = {}
    for record in load_prediction_jsonl(path):
        name = record.get("file")
        if not isinstance(name, str):
            continue
        if record.get("checker_passed") is True or record.get("retry") is True:
            finished[name] = record
    return finished


def _load_spectrum(path: Path) -> dict:
    spectrum = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(spectrum, dict):
        raise SystemExit(f"{path.name} is not a JSON object")
    # Gold answers must not be available to the checker or the retry prompt.
    spectrum.pop("answers", None)
    spectrum.pop("spectrum", None)
    return spectrum


def _context_and_peaks(spectrum: dict) -> tuple[dict, list]:
    context = spectrum.get("context") if isinstance(spectrum.get("context"), dict) else {}
    peaks = spectrum.get("peaks") if isinstance(spectrum.get("peaks"), list) else []
    return context, peaks


def _base_fields(prediction: dict, context: dict) -> dict:
    gold = prediction.get("gold")
    if not isinstance(gold, list):
        raise SystemExit(f"{prediction.get('file')} prediction has no gold list")
    return {
        "file": prediction.get("file"),
        "material": context.get("material"),
        "laser_nm": context.get("laser_nm"),
        "layer": context.get("layer"),
        "mode_card": context.get("mode_card"),
        "gold": gold,
    }


def _checked_record(
    base: dict,
    *,
    raw_model_text: str,
    raw_model_text_retry: str | None,
    parsed_labels_first,
    parsed_labels_retry,
    parsed_labels: list,
    checker_reasons: list[str],
    checker_reasons_after_retry: list[str],
    retry: bool,
    checker_passed: bool,
) -> dict:
    return {
        **base,
        "raw_model_text": raw_model_text,
        "raw_model_text_retry": raw_model_text_retry,
        "parsed_labels_first": parsed_labels_first,
        "parsed_labels_retry": parsed_labels_retry,
        "parsed_labels": parsed_labels,
        "checker_reasons": checker_reasons,
        "checker_reasons_after_retry": checker_reasons_after_retry,
        "retry": retry,
        "checker_passed": checker_passed,
    }


def _generate(prompts: list[str], backend: str, on_batch=None) -> list[str]:
    if not prompts:
        return []
    if model_id_is_placeholder():
        raise SystemExit(placeholder_refusal_message())
    if backend == "zeroshot":
        from scripts.modal_qwen_zeroshot import app, QwenZeroShot

        worker_cls = QwenZeroShot
    elif backend == "finetuned":
        from scripts.modal_qwen_finetune import app, QwenFineTune

        worker_cls = QwenFineTune
    else:
        raise SystemExit(f"unknown backend {backend!r}")
    texts: list[str] = []
    with app.run():
        worker = worker_cls()
        step = max(1, BATCH_SIZE)
        for start in range(0, len(prompts), step):
            batch = prompts[start : start + step]
            got = worker.generate.remote(batch, ZERO_SHOT_MODEL_ID, MAX_NEW_TOKENS, TEMPERATURE)
            if not isinstance(got, list) or len(got) != len(batch):
                raise RuntimeError(
                    f"model returned {len(got) if isinstance(got, list) else type(got)} texts for {len(batch)} prompts"
                )
            chunk = [text if isinstance(text, str) else str(text) for text in got]
            texts.extend(chunk)
            if on_batch is not None:
                on_batch(start, chunk)
            print(f"modal retry {len(texts)}/{len(prompts)}", flush=True)
    return texts


def run(
    predictions_path: Path,
    output_path: Path,
    *,
    backend: str = "zeroshot",
    test_dir: Path = TEST_DIR,
    audit_only: bool = False,
) -> int:
    if output_path.resolve() == PREDICTIONS_JSONL.resolve():
        raise SystemExit("refusing to overwrite step 5 predictions")
    if output_path.resolve() == predictions_path.resolve():
        raise SystemExit("refusing to overwrite the input predictions")
    predictions = load_prediction_jsonl(predictions_path)
    if len(predictions) != 184 and predictions_path.resolve() == PREDICTIONS_JSONL.resolve():
        raise SystemExit(f"step 5 predictions have {len(predictions)} lines, expected 184. Not rerunning zero-shot.")
    finished = {} if audit_only else _load_finished(output_path)
    order = [record.get("file") for record in predictions]
    pending_retry: list[dict] = []
    results: dict[str, dict] = dict(finished)
    n_pass = 0
    n_cached = 0
    n_fail = 0

    for prediction in predictions:
        name = prediction.get("file")
        if not isinstance(name, str):
            raise SystemExit("a prediction line has no file name")
        if name in finished:
            n_cached += 1
            continue
        spectrum_path = test_dir / name
        if not spectrum_path.is_file():
            raise SystemExit(f"test spectrum not found: {spectrum_path}")
        spectrum = _load_spectrum(spectrum_path)
        context, peaks = _context_and_peaks(spectrum)
        rules = rules_for(context.get("mode_card"))
        first_parsed = prediction.get("parsed_labels")
        if not isinstance(first_parsed, list):
            first_parsed = None
        outcome = check_assignment(peaks, first_parsed, rules, context)
        base = _base_fields(prediction, context)
        raw_text = prediction.get("raw_model_text")
        if not isinstance(raw_text, str):
            raw_text = "" if raw_text is None else str(raw_text)
        if outcome.passed:
            n_pass += 1
            if audit_only:
                continue
            results[name] = _checked_record(
                base,
                raw_model_text=raw_text,
                raw_model_text_retry=None,
                parsed_labels_first=first_parsed,
                parsed_labels_retry=None,
                parsed_labels=outcome.adjusted_labels,
                checker_reasons=[],
                checker_reasons_after_retry=[],
                retry=False,
                checker_passed=True,
            )
            continue
        n_fail += 1
        prompt = build_prompt(spectrum, load_card_text(context.get("mode_card")))
        pending_retry.append(
            {
                "base": base,
                "raw_model_text": raw_text,
                "parsed_labels_first": first_parsed,
                "checker_reasons": outcome.reasons,
                "prompt": retry_prompt(prompt, outcome.reasons),
                "peaks": peaks,
                "context": context,
            }
        )

    print(
        f"checker pass {n_pass + n_cached} fail {n_fail} cached {n_cached} of {len(predictions)}",
        flush=True,
    )
    if audit_only:
        shown = 0
        for item in pending_retry:
            if shown >= 12:
                break
            print(f"{item['base']['file']}: {item['checker_reasons'][0]}", flush=True)
            shown += 1
        return 0

    if n_pass:
        _write_jsonl(output_path, [results[name] for name in order if name in results])

    if pending_retry:

        def _store_batch(start: int, chunk: list[str]) -> None:
            for item, text in zip(pending_retry[start : start + len(chunk)], chunk):
                parsed_retry = coerce_parsed_labels(parse_model_output(text))
                rules = rules_for(item["context"].get("mode_card"))
                outcome = check_assignment(item["peaks"], parsed_retry, rules, item["context"])
                # Peaks that still fail stay "unassigned". Peaks that pass keep
                # the retry label. Do not copy a mode the checker rejected.
                results[item["base"]["file"]] = _checked_record(
                    item["base"],
                    raw_model_text=item["raw_model_text"],
                    raw_model_text_retry=text,
                    parsed_labels_first=item["parsed_labels_first"],
                    parsed_labels_retry=parsed_retry,
                    parsed_labels=outcome.adjusted_labels,
                    checker_reasons=item["checker_reasons"],
                    checker_reasons_after_retry=outcome.reasons,
                    retry=True,
                    checker_passed=outcome.passed,
                )
            _write_jsonl(output_path, [results[name] for name in order if name in results])

        _generate([item["prompt"] for item in pending_retry], backend, on_batch=_store_batch)

    missing = [name for name in order if name not in results]
    if missing:
        raise SystemExit(f"checker did not finish {len(missing)} files, first {missing[0]}")
    _write_jsonl(output_path, [results[name] for name in order])
    n_retry = sum(1 for name in order if results[name].get("retry"))
    n_still = sum(1 for name in order if not results[name].get("checker_passed"))
    print(f"wrote {output_path}", flush=True)
    print(f"retries {n_retry} still_failing {n_still}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check assignments and retry each failure once on Modal.")
    parser.add_argument("--predictions", type=Path, default=PREDICTIONS_JSONL)
    parser.add_argument("--output", type=Path, default=CHECKED_JSONL)
    parser.add_argument("--test-dir", type=Path, default=TEST_DIR)
    parser.add_argument(
        "--backend",
        choices=("zeroshot", "finetuned"),
        default="zeroshot",
        help="zeroshot calls Qwen/Qwen3.8-27B. finetuned calls the LoRA adapter on the Modal volume.",
    )
    parser.add_argument("--audit", action="store_true", help="Count failures. Do not call Modal or write output.")
    args = parser.parse_args(argv)
    return run(
        args.predictions,
        args.output,
        backend=args.backend,
        test_dir=args.test_dir,
        audit_only=args.audit,
    )


if __name__ == "__main__":
    raise SystemExit(main())
