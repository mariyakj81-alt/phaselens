# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module.
"""Rewrite orthographic label variants to ``canonical_label``.

Edits JSON string values only, in place, so spectrum arrays stay on one
line. Keys, numbers, and every other field are copied through unchanged.

Scope:
- ``training_data/*.json`` (all files, including names that contain a space)
- the mode cards the prompts load, plus ``anatase.json`` and ``calcite.json``

Does not touch ``*_comprehensive.json``, ``mode_cards/Qiaomu``, or ``data/``.
Idempotent. Re-running on canonical text does not write.

Run from the repo root::

    python -m scripts.homogenize_labels
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.label_norm import canonical_label  # noqa: E402
from scripts.qwen_config import MODE_CARDS_DIR, TRAINING_DATA_DIR  # noqa: E402

CARD_NAMES = (
    "mos2.json",
    "quartz.json",
    "silicon.json",
    "anatase_simplified.json",
    "calcite_simplified.json",
    "anatase.json",
    "calcite.json",
)


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def _read(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise SystemExit(f"refusing BOM: {path}")
    return data.decode("utf-8")


def _rewrite_string_values(raw: str) -> tuple[str, list[tuple[str, str]]]:
    """Re-encode JSON string values whose canonical form differs.

    Object keys are left byte-for-byte. Unchanged values are copied from
    the original text, including their escaping.
    """
    decoder = json.JSONDecoder()
    pieces: list[str] = []
    changes: list[tuple[str, str]] = []
    index = 0
    length = len(raw)
    while True:
        quote = raw.find('"', index)
        if quote < 0:
            pieces.append(raw[index:])
            break
        pieces.append(raw[index:quote])
        try:
            value, end = decoder.raw_decode(raw, quote)
        except json.JSONDecodeError:
            pieces.append(raw[quote])
            index = quote + 1
            continue
        if not isinstance(value, str):
            pieces.append(raw[quote:end])
            index = end
            continue
        cursor = end
        while cursor < length and raw[cursor] in " \t\r\n":
            cursor += 1
        if cursor < length and raw[cursor] == ":":
            pieces.append(raw[quote:end])
            index = end
            continue
        new = canonical_label(value)
        if new != value:
            changes.append((value, new))
            pieces.append(json.dumps(new, ensure_ascii=False))
        else:
            pieces.append(raw[quote:end])
        index = end
    return "".join(pieces), changes


def _assert_only_canonical(before, after, path: str = "") -> None:
    if type(before) is not type(after):
        raise SystemExit(f"type changed at {path}: {type(before).__name__} -> {type(after).__name__}")
    if isinstance(before, dict):
        if list(before) != list(after):
            raise SystemExit(f"keys changed at {path}: {list(before)} -> {list(after)}")
        for key in before:
            _assert_only_canonical(before[key], after[key], f"{path}/{key}")
        return
    if isinstance(before, list):
        if len(before) != len(after):
            raise SystemExit(f"length changed at {path}: {len(before)} -> {len(after)}")
        for offset, (old, new) in enumerate(zip(before, after)):
            _assert_only_canonical(old, new, f"{path}[{offset}]")
        return
    if isinstance(before, str):
        expected = canonical_label(before)
        if after != expected:
            raise SystemExit(f"string at {path} became {after!r}, canonical is {expected!r}")
        return
    if before != after:
        raise SystemExit(f"non-string changed at {path}: {before!r} -> {after!r}")


def _answer_labels(data: dict) -> Counter:
    counts: Counter = Counter()
    answers = data.get("answers")
    if not isinstance(answers, list):
        return counts
    for item in answers:
        if isinstance(item, dict) and isinstance(item.get("label"), str):
            counts[item["label"]] += 1
    return counts


def _rewrite_file(path: Path) -> list[tuple[str, str]]:
    original = _read(path)
    before = json.loads(original)
    updated, changes = _rewrite_string_values(original)
    if not changes:
        if updated != original:
            raise SystemExit(f"{path} text changed without a label change")
        return []
    after = json.loads(updated)
    _assert_only_canonical(before, after)
    if updated == original:
        raise SystemExit(f"{path} reported changes but the text is identical")
    path.write_bytes(updated.encode("utf-8"))
    return changes


def _card_paths() -> list[Path]:
    paths = []
    for name in CARD_NAMES:
        if "comprehensive" in name.casefold():
            raise SystemExit(f"refusing comprehensive card {name}")
        path = MODE_CARDS_DIR / name
        if "Qiaomu" in path.parts:
            raise SystemExit(f"refusing Qiaomu path {path}")
        if not path.is_file():
            raise SystemExit(f"mode card not found: {path}")
        paths.append(path)
    return paths


def _training_paths() -> list[Path]:
    if not TRAINING_DATA_DIR.is_dir():
        raise SystemExit(f"training data not found: {TRAINING_DATA_DIR}")
    return sorted(path for path in TRAINING_DATA_DIR.glob("*.json") if path.is_file())


def _print_counter(title: str, counts: Counter) -> None:
    print(title)
    if not counts:
        print("  (none)")
        return
    for (old, new), count in sorted(counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1])):
        print(f"  {count:5d}  {old!r} -> {new!r}")


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    if argv:
        raise SystemExit("homogenize_labels takes no arguments")
    training_changes: Counter = Counter()
    training_label_changes: Counter = Counter()
    card_changes: Counter = Counter()
    training_files = 0
    card_files = 0
    space_label_changes = 0
    for path in _training_paths():
        before = json.loads(_read(path))
        before_labels = _answer_labels(before)
        changes = _rewrite_file(path)
        if not changes:
            continue
        training_files += 1
        after = json.loads(_read(path))
        after_labels = _answer_labels(after)
        delta_old = before_labels - after_labels
        delta_new = after_labels - before_labels
        if sum(delta_old.values()) != sum(delta_new.values()):
            raise SystemExit(f"{path.name} label count changed")
        # Pair by canonical form. Each old label maps to exactly one new label.
        for old, count in delta_old.items():
            new = canonical_label(old)
            got = delta_new.get(new, 0)
            if got < count:
                raise SystemExit(f"{path.name} label delta {old!r} -> {new!r} missing")
            training_label_changes[(old, new)] += count
            delta_new[new] -= count
            if " " in path.name:
                space_label_changes += count
        if sum(delta_new.values()) != 0:
            raise SystemExit(f"{path.name} unexpected new labels {delta_new}")
        for old, new in changes:
            training_changes[(old, new)] += 1
    for path in _card_paths():
        changes = _rewrite_file(path)
        if not changes:
            continue
        card_files += 1
        for old, new in changes:
            card_changes[(old, new)] += 1
    _print_counter("training_data answer labels", training_label_changes)
    _print_counter("training_data json strings", training_changes)
    _print_counter("mode cards", card_changes)
    print(f"training_files_rewritten {training_files}")
    print(f"card_files_rewritten {card_files}")
    print(f"space_name_label_strings {space_label_changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
