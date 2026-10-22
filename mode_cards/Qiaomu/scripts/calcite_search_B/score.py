"""python -P score.py PDF...: numbers near 'calcite'/'CaCO3' in mode windows."""
import sys, re, fitz
wins = {"T155": (148, 164), "L282": (272, 292), "v4_712": (704, 722), "v1_1086": (1078, 1095), "v3_1436": (1425, 1450), "2v2_1749": (1738, 1758)}
for p in sys.argv[1:]:
    d = fitz.open(p)
    t = " ".join(re.sub(r"\s+", " ", pg.get_text()) for pg in d)
    low = t.lower()
    hits = {k: set() for k in wins}
    for m in re.finditer(r"calcite|caco|carbonate|ν1|v1|ν4", low):
        seg = t[max(0, m.start() - 250): m.end() + 250]
        for n in re.findall(r"(?<![\d.])(\d{3,4}(?:\.\d+)?)(?![\d])", seg):
            x = float(n)
            for k, (lo, hi) in wins.items():
                if lo <= x <= hi: hits[k].add(n)
    print(p.split("/")[-2] if "/" in p else p, "| pages", d.page_count, "| raman", low.count("raman"), "| calcite", low.count("calcite"))
    print("   ", {k: sorted(v, key=float)[:6] for k, v in hits.items() if v})
