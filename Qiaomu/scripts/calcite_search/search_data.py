import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from common import get
qs = ["calcite Raman", "calcite Raman spectra", "calcium carbonate Raman spectra", "Mg-calcite Raman", "carbonate Raman spectra dataset", "aragonite calcite Raman", "biogenic calcite Raman spectra"]
seen=set()
for q in qs:
    r = get("https://zenodo.org/api/records", params={"q": q, "size": 25, "sort":"bestmatch"}, min_gap=2)
    print("ZENODO", q, r.status_code)
    if r.status_code==200:
        for h in r.json()["hits"]["hits"]:
            if h["id"] in seen: continue
            seen.add(h["id"])
            md=h["metadata"]
            files=[(f["key"], f["size"]) for f in h.get("files",[])][:6]
            print(" Z", h["id"], md.get("publication_date"), md.get("title")[:100], "|", md.get("doi"), "| rel:", [ (x.get("relation"),x.get("identifier")) for x in md.get("related_identifiers",[])][:3], "|", len(h.get("files",[])), "files")
for q in ["calcite Raman", "calcium carbonate Raman spectra", "Mg calcite Raman"]:
    r = get("https://api.figshare.com/v2/articles/search", params=None, min_gap=2) if False else None
import requests
for q in ["calcite Raman", "calcium carbonate Raman", "Mg-calcite Raman"]:
    r = requests.post("https://api.figshare.com/v2/articles/search", json={"search_for": q, "page_size": 25}, headers={"User-Agent":"Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}, timeout=60)
    print("FIGSHARE", q, r.status_code)
    if r.status_code==200:
        for a in r.json():
            print(" F", a["id"], a.get("published_date","")[:10], a["title"][:100], "|", a.get("doi"))
    import time; time.sleep(2)
