"""Merge per-paper peak files into one CSV per mineral and check them against the protocol.

Usage: python -P scripts/merge_peaks.py calcite      (writes peaks/calcite_peaks.csv)
Problems are printed and written to peaks/<mineral>_problems.csv; the merge still runs.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLUMNS = ["material", "paper_id", "doi", "sample_id", "sample_description", "conditions", "laser_nm",
           "peak_cm1", "peak_uncertainty_cm1", "fwhm_cm1", "rel_intensity", "rel_area",
           "mode_label", "mode_symmetry", "mode_description", "assignment_source", "data_source",
           "location", "fit_r2", "notes"]
SOURCES = {"raw_fit", "table", "text", "figure_label", "figure_digitized"}
ASSIGNMENT = {"paper", "reference", "rule", ""}


def main(mineral):
    ref = json.loads((ROOT / "scripts" / "mode_reference.json").read_text())[mineral]
    modes = {m["label"]: m["position"] for reg in ref["regions"] for m in reg["modes"]}
    modes.update({reg["doublet"]["label"]: sum(m["position"] for m in reg["modes"]) / 2
                  for reg in ref["regions"] if "doublet" in reg})
    papers = pd.read_csv(ROOT / mineral / "papers.csv", dtype=str).fillna("")
    known = set(papers["paper_id"])

    frames, problems = [], []
    for f in sorted((ROOT / "peaks" / mineral).glob("*.csv")):
        if f.name == "extraction_status.csv":
            continue
        df = pd.read_csv(f, dtype=str).fillna("")
        if list(df.columns) != COLUMNS:
            problems.append((f.name, "", f"columns differ: {sorted(set(df.columns) ^ set(COLUMNS))}"))
            df = df.reindex(columns=COLUMNS).fillna("")
        frames.append(df)
    if not frames:
        raise SystemExit(f"no peak files in peaks/{mineral}/")
    df = pd.concat(frames, ignore_index=True)

    def bad(mask, msg):
        for _, r in df[mask].iterrows():
            problems.append((r["paper_id"], f"{r['sample_id']} @ {r['peak_cm1']}", msg))

    pos = pd.to_numeric(df["peak_cm1"], errors="coerce")
    bad(pos.isna(), "peak_cm1 is not a number")
    bad(df["material"] != mineral, "material column is wrong")
    bad(~df["paper_id"].isin(known), "paper_id not in papers.csv")
    bad(~df["data_source"].isin(SOURCES), "unknown data_source")
    bad(~df["assignment_source"].isin(ASSIGNMENT), "unknown assignment_source")
    bad(~df["mode_label"].isin(set(modes) | {"unassigned", "artifact"}), "mode_label not in mode_reference.json")
    bad(df["location"].str.strip() == "", "location is empty")
    expected = df["mode_label"].map(modes)
    far = (pos - expected).abs() > 30
    bad(far & ~df["conditions"].str.contains("GPa|kbar|K\\b|°C", regex=True), "more than 30 cm-1 from reference at ambient")
    bad(~df["laser_nm"].str.fullmatch(r"(\d+(\.\d*[1-9])?)?"), "laser_nm must be one plain number (e.g. 532, 514.5) or blank")
    nolabel = df["mode_label"].isin(["unassigned", "artifact"])
    bad(nolabel & (df["mode_symmetry"] != ""), "unassigned/artifact row has a mode_symmetry")
    bad((df["mode_label"] == "artifact") & (df["assignment_source"] != "rule"), "artifact row needs assignment_source=rule")
    key = ["paper_id", "sample_id", "laser_nm", "peak_cm1", "mode_label", "data_source", "location"]
    bad(df.duplicated(key, keep="first"), "duplicate row")
    # a resolved doublet is ordered by frequency: the lower line takes the first label
    for reg in ref["regions"]:
        if "doublet" not in reg:
            continue
        lo_lbl, hi_lbl = (m["label"] for m in reg["modes"])
        spec = ["paper_id", "sample_id", "laser_nm", "data_source", "location"]
        for _, g in df.assign(_p=pos).groupby(spec):
            lo, hi = g.loc[g["mode_label"] == lo_lbl, "_p"], g.loc[g["mode_label"] == hi_lbl, "_p"]
            if len(lo) and len(hi) and lo.max() > hi.min():
                r = g.iloc[0]
                problems.append((r["paper_id"], r["sample_id"], f"{lo_lbl} above {hi_lbl}: label the doublet by frequency"))
    bad(~df["paper_id"].str.fullmatch(r"(CAL|ANA)\d{3}"), "paper_id must have three digits")
    status_file = ROOT / "peaks" / mineral / "extraction_status.csv"
    if status_file.exists():
        st = pd.read_csv(status_file, dtype=str).fillna("")
        for pid in st.loc[st["paper_id"].duplicated(), "paper_id"].unique():
            problems.append((pid, "", "more than one line in extraction_status.csv"))
        counts = df["paper_id"].value_counts()
        for _, r in st.drop_duplicates("paper_id").iterrows():
            if r["n_rows"].isdigit() and int(r["n_rows"]) != counts.get(r["paper_id"], 0):
                problems.append((r["paper_id"], "", f"extraction_status n_rows {r['n_rows']} != {counts.get(r['paper_id'], 0)} rows"))
        for pid in sorted(set(df["paper_id"]) - set(st["paper_id"])):
            problems.append((pid, "", "no line in extraction_status.csv"))

    df["_pos"] = pos
    df = df.sort_values(["paper_id", "sample_id", "_pos"]).drop(columns="_pos")
    out = ROOT / "peaks" / f"{mineral}_peaks.csv"
    df.to_csv(out, index=False)
    pd.DataFrame(problems, columns=["paper_id", "row", "problem"]).to_csv(
        ROOT / "peaks" / f"{mineral}_problems.csv", index=False)

    print(f"{mineral}: {len(df)} rows from {df['paper_id'].nunique()} of {len(known)} papers -> {out.name}")
    missing = sorted(known - set(df["paper_id"]))
    print(f"papers with no rows: {', '.join(missing) or 'none'}")
    print("rows by data_source:", df["data_source"].value_counts().to_dict())
    stats = df.assign(p=pos).groupby("mode_label")["p"].describe()[["count", "min", "50%", "max"]]
    print(stats.round(1).to_string())
    print(f"{len(problems)} problems (see peaks/{mineral}_problems.csv)")
    for p in problems[:20]:
        print("  ", *p)


if __name__ == "__main__":
    main(sys.argv[1])
