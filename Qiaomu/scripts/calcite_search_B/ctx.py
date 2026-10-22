"""python -P ctx.py PDF : laser statements and calcite-number contexts with page numbers"""
import sys, re, fitz
d = fitz.open(sys.argv[1])
print("PAGES", d.page_count)
tx = [re.sub(r"\s+", " ", p.get_text()) for p in d]
print("HEAD:", tx[0][:500])
print("--- LASER")
n = 0
for i, t in enumerate(tx):
    for m in re.finditer(r"[^.]*(?:laser|excitation|excited|Ar\+|argon|Nd:YAG|diode|nm line)[^.]*\.", t):
        s = m.group(0).strip()
        if re.search(r"\d{3}(?:\.\d+)?\s?nm|\d{3}\s?nm|Hg|argon|Ar\+", s) and n < 8:
            print(f"p{i+1}:", s[:260]); n += 1
print("--- CALCITE NUMBERS")
wins = [(148, 164), (272, 292), (704, 722), (1078, 1095), (1425, 1450), (1738, 1758)]
n = 0
for i, t in enumerate(tx):
    for m in re.finditer(r"(?<![\d.])(\d{3,4}(?:\.\d+)?)(?![\d])", t):
        x = float(m.group(1))
        if any(lo <= x <= hi for lo, hi in wins):
            seg = t[max(0, m.start() - 100): m.end() + 100]
            if re.search(r"calcite|CaCO|carbonate|Raman|peak|band|mode|ν|cm", seg, re.I) and n < 14:
                print(f"p{i+1}:", seg); n += 1
