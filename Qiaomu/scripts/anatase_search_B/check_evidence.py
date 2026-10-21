"""For every row of anatase/papers_new_B.csv check that each 3-digit wavenumber quoted in raman_evidence also occurs in the paper text (typo guard),
that the quoted PDF page numbers exist, and that listed files exist. Prints problems only."""
import os, re, sys
import pandas as pd, fitz
fitz.TOOLS.mupdf_display_errors(False)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
d = pd.read_csv(os.path.join(ROOT, "anatase", "papers_new_B.csv"), dtype=str, keep_default_na=False)
bad = 0
for _, r in d.iterrows():
    pdf = os.path.join(ROOT, r.folder, "paper.pdf")
    if r.pdf_status == "needs_manual":
        print(r.paper_id, "needs_manual (no pdf)"); continue
    doc = fitz.open(pdf)
    txt = " ".join(p.get_text() for p in doc).replace("−", "-")
    flat = re.sub(r"\s+", " ", txt)
    nums = set(re.findall(r"(?<![\d.])(\d{3}(?:\.\d+)?)(?![\d])", r.raman_evidence))
    miss = []
    for n in sorted(nums):
        v = float(n)
        if v < 100 or v > 700:  # skip years, laser lines, temperatures etc.
            continue
        if not re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", flat):
            miss.append(n)
    pages = [int(x) for x in re.findall(r"p\.(\d+)", r.raman_evidence)]
    badp = [p for p in pages if p > doc.page_count]
    files = [f for f in (r.si_files + ";" + r.data_files).split(";") if f.strip()]
    nof = [f for f in files if not os.path.exists(os.path.join(ROOT, f))]
    if miss or badp or nof:
        bad += 1
        print(r.paper_id, r.doi[:30], "| numbers not in text:", miss, "| bad pages:", badp, "| missing files:", nof)
print("rows", len(d), "with problems", bad)
