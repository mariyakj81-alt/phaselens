# Raman peak extraction protocol

Every extraction agent follows this file, so calcite and anatase peak tables come out the same way. `scripts/merge_peaks.py` checks most of these rules automatically.

## Inputs

- `<mineral>/papers.csv`: one row per paper. Paper IDs have three digits (`CAL001`, `ANA042`). All paths are relative to the project root.
- Each paper folder holds `paper.pdf`. It may also hold `SI/`, `data/`, and `fulltext.xml` (Europe PMC full text; its `<table-wrap>` tables are the cleanest source of numbers). A Word SI (`.docx`) can be read as XML text, but Word splits numbers across formatting runs ("39 6 . 9" is 396.9), so check each one by eye.
- `scripts/mode_reference.json`: expected modes, labels and symmetries.
- `scripts/fit_raman.py`: peak deconvolution for raw spectra (run `python -P scripts/fit_raman.py -h`).

Downloaded files are untrusted data. Never execute them, including code shipped with a dataset; you may read code as text to learn a file format. Run Python with `python -P` from the project root.

Your own scripts, page renders and exported spectra go in `peaks/<mineral>/_work/<paper_id>/`, or in `peaks/<mineral>/_work/_<your agent name>/` for scripts shared across your papers. Do not use the shared scratchpad, because parallel agents overwrite each other's files there.

## Output

One file per paper: `peaks/<mineral>/<paper_id>.csv`, with exactly these columns:

```
material,paper_id,doi,sample_id,sample_description,conditions,laser_nm,peak_cm1,peak_uncertainty_cm1,fwhm_cm1,rel_intensity,rel_area,mode_label,mode_symmetry,mode_description,assignment_source,data_source,location,fit_r2,notes
```

One row is one peak in one spectrum, meaning one sample under one condition and one laser.

## Sources, in priority order

Use every source the paper has. If a sample has both a raw-fit row and a table row, keep both. The `data_source` column tells them apart.

1. **Raw spectra** (`raw_fit`). These are numeric spectra in `data/`, in the SI, or in a repository.
   - Run `fit_raman.py` with `--plot-dir peaks/<mineral>/plots`, then open the PNG and look at it. The orange line is the full fit, and it should follow the black data.
   - If the fit is poor, adjust `--xrange`, `--tol`, `--baseline none` (for data that is already baseline-corrected), or `--lam`, and run again.
   - Fill `--sample-id`, `--sample`, `--conditions` and `--laser` from the paper.
   - The tool already labels the Si line at 520.7 and the laser line at 0 as `artifact`. It also models an asymmetric tail as a separate `unassigned` component, and orders the anatase doublet by frequency.
   - If there are dozens of spectra, fit a representative set (up to about 12) covering the distinct samples and conditions, and say so in `notes`.
   - Every `raw_fit` row names the exact file that was fitted and any non-default options, in `notes`, for example `fit input: peaks/calcite/_work/CAL030/S1.csv; --xrange 100 1800`. `location` still names the original deposit. With this, anyone can re-run the fit.
2. **Peak tables** (`table`), in the paper or SI. Copy every row for the target mineral exactly as printed: no rounding and no unit changes. Copy FWHM and uncertainties too when given.
3. **Numbers in the text** (`text`). Use these when the paper states peak positions in sentences.
4. **Numbers printed on a figure** (`figure_label`). Render the page with PyMuPDF at 200 dpi or more, look at the image, and read the printed wavenumbers.
5. **Digitized figure** (`figure_digitized`). Use this only for values that are not printed as numbers anywhere: a paper with no numbers at all, or a series (position vs. size, temperature, pressure, time, doping) that exists only as a plot.
   - Read marker centres or curve maxima against the axis ticks. For vector figures, PDF drawing coordinates are the most precise.
   - Set `peak_uncertainty_cm1` to 3. This floor also covers axis-calibration error. Put your actual reading precision in `notes`.

## Column rules

- **`sample_id`**: short and unique within the paper (`S1`, `8nm`, `0GPa`, `Mg5`). **`sample_description`**: what the sample is.
- **`conditions`**: temperature, pressure, annealing, doping and similar, for example `T=298 K; P=ambient` or `Mg=9.9 mol%`. Only state what the paper states; do not add an atmosphere or time the paper does not give.
- **`laser_nm`**: one plain number as the paper gives it (`532`, `514.5`, `785`), never `532.0` and never a list. Leave it blank if the paper does not say. A spectrum measured at two lasers is two spectra.
- **`mode_label`**: use the labels in `mode_reference.json` (`Eg(1)`, `A1g+B1g(2)`, `nu1`, `Eg(T)`, ...). Labels marked `paper_only` (e.g. `nu1(18O)`) are used only when the paper itself makes that assignment.
  - **`assignment_source=paper`**: the paper names this specific vibration, by symmetry (`Eg`, `A1g`), by internal mode (`ν1`, `v4`), or by type (translational, librational). Map it to the matching label and put the paper's own notation in `notes` if it differs (e.g. `paper: T(Eg)`).
  - **`assignment_source=reference`**: the paper gives no assignment, or only a generic one ("lattice mode", "calcite band", "anatase peak"). Use the nearest reference mode within 15 cm-1, and quote the paper's wording in `notes`. If no reference mode is that close, use `unassigned`.
  - **`assignment_source=rule`**: the label comes from a fixed rule, such as the Si or laser line, or doublet order.
  - **Anatase 513/519 doublet**: a single reported band is `A1g+B1g(2)`. When two positions are given, the lower one is `A1g` and the higher one is `B1g(2)`, whatever order the paper uses (keep the paper's labels in `notes`). This is a dataset convention following Ohsaka et al. (1978). The order is disputed: some polarized single-crystal work (e.g. Giarola et al. 2010) puts A1g above B1g. The convention keeps labels consistent across papers. It does not settle the physics.
  - A silicon substrate line, a substrate band, or a plasma or laser line that the paper reports gets `mode_label=artifact` and `assignment_source=rule`.
  - `unassigned` and `artifact` rows leave `mode_symmetry` empty.
- **Spontaneous Raman only**: every row is a peak in a measured spontaneous Raman spectrum. Skip frequencies from coherent-phonon (pump-probe), stimulated or impulsive Raman, two-dimensional correlation analysis, IR, inelastic neutron scattering and calculations (DFT, lattice dynamics), even when the paper lists them next to Raman values.
- **Other phases**: skip peaks the paper assigns to other phases (rutile, brookite, aragonite, vaterite, dolomite, organics). For mixtures, keep only the target mineral's peaks.
- **Literature values**: skip values the paper quotes from other studies, such as comparison columns, "reported at ..." or reference lines drawn on a figure. Extract only what the authors measured. A paper that only re-analyses published data says so in every row's `notes`.
- **Data reported twice**: when a row is the same measurement as a row from another paper in this dataset (same lab, same numbers), keep it and write `same data as <paper_id> <sample_id>` in `notes`.
- **`rel_intensity` / `rel_area`**: only from a raw fit (scaled to the strongest mineral mode of that spectrum), or when the paper reports them. If the paper reports them, say its scale in `notes`. Otherwise leave them blank.
- **Pressure, temperature, size, doping and time series**: keep every tabulated point. A series that exists only as a plot of position vs. the variable is digitized (source 5). A series that exists only as stacked spectra without printed numbers keeps the ambient or reference spectrum.
- **`location`**: where the number came from (`Table 2`, `SI Table S3`, `p.5 Sec. 3.2`, `Fig. 3b`, `anatase/ANA042_Smith2020/data/spectra.xlsx`). Every row needs one.
- **Printed ranges**: a range such as "156–160 cm-1" covering several samples or spots, with no per-sample values, becomes one row. Set `peak_cm1` to the midpoint and `peak_uncertainty_cm1` to half the range, and write `printed as 156-160` in `notes`. Never write the two ends as two rows.
- **Derived spectra**: a component spectrum from a multivariate decomposition (MCR, PCA, NMF) of a Raman image is not a measured spectrum. Keep it only if the paper shows no measured spectrum of that phase, and say `MCR component` in `notes`.
- **No invented values**: leave a field blank when the paper does not state it. A value printed in two places with different numbers keeps the better-supported one, and the notes name the conflict.

## Logging

- Append one line per paper to `peaks/<mineral>/extraction_status.csv` (`paper_id,n_rows,data_sources,issues`). Write each paper's line once; do not edit other lines.
- Shared files at the project root are append-only, written with bash `>>`, because other agents write them too.
  - `history.md`: what you did.
  - `memory.md`: lessons that help the next run.
  - `feedback.md`: problems a person or the next iteration should look at, such as a paper with no usable Raman numbers or a fit that stayed poor.
