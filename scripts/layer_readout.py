# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.layer_readout).
"""Assign a MoS2 layer from checker-accepted peaks.

Uses ``MOS2_LAYER_TABLE`` in ``scripts/spectrum_generator`` for the file's
laser. The in-plane peak is E', Eg, or E1_2g. The out-of-plane peak is A1'
or A1g. The layer is the table row closest to that pair.

Strain is not computed. ``mos2.json`` has no numeric strain slope, and no
other file in this repo states one.

Run from the repo root::

    py -3.12 -m scripts.layer_readout
    py -3.12 -m scripts.layer_readout --checked outputs/step9_checked.jsonl --jsonl outputs/step9_layers.jsonl --summary outputs/step9_layer_summary.json
"""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.label_norm import canonical_label  # noqa: E402
from scripts.qwen_config import IGNORED_LABEL, TEST_DIR  # noqa: E402
from scripts.score_assignment import label_of, load_prediction_jsonl, position_of  # noqa: E402

CHECKED_JSONL = _REPO_ROOT / "outputs" / "step6_checked.jsonl"
LAYERS_JSONL = _REPO_ROOT / "outputs" / "step8_layers.jsonl"
SUMMARY_JSON = _REPO_ROOT / "outputs" / "step8_summary.json"

_LAYER_ORDER = ("1L", "2L", "3L", "4L", "bulk")
_IN_PLANE = frozenset({"E'", "Eg", "E1_2g"})
_OUT_PLANE = frozenset({"A1'", "A1g"})
STRAIN_REASON = (
    "No numeric strain slope is written on mode_cards/mos2.json or elsewhere in the repo. "
    "Strain was not computed and no slope was invented."
)


def load_mos2_layer_table() -> dict:
    """Load ``MOS2_LAYER_TABLE`` from the extensionless spectrum generator.

    ``spec_from_file_location`` returns None for a file with no suffix, and
    the generator imports the extensionless ``peak_finder``. A source loader
    plus a stub for that import still executes the generator module and reads
    the table it defines.
    """
    import types

    path = Path(__file__).resolve().parent / "spectrum_generator"
    if not path.is_file():
        raise SystemExit(f"cannot load {path}")
    if "peak_finder" not in sys.modules:
        stub = types.ModuleType("peak_finder")
        stub.find_raman_peaks = None
        sys.modules["peak_finder"] = stub
    loader = importlib.machinery.SourceFileLoader("phaselens_spectrum_generator", str(path))
    spec = importlib.util.spec_from_loader("phaselens_spectrum_generator", loader)
    if spec is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    table = getattr(module, "MOS2_LAYER_TABLE", None)
    if not isinstance(table, dict) or not table:
        raise SystemExit("MOS2_LAYER_TABLE is missing from scripts/spectrum_generator")
    return table


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    temporary.replace(path)


def _table_for(table: dict, laser_nm: object) -> tuple[dict, float | None]:
    try:
        laser = float(laser_nm)
    except (TypeError, ValueError):
        return table[532.0], 532.0
    nearest = min(table, key=lambda key: abs(float(key) - laser))
    if abs(float(nearest) - laser) > 1.0:
        return table[532.0], 532.0
    return table[nearest], float(nearest)


def _accepted_modes(record: dict) -> list[dict]:
    parsed = record.get("parsed_labels")
    if not isinstance(parsed, list):
        return []
    accepted = []
    for item in parsed:
        label = label_of(item)
        position = position_of(item)
        if label is None or position is None:
            continue
        if label == IGNORED_LABEL:
            continue
        name = canonical_label(label)
        if name in _IN_PLANE or name in _OUT_PLANE:
            accepted.append({"position_cm-1": position, "label": label, "canonical": name})
    return accepted


def _pick(pool: list[dict], target: float) -> dict | None:
    if not pool:
        return None
    return min(pool, key=lambda item: abs(item["position_cm-1"] - target))


def assign_layer(record: dict, table: dict) -> dict:
    by_laser, laser_key = _table_for(table, record.get("laser_nm"))
    e_refs = [float(by_laser[layer][0]) for layer in _LAYER_ORDER]
    a_refs = [float(by_laser[layer][1]) for layer in _LAYER_ORDER]
    e_target = sum(e_refs) / len(e_refs)
    a_target = sum(a_refs) / len(a_refs)
    accepted = _accepted_modes(record)
    in_plane = _pick([item for item in accepted if item["canonical"] in _IN_PLANE], e_target)
    out_plane = _pick([item for item in accepted if item["canonical"] in _OUT_PLANE], a_target)
    predicted = None
    distance = None
    reference = None
    gap = None
    if in_plane is not None and out_plane is not None:
        e_pos = float(in_plane["position_cm-1"])
        a_pos = float(out_plane["position_cm-1"])
        gap = a_pos - e_pos

        def _key(layer: str) -> tuple[float, float]:
            e_ref, a_ref = by_laser[layer]
            return (
                abs(e_pos - float(e_ref)) + abs(a_pos - float(a_ref)),
                abs((a_pos - e_pos) - (float(a_ref) - float(e_ref))),
            )

        predicted = min(_LAYER_ORDER, key=_key)
        distance = _key(predicted)[0]
        reference = {
            "in_plane": float(by_laser[predicted][0]),
            "out_of_plane": float(by_laser[predicted][1]),
        }
    gold_layer = record.get("layer")
    return {
        "file": record.get("file"),
        "laser_nm": record.get("laser_nm"),
        "table_laser_nm": laser_key,
        "gold_layer": gold_layer,
        "predicted_layer": predicted,
        "in_plane_cm-1": None if in_plane is None else in_plane["position_cm-1"],
        "in_plane_label": None if in_plane is None else in_plane["label"],
        "out_of_plane_cm-1": None if out_plane is None else out_plane["position_cm-1"],
        "out_of_plane_label": None if out_plane is None else out_plane["label"],
        "gap_cm-1": gap,
        "reference_cm-1": reference,
        "distance_cm-1": distance,
        "matched": predicted is not None and predicted == gold_layer,
        "strain": None,
        "strain_note": STRAIN_REASON,
    }


def _is_mos2_name(name: str) -> bool:
    return "mos2" in name.casefold() and " " not in name


def read_layers(checked_path: Path, test_dir: Path, table: dict) -> list[dict]:
    by_file = {}
    if checked_path.is_file():
        for record in load_prediction_jsonl(checked_path):
            name = record.get("file")
            if isinstance(name, str):
                by_file[name] = record
    rows = []
    paths = sorted(path for path in test_dir.glob("*.json") if path.is_file() and _is_mos2_name(path.name))
    for path in paths:
        record = by_file.get(path.name)
        if record is None:
            context = json.loads(path.read_text(encoding="utf-8")).get("context")
            if not isinstance(context, dict):
                context = {}
            record = {
                "file": path.name,
                "laser_nm": context.get("laser_nm"),
                "layer": context.get("layer"),
                "parsed_labels": [],
            }
        else:
            # Prefer the spectrum context layer over a copied field if we can
            # read it without using answers.
            spectrum = json.loads(path.read_text(encoding="utf-8"))
            context = spectrum.get("context") if isinstance(spectrum.get("context"), dict) else {}
            record = dict(record)
            record["layer"] = context.get("layer")
            record["laser_nm"] = context.get("laser_nm")
        rows.append(assign_layer(record, table))
    return rows


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    correct = sum(1 for row in rows if row.get("matched") is True)
    predicted = sum(1 for row in rows if row.get("predicted_layer"))
    return {
        "n_test_mos2": total,
        "n_with_both_peaks": predicted,
        "n_correct": correct,
        "fraction": None if total == 0 else correct / total,
        "denominator": "all test MoS2 files",
        "strain": "skipped",
        "strain_reason": STRAIN_REASON,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read MoS2 layer numbers from checker-accepted peaks.")
    parser.add_argument("--checked", type=Path, default=CHECKED_JSONL)
    parser.add_argument("--test-dir", type=Path, default=TEST_DIR)
    parser.add_argument("--jsonl", type=Path, default=LAYERS_JSONL)
    parser.add_argument("--summary", type=Path, default=SUMMARY_JSON)
    args = parser.parse_args(argv)
    table = load_mos2_layer_table()
    rows = read_layers(args.checked, args.test_dir, table)
    summary = summarize(rows)
    _write_jsonl(args.jsonl, rows)
    _write_json(args.summary, summary)
    fraction = summary["fraction"]
    shown = "n/a" if fraction is None else f"{fraction:.6f}"
    print(f"layer {summary['n_correct']}/{summary['n_test_mos2']} = {shown}")
    print(f"wrote {args.jsonl}")
    print(f"wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
