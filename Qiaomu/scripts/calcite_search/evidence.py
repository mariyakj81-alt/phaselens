"""Print best evidence snippets of calcite Raman peak numbers from a PDF. python -P evidence.py pdf [n]"""
import sys, re, fitz
RANGES = {"155": (145, 170), "282": (272, 295), "712": (703, 722), "1086": (1078, 1094), "1436": (1426, 1446), "1749": (1738, 1760)}
NUM = re.compile(r"(?<![\d.])(\d{3,4})(?:\.\d+)?(?![\d])")
def snippets(path, n=3, win=260):
    d = fitz.open(path)
    pages = [p.get_text() for p in d]
    cands = []
    for pi, t in enumerate(pages):
        flat = re.sub(r"\s+", " ", t)
        for mm in NUM.finditer(flat):
            v = int(mm.group(1))
            if not any(lo <= v <= hi for lo, hi in RANGES.values()): continue
            s = flat[max(0, mm.start()-win): mm.end()+win]
            low = s.lower()
            if "calcite" not in low and "caco" not in low and "carbonate" not in low: continue
            modes = {k for x in NUM.finditer(s) for k, (lo, hi) in RANGES.items() if lo <= int(x.group(1)) <= hi}
            cands.append((len(modes), pi + 1, s))
    cands.sort(key=lambda x: (-x[0], x[1]))
    out, used = [], set()
    for m, pg, s in cands:
        key = (pg, s[:40])
        if any(abs(pg - u) == 0 and s[100:140] in u2 for u, u2 in used): continue
        used.add((pg, s)); out.append((m, pg, s))
        if len(out) >= n: break
    return out
if __name__ == "__main__":
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    for m, pg, s in snippets(sys.argv[1], n):
        print(f"  [p{pg} modes={m}] ...{s}...")
