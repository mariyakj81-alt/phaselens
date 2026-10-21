"""EPMC OA full-text funnel: collect PMCIDs for calcite+Raman, score S3 XML for calcite Raman peak numbers. python -P funnel.py OUT.json"""
import sys, re, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
OUT = sys.argv[1]
RANGES = {"155": (145, 170), "282": (272, 295), "712": (703, 722), "1086": (1078, 1094), "1436": (1426, 1446), "1749": (1738, 1760)}
NUM = re.compile(r"(?<![\d.])(\d{3,4})(?:\.\d+)?(?![\d])")
S3 = "https://pmc-oa-opendata.s3.amazonaws.com/"
qs = ['"calcite" AND "Raman" AND ("cm-1" OR "cm−1") AND OPEN_ACCESS:y',
      '"calcite" AND "Raman spectroscopy" AND "peak" AND OPEN_ACCESS:y',
      '"Raman" AND "calcite" AND "aragonite" AND "vaterite" AND OPEN_ACCESS:y',
      '"Mg-calcite" AND "Raman" AND OPEN_ACCESS:y',
      '"calcitic" AND "Raman" AND OPEN_ACCESS:y',
      '"calcite" AND "Raman" AND ("532 nm" OR "785 nm" OR "633 nm" OR "514 nm" OR "488 nm" OR "1064 nm") AND OPEN_ACCESS:y']
cands = {}
for q in qs:
    cursor = "*"
    for page in range(5):
        r = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query": q, "format": "json", "resultType": "lite", "pageSize": 100, "cursorMark": cursor}, min_gap=1)
        if r.status_code != 200: break
        j = r.json()
        for w in j["resultList"]["result"]:
            if w.get("pmcid"): cands.setdefault(w["pmcid"], {"doi": w.get("doi"), "title": w.get("title"), "year": w.get("pubYear"), "journal": w.get("journalTitle")})
        nc = j.get("nextCursorMark")
        if not nc or nc == cursor or len(j["resultList"]["result"]) < 100: break
        cursor = nc
    print(q[:60], j.get("hitCount"), len(cands), flush=True)
res = json.load(open(OUT)) if os.path.exists(OUT) else {}
for i, (pm, meta) in enumerate(cands.items()):
    if pm in res: continue
    r = get(S3 + f"?prefix={pm}.&max-keys=300", min_gap=0.5)
    keys = re.findall(r"<Key>(.*?)</Key>", r.text)
    xk = [k for k in keys if k.endswith(".xml") and k.split("/")[-1].startswith("PMC")]
    if not xk: res[pm] = dict(meta, err="no s3 xml"); continue
    x = get(S3 + xk[0], min_gap=0.5, timeout=120)
    txt = re.sub(r"<[^>]+>", " ", x.text); txt = re.sub(r"\s+", " ", txt)
    low = txt.lower()
    found = {}
    for mm in NUM.finditer(txt):
        v = int(mm.group(1))
        for k, (lo, hi) in RANGES.items():
            if lo <= v <= hi:
                ctx = txt[max(0, mm.start()-200): mm.end()+200].lower()
                if ("calcite" in ctx or "caco" in ctx or "mg-cal" in ctx or "carbonate" in ctx) and ("cm" in ctx or "raman" in ctx):
                    found.setdefault(k, set()).add(v)
    res[pm] = dict(meta, raman=low.count("raman"), calcite=low.count("calcite"), arag=low.count("aragonite"), vat=low.count("vaterite"), modes={k: sorted(v) for k, v in found.items()}, nmodes=len(found), suppl=[k.split("/")[-1] for k in keys if not k.lower().endswith((".jpg", ".gif", ".png", ".json", ".txt", ".xml", ".pdf"))][:5])
    if i % 20 == 0:
        json.dump(res, open(OUT, "w"), indent=1); print(i, len(cands), flush=True)
json.dump(res, open(OUT, "w"), indent=1)
print("done", len(res))
