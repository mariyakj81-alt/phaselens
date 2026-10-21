import sys,os,re,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common_A import *
import pandas as pd
known=set()
for f in ("calcite/papers.csv","calcite/candidates_rejected.csv"):
    d=pd.read_csv(f,dtype=str,keep_default_na=False); known|=set(x.lower() for x in d.doi if x)
seen=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"work","records.json")))
seen_pm={r["pmcid"] for r in seen.values()}
qs=json.loads(sys.argv[1]) if sys.argv[1].startswith("[") else [sys.argv[1]]
for q in qs:
    hits,out=epmc_search(q,max_n=300)
    print("###",hits,q)
    for w in out:
        doi=(w.get("doi") or "").lower()
        if doi in known: continue
        tag="NEW" if w.get("pmcid") not in seen_pm else "   "
        print(tag,w.get("pmcid"),doi,w.get("pubYear"),re.sub("<[^>]+>","",w.get("title") or "")[:95],"|",w.get("hasSuppl"))
