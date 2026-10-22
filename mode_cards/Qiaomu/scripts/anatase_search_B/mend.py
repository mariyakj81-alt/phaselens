import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
for ds in sys.argv[1:]:
    ds = ds.split("/")[-1].split(".")[0]
    r = get(f"https://data.mendeley.com/public-api/datasets/{ds}", gap=6)
    if r.status_code != 200:
        print(ds, "ERR", r.status_code); continue
    j = r.json()
    print("##", ds, j.get("name", "")[:110], "| v", j.get("version"), "|", (j.get("publish_date") or "")[:10], "| lic:", (j.get("data_licence") or {}).get("short_name"))
    print("   ", re.sub(r"<[^>]+>", " ", j.get("description", ""))[:420].replace("\n", " "))
    print("   related:", [(x.get("type"), (x.get("title") or "")[:80], x.get("doi")) for x in j.get("related_links", [])][:3], [a.get("doi") for a in j.get("articles", [])][:3])
    for f in j.get("files", [])[:15]:
        print("   file:", f.get("filename"), f.get("size"), (f.get("content_details") or {}).get("download_url", "")[:100])
