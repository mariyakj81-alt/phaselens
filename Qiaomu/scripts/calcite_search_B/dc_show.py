import sys, json, re
sys.path.insert(0, '.')
from common import get
for doi in sys.argv[1:]:
    r = get("https://api.datacite.org/dois/" + doi, min_gap=1.5)
    if r.status_code != 200: print(doi, r.status_code); continue
    a = r.json()["data"]["attributes"]
    print("==", doi, a.get("publicationYear"), a.get("publisher"))
    print("T:", (a["titles"] or [{}])[0].get("title"))
    for d in a.get("descriptions") or []:
        print("D:", re.sub(r"<[^>]+>", " ", d.get("description") or "")[:900])
    print("REL:", [(x.get("relatedIdentifier"), x.get("relationType")) for x in a.get("relatedIdentifiers") or []][:8])
    print("rights:", [x.get("rights") for x in a.get("rightsList") or []])
