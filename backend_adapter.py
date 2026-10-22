"""
backend_adapter.py  --  the ONLY file that knows about the Raman analysis code.

app.py calls analyze_spectrum() and renders the dict it returns. When the real
PhaseLens backend is ready, change the body of analyze_spectrum(); the output
format (see EMPTY_RESULT) and app.py stay the same.

Folder layout expected next to this file:
    examples/<name>.csv    columns: shift, intensity  (real spectra from the repo, e.g. RRUFF)
    results/<name>.json    saved pipeline output for that example (optional)
    images/<name>.png      saved vibration image (optional)
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
EXAMPLES_DIR = HERE / "examples"
RESULTS_DIR = HERE / "results"
IMAGES_DIR = HERE / "images"

PLACEHOLDER_NAME = "PLACEHOLDER (no saved examples found)"
SI_PEAK_CM1 = 520.7   # first-order Raman peak of crystalline silicon
SI_TOL_CM1 = 4.0


# ---------------------------------------------------------------- output format
def empty_result(name: str = "") -> dict:
    """The one consistent output format the app displays."""
    return {
        "name": name,
        "status": "none",          # "saved_result" | "placeholder" | "no_backend"
        "spectrum": {"shift": [], "raw": [], "corrected": None, "corrected_source": None},
        "peaks": [],               # dicts: position_cm1, intensity, symmetry, is_artifact, artifact_reason
        "interpretation": None,    # {"label": "Layer number", "value": "3", "note": "..."}
        "visualization": {"available": False, "image_path": None},
        "references": [],          # [{"citation": "...", "doi": "..."}]
        "warnings": [],
    }


# ---------------------------------------------------------------- inputs
def list_examples() -> list[str]:
    names = sorted(p.stem for p in EXAMPLES_DIR.glob("*.csv")) if EXAMPLES_DIR.exists() else []
    return names or [PLACEHOLDER_NAME]


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:, :2].copy()
    df.columns = ["shift", "intensity"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna().sort_values("shift")
    return df.reset_index(drop=True)


def load_example_spectrum(name: str) -> pd.DataFrame:
    if name == PLACEHOLDER_NAME:
        # Synthetic, clearly labelled placeholder so the UI can be tested.
        x = np.linspace(100, 1200, 800)
        y = 50 + 0.02 * x
        for c, h in [(250, 300), (520.7, 1500), (800, 200)]:
            y = y + h * np.exp(-0.5 * ((x - c) / 6) ** 2)
        df = pd.DataFrame({"shift": x, "intensity": y})
    else:
        df = _clean(pd.read_csv(EXAMPLES_DIR / f"{name}.csv"))
    df.attrs["name"] = name
    return df


def parse_uploaded_csv(data: bytes, filename: str = "upload") -> pd.DataFrame:
    """CSV with two columns: Raman shift (cm^-1), intensity. Header optional."""
    try:
        df = pd.read_csv(io.BytesIO(data))
        if pd.to_numeric(df.columns[0], errors="coerce") == pd.to_numeric(df.columns[0], errors="coerce"):
            df = pd.read_csv(io.BytesIO(data), header=None)   # first row was numbers, not a header
    except Exception as e:
        raise ValueError(f"Could not read CSV: {e}")
    df = _clean(df)
    if len(df) < 10:
        raise ValueError("CSV needs two numeric columns (shift, intensity) with at least 10 rows.")
    df.attrs["name"] = f"upload:{filename}"
    return df


# ---------------------------------------------------------------- helpers
def _estimate_baseline(shift: np.ndarray, y: np.ndarray, deg: int = 3, iters: int = 30) -> np.ndarray:
    """Simple iterative polynomial baseline (app-side fallback, NOT the pipeline's correction)."""
    base = y.copy()
    for _ in range(iters):
        coef = np.polyfit(shift, base, deg)
        fit = np.polyval(coef, shift)
        base = np.minimum(base, fit)
    return np.polyval(np.polyfit(shift, base, deg), shift)


def _find_peaks(shift: np.ndarray, y: np.ndarray, rel_height: float = 0.08) -> list[dict]:
    """Very simple local-maximum finder, used only for uploads with no backend connected."""
    span = y.max() - y.min()
    if span <= 0:
        return []
    out = []
    for i in range(2, len(y) - 2):
        if y[i] == y[i - 2:i + 3].max() and y[i] - y.min() > rel_height * span:
            out.append({"position_cm1": float(shift[i]), "intensity": float(y[i])})
    return out


def _mark_artifacts(peaks: list[dict]) -> None:
    for p in peaks:
        p.setdefault("is_artifact", False)
        p.setdefault("artifact_reason", "")
        if abs(p["position_cm1"] - SI_PEAK_CM1) <= SI_TOL_CM1 and not p["is_artifact"]:
            p["is_artifact"] = True
            p["artifact_reason"] = "Silicon substrate (~520.7 cm^-1)"


def _pick(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def _normalize_saved(raw: dict, res: dict) -> None:
    """Map a saved pipeline JSON onto the standard format. Tolerates a few key spellings."""
    for p in _pick(raw, "peaks", "modes", default=[]):
        res["peaks"].append({
            "position_cm1": float(_pick(p, "position_cm1", "position", "shift", "frequency", "freq")),
            "intensity": _pick(p, "intensity", "height", "amplitude"),
            "symmetry": _pick(p, "symmetry", "symmetry_label", "irrep", "assignment", default="unassigned"),
            "is_artifact": bool(_pick(p, "is_artifact", "artifact", default=False)),
            "artifact_reason": _pick(p, "artifact_reason", "artifact_type", default=""),
        })
    interp = _pick(raw, "interpretation", "material_interpretation")
    if interp is None:
        for key, label in [("layer_number", "Layer number"), ("layers", "Layer number"), ("strain", "Strain")]:
            if key in raw:
                interp = {"label": label, "value": str(raw[key]), "note": ""}
                break
    res["interpretation"] = interp
    for r in _pick(raw, "references", "citations", default=[]):
        res["references"].append(r if isinstance(r, dict) else {"citation": str(r), "doi": ""})
    corr = _pick(raw, "corrected", "background_corrected", "corrected_intensity")
    if corr is not None:
        res["spectrum"]["corrected"] = list(corr)
        res["spectrum"]["corrected_source"] = "pipeline"


# ---------------------------------------------------------------- the function the app calls
def analyze_spectrum(spectrum: pd.DataFrame, mode_card=None, cif=None) -> dict:
    """
    spectrum  : DataFrame with columns shift, intensity (spectrum.attrs["name"] identifies it)
    mode_card : (later) parsed JSON mode card
    cif       : (later) crystal structure file contents

    TODO (backend connected): replace the body below with a call into the real
    PhaseLens pipeline and fill the same dict from empty_result().
    """
    name = spectrum.attrs.get("name", "")
    res = empty_result(name)
    shift = spectrum["shift"].to_numpy(float)
    y = spectrum["intensity"].to_numpy(float)
    res["spectrum"]["shift"] = shift.tolist()
    res["spectrum"]["raw"] = y.tolist()

    saved = RESULTS_DIR / f"{name}.json"
    if name == PLACEHOLDER_NAME:
        res["status"] = "placeholder"
        res["warnings"].append("PLACEHOLDER DATA: synthetic spectrum, not a real measurement or result.")
        res["peaks"] = [{"position_cm1": p["position_cm1"], "intensity": p["intensity"],
                         "symmetry": "placeholder"} for p in _find_peaks(shift, y)]
    elif saved.exists():
        res["status"] = "saved_result"
        _normalize_saved(json.loads(saved.read_text()), res)
    else:
        res["status"] = "no_backend"
        res["warnings"].append("No saved pipeline result for this spectrum, and the backend is not connected yet. "
                               "Peaks below are simple local maxima with no symmetry assignment.")
        res["peaks"] = [{**p, "symmetry": "unassigned"} for p in _find_peaks(shift, y)]

    if res["spectrum"]["corrected"] is None:
        res["spectrum"]["corrected"] = (y - _estimate_baseline(shift, y)).tolist()
        res["spectrum"]["corrected_source"] = "app polynomial estimate (not from pipeline)"

    if res["status"] != "saved_result":
        _mark_artifacts(res["peaks"])

    img = IMAGES_DIR / f"{name}.png"
    if img.exists():
        res["visualization"] = {"available": True, "image_path": str(img)}
    return res
