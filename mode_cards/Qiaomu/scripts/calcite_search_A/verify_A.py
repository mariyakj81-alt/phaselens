"""Verify staged PDFs: %PDF header, opens in PyMuPDF, title words on pages 1-2, calcite Raman peak numbers present.
usage: python -P verify_A.py PMCID [PMCID ...]   (staging dir from cfg_A) ; or  verify_A.py path/to/paper.pdf "Title text" """
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfg_A import STAGE
import fitz
from meta_A import meta

WIN = {"T": (150, 161), "L": (274, 291), "v4": (704, 720), "v1": (1080, 1092), "v3": (1428, 1445), "2v2": (1742, 1755)}

def verify_pdf(path, title):
    info = {"ok": False}
    head = open(path, "rb").read(5)
    if head != b"%PDF-": info["why"] = "no %PDF header"; return info
    try:
        d = fitz.open(path)
    except Exception as e:
        info["why"] = f"fitz fail {e}"; return info
    n = d.page_count
    first = " ".join(d[i].get_text() for i in range(min(2, n))).lower()
    full = " ".join(p.get_text() for p in d)
    low = full.lower()
    words = [w for w in re.findall(r"[a-z0-9]+", re.sub(r"<[^>]+>", "", title).lower()) if len(w) > 3]
    ws = set(words)
    hit = sum(1 for w in ws if w in first)
    nums = [float(x.replace(",", ".")) for x in re.findall(r"(?<![\d.])(\d{3,4}(?:[.,]\d+)?)(?![\d])", full)]
    modes = [k for k, (a, b) in WIN.items() if any(a <= v <= b for v in nums)]
    info.update(pages=n, title_hits=f"{hit}/{len(ws)}", raman=low.count("raman"), calcite=low.count("calcite"), modes=modes)
    info["ok"] = (hit >= max(2, int(0.6 * len(ws)))) and info["raman"] >= 3 and info["calcite"] >= 2 and len(modes) >= 3
    if not info["ok"]: info["why"] = "title/raman/calcite/modes check failed"
    return info

if __name__ == "__main__":
    for pm in sys.argv[1:]:
        try:
            m = meta(pm)
            v = verify_pdf(os.path.join(STAGE, pm, "paper.pdf"), m["title"])
        except Exception as e:
            print(pm, "ERR", repr(e)); continue
        print(pm, "OK " if v["ok"] else "BAD", v)
