"""DOAJ article search (OA journals; free API). Usage: doaj_search.py "query" [pages]. Keeps hits whose title+abstract mention anatase/TiO2 and Raman."""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
CACHE = os.path.join(HERE, "doaj_hits.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
q = sys.argv[1]
pages = int(sys.argv[2]) if len(sys.argv) > 2 else 3
for page in range(1, pages + 1):
    r = get("https://doaj.org/api/search/articles/" + q.replace(" ", "%20"), params={"pageSize": 50, "page": page}, gap=2)
    if r.status_code != 200:
        print("ERR", r.status_code, r.text[:150]); break
    js = r.json()
    res = js.get("results", [])
    for it in res:
        b = it["bibjson"]
        title = b.get("title", "")
        ab = b.get("abstract", "") or ""
        txt = (title + " " + ab).lower()
        doi = ""
        for i in b.get("identifier", []):
            if i.get("type") == "doi": doi = i["id"].lower()
        key = doi or it["id"]
        if key in cache: continue
        has = ("anatase" in txt or "tio2" in txt or "titania" in txt or "titanium dioxide" in txt) and "raman" in txt
        links = [l["url"] for l in b.get("link", []) if l.get("type") == "fulltext"]
        cache[key] = dict(title=title, year=b.get("year"), journal=b.get("journal", {}).get("title"), links=links, hit=has, first=((b.get("author") or [{}])[0].get("name", "")))
        if has:
            print(f"{key} | {b.get('year')} | {(b.get('journal') or {}).get('title','')[:35]} | {title[:100]} | {links[:1]}")
    if len(res) < 50: break
json.dump(cache, open(CACHE, "w"), indent=1)
