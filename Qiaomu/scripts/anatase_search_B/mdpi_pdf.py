"""Download MDPI article PDFs from the mdpi-res.com CDN (public, no challenge) and screen them.
Usage: mdpi_pdf.py 10.3390/xxx [...]   -> STAGE/<doi with / replaced by _>/paper.pdf"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, STAGE
import screen
SLUG = {"app": "applsci", "catal": "catalysts", "cryst": "crystals", "ma": "materials", "nano": "nanomaterials", "s": "sensors", "w": "water", "min": "minerals",
        "met": "metals", "inorganics": "inorganics", "ceramics": "ceramics", "chemosensors": "chemosensors", "photonics": "photonics", "mi": "micromachines",
        "coatings": "coatings", "surfaces": "surfaces", "condmat": "condensedmatter", "molecules": "molecules", "polym": "polymers", "ijms": "ijms", "energies": "energies",
        "processes": "processes", "batteries": "batteries", "nanoenergyadv": "nanoenergyadv", "solids": "solids", "jcs": "jcs", "technologies": "technologies",
        "membranes": "membranes", "gels": "gels", "toxics": "toxics", "environments": "environments", "sustainability": "sustainability", "applnano": "applnano",
        "chemengineering": "chemengineering", "colloids": "colloids", "nanomanufacturing": "nanomanufacturing", "physchem": "physchem", "photochem": "photochem",
        "analytica": "analytica", "applmech": "applmech", "jmmp": "jmmp", "lubricants": "lubricants", "materials": "materials", "optics": "optics", "quantumrep": "quantumrep",
        "spectroscj": "spectroscj", "textiles": "textiles", "water": "water", "separations": "separations", "sci": "sci", "foods": "foods", "fire": "fire", "dentistry": "dentistry",
        "jfb": "jfb", "biomimetics": "biomimetics", "bioengineering": "bioengineering", "cancers": "cancers", "micro": "micro", "nanomaterials": "nanomaterials", "applsci": "applsci"}


def mdpi_url(doi):
    m = re.match(r"10\.3390/([a-z]+)(\d+)$", doi.lower())
    if not m: return None
    code, digits = m.groups()
    vol, num = digits[:-6], digits[-4:]
    slug = SLUG.get(code, code)
    n5 = "%05d" % int(num)
    return f"https://mdpi-res.com/d_attachment/{slug}/{slug}-{int(vol):02d}-{n5}/article_deploy/{slug}-{int(vol):02d}-{n5}.pdf"


if __name__ == "__main__":
    for doi in sys.argv[1:]:
        u = mdpi_url(doi)
        if not u:
            print(doi, "cannot build url"); continue
        out = os.path.join(STAGE, doi.replace("/", "_"), "paper.pdf")
        ok, msg = fetch(u, out)
        print(doi, ok, msg[:140], flush=True)
        if ok:
            try: screen.analyse(out)
            except Exception as e: print("  screen err", e)
