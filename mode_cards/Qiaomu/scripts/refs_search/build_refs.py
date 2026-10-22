"""Write <material>/papers.csv and <material>/candidates_rejected.csv for mos2, quartz, silicon.

Run from the project root:  python -P scripts/refs_search/build_refs.py
Paper files are already in <material>/<ID>_<Surname><Year>/paper.pdf (placed by the search scripts).
The manifest below is the single place where evidence strings and notes are kept.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from manifest_refs import PAPERS, REJECTED  # noqa: E402

COLUMNS = ["paper_id", "folder", "doi", "title", "first_author", "year", "journal", "open_access",
           "raman_evidence", "laser_nm", "sample_description", "peak_table", "raw_data", "pdf_status",
           "si_files", "data_files", "source_urls", "found_via", "notes"]


def main():
    for material in ("mos2", "quartz", "silicon"):
        rows = [p for p in PAPERS if p["material"] == material]
        if not rows:
            continue
        with open(f"{material}/papers.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            w.writeheader()
            for p in rows:
                p = dict(p)
                p.setdefault("si_files", "")
                p.setdefault("data_files", "")
                w.writerow(p)
        rej = [r for r in REJECTED if r["material"] == material]
        with open(f"{material}/candidates_rejected.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["doi", "title", "reason"])
            for r in rej:
                w.writerow([r["doi"], r["title"], r["reason"]])
        print(material, len(rows), "papers,", len(rej), "rejected")


if __name__ == "__main__":
    main()
