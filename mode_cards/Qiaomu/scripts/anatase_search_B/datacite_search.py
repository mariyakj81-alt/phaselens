import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get

queries = sys.argv[1:] or ["anatase Raman", "TiO2 Raman spectra", "anatase Raman high pressure", "anatase single crystal Raman",
                           "TiO2 anatase Raman temperature"]
seen = {}
for q in queries:
    for page in (1, 2):
        r = get("https://api.datacite.org/dois", params={"query": q, "resource-type-id": "dataset", "page[size]": 50, "page[number]": page}, gap=2)
        if r.status_code != 200:
            print("ERR", q, r.status_code); break
        js = r.json()
        for it in js["data"]:
            a = it["attributes"]
            doi = a["doi"]
            if doi in seen: continue
            title = (a.get("titles") or [{}])[0].get("title", "")
            desc = " ".join(d.get("description", "") for d in (a.get("descriptions") or []))
            txt = (title + " " + desc).lower()
            if "anatase" in txt or ("tio2" in txt and "raman" in txt) or ("titan" in txt and "raman" in txt):
                seen[doi] = (title, a.get("publisher"), a.get("publicationYear"), [x.get("relatedIdentifier") for x in a.get("relatedIdentifiers", []) if x.get("relatedIdentifierType") == "DOI"][:3], desc[:200])
        if len(js["data"]) < 50: break
print(len(seen))
for k, v in seen.items():
    print(k, "|", v[0][:110], "|", v[1], v[2], v[3])
    print("    ", v[4].replace("\n", " ")[:200])
json.dump(seen, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "datacite_hits.json"), "w"), indent=1)
