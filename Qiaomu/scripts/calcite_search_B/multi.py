"""python -P multi.py STAGE name=url ... : download each, print brief check."""
import sys, os, re, fitz
sys.path.insert(0, '.')
from common import get
ST = sys.argv[1]
for a in sys.argv[2:]:
    name, u = a.split("=", 1)
    d = os.path.join(ST, name); os.makedirs(d, exist_ok=True)
    try:
        r = get(u, min_gap=10, timeout=180)
    except Exception as e:
        print(name, "EXC", type(e).__name__, str(e)[:80]); continue
    ct = r.headers.get("content-type", "")
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        p = os.path.join(d, "paper.pdf"); open(p, "wb").write(r.content)
        try:
            doc = fitz.open(p); t = "".join(pg.get_text() for pg in doc); low = t.lower()
            print(name, "PDF", doc.page_count, "p | raman", low.count("raman"), "calcite", low.count("calcite"), "|", re.sub(r"\s+", " ", doc[0].get_text())[:160])
        except Exception as e:
            print(name, "PDF but fitz fail", e)
    else:
        txt = ""
        if "html" in ct:
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S)))[:200]
        print(name, r.status_code, ct[:30], len(r.content), "|", txt)
