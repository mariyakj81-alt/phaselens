import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
titles = [l.strip() for l in sys.stdin if l.strip()]
for t in titles:
    r = get("https://api.crossref.org/works", params={"query.bibliographic": t, "rows": 2, "select": "DOI,title,issued,container-title,author,volume,page"}, gap=2)
    if r.status_code != 200: print("ERR", t[:40], r.status_code); continue
    for it in r.json()["message"]["items"][:2]:
        print(t[:45], "=>", it["DOI"], "|", (it.get("issued", {}).get("date-parts") or [[None]])[0][0], "|", (it.get("container-title") or [""])[0][:30], "|", (it.get("author") or [{}])[0].get("family"), "|", (it.get("title") or [""])[0][:70])
