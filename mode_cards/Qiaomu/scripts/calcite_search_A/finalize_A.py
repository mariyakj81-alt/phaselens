"""Build calcite/CALnnn_* folders from staged PMC packages and write calcite/papers_new_A.csv.
usage (from project root): python -P scripts/calcite_search_A/finalize_A.py FIRST_ID
Order: year, then first-author surname. Skips existing folders unless they are empty."""
import sys, os, re, json, csv, shutil, time, zipfile, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfg_A import STAGE
from common_A import get
from meta_A import meta
from rows_A import SPEC
from verify_A import verify_pdf

ROOT = os.getcwd()
FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 34
recs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "records.json")))
bypm = {r["pmcid"]: r for r in recs.values() if r["pmcid"]}
COLS = ["paper_id", "folder", "doi", "title", "first_author", "year", "journal", "open_access", "raman_evidence", "laser_nm",
        "sample_description", "peak_table", "raw_data", "pdf_status", "si_files", "data_files", "source_urls", "found_via", "notes"]
IMGEXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".mp4", ".mov", ".avi")
JOURNAL_FIX = {"Geochemistry, Geophysics, Geosystems : G(3)": "Geochemistry, Geophysics, Geosystems",
               "Environmental Science and Pollution Research International": "Environmental Science and Pollution Research",
               "ACS Earth & Space Chemistry": "ACS Earth and Space Chemistry"}

def ascii_fold(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9]", "", s)

def retry(fn, *a, n=5):
    for i in range(n):
        try:
            return fn(*a)
        except OSError as e:
            if i == n - 1: raise
            time.sleep(2)

def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    retry(shutil.copyfile, src, dst)

def surname_of(m):
    return ascii_fold(m["authors"][0][1]) if m["authors"] else "Unknown"

items = []
for pm, sp in SPEC.items():
    m = meta(pm)
    r = bypm[pm]
    items.append((int(r["year"]), surname_of(m), pm, m, sp))
items.sort(key=lambda x: (x[0], x[1].lower(), x[2]))
rows = []
for i, (yr, sn, pm, m, sp) in enumerate(items):
    cid = "CAL%03d" % (FIRST + i)
    folder = f"calcite/{cid}_{sn}{yr}"
    F = os.path.join(ROOT, folder)
    S = os.path.join(STAGE, pm)
    v = verify_pdf(os.path.join(S, "paper.pdf"), m["title"]) if pm != "PMC13555149" else {"ok": False}
    if not v["ok"]:
        print("VERIFY FAIL", pm, v); continue
    os.makedirs(F, exist_ok=True)
    copy(os.path.join(S, "paper.pdf"), os.path.join(F, "paper.pdf"))
    copy(os.path.join(S, "fulltext.xml"), os.path.join(F, "fulltext.xml"))
    si_files = []; unz = False
    sd = os.path.join(S, "SI")
    if os.path.isdir(sd):
        for name in sorted(os.listdir(sd)):
            low = name.lower()
            if low.endswith(IMGEXT) or "movies" in low: continue
            if low.endswith((".xlsx", ".xls")) and sp["raw_data"] == "Y" and ("MOESM3" in name and pm == "PMC12775475"):
                pass  # keep in SI as well as in data/
            copy(os.path.join(sd, name), os.path.join(F, "SI", name))
            si_files.append(f"{folder}/SI/{name}")
            if low.endswith(".zip"):
                zdir = os.path.join(F, "SI", "unzipped", os.path.splitext(name)[0])
                os.makedirs(zdir, exist_ok=True)
                with zipfile.ZipFile(os.path.join(sd, name)) as z:
                    for zi in z.infolist():
                        if zi.is_dir(): continue
                        base = os.path.basename(zi.filename)
                        if not base: continue
                        retry(lambda: open(os.path.join(zdir, base), "wb").write(z.read(zi)))
                unz = True
    if unz: si_files.append(f"{folder}/SI/unzipped")
    data_files = []
    for d in sp["data"]:
        if d == "MENDELEY":
            j = get("https://data.mendeley.com/public-api/datasets/ydrbh8b33f", min_gap=1).json()
            for f in j["files"]:
                if f["filename"].lower().endswith(".csv") and not f["filename"].lower().endswith(("_eds.csv", "_qox.csv")):
                    rr = get(f["content_details"]["download_url"], min_gap=2, timeout=120)
                    if rr.status_code == 200 and rr.content[:1].isdigit():
                        dst = os.path.join(F, "data", f["filename"])
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        retry(lambda: open(dst, "wb").write(rr.content))
                        data_files.append(f"{folder}/data/{f['filename']}")
        else:
            src_rel, dest = d
            copy(os.path.join(S, src_rel), os.path.join(F, "data", dest))
            data_files.append(f"{folder}/data/{dest}")
    doi = m["doi"]
    urls = [f"https://doi.org/{doi}", f"https://pmc-oa-opendata.s3.amazonaws.com/{pm}.1/{pm}.1.pdf", f"https://pmc.ncbi.nlm.nih.gov/articles/{pm}/"] + sp["extra_urls"]
    rows.append({"paper_id": cid, "folder": folder, "doi": doi, "title": m["title"], "first_author": m["first_author"], "year": str(yr),
                 "journal": JOURNAL_FIX.get(m["journal"], m["journal"]), "open_access": "Y", "raman_evidence": sp["evidence"], "laser_nm": sp["laser"],
                 "sample_description": sp["sample"], "peak_table": sp["peak_table"], "raw_data": sp["raw_data"], "pdf_status": "downloaded",
                 "si_files": ";".join(si_files), "data_files": ";".join(data_files), "source_urls": ";".join(urls), "found_via": "EuropePMC", "notes": sp["notes"]})
    print(cid, pm, folder, "SI", len(si_files), "data", len(data_files), flush=True)

with open(os.path.join(ROOT, "calcite", "papers_new_A.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\r\n")
    w.writeheader()
    for r in rows: w.writerow(r)
print("rows", len(rows))
