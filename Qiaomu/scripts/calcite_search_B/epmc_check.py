import sys, json, re
sys.path.insert(0, '.')
from common import get
from known import known
import csv
K = known()
A = set(r["doi"].lower() for r in csv.DictReader(open("../../calcite/papers_new_A.csv", encoding="utf-8")))
dois = []
for f in ("cr5.json",):
    dois += list(json.load(open(f)).keys())
dois += [l.split()[0] for l in open("cr5_oa.txt", encoding="utf-8") if l.startswith("10.")]
dois += ["10.1007/s44211-024-00684-7", "10.1177/00037028251318757", "10.1002/jrs.70126", "10.1002/jrs.6097", "10.1177/00037028241281386", "10.1007/s00269-024-01269-6", "10.1002/jrs.6822", "10.1002/jrs.5481", "10.1002/jrs.3057", "10.1002/jrs.6483", "10.1002/jrs.6500", "10.1002/jrs.6711"]
dois = sorted(set(d.lower() for d in dois))
for d in dois:
    if d in K or d in A: continue
    r = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query": f'DOI:"{d}"', "format": "json", "resultType": "lite"}, min_gap=0.5)
    if r.status_code != 200: continue
    for w in r.json().get("resultList", {}).get("result", []):
        if w.get("pmcid"):
            print(d, w["pmcid"], w.get("isOpenAccess"), w.get("pubYear"), (w.get("title") or "")[:90], flush=True)
