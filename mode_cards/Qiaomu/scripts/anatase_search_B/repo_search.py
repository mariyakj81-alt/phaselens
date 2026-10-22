"""Search Zenodo / Figshare / Dryad. Usage: repo_search.py zenodo|figshare|dryad "query" """
import sys, os, json, re, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, UA, throttle
which, q = sys.argv[1], sys.argv[2]
if which == "zenodo":
    for page in (1, 2):
        r = get("https://zenodo.org/api/records", params={"q": q, "size": 25, "page": page, "sort": "bestmatch"}, gap=5)
        if r.status_code != 200:
            print("ERR", r.status_code, r.text[:200]); break
        for h in r.json()["hits"]["hits"]:
            m = h["metadata"]
            files = h.get("files", [])
            desc = re.sub(r"<[^>]+>", " ", m.get("description", ""))
            txt = (m["title"] + " " + desc).lower()
            flag = "RAMAN" if "raman" in txt else ""
            flag += " ANAT" if ("anatase" in txt or "tio2" in txt or "tio₂" in txt or "titan" in txt) else ""
            print(h["doi"], "|", m["title"][:90], "|", m.get("resource_type", {}).get("type"), "|", len(files), "files |", flag, "|", [x["key"] for x in files][:4])
elif which == "figshare":
    throttle("https://api.figshare.com/v2/articles/search", 5)
    r = requests.post("https://api.figshare.com/v2/articles/search", json={"search_for": q, "page_size": 50}, headers=UA, timeout=60)
    if r.status_code != 200:
        print("ERR", r.status_code, r.text[:200])
    else:
        for h in r.json():
            print(h.get("doi"), "|", h["title"][:100], "|", h.get("defined_type_name"), "|", h.get("published_date", "")[:4])
elif which == "dryad":
    r = get("https://datadryad.org/api/v2/search", params={"q": q, "per_page": 50}, gap=5)
    if r.status_code != 200:
        print("ERR", r.status_code, r.text[:200])
    else:
        for h in r.json()["_embedded"]["stash:datasets"]:
            print(h.get("identifier"), "|", h["title"][:110], "|", h.get("publicationDate", "")[:4], "|", h.get("relatedWorks", [{}])[0].get("identifier") if h.get("relatedWorks") else "")
