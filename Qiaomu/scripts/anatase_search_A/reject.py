"""Record a rejection and delete its folder. Usage: reject.py ANAid|- DOI "title" "reason" """
import sys, os, csv, glob, shutil
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
out = os.path.join(ROOT, "anatase", "candidates_rejected_A.csv")
aid, doi, title, reason = sys.argv[1:5]
new = not os.path.exists(out)
with open(out, "a", encoding="utf-8", newline="") as f:
    w = csv.writer(f, lineterminator="\r\n")
    if new: w.writerow(["doi", "title", "reason"])
    w.writerow([doi, title, reason])
if aid != "-":
    for d in glob.glob(os.path.join(ROOT, "anatase", aid + "_*")):
        shutil.rmtree(d); print("deleted", d)
