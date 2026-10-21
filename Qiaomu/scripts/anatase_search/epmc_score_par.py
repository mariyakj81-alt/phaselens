import json, os, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,os.path.dirname(__file__))
import epmc_pool as ep
pool=json.load(open(ep.POOL,encoding="utf-8"))
todo=[k for k,v in pool.items() if v["score"] is None or "err" in (v["score"] or {})]
print("todo",len(todo),flush=True)
def work(k):
    try:
        r=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{k}/fullTextXML",headers=ep.UA,timeout=120)
        s=ep.score_xml(r.text) if r.status_code==200 else {"err":r.status_code}
    except Exception as e: s={"err":str(e)[:50]}
    time.sleep(0.5)
    return k,s
n=0
with ThreadPoolExecutor(4) as ex:
    for k,s in ex.map(work,todo):
        pool[k]["score"]=s; n+=1
        if n%25==0:
            json.dump(pool,open(ep.POOL,"w",encoding="utf-8")); print(n,flush=True)
json.dump(pool,open(ep.POOL,"w",encoding="utf-8")); print("done",flush=True)
