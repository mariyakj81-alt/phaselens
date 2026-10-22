"""python -P batch_score.py STAGE prefix id1 id2 ... : download arxiv PDFs (https://arxiv.org/pdf/ID) and print score."""
import sys, os, re, fitz
sys.path.insert(0, '.')
from common import get
ST = sys.argv[1]; pre = sys.argv[2]
wins = {"T155": (148, 164), "L282": (272, 292), "v4_712": (704, 722), "v1_1086": (1078, 1095), "v3_1436": (1425, 1450), "2v2_1749": (1738, 1758)}
for aid in sys.argv[3:]:
    name = pre + aid.replace("/", "_")
    d = os.path.join(ST, name); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "paper.pdf")
    if not os.path.exists(p):
        try:
            r = get("https://arxiv.org/pdf/" + aid, min_gap=10, timeout=120)
        except Exception as e:
            print(name, "EXC"); continue
        if not (r.status_code == 200 and r.content[:5] == b"%PDF-"):
            print(name, r.status_code); continue
        open(p, "wb").write(r.content)
    doc = fitz.open(p)
    t = " ".join(re.sub(r"\s+", " ", pg.get_text()) for pg in doc); low = t.lower()
    hits = {k: set() for k in wins}
    for m in re.finditer(r"calcite|caco|carbonate", low):
        seg = t[max(0, m.start() - 250): m.end() + 250]
        for n in re.findall(r"(?<![\d.])(\d{3,4}(?:\.\d+)?)(?![\d])", seg):
            x = float(n)
            for k, (lo, hi) in wins.items():
                if lo <= x <= hi: hits[k].add(n)
    print(name, "| p", doc.page_count, "| raman", low.count("raman"), "| calcite", low.count("calcite"), "|", {k: sorted(v, key=float)[:4] for k, v in hits.items() if v}, "|", re.sub(r"\s+", " ", t[:70]), flush=True)
