# Architecture Overview

spectrum file
│
▼

1. Clean and pick peaks          pybaselines, scipy
│  peak list: position, height, width
▼
2. Load a mode card              spglib + a small curated table
│  allowed irreps, expected positions, silent modes,
│  plasma lines for this laser, substrate lines
▼
3. Assign                        Qwen, JSON only
│  each peak → one irrep, or "artifact"
▼
4. Accept or reject              plain Python constraints
│
▼
5. Read the structure            a formula, not the model
layers, strain direction, phase
│
▼
marimo plot: raw spectrum, baseline, sticks, assignment table,
a drawing of each vibration, a citation



**Sponsors used: **marimo, Valency, Adaptation, AutoScientist, Hugging Face Space

**Tools/libraries used: **pybaselines, scipy, spglib
