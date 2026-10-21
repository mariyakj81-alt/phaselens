#!/usr/bin/env python3
"""Digitize a calibrated Raman trace and measure peaks on the resulting spectrum.

This never applies peak finding to PDF text. Docling is used only for tables/text
when installed; plotted data require explicit pixel-axis calibration.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.signal import find_peaks, peak_widths


def docling_available(pdf: Path) -> bool:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        return False
    DocumentConverter().convert(pdf)
    return True


def digitize_plechinger_3l(png: Path) -> dict:
    """Red 3-layer trace, Fig. 1(b), p. 2, arXiv:1205.1916.

    x pixels 331..497 are calibrated to 13..47 cm^-1. Intensity is arbitrary
    pixel height, so it is demonstration-only and never a training label.
    """
    image = np.asarray(Image.open(png).convert("RGB"))
    x0, x1, y0, y1 = 331, 497, 260, 326
    crop = image[y0:y1, x0:x1]
    r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
    red = (r > 150) & (r > 1.35 * g) & (r > 1.35 * b) & (g < 180)
    trace_y = np.array([np.where(red[:, col])[0].min() if np.any(red[:, col]) else np.nan for col in range(red.shape[1])], dtype=float)
    good = np.isfinite(trace_y)
    if good.sum() < 3:
        raise RuntimeError("No trace recovered from calibrated crop")
    trace_y = np.interp(np.arange(trace_y.size), np.flatnonzero(good), trace_y[good])
    intensity = np.median(trace_y[-35:]) - trace_y
    shift = np.linspace(13.0, 47.0, intensity.size)
    indices, _ = find_peaks(intensity, prominence=8, distance=10)
    widths = peak_widths(intensity, indices, rel_height=0.5)[0]
    step = shift[1] - shift[0]
    peaks = [{"position_cm-1": round(float(shift[i]), 3), "height_arbitrary": round(float(intensity[i]), 3), "fwhm_cm-1": round(float(width * step), 3)} for i, width in zip(indices, widths)]
    return {"wavenumber_cm-1": shift.round(3).tolist(), "intensity_arbitrary": intensity.round(3).tolist(), "peaks": peaks}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = digitize_plechinger_3l(root / "tmp/pdfs/plechinger_p-2.png")
    result["docling_table_extraction_available"] = docling_available(root / "tmp/pdfs/plechinger_2012.pdf")
    result["source"] = {"doi": "10.1063/1.4751266", "page": 2, "figure": "Fig. 1(b)", "method": "calibrated figure digitization"}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
