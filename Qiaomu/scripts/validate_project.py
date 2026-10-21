"""Check that the literature dataset hangs together: bibliography, paper folders, PDFs, peak files, status lines.

Usage: python -P scripts/validate_project.py [--no-pdf]
Peak rows themselves are checked by scripts/merge_peaks.py; run both before committing.
Exit code 1 if any problem is found.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PREFIX = {"calcite": "CAL", "anatase": "ANA"}  # literature collections with peak tables
REFERENCE = {"mos2": "MOS", "quartz": "QTZ", "silicon": "SIL"}  # one source paper per mode card, no peak tables
PAPER_COLUMNS = ["paper_id", "folder", "doi", "title", "first_author", "year", "journal", "open_access",
                 "raman_evidence", "laser_nm", "sample_description", "peak_table", "raw_data", "pdf_status",
                 "si_files", "data_files", "source_urls", "found_via", "notes"]


def check_pdf(path):
    import fitz
    if path.read_bytes()[:5] != b"%PDF-":
        return "does not start with %PDF"
    try:
        return "" if fitz.open(path).page_count > 0 else "has no pages"
    except Exception as e:  # damaged file
        return f"does not open ({e})"


def check_mineral(mineral, problems, check_pdfs, with_peaks=True):
    pre = {**PREFIX, **REFERENCE}[mineral]
    p = pd.read_csv(ROOT / mineral / "papers.csv", dtype=str).fillna("")
    add = lambda pid, msg: problems.append((mineral, pid, msg))

    if list(p.columns) != PAPER_COLUMNS:
        add("", f"papers.csv columns differ: {sorted(set(p.columns) ^ set(PAPER_COLUMNS))}")
    ids = list(p["paper_id"])
    for pid in ids:
        if not re.fullmatch(rf"{pre}\d{{3}}", pid):
            add(pid, "paper_id must be the mineral prefix plus three digits")
    for pid in sorted({i for i in ids if ids.count(i) > 1}):
        add(pid, "paper_id appears more than once")
    nums = sorted(int(i[3:]) for i in ids if re.fullmatch(rf"{pre}\d{{3}}", i))
    gaps = sorted(set(range(1, max(nums, default=0) + 1)) - set(nums))
    if gaps:
        add("", f"IDs are not contiguous; missing {', '.join(f'{pre}{g:03d}' for g in gaps)}")
    doi = p["doi"].str.lower().str.strip()
    for d in sorted(set(doi[doi.duplicated() & (doi != "")])):
        add(", ".join(p.loc[doi == d, "paper_id"]), f"DOI {d} appears more than once")
    title = p["title"].str.lower().str.replace(r"\W+", " ", regex=True).str.strip()
    for t in sorted(set(title[title.duplicated() & (title != "")])):
        add(", ".join(p.loc[title == t, "paper_id"]), "same title appears more than once")
    rej = ROOT / mineral / "candidates_rejected.csv"
    if rej.exists():
        rejected = set(pd.read_csv(rej, dtype=str).fillna("")["doi"].str.lower().str.strip()) - {""}
        for d in sorted(set(doi) & rejected):
            add(", ".join(p.loc[doi == d, "paper_id"]), f"kept paper {d} is also in candidates_rejected.csv")

    status = ROOT / "peaks" / mineral / "extraction_status.csv"
    status_ids = set(pd.read_csv(status, dtype=str)["paper_id"]) if status.exists() else set()
    for _, r in p.iterrows():
        folder = ROOT / r["folder"]
        if not folder.is_dir():
            add(r["paper_id"], f"folder {r['folder']} is missing")
            continue
        if not folder.name.startswith(r["paper_id"] + "_"):
            add(r["paper_id"], f"folder name {folder.name} does not start with the paper_id")
        pdf = folder / "paper.pdf"
        if r["pdf_status"] == "needs_manual":
            if pdf.exists():
                add(r["paper_id"], "pdf_status is needs_manual but paper.pdf exists")
        elif not pdf.exists():
            add(r["paper_id"], "paper.pdf is missing")
        elif check_pdfs and (msg := check_pdf(pdf)):
            add(r["paper_id"], f"paper.pdf {msg}")
        for f in [x for x in (r["si_files"] + ";" + r["data_files"]).split(";") if x.strip()]:
            if not (ROOT / f).exists():
                add(r["paper_id"], f"listed file is missing: {f}")
        if with_peaks and not (ROOT / "peaks" / mineral / f"{r['paper_id']}.csv").exists():
            add(r["paper_id"], "no peak file in peaks/" + mineral)
        if with_peaks and r["paper_id"] not in status_ids:
            add(r["paper_id"], "no line in extraction_status.csv")

    listed = {Path(f).name for f in p["folder"]}
    for d in (ROOT / mineral).iterdir():
        if d.is_dir() and d.name not in listed:
            add("", f"folder {mineral}/{d.name} is not in papers.csv")
    for f in (ROOT / "peaks" / mineral).glob(f"{pre}*.csv") if with_peaks else []:
        if f.stem not in set(ids):
            add(f.stem, "peak file has no row in papers.csv")
    return p


def main():
    check_pdfs = "--no-pdf" not in sys.argv
    problems, dois = [], {}
    for mineral in PREFIX:
        p = check_mineral(mineral, problems, check_pdfs)
        dois[mineral] = set(p["doi"].str.lower().str.strip()) - {""}
        print(f"{mineral}: {len(p)} papers, {(p['pdf_status'] != 'needs_manual').sum()} with PDF, "
              f"{(p['si_files'] != '').sum()} with SI files, {(p['raw_data'] == 'Y').sum()} with raw data")
    for material in REFERENCE:
        if (ROOT / material / "papers.csv").exists():
            p = check_mineral(material, problems, check_pdfs, with_peaks=False)
            print(f"{material}: {len(p)} mode-card source paper(s): {', '.join(p['paper_id'])}")
    for material in list(PREFIX) + list(REFERENCE):
        if not (ROOT / "structures" / f"{material}.cif").exists():
            problems.append((material, "", f"structures/{material}.cif is missing"))
    for d in sorted(dois["calcite"] & dois["anatase"]):
        problems.append(("both", "", f"DOI {d} is in both bibliographies"))
    for m, pid, msg in problems:
        print(f"  [{m}] {pid}: {msg}")
    print(f"{len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
