"""Resolve DOI -> landing page -> citation_pdf_url meta -> download + screen. Honest UA, per-host throttle, stops at challenge pages (never bypassed).
Usage: getdoi.py DOI [DOI...]   (MDPI DOIs use mdpi-res.com CDN)"""
import sys, os, re, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, fetch, STAGE
import screen
import mdpi_pdf
CH = re.compile(r"Making sure you.re not a bot|Client Challenge|cf-challenge|Just a moment|perfdrive|Access Denied|Attention Required|Verify you are human|Enable JavaScript and cookies", re.I)


def one(doi):
    out = os.path.join(STAGE, doi.replace("/", "_"), "paper.pdf")
    if doi.lower().startswith("10.3390/"):
        u = mdpi_pdf.mdpi_url(doi)
        ok, msg = fetch(u, out)
        return ok, msg, u
    try:
        r = get("https://doi.org/" + doi, timeout=60)
    except Exception as e:
        return False, "EXC doi.org " + str(e)[:80], None
    final = r.url; body = r.text if "html" in r.headers.get("content-type", "") else ""
    if r.content[:4] == b"%PDF":
        os.makedirs(os.path.dirname(out), exist_ok=True); open(out, "wb").write(r.content)
        return True, "direct pdf from doi.org " + final, final
    if r.status_code != 200 or CH.search(body[:6000]):
        return False, f"landing {r.status_code} {'CHALLENGE' if CH.search(body[:6000]) else ''} {final[:100]}", final
    m = re.search(r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"', body, re.I) or re.search(r'content="([^"]+)"\s+name="citation_pdf_url"', body, re.I)
    if not m:
        links = re.findall(r'href="([^"]+\.pdf[^"]*)"', body)
        pu = urllib.parse.urljoin(final, links[0]) if links else None
    else:
        pu = urllib.parse.urljoin(final, m.group(1).replace("&amp;", "&"))
    if not pu:
        return False, "no pdf link on " + final[:100], final
    ok, msg = fetch(pu, out)
    return ok, msg, pu


if __name__ == "__main__":
    for doi in sys.argv[1:]:
        ok, msg, u = one(doi)
        print(doi, ok, msg[:170], flush=True)
        if ok:
            try: screen.analyse(os.path.join(STAGE, doi.replace("/", "_"), "paper.pdf"))
            except Exception as e: print("  screen err", e)
