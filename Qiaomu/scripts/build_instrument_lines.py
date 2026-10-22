"""Build data/mode_card_sources/instrument_lines.json (an input of scripts/build_mode_cards.py): laser plasma lines and the silicon line, as Raman shifts.

Gas lasers leak emission lines of their discharge. Without a clean-up filter these show up in a Raman
spectrum as narrow peaks at fixed Raman shifts, the "laser-plasma lines" of ARCHITECTURE.md. Line
wavelengths come from the NIST Atomic Spectra Database (air wavelengths, saved in data/reference/nist_asd/).
Raman shift = 1e7/laser_nm - 1e7/line_nm. NIST intensities rank lines within one spectrum only; which
lines are strong in a given laser tube varies, so treat the list as candidates.

Usage: python -P scripts/build_instrument_lines.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
NIST = ROOT / "data" / "reference" / "nist_asd"
LASERS = [  # laser, gas spectrum, NIST file, laser wavelength in air (nm)
    ("Ar+ 488.0 nm", "Ar II", "Ar_II_480-580nm.csv", 487.986),
    ("Ar+ 514.5 nm", "Ar II", "Ar_II_480-580nm.csv", 514.532),
    ("He-Ne 632.8 nm", "Ne I", "Ne_I_626-720nm.csv", 632.816),
    ("Kr+ 647.1 nm", "Kr II", "Kr_II_640-735nm.csv", 647.088),
]
NO_PLASMA = {"DPSS 532 nm": 532.0, "diode 785 nm": 785.0, "Nd:YAG 1064 nm (FT-Raman)": 1064.0}
TOP_N, SHIFT_RANGE = 8, (50, 2000)


def load(path):
    d = pd.read_csv(path, dtype=str).fillna("").apply(lambda c: c.str.strip('="'))
    wl = d["obs_wl_air(nm)"].where(d["obs_wl_air(nm)"] != "", d["ritz_wl_air(nm)"])
    return pd.DataFrame({"wl": pd.to_numeric(wl, errors="coerce"),
                         "intens": pd.to_numeric(d["intens"].str.extract(r"(\d+\.?\d*)")[0], errors="coerce")}).dropna()


def main():
    out = {"_note": __doc__.split("\n\n")[1].replace("\n", " "),
           "source": "NIST Atomic Spectra Database, https://physics.nist.gov/asd (air wavelengths)",
           "silicon_line": {"position_cm1": 520.7, "label": "artifact",
                            "note": "first-order Si optical phonon (F2g) from a Si or SiO2/Si substrate; "
                                    "see the team silicon card (repo-root mode_cards/silicon.json) for its source"},
           "laser_line": {"position_cm1": 0.0, "label": "artifact", "note": "Rayleigh line, seen when data start below the edge/notch filter"},
           "plasma_lines": {}, "lasers_without_plasma_lines": NO_PLASMA}
    for name, gas, fname, laser in LASERS:
        d = load(NIST / fname)
        d["shift"] = 1e7 / laser - 1e7 / d["wl"]
        w = d[(d["shift"] >= SHIFT_RANGE[0]) & (d["shift"] <= SHIFT_RANGE[1])].nlargest(TOP_N, "intens")
        out["plasma_lines"][name] = {
            "laser_nm_air": laser, "gas_spectrum": gas, "label": "artifact",
            "lines": [{"raman_shift_cm1": round(r.shift, 1), "line_nm_air": round(r.wl, 3), "nist_intensity": r.intens}
                      for r in w.sort_values("shift").itertuples()]}
    path = ROOT / "data" / "mode_card_sources" / "instrument_lines.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, v in out["plasma_lines"].items():
        print(f"{name}: " + ", ".join(str(l["raman_shift_cm1"]) for l in v["lines"]))
    print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
