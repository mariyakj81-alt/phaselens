# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.score_assignment).
"""Score peak assignments against gold labels.

Predictions JSONL, one JSON object per line, one spectrum per object::

    {
      "file": "00001_calcite_simplified.json",
      "material": "calcite (CaCO3)",
      "laser_nm": 632.8,
      "layer": null,
      "mode_card": "calcite_simplified.json",
      "gold": [
        {"position_cm-1": 1086.02, "label": "A1g", "source": "mode"}
      ],
      "raw_model_text": "[{\\"position_cm-1\\": 1086.02, \\"label\\": \\"A1g\\"}]",
      "parsed_labels": [
        {"position_cm-1": 1086.02, "label": "A1g"}
      ]
    }

``parsed_labels`` may be null when the model text is not a JSON list. Those
peaks stay in the denominator and count as wrong. A ``predicted`` list is
accepted when ``parsed_labels`` is absent. Gold and predictions are joined on
``position_cm-1`` within 0.001 cm^-1. Each prediction is used at most once.
Extra predictions are ignored in the denominators.

Headline fractions, both exact:

1. Gold ``source == "mode"`` whose predicted label equals the gold label.
2. Gold ``source`` in ``{"plasma", "substrate"}`` predicted as ``"artifact"``.

``source == "false_peak"`` and gold label ``"unassigned"`` are left out of both
denominators. Normalized fractions use the same denominators after
``canonical_label`` (prime position, U+2032, U+2033 as two apostrophes,
subscript digits, ``E^1_2g`` / standalone ``E2g``, ``A1g + B1g`` spacing),
then stripping whitespace and casefolding.

A file that is both calcite and the held-out laser is counted in both slice
breakdowns and once in the headline.

Run from the repo root::

    python -m scripts.score_assignment --self-test
    python -m scripts.score_assignment outputs/step5_predictions.jsonl -o outputs/step5_scores.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.label_norm import canonical_label  # noqa: E402
from scripts.qwen_config import (  # noqa: E402
    ARTIFACT_LABEL,
    ARTIFACT_SOURCES,
    HELD_OUT_LASER_NM,
    HELD_OUT_MATERIAL,
    IGNORED_LABEL,
    IGNORED_SOURCE,
    MODE_SOURCE,
    is_held_out_material,
    laser_matches,
)

POSITION_MATCH_ABS_TOL_CM = 1e-3
_POSITION_KEYS = ("position_cm-1", "position_cm1", "position")
_LABEL_KEYS = ("label", "symmetry", "assignment")
_COUNTERS = (
    "mode_peaks",
    "mode_exact_correct",
    "mode_normalized_correct",
    "mode_unjoined",
    "artifact_peaks",
    "artifact_exact_correct",
    "artifact_normalized_correct",
    "artifact_unjoined",
    "ignored_extra_predictions",
)
_NOTES = (
    "Headline numbers are mode_exact and artifact_exact. "
    "Normalized fractions are secondary and use canonical_label "
    "(prime position, unicode primes, subscript digits, E^1_2g/E2g, "
    "A1g + B1g spacing) then strip whitespace and casefold. "
    "false_peak and unassigned gold labels are excluded from both denominators. "
    "A file in both slices is counted in each slice and once in the headline."
)


def normalize_label(label: object) -> str:
    """Casefolded canonical spelling, with whitespace removed.

    Exact scoring does not call this. Headline exact match compares the
    strings as written, which are already canonical after homogenize.
    """
    text = "" if label is None else str(label)
    text = canonical_label(text)
    text = "".join(text.split())
    return text.casefold()


def position_of(item: object) -> float | None:
    if not isinstance(item, dict):
        return None
    for key in _POSITION_KEYS:
        if key not in item or item[key] is None:
            continue
        try:
            return float(item[key])
        except (TypeError, ValueError):
            continue
    return None


def label_of(item: object) -> str | None:
    if not isinstance(item, dict):
        return None
    for key in _LABEL_KEYS:
        if key not in item or item[key] is None:
            continue
        return str(item[key])
    return None


def predictions_of(record: dict) -> list:
    if "parsed_labels" in record:
        parsed = record["parsed_labels"]
    elif "predicted" in record:
        parsed = record["predicted"]
    else:
        parsed = []
    if not isinstance(parsed, list):
        return []
    return parsed


def _is_ignored(gold_item: object) -> bool:
    if not isinstance(gold_item, dict):
        return True
    if gold_item.get("source") == IGNORED_SOURCE:
        return True
    return gold_item.get("label") == IGNORED_LABEL


def _align(gold: list, predicted: list) -> tuple[list[tuple[object, object | None]], int]:
    used = [False] * len(predicted)
    pairs: list[tuple[object, object | None]] = []
    for item in gold:
        gold_pos = position_of(item)
        best: int | None = None
        best_distance: float | None = None
        if gold_pos is not None:
            for index, pred in enumerate(predicted):
                if used[index]:
                    continue
                pred_pos = position_of(pred)
                if pred_pos is None:
                    continue
                distance = abs(gold_pos - pred_pos)
                if distance <= POSITION_MATCH_ABS_TOL_CM and (
                    best_distance is None or distance < best_distance
                ):
                    best = index
                    best_distance = distance
        if best is None:
            pairs.append((item, None))
        else:
            used[best] = True
            pairs.append((item, predicted[best]))
    extras = sum(1 for flag in used if not flag)
    return pairs, extras


def _empty_bucket() -> dict[str, int]:
    return {key: 0 for key in _COUNTERS}


def _add(bucket: dict[str, int], stats: dict[str, int]) -> None:
    for key in _COUNTERS:
        bucket[key] += stats[key]


def _file_stats(record: dict) -> dict[str, int]:
    gold = record.get("gold")
    if not isinstance(gold, list):
        gold = []
    pairs, extras = _align(gold, predictions_of(record))
    stats = _empty_bucket()
    stats["ignored_extra_predictions"] = extras
    for gold_item, pred_item in pairs:
        if _is_ignored(gold_item) or not isinstance(gold_item, dict):
            continue
        source = gold_item.get("source")
        pred_label = label_of(pred_item)
        if source == MODE_SOURCE:
            stats["mode_peaks"] += 1
            if pred_item is None:
                stats["mode_unjoined"] += 1
            gold_label = gold_item.get("label")
            gold_text = None if gold_label is None else str(gold_label)
            if pred_label is not None and gold_text is not None and pred_label == gold_text:
                stats["mode_exact_correct"] += 1
            if (
                pred_label is not None
                and gold_text is not None
                and normalize_label(pred_label) != ""
                and normalize_label(pred_label) == normalize_label(gold_text)
            ):
                stats["mode_normalized_correct"] += 1
        elif source in ARTIFACT_SOURCES:
            stats["artifact_peaks"] += 1
            if pred_item is None:
                stats["artifact_unjoined"] += 1
            if pred_label == ARTIFACT_LABEL:
                stats["artifact_exact_correct"] += 1
            if pred_label is not None and normalize_label(pred_label) == normalize_label(ARTIFACT_LABEL):
                stats["artifact_normalized_correct"] += 1
    return stats


def _rate(correct: int, total: int) -> dict:
    fraction = None if total == 0 else correct / total
    return {"correct": correct, "total": total, "fraction": fraction}


def _finish(bucket: dict[str, int]) -> dict:
    return {
        "mode_exact": _rate(bucket["mode_exact_correct"], bucket["mode_peaks"]),
        "artifact_exact": _rate(bucket["artifact_exact_correct"], bucket["artifact_peaks"]),
        "mode_normalized": _rate(bucket["mode_normalized_correct"], bucket["mode_peaks"]),
        "artifact_normalized": _rate(bucket["artifact_normalized_correct"], bucket["artifact_peaks"]),
        "mode_unjoined": bucket["mode_unjoined"],
        "artifact_unjoined": bucket["artifact_unjoined"],
        "ignored_extra_predictions": bucket["ignored_extra_predictions"],
    }


def _material_key(record: dict) -> str:
    material = record.get("material")
    if isinstance(material, str) and material.strip():
        return material.strip()
    return "unknown"


def score_records(records: list[dict]) -> dict:
    """Score a list of per-file gold/prediction records."""
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    headline = _empty_bucket()
    by_material: dict[str, dict[str, int]] = {}
    by_slice = {"calcite": _empty_bucket(), "held_out_laser": _empty_bucket()}
    both = 0
    n_files = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        n_files += 1
        stats = _file_stats(record)
        _add(headline, stats)
        key = _material_key(record)
        by_material.setdefault(key, _empty_bucket())
        _add(by_material[key], stats)
        calcite = is_held_out_material(record.get("material"), record.get("mode_card"))
        held_laser = laser_matches(record.get("laser_nm"))
        if calcite:
            _add(by_slice["calcite"], stats)
        if held_laser:
            _add(by_slice["held_out_laser"], stats)
        if calcite and held_laser:
            both += 1
    return {
        "headline_metric": "exact",
        "held_out_laser_nm": HELD_OUT_LASER_NM,
        "held_out_material": HELD_OUT_MATERIAL,
        "position_match_abs_tol_cm-1": POSITION_MATCH_ABS_TOL_CM,
        "n_files": n_files,
        "n_files_in_both_slices": both,
        "headline": _finish(headline),
        "by_material": {key: _finish(bucket) for key, bucket in sorted(by_material.items())},
        "by_slice": {name: _finish(bucket) for name, bucket in by_slice.items()},
        "notes": _NOTES,
    }


def load_prediction_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            item = json.loads(text)
            if not isinstance(item, dict):
                raise SystemExit(f"{path}:{line_number} is not a JSON object")
            records.append(item)
    return records


def write_scores(scores: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(scores, indent=2, ensure_ascii=False) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def format_headline(scores: dict) -> str:
    mode = scores["headline"]["mode_exact"]
    artifact = scores["headline"]["artifact_exact"]

    def _fmt(value: object) -> str:
        if value is None:
            return "n/a"
        return f"{float(value):.6f}"

    return (
        f"mode_exact {mode['correct']}/{mode['total']} = {_fmt(mode['fraction'])}\n"
        f"artifact_exact {artifact['correct']}/{artifact['total']} = {_fmt(artifact['fraction'])}"
    )


def _expect_rate(failures: list[str], block: dict, correct: int, total: int, name: str) -> None:
    if block["correct"] != correct or block["total"] != total:
        failures.append(
            f"{name} expected {correct}/{total} got {block['correct']}/{block['total']}"
        )
        return
    if total == 0:
        if block["fraction"] is not None:
            failures.append(f"{name} fraction should be null when total is 0")
        return
    if abs(float(block["fraction"]) - (correct / total)) > 1e-12:
        failures.append(f"{name} fraction {block['fraction']} != {correct / total}")


def _mode(gold_pos: float, label: str) -> dict:
    return {"position_cm-1": gold_pos, "label": label, "source": "mode"}


def _artifact(gold_pos: float, source: str) -> dict:
    return {"position_cm-1": gold_pos, "label": "artifact", "source": source}


def _pred(gold_pos: float, label: str) -> dict:
    return {"position_cm-1": gold_pos, "label": label}


def self_test() -> int:
    failures: list[str] = []
    expected_canonical = {
        "A'1": "A1'",
        "A\u20321": "A1'",
        "A1'": "A1'",
        "E\u2032": "E'",
        "E'": "E'",
        "E\u2033": "E''",
        "E^1_2g": "E1_2g",
        "E1_2g": "E1_2g",
        "E^2_2g": "E^2_2g",
        "E2g": "E1_2g",
        "A1g+B1g": "A1g + B1g",
        "A1g + B1g": "A1g + B1g",
        "A1g": "A1g",
        "B1g": "B1g",
        "F2g": "F2g",
        "T2g": "T2g",
        "artifact": "artifact",
        "Eg": "Eg",
        "A\u2081g": "A1g",
        "E\u2032 (monolayer); E^1_2g (bulk notation)": "E' (monolayer); E1_2g (bulk notation)",
        "A\u20321 (monolayer); A1g (bulk notation)": "A1' (monolayer); A1g (bulk notation)",
        "1T\u2032": "1T'",
        "A1g+B1g(2)": "A1g + B1g(2)",
        "E^2_2g shear": "E^2_2g shear",
    }
    for old, new in expected_canonical.items():
        got = canonical_label(old)
        if got != new:
            failures.append(f"canonical {old!r} -> {got!r}, expected {new!r}")
        if canonical_label(got) != got:
            failures.append(f"canonical not idempotent on {old!r}")
    if normalize_label("E\u2032") != "e'" or normalize_label("E'") != "e'":
        failures.append(f"prime fold failed: {normalize_label('E′')!r}")
    if normalize_label("E\u2033") != "e''":
        failures.append(f"double prime fold failed: {normalize_label('E″')!r}")
    if normalize_label("E\u2033") == normalize_label("E'"):
        failures.append("E double prime collapsed into E'")
    if normalize_label("A\u2081g") != normalize_label("A1g") or normalize_label("A\u2081g") != "a1g":
        failures.append("subscript fold failed")
    if normalize_label("A1g + B1g") != normalize_label("A1g+B1g"):
        failures.append("plus-sign spacing fold failed")
    if normalize_label("A'1") != normalize_label("A1'") or normalize_label("A\u20321") != "a1'":
        failures.append("A'1 prime-position fold failed")
    if normalize_label("E^1_2g") != normalize_label("E1_2g") or normalize_label("E2g") != "e1_2g":
        failures.append("E1_2g fold failed")
    if normalize_label("E^2_2g") == normalize_label("E1_2g"):
        failures.append("shear mode E^2_2g collapsed into E1_2g")
    if normalize_label("T2g") == normalize_label("F2g"):
        failures.append("T2g must not match F2g")
    if canonical_label("artifact") != "artifact":
        failures.append("artifact changed")

    perfect_gold = [
        _mode(128.0, "A1g"),
        _mode(206.0, "Eg"),
        _artifact(300.0, "plasma"),
        _artifact(520.2, "substrate"),
    ]
    perfect_pred = [
        _pred(128.0, "A1g"),
        _pred(206.0, "Eg"),
        _pred(300.0, "artifact"),
        _pred(520.2, "artifact"),
    ]
    perfect = score_records(
        [
            {
                "file": "perfect.json",
                "material": "quartz",
                "laser_nm": 532.0,
                "layer": None,
                "gold": perfect_gold,
                "parsed_labels": perfect_pred,
            }
        ]
    )
    _expect_rate(failures, perfect["headline"]["mode_exact"], 2, 2, "perfect mode exact")
    _expect_rate(failures, perfect["headline"]["artifact_exact"], 2, 2, "perfect artifact exact")
    _expect_rate(failures, perfect["headline"]["mode_normalized"], 2, 2, "perfect mode normalized")
    _expect_rate(failures, perfect["headline"]["artifact_normalized"], 2, 2, "perfect artifact normalized")

    wrong = score_records(
        [
            {
                "file": "wrong.json",
                "material": "anatase (TiO2)",
                "laser_nm": 488.0,
                "gold": perfect_gold,
                "parsed_labels": [
                    _pred(128.0, "X"),
                    _pred(206.0, "Y"),
                    _pred(300.0, "Eg"),
                    _pred(520.2, "F2g"),
                ],
            }
        ]
    )
    _expect_rate(failures, wrong["headline"]["mode_exact"], 0, 2, "wrong mode exact")
    _expect_rate(failures, wrong["headline"]["artifact_exact"], 0, 2, "wrong artifact exact")
    _expect_rate(failures, wrong["headline"]["mode_normalized"], 0, 2, "wrong mode normalized")
    _expect_rate(failures, wrong["headline"]["artifact_normalized"], 0, 2, "wrong artifact normalized")

    miss = score_records(
        [
            {
                "file": "artifact_miss.json",
                "material": "pristine diamond-cubic Si-I",
                "laser_nm": 514.5,
                "gold": perfect_gold,
                "parsed_labels": [
                    _pred(128.0, "A1g"),
                    _pred(206.0, "Eg"),
                    _pred(300.0, "F2g"),
                    _pred(520.2, "plasma"),
                ],
            }
        ]
    )
    _expect_rate(failures, miss["headline"]["mode_exact"], 2, 2, "artifact-miss mode")
    _expect_rate(failures, miss["headline"]["artifact_exact"], 0, 2, "artifact-miss artifact")
    _expect_rate(failures, miss["headline"]["artifact_normalized"], 0, 2, "artifact-miss artifact normalized")

    norm = score_records(
        [
            {
                "file": "norm.json",
                "material": "molybdenum disulfide",
                "laser_nm": 488.0,
                "layer": "1L",
                "gold": [
                    _mode(385.0, "E'"),
                    _mode(404.0, "A1g + B1g"),
                    _mode(410.0, "A\u2081g"),
                    _artifact(700.0, "plasma"),
                ],
                "parsed_labels": [
                    _pred(385.0, "E\u2032"),
                    _pred(404.0, "A1g+B1g"),
                    _pred(410.0, "A1g"),
                    _pred(700.0, "Artifact"),
                ],
            }
        ]
    )
    _expect_rate(failures, norm["headline"]["mode_exact"], 0, 3, "norm mode exact")
    _expect_rate(failures, norm["headline"]["mode_normalized"], 3, 3, "norm mode normalized")
    _expect_rate(failures, norm["headline"]["artifact_exact"], 0, 1, "norm artifact exact")
    _expect_rate(failures, norm["headline"]["artifact_normalized"], 1, 1, "norm artifact normalized")

    prime_order = score_records(
        [
            {
                "file": "prime_order.json",
                "material": "molybdenum disulfide",
                "laser_nm": 514.5,
                "layer": "1L",
                "gold": [_mode(384.0, "A1'"), _mode(408.0, "E1_2g")],
                "parsed_labels": [_pred(384.0, "A'1"), _pred(408.0, "E^2_2g")],
            }
        ]
    )
    _expect_rate(failures, prime_order["headline"]["mode_exact"], 0, 2, "prime-order mode exact")
    _expect_rate(failures, prime_order["headline"]["mode_normalized"], 1, 2, "prime-order mode normalized")

    ignored = score_records(
        [
            {
                "file": "false_peak.json",
                "material": "quartz",
                "laser_nm": 532.0,
                "gold": [
                    _mode(128.0, "A1g"),
                    _mode(206.0, "Eg"),
                    _artifact(300.0, "plasma"),
                    {"position_cm-1": 999.0, "label": "unassigned", "source": "false_peak"},
                    {"position_cm-1": 111.0, "label": "unassigned", "source": "mode"},
                ],
                "parsed_labels": [
                    _pred(128.0, "A1g"),
                    _pred(206.0, "Eg"),
                    _pred(300.0, "artifact"),
                    _pred(999.0, "Eg"),
                    _pred(111.0, "NOPE"),
                ],
            }
        ]
    )
    _expect_rate(failures, ignored["headline"]["mode_exact"], 2, 2, "false_peak mode")
    _expect_rate(failures, ignored["headline"]["artifact_exact"], 1, 1, "false_peak artifact")
    if ignored["headline"]["ignored_extra_predictions"] != 0:
        failures.append("false_peak predictions were counted as extra")

    missing = score_records(
        [
            {
                "file": "missing.json",
                "material": "anatase (TiO2)",
                "laser_nm": 514.5,
                "gold": [_mode(10.0, "Eg"), _mode(20.0, "A1g")],
                "parsed_labels": [_pred(10.0, "Eg"), _pred(20.5, "A1g"), _pred(50.0, "B1g")],
            }
        ]
    )
    _expect_rate(failures, missing["headline"]["mode_exact"], 1, 2, "missing mode")
    _expect_rate(failures, missing["headline"]["artifact_exact"], 0, 0, "missing artifact empty")
    if missing["headline"]["mode_unjoined"] != 1:
        failures.append(f"missing unjoined {missing['headline']['mode_unjoined']}")
    if missing["headline"]["ignored_extra_predictions"] != 2:
        failures.append(f"missing extras {missing['headline']['ignored_extra_predictions']}")

    unparsed = score_records(
        [
            {
                "file": "unparsed.json",
                "material": "quartz",
                "laser_nm": 488.0,
                "gold": [_mode(10.0, "Eg")],
                "raw_model_text": "not json",
                "parsed_labels": None,
            }
        ]
    )
    _expect_rate(failures, unparsed["headline"]["mode_exact"], 0, 1, "unparsed mode")
    if unparsed["headline"]["mode_unjoined"] != 1:
        failures.append("unparsed peak was not unjoined")

    only_false = score_records(
        [
            {
                "file": "only_false.json",
                "material": "quartz",
                "laser_nm": 532.0,
                "gold": [{"position_cm-1": 10.0, "label": "unassigned", "source": "false_peak"}],
                "parsed_labels": [_pred(10.0, "Eg")],
            }
        ]
    )
    _expect_rate(failures, only_false["headline"]["mode_exact"], 0, 0, "only false mode")
    _expect_rate(failures, only_false["headline"]["artifact_exact"], 0, 0, "only false artifact")

    alias = score_records(
        [
            {
                "file": "alias.json",
                "material": "quartz",
                "laser_nm": 488.0,
                "gold": [_mode(10.0, "Eg")],
                "predicted": [_pred(10.0, "Eg")],
            }
        ]
    )
    _expect_rate(failures, alias["headline"]["mode_exact"], 1, 1, "predicted alias")

    slices = score_records(
        [
            {
                "file": "calcite_632.json",
                "material": "calcite (CaCO3)",
                "mode_card": "calcite_simplified.json",
                "laser_nm": 632.8,
                "layer": None,
                "gold": [_mode(100.0, "Eg"), _artifact(200.0, "plasma")],
                "parsed_labels": [_pred(100.0, "Eg"), _pred(200.0, "artifact")],
            },
            {
                "file": "quartz_632.json",
                "material": "quartz",
                "mode_card": "quartz.json",
                "laser_nm": "632.8",
                "gold": [_mode(100.0, "Eg")],
                "parsed_labels": [_pred(100.0, "NOPE")],
            },
            {
                "file": "calcite_532.json",
                "material": "calcite (CaCO3)",
                "mode_card": "calcite_simplified.json",
                "laser_nm": 532.0,
                "gold": [_mode(100.0, "A1g"), _artifact(520.2, "substrate")],
                "parsed_labels": [_pred(100.0, "A1g"), _pred(520.2, "F2g")],
            },
        ]
    )
    _expect_rate(failures, slices["headline"]["mode_exact"], 2, 3, "slice headline mode")
    _expect_rate(failures, slices["headline"]["artifact_exact"], 1, 2, "slice headline artifact")
    _expect_rate(failures, slices["by_slice"]["calcite"]["mode_exact"], 2, 2, "calcite slice mode")
    _expect_rate(failures, slices["by_slice"]["calcite"]["artifact_exact"], 1, 2, "calcite slice artifact")
    _expect_rate(failures, slices["by_slice"]["held_out_laser"]["mode_exact"], 1, 2, "laser slice mode")
    _expect_rate(failures, slices["by_slice"]["held_out_laser"]["artifact_exact"], 1, 1, "laser slice artifact")
    _expect_rate(failures, slices["by_material"]["calcite (CaCO3)"]["mode_exact"], 2, 2, "calcite material")
    _expect_rate(failures, slices["by_material"]["quartz"]["mode_exact"], 0, 1, "quartz material")
    if slices["n_files"] != 3:
        failures.append(f"slice n_files {slices['n_files']}")
    if slices["n_files_in_both_slices"] != 1:
        failures.append(f"both slices {slices['n_files_in_both_slices']}")
    if set(slices["by_material"]) != {"calcite (CaCO3)", "quartz"}:
        failures.append(f"materials {sorted(slices['by_material'])}")

    if failures:
        print("self-test failed", file=sys.stderr)
        for item in failures:
            print(item, file=sys.stderr)
        return 1
    print("self-test passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score assignment predictions JSONL, or run the self-test.")
    parser.add_argument("predictions", nargs="?", type=Path, help="Predictions JSONL path.")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic scorer cases and exit.")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Write the scores JSON here.")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.predictions is None:
        parser.error("pass a predictions JSONL, or --self-test")
    if not args.predictions.is_file():
        print(f"predictions not found: {args.predictions}", file=sys.stderr)
        return 1
    scores = score_records(load_prediction_jsonl(args.predictions))
    if args.output is not None:
        write_scores(scores, args.output)
        print(format_headline(scores))
        print(f"wrote {args.output}")
    else:
        print(json.dumps(scores, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
