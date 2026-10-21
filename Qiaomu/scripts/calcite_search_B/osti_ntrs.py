import sys, json, re, urllib.parse
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
seen = {}
for q in ["calcite Raman", "calcite Raman spectroscopy", "calcium carbonate Raman", "carbonate Raman spectra", "Mg-calcite Raman", "calcite Raman high pressure", "calcite Raman temperature", "CaCO3 Raman", "Raman spectroscopy carbonate minerals"]:
    for page in (0, 1):
        r = get("https://www.osti.gov/api/v1/records", params={"q": q, "rows": 50, "page": page}, min_gap=2, headers={"Accept": "application/json"})
        if r.status_code != 200: print("osti fail", r.status_code); break
        for it in r.json():
            doi = (it.get("doi") or "").lower()
            t = it.get("title", "")
            ab = (it.get("description") or "")
            if re.search(r"raman", t + ab, re.I) and re.search(r"calcite|carbonate|CaCO", t + ab, re.I) and it["osti_id"] not in seen:
                link = [l["href"] for l in it.get("links", []) if l.get("rel") in ("fulltext", "citation")]
                seen[it["osti_id"]] = (it.get("publication_date", "")[:4], doi, t[:100], it.get("product_type"), ab.lower().count("calcite"), link[:1])
print("OSTI", len(seen))
for k, v in sorted(seen.items(), key=lambda kv: -kv[1][4]): print(k, *v, "KNOWN" if v[1] in K else "", sep=" | ")
