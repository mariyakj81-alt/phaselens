"""Re-verify calcite/papers_new_A.csv from the project root: PDF header, PyMuPDF, title on p1-2, calcite Raman numbers, listed files exist, 19 columns."""
import sys, os, csv, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_A import verify_pdf
rows = list(csv.DictReader(open("calcite/papers_new_A.csv", encoding="utf-8", newline="")))
ref = list(csv.reader(open("calcite/papers.csv", encoding="utf-8", newline="")))[0]
print("columns match papers.csv:", list(rows[0].keys()) == ref, len(ref))
bad = 0
for r in rows:
    probs = []
    pdf = os.path.join(r["folder"], "paper.pdf")
    v = verify_pdf(pdf, r["title"])
    if not v["ok"]: probs.append(("pdf", v))
    for key in ("si_files", "data_files"):
        for p in filter(None, r[key].split(";")):
            if not os.path.exists(p): probs.append(("missing", p))
    if not os.path.exists(os.path.join(r["folder"], "fulltext.xml")): probs.append("no xml")
    if re.search(r"\.0(;|$)", r["laser_nm"]): probs.append("laser .0")
    if not re.fullmatch(r"CAL\d{3}", r["paper_id"]): probs.append("id")
    print(r["paper_id"], r["folder"].split("/")[-1], "OK" if not probs else probs, v.get("modes"), "raman", v.get("raman"), "calcite", v.get("calcite"), "SI", len(r["si_files"].split(";")) if r["si_files"] else 0, "data", len(r["data_files"].split(";")) if r["data_files"] else 0)
    bad += bool(probs)
print("papers", len(rows), "with problems", bad)
ids = [r["paper_id"] for r in rows]
print("ids", ids[0], ids[-1], "contiguous", ids == ["CAL%03d" % i for i in range(34, 34 + len(ids))])
dois = [r["doi"].lower() for r in rows]; print("dup dois", len(dois) - len(set(dois)))
