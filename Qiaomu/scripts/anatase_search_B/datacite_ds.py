import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
seen = {}
qs = ["TiO2 Raman", "anatase Raman", "titanium dioxide Raman spectra", "titania Raman", "TiO2 nanoparticles Raman spectra", "TiO2 thin films Raman", "TiO2 nanotubes Raman", "anatase rutile Raman", "TiO2 spectroscopy Raman XRD data", "titanium oxide Raman raw data"]
for q in qs:
    for page in (1, 2, 3, 4):
        r = get("https://api.datacite.org/dois", params={"query": q, "resource-type-id": "dataset", "page[size]": 100, "page[number]": page}, gap=2)
        if r.status_code != 200: print("ERR", q, r.status_code); break
        js = r.json()
        for it in js["data"]:
            a = it["attributes"]; doi = a["doi"]
            if doi in seen: continue
            title = (a.get("titles") or [{}])[0].get("title", "")
            desc = re.sub(r"<[^>]+>", " ", " ".join(d.get("description", "") for d in (a.get("descriptions") or [])))
            txt = (title + " " + desc).lower()
            seen[doi] = 1
            if "raman" in txt and re.search(r"anatase|tio2|tio₂|titania|titanium dioxide|titanium oxide", txt):
                rel = [x.get("relatedIdentifier") for x in a.get("relatedIdentifiers", []) if x.get("relatedIdentifierType") == "DOI" and x.get("relationType") in ("IsSupplementTo", "IsReferencedBy", "IsCitedBy", "IsDescribedBy")]
                print(doi, "|", a.get("publicationYear"), "|", (a.get("publisher") or "")[:18], "|", title[:85], "|", rel[:1])
        if len(js["data"]) < 100: break
print("seen", len(seen))
