"""Print Raman sentences (with anatase-range numbers) of cached PMC xml for manual screening. Usage: python -P show.py PMC... [--max N]"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_all as S
import xml.etree.ElementTree as ET
pool = json.load(open(S.POOL, encoding="utf-8"))
sc = json.load(open(S.SCORES, encoding="utf-8")) if os.path.exists(S.SCORES) else {}
def show(pmc, maxs=7, width=420):
    fn = os.path.join(S.CACHE, pmc + ".xml")
    p = pool.get(pmc, {})
    s = sc.get(pmc, {})
    print("=" * 100)
    print(pmc, p.get("year"), s.get("doi"), "|", (p.get("journal") or "")[:30], "|", re.sub(r"<[^>]+>", "", (p.get("title") or ""))[:110])
    print("  R", s.get("raman"), "A", s.get("anatase"), "modes_meas", s.get("modes_meas"), "sym", s.get("sym"), "fwhm", s.get("fwhm"), "tab", s.get("rtab"), "lasers", s.get("lasers"), "suppl", p.get("hasSuppl"), "data", s.get("data"))
    print("  flags", s.get("flags"))
    root = ET.parse(fn).getroot()
    body = root.find(".//body")
    n = 0
    for el in list(body.iter("p")) + list(body.iter("caption")):
        t = S.itertext_marked(el)
        if "Raman" not in t: continue
        for sent in S.sentences(t):
            ok = False
            for m in S.NUM.finditer(sent):
                v = int(m.group(1))
                if any(lo <= v <= hi for lo, hi in S.MODES.values()): ok = True
            if ok and re.search(r"cm|Raman|peak|mode|band", sent):
                print("   -", sent[:width]); n += 1
                if n >= maxs: return
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mx = 7
    if "--max" in sys.argv: mx = int(sys.argv[sys.argv.index("--max") + 1]); args = [a for a in args if a != str(mx)]
    for a in args: show(a, mx)
