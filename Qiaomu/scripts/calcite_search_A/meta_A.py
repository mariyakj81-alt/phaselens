"""Metadata + evidence locator for a staged PMC paper.
usage: python -P meta_A.py PMCID [regex-for-evidence ...]
Reads fulltext.xml and paper.pdf from the staging dir (cfg_A.STAGE/PMCID)."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfg_A import STAGE
import xml.etree.ElementTree as ET
import fitz

def meta(pm):
    root = ET.parse(os.path.join(STAGE, pm, "fulltext.xml")).getroot()
    m = {}
    art = root.find(".//article-meta")
    jm = root.find(".//journal-meta")
    m["title"] = re.sub(r"\s+", " ", "".join(art.find(".//article-title").itertext())).strip()
    m["journal"] = re.sub(r"\s+", " ", "".join(jm.find(".//journal-title").itertext())).strip() if jm.find(".//journal-title") is not None else ""
    doi = ""
    for a in art.findall("article-id"):
        if a.get("pub-id-type") == "doi": doi = a.text
    m["doi"] = (doi or "").lower()
    au = []
    for c in art.findall(".//contrib-group/contrib"):
        if c.get("contrib-type") == "author":
            sn = c.find(".//surname"); gn = c.find(".//given-names")
            au.append(((gn.text if gn is not None else ""), (sn.text if sn is not None else "")))
    m["authors"] = au
    m["first_author"] = (au[0][0] + " " + au[0][1]).strip() if au else ""
    yrs = [(pd.get("pub-type") or pd.get("date-type"), pd.findtext("year")) for pd in art.findall("pub-date")]
    m["years"] = yrs
    lic = art.find(".//license")
    m["license"] = lic.get("{http://www.w3.org/1999/xlink}href") if lic is not None else ""
    return m

def pages(pm):
    d = fitz.open(os.path.join(STAGE, pm, "paper.pdf"))
    return [p.get_text() for p in d]

def locate(pm, patterns):
    pg = pages(pm)
    out = []
    for pat in patterns:
        hit = [i + 1 for i, t in enumerate(pg) if re.search(pat, t, re.S)]
        out.append((pat, hit))
    return out

if __name__ == "__main__":
    pm = sys.argv[1]
    m = meta(pm)
    print(json.dumps(m, indent=1, ensure_ascii=False)[:1500])
    if len(sys.argv) > 2:
        for pat, hit in locate(pm, sys.argv[2:]): print("pages", hit, "<-", pat)
