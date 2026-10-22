import sys, re, json
sys.path.insert(0, '.')
from common import get
from known import known
K = known()
qs = ["calcite Raman", "calcium carbonate Raman", "Mg-calcite Raman", "carbonate Raman spectra", "Raman spectra calcite aragonite",
      "Raman spectra biogenic calcite", "carbonate minerals Raman", "calcite polymorph Raman", "CaCO3 Raman", "Raman calcite high pressure",
      "Raman spectra limestone", "Raman spectra speleothem", "Raman foraminifera calcite", "Raman coccolith calcite", "Raman mollusc shell calcite prismatic",
      "Raman spectra marble", "Raman carbonate meteorite", "Raman dolomite calcite", "vaterite calcite Raman", "Raman otolith echinoderm calcite",
      "Raman spectra carbonate temperature series", "calcite lattice modes", "Raman brachiopod calcite", "Raman spectroscopy calcite crystals dataset"]
seen = {}
for q in qs:
    for page in (1, 2):
        try:
            r = get("https://api.datacite.org/dois", params={"query": q, "resource-type-id": "dataset", "page[size]": 100, "page[number]": page}, min_gap=2)
        except Exception as e:
            print("exc", q, e); break
        if r.status_code != 200: print("fail", q, page, r.status_code); break
        d = r.json().get("data", [])
        if not d: break
        for it in d:
            a = it["attributes"]; title = (a.get("titles") or [{}])[0].get("title", "") or ""
            desc = " ".join(x.get("description", "") or "" for x in (a.get("descriptions") or []))
            txt = (title + " " + desc).lower()
            if "raman" in txt and ("calcite" in txt or "caco" in txt or "calcium carbonate" in txt or "carbonate" in txt):
                if it["id"] not in seen:
                    rel = [(x.get("relatedIdentifier"), x.get("relationType")) for x in (a.get("relatedIdentifiers") or [])]
                    seen[it["id"]] = (a.get("publicationYear"), a.get("publisher"), title[:120], rel[:4], txt.count("calcite"))
    print(q, len(seen), flush=True)
json.dump(seen, open("dc_results.json", "w"), indent=1)
for k, v in sorted(seen.items(), key=lambda kv: (-(kv[1][4]), kv[1][0] or 0)):
    flag = " KNOWN" if any((x[0] or "").lower() in K for x in v[3]) else ""
    print(k, v, flag)
