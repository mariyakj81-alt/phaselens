"""python -P dl.py OUTFILE URL [URL...]  -> downloads first URL that returns a PDF; prints status. Never bypasses challenges."""
import sys, re
sys.path.insert(0, '.')
from common import get
import fitz
out = sys.argv[1]
for u in sys.argv[2:]:
    try:
        r = get(u, min_gap=10, timeout=120)
    except Exception as e:
        print("EXC", u, type(e).__name__, str(e)[:100]); continue
    ct = r.headers.get("content-type", "")
    print(r.status_code, ct[:40], len(r.content), u)
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        open(out, "wb").write(r.content)
        d = fitz.open(out)
        print("PDF OK pages", d.page_count, "|", re.sub(r"\s+", " ", d[0].get_text())[:200])
        break
    elif r.status_code == 200 and "html" in ct:
        t = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S))
        print("  HTML:", re.sub(r"<[^>]+>", " ", t)[:200])
        for m in re.findall(r'(?:citation_pdf_url|href)[^>]*?["\'=]\s*["\']?([^"\' >]+\.pdf[^"\' >]*)', r.text)[:5]:
            print("   pdf link:", m)
