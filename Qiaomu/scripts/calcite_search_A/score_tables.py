import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cfg_A import CACHE
import sys,os,re,json
import xml.etree.ElementTree as ET
SP=CACHE
recs=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"work","records.json")))
s=json.load(open(os.path.join(SP,"scores.json")))
WIN={"T":(150,161),"L":(274,291),"v4":(704,720),"v1":(1080,1092),"v3":(1428,1445),"2v2":(1742,1755)}
numre=re.compile(r"(?<![\d.])(\d{3,4}(?:[.,]\d+)?)(?![\d])")
out={}
for k,r in recs.items():
    pm=r["pmcid"]
    if not pm or k not in s or "err" in s[k]: continue
    fp=os.path.join(SP,pm+".xml")
    try: root=ET.parse(fp).getroot()
    except Exception: continue
    for tw in root.iter("table-wrap"):
        t=re.sub(r"\s+"," ","".join(tw.itertext()))
        tl=t.lower()
        if "raman" not in tl and "cm" not in tl: continue
        if not re.search(r"(?i)calcite|caco|carbonate|ν1|v1|\bν\d",t): continue
        modes=set()
        for m in numre.finditer(t):
            x=float(m.group(1).replace(",","."))
            for nm,(a,b) in WIN.items():
                if a<=x<=b: modes.add(nm)
        if len(modes)>=2:
            out.setdefault(k,[]).append({"modes":sorted(modes),"txt":t[:300]})
json.dump(out,open(os.path.join(SP,"tables.json"),"w"))
print(len(out))
for k,v in out.items():
    r=recs[k]; sc=s[k]
    print(r["pmcid"],r["doi"],r["year"],re.sub("<[^>]+>","",r["title"])[:70],"| cal",sc["cal"],"nm",sc["nmodes"],"|",v[0]["modes"],v[0]["txt"][:150])
