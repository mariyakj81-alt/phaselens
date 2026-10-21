import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cfg_A import CACHE
import sys,os,json
SP=CACHE
recs=json.load(open("scripts/calcite_search_A/work/records.json"))
s=json.load(open(os.path.join(SP,"scores.json")))
rows=[]
for k,v in s.items():
    if "err" in v: continue
    r=recs[k]
    sc=v["nmodes"]*3+min(v["cal"],30)/5+min(v["ram"],30)/10
    rows.append((sc,k,v,r))
rows.sort(key=lambda x:-x[0])
N=int(sys.argv[1]) if len(sys.argv)>1 else 60
for sc,k,v,r in rows[:N]:
    print(f"{sc:5.1f} {r['pmcid']} {r['doi']} | {r['year']} {str(r['journal'])[:22]} | {r['title'][:75]} | cal{v['cal']} ram{v['ram']} m{v['nmodes']} {''.join(m+',' for m in v['modes'])} L{v['lasers']} S{r['suppl']}")
