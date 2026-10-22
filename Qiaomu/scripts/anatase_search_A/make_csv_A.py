"""Build anatase/papers_new_A.csv from folders ANA034..ANA067 + specs_A.py + fulltext.xml. Run with python -P from anything."""
import os, re, sys, csv, glob, json, unicodedata
import xml.etree.ElementTree as ET
import fitz
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from specs_A import S
OUT = os.path.join(ROOT, "anatase")
COLS = next(csv.reader(open(os.path.join(OUT, "papers.csv"), encoding="utf-8-sig", newline="")))

def norm(t):
    t = unicodedata.normalize("NFKC", t).replace("−", "-").replace("–", "-").replace("­", "").replace("‐", "-").replace("‑", "-")
    return re.sub(r"\s+", " ", t).lower()

def locate(pdf, phrase):
    d = fitz.open(pdf)
    ph = norm(phrase)
    for cand in (ph, ph[:40], ph[:25]):
        for i, pg in enumerate(d):
            if cand in norm(pg.get_text()):
                return i + 1
    return None

def meta(folder):
    root = ET.parse(os.path.join(folder, "fulltext.xml")).getroot()
    doi = [a.text for a in root.iter("article-id") if a.get("pub-id-type") == "doi"][0]
    pmc = [a.text for a in root.iter("article-id") if a.get("pub-id-type") in ("pmc", "pmcid")]
    t = root.find(".//article-title")
    title = re.sub(r"\s+", " ", "".join(t.itertext())).strip()
    au = ("", "")
    for c in root.iter("contrib"):
        if c.get("contrib-type") in (None, "author"):
            sn = c.find(".//surname"); gn = c.find(".//given-names")
            if sn is not None and sn.text:
                au = (sn.text, gn.text if gn is not None else ""); break
    years = []
    for pd in root.iter("pub-date"):
        y = pd.find("year")
        if y is not None and y.text and y.text.isdigit(): years.append(int(y.text))
    j = root.find(".//journal-title")
    journal = "".join(j.itertext()).strip() if j is not None else ""
    return dict(doi=doi, title=title, author=re.sub(r"\s+", " ", f"{au[0]}, {au[1]}").strip(", "), year=str(min(years)), journal=journal, pmc=pmc)

def main():
    rows = []
    for i in range(34, 68):
        aid = f"ANA{i:03d}"
        fl = glob.glob(os.path.join(OUT, aid + "_*"))
        assert len(fl) == 1, aid
        folder = fl[0]; fname = os.path.basename(folder)
        m = meta(folder); sp = S[aid]
        pdf = os.path.join(folder, "paper.pdf")
        pg = locate(pdf, sp["loc"])
        ev = sp["ev"].replace("@p", f"p.{pg}" if pg else "")
        ev = ev.replace("text : ", "text: ").replace("  ", " ")
        if not pg: print("PAGE NOT FOUND", aid, sp["loc"])
        # SI + data files
        si = []; data = []
        sd = os.path.join(folder, "SI")
        if os.path.isdir(sd):
            for r_, _, fs in os.walk(sd):
                for f in sorted(fs):
                    rel = os.path.relpath(os.path.join(r_, f), ROOT).replace("\\", "/")
                    if f.lower().endswith(".zip"): continue
                    si.append(rel)
        dd = os.path.join(folder, "data")
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                data.append(os.path.relpath(os.path.join(dd, f), ROOT).replace("\\", "/"))
        if "_He2025" in fname:
            data.append([x for x in si if x.endswith("MOESM5_ESM.xlsx")][0])
        pmcid = None
        for f in glob.glob(os.path.join(HERE, "*.json")): pass
        # source url: PDF from the PMC OA bucket (PMCID from the build log in fulltext.xml ids)
        px = [a.text for a in ET.parse(os.path.join(folder, "fulltext.xml")).getroot().iter("article-id") if a.get("pub-id-type") in ("pmcid", "pmc")]
        pmcid = px[0] if px else None
        if pmcid and not pmcid.startswith("PMC"): pmcid = "PMC" + pmcid
        urls = []
        if pmcid: urls.append(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.pdf")
        urls.append(f"https://doi.org/{m['doi']}")
        row = {
            "paper_id": aid, "folder": f"anatase/{fname}", "doi": m["doi"], "title": m["title"], "first_author": m["author"], "year": m["year"],
            "journal": m["journal"], "open_access": "Y", "raman_evidence": ev, "laser_nm": sp["laser"], "sample_description": sp["sample"],
            "peak_table": sp["table"], "raw_data": sp["raw"], "pdf_status": "downloaded", "si_files": ";".join(si), "data_files": ";".join(data),
            "source_urls": "; ".join(urls), "found_via": "EuropePMC", "notes": sp["notes"],
        }
        rows.append(row)
    outp = os.path.join(OUT, "papers_new_A.csv")
    with open(outp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\r\n")
        w.writeheader(); w.writerows(rows)
    print("wrote", outp, len(rows))

if __name__ == "__main__":
    main()
