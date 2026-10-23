# PhaseLens

PhaseLens assigns each peak in a Raman spectrum to a symmetry name, or marks it as an instrument artifact. For MoS₂, it then reads a layer number from the peaks a physics checker accepted, and it can draw the atomic motion of a matched mode.

A spectrum is two columns, Raman shift (cm⁻¹) and intensity, plus the laser wavelength. The same peak finder runs on synthetic curves and on measured ones. Every spectrum is sent with that material’s mode card as context, during training and during testing.

## How a spectrum is labeled

1. **Peak finder.** `pybaselines` removes the fluorescence background. `scipy.signal.find_peaks` returns each peak’s position, height, and width.
2. **Mode card.** One JSON file per material: MoS₂, quartz, calcite, anatase, and silicon. A card lists the point group, Raman-active and silent modes, expected positions, instrument lines, and the citation. `spglib` checks a CIF’s point group against the card when a structure is available. The frequencies were taken from papers retrieved with [Valency](https://app.valency.io).
3. **Assignment.** `Qwen/Qwen3.8-27B` (27 billion parameters) reads the card and the peak list and returns JSON. Each peak gets one symmetry name, or `"artifact"`. The prompt is the mode card and the peak list. Temperature is 0.
4. **Checker.** A Python check enforces one label per peak, rejects silent modes, and requires a named mode to sit within 4 cm⁻¹ of that mode on the card. A plasma line must be `"artifact"`. The silicon line must be `"artifact"` unless the sample is silicon. If the check fails, the reason is sent back once. A peak that still fails stays `"unassigned"`.
5. **Layer readout.** For MoS₂, the gap between the in-plane and out-of-plane peaks is matched to the Lee et al. 2010 row for that laser: 1L, 2L, 3L, 4L, or bulk. Only checker-accepted peaks are used.
6. **View.** The marimo page in `app.py` shows the raw curve, the corrected curve, the labels, the layer sentence, the citation, and a phonon picture drawn from saved Materials Project eigenvectors. If a mode cannot be matched, the page says so and does not draw motion.

## Data

Mode cards live in `mode_cards/`. The assignment prompt uses the simplified cards (`mos2.json`, `quartz.json`, `calcite_simplified.json`, `anatase_simplified.json`, `silicon.json`).

`training_data/` holds 500 canonical synthetic spectra. The generator plants a peak at each card frequency, shifts the MoS₂ peaks with layer number using the Lee table, and adds noise, a fluorescence background, one laser-plasma line, and, for MoS₂, a silicon substrate line. The label is known because the generator placed the peak. Plasma and substrate peaks are `"artifact"`.

`scripts/make_split.py` copies those files into the split below. Calcite is the pre-train test material. 632.8 nm is the pre-train test laser, the only laser whose plasma lines are real neon lines. A file that is both is stored once, in test.

| Files | What they are | Split |
| --- | --- | --- |
| 316 | Synthetic spectra that are not calcite and not 632.8 nm | `data/train` |
| 74 | Calcite at the other laser wavelengths | `data/test` |
| 84 | Other materials at 632.8 nm | `data/test` |
| 26 | Calcite at 632.8 nm | `data/test` |

The test set is the union: 184 spectra. Reported scores use that folder. Qwen still receives the mode card for the material being tested.

RRUFF curves and the MoS₂ peak list typed from Lee et al. 2010 can be run through the same peak finder and checker. RRUFF files include a mineral name and a measured curve. Published scores are computed on the 184 synthetic test spectra.

## Model

The base model is [`Qwen/Qwen3.8-27B`](https://huggingface.co/Qwen/Qwen3.8-27B). Zero-shot scoring and LoRA fine-tuning run on [Modal](https://modal.com), one NVIDIA B300.

Fine-tuning is one epoch of LoRA (rank 16, alpha 32) on the 316 training files. The prompt is the mode card plus the peak list. The completion is the gold JSON. The test folder is not used for training. The adapter is kept when both test scores are at least the checker-only scores.

On the 184-file test set:

| Stage | Mode assignment | Artifact identification |
| --- | --- | --- |
| Zero-shot | 96.4% (1001/1038) | 98.5% (193/196) |
| After the checker | 94.2% (978/1038) | 100% (196/196) |
| LoRA, then the same checker | 94.4% (980/1038) | 100% (196/196) |

Score files are written under `outputs/` and are left out of git.

## Requirements

Python 3.12. From the repository root:

```bash
pip install -r requirements.txt
pip install modal
modal setup
```

`modal setup` is only needed for the assignment, checker retry, and fine-tune commands. The demo page and `--prepare-only` do not call Modal.

| Package | Role |
| --- | --- |
| pybaselines | Remove the fluorescence background |
| SciPy | Find peak positions |
| NumPy | Store the shift and intensity columns |
| spglib | Check a CIF point group against the mode card |
| marimo | The spectrum page and the phonon viewer |
| pandas, plotly | Tables and plots on those pages |
| Qwen3.8-27B | Assign each peak, through Modal |
| Valency | Source of the papers behind the mode cards |

## Run it end to end

Run these from the repository root, in order. `training_data/`, `data/train/`, and `data/test/` are already in the repository. The first two commands rebuild them.

```bash
python scripts/spectrum_generator
python -m scripts.make_split
python -m scripts.qwen_zeroshot --prepare-only
python -m scripts.qwen_zeroshot
python -m scripts.run_checker
python -m scripts.score_checked
python -m scripts.layer_readout
python -m scripts.qwen_finetune
```

| Command | What it does |
| --- | --- |
| `python scripts/spectrum_generator` | Writes 500 labeled spectra to `training_data/`. Same seed, same files. |
| `python -m scripts.make_split` | Copies the canonical files into `data/train` (316) and `data/test` (184). |
| `python -m scripts.qwen_zeroshot --prepare-only` | Writes `outputs/step5_prompts.jsonl` on this machine. |
| `python -m scripts.qwen_zeroshot` | Zero-shot Qwen on `data/test`. Writes `outputs/step5_predictions.jsonl` and `outputs/step5_scores.json`. |
| `python -m scripts.run_checker` | Checks every prediction and retries each failure once. Writes `outputs/step6_checked.jsonl`. |
| `python -m scripts.score_checked` | Scores the checked labels next to the zero-shot scores in `outputs/step7_scores.json`. |
| `python -m scripts.layer_readout` | Writes MoS₂ layer calls for the test files. |
| `python -m scripts.qwen_finetune` | LoRA-tunes on `data/train`, then runs the test set through the same checker. Writes `outputs/step9_scores.json`. |

`qwen_finetune` needs `outputs/step7_scores.json` first. A finished step 9 score keeps that command from starting another training run. Pass `--retrain` to train again.

## Open the demo

```bash
marimo run app.py
```

The page opens on a built-in example. A CSV with two columns (shift, intensity) can be uploaded instead. With no model endpoint configured, peaks stay unassigned until a model answer JSON is pasted in. Set `PHASELENS_ASSIGN_URL` to an endpoint that accepts `{"prompt": "..."}` and returns `{"text": "..."}` to call Qwen from the page.

The phonon viewer plays a saved animation:

```bash
marimo run scripts/silicon_phonon_viewer.py
```
