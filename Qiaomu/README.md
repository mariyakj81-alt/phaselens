# Qiaomu's part: calcite and anatase

This folder holds my assigned work for the project in [../README.md](../README.md): step 1 of [../SEQUENCE_OF_EXECUTION.md](../SEQUENCE_OF_EXECUTION.md) (mode cards) for **calcite** and **anatase**, plus the literature data behind them. The other materials (MoS2, quartz, Si) belong to teammates; their cards are in the repo-root `mode_cards/`.

## Deliverable: mode cards, in two versions

| Folder | Files | Size | Use it for |
| --- | --- | --- | --- |
| [mode_cards_simplified/](mode_cards_simplified/) | `calcite.json`, `anatase.json` (default) | ~15 KB | Qwen's context (ARCHITECTURE.md step 4) and quick reading. Sized like the team's cards. **An identical copy is in the repo-root team folder `../mode_cards/`.** |
| [mode_cards_comprehensive/](mode_cards_comprehensive/) | `calcite_comprehensive.json`, `anatase_comprehensive.json` | ~1 MB | All the literature: every collected paper and every extracted peak. **An identical copy is in `../mode_cards/`.** |

Both versions use the team's schema 2.1 (same layout as the repo-root `mode_cards/mos2.json` and `silicon.json`) and share these sections:
- `curated_expected_modes`: each Raman-active mode with its symmetry, a one-line description of the atomic motion, and the expected position, **copied from one primary paper**. Each mode also has a `literature_summary` over all collected papers: how many report it, the median and the 10–90% range.
  - Calcite: Bischoff, Sharma & Mackenzie 1985, Am. Mineral. 70, 581, Table 1 (488 nm).
  - Anatase: Ishioka et al. 2012, Phys. Rev. B 86, 205201, Table I (natural crystal, 532 nm).
- `symmetry_validation`: point group checked with spglib on the COD structure (`structures/`), plus the factor-group table (Raman-active, IR-only and silent irreps).
- `artifact_lines`: Si substrate line (520.2, from the team's silicon card) and laser plasma lines (NIST).
- `modes`, `cross_paper_summary` (agreement, conflicts, missing) and `confounders`.

They differ only in `studies` (and the plasma-line list):

| | Simplified | Comprehensive |
| --- | --- | --- |
| `studies` | one paper, the most trusted: the checked primary source of the curated positions (calcite: Bischoff et al. 1985, CAL003; anatase: Ishioka et al. 2012, ANA069) | every paper: calcite 67 papers / 1187 peaks, anatase 99 papers / 1268 peaks |
| plasma lines | only for the primary paper's laser | all lasers in `instrument_lines.json` |

**Done when** (SEQUENCE step 1): a teammate has checked every number against the paper. A checker agent has compared every curated number with the source tables ([CHECK.md](data/mode_card_sources/CHECK.md)); a human teammate still needs to sign off.

**Valency:** the project README says to use Valency to find the paper. Valency is blocked by organization policy in the tools I used, so the source papers came from OpenAlex, Europe PMC, Crossref and web search. To use a Valency-found paper instead, edit `data/mode_card_sources/primary_v1/` and rebuild.

## How the cards are built

```
data/mode_card_sources/primary_v1/<material>_v1.json   checked one-paper card (curated positions)
data/mode_card_sources/instrument_lines.json           Si line + NIST plasma lines   <- scripts/build_instrument_lines.py
<material>/papers.csv + peaks/<material>_peaks.csv     all papers and peaks          <- extraction + scripts/merge_peaks.py
        |
        v  scripts/build_mode_cards.py
mode_cards_comprehensive/<material>_comprehensive.json  ->  ../mode_cards/<material>_comprehensive.json (identical copy)
mode_cards_simplified/<material>.json                    ->  ../mode_cards/<material>.json (identical copy)
```

Rebuild and check, from this folder:

```bash
pip install -r requirements.txt
python -P scripts/build_instrument_lines.py
python -P scripts/merge_peaks.py calcite
python -P scripts/merge_peaks.py anatase
python -P scripts/build_mode_cards.py
python -P scripts/validate_project.py --no-pdf
```

`validate_project.py` also checks the cards: both versions exist and load, their curated positions equal the checked `primary_v1` values, every simplified study is in the comprehensive card, and the copies in `../mode_cards/` are identical to the ones here. The build writes only `<material>.json` and `<material>_comprehensive.json` (calcite, anatase) in `../mode_cards/`; it never touches the other files there.

## Folder layout

| Path | What it is |
| --- | --- |
| `mode_cards_simplified/`, `mode_cards_comprehensive/` | The two card versions (deliverable). Both are copied to the repo-root `mode_cards/`: the simplified card as the default `<material>.json`, the comprehensive one as `<material>_comprehensive.json`. |
| `Architecture Overview.md`, `Sequence of Execution.md` | The team plan, with notes on where the calcite/anatase cards and data fit (step 1 status, test-only calcite data, checker window). |
| `data/mode_card_sources/` | Inputs of the cards: `primary_v1/` (checked one-paper cards), `CHECK.md`, `instrument_lines.json`. |
| `data/reference/nist_asd/` | NIST line lists used for the plasma lines. |
| `calcite/papers.csv`, `anatase/papers.csv` | Bibliographies: 67 calcite and 100 anatase papers with Raman data. Each paper's PDF, SI and data files are in its own folder, kept out of git (copyrighted). |
| `peaks/` | Extracted peak tables (`calcite_peaks.csv`, `anatase_peaks.csv`), one file per paper, fit plots and review logs. See [peaks/README.md](peaks/README.md). |
| `scripts/` | `build_mode_cards.py`, `build_instrument_lines.py`, `fit_raman.py` (peak positions from raw spectra), `merge_peaks.py` and `validate_project.py` (checks), `EXTRACTION_PROTOCOL.md` (rules for the peak tables), `mode_reference.json` (fit windows), and the search agents' scripts. |
| `structures/` | COD CIFs (calcite and anatase are used; quartz, Si, MoS2 were fetched before the scope was narrowed). |
| `mos2/`, `quartz/`, `silicon/` | One source paper each, collected before the scope was narrowed. Not used by my cards. |
| `history.md`, `memory.md`, `feedback.md` | Logs written by the agents that built the dataset. |

## Not finished

- Calcite has 67 papers, not 100. The search for CAL068–CAL100 was stopped when the scope moved to mode cards.
- ANA088 has no usable peaks (its numbers came from 2D-correlation analysis) and needs a replacement paper, so the anatase cards hold 99 studies.
- The second review round (papers 34–100) was stopped before it recorded results. Round 1 (papers 1–33) was reviewed: no wrong peak values in 135 sampled rows.
- Calcite is the held-out test material in the project README. If the calcite studies are used as data, keep them in test, not train.
