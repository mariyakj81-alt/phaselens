import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, STAGE
import screen
items = {
 "Giarola2010": "https://iris.univr.it/bitstream/11562/342058/1/Vibrational%20dynamics%20of%20anatase%20TiO.pdf",
 "korea2004": "https://koreascience.kr/article/JAKO200402727211737.pdf",
 "APP116z106": "https://przyrbwn.icm.edu.pl/APP/PDF/116/a116z106.pdf",
 "Rigby": "https://rgu-repository.worktribe.com/output/247960/the-application-of-raman-and-anti-stokes-raman-spectroscopy-for-in-situ-monitoring-of-structural-changes-in-laser-irradiated-titanium-dioxide-materials",
 "sciforum7086": "https://sciforum.net/paper/download/7086/manuscript",
 "Ishioka": "https://www.nims.go.jp/ldynamics/eprints/PhysRevB.86.205201.pdf",
 "nanotubeRSC": "https://pubs.rsc.org/en/content/getauthorversionpdf/c6ra15614b",
}
for k, u in items.items():
    out = os.path.join(STAGE, k, "paper.pdf")
    ok, msg = fetch(u, out)
    print(k, ok, msg[:180], flush=True)
    if ok:
        try: screen.analyse(out)
        except Exception as e: print("  screen err", e)
