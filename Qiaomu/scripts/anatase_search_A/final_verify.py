"""Final verification of ANA034..ANA067: %PDF magic, PyMuPDF opens, title words on first 2 pages, anatase mode numbers in PDF text, Raman count."""
import os, re, glob, csv, fitz, unicodedata
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
rows = list(csv.DictReader(open(os.path.join(ROOT, "anatase", "papers_new_A.csv"), encoding="utf-8", newline="")))
def norm(s): return re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFKC", s).lower().replace("−", "-"))
RANGES = [(130, 160), (185, 210), (380, 412), (503, 530), (625, 655)]
bad = 0
for r in rows:
    p = os.path.join(ROOT, r["folder"], "paper.pdf")
    magic = open(p, "rb").read(5)
    d = fitz.open(p)
    first = norm(" ".join(d[i].get_text() for i in range(min(2, len(d)))))
    words = [w for w in norm(r["title"]).split() if len(w) > 3]
    hit = sum(1 for w in words if w in first)
    flat = unicodedata.normalize("NFKC", " ".join(pg.get_text() for pg in d)).replace("−", "-")
    nR = len(re.findall("Raman", flat)); nA = len(re.findall("anatase", flat, re.I))
    modes = set()
    for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])", flat):
        v = int(m.group(1))
        for k, (lo, hi) in enumerate(RANGES):
            if lo <= v <= hi: modes.add(k)
    ok = magic.startswith(b"%PDF") and hit >= max(3, int(0.6 * len(words))) and nR >= 5 and len(modes) >= 3
    if not ok: bad += 1
    print(r["paper_id"], "OK " if ok else "BAD", "magic", magic[:4] == b"%PDF", "pages", len(d), f"title {hit}/{len(words)}", "Raman", nR, "anatase", nA, "modes", len(modes))
print("bad:", bad)
