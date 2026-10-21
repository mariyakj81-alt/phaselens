"""Compact view: Raman paragraphs containing anatase-range numbers (+tables). Usage: ram2.py PMC [maxchars]"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_all as S
import xml.etree.ElementTree as ET
pool=json.load(open(S.POOL,encoding="utf-8")); sc=json.load(open(S.SCORES,encoding="utf-8"))
def view(pmc,mx=1800):
    root=ET.parse(os.path.join(S.CACHE,pmc+".xml")).getroot()
    body=root.find(".//body"); v=sc.get(pmc,{}); p=pool.get(pmc,{})
    print("="*90); print(pmc,p.get("year"),v.get("doi"),"|",p.get("journal"),"|",re.sub(r"<[^>]+>","",p.get("title") or "")[:120])
    print(" R",v.get("raman"),"A",v.get("anatase"),"lasers",v.get("lasers"),"suppl",p.get("hasSuppl"),"data",v.get("data"),"flags",v.get("flags"))
    out=[]; seen=set()
    for el in body.iter():
        if el.tag in ("p","caption"):
            t=S.itertext_marked(el)
            if "Raman" not in t or t in seen: continue
            seen.add(t)
            ok=any(any(lo<=int(m.group(1))<=hi for lo,hi in S.MODES.values()) for m in S.NUM.finditer(t))
            if ok: out.append(t)
    s=" || ".join(out)
    print(s[:mx])
    for tw in body.iter("table-wrap"):
        cap=tw.find("caption"); ct=S.itertext_marked(cap) if cap is not None else ""
        tt=" | ".join(S.itertext_marked(td) for td in tw.iter("td"))
        if re.search("Raman",ct): print("  TABLE:",ct[:150],"::",tt[:500])
if __name__=="__main__":
    mx=1800
    ids=[a for a in sys.argv[1:] if a.startswith("PMC")]
    for a in sys.argv[1:]:
        if a.isdigit(): mx=int(a)
    for i in ids: view(i,mx)
