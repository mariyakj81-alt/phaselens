"""OpenAlex search for OA anatase Raman works. Usage: oa_search.py "query" [more queries]. Prints compact hit list and caches to oa_hits.json"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
CACHE = os.path.join(HERE, "oa_hits.json")
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
queries = sys.argv[1:]
for q in queries:
    for page in (1, 2):
        r = get("https://api.openalex.org/works", params={"search": q, "filter": "open_access.is_oa:true,type:article|preprint", "per-page": 50, "page": page,
                "select": "id,doi,title,publication_year,cited_by_count,best_oa_location,open_access,primary_location,authorships"}, gap=2)
        if r.status_code != 200:
            print("ERR", q, r.status_code, r.text[:200]); break
        js = r.json()
        for w in js["results"]:
            doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            key = doi or w["id"]
            if key in cache: continue
            bol = w.get("best_oa_location") or {}
            pl = w.get("primary_location") or {}
            cache[key] = dict(title=w["title"], year=w["publication_year"], cites=w["cited_by_count"], pdf=bol.get("pdf_url"), landing=bol.get("landing_page_url"),
                              src=(pl.get("source") or {}).get("display_name"), oa=w["open_access"].get("oa_status"), first=(w["authorships"][0]["author"]["display_name"] if w["authorships"] else ""), q=q)
            print(key, "|", w["publication_year"], "|", (w["title"] or "")[:100], "|", (pl.get("source") or {}).get("display_name"), "|", bol.get("pdf_url") or bol.get("landing_page_url"))
        if len(js["results"]) < 50: break
json.dump(cache, open(CACHE, "w"), indent=1)
