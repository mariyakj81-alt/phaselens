import csv, os
ROOT = "G:/My Drive/Qiaomu_Coding/LLM_Hackason/2026_Raman"
def known():
    s = set()
    for f in ("calcite/papers.csv", "calcite/candidates_rejected.csv", "calcite/candidates_rejected_B.csv", "calcite/papers_new_B.csv"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                d = (r.get("doi") or "").strip().lower()
                if d: s.add(d)
    p = os.path.join(ROOT, "calcite/_claims.txt")
    if os.path.exists(p):
        for l in open(p, encoding="utf-8"):
            d = l.split("\t")[0].strip().lower()
            if d and d != "doi": s.add(d)
    return s
