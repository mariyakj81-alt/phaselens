import sys, os, re
sys.path.insert(0, '.')
from common import get
import fitz
ST = sys.argv[1]
items = [("ana5_1a", "seca", 5, 1, 76, 86), ("ana5_1b", "seca", 5, 1, 87, 93), ("ana5_2", "seca", 5, 2, 175, 184), ("ana5_3", "seca", 5, 3, 200, 221),
         ("bhag1939", "seca", 9, 3, 224, 258), ("bhag1940", "seca", 11, 1, 62, 71), ("bhag1941", "seca", 13, 6, 543, 563), ("saksena1940", "seca", 11, 3, 229, 245)]
for name, j, v, i, a, b in items:
    u = f"https://www.ias.ac.in/public/Volumes/{j}/{v:03d}/{i:02d}/{a:04d}-{b:04d}.pdf"
    r = get(u, min_gap=10, timeout=120)
    ok = r.status_code == 200 and r.content[:5] == b"%PDF-"
    print(name, r.status_code, ok, len(r.content))
    if ok:
        p = os.path.join(ST, "ias", name + ".pdf"); open(p, "wb").write(r.content)
        d = fitz.open(p); t = "".join(pg.get_text() for pg in d).lower()
        print("   pages", d.page_count, "calcite", t.count("calcite"), "iceland", t.count("iceland"), "raman", t.count("raman"), "|", re.sub(r"\s+", " ", d[0].get_text())[:120])
