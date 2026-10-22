import sys, json, re, csv, collections
sys.path.insert(0, '.')
from common import get
from known import known, ROOT
K = known()
rows = list(csv.DictReader(open(ROOT + "/calcite/papers.csv", encoding="utf-8")))
cnt = collections.Counter(); who = collections.defaultdict(list)
for r in rows:
    d = r["doi"].strip().lower()
    if not d: continue
    resp = get("https://api.crossref.org/works/" + d, min_gap=1.0)
    if resp.status_code != 200: print("fail", d); continue
    refs = resp.json()["message"].get("reference", [])
    n = 0
    for x in refs:
        rd = (x.get("DOI") or "").lower()
        if rd:
            cnt[rd] += 1; who[rd].append(r["paper_id"]); n += 1
    print(r["paper_id"], d, len(refs), n, flush=True)
json.dump({k: [v, who[k]] for k, v in cnt.items()}, open("refgraph.json", "w"))
