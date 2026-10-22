"""Resolve OA/legit PDF URLs for DOIs, download, verify. Usage: python -P acquire.py STAGE_DIR doi1 doi2 ...
Never bypasses challenges: if a response is not a PDF it is logged and the next legitimate source is tried."""
import sys, os, re, json, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get
import fitz

STAGE = sys.argv[1] if __name__ == "__main__" else None
MODES = ["1086","1085","1087","1088","712","713","714","282","281","283","155","154","156","1436","1437","1435","1749","1750","1748"]

def slug(doi): return re.sub(r"[^A-Za-z0-9._-]", "_", doi)

def openalex(doi):
    r = get("https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi, safe="/"), min_gap=1)
    if r.status_code != 200: return None
    return r.json()

def epmc_pmcid(doi):
    r = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params={"query": f'DOI:"{doi}"', "format": "json", "resultType": "lite"}, min_gap=1)
    if r.status_code == 200:
        for w in r.json().get("resultList", {}).get("result", []):
            if w.get("pmcid"): return w["pmcid"]
    return None

BLOCKED = ["europepmc.org", "pmc.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov", "mdpi.com", "onlinelibrary.wiley.com", "pubs.rsc.org",
           "link.springer.com", "preprints.org", "researchgate.net", "sciencedirect.com", "pubs.acs.org", "academic.oup.com", "tandfonline.com"]
def is_blocked(u): return any(b in urllib.parse.urlparse(u).netloc for b in BLOCKED)

S3 = "https://pmc-oa-opendata.s3.amazonaws.com/"
def s3_package(pmcid, d):
    """NIH PMC Open Access dataset on AWS (public bucket): PDF, XML and supplementary files for OA-licensed articles."""
    r = get(S3 + f"?prefix={pmcid}.&max-keys=300", min_gap=1)
    keys = re.findall(r"<Key>(.*?)</Key>", r.text) if r.status_code == 200 else []
    got = {"pdf": None, "xml": None, "si": []}
    for k in keys:
        name = k.split("/")[-1]
        if name.endswith((".json", ".txt")): continue
        isimg = re.search(r"\.(jpg|jpeg|gif|png|tif|tiff)$", name, re.I) and "MOESM" not in name and not re.search(r"(?i)supp|s0\d\d", name)
        if isimg: continue
        if name == f"{pmcid}.1.pdf" or name.endswith(".1.pdf") and name.startswith("PMC"):
            r2 = get(S3 + k, min_gap=1, timeout=120)
            if r2.status_code == 200 and r2.content[:5] == b"%PDF-":
                open(os.path.join(d, "paper.pdf"), "wb").write(r2.content); got["pdf"] = os.path.join(d, "paper.pdf")
        elif name.endswith(".1.xml") and name.startswith("PMC"):
            r2 = get(S3 + k, min_gap=1, timeout=120)
            if r2.status_code == 200: open(os.path.join(d, "fulltext.xml"), "wb").write(r2.content); got["xml"] = True
        else:
            r2 = get(S3 + k, min_gap=1, timeout=300)
            if r2.status_code == 200:
                os.makedirs(os.path.join(d, "SI"), exist_ok=True)
                open(os.path.join(d, "SI", name), "wb").write(r2.content); got["si"].append(name)
    return got

def candidate_urls(doi, w, pmcid):
    urls = []
    for l in (w or {}).get("locations", []):
        if l.get("pdf_url"):
            urls.append(("oa-loc:" + str(l.get("version")), l["pdf_url"]))
    try:
        rr = get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}", params={"fields": "openAccessPdf"}, min_gap=2)
        if rr.status_code == 200 and (rr.json().get("openAccessPdf") or {}).get("url"):
            urls.append(("s2", rr.json()["openAccessPdf"]["url"]))
    except Exception: pass
    suffix = doi.split("/",1)[1] if "/" in doi else doi
    if doi.startswith("10.1007") or doi.startswith("10.1186"):
        urls.append(("springer", f"https://link.springer.com/content/pdf/{doi}.pdf"))
    if doi.startswith("10.1038"):
        urls.append(("nature", f"https://www.nature.com/articles/{suffix}.pdf"))
    if doi.startswith("10.1371"):
        urls.append(("plos", f"https://journals.plos.org/plosone/article/file?id={doi}&type=printable"))
    seen=set(); out=[]
    for k,u in urls:
        if u not in seen: seen.add(u); out.append((k,u))
    return out

def verify(path, title):
    info = {"ok": False}
    with open(path, "rb") as f: head = f.read(5)
    if head != b"%PDF-": info["why"] = "not %PDF"; return info
    try:
        d = fitz.open(path)
    except Exception as e:
        info["why"] = f"fitz fail {e}"; return info
    n = d.page_count
    txt = "".join(d[i].get_text() for i in range(min(n, 3))).lower()
    full = "".join(p.get_text() for p in d).lower()
    words = [x for x in re.findall(r"[a-z0-9]+", (title or "").lower()) if len(x) > 3]
    hit = sum(1 for x in set(words) if x in txt)
    info.update(pages=n, title_hits=f"{hit}/{len(set(words))}", raman=full.count("raman"), calcite=full.count("calcite"),
                modes=sorted({m for m in MODES if re.search(r"(?<![0-9.])" + m + r"(?![0-9])", full)}))
    info["ok"] = hit >= max(2, int(0.5 * len(set(words)))) and info["raman"] > 3
    if not info["ok"]: info["why"] = "title/raman mismatch"
    return info

def run(doi):
    d = os.path.join(STAGE, slug(doi)); os.makedirs(d, exist_ok=True)
    res = {"doi": doi}
    w = openalex(doi)
    if not w:
        res["err"] = "openalex fail"; return res
    res["title"] = w.get("title"); res["year"] = w.get("publication_year")
    res["authors"] = [a["author"]["display_name"] for a in w.get("authorships", [])][:3]
    res["venue"] = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
    pmcid = epmc_pmcid(doi); res["pmcid"] = pmcid
    tries = []
    if pmcid:
        g = s3_package(pmcid, d); res["s3"] = {"xml": g["xml"], "si": g["si"]}
        if g["pdf"]:
            v = verify(g["pdf"], res["title"]); tries.append(("pmc-s3", "s3", v))
            if v["ok"]: res["pdf"] = g["pdf"]; res["pdf_url"] = "pmc-oa-opendata " + pmcid; res["verify"] = v
            else: os.remove(g["pdf"])
    for kind, u in ([] if res.get("pdf") else candidate_urls(doi, w, pmcid)):
        if is_blocked(u):
            tries.append((kind, u, "skipped (known bot-challenge host)")); continue
        host = urllib.parse.urlparse(u).netloc
        try:
            r = get(u, min_gap=10 if "europepmc" not in host and "ebi.ac.uk" not in host else 2, timeout=90)
        except Exception as e:
            tries.append((kind, u, f"exc {type(e).__name__}")); continue
        ctype = r.headers.get("content-type", "")
        if r.status_code == 200 and r.content[:5] == b"%PDF-":
            p = os.path.join(d, "paper.pdf")
            open(p, "wb").write(r.content)
            v = verify(p, res["title"]); tries.append((kind, u, v))
            if v["ok"]:
                res["pdf"] = p; res["pdf_url"] = u; res["verify"] = v; break
            else:
                os.remove(p)
        else:
            tries.append((kind, u, f"{r.status_code} {ctype[:30]}"))
            m = re.search(r"""<meta[^>]+name=["']citation_pdf_url["'][^>]+content=["']([^"']+)""", r.text[:200000]) if r.status_code == 200 and "html" in ctype else None
            if m:
                pu = urllib.parse.urljoin(r.url, m.group(1).replace("&amp;", "&"))
                if not is_blocked(pu):
                    try:
                        r2 = get(pu, min_gap=10, timeout=90)
                        if r2.status_code == 200 and r2.content[:5] == b"%PDF-":
                            p = os.path.join(d, "paper.pdf"); open(p, "wb").write(r2.content)
                            v = verify(p, res["title"]); tries.append((kind + "+meta", pu, v))
                            if v["ok"]: res["pdf"] = p; res["pdf_url"] = pu; res["verify"] = v; break
                            os.remove(p)
                        else: tries.append((kind + "+meta", pu, f"{r2.status_code} {r2.headers.get('content-type','')[:30]}"))
                    except Exception as e: tries.append((kind + "+meta", pu, f"exc {type(e).__name__}"))
    res["tries"] = tries
    if pmcid and not res.get("xml") and not (res.get("s3") or {}).get("xml"):
        r = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", min_gap=1)
        if r.status_code == 200 and b"<article" in r.content[:2000]:
            open(os.path.join(d, "fulltext.xml"), "wb").write(r.content); res["xml"] = True
    json.dump(res, open(os.path.join(d, "result.json"), "w"), indent=1, default=str)
    return res

if __name__ == "__main__":
    for doi in sys.argv[2:]:
        try:
            r = run(doi.lower())
        except Exception as e:
            print("ERR", doi, e); continue
        v = r.get("verify")
        print(("OK  " if v else "FAIL"), doi, "|", (r.get("title") or "")[:60], "|", r.get("authors", [""])[:1], r.get("year"), "| pmc" if r.get("pmcid") else "", "|", v and (v["pages"], v["raman"], v["calcite"], v["modes"]) or [str(t[2])[:40] for t in r.get("tries", [])], flush=True)
