"""Build one anatase paper folder from a PMC OA article.
Usage: python -P build_A.py PMCID ANAid [--nosi]     e.g. build_A.py PMC7198570 ANA034
Steps: claim DOI in anatase/_claims.txt (abort if agent B was first), PDF from the PMC OA S3 bucket, fulltext.xml and SI via
Europe PMC REST, SI cleanup (drop article figure images, unzip nested zips), mirror data-like SI files into data/.
Honest UA, >=10 s between requests to the same host. No challenge evasion."""
import os, sys, re, json, time, zipfile, io, shutil, unicodedata, requests
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "anatase")
CLAIMS = os.path.join(OUT, "_claims.txt")
UA = {"User-Agent": "Mozilla/5.0 (compatible; RamanLitResearch/0.1; academic use)"}
CACHE = r"C:\Users\yqm12\AppData\Local\Temp\claude\G--My-Drive-Qiaomu-Coding-LLM-Hackason\6904f568-fbff-48aa-b9f2-a1642df7e094\scratchpad\anaA\xml"
LAST = {}
def throttle(url, gap=10):
    host = url.split("/")[2]
    w = LAST.get(host, 0) + gap - time.time()
    if w > 0: time.sleep(w)
    LAST[host] = time.time()
def get(url, gap=10, timeout=120):
    throttle(url, gap)
    return requests.get(url, headers=UA, timeout=timeout)
def ascii_(s): return re.sub(r"[^A-Za-z0-9]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode())

def claim(doi):
    d = doi.lower()
    for line in open(CLAIMS, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2 and p[0].strip().lower() == d:
            return p[1] == "A"   # someone already claimed it; ok only if it is us
    with open(CLAIMS, "a", encoding="utf-8", newline="") as f:
        f.write(f"{doi}\tA\t{time.strftime('%H:%M:%S')}\n")
    for line in open(CLAIMS, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2 and p[0].strip().lower() == d:
            return p[1] == "A"   # first occurrence decides
    return True

def meta_from_xml(pmc):
    fn = os.path.join(CACHE, pmc + ".xml")
    if not os.path.exists(fn) or os.path.getsize(fn) < 500:
        r = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML", gap=2)
        open(fn, "wb").write(r.content)
    root = ET.parse(fn).getroot()
    doi = None
    for a in root.iter("article-id"):
        if a.get("pub-id-type") == "doi": doi = a.text
    t = root.find(".//article-title")
    title = re.sub(r"\s+", " ", "".join(t.itertext())).strip() if t is not None else ""
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
    lic = None
    for l in root.iter("license"):
        lic = l.get("{http://www.w3.org/1999/xlink}href") or "".join(l.itertext())[:100]
    return {"doi": doi, "title": title, "surname": au[0], "given": au[1], "years": sorted(set(years)), "journal": journal, "license": lic}

IMG = re.compile(r"\.(?:gif|jpg|jpeg|png|tif|tiff|bmp|webp)$", re.I)
DATAEXT = {".xlsx", ".xls", ".csv", ".txt", ".dat", ".tsv", ".json", ".spc", ".jdx", ".opju", ".opj", ".jnb", ".xlsm", ".ods", ".docx", ".doc"}
DATAEXT_STRICT = {".xlsx", ".xls", ".csv", ".txt", ".dat", ".tsv", ".json", ".spc", ".jdx", ".opju", ".opj", ".jnb", ".xlsm", ".ods"}

def unzip_safe(zbytes_or_path, dest):
    os.makedirs(dest, exist_ok=True); out = []
    z = zipfile.ZipFile(zbytes_or_path)
    for n in z.namelist():
        p = os.path.realpath(os.path.join(dest, n))
        if not p.startswith(os.path.realpath(dest) + os.sep): continue
        if n.endswith("/"): os.makedirs(p, exist_ok=True); continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(z.read(n)); out.append(p)
    return out

def build(pmc, anaid, nosi=False, surname_override=None):
    m = meta_from_xml(pmc)
    if not m["doi"]: print("no doi"); return None
    if not claim(m["doi"]):
        print("CLAIMED BY B:", m["doi"]); return None
    year = min(m["years"]) if m["years"] else "XXXX"
    sn = ascii_(surname_override or m["surname"])
    folder = f"{anaid}_{sn}{year}"
    d = os.path.join(OUT, folder)
    os.makedirs(d, exist_ok=True)
    rec = {"pmc": pmc, "folder": folder, "meta": m}
    # PDF
    pdf = None
    for v in (1, 2, 3):
        u = f"https://pmc-oa-opendata.s3.amazonaws.com/{pmc}.{v}/{pmc}.{v}.pdf"
        r = get(u, gap=10)
        if r.status_code == 200 and r.content[:4] == b"%PDF":
            open(os.path.join(d, "paper.pdf"), "wb").write(r.content); pdf = u; break
    rec["pdf_url"] = pdf
    if pdf is None:
        print("PDF NOT AVAILABLE for", pmc); return rec
    shutil.copyfile(os.path.join(CACHE, pmc + ".xml"), os.path.join(d, "fulltext.xml"))
    si_files = []; data_files = []
    if not nosi:
        s = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles", gap=10)
        rec["suppl_status"] = s.status_code
        if s.status_code == 200 and s.content[:2] == b"PK":
            sid = os.path.join(d, "SI"); os.makedirs(sid, exist_ok=True)
            tmp = os.path.join(d, "_tmp_si");
            names = unzip_safe(io.BytesIO(s.content), tmp)
            keep = [p for p in names if not IMG.search(p)]
            for p in keep:
                rel = os.path.relpath(p, tmp)
                tgt = os.path.join(sid, rel)
                os.makedirs(os.path.dirname(tgt), exist_ok=True)
                shutil.move(p, tgt)
            shutil.rmtree(tmp, ignore_errors=True)
            # nested zips -> SI/unzipped/<name>
            for root_, _, files in list(os.walk(sid)):
                for f in files:
                    if f.lower().endswith(".zip"):
                        p = os.path.join(root_, f)
                        try: unzip_safe(p, os.path.join(sid, "unzipped", os.path.splitext(f)[0]))
                        except Exception as e: rec.setdefault("zip_err", []).append(str(e))
            for root_, _, files in os.walk(sid):
                for f in files:
                    p = os.path.join(root_, f)
                    si_files.append(os.path.relpath(p, d).replace("\\", "/"))
            if not si_files:
                shutil.rmtree(sid, ignore_errors=True)
    rec["si_files"] = si_files
    json.dump(rec, open(os.path.join(HERE, f"built_{anaid}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(anaid, folder, "| PDF", pdf, "| SI files", len(si_files))
    for f in si_files[:30]: print("   ", f)
    return rec

if __name__ == "__main__":
    pmc, anaid = sys.argv[1], sys.argv[2]
    build(pmc, anaid, nosi="--nosi" in sys.argv)
