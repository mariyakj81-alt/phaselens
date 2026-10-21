"""python -P claim.py DOI...: check claims file; if free append a B claim; re-read; print OK or LOST."""
import sys, time, os
P = "G:/My Drive/Qiaomu_Coding/LLM_Hackason/2026_Raman/calcite/_claims.txt"
for doi in sys.argv[1:]:
    d = doi.strip().lower()
    lines = [l.rstrip("\n").split("\t") for l in open(P, encoding="utf-8")] if os.path.exists(P) else []
    prior = [l for l in lines if l and l[0].strip().lower() == d]
    if any(l[1] == "A" for l in prior):
        print("SKIP (A has it)", doi); continue
    if not any(l[1] == "B" for l in prior):
        with open(P, "a", encoding="utf-8", newline="") as f:
            f.write(f"{doi}\tB\t{time.strftime('%H:%M:%S')}\n")
    lines = [l.rstrip("\n").split("\t") for l in open(P, encoding="utf-8")]
    ms = [l for l in lines if l and l[0].strip().lower() == d]
    first = ms[0][1]
    print(("OK   " if first == "B" else "LOST ") + doi, "| claimed by", [m[1] for m in ms])
