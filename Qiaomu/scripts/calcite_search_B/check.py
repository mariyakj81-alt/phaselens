"""python -P check.py PDF [title words...]: print summary of a PDF to judge calcite Raman evidence."""
import sys, re, fitz
p = sys.argv[1]
d = fitz.open(p)
txt = [pg.get_text() for pg in d]
full = "\n".join(txt)
low = full.lower()
print("pages", d.page_count, "| raman", low.count("raman"), "| calcite", low.count("calcite"), "| head:", re.sub(r"\s+", " ", txt[0])[:220])
if len(sys.argv) > 2:
    w = [x.lower() for x in sys.argv[2:]]
    print("title words on p1-2:", sum(1 for x in w if x in (txt[0] + (txt[1] if len(txt) > 1 else "")).lower()), "/", len(w))
lasers = sorted(set(re.findall(r"(?<![\d.])(\d{3,4}(?:\.\d+)?)\s?nm", full)))
print("nm values:", lasers[:30])
wins = {"155": (148, 162), "282": (274, 290), "712": (705, 720), "1086": (1080, 1094), "1436": (1428, 1445), "1749": (1740, 1756)}
nums = re.findall(r"(?<![\d.])(\d{3,4}(?:\.\d+)?)(?![\d])", full)
nn = [float(x) for x in nums]
print({k: sorted(set(v for v in nn if lo <= v <= hi))[:8] for k, (lo, hi) in wins.items()})
for m in re.finditer(r"[^\n]*(?:1086|1085|1087|1088|1089|712|713|711|714|282|281|283|155|156)[^\n]*", full):
    s = m.group(0).strip()
    if re.search(r"cm|raman|peak|band|mode|nu|calcite", s, re.I) and len(s) < 220:
        print("  >", s[:200])
        if sum(1 for _ in [0]) and False: break
