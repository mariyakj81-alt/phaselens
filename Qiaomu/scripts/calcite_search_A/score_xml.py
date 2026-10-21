import sys,os,re,json,csv; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_A import *
import xml.etree.ElementTree as ET
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
XD = os.environ.get("CALA_XML_DIR") or os.path.join(W, "xml"); os.makedirs(XD, exist_ok=True)
recs = json.load(open(os.path.join(W, "records.json")))
# exclusions
import pandas as pd
known = set()
for f in ("calcite/papers.csv", "calcite/candidates_rejected.csv"):
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    known |= set(x.lower() for x in d["doi"] if x)
WIN = {"T":(150,161),"L":(274,291),"v4":(704,720),"v1":(1080,1092),"v3":(1428,1445),"2v2":(1742,1755)}
numre = re.compile(r"(?<![\d.])(\d{3,4}(?:[.,]\d+)?)(?![\d])")
def text_of(root):
    # drop reference lists
    for p in list(root.iter()):
        for ch in list(p):
            if ch.tag in ("ref-list",): p.remove(ch)
    paras = []
    for el in root.iter():
        if el.tag in ("p","td","th","title","caption","label"):
            t = "".join(el.itertext())
            paras.append(re.sub(r"\s+", " ", t))
    return paras
def lasers(txt):
    s = set()
    for m in re.finditer(r"(\d{3}(?:\.\d+)?)\s*-?\s*nm", txt):
        v = float(m.group(1))
        ctx = txt[max(0,m.start()-80):m.end()+80].lower()
        if 244<=v<=1100 and ("laser" in ctx or "excit" in ctx or "raman" in ctx): s.add(m.group(1))
    return sorted(s)
out = {}
OUTF = os.path.join(XD, "scores.json")
if os.path.exists(OUTF): out = json.load(open(OUTF))
items = [(k,v) for k,v in recs.items() if v["pmcid"] and v["doi"] not in known]
print("to score", len(items), flush=True)
for i,(k,v) in enumerate(items):
    if k in out: continue
    pm = v["pmcid"]; fp = os.path.join(XD, pm + ".xml")
    if not os.path.exists(fp):
        r = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pm}/fullTextXML", min_gap=0.4)
        if r.status_code != 200:
            out[k] = {"err": r.status_code}; continue
        open(fp, "wb").write(r.content)
    try:
        root = ET.parse(fp).getroot()
    except Exception as e:
        out[k] = {"err": "parse"}; continue
    paras = text_of(root)
    full = " ".join(paras)
    cal = len(re.findall(r"(?i)calcite", full)); ram = len(re.findall(r"(?i)raman", full))
    modes = {}
    for p in paras:
        pl = p.lower()
        if "calcite" not in pl and "caco3" not in pl.replace("caco₃","caco3"): continue
        if "raman" not in pl and "cm" not in pl: continue
        for m in numre.finditer(p):
            x = float(m.group(1).replace(",", "."))
            for nm,(a,b) in WIN.items():
                if a<=x<=b: modes.setdefault(nm, set()).add(m.group(1))
    out[k] = {"cal": cal, "ram": ram, "modes": {a: sorted(b) for a,b in modes.items()}, "nmodes": len(modes), "lasers": lasers(full), "len": len(full)}
    if i % 50 == 0:
        json.dump(out, open(OUTF, "w")); print(i, len(items), "\n", end="", flush=True)
json.dump(out, open(OUTF, "w"))
print("done")
