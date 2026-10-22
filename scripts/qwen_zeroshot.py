# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.qwen_zeroshot).
"""Zero-shot Qwen assignment on the test split.

``--prepare-only`` (alias ``--local-dry-run``) writes
``outputs/step5_prompts.jsonl`` with the prompt and gold for every test file
and does not import Modal or call a model.

The launch path refuses while ``ZERO_SHOT_MODEL_ID`` is a placeholder, before
importing Modal. ``Qwen/Qwen3.8-27B`` is not a placeholder, so a run without
``--prepare-only`` imports Modal and calls the B300 class in
``scripts/modal_qwen_zeroshot.py``. That writes
``outputs/step5_predictions.jsonl`` and scores it to
``outputs/step5_scores.json``. ``--help`` and ``--prepare-only`` do not
import Modal.

Prediction lines use the schema documented in ``scripts/score_assignment.py``.

Run from the repo root::

    python -m scripts.qwen_zeroshot --prepare-only
    python -m scripts.qwen_zeroshot
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# File execution puts the scripts directory on sys.path[0]. Insert the repo
# root (the parent of scripts) before importing sibling modules so
# `import scripts` works from any working directory.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.make_prompt import INSTRUCTION, build_prompt, gold_labels, load_card_text  # noqa: E402
from scripts.qwen_config import (  # noqa: E402
    BATCH_SIZE,
    MAX_NEW_TOKENS,
    PREDICTIONS_JSONL,
    PROMPTS_JSONL,
    SCORES_JSON,
    TEMPERATURE,
    TEST_DIR,
    ZERO_SHOT_MODEL_ID,
    model_id_is_placeholder,
    placeholder_refusal_message,
)
from scripts.score_assignment import (  # noqa: E402
    format_headline,
    label_of,
    position_of,
    score_records,
    write_scores,
)

# Prompt text must not carry these. ``shift_cm-1`` is the spectrum column.
_FORBIDDEN_IN_PROMPT = ("answers", "known_artifact", "shift_cm-1")
_WRAPPER_KEYS = ("assignments", "peaks", "labels", "predictions", "result")


def strip_fences(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _loads_or_none(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _unwrap_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in _WRAPPER_KEYS:
            inner = value.get(key)
            if isinstance(inner, list):
                return inner
    return None


def parse_model_output(text: str | None):
    """Return a JSON list from model text, or None.

    Fences are stripped. If the whole text is not JSON, the last decodable
    JSON list in the text is used so a reasoning preface does not hide the
    answer. There is no index alignment: items still need ``position_cm-1``.
    """
    if not isinstance(text, str) or not text.strip():
        return None
    stripped = strip_fences(text)
    loaded = _loads_or_none(stripped)
    if loaded is None and stripped != text.strip():
        loaded = _loads_or_none(text.strip())
    if loaded is not None:
        return _unwrap_list(loaded)
    decoder = json.JSONDecoder()
    last = None
    index = 0
    while True:
        start = stripped.find("[", index)
        if start < 0:
            break
        try:
            value, end = decoder.raw_decode(stripped, start)
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(value, list):
            last = value
        index = max(end, start + 1)
    return last


def coerce_parsed_labels(parsed) -> list | None:
    if not isinstance(parsed, list):
        return None
    labels = []
    for item in parsed:
        position = position_of(item)
        label = label_of(item)
        if position is None or label is None:
            continue
        labels.append({"position_cm-1": position, "label": label})
    return labels


def parser_self_test() -> list[str]:
    failures: list[str] = []

    fenced = '```json\n[{"position_cm-1": 1.5, "label": "Eg"}]\n```'
    fenced_labels = coerce_parsed_labels(parse_model_output(fenced))
    if fenced_labels != [{"position_cm-1": 1.5, "label": "Eg"}]:
        failures.append(f"fence parse {fenced_labels!r}")

    prose = 'reasoning [not valid\nfinal [{"position_cm-1": 2, "symmetry": "A1g"}]'
    prose_labels = coerce_parsed_labels(parse_model_output(prose))
    if prose_labels != [{"position_cm-1": 2.0, "label": "A1g"}]:
        failures.append(f"prose parse {prose_labels!r}")

    if parse_model_output("nope") is not None:
        failures.append("garbage text parsed")
    if parse_model_output("") is not None or parse_model_output(None) is not None:
        failures.append("empty text parsed")

    wrapped = '{"assignments": [{"position_cm-1": 3, "label": "B1g"}]}'
    wrapped_labels = coerce_parsed_labels(parse_model_output(wrapped))
    if wrapped_labels != [{"position_cm-1": 3.0, "label": "B1g"}]:
        failures.append(f"wrapper parse {wrapped_labels!r}")

    later = 'see [1, 2] then [{"position_cm-1": 4, "label": "Eg"}]'
    later_labels = coerce_parsed_labels(parse_model_output(later))
    if later_labels != [{"position_cm-1": 4.0, "label": "Eg"}]:
        failures.append(f"last-list parse {later_labels!r}")

    broken = "```json\n{broken\n```"
    if parse_model_output(broken) is not None:
        failures.append("broken fence parsed")
    return failures


def build_test_rows(test_dir: Path = TEST_DIR) -> list[dict]:
    if not test_dir.is_dir():
        raise SystemExit(f"test directory not found: {test_dir}. Run python -m scripts.make_split first.")
    paths = sorted(path for path in test_dir.glob("*.json") if path.is_file() and " " not in path.name)
    if not paths:
        raise SystemExit(f"no JSON files in {test_dir}")
    rows = []
    for path in paths:
        spectrum = json.loads(path.read_text(encoding="utf-8"))
        context = spectrum.get("context") if isinstance(spectrum.get("context"), dict) else {}
        mode_card = context.get("mode_card")
        prompt = build_prompt(spectrum, load_card_text(mode_card))
        for forbidden in _FORBIDDEN_IN_PROMPT:
            if forbidden in prompt:
                raise SystemExit(f"{path.name} prompt contains {forbidden!r}")
        if INSTRUCTION not in prompt or "Peak list:" not in prompt:
            raise SystemExit(f"{path.name} prompt is missing the instruction or the peak list")
        rows.append(
            {
                "file": path.name,
                "material": context.get("material"),
                "laser_nm": context.get("laser_nm"),
                "layer": context.get("layer"),
                "mode_card": mode_card,
                "prompt": prompt,
                "gold": gold_labels(spectrum),
            }
        )
    return rows


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def prepare_prompts() -> int:
    failures = parser_self_test()
    if failures:
        print("parser self-test failed", file=sys.stderr)
        for item in failures:
            print(item, file=sys.stderr)
        raise SystemExit(1)
    rows = build_test_rows()
    _write_jsonl(PROMPTS_JSONL, rows)
    return len(rows)


def _chunks(items: list, size: int):
    step = max(1, size)
    for start in range(0, len(items), step):
        yield items[start : start + step]


def _prediction_record(row: dict, raw_text: str) -> dict:
    parsed = coerce_parsed_labels(parse_model_output(raw_text))
    return {
        "file": row["file"],
        "material": row["material"],
        "laser_nm": row["laser_nm"],
        "layer": row["layer"],
        "mode_card": row["mode_card"],
        "gold": row["gold"],
        "raw_model_text": raw_text,
        "parsed_labels": parsed,
    }


def run_modal(already_running: bool = False) -> int:
    """Call the configured model on Modal. Refuses a placeholder id first."""
    if model_id_is_placeholder():
        print(placeholder_refusal_message(), file=sys.stderr)
        raise SystemExit(1)
    from scripts.modal_qwen_zeroshot import app, QwenZeroShot

    rows = build_test_rows()

    def _go() -> list[dict]:
        assigner = QwenZeroShot()
        records: list[dict] = []
        for batch in _chunks(rows, BATCH_SIZE):
            texts = assigner.generate.remote(
                [row["prompt"] for row in batch],
                ZERO_SHOT_MODEL_ID,
                MAX_NEW_TOKENS,
                TEMPERATURE,
            )
            if len(texts) != len(batch):
                raise RuntimeError(f"model returned {len(texts)} texts for {len(batch)} prompts")
            for row, text in zip(batch, texts):
                records.append(_prediction_record(row, text if isinstance(text, str) else str(text)))
        return records

    if already_running:
        records = _go()
    else:
        with app.run():
            records = _go()
    _write_jsonl(PREDICTIONS_JSONL, records)
    scores = score_records(records)
    write_scores(scores, SCORES_JSON)
    print(format_headline(scores))
    print(f"wrote {PREDICTIONS_JSONL}")
    print(f"wrote {SCORES_JSON}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare or run the Qwen zero-shot baseline on data/test.")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Write outputs/step5_prompts.jsonl and do not call a model.",
    )
    parser.add_argument("--local-dry-run", action="store_true", help="Alias of --prepare-only.")
    args = parser.parse_args(argv)
    if args.prepare_only or args.local_dry_run:
        count = prepare_prompts()
        print(f"prompts {count}")
        print(f"wrote {PROMPTS_JSONL}")
        return 0
    return run_modal(already_running=False)


if __name__ == "__main__":
    raise SystemExit(main())
