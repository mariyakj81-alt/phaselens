"""Print all paragraphs/captions containing Raman from cached xml. Usage: ramtext.py PMC [maxchars]"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_all as S
import xml.etree.ElementTree as ET
pmc=sys.argv[1]; mx=int(sys.argv[2]) if len(sys.argv)>2 else 6000
root=ET.parse(os.path.join(S.CACHE,pmc+".xml")).getroot()
body=root.find(".//body")
out=[]
for el in body.iter():
    if el.tag in ("p","caption"):
        t=S.itertext_marked(el)
        if "Raman" in t and len(t)>40: out.append(t)
seen=set(); txt=[]
for t in out:
    if t in seen: continue
    seen.add(t); txt.append(t)
s="\n- ".join(txt)
print(s[:mx])
# tables
for tw in body.iter("table-wrap"):
    cap=tw.find("caption"); ct=S.itertext_marked(cap) if cap is not None else ""
    tt=" | ".join(S.itertext_marked(td) for td in tw.iter("td"))
    if re.search("Raman",ct+tt): print("TABLE:",ct[:200],"::",tt[:800])
