"""Claim DOIs in calcite/_claims.txt (tab-separated doi/agent/time). usage: python -P claim_A.py doi1 doi2 ...
Prints CLAIMED or LOST (earlier claim by B) per DOI. Run from the project root."""
import sys, time
F = "calcite/_claims.txt"

def read():
    rows = []
    for ln in open(F, encoding="utf-8").read().splitlines()[1:]:
        p = ln.split("\t")
        if len(p) >= 3: rows.append((p[0].strip().lower(), p[1].strip(), p[2].strip()))
    return rows

for doi in sys.argv[1:]:
    d = doi.lower()
    rows = read()
    owners = [r for r in rows if r[0] == d]
    if any(r[1] != "A" for r in owners):
        print("LOST", d, owners); continue
    if not owners:
        with open(F, "a", encoding="utf-8", newline="") as f:
            f.write("%s\tA\t%s\n" % (d, time.strftime("%H:%M:%S")))
    rows = read()
    first = [r for r in rows if r[0] == d][0]
    print("CLAIMED" if first[1] == "A" else "LOST", d)
