# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.score_checked).
"""Score checker-adjusted test labels and put them beside the step 5 scores.

The input JSONL must be the checker loop output (``parsed_labels`` are the
adjusted labels). Headline numbers are the test set only.

Run from the repo root::

    py -3.12 -m scripts.score_checked
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.qwen_config import SCORES_JSON  # noqa: E402
from scripts.score_assignment import format_headline, load_prediction_jsonl, score_records, write_scores  # noqa: E402

CHECKED_JSONL = _REPO_ROOT / "outputs" / "step6_checked.jsonl"
STEP7_JSON = _REPO_ROOT / "outputs" / "step7_scores.json"


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"{path} is not a JSON object")
    return payload


def fraction(block: dict) -> float | None:
    total = block.get("total")
    correct = block.get("correct")
    if not isinstance(total, int) or not isinstance(correct, int) or total == 0:
        return None
    return correct / total


def compare_headlines(new_scores: dict, old_scores: dict) -> dict:
    new_mode = new_scores["headline"]["mode_exact"]
    old_mode = old_scores["headline"]["mode_exact"]
    new_artifact = new_scores["headline"]["artifact_exact"]
    old_artifact = old_scores["headline"]["artifact_exact"]
    new_mode_f = fraction(new_mode)
    old_mode_f = fraction(old_mode)
    new_artifact_f = fraction(new_artifact)
    old_artifact_f = fraction(old_artifact)
    both_present = None not in (new_mode_f, old_mode_f, new_artifact_f, old_artifact_f)
    kept = bool(
        both_present and new_mode_f >= old_mode_f and new_artifact_f >= old_artifact_f
    )
    beat_both = bool(
        both_present and new_mode_f > old_mode_f and new_artifact_f > old_artifact_f
    )
    return {
        "mode_exact_fraction_new": new_mode_f,
        "mode_exact_fraction_old": old_mode_f,
        "artifact_exact_fraction_new": new_artifact_f,
        "artifact_exact_fraction_old": old_artifact_f,
        "both_greater_or_equal": kept,
        "both_strictly_greater": beat_both,
    }


def score_checked(checked_path: Path, step5_path: Path, output_path: Path) -> dict:
    records = load_prediction_jsonl(checked_path)
    if not records:
        raise SystemExit(f"no records in {checked_path}")
    for record in records:
        if "checker_passed" not in record or "retry" not in record:
            raise SystemExit(f"{checked_path} is not checker-loop output")
        if "gold" not in record or "parsed_labels" not in record:
            raise SystemExit(f"{record.get('file')} is missing gold or parsed_labels")
    step7 = score_records(records)
    step5 = load_json(step5_path)
    payload = {
        "headline_split": "test",
        "step5": step5,
        "step7": step7,
        "comparison_step7_vs_step5": compare_headlines(step7, step5),
        "notes": (
            "Headline is the test set. step7 scores checker-adjusted parsed_labels "
            "from the checker loop. step5 is the zero-shot score file, copied, not recomputed. "
            "Train-set scores are not mixed into these headline fractions."
        ),
    }
    write_scores(payload, output_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write step 7 scores beside the step 5 scores.")
    parser.add_argument("--checked", type=Path, default=CHECKED_JSONL)
    parser.add_argument("--step5", type=Path, default=SCORES_JSON)
    parser.add_argument("--output", type=Path, default=STEP7_JSON)
    args = parser.parse_args(argv)
    if not args.checked.is_file():
        print(f"checked predictions not found: {args.checked}", file=sys.stderr)
        return 1
    if not args.step5.is_file():
        print(f"step 5 scores not found: {args.step5}", file=sys.stderr)
        return 1
    payload = score_checked(args.checked, args.step5, args.output)
    print(format_headline(payload["step7"]))
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
