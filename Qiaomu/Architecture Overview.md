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
│  calcite, anatase: Qiaomu/mode_cards_simplified/<material>.json
│  (literature backing: Qiaomu/mode_cards_comprehensive/)
▼
3. Assign                        Qwen, JSON only
│  each peak → one irrep, or "artifact"
▼
4. Accept or reject              plain Python constraints
│  "too far from the card": the mode's literature_summary
│  10-90% range in the card (calcite, anatase)
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

## Calcite and anatase (Qiaomu)

- Mode cards (step 2) come in two versions with the same schema 2.1 as the team's `mode_cards/`:
  - `Qiaomu/mode_cards_simplified/`: load this one at runtime and send it to Qwen (about 25 KB).
  - `Qiaomu/mode_cards_comprehensive/`: every collected paper and peak (calcite 67 papers / 1187 peaks, anatase 99 papers / 1268 peaks), for checking and for real test data.
- Expected positions come from one checked primary paper per material (Bischoff et al. 1985 for calcite; Ishioka et al. 2012 for anatase). Each mode's `literature_summary` gives the spread over all papers; the checker (step 4) can use it as the allowed window.
- Each card carries the factor-group table (spglib-checked point group, Raman-active, IR-only and silent irreps), the Si line and the NIST laser plasma lines, so step 4 can mark them "artifact".
- Valency was blocked by organization policy for this part; papers were found with OpenAlex, Europe PMC, Crossref and web search.
- Calcite is the held-out test material: keep calcite literature data out of training.

