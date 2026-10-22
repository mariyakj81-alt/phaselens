"""Crossref search. Usage: cr_search.py [--oa] "query" ... ; prints doi | year | journal | title | OA-license flag"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
args = sys.argv[1:]
oa_only = "--oa" in args
args = [a for a in args if a != "--oa"]
KW = re.compile(r"anatase|tio2|tio<sub>2|titan|titania", re.I)
rows = 60
CACHE = os.path.join(HERE, "cr_hits.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
for q in args:
    params = {"query.bibliographic": q, "rows": rows, "select": "DOI,title,issued,container-title,license,author,is-referenced-by-count"}
    if oa_only:
        params["filter"] = "license.url:creativecommons.org"
    r = get("https://api.crossref.org/works", params=params, gap=2)
    if r.status_code != 200:
        print("ERR", q, r.status_code); continue
    print("##", q)
    for it in r.json()["message"]["items"]:
        doi = it["DOI"].lower()
        title = (it.get("title") or [""])[0]
        yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        jr = (it.get("container-title") or [""])[0]
        lic = any("creativecommons" in (l.get("URL") or "") for l in it.get("license", []))
        au = (it.get("author") or [{}])[0].get("family", "")
        if not KW.search(title): continue
        new = doi not in cache
        cache[doi] = dict(title=title, year=yr, journal=jr, cc=lic, first=au, cites=it.get("is-referenced-by-count"))
        print(("  " if not new else "* ") + f"{doi} | {yr} | {au} | {jr[:30]} | {title[:95]} | {'CC' if lic else ''}")
json.dump(cache, open(CACHE, "w"), indent=1)
