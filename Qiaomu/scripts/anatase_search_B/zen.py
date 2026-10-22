import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
for rid in sys.argv[1:]:
    rid = rid.split("zenodo.")[-1]
    r = get(f"https://zenodo.org/api/records/{rid}", gap=6)
    if r.status_code != 200:
        print(rid, "ERR", r.status_code); continue
    j = r.json(); m = j["metadata"]
    print("##", rid, m["title"][:120], "|", m.get("publication_date"), "|", m.get("license", {}).get("id"), "| related:", [x.get("identifier") for x in m.get("related_identifiers", [])][:3])
    print("   ", re.sub(r"<[^>]+>", " ", m.get("description", ""))[:500].replace("\n", " "))
    for f in j.get("files", [])[:12]:
        print("   file:", f["key"], f["size"], f["links"]["self"])
