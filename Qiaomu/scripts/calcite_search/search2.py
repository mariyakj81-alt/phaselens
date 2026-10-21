import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from common import get
OUT = sys.argv[1]
queries = [
 "calcite diamond anvil cell Raman phase transition calcite II calcite III",
 "calcite Raman low temperature cryogenic spectra",
 "calcite Raman high temperature peak shift linewidth anharmonic",
 "Raman spectroscopy calcite nanoparticles size effect",
 "Sr-doped calcite Raman", "Mn calcite Raman", "calcite Raman shock impact deformation",
 "coccolith calcite Raman", "foraminifera calcite Raman Mg/Ca", "sea urchin spine magnesian calcite Raman",
 "eggshell calcite Raman spectrum", "mollusc shell calcite aragonite Raman peak positions",
 "portable Raman calcite 785 nm", "calcite 532 nm Raman spectra carbonate minerals database",
 "carbonate minerals Raman calcite dolomite magnesite siderite internal modes", 
 "calcite Raman oriented single crystal polarization symmetry Eg A1g",
 "calcite ultraviolet Raman", "calcite Raman spectral library RRUFF carbonate",
 "calcite Raman stress strain micro-Raman", "calcite twin Raman crystallographic orientation",
 "vaterite calcite Raman lattice phonon", "amorphous calcium carbonate Raman calcite crystallization in situ",
 "calcite Raman first-principles DFT phonon frequencies experimental comparison",
 "calcite aragonite Raman quantitative mixture", "cave calcite speleothem Raman", "stromatolite microbial calcite Raman",
 "calcite Raman Mars analogue carbonate", "calcite coral skeleton Raman", "calcite crystallite size Raman FWHM 1086",
 "calcite Raman 1750 cm-1 overtone", "calcite 2nu2 Raman combination band", "calcite Raman 18O 13C isotopic shift",
 "marble limestone Raman calcite", "pigment calcite Raman cultural heritage peak positions",
 "calcite hydrothermal diamond anvil Raman in situ", "calcite decomposition Raman heating CaO",
]
res = {}
def abstr(w):
    ii = w.get("abstract_inverted_index")
    if not ii: return ""
    pos = {}
    for word, ps in ii.items():
        for p in ps: pos[p] = word
    return " ".join(pos[i] for i in sorted(pos))
for q in queries:
    r = get("https://api.openalex.org/works", params={"search": q, "per-page": 30, "filter": "type:article"}, min_gap=1)
    if r.status_code != 200:
        print("OA fail", q, r.status_code); continue
    for w in r.json().get("results", []):
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
        key = doi or w["id"]
        locs = [(l.get("pdf_url"), l.get("landing_page_url"), l.get("version")) for l in w.get("locations", []) if l.get("is_oa")]
        e = res.setdefault(key, {"doi": doi, "title": w["title"], "year": w["publication_year"], "oa": w["open_access"]["is_oa"],
            "oa_status": w["open_access"].get("oa_status"), "locs": locs, "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", [])][:3], "abstract": abstr(w), "queries": []})
        e["queries"].append(q)
    print("OA", q, len(res), flush=True)
json.dump(res, open(OUT, "w"), indent=1)
