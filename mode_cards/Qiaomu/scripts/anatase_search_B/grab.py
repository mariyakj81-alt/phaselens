"""Download candidate PDFs into the staging dir. Usage: grab.py key=url [key=url ...]  (key -> STAGE/key/paper.pdf). arXiv keys: arxiv-ID -> https://arxiv.org/pdf/ID"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, STAGE
import screen
for a in sys.argv[1:]:
    if "=" in a:
        key, url = a.split("=", 1)
    else:
        key, url = a, "https://arxiv.org/pdf/" + a
    out = os.path.join(STAGE, key.replace("/", "_").replace(":", "_"), "paper.pdf")
    ok, msg = fetch(url, out)
    print(key, ok, msg[:200], flush=True)
    if ok:
        try:
            screen.analyse(out)
        except Exception as e:
            print("   screen ERR", e)
