"""Compact evidence sheet for staged PMC papers: metadata, laser sentences, calcite number sentences with PDF pages, SI names.
usage: python -P evid_A.py PMCID [PMCID ...]"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfg_A import STAGE
import dossier_A as D
from meta_A import meta, pages

def laser_sents(paras):
    out = []
    for p in paras:
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", p):
            if re.search(r"(?i)\b\d{3}(\.\d+)?\s*-?\s*nm\b", s) and re.search(r"(?i)laser|excit|raman", s) and not re.search(r"(?i)\bXRD|SEM\b|UV-vis|absorbance", s):
                out.append(s[:260])
    seen = []
    for s in out:
        if s not in seen: seen.append(s)
    return seen[:3]

def page_of(pgs, sent):
    nums = re.findall(r"\d{3,4}(?:\.\d+)?", sent)
    nums = [n.replace(".", ".") for n in nums][:6]
    hits = []
    for i, t in enumerate(pgs):
        tt = t.replace("−", "-")
        if nums and all(n in tt for n in nums): hits.append(i + 1)
    return hits

if __name__ == "__main__":
    for pm in sys.argv[1:]:
        d = os.path.join(STAGE, pm)
        try:
            m = meta(pm)
        except Exception as e:
            print("##", pm, "meta fail", e); continue
        paras = D.paras_of(os.path.join(d, "fulltext.xml"))
        pgs = pages(pm)
        si = sorted(os.listdir(os.path.join(d, "SI"))) if os.path.isdir(os.path.join(d, "SI")) else []
        print(f"## {pm} | {m['doi']} | {m['first_author']} | {m['years']} | {m['journal']} | si={si}")
        print("   T:", m["title"][:200])
        for s in laser_sents(paras): print("   L:", s)
        tags, sents, w = D.dossier(pm, maxs=4)
        print("   tags:", ",".join(tags))
        for ns, s in sents:
            print("   E[p%s]:" % page_of(pgs, s), s[:330])
