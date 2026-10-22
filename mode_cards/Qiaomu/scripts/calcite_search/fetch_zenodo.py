"""Download all files of a Zenodo record (public, open access). Usage: python -P fetch_zenodo.py RECORD_ID DEST_DIR [max_mb]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
rid, dest = sys.argv[1], sys.argv[2]
maxmb = float(sys.argv[3]) if len(sys.argv) > 3 else 100
os.makedirs(dest, exist_ok=True)
j = get(f"https://zenodo.org/api/records/{rid}", min_gap=3).json()
meta = {"id": rid, "doi": j.get("doi"), "title": j["metadata"]["title"], "license": j["metadata"].get("license", {}).get("id"), "files": []}
for f in j.get("files", []):
    if f["size"] > maxmb * 1e6:
        print("skip large", f["key"], f["size"]); meta["files"].append({"name": f["key"], "size": f["size"], "skipped": True}); continue
    r = get(f["links"]["self"], min_gap=3, timeout=300)
    if r.status_code == 200:
        open(os.path.join(dest, f["key"]), "wb").write(r.content); print("ok", f["key"], len(r.content)); meta["files"].append({"name": f["key"], "size": f["size"]})
    else: print("fail", f["key"], r.status_code)
json.dump(meta, open(os.path.join(dest, "_zenodo_record.json"), "w"), indent=1)
