"""Screen PDFs for anatase Raman evidence. Usage: screen.py [-v] file.pdf [file.pdf ...]
Prints magic/pages/title(first 150 chars of p1), Raman & anatase counts, symmetry labels, best window of mode numbers, lasers."""
import sys, re, fitz
RANGES = {"Eg1": (138, 160), "Eg2": (190, 210), "B1g1": (388, 412), "A1g/B1g2": (505, 530), "Eg3": (625, 655)}


def analyse(path, verbose=False):
    raw = open(path, "rb").read(8)
    d = fitz.open(path)
    pages = [p.get_text() for p in d]
    full = " ".join(pages)
    flat = re.sub(r"\s+", " ", full.replace("−", "-"))
    nraman = len(re.findall("Raman", flat))
    nanat = len(re.findall("anatase", flat, re.I))
    sym = len(re.findall(r"\bE\s?g\b|\bB\s?1g\b|\bA\s?1g\b", flat))
    nums = []
    for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])", flat):
        v = int(m.group(1))
        for k, (lo, hi) in RANGES.items():
            if lo <= v <= hi:
                nums.append((m.start(), k, m.group(0)))
    best = (0, None)
    for pos, k, _ in nums:
        win = [(p, kk) for p, kk, _ in nums if pos <= p <= pos + 300]
        ks = set(kk for _, kk in win)
        if len(ks) > best[0]:
            end = max(p for p, _ in win)
            if re.search(r"cm|Raman|shift", flat[max(0, pos - 300):end + 100]):
                best = (len(ks), flat[max(0, pos - 80):end + 40])
    lasers = sorted(set(re.findall(r"(\d{3}(?:\.\d+)?)\s*nm(?=[^.]{0,100}(?:laser|excitation|Raman|line|He-Ne|Ar))", flat)) |
                    set(re.findall(r"(?:laser|excitation|Raman|He-Ne|Ar\+?|argon)[^.]{0,100}?(\d{3}(?:\.\d+)?)\s*nm", flat)), key=float)
    lasers = [l for l in lasers if 320 <= float(l) <= 1100]
    print(f"== {path}")
    print(f"   magic={raw[:4]==b'%PDF'} pages={len(pages)} Raman={nraman} anatase={nanat} sym={sym} modes_in_window={best[0]} lasers={lasers[:8]}")
    print("   p1:", re.sub(r'\s+', ' ', pages[0])[:200])
    if best[1]:
        print("   win:", best[1][:400])
    if verbose:
        # print Raman sentences containing numbers
        k = 0
        for m in re.finditer(r"[^.]*Raman[^.]*\d{3}[^.]*\.", flat):
            print("   >>", m.group(0)[:300]); k += 1
            if k > 8: break


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "-v"]
    for a in args:
        try:
            analyse(a, "-v" in sys.argv)
        except Exception as e:
            print("ERR", a, e)
