"""Materialise the accepted papers of agent B: folders anatase/ANAnnn_<Surname><Year>/ with paper.pdf, SI/, data/; writes anatase/papers_new_B.csv.
Usage: python -P build_B.py [--dry]
Specs come from specs_B.py (list SPECS, in acceptance order = ID order, first ID = START).
Verification per paper: %PDF magic, PyMuPDF opens, title words on page 1, anatase-mode numbers present in the text (or SI)."""
import sys, os, re, json, shutil, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fitz, pandas as pd
from common import ROOT, STAGE, fetch
from specs_B import SPECS, START
import specs_B_more  # noqa: appends more specs to SPECS
fitz.TOOLS.mupdf_display_errors(False)
COLS = ["paper_id", "folder", "doi", "title", "first_author", "year", "journal", "open_access", "raman_evidence", "laser_nm", "sample_description",
        "peak_table", "raw_data", "pdf_status", "si_files", "data_files", "source_urls", "found_via", "notes"]
RANGES = {"Eg1": (138, 160), "Eg2": (190, 210), "B1g1": (388, 412), "A1g/B1g2": (505, 530), "Eg3": (625, 655)}
dry = "--dry" in sys.argv


def norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("−", "-"))


def verify(pdf, title):
    raw = open(pdf, "rb").read(5)
    if raw[:4] != b"%PDF":
        return False, "no %PDF magic"
    d = fitz.open(pdf)
    if d.page_count < 1:
        return False, "no pages"
    p1 = norm(" ".join(d[i].get_text() for i in range(min(3, d.page_count))))  # cover pages of repository copies are allowed
    tw = [w for w in norm(title).split() if len(w) > 3]
    hit = sum(1 for w in tw if w in p1)
    flat = re.sub(r"\s+", " ", " ".join(p.get_text() for p in d).replace("−", "-"))
    modes = set()
    for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])", flat):
        v = int(m.group(1))
        for k, (lo, hi) in RANGES.items():
            if lo <= v <= hi and re.search(r"cm|Raman|mode|peak|shift", flat[max(0, m.start() - 120):m.end() + 120]):
                modes.add(k)
    ok = hit >= max(2, int(0.5 * len(tw))) and len(modes) >= 2
    return ok, f"title {hit}/{len(tw)} modes {sorted(modes)} pages {d.page_count}"


def resolve(text, pdf):
    """replace {p:REGEX} by the 1-based PDF page where REGEX first occurs"""
    if "{p:" not in text:
        return text
    d = fitz.open(pdf)
    pages = [re.sub(r"\s+", " ", pg.get_text().replace("−", "-")) for pg in d]

    def rep(m):
        rx = m.group(1)
        for i, t in enumerate(pages):
            if re.search(rx, t):
                return str(i + 1)
        print("   WARN page not found for", rx[:40])
        return "?"
    return re.sub(r"\{p:(.*?)\}(?=[^}]|$)", rep, text)


# CLEAN: remove previous output folders of agent B (ANA068..ANA100 only) so that a rebuild is deterministic
if not dry:
    adir = os.path.join(ROOT, "anatase")
    for dn in os.listdir(adir):
        m = re.match(r"ANA(\d{3})_", dn)
        if m and START <= int(m.group(1)) <= 100 and os.path.isdir(os.path.join(adir, dn)):
            shutil.rmtree(os.path.join(adir, dn))

rows = []
for i, s in enumerate(SPECS):
    pid = "ANA%03d" % (START + i)
    sur = re.sub(r"[^A-Za-z]", "", s["surname"])
    folder = f"anatase/{pid}_{sur}{s['year']}"
    absf = os.path.join(ROOT, folder)
    src = s["pdf"] if os.path.isabs(s["pdf"]) else os.path.join(STAGE, s["pdf"])
    ok = True; msg = "needs_manual"
    if s.get("pdf_status") != "needs_manual":
        for fld in ("raman_evidence", "notes", "sample_description"):
            s[fld] = resolve(s[fld], src)
        ok, msg = verify(src, s["title"])
        print(pid, s["doi"], "VERIFY", ok, msg, flush=True)
        if not ok:
            print("   !!! failed verification; fix or drop", pid); continue
    if not dry:
        os.makedirs(absf, exist_ok=True)
        if s.get("pdf_status") != "needs_manual":
            shutil.copyfile(src, os.path.join(absf, "paper.pdf"))
    si_files, data_files = [], []
    for sub, lst, out in (("SI", s.get("si", []), si_files), ("data", s.get("data", []), data_files)):
        for item in lst:  # item = (source path under STAGE or abs, dest filename [, unzip])
            srcp, dest = item[0], item[1]
            srcp = srcp if os.path.isabs(srcp) else os.path.join(STAGE, srcp)
            dst = os.path.join(absf, sub, dest)
            if not dry:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(srcp, dst)
                if len(item) > 2 and item[2] == "unzip":
                    ud = os.path.join(absf, sub, "unzipped")
                    os.makedirs(ud, exist_ok=True)
                    try:
                        with zipfile.ZipFile(dst) as z:
                            z.extractall(ud)
                    except Exception as e:
                        print("   unzip failed", dest, e)
                    for r, _, fs in os.walk(ud):
                        for f in fs:
                            out.append(os.path.relpath(os.path.join(r, f), ROOT).replace("\\", "/"))
            out.append(f"{folder}/{sub}/{dest}")
    rows.append(dict(paper_id=pid, folder=folder, doi=s["doi"], title=s["title"], first_author=s["first_author"], year=str(s["year"]), journal=s["journal"],
                     open_access=s["open_access"], raman_evidence=s["raman_evidence"], laser_nm=s["laser_nm"], sample_description=s["sample_description"],
                     peak_table=s["peak_table"], raw_data=s.get("raw_data", "N"), pdf_status=s.get("pdf_status", "downloaded"),
                     si_files=";".join(si_files), data_files=";".join(data_files), source_urls=s["source_urls"], found_via=s["found_via"], notes=s["notes"]))
if not dry:
    df = pd.DataFrame(rows, columns=COLS)
    df.to_csv(os.path.join(ROOT, "anatase", "papers_new_B.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    print("wrote", len(rows), "rows")
