import sys, re, urllib.parse
sys.path.insert(0, '.')
from common import get
for u in sys.argv[1:]:
    try:
        r = get(u, min_gap=5, timeout=90)
    except Exception as e:
        print("EXC", u, type(e).__name__); continue
    print("==", r.url, r.status_code, len(r.text))
    links = set()
    for m in re.findall(r"""(?:href|content|src)=["']([^"']+)["']""", r.text):
        if re.search(r"\.pdf|bitstream|/download|/files?/|/retrieve/|pdf\?|article/view/\d+/\d+", m, re.I) and not re.search(r"\.(png|jpg|svg|css|js)(\?|$)", m, re.I):
            links.add(urllib.parse.urljoin(r.url, m.replace("&amp;", "&")))
    for l in sorted(links)[:12]: print("  ", l[:200])
