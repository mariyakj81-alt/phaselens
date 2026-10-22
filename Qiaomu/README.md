# Qiaomu's part: calcite and anatase

This folder holds my assigned work for the project in [../README.md](../README.md): step 1 of [../SEQUENCE_OF_EXECUTION.md](../SEQUENCE_OF_EXECUTION.md) (mode cards) for **calcite** and **anatase**, plus the literature data behind them.

## Deliverable: mode cards

| File | Source paper | Status |
| --- | --- | --- |
| [data/mode_cards/calcite.json](data/mode_cards/calcite.json) | Bischoff, Sharma & Mackenzie 1985, Am. Mineral. 70, 581, Table 1 (488 nm) | Checked by agent, human sign-off pending: [CHECK.md](data/mode_cards/CHECK.md) |
| [data/mode_cards/anatase.json](data/mode_cards/anatase.json) | Ishioka et al. 2012, Phys. Rev. B 86, 205201, Table I (natural crystal, 532 nm) | Checked by agent, human sign-off pending: [CHECK.md](data/mode_cards/CHECK.md) |
| [data/mode_cards/instrument_lines.json](data/mode_cards/instrument_lines.json) | NIST Atomic Spectra Database (laser plasma lines), Si line | Built by `scripts/build_instrument_lines.py` |

Both cards use the team's schema 2.1 (same layout as `../mode_cards/mos2.json` and `silicon.json`) and are built by `scripts/build_mode_cards.py`:
- `curated_expected_modes`: each Raman-active mode with its symmetry, motion and expected position, **copied from one primary paper** (checked number by number, `data/mode_cards/CHECK.md`; the checked one-paper version is kept in `data/mode_cards/primary_v1/`). Each mode also carries a `literature_summary`: how many papers report it, median and 10-90% range.
- `studies`: **every collected paper** (calcite 67, anatase 99) with all its spectra and peaks (1187 and 1268 peaks), provenance, value type and `training_eligible` flag.
- `symmetry_validation` (spglib on the COD structure + factor-group table: Raman-active, IR-only and silent irreps), `artifact_lines` (Si substrate line, laser line, NIST plasma lines), `cross_paper_summary` (agreement, conflicts, missing) and `confounders`.

Each card is about 1 MB because of `studies`. For the Qwen prompt (ARCHITECTURE.md step 4) pass only `curated_expected_modes`, `symmetry_validation` and `artifact_lines`.

**Done when** (SEQUENCE step 1): a teammate has checked every number against the paper. A checker agent has compared every number. A human teammate still needs to sign off: compare `curated_expected_modes` with the two source tables (instructions in CHECK.md).

**Valency:** the README says to use Valency to find the paper. Valency is blocked by organization policy in the tools I used, so the source papers came from OpenAlex, Europe PMC, Crossref and web search. If you prefer a Valency-found paper, change `primary_v1/` and rerun `scripts/build_mode_cards.py`.

## Supporting data

| Path | What it is |
| --- | --- |
| `calcite/papers.csv`, `anatase/papers.csv` | Bibliographies: 67 calcite and 100 anatase papers with Raman data. Each paper's PDF, SI and data files are in its own folder, kept out of git (copyrighted). |
| `peaks/calcite_peaks.csv`, `peaks/anatase_peaks.csv` | Peak positions extracted from those papers: 1187 calcite rows and 1268 anatase rows, with mode labels, conditions, laser and source location. Built by `scripts/merge_peaks.py`. See [peaks/README.md](peaks/README.md). |
| `scripts/` | `fit_raman.py` (peak positions from raw spectra), `merge_peaks.py` and `validate_project.py` (consistency checks), `EXTRACTION_PROTOCOL.md` (rules for the peak tables), `mode_reference.json` (fit windows). |
| `structures/` | COD CIFs for calcite and anatase (plus quartz, Si, MoS2, fetched before the scope was narrowed). |
| `mos2/`, `quartz/`, `silicon/` | One source paper each, collected before the scope was narrowed to calcite and anatase. Not used by my cards; left for the teammates who own those materials. |
| `history.md`, `memory.md`, `feedback.md` | Logs written by the agents that built the dataset. |

Run the checks from this folder:

```bash
pip install -r requirements.txt
python -P scripts/merge_peaks.py calcite
python -P scripts/validate_project.py --no-pdf
```

## Not finished

- Calcite has 67 papers, not 100. The search for CAL068–CAL100 was stopped when the scope moved to mode cards.
- ANA088 has no usable peaks (its numbers came from 2D-correlation analysis) and needs a replacement paper.
- The second review round (spot checks of papers 34–100) was stopped before it recorded results. Round 1 (papers 1–33) was reviewed: no wrong peak values in 135 sampled rows.
- Calcite is the held-out test material in the project README. If the calcite peak tables are used, keep them in test, not train.
