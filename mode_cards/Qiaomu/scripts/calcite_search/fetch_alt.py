"""Download a PDF from an explicitly given legit URL (repository/OA copy) into stage and verify.
Usage: python -P fetch_alt.py STAGE ID URL [TITLE]   (ID = DOI, or a pseudo id like am1985_70_581 when no DOI; TITLE needed then)"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import acquire
from common import get
stage, doi, url = sys.argv[1:4]
title = sys.argv[4] if len(sys.argv) > 4 else ""
d = os.path.join(stage, acquire.slug(doi.lower())); os.makedirs(d, exist_ok=True)
w = {}
if doi.startswith("10.") and not title:
    w = acquire.openalex(doi) or {}
    title = w.get("title") or ""
r = get(url, min_gap=10, timeout=180)
print(r.status_code, r.headers.get("content-type"), len(r.content))
if r.content[:5] == b"%PDF-":
    p = os.path.join(d, "paper.pdf"); open(p, "wb").write(r.content)
    v = acquire.verify(p, title); print(v)
    if v["ok"]:
        json.dump({"doi": doi if doi.startswith("10.") else "", "title": title, "year": w.get("publication_year"), "authors": [a["author"]["display_name"] for a in w.get("authorships", [])][:3],
                   "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"), "pdf": p, "pdf_url": url, "verify": v}, open(os.path.join(d, "result.json"), "w"), indent=1, default=str)
        print("OK", doi)
    else:
        os.remove(p); print("FAIL verify", doi)
else:
    print("not a PDF:", r.text[:200].replace("\n", " "))
