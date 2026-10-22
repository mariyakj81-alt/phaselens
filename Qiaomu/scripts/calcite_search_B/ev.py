import sys, re, fitz
d = fitz.open(sys.argv[1]); maxn = int(sys.argv[2]) if len(sys.argv) > 2 else 10
pat = sys.argv[3] if len(sys.argv) > 3 else r"calcite|CaCO"
n = 0
for i, p in enumerate(d):
    t = re.sub(r"\s+", " ", p.get_text())
    for m in re.finditer(pat, t, re.I):
        seg = t[max(0, m.start() - 130): m.end() + 230]
        if re.search(r"(?<![\d.])(1[0-9]{3}|[1-9][0-9]{2})(?:\.\d)?\s?(?:cm|±)", seg) and n < maxn:
            print(f"p{i+1}:", seg); n += 1; break
