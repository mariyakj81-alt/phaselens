"""Fetch Europe PMC fullTextXML for every pool_all.json PMCID (cache in scratchpad) and score for anatase Raman evidence.
Usage: python -P score_all.py [fetch|score]"""
import requests, json, time, os, re, sys, html, threading
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
UA = {"User-Agent": "Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = r"C:\Users\yqm12\AppData\Local\Temp\claude\G--My-Drive-Qiaomu-Coding-LLM-Hackason\6904f568-fbff-48aa-b9f2-a1642df7e094\scratchpad\anaA\xml"
POOL = os.path.join(HERE, "pool_all.json")
SCORES = os.path.join(HERE, "scores_all.json")

def fetch_one(pmc):
    fn = os.path.join(CACHE, pmc + ".xml")
    if os.path.exists(fn) and os.path.getsize(fn) > 200:
        return
    for attempt in range(3):
        try:
            r = requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML", headers=UA, timeout=90)
            if r.status_code == 200:
                open(fn, "wb").write(r.content)
                return
            if r.status_code == 404:
                open(fn, "wb").write(b"<none/>" + b" " * 300)
                return
        except Exception:
            pass
        time.sleep(3)

def do_fetch():
    pool = json.load(open(POOL, encoding="utf-8"))
    todo = [k for k in pool if not (os.path.exists(os.path.join(CACHE, k + ".xml")) and os.path.getsize(os.path.join(CACHE, k + ".xml")) > 200)]
    print("to fetch", len(todo), flush=True)
    def w(k):
        fetch_one(k); time.sleep(0.4)
    with ThreadPoolExecutor(4) as ex:
        for i, _ in enumerate(ex.map(w, todo)):
            if i % 200 == 0: print(i, flush=True)
    print("fetched")

MODES = {"Eg1": (130, 160), "Eg2": (185, 210), "B1g1": (385, 410), "A1g": (503, 530), "Eg3": (625, 655)}
NUM = re.compile(r"(?<![\d.\-])(\d{3})(?:[.,]\d+)?(?![\d])")

def itertext_marked(el):
    """text of an element, bibliographic xrefs replaced by [REF]"""
    out = []
    def rec(e):
        if e.tag == "xref" and e.get("ref-type") == "bibr":
            out.append(" [REF] ");
            if e.tail: out.append(e.tail)
            return
        if e.text: out.append(e.text)
        for c in e:
            rec(c)
        if e.tail: out.append(e.tail)
    # do not include tail of root
    if el.text: out.append(el.text)
    for c in el: rec(c)
    return html.unescape(re.sub(r"\s+", " ", "".join(out)))

def sentences(t):
    return re.split(r"(?<=[a-z\)\]\d])\.\s+(?=[A-Z\[])", t)

def score_xml(path):
    try:
        tree = ET.parse(path)
    except Exception as e:
        return {"err": "parse"}
    root = tree.getroot()
    doi = None
    for a in root.iter("article-id"):
        if a.get("pub-id-type") == "doi": doi = a.text
    body = root.find(".//body")
    if body is None:
        return {"err": "nobody", "doi": doi}
    texts = []
    for p in body.iter("p"):
        texts.append(("p", itertext_marked(p)))
    nfigR = 0
    for c in body.iter("caption"):
        _t = itertext_marked(c); texts.append(("cap", _t))
        if "Raman" in _t: nfigR += 1
    tabs = []
    for tw in body.iter("table-wrap"):
        cap = tw.find("caption")
        ct = itertext_marked(cap) if cap is not None else ""
        tt = " ".join(itertext_marked(td) for td in tw.iter("td"))
        tabs.append((ct, tt))
    full = " ".join(t for _, t in texts)
    nra = len(re.findall(r"Raman", full)); nan = len(re.findall(r"anatase", full, re.I))
    modes_all, modes_meas = set(), set()
    nums_meas = []
    sym = 0; fwhm = 0
    nshift = 0; best_sent = ("", 0); nfigR = 0
    lasers = set()
    raman_sents = 0
    for kind, t in texts:
        if "Raman" not in t and "cm" not in t:
            continue
        for s in sentences(t):
            hasR = "Raman" in s
            hascm = bool(re.search(r"cm\s*[\u2212\-\u2013^−]?\s*[-−]?1|cm\u22121|cm-1|cm⁻¹", s)) or "cm" in s
            if not (hasR or (hascm and re.search(r"\bE\s?g\b|\bB\s?1g\b|\bA\s?1g\b|anatase", s))):
                continue
            raman_sents += 1
            if re.search(r"shift|broaden|asymmetr|blue|red.?shift|softening|hardening|confinement", s, re.I): nshift += 1
            _cnt = 0
            for _m in NUM.finditer(s):
                _v = int(_m.group(1))
                if any(lo <= _v <= hi for lo, hi in MODES.values()): _cnt += 1
            if "[REF]" in s: _cnt = _cnt * 0.3
            if _cnt > best_sent[1]: best_sent = (s[:320], _cnt)
            if re.search(r"\bE\s?g\b|\bB\s?1g\b|\bA\s?1g\b", s): sym += 1
            if re.search(r"FWHM|full width|linewidth|line width|half.width", s, re.I): fwhm += 1
            for m in re.finditer(r"(\d{3})(?:\.\d+)?\s*nm", s):
                v = int(m.group(1))
                if 244 <= v <= 1100 and re.search(r"laser|excit|Raman|He-?Ne|Ar|Nd|diode", s, re.I): lasers.add(v)
            for m in NUM.finditer(s):
                v = int(m.group(1))
                for k, (lo, hi) in MODES.items():
                    if lo <= v <= hi:
                        ctx = s[max(0, m.start() - 60): m.end() + 40]
                        if re.search(r"cm|Raman|mode|peak|band|shift", s):
                            modes_all.add(k)
                            if "[REF]" not in s and not re.search(r"reported|literature|previous|according to|typical|characteristic|ascrib|correspond.* to|assigned to the", s, re.I):
                                modes_meas.add(k); nums_meas.append(m.group(0))
    # raman tables
    rtab = 0; tab_modes = set()
    for ct, tt in tabs:
        if re.search(r"Raman|cm", ct) or re.search(r"Raman", tt):
            tm = set()
            for m in NUM.finditer(tt):
                v = int(m.group(1))
                for k, (lo, hi) in MODES.items():
                    if lo <= v <= hi: tm.add(k)
            if len(tm) >= 2 or re.search(r"Raman", ct):
                rtab += 1; tab_modes |= tm
    ack = ""
    low = full.lower()
    data = [w for w in ("zenodo", "figshare", "dryad", "mendeley data", "source data", "supplementary data", "data availability") if w in low]
    flags = {w: bool(re.search(w, low)) for w in ("temperature-dependent", "variable temperature", "in situ raman", "pressure", "single crystal", "epitaxial", "thin film", "nanotube", "doped", "doping", "phonon confinement", "grain size", "crystallite size", "rutile", "brookite", "oxygen vacanc", "18o", "uv raman", "325 nm", "photocatal", "sers", "anodi", "aerogel", "sol-gel", "hydrothermal", "ald", "sputter", "pld", "laser annealing", "mapping")}
    return {"doi": doi, "raman": nra, "anatase": nan, "ramsent": raman_sents, "modes_all": sorted(modes_all), "modes_meas": sorted(modes_meas),
            "nmeas": len(nums_meas), "sym": sym, "fwhm": fwhm, "lasers": sorted(lasers), "rtab": rtab, "tab_modes": sorted(tab_modes), "data": data,
            "flags": [k for k, v in flags.items() if v], "len": len(full), "nshift": nshift, "best_sent": best_sent[0], "best_cnt": best_sent[1], "nfigR": nfigR}

def do_score():
    pool = json.load(open(POOL, encoding="utf-8"))
    res = {}
    for k in pool:
        fn = os.path.join(CACHE, k + ".xml")
        if not os.path.exists(fn): continue
        res[k] = score_xml(fn)
    json.dump(res, open(SCORES, "w", encoding="utf-8"))
    print("scored", len(res))

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "fetch"
    if a == "fetch": do_fetch()
    else: do_score()
