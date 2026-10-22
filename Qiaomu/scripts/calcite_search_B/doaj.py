import sys, json, re, urllib.parse
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
res = {}
qs = ['bibjson.abstract:(calcite AND Raman)', 'bibjson.abstract:(calcite AND "Raman spectra")', 'bibjson.abstract:("calcium carbonate" AND Raman)', 'bibjson.title:(calcite AND Raman)', 'bibjson.abstract:(carbonate AND Raman AND (shift OR peak OR band))', 'bibjson.abstract:(Mg-calcite AND Raman)', 'bibjson.abstract:("magnesian calcite" AND Raman)', 'bibjson.abstract:(calcite AND ("micro-Raman" OR "Raman microscopy" OR "Raman spectroscopy"))', 'bibjson.abstract:(limestone AND Raman AND calcite)', 'bibjson.abstract:(speleothem AND Raman)', 'bibjson.abstract:(mortar AND Raman AND calcite)']
for q in qs:
    for page in (1, 2, 3):
        r = get("https://doaj.org/api/search/articles/" + urllib.parse.quote(q), params={"pageSize": 50, "page": page}, min_gap=2)
        if r.status_code != 200: print("fail", q, r.status_code); break
        d = r.json().get("results", [])
        if not d: break
        for it in d:
            b = it["bibjson"]
            doi = next((i["id"].lower() for i in b.get("identifier", []) if i["type"] == "doi"), None)
            key = doi or b["title"][:50]
            if key in res or (doi and doi in K): continue
            ab = b.get("abstract", "") or ""
            res[key] = (b.get("year"), (b.get("author") or [{}])[0].get("name", ""), b["title"][:105], (b.get("journal") or {}).get("title", "")[:28], ab.lower().count("calcite"), ab.lower().count("raman"), [l["url"] for l in b.get("link", []) if l.get("type") == "fulltext"][:1])
    print(q[:50], len(res), flush=True)
json.dump(res, open("doaj.json", "w"))
for k, v in sorted(res.items(), key=lambda kv: -(kv[1][4])):
    if v[5] >= 1 and v[4] >= 1: print(k, *v, sep=" | ")
