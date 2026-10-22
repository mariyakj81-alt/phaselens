"""Stage a PMC Open Access article: PDF (+xml) from the NIH PMC OA AWS bucket, SI from the Europe PMC REST API.
Usage: python -P fetch_pmc.py STAGE_ROOT PMCID [PMCID ...]
Writes STAGE_ROOT/<PMCID>/{paper.pdf, fulltext.xml, SI/..., result.json}. Never bypasses challenges."""
import sys, os, re, json, io, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_A import get
import fitz

S3 = "https://pmc-oa-opendata.s3.amazonaws.com/"
EREST = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
IMG = re.compile(r"\.(jpg|jpeg|gif|png|tif|tiff|svg)$", re.I)

def s3_package(pmcid, d):
    got = {"pdf": False, "xml": False, "s3_other": []}
    r = get(S3 + f"?prefix={pmcid}.&max-keys=300", min_gap=1)
    keys = re.findall(r"<Key>(.*?)</Key>", r.text) if r.status_code == 200 else []
    got["keys"] = keys
    for k in keys:
        name = k.split("/")[-1]
        if name.endswith(".1.pdf") and name.startswith("PMC"):
            r2 = get(S3 + k, min_gap=1, timeout=180)
            if r2.status_code == 200 and r2.content[:5] == b"%PDF-":
                open(os.path.join(d, "paper.pdf"), "wb").write(r2.content); got["pdf"] = True
        elif name.endswith(".1.xml") and name.startswith("PMC"):
            r2 = get(S3 + k, min_gap=1, timeout=120)
            if r2.status_code == 200:
                open(os.path.join(d, "fulltext.xml"), "wb").write(r2.content); got["xml"] = True
        elif name.endswith((".json", ".txt")):
            continue
        else:
            got["s3_other"].append(name)
    return got

def epmc_si(pmcid, d):
    """Supplementary files zip from Europe PMC REST (contains figure images + real SI)."""
    r = get(EREST + f"{pmcid}/supplementaryFiles", min_gap=1, timeout=300)
    names = []
    if r.status_code == 200 and r.content[:2] == b"PK":
        os.makedirs(os.path.join(d, "SI"), exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for n in z.namelist():
            if n.endswith("/"): continue
            base = os.path.basename(n)
            data = z.read(n)
            if IMG.search(base) and "moesm" not in base.lower() and not re.search(r"(?i)supp|_s\d|\bs\d", base):
                continue
            open(os.path.join(d, "SI", base), "wb").write(data); names.append(base)
    return r.status_code, names

def run(stage, pmcid):
    d = os.path.join(stage, pmcid); os.makedirs(d, exist_ok=True)
    g = s3_package(pmcid, d)
    if not g["xml"]:
        r = get(EREST + f"{pmcid}/fullTextXML", min_gap=1)
        if r.status_code == 200 and b"<article" in r.content[:3000]:
            open(os.path.join(d, "fulltext.xml"), "wb").write(r.content); g["xml"] = True
    sc, names = epmc_si(pmcid, d)
    res = {"pmcid": pmcid, "pdf": g["pdf"], "xml": g["xml"], "si_status": sc, "si": names, "s3_keys": g.get("keys")}
    json.dump(res, open(os.path.join(d, "result.json"), "w"), indent=1)
    return res

if __name__ == "__main__":
    stage = sys.argv[1]
    for pm in sys.argv[2:]:
        try:
            r = run(stage, pm)
            print(pm, "pdf", r["pdf"], "xml", r["xml"], "si", r["si_status"], r["si"], flush=True)
        except Exception as e:
            print(pm, "ERR", repr(e), flush=True)
