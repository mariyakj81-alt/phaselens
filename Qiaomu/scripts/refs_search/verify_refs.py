"""Verify every downloaded paper of mos2/, quartz/, silicon/: %PDF header, PyMuPDF opens, title words on
the first two pages, and the key numbers appear in the text layer.

Run from the project root:  python -P scripts/refs_search/verify_refs.py
(Old OCR layers such as minsocam scans split digits, so numbers are matched with optional spaces.)
"""
import csv
import os
import re
import sys

import fitz

CHECKS = {
    "MOS001": (["Anomalous", "Lattice", "Vibrations", "MoS2"], ["384", "514.5", "520", "2.1"]),
    "MOS002": (["Band", "Gap", "Engineering", "Biaxial", "MoS2"], ["-5.2", "-1.7", "385", "405", "532", "21.7", "23.7"]),
    "MOS003": (["Bandgap", "Engineering", "Strained", "MoS2"], ["4.5", "403", "384", "532", "1.0"]),
    "QTZ001": (["Raman", "microcrystalline", "silica"],
               ["128", "206", "265", "355", "394", "401", "450", "464", "511", "696", "796", "808", "1069", "1085", "1162", "1230"]),
    "QTZ002": (["Raman", "intensities", "quartz"],
               ["207", "356", "464", "1085", "128", "265", "394", "450", "697", "795", "1072", "1162", "401", "509", "807", "1235"]),
    "SIL001": (["Silicon", "Nanowire", "Raman"], ["520.05", "302.06", "964.48", "532"]),
    "SIL002": (["Raman", "nanostructured", "silicon"], ["520.0", "3.5", "2TO", "2TA", "488", "514", "633"]),
}


def loose(num):
    # allow OCR spaces between digits: '1085' -> '1\s?0\s?8\s?5'
    return r"\s?".join(re.escape(c) for c in num)


def main():
    ok_all = True
    for material in ("mos2", "quartz", "silicon"):
        for row in csv.DictReader(open(f"{material}/papers.csv", encoding="utf-8")):
            pid, folder, status = row["paper_id"], row["folder"], row["pdf_status"]
            path = os.path.join(folder, "paper.pdf")
            if status == "needs_manual":
                n = len(os.listdir(folder)) if os.path.isdir(folder) else -1
                print(f"{pid}: needs_manual, folder exists={os.path.isdir(folder)}, files in folder={n}")
                continue
            head = open(path, "rb").read(5)
            doc = fitz.open(path)
            text = "".join(p.get_text() for p in doc)
            first = "".join(doc[i].get_text() for i in range(min(2, len(doc))))
            words, nums = CHECKS[pid]
            wmiss = [w for w in words if w.lower() not in first.lower()]
            nmiss = [n for n in nums if not re.search(loose(n), text)]
            good = head == b"%PDF-" and len(doc) > 0 and not wmiss
            ok_all &= good
            print(f"{pid}: {os.path.getsize(path)} bytes, {len(doc)} pages, header={head!r}, title words missing={wmiss}, "
                  f"numbers not found in text layer={nmiss}, {'OK' if good else 'CHECK'}")
    print("ALL OK" if ok_all else "SOME CHECKS FAILED")


if __name__ == "__main__":
    sys.exit(main())
