"""Evidence for composing a papers.csv row: Raman sentences with anatase-range numbers (with PDF page), laser sentences, SI/data listing.
Usage: python -P evid.py ANA035 [max_sentences]"""
import os, sys, re, glob, fitz
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "anatase")
RANGES = [(130, 160), (185, 210), (380, 412), (503, 530), (625, 655)]
NUM = re.compile(r"(?<![\d.\-])(\d{3})(?:[.,]\d+)?(?![\d])")
def run(aid, mx=10):
    f = glob.glob(os.path.join(OUT, aid + "_*"))[0]
    d = fitz.open(os.path.join(f, "paper.pdf"))
    print("##", os.path.basename(f), "pages", len(d))
    n = 0
    lasers = []
    for pi, pg in enumerate(d):
        t = re.sub(r"\s+", " ", pg.get_text().replace("−", "-").replace("–", "-"))
        for s in re.split(r"(?<=[a-z\)\]\d])\.\s+(?=[A-Z\[])", t):
            if re.search(r"(\d{3}(?:\.\d+)?)\s*nm", s) and re.search(r"laser|excitation|He-?Ne|Ar\+|Raman", s, re.I) and re.search(r"Raman", s):
                lasers.append((pi + 1, s[:230]))
            ok = any(any(lo <= int(m.group(1)) <= hi for lo, hi in RANGES) for m in NUM.finditer(s))
            if ok and re.search(r"Raman|cm-1|cm", s) and re.search(r"anatase|E\s?g|B\s?1g|A\s?1g|mode|peak|band", s, re.I):
                if n < mx:
                    print(f"  p{pi+1}: {s[:340]}"); n += 1
    print(" lasers:")
    for p, s in lasers[:4]: print(f"  p{p}: {s}")
    for sub in ("SI", "data"):
        sd = os.path.join(f, sub)
        if os.path.isdir(sd):
            for r_, _, fs in os.walk(sd):
                for x in fs: print(" ", sub, os.path.relpath(os.path.join(r_, x), f).replace("\\", "/"), os.path.getsize(os.path.join(r_, x)))
if __name__ == "__main__":
    run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)
