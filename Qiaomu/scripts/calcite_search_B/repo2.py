import sys, json, re
sys.path.insert(0, '.')
from common import get
def pr(src, items):
    for it in items: print(src, "|", *it, sep=" | ")
# Harvard Dataverse and other Dataverse installs
for base in ["https://dataverse.harvard.edu", "https://dataverse.jpl.nasa.gov", "https://data.caltech.edu", "https://dataverse.nl", "https://darus.uni-stuttgart.de", "https://edmond.mpg.de", "https://dataverse.no", "https://entrepot.recherche.data.gouv.fr", "https://data.ub.uni-muenchen.de", "https://dataverse.csuc.cat", "https://borealisdata.ca"]:
    for q in ["calcite Raman", "Raman carbonate spectra"]:
        try:
            r = get(base + "/api/search", params={"q": q, "type": "dataset", "per_page": 30}, min_gap=2, timeout=40)
        except Exception as e:
            print(base, "EXC", type(e).__name__); break
        if r.status_code != 200: print(base, r.status_code); break
        its = []
        for it in r.json().get("data", {}).get("items", []):
            t = it.get("name", ""); d = it.get("description", "") or ""
            if re.search(r"raman", t + d, re.I) and re.search(r"calcite|carbonate|CaCO", t + d, re.I):
                its.append((it.get("global_id"), it.get("published_at", "")[:4], t[:100], d[:100].replace("\n", " ")))
        pr(base.split("//")[1], its)
# PANGAEA
for q in ["Raman calcite", "Raman spectra carbonate", "Raman spectroscopy calcite shell"]:
    r = get("https://ws.pangaea.de/es/pangaea/panmd/_search", params={"q": q, "size": 40}, min_gap=2)
    if r.status_code == 200:
        for h in r.json()["hits"]["hits"]:
            s = h["_source"]; t = s.get("citation_title") or s.get("title") or ""; d = s.get("description") or s.get("abstract") or ""
            if re.search(r"raman", t + str(d), re.I): print("PANGAEA |", h["_id"], "|", t[:110])
    else: print("pangaea", r.status_code)
