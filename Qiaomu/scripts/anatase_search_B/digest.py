"""Compact evidence digest of a PDF: title lines, laser sentences, clusters of anatase-range wavenumbers with page numbers.
Usage: digest.py file.pdf [maxclusters] [width]"""
import sys, re, fitz
fitz.TOOLS.mupdf_display_errors(False)
path = sys.argv[1]
maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 6
width = int(sys.argv[3]) if len(sys.argv) > 3 else 380
d = fitz.open(path)
print("PAGES", len(d), "| p1:", re.sub(r"\s+", " ", d[0].get_text())[:300])
las = re.compile(r"(laser|excitation|excited|line of|wavelength)", re.I)
n = 0; seen = set()
for pi, p in enumerate(d):
    t = re.sub(r"\s+", " ", p.get_text().replace("−", "-"))
    for m in re.finditer(r"[^.!?]{0,200}?(?:\b\d{3}(?:\.\d+)?\s*nm|\d\.\d+\s*eV)[^!?]{0,160}", t):
        s = m.group(0).strip()
        if las.search(s) and re.search(r"Raman", t[max(0, m.start() - 500):m.end() + 500]) and s[:50] not in seen:
            seen.add(s[:50]); print(f"LASER p{pi+1}: {s[:260]}"); n += 1
            if n >= 3: break
    if n >= 3: break
num = re.compile(r"(?<![\d.])(1[3-6]\d|19\d|20\d|3[89]\d|40\d|41[0-2]|5[0-3]\d|6[2-5]\d)(?:\.\d+)?(?![\d])")
k = 0
for pi, p in enumerate(d):
    t = re.sub(r"\s+", " ", p.get_text().replace("−", "-"))
    last_end = -1
    for m in num.finditer(t):
        if m.start() < last_end: continue
        ctx = t[m.start():m.start() + 40]
        if not re.search(r"cm\s?-?\s?1|cm−1", t[m.end():m.end() + 14] + " ") and not re.search(r"cm\s?-\s?1", ctx):
            continue
        before = t[max(0, m.start() - 160):m.start()]
        if not re.search(r"Raman|peak|mode|band|Eg|B1g|A1g|E g|shift", before + t[m.end():m.end() + 80]):
            continue
        # cluster: extend while next numbers within 60 chars
        end = m.end()
        for m2 in num.finditer(t, m.end()):
            if m2.start() - end < 70: end = m2.end()
            else: break
        seg = t[max(0, m.start() - 150):end + 120]
        print(f"RAMAN p{pi+1}: ...{seg[:width]}")
        last_end = end; k += 1
        if k >= maxc: break
    if k >= maxc: break
print("TABLES:", sorted(set(re.findall(r"Table\s?(?:S?\d+)", " ".join(p.get_text() for p in d))))[:10])
