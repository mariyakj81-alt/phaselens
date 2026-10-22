"""Download each candidate arXiv PDF, score for anatase Raman evidence, keep only good ones (STAGE/arxiv_keep/<id>.pdf). Resumable: arxiv_scores.jsonl"""
import sys, os, re, json, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE, STAGE
import fitz
fitz.TOOLS.mupdf_display_errors(False)
OUT = os.path.join(STAGE, "arxiv_keep"); os.makedirs(OUT, exist_ok=True)
SC = os.path.join(HERE, "arxiv_scores.jsonl")
done = set()
if os.path.exists(SC):
    for ln in open(SC, encoding="utf-8"):
        try: done.add(json.loads(ln)["id"])
        except Exception: pass
ids = json.load(open(os.path.join(HERE, "arxiv_cand.json")))
pool = json.load(open(os.path.join(HERE, "arxiv_pool.json")))
# prioritise raman-in-abstract first
ids.sort(key=lambda k: not pool[k]["raman"])
RANGES = {"Eg1": (138, 160), "Eg2": (190, 210), "B1g1": (388, 412), "A1g/B1g2": (505, 530), "Eg3": (625, 655)}
for aid in ids:
    if aid in done: continue
    try:
        r = get("https://arxiv.org/pdf/" + aid, gap=3, timeout=120)
    except Exception as e:
        print(aid, "EXC", str(e)[:80], flush=True); continue
    rec = dict(id=aid, title=pool[aid]["title"][:100], status=r.status_code)
    if r.status_code == 200 and r.content[:4] == b"%PDF":
        try:
            d = fitz.open(stream=r.content, filetype="pdf")
            flat = re.sub(r"\s+", " ", " ".join(p.get_text() for p in d).replace("−", "-"))
            nR = len(re.findall("Raman", flat)); nA = len(re.findall("anatase", flat, re.I))
            nums = set()
            for m in re.finditer(r"(?<![\d.])(\d{3})(?:\.\d+)?(?![\d])", flat):
                v = int(m.group(1))
                for k, (lo, hi) in RANGES.items():
                    if lo <= v <= hi and re.search(r"cm|Raman|mode|peak|shift", flat[max(0, m.start() - 120):m.end() + 120]):
                        nums.add(k)
            rec.update(raman=nR, anatase=nA, modes=len(nums), pages=len(d), size=len(r.content))
            if nR >= 4 and nA >= 2 and len(nums) >= 3:
                open(os.path.join(OUT, aid.replace("/", "_") + ".pdf"), "wb").write(r.content)
                rec["kept"] = True
        except Exception as e:
            rec["err"] = str(e)[:80]
    with open(SC, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    if rec.get("kept"): print("KEEP", aid, rec["raman"], rec["anatase"], rec["modes"], rec["title"], flush=True)
print("DONE")
