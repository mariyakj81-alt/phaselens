import os, re, sys, glob, zipfile, fitz
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
NUM = re.compile(r"(?<![\d.\-])(\d{3})(?:[.,]\d+)?(?![\d])")
RANGES = [(130, 160), (185, 210), (380, 412), (503, 530), (625, 655)]
def text_of(p):
    if p.lower().endswith(".pdf"):
        try: return " ".join(pg.get_text() for pg in fitz.open(p))
        except Exception as e: return ""
    if p.lower().endswith(".docx"):
        try:
            x = zipfile.ZipFile(p).read("word/document.xml").decode("utf8", "ignore")
            return re.sub(r"<[^>]+>", " ", x)
        except Exception: return ""
    return ""
for f in sorted(glob.glob(os.path.join(ROOT, "anatase", sys.argv[1] + "*"))):
    sid = os.path.join(f, "SI")
    if not os.path.isdir(sid): continue
    for r_, _, fs in os.walk(sid):
        for x in fs:
            p = os.path.join(r_, x)
            t = re.sub(r"\s+", " ", text_of(p).replace("−", "-"))
            nR = len(re.findall("Raman", t)); 
            hits = 0
            for s in re.split(r"(?<=[a-z\)\]\d])\.\s+", t):
                if "Raman" in s or "cm-1" in s:
                    hits += sum(1 for m in NUM.finditer(s) if any(lo <= int(m.group(1)) <= hi for lo, hi in RANGES))
            if nR: print(os.path.basename(f), os.path.relpath(p, f).replace("\\", "/"), "Raman", nR, "range-numbers", hits)
