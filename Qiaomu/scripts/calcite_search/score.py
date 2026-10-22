"""Score how much calcite Raman peak data a paper PDF contains. Usage: python -P score.py pdf [pdf ...]  (run with -P; reads untrusted PDFs via fitz only)"""
import sys, re, fitz
RANGES = {"155": (145, 170), "282": (272, 295), "712": (703, 722), "1086": (1078, 1094), "1436": (1426, 1446), "1749": (1738, 1760)}
NUM = re.compile(r"(?<![\d.])(\d{3,4})(?:\.\d+)?(?![\d])")
def score(path):
    d = fitz.open(path)
    text = "\n".join(p.get_text() for p in d)
    low = text.lower()
    out = {"pages": d.page_count, "raman": low.count("raman"), "calcite": low.count("calcite"), "aragonite": low.count("aragonite"), "vaterite": low.count("vaterite")}
    found = {}
    for m in re.finditer(r"calcite|CaCO|carbonate|Raman", text):
        pass
    # numbers in windows around 'cm-1' / 'cm−1' / 'cm 1' units or inside text with Raman
    for mm in NUM.finditer(text):
        v = int(mm.group(1))
        ctx = text[max(0, mm.start()-200): mm.end()+200].lower()
        if "calcite" not in ctx and "caco" not in ctx and "carbonate" not in ctx and "mg-cal" not in ctx: continue
        for k, (lo, hi) in RANGES.items():
            if lo <= v <= hi and ("cm" in ctx or "shift" in ctx or "raman" in ctx or "peak" in ctx or "band" in ctx):
                found.setdefault(k, set()).add(v)
    out["modes"] = {k: sorted(v) for k, v in found.items()}
    out["n_modes"] = len(found)
    m = re.search(r"(\d{3})\s?nm", text)
    lasers = sorted({int(x) for x in re.findall(r"(?<!\d)(244|248|266|325|355|457|473|488|514|532|633|638|660|671|780|785|830|1064)\s?nm", text)})
    out["lasers"] = lasers
    return out
if __name__ == "__main__":
    for p in sys.argv[1:]:
        try:
            o = score(p)
            print(p.split("stage")[-1][:50], "|", o["pages"], "p raman", o["raman"], "cal", o["calcite"], "arag", o["aragonite"], "vat", o["vaterite"], "| n_modes", o["n_modes"], o["modes"], "| lasers", o["lasers"])
        except Exception as e:
            print(p, "ERR", e)
