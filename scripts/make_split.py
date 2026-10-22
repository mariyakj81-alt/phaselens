# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.make_split).
"""Copy the canonical synthetic spectra into data/train and data/test.

Train is every canonical file that is not calcite and not the held-out laser.
Test is the union of calcite and the held-out laser (632.8 nm). Files whose
names contain a space are not copied. ``training_data/`` is only read.

Run from the repo root::

    python -m scripts.make_split
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.qwen_config import (  # noqa: E402
    ARTIFACT_SOURCES,
    HELD_OUT_LASER_NM,
    HELD_OUT_MATERIAL,
    HELD_OUT_MODE_CARD,
    IGNORED_SOURCE,
    MODE_SOURCE,
    REPO_ROOT,
    SPLIT_MANIFEST,
    TEST_DIR,
    TRAIN_DIR,
    TRAINING_DATA_DIR,
    is_held_out_material,
    laser_matches,
)

RULE = (
    "Canonical files are training_data JSON files whose names contain no space. "
    "Files with a space in the name (reused indexes such as '00268_quartz 2.json') "
    "are excluded and not copied. "
    "Train = canonical files that are not the held-out material and not the held-out laser. "
    "Test = canonical files that are the held-out material or the held-out laser (union). "
    "A file that is both is copied once, into test. "
    "Held-out material is calcite (mode card calcite_simplified.json). "
    "Held-out laser is 632.8 nm because it is the only laser whose plasma lines are real neon lines. "
    "This follows the README and ARCHITECTURE exclusion rule. "
    "SEQUENCE_OF_EXECUTION.md step 4 also lists clean Valency peak lists and the Lee et al. "
    "MoS2 list; those files are not in training_data and are not part of this copy. "
    "training_data is only read, never modified."
)


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _reset_output_dir(path: Path) -> None:
    if path.exists() and not path.is_dir():
        raise SystemExit(f"{path} exists and is not a directory")
    if path.exists():
        for child in path.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    path.mkdir(parents=True, exist_ok=True)


def _guard_destinations(source: Path, train: Path, test: Path, manifest: Path) -> None:
    source_resolved = source.resolve()
    for dest in (train.resolve(), test.resolve(), manifest.resolve()):
        if dest == source_resolved or source_resolved in dest.parents:
            raise SystemExit(f"refusing to write {dest} inside {source_resolved}")
    if train.resolve() == test.resolve():
        raise SystemExit("train and test directories must differ")


def _count_answers(spectrum: dict) -> tuple[int, int, int, int]:
    mode = artifact = false_peak = other = 0
    for answer in spectrum.get("answers") or []:
        if not isinstance(answer, dict):
            other += 1
            continue
        source = answer.get("source")
        if source == MODE_SOURCE:
            mode += 1
        elif source in ARTIFACT_SOURCES:
            artifact += 1
        elif source == IGNORED_SOURCE:
            false_peak += 1
        else:
            other += 1
    return mode, artifact, false_peak, other


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def split_dataset(
    source: Path = TRAINING_DATA_DIR,
    train_dir: Path = TRAIN_DIR,
    test_dir: Path = TEST_DIR,
    manifest_path: Path = SPLIT_MANIFEST,
) -> dict:
    source = source.resolve()
    train_dir = train_dir.resolve()
    test_dir = test_dir.resolve()
    manifest_path = manifest_path.resolve()
    if not source.is_dir():
        raise SystemExit(f"source directory not found: {source}")
    _guard_destinations(source, train_dir, test_dir, manifest_path)
    _reset_output_dir(train_dir)
    _reset_output_dir(test_dir)

    excluded_space: list[str] = []
    ignored_non_json: list[str] = []
    records: list[dict] = []
    mode_card_counts: dict[str, int] = {}
    totals = {
        "train": {"files": 0, "mode": 0, "artifact": 0, "false_peak": 0, "other": 0},
        "test": {"files": 0, "mode": 0, "artifact": 0, "false_peak": 0, "other": 0},
    }
    slice_files = {"calcite_only": 0, "held_out_laser_only": 0, "both": 0}
    by_split_material: dict[str, dict[str, int]] = {"train": {}, "test": {}}

    for path in sorted(source.iterdir(), key=lambda item: item.name):
        if not path.is_file():
            continue
        if path.suffix.lower() != ".json":
            ignored_non_json.append(path.name)
            continue
        if " " in path.name:
            excluded_space.append(path.name)
            continue
        spectrum = json.loads(path.read_text(encoding="utf-8"))
        context = spectrum.get("context")
        if not isinstance(context, dict):
            raise SystemExit(f"{path.name} has no context object")
        material = context.get("material")
        mode_card = context.get("mode_card")
        laser = context.get("laser_nm")
        layer = context.get("layer")
        calcite = is_held_out_material(material, mode_card)
        held_laser = laser_matches(laser)
        split = "test" if calcite or held_laser else "train"
        dest_dir = test_dir if split == "test" else train_dir
        dest = dest_dir / path.name
        shutil.copy2(path, dest)
        if dest.stat().st_size != path.stat().st_size:
            raise SystemExit(f"copy size mismatch for {path.name}")
        mode_n, artifact_n, false_n, other_n = _count_answers(spectrum)
        bucket = totals[split]
        bucket["files"] += 1
        bucket["mode"] += mode_n
        bucket["artifact"] += artifact_n
        bucket["false_peak"] += false_n
        bucket["other"] += other_n
        card_key = mode_card if isinstance(mode_card, str) else "(missing)"
        mode_card_counts[card_key] = mode_card_counts.get(card_key, 0) + 1
        material_key = material if isinstance(material, str) and material else "(missing)"
        materials = by_split_material[split]
        materials[material_key] = materials.get(material_key, 0) + 1
        if split == "test":
            if calcite and held_laser:
                slice_files["both"] += 1
            elif calcite:
                slice_files["calcite_only"] += 1
            else:
                slice_files["held_out_laser_only"] += 1
        records.append(
            {
                "source": _rel(path),
                "destination": _rel(dest),
                "material": material,
                "mode_card": mode_card,
                "laser_nm": laser,
                "layer": layer,
                "split": split,
            }
        )

    manifest = {
        "rule": RULE,
        "held_out_laser_nm": HELD_OUT_LASER_NM,
        "held_out_laser_reason": (
            "632.8 nm is the only laser whose plasma lines are real neon lines."
        ),
        "held_out_material": HELD_OUT_MATERIAL,
        "held_out_mode_card": HELD_OUT_MODE_CARD,
        "source_dir": _rel(source),
        "counts": {
            "source_json_files": len(records) + len(excluded_space),
            "excluded_space_in_name": len(excluded_space),
            "ignored_non_json": len(ignored_non_json),
            "canonical_files": len(records),
            "train_files": totals["train"]["files"],
            "test_files": totals["test"]["files"],
            "test_calcite_only": slice_files["calcite_only"],
            "test_held_out_laser_only": slice_files["held_out_laser_only"],
            "test_both_calcite_and_held_out_laser": slice_files["both"],
            "train_mode_peaks": totals["train"]["mode"],
            "train_artifact_peaks": totals["train"]["artifact"],
            "train_false_peaks": totals["train"]["false_peak"],
            "train_other_peaks": totals["train"]["other"],
            "test_mode_peaks": totals["test"]["mode"],
            "test_artifact_peaks": totals["test"]["artifact"],
            "test_false_peaks": totals["test"]["false_peak"],
            "test_other_peaks": totals["test"]["other"],
            "mode_cards": mode_card_counts,
            "by_split_material": by_split_material,
        },
        "excluded_space_files": excluded_space,
        "files": records,
    }
    _write_json(manifest_path, manifest)
    return manifest


def _print_summary(manifest: dict, manifest_path: Path) -> None:
    counts = manifest["counts"]
    lines = [
        f"canonical_files {counts['canonical_files']}",
        f"excluded_space_in_name {counts['excluded_space_in_name']}",
        f"train_files {counts['train_files']}",
        f"train_mode_peaks {counts['train_mode_peaks']}",
        f"train_artifact_peaks {counts['train_artifact_peaks']}",
        f"train_false_peaks {counts['train_false_peaks']}",
        f"test_files {counts['test_files']}",
        f"test_mode_peaks {counts['test_mode_peaks']}",
        f"test_artifact_peaks {counts['test_artifact_peaks']}",
        f"test_false_peaks {counts['test_false_peaks']}",
        f"test_calcite_only {counts['test_calcite_only']}",
        f"test_held_out_laser_only {counts['test_held_out_laser_only']}",
        f"test_both_calcite_and_held_out_laser {counts['test_both_calcite_and_held_out_laser']}",
        f"manifest {_rel(manifest_path)}",
    ]
    print("\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Split canonical spectra into data/train and data/test.")
    parser.add_argument("--source", type=Path, default=TRAINING_DATA_DIR)
    parser.add_argument("--train", type=Path, default=TRAIN_DIR)
    parser.add_argument("--test", type=Path, default=TEST_DIR)
    parser.add_argument("--manifest", type=Path, default=SPLIT_MANIFEST)
    args = parser.parse_args(argv)
    manifest = split_dataset(args.source, args.train, args.test, args.manifest)
    _print_summary(manifest, args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
