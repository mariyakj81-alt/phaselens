import sys, json, csv, collections, re
sys.path.insert(0, '.')
from common import get
from known import ROOT
seeds = []
for f in ("calcite/papers.csv", "calcite/papers_new_A.csv"):
    for r in csv.DictReader(open(ROOT + "/" + f, encoding="utf-8")):
        if r["doi"].strip(): seeds.append(r["doi"].strip().lower())
seeds += ["10.1002/jrs.2835", "10.2138/am-2018-6442", "10.1016/j.pepi.2018.05.002", "10.1002/jrs.5481", "10.1002/jrs.5156", "10.1016/j.saa.2005.02.026", "10.1002/jrs.1518", "10.1366/0003702874448841", "10.1039/a908609i", "10.1002/jrs.806", "10.1088/0022-3719/7/24/015", "10.1007/bf00202245", "10.1002/jrs.2438", "10.1002/jrs.4622", "10.1002/jrs.6174", "10.1016/j.icarus.2020.113969", "10.1016/j.pss.2021.105356", "10.1016/j.saa.2007.06.036", "10.1016/j.saa.2006.12.043", "10.1080/08957959.2017.1384824", "10.2138/am.2005.1954", "10.2138/am.2012.4116", "10.1007/s00269-016-0815-8", "10.1002/jrs.5893", "10.1016/j.saa.2021.119980", "10.3390/min13111358", "10.1002/jrs.6097", "10.1002/jrs.4218", "10.1002/ceat.200500354", "10.1081/sl-100107901", "10.1002/jrs.5235", "10.1016/j.aca.2023.340798", "10.1039/c4cp01772b"]
seeds = list(dict.fromkeys(seeds))
cnt = collections.Counter(); who = collections.defaultdict(list)
for s in seeds:
    try:
        r = get("https://opencitations.net/index/coci/api/v1/citations/" + s, min_gap=1.5, timeout=90)
    except Exception as e:
        print("exc", s); continue
    if r.status_code != 200: print("fail", s, r.status_code); continue
    c = [x["citing"].lower() for x in r.json()]
    for d in c: cnt[d] += 1; who[d].append(s)
    print(s, len(c), flush=True)
json.dump({d: [n, who[d]] for d, n in cnt.items()}, open("cites.json", "w"))
print(len(cnt), sum(1 for n in cnt.values() if n >= 2))
