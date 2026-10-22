# Writes examples/*.csv and results/*.json from spectrum files.
# The JSON copies gold answers. It is not model output, and app.py does not read it.
import csv, json, sys
from pathlib import Path

# Only fill in citations you have checked in the mode cards. Empty = app says "no citation".
REFERENCES = {
    "quartz": [{"citation": "Zicovich-Wilson et al. 2004, J. Comput. Chem. 25, 1873", "doi": "10.1002/jcc.20120"}],
    "mos2": [{"citation": "Lee et al., ACS Nano 4, 2695-2700 (2010)", "doi": "10.1021/nn1003937"}],
    "silicon": [{"citation": "Parker, Feldman, and Ashkin, Physical Review 155, 712-714 (1967)", "doi": "10.1103/PhysRev.155.712"}],
    "anatase_simplified": [{"citation": "Rousseau, Bauman & Porto 1981, J. Raman Spectrosc. 10, 253", "doi": ""}],
    "calcite_simplified": [{"citation": "Rousseau, Bauman & Porto 1981, J. Raman Spectrosc. 10, 253", "doi": ""}],
}

def convert(path: Path):
    d = json.loads(path.read_text())
    idx, material = path.stem.split("_", 1)          # "00003_quartz" -> "00003", "quartz"
    name = f"{material}_{idx}"                        # -> "quartz_00003"
    ctx = d.get("context", {})
    sp = d["spectrum"]

    # 1) spectrum -> examples/<name>.csv
    with open(f"examples/{name}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shift", "intensity"])
        w.writerows(zip(sp["shift_cm-1"], sp["intensity"]))

    # 2) peaks + labels -> results/<name>.json
    labels = {round(a["position_cm-1"], 2): a for a in d.get("answers", [])}
    plasma_placeholder = ctx.get("known_artifact_lines_cm-1", {}).get("plasma_is_placeholder")
    peaks = []
    for p in d["peaks"]:
        pos = p["position_cm-1"]
        a = labels.get(round(pos, 2), {})
        label = a.get("label", "unassigned")
        is_art = (label == "artifact")
        reason = ""
        if is_art:
            reason = f"{a.get('source', 'unknown')} line"
            if a.get("source") == "plasma" and plasma_placeholder:
                reason += " (placeholder position, not verified)"
        peaks.append({
            "position_cm1": pos,
            "intensity": p.get("height"),
            "symmetry": "artifact" if is_art else label,
            "is_artifact": is_art,
            "artifact_reason": reason,
        })

    out = {"peaks": peaks,
                      "references": REFERENCES.get(material, REFERENCES.get(ctx.get("material", ""), []))}
    if ctx.get("layer") is not None:
        out["interpretation"] = {"label": "Layer number", "value": str(ctx["layer"]),
                                 "note": "From the saved file's context."}
    Path(f"results/{name}.json").write_text(json.dumps(out, indent=2))
    print(f"OK: {name}  ({len(sp['shift_cm-1'])} points, {len(peaks)} peaks)")

if __name__ == "__main__":
    folder = Path(sys.argv[1])
    arg = sys.argv[2:]
    if arg and arg[0].isdigit():              # a number: that many per material
        per_material = int(arg[0])
        seen = {}
        for p in sorted(folder.glob("*.json")):
            material = p.stem.split("_", 1)[1]
            if seen.get(material, 0) < per_material:
                convert(p)
                seen[material] = seen.get(material, 0) + 1
    elif arg == ["all"]:                      # every file in the folder
        for p in sorted(folder.glob("*.json")):
            convert(p)
    else:                                     # specific file names
        for fname in arg:
            convert(folder / fname)
