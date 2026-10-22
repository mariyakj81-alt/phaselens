import sys, re, json
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
seen = {}
for q in ["Raman calcite", "Raman spectrum calcite", "Raman effect calcite", "calcite crystal Raman lattice", "Raman carbonates", "Raman spectra dolomite calcite aragonite", "Raman spectra of calcite polarisation", "calcite temperature Raman", "Raman spectra rhombohedral carbonates"]:
    for cont in ["Proceedings of the Indian Academy of Sciences - Section A", "Pramana", "Proceedings of the Indian Academy of Sciences - Section B", "Current Science", "Indian Journal of Physics"]:
        r = get("https://api.crossref.org/works", params={"query.title": q, "query.container-title": cont, "rows": 15, "select": "DOI,title,issued,container-title,volume,issue,page,author"}, min_gap=1.2)
        if r.status_code != 200: continue
        for it in r.json()["message"]["items"]:
            t = (it.get("title") or [""])[0]
            if re.search(r"calcite|carbonate|CaCO|dolomite|aragonite|rhombohedral|crystal", t, re.I) and re.search(r"raman|spectr|scatter", t, re.I):
                seen[it["DOI"].lower()] = (it.get("issued", {}).get("date-parts", [[None]])[0][0], (it.get("author") or [{}])[0].get("family", ""), t[:100], (it.get("container-title") or [""])[0][:30], it.get("volume"), it.get("issue"), it.get("page"))
for d, v in sorted(seen.items(), key=lambda kv: kv[1][0] or 0):
    print(d, v, "KNOWN" if d in K else "")
