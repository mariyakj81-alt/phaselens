"""Dossier for authoring papers.csv rows: python -P dossier.py STAGE slug [slug...]"""
import sys, os, re, json, fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evidence import snippets
S = sys.argv[1]
for slug in sys.argv[2:]:
    d = os.path.join(S, slug); p = os.path.join(d, "paper.pdf")
    r = json.load(open(os.path.join(d, "result.json"))) if os.path.exists(os.path.join(d, "result.json")) else {}
    doc = fitz.open(p); pages = [re.sub(r"\s+", " ", x.get_text()) for x in doc]; t = " ".join(pages)
    print("=" * 100); print(slug, "|", r.get("title"), "|", r.get("authors"), r.get("year"), "|", r.get("venue"))
    las = {}
    for m in re.finditer(r"(?<![\d.])(244|248|266|325|355|457|473|488(?:\.0)?|514(?:\.5)?|532|568|632\.8|633|647|660|671|780|785|830|1064)\s?nm", t):
        ctx = t[max(0, m.start()-120): m.end()+120].lower()
        if any(w in ctx for w in ("laser", "excit", "raman", "line")): las[m.group(1)] = las.get(m.group(1), 0) + 1
    print("LASERS:", las)
    print("title check first page:", pages[0][:150])
    for mm, pg, s in snippets(p, 2, 200): print(f"  [p{pg} modes={mm}] ...{s}...")
