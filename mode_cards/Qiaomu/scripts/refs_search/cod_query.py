import sys,re,json,os
sys.path.insert(0,os.path.dirname(__file__))
from common import *
S="C:/Users/yqm12/AppData/Local/Temp/claude/G--My-Drive-Qiaomu-Coding-LLM-Hackason/6904f568-fbff-48aa-b9f2-a1642df7e094/scratchpad/refs_search_x/"
Q={"calcite":dict(text="calcite",el1="C",el2="Ca",el3="O",nel=3),
   "anatase":dict(text="anatase",el1="O",el2="Ti",nel=2),
   "quartz":dict(text="quartz",el1="O",el2="Si",nel=2),
   "silicon":dict(el1="Si",nel=1,vmin=159.5,vmax=161.0),
   "mos2":dict(el1="Mo",el2="S",nel=2,vmin=104,vmax=109)}
fn=S+"cod_candidates.json"
out=json.load(open(fn)) if os.path.exists(fn) else {}
for k,p in Q.items():
    if k in out: continue
    p=dict(p); p["format"]="json"
    try:
        r=get("https://www.crystallography.net/cod/result",params=p,min_gap=5)
        out[k]=r.json(); print(k,len(out[k]),flush=True)
    except Exception as e:
        print(k,"ERR",repr(e)[:150],flush=True)
    json.dump(out,open(fn,"w"))
def show(k,filt=lambda e:True):
    for e in sorted(out[k],key=lambda e:e['year'] or ''):
        if not filt(e): continue
        print(e['file'],e['sg'],e['a'],e['c'],'T',e['celltemp'],e['diffrtemp'],'P',e['cellpressure'],e['diffrpressure'],'R',e['Robs'],e['Rall'],e['wRall'],'|',(e['authors'] or '')[:40],e['year'],'|',(e['journal'] or '')[:25],e['volume'],'|',e['mineral'],e['formula'],e['flags'],e['duplicateof'],e['status'])
if __name__=="__main__":
    for k in out:
        print("=====",k,len(out[k]))
