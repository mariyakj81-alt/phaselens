"""Crossref search restricted to a DOI prefix, filtering on abstract/title text. Usage: cr_mdpi.py prefix "query" [pages]"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
prefix, q = sys.argv[1], sys.argv[2]
pages = int(sys.argv[3]) if len(sys.argv) > 3 else 2
OUT = os.path.join(HERE, "cr_prefix_hits.json")
cache = json.load(open(OUT)) if os.path.exists(OUT) else {}
n = 0
for p in range(pages):
    r = get("https://api.crossref.org/works", params={"query": q, "filter": f"prefix:{prefix},type:journal-article", "rows": 100, "offset": p * 100, "select": "DOI,title,issued,container-title,abstract,author,license"}, gap=2)
    if r.status_code != 200:
        print("ERR", r.status_code); break
    items = r.json()["message"]["items"]
    for it in items:
        doi = it["DOI"].lower(); title = (it.get("title") or [""])[0]
        ab = re.sub(r"<[^>]+>", " ", it.get("abstract", "") or "")
        txt = (title + " " + ab).lower()
        ok = ("anatase" in txt or "tio2" in txt or "titanium dioxide" in txt or "titania" in txt) and "raman" in txt
        if doi in cache: continue
        cache[doi] = dict(title=title, year=(it.get("issued", {}).get("date-parts") or [[None]])[0][0], journal=(it.get("container-title") or [""])[0], first=(it.get("author") or [{}])[0].get("family", ""), ok=ok, hasabs=bool(ab.strip()))
        if ok:
            n += 1
            print(doi, "|", cache[doi]["year"], "|", cache[doi]["journal"][:22], "|", title[:90])
    if len(items) < 100: break
json.dump(cache, open(OUT, "w"))
print("new ok:", n, "cache", len(cache))
