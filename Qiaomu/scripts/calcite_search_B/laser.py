import sys, re, fitz
for p in sys.argv[1:]:
    d = fitz.open(p); n = 0
    print("=====", p.split("/")[-2])
    for i, pg in enumerate(d):
        t = re.sub(r"\s+", " ", pg.get_text())
        for m in re.finditer(r"(\d{3,4}(?:\.\d+)?)\s?[-–]?\s?nm", t):
            seg = t[max(0, m.start() - 110): m.end() + 90]
            if re.search(r"laser|excit|wavelength|line|Raman", seg, re.I) and n < 5:
                print(f"p{i+1}:", seg); n += 1
