"""Verify anatase/ANAnnn_*/paper.pdf: %PDF magic, opens in PyMuPDF, title words on page 1, anatase Raman number windows, lasers.
Usage: python -P verify_A.py ANA034 [ANA035 ...]   (folder found by prefix under anatase/)"""
import os, sys, re, json, glob, fitz
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "anatase")
RANGES = {"Eg1": (135, 160), "Eg2": (190, 210), "B1g1": (385, 412), "A1g/B1g2": (503, 530), "Eg3": (625, 655)}
def norm(s): return re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("−", "-"))
def title_of(folder):
    fx = os.path.join(folder, "fulltext.xml")
    if os.path.exists(fx):
        root = ET.parse(fx).getroot()
        t = root.find(".//article-title")
        if t is not None: return re.sub(r"\s+", " ", "".join(t.itertext()))
    return ""
def analyse(folder):
    p = os.path.join(folder, "paper.pdf")
    raw = open(p, "rb").read(8)
    d = fitz.open(p); pages = [pg.get_text() for pg in d]
    title = title_of(folder)
    first = norm(pages[0]); tw = [w for w in norm(title).split() if len(w) > 3]
    hit = sum(1 for w in tw if w in first)
    flat = re.sub(r"\s+", " ", " ".join(pages).replace("−", "-"))
    nR = len(re.findall("Raman", flat)); nA = len(re.findall("anatase", flat, re.I))
    nums = []
    for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])", flat):
        v = int(m.group(1))
        for k, (lo, hi) in RANGES.items():
            if lo <= v <= hi: nums.append((m.start(), k, m.group(0)))
    best = (0, None)
    for pos, k, _ in nums:
        win = [(p_, kk) for p_, kk, _ in nums if pos <= p_ <= pos + 300]
        ks = set(kk for _, kk in win)
        if len(ks) > best[0] and re.search(r"cm|Raman|shift", flat[max(0, pos - 300):pos + 400]):
            end = max(p_ for p_, _ in win); best = (len(ks), flat[max(0, pos - 80):end + 50])
    lasers = sorted(set(re.findall(r"(\d{3}(?:\.\d+)?)\s*nm(?=[^.]{0,100}(?:laser|excitation|Raman|He-Ne))", flat)) | set(re.findall(r"(?:laser|excitation|Raman|He-Ne)[^.]{0,100}?(\d{3}(?:\.\d+)?)\s*nm", flat)), key=float)
    lasers = [l for l in lasers if 240 <= float(l) <= 1100]
    return {"magic_ok": raw[:4] == b"%PDF", "pages": len(pages), "title": title[:90], "title_hit": f"{hit}/{len(tw)}", "raman": nR, "anatase": nA,
            "modes_in_window": best[0], "best_window": best[1], "lasers": lasers}
if __name__ == "__main__":
    for aid in sys.argv[1:]:
        fs = glob.glob(os.path.join(OUT, aid + "_*"))
        if not fs: print(aid, "no folder"); continue
        r = analyse(fs[0])
        print(os.path.basename(fs[0]), json.dumps(r, ensure_ascii=False, indent=1))
