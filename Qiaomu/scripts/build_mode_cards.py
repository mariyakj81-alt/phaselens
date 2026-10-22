"""Build the calcite and anatase mode cards in the team's schema 2.1 (same layout as the repo-root mode_cards/mos2.json, silicon.json).

Inputs
- data/mode_card_sources/primary_v1/<material>_v1.json: the checked one-paper card (expected positions copied from
  the primary source paper, verified against its table; see data/mode_card_sources/CHECK.md).
- <material>/papers.csv and peaks/<material>_peaks.csv: every collected paper and every extracted peak.
- data/mode_card_sources/instrument_lines.json: Si line and laser plasma lines (NIST ASD).

Outputs
- mode_cards_comprehensive/<material>_comprehensive.json (about 1 MB) with
- curated_expected_modes: one entry per Raman-active mode, position from the primary paper, plus the
  spread of that mode over all papers (literature_summary);
- studies: every paper, its spectra (one per sample/condition/laser) and all peaks;
- cross_paper_summary: agreement (per-mode statistics), conflicts and missing items.
- mode_cards_simplified/<material>.json, the default card (a few tens of KB, sized like the team's cards): the same sections, but
  studies cut to the single most trusted paper (the primary paper the curated positions come from), and plasma
  lines only for that paper's laser.
  Use the simplified card as Qwen's context (ARCHITECTURE.md step 4). An identical copy is written to the
  repo-root team folder: mode_cards/<material>.json (simplified) and mode_cards/<material>_comprehensive.json;
  no other file in that folder is touched.
  Paths inside the cards (CIF, NIST files) are relative to the repo root, so every copy reads the same.

Usage: python -P scripts/build_mode_cards.py
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "mode_card_sources"
FULL_DIR = ROOT / "mode_cards_comprehensive"
SIMPLE_DIR = ROOT / "mode_cards_simplified"
TEAM_DIR = ROOT.parent / "mode_cards"  # repo-root team folder: only <material>.json and <material>_comprehensive.json are written there

VALUE_TYPE = {"table": "reported", "text": "reported", "figure_label": "reported_figure_label",
              "figure_digitized": "digitized", "raw_fit": "fitted_from_deposited_spectrum"}
SPEC = {
    "calcite": dict(
        material="calcite (CaCO3)", phase="calcite", spg="R-3c", spg_no=167,
        factor_group="Gamma(optical) = A1g + 4Eg (Raman) + 3A2u + 5Eu (IR only) + 3A2g + 2A1u (inactive), D3d, Z = 2",
        ir_only=["A2u", "Eu"], inactive=["A2g", "A1u"],
        confounders=["Mg substitution (all bands shift up)", "pressure (calcite-II/III above ~1.5 GPa)", "temperature",
                     "polymorph mixtures (aragonite, vaterite) and dolomite", "biogenic organic matrix / fluorescence",
                     "carbon and oxygen isotopes", "spectrometer calibration offsets"],
        keywords={"Mg substitution": r"\bMg\b|MgCO3|magnesian", "pressure": r"GPa|kbar", "temperature": r"\d+\s*K\b(?<!298 K)|°C",
                  "biogenic": r"biogenic|shell|skeleton|coral|barnacle|ossicle|bacteria|biofilm", "isotope": r"13C|18O|isotop"},
        conflicts=["CAL029 prints 262 cm-1 for Eg(L) in the text; its figure shows 282 (likely typo; both rows kept, flagged).",
                   "CAL049 room-temperature rows sit 7-12 cm-1 above the matching 5% CO2 rows (flagged in notes).",
                   "CAL018, CAL030 (S4, S9), CAL031 (S17) deposited spectra carry calibration offsets of 1-6 cm-1 (noted per row).",
                   "CAL005's 9.9 mol% Mg-calcite repeats CAL003 sample 17A; CAL035 repeats CAL008 (same labs)."],
        missing=["Papers CAL068-CAL100 were not collected (stopped at 67 papers).",
                 "Open-access temperature series and polarized single-crystal studies are scarce (most are paywalled).",
                 "Round-2 papers (CAL034-CAL067) have extractor self-checks but no independent review sample yet."]),
    "anatase": dict(
        material="anatase (TiO2)", phase="anatase", spg="I4_1/amd", spg_no=141,
        factor_group="Gamma(optical) = A1g + 2B1g + 3Eg (Raman) + A2u + 2Eu (IR only) + B2u (inactive), D4h, primitive cell 2 TiO2",
        ir_only=["A2u", "Eu"], inactive=["B2u"],
        confounders=["crystallite size (phonon confinement: Eg(1) shifts up and broadens)", "doping and oxygen vacancies",
                     "temperature", "rutile/brookite mixtures", "Si substrate line at 520.7 on the 513-519 doublet",
                     "laser heating", "spectrometer calibration offsets"],
        keywords={"particle size": r"\bnm\b|size|nano", "doping": r"dop|=\s*\d+(\.\d+)?\s*(wt|at|mol)?\s*%|Zr=|Fe|Co|Cu|Sn|La|Ce|Eu|Hf|Nb|Ta|Ag|N-",
                  "temperature": r"\d+\s*K\b|°C|in situ", "rutile mixture": r"rutile|brookite", "oxygen vacancies": r"vacanc|reduced|blue"},
        conflicts=["Order of the A1g/B1g(2) pair near 513/519 is disputed: Ohsaka 1978 puts A1g lower (used as this dataset's labelling convention); "
                   "polarized single-crystal work (Giarola 2010, ANA068) puts A1g higher. Paper labels are kept in notes.",
                   "ANA034 reports every mode 8-13 cm-1 below the usual positions; ANA080 and ANA097 are 3-7 cm-1 low (copied as printed).",
                   "ANA032 deposited furnace spectra read 3-10 cm-1 low (calibration).",
                   "ANA005 re-analyses literature data that overlap ANA001 (flagged 'same data as')."],
        missing=["ANA088 has no spontaneous-Raman peaks (only 2D-correlation values) and needs a replacement paper.",
                 "No open-access in situ high-pressure or 18O-isotope anatase Raman paper was found (APS/ACS/RSC paywalls).",
                 "Round-2 papers (ANA034-ANA100) have extractor self-checks but no independent review sample yet."]),
}


def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() and "." not in str(v) else f
    except (TypeError, ValueError):
        return None


def page_of(loc):
    m = re.search(r"\bp\.?\s*(\d+)", loc)
    return int(m.group(1)) if m else None


def build(material):
    spec = SPEC[material]
    v1 = json.loads((SOURCES / "primary_v1" / f"{material}_v1.json").read_text(encoding="utf-8"))
    papers = pd.read_csv(ROOT / material / "papers.csv", dtype=str).fillna("").set_index("paper_id")
    peaks = pd.read_csv(ROOT / "peaks" / f"{material}_peaks.csv", dtype=str).fillna("")
    il = json.loads((SOURCES / "instrument_lines.json").read_text(encoding="utf-8"))
    cite = v1["citation"]
    prim_doi = cite.get("doi") or None
    prim_prov = {"doi": prim_doi, "url": cite.get("url"), "paper_id": cite["paper_id"],
                 "page": page_of(cite["table_used"]), "figure_or_table": cite["table_used"]}

    # literature spread per mode, from measured spontaneous-Raman rows that are training eligible
    pos = pd.to_numeric(peaks["peak_cm1"], errors="coerce")
    stats = {}
    for label, g in peaks.assign(p=pos).groupby("mode_label"):
        if label in ("unassigned", "artifact"):
            continue
        stats[label] = {"n_peaks": int(g["p"].notna().sum()), "n_papers": int(g["paper_id"].nunique()),
                        "median_cm-1": round(float(g["p"].median()), 1),
                        "p10_cm-1": round(float(g["p"].quantile(0.1)), 1), "p90_cm-1": round(float(g["p"].quantile(0.9)), 1),
                        "min_cm-1": round(float(g["p"].min()), 1), "max_cm-1": round(float(g["p"].max()), 1)}

    curated, modes = [], []
    for m in v1["modes"]:
        width = m.get("halfwidth_cm1", m.get("hwhm_cm1"))
        curated.append({
            "phase": spec["phase"], "mode": m["id"], "symmetry": m["symmetry"], "position_cm-1": m["position_cm1"],
            "position_uncertainty_cm-1": 1 if material == "calcite" and m["position_cm1"] is not None else None,
            "width_cm-1": width, "width_type": "halfwidth as printed (FWHM in the paper's usage)" if material == "calcite" else "HWHM as printed",
            "paper_label": m["paper_label"], "motion": m["motion"],
            "source_verified": m["position_cm1"] is not None, "training_eligible": m["position_cm1"] is not None,
            "provenance": prim_prov if m["position_cm1"] is not None else None,
            "literature_summary": stats.get(m["id"])})
        modes.append({"mode": m["id"], "symmetry": m["symmetry"], "raman_activity": "active" if "overtone" not in m["symmetry"] else "second-order",
                      "training_eligible": m["position_cm1"] is not None})

    plasma = [{"laser_wavelength_nm": v["laser_nm_air"], "position_cm-1": l["raman_shift_cm1"], "instrument": f"{name} laser ({v['gas_spectrum']} line {l['line_nm_air']} nm)",
               "source_verified": True, "training_eligible": False,
               "provenance": {"source": "NIST Atomic Spectra Database", "file": "Qiaomu/data/reference/nist_asd/"}}
              for name, v in il["plasma_lines"].items() for l in v["lines"]]

    studies = []
    for pid, g in peaks.groupby("paper_id", sort=True):
        p = papers.loc[pid] if pid in papers.index else None
        doi = (p["doi"] if p is not None else g["doi"].iloc[0]) or None
        cond_text = " ; ".join(sorted(set(g["conditions"])))
        conf = [k for k, rx in spec["keywords"].items() if re.search(rx, cond_text + " " + " ".join(g["sample_description"]), re.I)]
        spectra = []
        for (sid, laser), s in g.groupby(["sample_id", "laser_nm"], sort=False):
            spectra.append({
                "sample_id": sid, "sample_description": s["sample_description"].iloc[0],
                "conditions": s["conditions"].iloc[0], "laser_wavelength_nm": num(laser),
                "peaks": [{
                    "position_cm-1": num(r.peak_cm1), "position_uncertainty_cm-1": num(r.peak_uncertainty_cm1),
                    "height": num(r.rel_intensity), "height_units": "relative to strongest mode of this spectrum" if r.rel_intensity else None,
                    "fwhm_cm-1": num(r.fwhm_cm1), "mode": r.mode_label, "symmetry": r.mode_symmetry or None,
                    "raman_activity": {"artifact": "artifact", "unassigned": "unassigned"}.get(r.mode_label, "second-order" if "overtone" in r.mode_symmetry else "active"),
                    "phase": spec["phase"],
                    "training_eligible": r.mode_label not in ("unassigned", "artifact") and r.data_source != "figure_digitized",
                    "value_type": VALUE_TYPE.get(r.data_source, r.data_source), "assignment_source": r.assignment_source,
                    "provenance": {"page": page_of(r.location), "figure_or_table": r.location},
                    "notes": r.notes or None} for r in s.itertuples()]})
        studies.append({
            "paper_id": pid, "doi": doi,
            "citation": f"{p['first_author']} et al., {p['journal']} ({p['year']}). {p['title']}" if p is not None else None,
            "source": (p["source_urls"].split(";")[0].strip() or None) if p is not None else None,
            "source_verified": bool(p is not None and p["pdf_status"] != "needs_manual"),
            "sample": {"phase": spec["phase"], "orientation": None, "confounders": conf},
            "conditions": {"laser_wavelength_nm": sorted({num(x) for x in g["laser_nm"] if x}) or None, "laser_power_mw": None,
                           "temperature": None, "room_temperature_confirmed": None, "wavenumber_calibration": None,
                           "instrument_resolution_cm-1": None, "substrate": None},
            "spectra": spectra,
            "training_eligible": bool(any(pk["training_eligible"] for sp in spectra for pk in sp["peaks"]))})

    n_rows = len(peaks)
    agreement = [f"{k}: {v['n_peaks']} peaks from {v['n_papers']} papers, median {v['median_cm-1']} cm-1 "
                 f"(10-90% range {v['p10_cm-1']}-{v['p90_cm-1']})" for k, v in stats.items()]
    card = {
        "schema_version": "2.1",
        "material": spec["material"],
        "point_group": v1["point_group"],
        "symmetry_validation": {
            "method": "spglib 2.8.0 on the COD crystal structure; phonon irreps from factor-group analysis (literature-backed, not inferred by spglib)",
            "structure": {"space_group": spec["spg"], "space_group_number": spec["spg_no"],
                          "point_group": v1["point_group_status"].split("point group ")[-1].split(":")[0],
                          "spglib_verified": True, "cif": f"Qiaomu/structures/{material}.cif",
                          "cod_id": re.search(r"COD (\d+)", v1["point_group_status"]).group(1)},
            "literature_symmetry_table": {
                "doi": None, "source": "factor-group analysis (Rousseau, Bauman & Porto 1981, J. Raman Spectrosc. 10, 253)",
                "raman_active": sorted({m["symmetry"] for m in v1["modes"] if "overtone" not in m["symmetry"] and "+" not in m["symmetry"]}),
                "silent_modes": spec["inactive"], "ir_only_modes": spec["ir_only"],
                "notes": spec["factor_group"]}},
        "curated_expected_modes": curated,
        "artifact_lines": {
            "substrate_raman": [{"material": "Si-I", "position_cm-1": 520.2, "symmetry": "F2g", "role": "substrate/reference",
                                 "provenance": {"doi": "10.1103/PhysRev.155.712", "page": 712, "figure_or_table": "abstract (see the team silicon card, repo-root mode_cards/silicon.json)"}}],
            "laser_dependent_plasma_or_stray_light": plasma,
            "laser_line": {"position_cm-1": 0.0, "role": "Rayleigh line when data start below the edge filter"}},
        "modes": modes,
        "studies": studies,
        "cross_paper_summary": {"agreement": agreement, "conflicts": spec["conflicts"], "missing": spec["missing"]},
        "confounders": spec["confounders"],
        "dataset_notes": [
            f"curated_expected_modes come from one primary paper ({cite['primary']}), checked number by number (Qiaomu/data/mode_card_sources/CHECK.md); "
            "human teammate sign-off pending.",
            f"studies hold every collected paper: {len(studies)} papers, {n_rows} peaks, extracted by the rules in scripts/EXTRACTION_PROTOCOL.md.",
            "training_eligible is false for unassigned peaks, artifacts and digitized-from-plot values.",
            "Calcite is the held-out test material in README.md: use calcite studies for testing, not training." if material == "calcite" else
            "Mode names (Eg(1), A1g+B1g(2), ...) match the mode_label column of peaks/anatase_peaks.csv.",
            "Sources were found with OpenAlex, Europe PMC, Crossref and web search; Valency was blocked by organization policy."] + v1["notes"],
    }
    FULL_DIR.mkdir(exist_ok=True)
    out = FULL_DIR / f"{material}_comprehensive.json"
    text = json.dumps(card, indent=1, ensure_ascii=False) + "\n"
    out.write_text(text, encoding="utf-8")
    TEAM_DIR.mkdir(exist_ok=True)
    (TEAM_DIR / out.name).write_text(text, encoding="utf-8")
    print(f"{material}: {len(curated)} curated modes, {len(studies)} studies, "
          f"{sum(len(s['spectra']) for s in studies)} spectra, {n_rows} peaks -> {out.relative_to(ROOT)}")


# Simplified cards: same schema, but sized like the team's cards in the repo-root mode_cards/.
# studies keeps one paper: the primary source of curated_expected_modes, whose numbers were checked against its
# table (data/mode_card_sources/CHECK.md); (paper_id, sample_id, value_type or None)
SIMPLE_PICKS = {
    "calcite": [("CAL003", "Calcite", None)],   # Bischoff, Sharma & Mackenzie 1985, Table 1, pure calcite, 488 nm
    "anatase": [("ANA069", "S532", None)],      # Ishioka et al. 2012, Table I, natural single crystal, 532 nm
}


def simplify(material):
    full = json.loads((FULL_DIR / f"{material}_comprehensive.json").read_text(encoding="utf-8"))
    by_id = {s["paper_id"]: s for s in full["studies"]}
    studies = []
    for pid, sid, vtype in SIMPLE_PICKS[material]:
        s = by_id[pid]
        sp = next(x for x in s["spectra"] if x["sample_id"] == sid)
        peaks = [{k: v for k, v in p.items() if k != "notes"} for p in sp["peaks"]
                 if p["training_eligible"] and (vtype is None or p["value_type"] == vtype)]
        studies.append({**{k: s[k] for k in ("paper_id", "doi", "citation", "source", "source_verified", "sample")},
                        "conditions": {**s["conditions"], "laser_wavelength_nm": sp["laser_wavelength_nm"]},
                        "spectra": [{"sample_id": sid, "sample_description": sp["sample_description"], "peaks": peaks}],
                        "training_eligible": True})
    primary_laser = next(s["conditions"]["laser_wavelength_nm"] for s in studies)
    plasma = [l for l in full["artifact_lines"]["laser_dependent_plasma_or_stray_light"]
              if primary_laser and abs(l["laser_wavelength_nm"] - primary_laser) < 1]
    card = {
        "schema_version": full["schema_version"],
        "material": full["material"],
        "point_group": full["point_group"],
        "symmetry_validation": full["symmetry_validation"],
        "curated_expected_modes": [{k: v for k, v in e.items() if k != "width_type"} for e in full["curated_expected_modes"]],
        "artifact_lines": {"substrate_raman": full["artifact_lines"]["substrate_raman"],
                           "laser_dependent_plasma_or_stray_light": plasma or [
                               {"laser_wavelength_nm": primary_laser, "position_cm-1": None, "instrument": "solid-state laser, no plasma lines",
                                "source_verified": True, "training_eligible": False}]},
        "modes": full["modes"],
        "studies": studies,
        "cross_paper_summary": full["cross_paper_summary"],
        "confounders": full["confounders"],
        "dataset_notes": [f"Simplified card: one study, the most trusted paper (the checked primary source of curated_expected_modes). "
                          f"The comprehensive card with every paper "
                          f"({len(full['studies'])} studies) is Qiaomu/mode_cards_comprehensive/{material}_comprehensive.json.",
                          "literature_summary in each curated mode is computed over all papers in the full card.",
                          full["dataset_notes"][0]],
    }
    out = SIMPLE_DIR / f"{material}.json"
    out.parent.mkdir(exist_ok=True)
    text = json.dumps(card, indent=2, ensure_ascii=False) + "\n"
    out.write_text(text, encoding="utf-8")
    # identical copy in the repo-root team folder (the comprehensive copy is written by build())
    (TEAM_DIR / out.name).write_text(text, encoding="utf-8")
    print(f"simplified {material}: {len(studies)} studies, {sum(len(s['spectra'][0]['peaks']) for s in studies)} peaks, "
          f"{out.stat().st_size // 1024} KB -> {out.relative_to(ROOT)} and ../mode_cards/{out.name}")


if __name__ == "__main__":
    for m in SPEC:
        build(m)
        simplify(m)
