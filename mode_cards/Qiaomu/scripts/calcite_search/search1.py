import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from common import get
OUT = sys.argv[1]
queries = [
 "calcite Raman spectrum", "calcite Raman peak assignment", "calcite Raman high pressure",
 "calcite Raman temperature dependence", "Mg calcite Raman shift", "biogenic calcite Raman",
 "calcium carbonate polymorphs Raman calcite aragonite vaterite", "calcite Raman 1086 cm-1 FWHM",
 "calcite Raman isotope 13C", "calcite Raman laser wavelength", "magnesian calcite Raman spectroscopy composition",
 "calcite single crystal polarized Raman", "calcite lattice modes Raman low frequency",
 "calcite Raman spectroscopy amorphous calcium carbonate transformation",
]
res = {}
for q in queries:
    r = get("https://api.openalex.org/works", params={"search": q, "per-page": 40, "filter": "type:article"}, min_gap=1)
    if r.status_code != 200:
        print("OA fail", q, r.status_code); continue
    for w in r.json().get("results", []):
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        key = doi or w["id"]
        loc = w.get("best_oa_location") or {}
        res.setdefault(key, {"doi": doi, "title": w["title"], "year": w["publication_year"], "oa": w["open_access"]["is_oa"],
            "pdf": loc.get("pdf_url"), "landing": loc.get("landing_page_url"), "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])][:3], "queries": []})["queries"].append(q)
    print("OA", q, len(res))
    r = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query": q + " AND OPEN_ACCESS:y", "format": "json", "resultType": "core", "pageSize": 40}, min_gap=1)
    if r.status_code == 200:
        for w in r.json().get("resultList", {}).get("result", []):
            doi = (w.get("doi") or "").lower()
            key = doi or w.get("id")
            e = res.setdefault(key, {"doi": doi, "title": w.get("title"), "year": w.get("pubYear"), "oa": True, "pdf": None, "landing": None,
                "venue": w.get("journalTitle"), "authors": [w.get("authorString", "")[:60]], "queries": []})
            e["pmcid"] = w.get("pmcid"); e["epmc"] = True
            e["queries"].append("EPMC:" + q)
    else:
        print("EPMC fail", q, r.status_code)
json.dump(res, open(OUT, "w"), indent=1)
print(len(res))
