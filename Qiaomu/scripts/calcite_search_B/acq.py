"""Acquire OA PDFs for DOIs via legitimate routes (no challenge evasion), verify, and score calcite Raman numbers.
usage: python -P acq.py STAGE_DIR doi1 doi2 ...
Routes: OpenAlex locations (skipping known bot-challenge hosts), nature.com/articles/<id>.pdf, PMC OA S3 bucket,
repository landing pages (citation_pdf_url meta or bitstream links)."""
import sys, os, re, json, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
import fitz

STAGE = sys.argv[1]
BLOCK = re.compile(r"mdpi\.com|onlinelibrary\.wiley|wiley\.com|pubs\.rsc|link\.springer|springer\.com|sciencedirect|pubs\.acs|iopscience|tandfonline|academic\.oup|hal\.science|hal\.archives|opus4|aps\.org|aip\.|pubs\.aip|degruyter|geoscienceworld|europepmc\.org|ncbi\.nlm\.nih|preprints\.org|researchgate|ssrn\.com|doi\.org|dx\.doi|sagepub|hindawi|researchsquare|rruff|e3s-conferences|cambridge\.org/core/journals|liebertpub|cancerres|ieee", re.I)
WINS = {"T155": (148, 164), "L282": (272, 292), "v4_712": (704, 722), "v1_1086": (1078, 1095), "v3_1436": (1425, 1450), "2v2_1749": (1738, 1758)}
S3 = "https://pmc-oa-opendata.s3.amazonaws.com/"
DEAD = set()


def slug(d):
    return re.sub(r"[^A-Za-z0-9._-]", "_", d)


def openalex(doi):
    r = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/"), params={"select": "title,publication_year,locations,authorships"}, min_gap=0.8)
    return r.json() if r.status_code == 200 else None


def pmcid_of(doi):
    r = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query": f'DOI:"{doi}"', "format": "json", "resultType": "lite"}, min_gap=0.5)
    if r.status_code == 200:
        for w in r.json().get("resultList", {}).get("result", []):
            if w.get("pmcid"):
                return w["pmcid"]
    return None


def score(path):
    d = fitz.open(path)
    t = " ".join(re.sub(r"\s+", " ", pg.get_text()) for pg in d)
    low = t.lower()
    hits = {k: set() for k in WINS}
    for m in re.finditer(r"calcite|caco|carbonate", low):
        seg = t[max(0, m.start() - 250): m.end() + 250]
        for n in re.findall(r"(?<![\d.])(\d{3,4}(?:\.\d+)?)(?![\d])", seg):
            x = float(n)
            for k, (lo, hi) in WINS.items():
                if lo <= x <= hi:
                    hits[k].add(n)
    return d.page_count, low.count("raman"), low.count("calcite"), {k: sorted(v, key=float)[:5] for k, v in hits.items() if v}, t


def verify(path, title):
    with open(path, "rb") as f:
        if f.read(5) != b"%PDF-":
            return None
    try:
        n, ram, cal, hits, t = score(path)
    except Exception:
        return None
    words = [w for w in re.findall(r"[a-z0-9]+", (title or "").lower()) if len(w) > 3]
    first = t[:6000].lower()
    th = sum(1 for w in set(words) if w in first)
    return dict(pages=n, raman=ram, calcite=cal, hits=hits, title_hits=f"{th}/{len(set(words))}", ok=(th >= max(2, int(0.4 * len(set(words)))) and ram > 2))


def try_pdf(u, d, title, tries, depth=0):
    try:
        host = urllib.parse.urlparse(u).netloc
        if host in DEAD:
            tries.append((u[:80], 'dead-host')); return None
        r = get(u, min_gap=10, timeout=(15, 90), retries=0)
    except Exception as e:
        tries.append((u[:80], type(e).__name__)); DEAD.add(urllib.parse.urlparse(u).netloc); return None
    ct = r.headers.get("content-type", "")
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        p = os.path.join(d, "paper.pdf"); open(p, "wb").write(r.content)
        v = verify(p, title)
        tries.append((u[:80], v and v["title_hits"]))
        if v and v["ok"]:
            return p, v
        os.remove(p); return None
    tries.append((u[:80], f"{r.status_code} {ct[:25]}"))
    if r.status_code == 200 and "html" in ct and depth == 0 and not BLOCK.search(r.url):
        cands = re.findall(r"""<meta[^>]+name=["']citation_pdf_url["'][^>]+content=["']([^"']+)""", r.text[:300000])
        cands += [urllib.parse.urljoin(r.url, m.replace("&amp;", "&")) for m in re.findall(r"""href=["']([^"']*(?:bitstream|/retrieve/|/download|\.pdf)[^"']*)["']""", r.text[:600000])[:6]]
        seen = set()
        for c in cands:
            c = urllib.parse.urljoin(r.url, c.replace("&amp;", "&"))
            if c in seen or c == u or BLOCK.search(c) or re.search(r"(?i)(license|policy|sitemap|\.css|\.js)", c):
                continue
            seen.add(c)
            res = try_pdf(c, d, title, tries, depth=1)
            if res:
                return res
            if len(seen) >= 4:
                break
    return None


def run(doi):
    d = os.path.join(STAGE, slug(doi)); os.makedirs(d, exist_ok=True)
    out = {"doi": doi, "tries": []}
    w = openalex(doi)
    title = (w or {}).get("title") or ""
    out["title"] = title; out["year"] = (w or {}).get("publication_year")
    out["author"] = (((w or {}).get("authorships") or [{}])[0].get("author") or {}).get("display_name")
    urls = []
    suffix = doi.split("/", 1)[1] if "/" in doi else doi
    if doi.startswith("10.1038/") or doi.startswith("10.1186/s40494"):
        urls.append(f"https://www.nature.com/articles/{suffix}.pdf")
    if doi.startswith("10.3389/"):
        urls.append(f"https://www.frontiersin.org/articles/{doi}/pdf")
    if doi.startswith("10.1371/"):
        urls.append(f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable")
    if doi.startswith("10.5194/"):
        pass
    pm = None
    for l in (w or {}).get("locations", []):
        for k in ("pdf_url", "landing_page_url"):
            u = l.get(k)
            if u and u not in urls:
                urls.append(u)
    # PMC S3 package
    try:
        pm = pmcid_of(doi)
    except Exception:
        pm = None
    out["pmcid"] = pm
    res = None
    if pm:
        r = get(S3 + f"?prefix={pm}.&max-keys=300", min_gap=1)
        keys = re.findall(r"<Key>(.*?)</Key>", r.text) if r.status_code == 200 else []
        for k in keys:
            if k.endswith(".1.pdf"):
                r2 = get(S3 + k, min_gap=1, timeout=120)
                if r2.status_code == 200 and r2.content[:5] == b"%PDF-":
                    p = os.path.join(d, "paper.pdf"); open(p, "wb").write(r2.content)
                    v = verify(p, title)
                    out["tries"].append(("pmc-s3", v and v["title_hits"]))
                    if v and v["ok"]:
                        res = (p, v); out["via"] = "PMC OA bucket " + pm
                    else:
                        os.remove(p)
    for u in ([] if res else urls):
        if BLOCK.search(u) and "nature.com" not in u:
            out["tries"].append((u[:80], "skip-blocked-host")); continue
        res = try_pdf(u, d, title, out["tries"])
        if res:
            out["via"] = u; break
    if res:
        out["ok"] = True; out["verify"] = res[1]
    else:
        out["ok"] = False
    json.dump(out, open(os.path.join(d, "result.json"), "w"), indent=1, default=str)
    return out


if __name__ == "__main__":
    for doi in sys.argv[2:]:
        try:
            o = run(doi.lower())
        except Exception as e:
            print("ERR", doi, type(e).__name__, str(e)[:80]); continue
        v = o.get("verify")
        if v:
            print("OK  ", doi, "|", (o["author"] or "")[:20], o["year"], "|", (o["title"] or "")[:55], "| p", v["pages"], "r", v["raman"], "c", v["calcite"], v["hits"], flush=True)
        else:
            print("FAIL", doi, "|", (o["title"] or "")[:55], "|", [str(t[1])[:25] for t in o["tries"]][:5], flush=True)
