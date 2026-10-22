"""Fetch landing pages and list candidate PDF links. Usage: findpdf.py URL [URL...]  (honest UA, throttled; prints status + links; stops at challenge pages)"""
import sys, os, re, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
for u in sys.argv[1:]:
    try:
        r = get(u, timeout=60)
    except Exception as e:
        print(u, "EXC", e); continue
    body = r.text
    flag = ""
    if re.search(r"Making sure you.re not a bot|Client Challenge|cf-challenge|Just a moment|perfdrive|Access Denied", body[:5000], re.I):
        flag = "CHALLENGE"
    print("##", u, r.status_code, r.headers.get("content-type", "")[:30], len(body), flag)
    if flag: continue
    t = re.search(r"<title>(.*?)</title>", body, re.S | re.I)
    print("   title:", re.sub(r"\s+", " ", t.group(1))[:150] if t else "")
    links = set()
    for m in re.finditer(r'(?:href|content)=["\']([^"\']+)["\']', body):
        h = m.group(1)
        if re.search(r"\.pdf|bitstream|/download|citation_pdf|fulltext|getfile|file", h, re.I) and not h.startswith("#"):
            links.add(urllib.parse.urljoin(r.url, h))
    for h in sorted(links)[:15]:
        print("   ", h[:220])
