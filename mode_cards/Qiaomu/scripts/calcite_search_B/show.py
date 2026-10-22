"""python -P show.py PDF [start_phrase] [nchars]: print beginning of text and the section after a phrase"""
import sys, fitz
d = fitz.open(sys.argv[1])
t = "".join(p.get_text() for p in d)
print(t[:int(sys.argv[3]) if len(sys.argv) > 3 else 1500])
if len(sys.argv) > 2:
    i = t.lower().find(sys.argv[2].lower())
    print("....", i); print(t[i:i + 2500] if i > 0 else "")
