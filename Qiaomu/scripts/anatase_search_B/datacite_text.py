import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE
rtype = sys.argv[1]
seen = {}
for q in sys.argv[2:]:
    for page in (1, 2, 3):
        r = get("https://api.datacite.org/dois", params={"query": q, "resource-type-id": rtype, "page[size]": 100, "page[number]": page}, gap=2)
        if r.status_code != 200:
            print("ERR", q, r.status_code); break
        js = r.json()
        for it in js["data"]:
            a = it["attributes"]; doi = a["doi"]
            if doi in seen: continue
            title = (a.get("titles") or [{}])[0].get("title", "")
            desc = " ".join(d.get("description", "") for d in (a.get("descriptions") or []))
            txt = (title + " " + desc).lower()
            if "raman" in txt and ("anatase" in txt or "tio2" in txt or "tio₂" in txt or "titania" in txt or "titanium dioxide" in txt):
                seen[doi] = 1
                print(doi, "|", a.get("publicationYear"), "|", a.get("publisher"), "|", title[:100], "|", a.get("url", "")[:90])
        if len(js["data"]) < 100: break
