"""python -P oa_lookup.py DOI... : OpenAlex single-work lookup -> OA status and locations."""
import sys, re, json
sys.path.insert(0, '.')
from common import get
import urllib.parse
for doi in sys.argv[1:]:
    r = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/"), params={"select": "id,title,publication_year,open_access,best_oa_location,locations"}, min_gap=1)
    if r.status_code != 200:
        print(doi, r.status_code); continue
    w = r.json()
    oa = w.get("open_access", {})
    locs = [(l.get("version"), l.get("pdf_url") or l.get("landing_page_url")) for l in w.get("locations", []) if l.get("is_oa")]
    print(doi, "|", (w.get("title") or "")[:60], "|", oa.get("oa_status"), "|", locs[:4])
