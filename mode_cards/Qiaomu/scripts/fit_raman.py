"""Deconvolve a measured Raman spectrum into pseudo-Voigt peaks and assign them to calcite or anatase modes.

Each region in scripts/mode_reference.json is fitted on its own: a local linear background plus one
pseudo-Voigt per expected mode. A mode is reported only if its fitted height is above 3x the noise.
For the anatase 513/519 doublet, a one-peak and a two-peak model are compared by BIC.
Peaks left in the residual are fitted one by one and reported as "unassigned" with a hint.

Example:
  python -P scripts/fit_raman.py anatase/ANA005_Smith2019/data/spectra.csv --material anatase \
      --paper-id ANA005 --doi 10.1000/xyz --ycol all --laser 532 \
      --out peaks/raw_fits/ANA005.csv --plot-dir peaks/raw_fits/plots
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

REFERENCE = Path(__file__).with_name("mode_reference.json")
COLUMNS = ["material", "paper_id", "doi", "sample_id", "sample_description", "conditions", "laser_nm",
           "peak_cm1", "peak_uncertainty_cm1", "fwhm_cm1", "rel_intensity", "rel_area",
           "mode_label", "mode_symmetry", "mode_description", "assignment_source", "data_source",
           "location", "fit_r2", "notes"]
LN2 = np.log(2)


def pseudo_voigt(x, h, c, w, eta):
    u = (x - c) / w
    return h * (eta / (1 + 4 * u**2) + (1 - eta) * np.exp(-4 * LN2 * u**2))


def pv_area(h, w, eta):
    return h * w * (eta * np.pi / 2 + (1 - eta) * np.sqrt(np.pi / (4 * LN2)))


def region_model(x0):
    def f(x, a, b, *p):
        y = a + b * (x - x0)
        for i in range(0, len(p), 4):
            y = y + pseudo_voigt(x, *p[i:i + 4])
        return y
    return f


# ---------------------------------------------------------------- loading
def _to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _split(line):
    if "\t" in line or ";" in line:
        return [f.strip().replace(",", ".") for f in re.split(r"[\t;]+", line.strip())]
    return [f for f in re.split(r"[\s,]+", line.strip()) if f]


def load_rows(path, sheet=None):
    """Return a list of rows (lists of strings/numbers) from a text or Excel file."""
    if path.suffix.lower() in (".xlsx", ".xls", ".xlsm"):
        df = pd.read_excel(path, sheet_name=sheet if sheet is not None else 0, header=None)
        return df.values.tolist()
    text = path.read_text(encoding="utf-8", errors="replace")
    return [_split(ln) for ln in text.splitlines() if ln.strip()]


def load_spectra(path, xcol, ycol, sheet=None, skiprows=0):
    """Return (x, {name: y}) using the first block of numeric rows; the header is the last text row above it."""
    rows = load_rows(path, sheet)[skiprows:]
    header, data = None, []
    for row in rows:
        nums = [_to_float(v) for v in row]
        if sum(v is not None and np.isfinite(v) for v in nums) >= 2:
            data.append(nums)
        elif data:
            break  # stop at the end of the first numeric block
        else:
            header = [str(v) for v in row]
    width = max(len(r) for r in data)
    arr = np.array([r + [None] * (width - len(r)) for r in data], dtype=float)
    names = header if header and len(header) == width else [f"col{j}" for j in range(width)]

    def col_index(c):
        if isinstance(c, str) and not c.lstrip("-").isdigit():
            return names.index(c)
        return int(c)

    xi = col_index(xcol)
    if ycol == "all":
        yidx = [j for j in range(width) if j != xi]
    else:
        yidx = [col_index(c) for c in str(ycol).split(",")]
    spectra = {}
    for j in yidx:
        ok = np.isfinite(arr[:, xi]) & np.isfinite(arr[:, j])
        if ok.sum() > 20:
            spectra[names[j]] = (arr[ok, xi], arr[ok, j])
    return spectra


# ---------------------------------------------------------------- fitting
def noise_level(y):
    d = np.diff(y)
    return 1.4826 * np.median(np.abs(d - np.median(d))) / np.sqrt(2)


def fit_peaks(x, y, guesses, tol):
    """guesses: list of (center, center_lo, center_hi[, width]). Returns (params, errors, r2, bic, model) or None."""
    x0 = float(np.mean(x))
    p0, lo, hi = [float(np.min(y)), 0.0], [-np.inf, -np.inf], [np.inf, np.inf]
    span = np.ptp(y) or 1.0
    for g in guesses:
        c, clo, chi = g[:3]
        w0 = g[3] if len(g) > 3 else 8.0
        near = (x >= clo) & (x <= chi)
        cguess = float(x[near][np.argmax(y[near])]) if near.any() else c
        cguess = min(max(cguess, clo + 0.1), chi - 0.1)
        hguess = max(float(np.interp(cguess, x, y) - np.min(y)), 0.05 * span)
        p0 += [hguess, cguess, min(max(w0, 1.5), 79.0), 0.5]
        lo += [0.0, clo, 1.0, 0.0]
        hi += [np.inf, chi, 80.0, 1.0]
    f = region_model(x0)
    starts = [p0]
    if any(len(g) > 3 for g in guesses):  # also try the default starting width
        alt = list(p0)
        alt[4::4] = [8.0] * len(guesses)
        starts.append(alt)
    best = None
    for start in starts:
        try:
            p_try, cov_try = curve_fit(f, x, y, p0=start, bounds=(lo, hi), maxfev=20000)
        except (RuntimeError, ValueError):
            continue
        rss_try = float(np.sum((y - f(x, *p_try))**2))
        if best is None or rss_try < best[2]:
            best = (p_try, cov_try, rss_try)
    if best is None:
        return None
    p, cov, _ = best
    resid = y - f(x, *p)
    rss = float(np.sum(resid**2))
    tss = float(np.sum((y - y.mean())**2)) or 1.0
    n, k = len(x), len(p)
    bic = n * np.log(max(rss, 1e-30) / n) + k * np.log(n)
    err = np.sqrt(np.clip(np.diag(cov), 0, None)) if np.all(np.isfinite(cov)) else np.full(len(p), np.nan)
    return p, err, 1 - rss / tss, bic, f


def fit_region(xs, ys, reg, tol, noise, extras, warn=True):
    """Fit one region: its expected modes plus any extra peaks found there. Returns (components, r2, note, peak model, local background)."""
    extra_modes = [dict(label="unassigned", symmetry="", description="", position=c, extra=True) for c, _ in extras]
    # first-pass positions of extra peaks can be biased by a few cm-1, so give them +-10 in the joint fit
    extra_guesses = [(c, c - 10, c + 10, w) for c, w in extras]
    def fit_modes(modes):
        return fit_peaks(xs, ys, [(m["position"], m["position"] - m.get("tol", tol), m["position"] + m.get("tol", tol))
                                  for m in modes] + extra_guesses, tol)

    modes = [m for m in reg["modes"] if not m.get("paper_only")]
    fit = fit_modes(modes)
    if fit is None and any(m.get("optional") for m in modes):
        # a near-zero optional component can stall the optimiser; retry without it
        modes = [m for m in modes if not m.get("optional")]
        fit = fit_modes(modes)
    if fit is None:
        if warn:
            print(f"warning: fit failed in region {reg['range']}; its modes are missing from the output", file=sys.stderr)
        return [], 0.0, "", np.zeros_like(ys), np.zeros_like(ys)
    # an optional mode pinned at its window edge is fitting something else (e.g. a shoulder): drop it and refit
    pinned = [m for i, m in enumerate(modes) if m.get("optional")
              and abs(abs(fit[0][3 + 4 * i] - m["position"]) - m.get("tol", tol)) < 0.5]
    if pinned:
        modes = [m for m in modes if m not in pinned]
        fit = fit_modes(modes)
        if fit is None:
            if warn:
                print(f"warning: refit without optional modes failed in region {reg['range']}", file=sys.stderr)
            return [], 0.0, "", np.zeros_like(ys), np.zeros_like(ys)
    # an expected mode pinned at its window edge is usually soaking up an asymmetric tail of a neighbour:
    # add a free broad component there and keep it if BIC clearly improves
    # the tail may sit anywhere in the region (a neighbour's tail can lie well beyond the pinned mode's window)
    tails = [(fit[0][3 + 4 * i], float(xs.min()), float(xs.max()), max(fit[0][4 + 4 * i], 15))
             for i, m in enumerate(modes)
             if not m.get("optional") and abs(abs(fit[0][3 + 4 * i] - m["position"]) - m.get("tol", tol)) < 0.5]
    if tails:
        fit2 = fit_peaks(xs, ys, [(m["position"], m["position"] - m.get("tol", tol), m["position"] + m.get("tol", tol))
                                  for m in modes] + extra_guesses + tails, tol)
        if fit2 is not None and fit2[3] < fit[3] - 10:
            fit = fit2
            extra_guesses = extra_guesses + tails
            extra_modes = extra_modes + [dict(label="unassigned", symmetry="", description="", position=t[0],
                                              extra=True, tail=True) for t in tails]
    p, err, r2, bic, f = fit
    comps = modes + extra_modes
    note = ""
    if "doublet" in reg:
        mid = float(np.mean([m["position"] for m in modes]))
        single = fit_peaks(xs, ys, [(mid, mid - tol, mid + tol)] + extra_guesses, tol)
        hs, centers, widths = p[2:10:4], p[3:10:4], p[4:10:4]
        # two similar-width lines with a real gap; a narrow + broad pair at one centre is line shape, not a doublet
        resolved = ((single is None or bic < single[3] - 10) and min(hs) > 3 * noise
                    and max(3, 0.5 * min(widths)) < abs(centers[1] - centers[0]) < 15 and max(widths) < 3 * min(widths))
        if not resolved and single is not None:
            p, err, r2, bic, f = single
            comps = [dict(reg["doublet"], position=mid)] + extra_modes
            note = "doublet not resolved; one-peak model preferred by BIC"
        elif p[3] > p[7]:  # resolved: the lower-frequency line takes the first (lower) label
            comps[0], comps[1] = comps[1], comps[0]
    # the expected mode is the dominant peak near its reference position. Candidates are the mode's own
    # component (unless it is pinned at its window edge, i.e. soaking up a tail) and extra components in its
    # window, except a narrow line at the Si position. The strongest candidate takes the label.
    def si_like(k):
        return abs(p[3 + 4 * k] - 520.7) < 1.2 and p[4 + 4 * k] < 6

    for i, m in enumerate(comps):
        if m.get("extra"):
            continue
        t = m.get("tol", tol)
        own_pinned = abs(abs(p[3 + 4 * i] - m["position"]) - t) < 0.5
        cands = [j for j, e in enumerate(comps)
                 if abs(p[3 + 4 * j] - m["position"]) <= t and not si_like(j)
                 and ((j == i and not own_pinned) or (j != i and e.get("extra")))]
        if cands:
            best = max(cands, key=lambda k: p[2 + 4 * k])
            if best != i:
                comps[i], comps[best] = comps[best], m
    chosen = [(m, p[2 + 4 * i:6 + 4 * i], err[2 + 4 * i:6 + 4 * i]) for i, m in enumerate(comps)]
    background = p[0] + p[1] * (xs - np.mean(xs))
    return chosen, r2, note, f(xs, *p) - background, background


def hint_for(c, ref, reported):
    """Name the nearest known non-mode line, or an expected mode that was not reported, within 8 cm-1."""
    cands = list(ref.get("other_lines", []))
    cands += [dict(position=m["position"], hint=f"{m['label']} reference position")
              for reg in ref["regions"] for m in reg["modes"] if m["label"] not in reported]
    best = min(cands, key=lambda o: abs(o["position"] - c), default=None)
    return f"near {best['position']} ({best['hint']})" if best and abs(best["position"] - c) < 8 else ""


def flag_silicon(peaks, ref):
    """A narrow peak at 520.7 +- 1.2 cm-1 is the silicon substrate line, unless it is half of a resolved
    anatase doublet whose partner has a similar width (single-crystal anatase B1g(2) sits at ~519)."""
    for pk in peaks:
        if abs(pk["peak"] - 520.7) >= 1.2 or pk["fwhm"] >= 6:
            continue
        partners = [q for q in peaks if q is not pk and abs(q["peak"] - pk["peak"]) < 15]
        if partners and all(q["fwhm"] < 2 * pk["fwhm"] for q in partners):
            continue
        pk.update(label="artifact", symmetry="", description="silicon substrate line",
                  notes="narrow line at Si 520.7 cm-1")
    for reg in ref["regions"]:
        if "doublet" not in reg:
            continue
        labels = {m["label"] for m in reg["modes"]}
        left = [pk for pk in peaks if pk["label"] in labels]
        if len(left) == 1 and any(pk["label"] == "artifact" for pk in peaks):
            left[0].update(label=reg["doublet"]["label"], symmetry=reg["doublet"]["symmetry"],
                           description=reg["doublet"]["description"],
                           notes="doublet not resolved; Si line fitted separately")


def merge_tails(peaks, x):
    """A tail component that overlaps an expected mode is part of one asymmetric band. Report that band as
    papers do: position = maximum of the summed profile, FWHM = its full width at half maximum."""
    for t in [pk for pk in peaks if pk.get("tail")]:
        modes = [pk for pk in peaks if not pk.get("tail") and pk["label"] not in ("unassigned", "artifact")]
        if not modes:
            continue
        m = min(modes, key=lambda pk: abs(pk["peak"] - t["peak"]))
        if abs(m["peak"] - t["peak"]) > (m["fwhm"] + t["fwhm"]) / 2:
            continue  # separate band: keep the tail as its own unassigned peak
        grid = np.arange(min(x), max(x), 0.01)
        prof = pseudo_voigt(grid, m["height"], m["peak"], m["fwhm"], m["eta"]) +             pseudo_voigt(grid, t["height"], t["peak"], t["fwhm"], t["eta"])
        i = int(np.argmax(prof))
        above = grid[prof >= prof[i] / 2]
        m.update(peak=float(grid[i]), height=float(prof[i]), fwhm=float(above.max() - above.min()),
                 area=m["area"] + t["area"], components=[dict(m), dict(t)],
                 notes="; ".join(filter(None, [m["notes"], "asymmetric band: position and FWHM from the summed "
                                               f"profile of 2 components ({m['peak']:.1f}, {t['peak']:.1f})"])))
        peaks.remove(t)


def analyse(x, y, ref, tol, baseline, lam, min_rel=0.02):
    order = np.argsort(x)
    x, y = x[order], y[order]
    if baseline == "arpls":
        from pybaselines import Baseline
        bl, _ = Baseline(x_data=x).arpls(y, lam=lam)
        yc = y - bl
    else:
        bl, yc = np.zeros_like(y), y.copy()
    # smooth (processed or digitized) curves have almost no point-to-point noise; floor it at 0.1% of the range
    noise = max(noise_level(yc), 1e-3 * float(np.ptp(yc)))
    dx = float(np.median(np.diff(x)))
    regions = [(reg, (x >= reg["range"][0]) & (x <= reg["range"][1])) for reg in ref["regions"]]
    regions = [(reg, sel) for reg, sel in regions if sel.sum() >= 10]

    def run(extras, warn):
        peaks, model, background = [], np.zeros_like(yc), np.zeros_like(yc)
        for reg, sel in regions:
            inside = [(c, w) for c, w in extras if reg["range"][0] <= c <= reg["range"][1]]
            chosen, r2, note, contrib, bg = fit_region(x[sel], yc[sel], reg, tol, noise, inside, warn)
            model[sel] += contrib
            background[sel] = bg
            for m, (h, c, w, eta), ee in chosen:
                if h < 3 * noise or (m.get("optional") or m.get("extra")) and h < 4 * noise:
                    continue
                if m.get("extra") and w < 2 * dx or w < max(1.05, 1.5 * dx):
                    continue  # collapsed to the width limit: a spike or noise, not a band
                t = m.get("tol", tol)
                at_bound = not m.get("extra") and min(abs(c - m["position"] + t), abs(c - m["position"] - t)) < 0.5
                peaks.append(dict(peak=c, err=ee[1], fwhm=w, height=h, eta=eta, area=pv_area(h, w, eta), label=m["label"],
                                  tail=bool(m.get("tail")),
                                  symmetry=m["symmetry"], description=m["description"], r2=r2,
                                  notes="; ".join(filter(None, [note, "center at fit bound" if at_bound else "",
                                                               "broad component taking an asymmetric tail" if m.get("tail") else ""]))))
        return peaks, model, background

    # pass 1: expected modes only; then look for peaks left in the residual
    peaks, model, _ = run([], warn=False)
    resid = yc - model
    # smoothed or processed spectra have almost no point-to-point noise, so also require a minimum
    # height relative to the strongest expected mode
    floor = max(4 * noise, min_rel * max((pk["height"] for pk in peaks), default=0))
    idx, _ = find_peaks(resid, prominence=max(5 * noise, floor), distance=3)
    extras = []
    for i in idx:
        xc = x[i]
        if any(abs(xc - pk["peak"]) < max(0.75 * pk["fwhm"], 4) for pk in peaks) or any(abs(xc - c) < 4 for c, _ in extras):
            continue
        sel = (x >= xc - 25) & (x <= xc + 25)
        fit = fit_peaks(x[sel], resid[sel], [(xc, xc - 5, xc + 5)], 5) if sel.sum() >= 8 else None
        if fit is None:
            continue
        h, c, w, eta = fit[0][2:6]
        if h >= floor and w >= 2 * dx and fit[2] > 0.5:
            extras.append((float(c), float(w)))

    # pass 2: refit regions jointly with the extra peaks that fall inside them; fit the rest on their own
    peaks, model, background = run(extras, warn=True)
    for c0, w0 in extras:
        if any(reg["range"][0] <= c0 <= reg["range"][1] for reg, _ in regions):
            continue
        sel = (x >= c0 - 25) & (x <= c0 + 25)
        fit = fit_peaks(x[sel], yc[sel], [(c0, c0 - 5, c0 + 5, w0)], 5)
        if fit is None:
            continue
        p, err, r2, _, _ = fit
        h, c, w, eta = p[2:6]
        if h < floor or w < 2 * dx or r2 < 0.5:
            continue
        peaks.append(dict(peak=c, err=err[3], fwhm=w, height=h, eta=eta, area=pv_area(h, w, eta), label="unassigned",
                          symmetry="", description="", r2=r2, notes=""))

    merge_tails(peaks, x)

    # label pass, once every peak is known
    flag_silicon(peaks, ref)
    for pk in peaks:  # the laser (Rayleigh) line itself, when the data start below the notch
        if abs(pk["peak"]) < 15:
            pk.update(label="artifact", symmetry="", description="laser (Rayleigh) line", notes="peak at 0 cm-1")
    reported = {pk["label"] for pk in peaks}
    optional = {m["label"]: m for reg in ref["regions"] for m in reg["modes"] if m.get("optional")}
    for pk in peaks:
        if pk["label"] != "unassigned":
            continue
        m = next((m for lbl, m in optional.items() if lbl not in reported and abs(m["position"] - pk["peak"]) < m.get("tol", 5)), None)
        if m:
            pk.update(label=m["label"], symmetry=m["symmetry"], description=m["description"])
            reported.add(m["label"])
        else:
            pk["notes"] = "; ".join(filter(None, [pk["notes"], hint_for(pk["peak"], ref, reported)]))
    return x, y, bl, yc, sorted(peaks, key=lambda d: d["peak"]), noise, background


def plot(path, x, y, bl, yc, peaks, title, background=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    a1.plot(x, y, lw=0.8, label="raw")
    a1.plot(x, bl, lw=0.8, label="baseline")
    a1.legend(fontsize=8)
    a2.plot(x, yc, lw=0.8, color="k", label="baseline-corrected")
    comps = [pseudo_voigt(x, c["height"], c["peak"], c["fwhm"], c["eta"])
             for pk in peaks for c in pk.get("components", [pk])]
    for cmp in comps:
        a2.plot(x, cmp, lw=0.6, color="tab:blue", alpha=0.6)
    if comps:
        local = background if background is not None else 0
        a2.plot(x, np.sum(comps, axis=0) + local, lw=0.8, color="tab:orange", label="fit (peaks + local background)")
    a2.legend(fontsize=8)
    for pk in peaks:
        a2.axvline(pk["peak"], color="grey" if pk["label"] in ("unassigned", "artifact") else "r", lw=0.6, ls="--")
        a2.text(pk["peak"], pk["height"], f" {pk['label']}\n {pk['peak']:.1f}", fontsize=7, rotation=90, va="bottom")
    a2.set_xlabel("Raman shift (cm$^{-1}$)")
    a1.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--material", required=True, choices=["calcite", "anatase"])
    ap.add_argument("--paper-id", required=True)
    ap.add_argument("--doi", default="")
    ap.add_argument("--xcol", default="0")
    ap.add_argument("--ycol", default="1", help="column index/name, comma list, or 'all'")
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--skiprows", type=int, default=0)
    ap.add_argument("--x-unit", default="cm-1", choices=["cm-1", "nm"])
    ap.add_argument("--laser", type=float, default=None, help="laser wavelength in nm")
    ap.add_argument("--xrange", type=float, nargs=2, default=None)
    ap.add_argument("--baseline", default="arpls", choices=["arpls", "none"])
    ap.add_argument("--lam", type=float, default=1e5, help="arPLS smoothness")
    ap.add_argument("--tol", type=float, default=15, help="allowed shift of a mode from its reference (cm-1)")
    ap.add_argument("--min-rel", type=float, default=0.02,
                    help="extra (unexpected) peaks must reach this fraction of the strongest expected mode")
    ap.add_argument("--sample", default="", help="sample description (default: the spectrum's name)")
    ap.add_argument("--sample-id", default="", help="sample_id for a one-spectrum file (default: the file name)")
    ap.add_argument("--conditions", default="")
    ap.add_argument("--location", default="", help="where the data came from, e.g. 'SI Fig. S3 data'")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--plot-dir", type=Path, default=None)
    a = ap.parse_args()

    ref = json.loads(REFERENCE.read_text())[a.material]
    sheet = int(a.sheet) if a.sheet and a.sheet.isdigit() else a.sheet
    spectra = load_spectra(a.input, a.xcol, a.ycol, sheet, a.skiprows)
    if not spectra:
        raise SystemExit(f"no numeric spectrum found in {a.input}")
    rows = []
    for name, (x, y) in spectra.items():
        if a.x_unit == "nm":
            if not a.laser:
                raise SystemExit("--x-unit nm needs --laser")
            x = 1e7 / a.laser - 1e7 / x
        if a.xrange:
            keep = (x >= a.xrange[0]) & (x <= a.xrange[1])
            x, y = x[keep], y[keep]
        # a file with one spectrum is named after the file (column headers like "Intensity" repeat across
        # files); a multi-column file keeps its column headers
        if len(spectra) == 1:
            name = a.sample_id or a.input.stem
        elif re.fullmatch(r"col\d+", str(name)):
            name = f"{a.sample_id or a.input.stem}_{name}"
        x, y, bl, yc, peaks, noise, local_bg = analyse(x, y, ref, a.tol, a.baseline, a.lam, a.min_rel)
        if not peaks:
            print(f"[{name}] no peaks above noise")
            continue
        # relative intensities are scaled to the strongest mineral mode, not to Si or unassigned bands
        mineral = [p for p in peaks if p["label"] not in ("unassigned", "artifact")] or peaks
        hmax = max(p["height"] for p in mineral)
        amax = max(p["area"] for p in mineral)
        sid = re.sub(r"[^A-Za-z0-9._-]+", "_", str(name)).strip("_") or "spectrum"
        plot_name = f"{a.paper_id}_{sid}.png" if len(spectra) == 1 else f"{a.paper_id}_{a.input.stem}_{sid}.png"
        for p in peaks:
            rows.append(dict(material=a.material, paper_id=a.paper_id, doi=a.doi, sample_id=sid,
                             sample_description=a.sample or str(name), conditions=a.conditions,
                             laser_nm=f"{a.laser:g}" if a.laser else "", peak_cm1=round(p["peak"], 2),
                             peak_uncertainty_cm1=round(float(p["err"]), 2) if np.isfinite(p["err"]) else "",
                             fwhm_cm1=round(p["fwhm"], 2), rel_intensity=round(p["height"] / hmax, 3),
                             rel_area=round(p["area"] / amax, 3), mode_label=p["label"],
                             mode_symmetry=p["symmetry"], mode_description=p["description"],
                             assignment_source={"unassigned": "", "artifact": "rule"}.get(p["label"], "reference"),
                             data_source="raw_fit", location=a.location or a.input.as_posix(),
                             fit_r2=round(p["r2"], 4), notes=p["notes"]))
        if a.plot_dir:
            a.plot_dir.mkdir(parents=True, exist_ok=True)
            plot(a.plot_dir / plot_name, x, y, bl, yc, peaks, f"{a.paper_id} {name}", local_bg)
        print(f"[{name}] {len(peaks)} peaks: " + ", ".join(f"{p['label']}@{p['peak']:.1f}" for p in peaks))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=COLUMNS).to_csv(a.out, index=False)
    print(f"wrote {len(rows)} rows to {a.out}")


if __name__ == "__main__":
    main()
