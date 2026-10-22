# scripts/spectrum_generator and scripts/peak_finder are extensionless.
# This file uses a .py suffix so it can be run as a module (python -m scripts.make_prompt).
"""Build the zero-shot prompt: raw mode card text, then the peak list.

The prompt never includes ``answers``, the spectrum arrays, or
``known_artifact_lines_cm-1``. Gold labels are returned separately.

Run from the repo root::

    python -m scripts.make_prompt path/to/spectrum.json
    python -m scripts.make_prompt path/to/spectrum.json --gold-out gold.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_repo_str = str(_REPO_ROOT)
sys.path[:] = [_repo_str, *[p for p in sys.path if p != _repo_str]]

from scripts.qwen_config import MODE_CARDS_DIR  # noqa: E402

INSTRUCTION = (
    'Return a JSON list pairing each peak with one symmetry name from the card or "artifact". '
    "Preserve position_cm-1 on every item so the list can be joined to these peaks. "
    "Each item must be an object with keys position_cm-1 and label. "
    "Return only that JSON list."
)


def gold_labels(spectrum: dict) -> list:
    """Gold rows aligned with ``answers``, joined later on ``position_cm-1``."""
    answers = spectrum.get("answers")
    if not isinstance(answers, list):
        return []
    gold = []
    for item in answers:
        if not isinstance(item, dict):
            continue
        gold.append(
            {
                "position_cm-1": item.get("position_cm-1"),
                "label": item.get("label"),
                "source": item.get("source"),
            }
        )
    return gold


def _public_peaks(spectrum: dict) -> list[dict]:
    peaks = spectrum.get("peaks")
    if not isinstance(peaks, list):
        return []
    public = []
    for peak in peaks:
        if not isinstance(peak, dict):
            continue
        public.append(
            {
                "position_cm-1": peak.get("position_cm-1"),
                "height": peak.get("height"),
                "fwhm_cm-1": peak.get("fwhm_cm-1"),
            }
        )
    return public


def build_prompt(spectrum: dict, card_text: str) -> str:
    """Plain text: raw mode card, then peak JSON, then the step-5 instruction.

    Only ``spectrum["peaks"]`` is read. Answers, the spectrum curve, and
    ``known_artifact_lines_cm-1`` are not interpolated.
    """
    peaks_json = json.dumps(_public_peaks(spectrum), ensure_ascii=False, indent=2)
    return (
        f"{card_text.rstrip()}\n\n"
        "Peak list:\n"
        f"{peaks_json}\n\n"
        f"{INSTRUCTION}\n"
    )


def load_card_text(mode_card: object, cards_dir: Path = MODE_CARDS_DIR) -> str:
    if not isinstance(mode_card, str) or not mode_card.strip():
        raise SystemExit("spectrum context.mode_card is missing")
    name = Path(mode_card).name
    if name != mode_card or ".." in name:
        raise SystemExit(f"refusing mode card path {mode_card!r}")
    if "comprehensive" in name.casefold():
        raise SystemExit(f"refusing comprehensive mode card {name}")
    path = cards_dir / name
    if not path.is_file():
        raise SystemExit(f"mode card not found: {path}")
    return path.read_text(encoding="utf-8")


def _utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    parser = argparse.ArgumentParser(description="Print a zero-shot prompt for one spectrum JSON file.")
    parser.add_argument("spectrum", type=Path)
    parser.add_argument("--cards", type=Path, default=MODE_CARDS_DIR)
    parser.add_argument("--gold-out", type=Path, default=None, help="Write gold labels JSON to this path.")
    args = parser.parse_args(argv)
    if not args.spectrum.is_file():
        print(f"spectrum not found: {args.spectrum}", file=sys.stderr)
        return 1
    spectrum = json.loads(args.spectrum.read_text(encoding="utf-8"))
    mode_card = (spectrum.get("context") or {}).get("mode_card")
    card_text = load_card_text(mode_card, args.cards)
    prompt = build_prompt(spectrum, card_text)
    sys.stdout.write(prompt)
    if args.gold_out is not None:
        payload = json.dumps(gold_labels(spectrum), indent=2, ensure_ascii=False) + "\n"
        args.gold_out.parent.mkdir(parents=True, exist_ok=True)
        with args.gold_out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
