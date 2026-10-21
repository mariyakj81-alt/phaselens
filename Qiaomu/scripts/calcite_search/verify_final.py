"""Re-verify every paper.pdf in calcite/ against papers.csv. python -P verify_final.py PROJECT_ROOT"""
import sys, os, csv, re, fitz
ROOT = sys.argv[1]
MODES = {"155": (150, 160), "282": (277, 288), "712": (708, 718), "1086": (1082, 1092), "1436": (1430, 1442), "1749": (1743, 1755)}
rows = list(csv.DictReader(open(os.path.join(ROOT, "calcite", "papers.csv"), encoding="utf-8")))
bad = 0
for r in rows:
    p = os.path.join(ROOT, r["folder"], "paper.pdf")
    if r["pdf_status"] != "downloaded":
        print(r["paper_id"], "needs_manual (no pdf) data:", r["data_files"][:80]); continue
    ok = True; msg = []
    head = open(p, "rb").read(5)
    if head != b"%PDF-": ok = False; msg.append("no %PDF header")
    try:
        d = fitz.open(p); n = d.page_count
        first = " ".join(d[i].get_text() for i in range(min(2, n))).lower()
        full = " ".join(pg.get_text() for pg in d)
    except Exception as e:
        print(r["paper_id"], "FITZ FAIL", e); bad += 1; continue
    words = [w for w in re.findall(r"[a-z0-9]+", r["title"].lower()) if len(w) > 3]
    hits = sum(1 for w in set(words) if w in first)
    tcheck = hits / max(1, len(set(words)))
    low = full.lower()
    nums = [int(x) for x in re.findall(r"(?<![\d.])(\d{3,4})(?:\.\d+)?(?![\d])", full)]
    modes = [k for k, (lo, hi) in MODES.items() if any(lo <= v <= hi for v in nums)]
    if tcheck < 0.5: ok = False; msg.append(f"title match {tcheck:.2f}")
    if low.count("raman") < 5: ok = False; msg.append("few Raman")
    if "calcite" not in low and "caco" not in low: ok = False; msg.append("no calcite")
    print(r["paper_id"], "OK " if ok else "BAD", f"{n}p", f"title {tcheck:.2f}", "raman", low.count("raman"), "calcite", low.count("calcite"), "modes", modes, msg)
    if not ok: bad += 1
print("bad:", bad, "of", len(rows))
