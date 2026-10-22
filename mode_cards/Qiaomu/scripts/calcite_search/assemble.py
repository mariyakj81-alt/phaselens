"""Assemble calcite/CALnn_<Surname><Year>/ folders from the staging dir and write calcite/papers.csv.
Usage: python -P assemble.py STAGE_DIR PROJECT_ROOT
Archives from third parties are only extracted (never executed); member paths are checked to stay inside the target dir."""
import sys, os, re, json, csv, shutil, zipfile, tarfile, subprocess, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
from manifest import E
import acquire

STAGE, ROOT = sys.argv[1], sys.argv[2]
CAL = os.path.join(ROOT, "calcite")
os.makedirs(CAL, exist_ok=True)

DATA_URLS = {
    "10.1098_rsos.200725": ["https://doi.org/10.5061/dryad.brv15dv7g", "https://zenodo.org/records/4135137"],
    "10.1098_rsos.220773": ["https://doi.org/10.5281/zenodo.5103052", "https://doi.org/10.6084/m9.figshare.c.6186123"],
    "10.1177_00037028251330654": ["https://doi.org/10.5281/zenodo.13387413"],
    "10.1002_jrs.70059": ["https://doi.org/10.5281/zenodo.17033032"],
    "10.1016_j.saa.2013.06.121": ["https://zenodo.org/records/14769788"],
}


def clean_title(t):
    t = html.unescape(re.sub(r"<[^>]+>", "", t or ""))
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace(" 2 ", "2 ") if "CO 2" in t else t
    return t


def safe_extract_zip(zpath, dest):
    os.makedirs(dest, exist_ok=True)
    base = os.path.realpath(dest)
    n = 0
    with zipfile.ZipFile(zpath) as z:
        for m in z.infolist():
            target = os.path.realpath(os.path.join(dest, m.filename))
            if not (target == base or target.startswith(base + os.sep)):
                print("  skip unsafe member", m.filename); continue
            if m.is_dir():
                os.makedirs(target, exist_ok=True); continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(m) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
            n += 1
    return n


def safe_extract_tar(tpath, dest):
    os.makedirs(dest, exist_ok=True)
    base = os.path.realpath(dest)
    n = 0
    with tarfile.open(tpath) as tf:
        for m in tf.getmembers():
            target = os.path.realpath(os.path.join(dest, m.name))
            if not (target.startswith(base + os.sep) or target == base) or not (m.isfile() or m.isdir()):
                continue
            if os.path.basename(m.name).startswith("._") or os.path.basename(m.name) == ".DS_Store":
                continue
            tf.extract(m, dest, filter="data"); n += 1
    return n


def extract_archives(folder):
    """Extract zip/rar/tgz found directly in folder into folder/unzipped/<archive-name>/."""
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name)
        if not os.path.isfile(p):
            continue
        low = name.lower()
        dest = os.path.join(folder, "unzipped", os.path.splitext(name)[0] if not low.endswith(".tgz") else name[:-4])
        try:
            if low.endswith(".zip"):
                print("  unzip", name, safe_extract_zip(p, dest))
            elif low.endswith((".tgz", ".tar.gz")):
                print("  untar", name, safe_extract_tar(p, dest))
            elif low.endswith(".rar"):
                os.makedirs(dest, exist_ok=True)
                r = subprocess.run(["bsdtar", "-xf", p, "-C", dest], capture_output=True, text=True, timeout=300)
                print("  rar", name, r.returncode, r.stderr[:100])
        except Exception as e:
            print("  extract fail", name, e)


def list_rel(folder, sub):
    d = os.path.join(folder, sub)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        out.append(os.path.relpath(os.path.join(d, name), ROOT).replace("\\", "/"))
    return out


rows = []
for i, e in enumerate(E, 1):
    pid = f"CAL{i:02d}"
    folder_name = f"{pid}_{e['surname']}{e['year']}"
    folder = os.path.join(CAL, folder_name)
    st = os.path.join(STAGE, e["slug"])
    res = json.load(open(os.path.join(st, "result.json"))) if os.path.exists(os.path.join(st, "result.json")) else {}
    print(pid, folder_name)
    os.makedirs(os.path.join(folder, "SI"), exist_ok=True)
    os.makedirs(os.path.join(folder, "data"), exist_ok=True)
    pdf_status = "needs_manual"
    if not e.get("nopdf"):
        shutil.copy2(os.path.join(st, "paper.pdf"), os.path.join(folder, "paper.pdf"))
        pdf_status = "downloaded"
    if os.path.exists(os.path.join(st, "fulltext.xml")):
        shutil.copy2(os.path.join(st, "fulltext.xml"), os.path.join(folder, "fulltext.xml"))
    # SI
    sidir = os.path.join(st, "SI")
    if os.path.isdir(sidir):
        for name in os.listdir(sidir):
            s = os.path.join(sidir, name)
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(folder, "SI", name))
        extract_archives(os.path.join(folder, "SI"))
    # data
    dd = os.path.join(st, "data")
    if os.path.isdir(dd):
        for name in os.listdir(dd):
            s = os.path.join(dd, name)
            t = os.path.join(folder, "data", name)
            if os.path.isdir(s):
                if os.path.exists(t):
                    shutil.rmtree(t)
                shutil.copytree(s, t)
            else:
                shutil.copy2(s, t)
        extract_archives(os.path.join(folder, "data")) if e["slug"] == "10.1002_jrs.70059" else None
    # data pulled from SI
    if e["slug"] == "10.1038_s41467-025-67899-8":
        shutil.copy2(os.path.join(folder, "SI", "41467_2025_67899_MOESM6_ESM.xlsx"), os.path.join(folder, "data", "SourceData_Raman_etc_MOESM6.xlsx"))
    if e["slug"] == "10.1038_s41467-025-67899-8":
        src = os.path.join(folder, "SI", "unzipped", "41467_2025_67899_MOESM3_ESM")
        dst = os.path.join(folder, "data", "SupplementaryData1_Raman_txt")
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    if e["slug"] == "10.1371_journal.pone.0312495":
        src = os.path.join(folder, "SI", "unzipped", "pone.0312495.s003", "submited_DRX_microRaman_csv")
        dst = os.path.join(folder, "data", "microRaman_XRD_csv")
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    # remove empty dirs
    for sub in ("SI", "data"):
        d = os.path.join(folder, sub)
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
    doi = res.get("doi", "") if e["slug"].startswith("10.") else ""
    if e["slug"].startswith("10.") and not doi:
        doi = e["slug"].replace("_", "/", 1)
    src_urls = []
    if doi:
        src_urls.append(f"https://doi.org/{doi}")
    pu = res.get("pdf_url")
    if pu:
        if pu.startswith("pmc-oa-opendata"):
            pm = pu.split()[-1]
            src_urls.append(f"https://pmc-oa-opendata.s3.amazonaws.com/{pm}.1/{pm}.1.pdf")
            src_urls.append(f"https://pmc.ncbi.nlm.nih.gov/articles/{pm}/")
        else:
            src_urls.append(pu)
    elif res.get("pmcid"):
        src_urls.append(f"https://pmc.ncbi.nlm.nih.gov/articles/{res['pmcid']}/")
    src_urls += DATA_URLS.get(e["slug"], [])
    # dedupe
    seen = set(); src_urls = [u for u in src_urls if not (u in seen or seen.add(u))]
    title = clean_title(res.get("title"))
    if e.get("title"):
        title = e["title"]
    if e["slug"] == "10.1002_jrs.70059":
        title = "Comparison of Red (785 nm) and Blue (457 nm) Excitation Lasers for Raman Analysis of Synthetic and Natural Calcium Carbonate Samples"
    notes = e["notes"]
    if "EXTRA" not in notes and i > 30:
        notes = "EXTRA. " + notes
    rows.append({
        "paper_id": pid, "folder": os.path.relpath(folder, ROOT).replace("\\", "/"), "doi": doi, "title": title,
        "first_author": e["first_author"], "year": e["year"], "journal": e["journal"], "open_access": e["oa"],
        "raman_evidence": e["evidence"], "laser_nm": e["laser"], "sample_description": e["sample"],
        "peak_table": e["peak_table"], "raw_data": e["raw"], "pdf_status": pdf_status,
        "si_files": ";".join(list_rel(folder, "SI")), "data_files": ";".join(list_rel(folder, "data")),
        "source_urls": ";".join(src_urls), "found_via": e["found_via"], "notes": notes})

cols = ["paper_id", "folder", "doi", "title", "first_author", "year", "journal", "open_access", "raman_evidence", "laser_nm", "sample_description",
        "peak_table", "raw_data", "pdf_status", "si_files", "data_files", "source_urls", "found_via", "notes"]
with open(os.path.join(CAL, "papers.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print("wrote", len(rows), "rows")
