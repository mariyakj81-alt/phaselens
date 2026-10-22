"""python -P probe.py URL...: print status, text snippet, pdf links."""
import sys, re
sys.path.insert(0, '.')
from common import get
for u in sys.argv[1:]:
    try:
        r = get(u, min_gap=5)
    except Exception as e:
        print("==", u, "EXC", type(e).__name__, str(e)[:120]); continue
    ct = r.headers.get("content-type", "")
    print("==", u, r.status_code, ct[:30], len(r.content))
    if "html" in ct:
        t = re.sub(r"<script.*?</script>|<style.*?</style>", "", r.text, flags=re.S)
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
        print(t[:600])
        print([m for m in re.findall(r"""(?:href|content)=["']([^"']*(?:\.pdf|download|Pdf|PDF)[^"']*)""", r.text)][:8])
