"""Print compact dossiers (calcite Raman sentences with mode numbers) for scored candidates.
env CALA_XML_DIR = cache dir (xml + scores.json). usage: python -P dossier_A.py MIN_MODES [START] [N]  or  dossier_A.py ids PMC1 PMC2"""
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cfg_A import CACHE
import sys, os, re, json
import xml.etree.ElementTree as ET
SP = CACHE
recs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "records.json")))
scores = json.load(open(os.path.join(SP, "scores.json")))
WIN = {"T": (150, 161), "L": (274, 291), "v4": (704, 720), "v1": (1080, 1092), "v3": (1428, 1445), "2v2": (1742, 1755)}
numre = re.compile(r"(?<![\d.])(\d{3,4}(?:[.,]\d+)?)(?![\d])")
TAGS = {"press": r"(?i)diamond anvil|GPa|high.pressure", "temp": r"(?i)heating|temperature.dependent|in situ.{0,30}temperature|°C.{0,40}Raman|hot stage|Linkam",
        "pol": r"(?i)polariz", "xtal": r"(?i)single crystal|iceland spar", "fwhm": r"(?i)FWHM|full width", "iso": r"(?i)13C|18O|isotop",
        "mg": r"(?i)Mg.?calcite|magnesian calcite|mol ?% ?Mg|Mg/Ca", "data": r"(?i)zenodo|figshare|dryad|mendeley data|source data|data availability.{0,200}(repository|deposited)",
        "table": r"(?i)Table \d+.{0,200}(Raman|cm)", "uv": r"(?i)\b(244|248|266|325|355)\s*nm"}

def paras_of(fp):
    root = ET.parse(fp).getroot()
    for p in list(root.iter()):
        for ch in list(p):
            if ch.tag == "ref-list": p.remove(ch)
    out = []
    for el in root.iter():
        if el.tag in ("p", "td", "th", "caption"):
            out.append(re.sub(r"\s+", " ", "".join(el.itertext())))
    return out

def dossier(pm, maxs=3, width=420):
    fp = os.path.join(SP, pm + ".xml")
    paras = paras_of(fp)
    full = " ".join(paras)
    tags = [k for k, rx in TAGS.items() if re.search(rx, full)]
    sents = []
    for p in paras:
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", p):
            sl = s.lower()
            if "calcite" not in sl and "caco" not in sl: continue
            hit = set()
            for m in numre.finditer(s):
                x = float(m.group(1).replace(",", "."))
                for nm, (a, b) in WIN.items():
                    if a <= x <= b: hit.add(nm)
            if len(hit) >= 1 and ("cm" in sl or "raman" in sl or "peak" in sl or "band" in sl):
                sents.append((len(hit), s))
    sents.sort(key=lambda x: -x[0])
    return tags, sents[:maxs], width

if __name__ == "__main__":
    if sys.argv[1] == "ids":
        ids = sys.argv[2:]
    else:
        mn = int(sys.argv[1]); st = int(sys.argv[2]) if len(sys.argv) > 2 else 0; n = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        cand = []
        for k, v in scores.items():
            if "err" in v or v["nmodes"] < mn: continue
            r = recs[k]
            cand.append((v["nmodes"] * 3 + min(v["cal"], 30) / 5 + min(v["ram"], 30) / 10, r["pmcid"]))
        cand.sort(reverse=True)
        ids = [c[1] for c in cand][st:st + n]
    bypm = {r["pmcid"]: (k, r) for k, r in recs.items() if r["pmcid"]}
    for pm in ids:
        k, r = bypm[pm]; v = scores.get(k, {})
        tags, sents, width = dossier(pm)
        print(f"## {pm} {r['doi']} | {r['year']} | {r['title'][:90]} | cal{v.get('cal')} ram{v.get('ram')} m{v.get('nmodes')} L{v.get('lasers')} S{r['suppl']} lic={r['license']} tags={','.join(tags)}")
        for ns, s in sents:
            print("   -", s[:width])
