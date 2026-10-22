# Literature Raman peak tables

> Counts and statistics below are from round 1 (33 papers per mineral). The tables now hold 1187 calcite rows (67 papers) and 1268 anatase rows (99 of 100 papers); rerun `python -P scripts/merge_peaks.py <mineral>` for current numbers.

Peak positions for calcite and anatase, collected from 33 papers each. Each row is one peak in one spectrum: one sample under one condition.

| File | What it holds |
| --- | --- |
| `calcite_peaks.csv` | 810 peaks, 33 papers, 179 spectra or samples |
| `anatase_peaks.csv` | 556 peaks, 33 papers, 223 spectra or samples |
| `<mineral>/<paper_id>.csv` | The same rows, one file per paper. Edit these, then rebuild the merged file with `python -P scripts/merge_peaks.py <mineral>`. |
| `<mineral>/plots/` | Fit plots for every spectrum fitted from raw data |
| `<mineral>_review.csv` | Rows re-checked against the source papers (68 calcite, 67 anatase) |
| `<mineral>_changes.csv` | Every cell the review changed, with the reason |

The papers themselves are listed in `../calcite/papers.csv` and `../anatase/papers.csv`. Each paper's PDF, SI and data files are in its own folder there. Those folders are not in git because the papers are copyrighted.

## Columns

The column rules are in [`../scripts/EXTRACTION_PROTOCOL.md`](../scripts/EXTRACTION_PROTOCOL.md). The ones you will filter on most:

- `mode_label` / `mode_symmetry`: labels from [`../scripts/mode_reference.json`](../scripts/mode_reference.json). `unassigned` is a peak with no mode. `artifact` is a silicon substrate line or the laser line.
- `assignment_source`: `paper` (the paper's own assignment), `reference` (nearest reference mode), or `rule` (set by a fixed rule, such as the Si line or doublet order).
- `data_source`, from most to least direct:
  - `raw_fit`: our own deconvolution of deposited spectra with `scripts/fit_raman.py`.
  - `table` or `text`: copied as printed.
  - `figure_label`: a number printed on a figure.
  - `figure_digitized`: read off a plot.
- `conditions`, `laser_nm`, `notes`: temperature, pressure, doping and annealing. Notes also carry every known caveat.

## How good the numbers are

- **Reviewed rows:** 135 sampled rows were re-checked against the source pages. No peak value was wrong. Five anatase rows had a label or condition problem, and those were fixed. About 400 more calcite values were re-read table by table, with no copy errors.
- **Digitized values:** they reproduce within 0.03 cm⁻¹ on marker plots and within 0.7 cm⁻¹ on curve maxima. They still carry a ±3 cm⁻¹ uncertainty, which is conservative.
- **Uncalibrated raw spectra:** some deposited spectra are offset, and their notes say so:
  - CAL018 reads about 1–2 cm⁻¹ high.
  - CAL030 S4 and S9 read 3–6 cm⁻¹ low.
  - CAL031 S17 reads about 5 cm⁻¹ low.
  - ANA032 reads 3–10 cm⁻¹ low.

## Rows you may want to filter

| Rows | How to find them |
| --- | --- |
| Very high-Mg calcite (up to 49 mol% MgCO3) | CAL012 rows whose `conditions` contain `Mg=` |
| Approximate high-pressure calcite | CAL020, and CAL004 Fig. 2 |
| Data reported twice | CAL005 9.9 mol% vs CAL003 17A; ANA005 vs ANA001. `notes` say "duplicate" or "same data as". |
| Likely typos kept as printed | CAL029 262 (figure says 282), ANA003 540 (likely 519) |
| Literature values, not measurements | ANA031 |
| No paper PDF; data repository only | CAL033, ANA032 |

## Median positions (cm⁻¹), with 10th–90th percentile

| Calcite | n | median | p10–p90 | Anatase | n | median | p10–p90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Eg(T) | 97 | 155.5 | 152.0–161.3 | Eg(1) | 228 | 145.0 | 143.0–150.6 |
| Eg(L) | 156 | 281.6 | 277.0–285.8 | Eg(2) | 66 | 197.5 | 195.5–202.4 |
| nu4 | 155 | 712.5 | 711.0–715.8 | B1g(1) | 84 | 395.0 | 387.7–399.0 |
| nu1 | 185 | 1086.4 | 1085.0–1089.1 | A1g+B1g(2) | 56 | 515.0 | 506.8–519.5 |
| nu3 | 66 | 1436.9 | 1434.0–1439.9 | Eg(3) | 84 | 637.1 | 625.4–640.5 |
| 2nu2 | 61 | 1749.8 | 1747.4–1752.7 | | | | |

Calcite is the held-out test material in this project's train/test split (see the main README). If these calcite rows go into training, the model will have seen calcite before it is tested.
