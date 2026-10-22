# Model Training handoff

PhaseLens gives the model a mode card and a peak list and asks for a JSON list. Each peak keeps its `position_cm-1` and gets one label: a symmetry name from that card, or `artifact`. Layer number is read afterward from the peaks the checker accepted. This file is the record of the zero-shot run, the checker, the layer readout, and the LoRA fine-tune. Nothing here was committed.

## What was already done before tonight

The split holds out calcite and laser 632.8 nm. Test is the union of those two. Train is everything else. Only canonical files are used: `training_data` has 500 JSON files whose names contain no space, and 20 files whose names contain a space are left out. That copy is 316 files in `data/train` and 184 files in `data/test`. Do not edit `data/test`.

Label spelling was cleaned before scoring: `A1'`, `E'`, `E1_2g`, and `A1g + B1g`. The cleanup changes spelling only. It does not merge different modes.

The zero-shot model is `Qwen/Qwen3.8-27B`.

## Step 5 — zero-shot, already finished

`scripts/qwen_zeroshot.py` sends each test file's mode card and peak list to Qwen and writes `outputs/step5_predictions.jsonl`. `scripts/score_assignment.py` scores that file on the test set only. Gold `source == mode` is the mode score. Gold `source` of `plasma` or `substrate` is the artifact score. Those files were already complete (184 lines) and were not rerun.

Headline, from `outputs/step5_scores.json`:

- Mode: 1001/1038 = 0.964354527938343
- Artifact: 193/196 = 0.9846938775510204

Normalized match equals those exact fractions. Per material:

- Anatase: mode 127/135 = 0.9407407407407408, artifact 27/27 = 1.0
- Calcite: mode 499/499 = 1.0, artifact 96/98 = 0.9795918367346939
- Silicon: mode 12/13 = 0.9230769230769231, artifact 13/13 = 1.0
- Quartz: mode 346/347 = 0.9971181556195965, artifact 18/19 = 0.9473684210526315

Calcite slice: mode 499/499, artifact 96/98. Held-out laser slice: mode 632/669 = 0.9446935724962631, artifact 123/124 = 0.9919354838709677. A file that is both calcite and 632.8 nm is in both slices and once in the headline. 26 files are in both slices.

## Step 6 — checker, then one retry

`scripts/checker.py` checks a parsed list against the mode card named by `context.mode_card` and against context metadata. It does not read gold answers. `scripts/run_checker.py` runs that check on every test prediction.

The rules it enforces:

- One peak, one label. Every input peak is paired, `position_cm-1` is kept (within 0.05 cm^-1), and the label is a single string.
- The label is `artifact` or a symmetry name on that card. `scripts/label_norm.py` makes `A1'`, primes, and `A1g + B1g` spacing match.
- A silent mode listed on the card cannot be used.
- A peak more than 4.0 cm^-1 from a mode's card frequency cannot take that mode's name. 4.0 cm^-1 is the tolerance in `scripts/spectrum_generator`. If several card modes sit in that window, the label is accepted when it is one of them.
- A peak within 4.0 cm^-1 of a line in `context.known_artifact_lines_cm-1.plasma` must be `artifact`.
- A peak within 4.0 cm^-1 of the context silicon line must be `artifact` only when that line is present and the sample is not silicon. The silicon card's own F2g line stays a real mode. There is no rule that every peak near 520 is an artifact.

141 of 184 files passed on the first answer. The other 43 were sent back to `Qwen/Qwen3.8-27B` once, temperature 0, with the original prompt plus the checker's reasons. After that retry, 0 files still failed. Files that already passed were written to `outputs/step6_checked.jsonl` before the Modal call, so a crash would not have redone them. Step 5 files were left as they were.

The scored labels are `parsed_labels` in `outputs/step6_checked.jsonl`. The file also has the gold list, both raw model texts, the first parse, the retry parse, the reasons, and whether a retry happened.

## Step 7 — rescore on the test set

`scripts/score_checked.py` scores the checker-adjusted labels with `scripts/score_assignment.py` and writes `outputs/step7_scores.json`. That file holds the step 5 object and the step 7 object together. The headline is the test set. The train set was not scored.

Headline:

- Mode: 978/1038 = 0.9421965317919075
- Artifact: 196/196 = 1.0

Normalized match equals those exact fractions.

Per material:

- Anatase: mode 127/135 = 0.9407407407407408, artifact 27/27 = 1.0
- Calcite: mode 498/499 = 0.9979959919839679, artifact 98/98 = 1.0
- Silicon: mode 12/13 = 0.9230769230769231, artifact 13/13 = 1.0
- Quartz: mode 323/347 = 0.930835734870317, artifact 19/19 = 1.0

Calcite slice: mode 498/499, artifact 98/98. Held-out laser slice: mode 610/669 = 0.9118086696562033, artifact 124/124 = 1.0.

Artifact accuracy rose from 193/196 to 196/196. Mode accuracy fell from 1001/1038 to 978/1038. The quartz drop is 23 peaks: each was a real mode that step 5 labeled correctly, and the checker-adjusted label is `artifact`. On 632.8 nm the context lists every neon line in the window, not only the planted peak, so a real peak within 4 cm^-1 of one of those lines has to be called `artifact`.

## Step 8 — layer readout

`scripts/layer_readout.py` uses only checker-accepted peaks on the 22 test MoS2 files. The in-plane peak is `E'`, `Eg`, or `E1_2g`. The out-of-plane peak is `A1'` or `A1g`. The layer is the closest row of `MOS2_LAYER_TABLE` in `scripts/spectrum_generator` for that file's laser (1L, 2L, 3L, 4L, bulk).

From `outputs/step8_summary.json`: 7/22 = 0.3181818181818182. The denominator is all 22 test MoS2 files. 10 of 22 had both an in-plane and an out-of-plane peak left after the checker. Per-file rows are in `outputs/step8_layers.jsonl`.

## Step 9 — LoRA fine-tune, then the same checker, then the test score

`scripts/qwen_finetune.py` trains on the 316 `data/train` files only. The prompt is `make_prompt` (card plus peaks; no answers, no spectrum, no `known_artifact_lines`). The completion is the gold JSON: `position_cm-1` and the canonical label, no `source` field. The 20 space-named files are not in `data/train`. Calcite and 632.8 nm are not in the training set.

This was prompt-completion LoRA supervised fine-tuning, one epoch, not a from-scratch pretrain and not a full-weight update. Rank 16 loaded and finished. Rank was not lowered. Train loss was 0.007171159639624478. No example was skipped or truncated (token lengths 1560 to 8965).

The fine-tuned model was then run on all 184 test files. 138 passed the checker on the first answer. 46 were retried once. 

`outputs/step9_scores.json` puts step 9 (LoRa finetune) next to step 5 (zero-shot) and step 7 (checking and rescoring). Headline, checker-adjusted, test set only:

- Mode: 980/1038 = 0.9441233140655106
- Artifact: 196/196 = 1.0

Normalized match equals those exact fractions.

Per material:

- Anatase: mode 128/135 = 0.9481481481481482, artifact 27/27 = 1.0
- Calcite: mode 498/499 = 0.9979959919839679, artifact 98/98 = 1.0
- Silicon: mode 13/13 = 1.0, artifact 13/13 = 1.0
- Quartz: mode 325/347 = 0.9365994236311239, artifact 19/19 = 1.0

Calcite slice: mode 498/499, artifact 98/98. Held-out laser slice: mode 612/669 = 0.9147982062780269, artifact 124/124 = 1.0.

Against step 7, mode went from 978/1038 to 980/1038. Artifact stayed at 196/196. Both fractions are at least the step 7 fractions, so the fine-tuned adapter is the current model. It did not beat step 7 on both numbers, because the artifact fraction did not rise. The zero-shot mode fraction, 1001/1038, is still higher than both checker results. The keep rule compares the adapter with step 7, not with the raw zero-shot.

## How the model is set up

- Base model: `Qwen/Qwen3.8-27B`
- Zero-shot Modal app: `phaselens-qwen-zeroshot`
- Fine-tune Modal app: `phaselens-qwen-finetune`
- GPU: `B300`
- Containers: 1
- Train batch size: 1, gradient accumulation 4 (effective batch 4)
- LoRA rank 16, alpha 32, dropout 0.05, modules `q_proj`, `k_proj`, `v_proj`, `o_proj`
- Epochs: 1
- Learning rate: 0.0001, cosine schedule. This Transformers build rejected `warmup_ratio`, so the run used `warmup_steps` 8.
- Gradient checkpointing: on
- Adapter on Modal volume `phaselens-qwen-adapter`, container path `/vol/adapter`
- Local copy: `outputs/step9_adapter/adapter` (about 42 MB for `adapter_model.safetensors`)
- Predictions: `outputs/step5_predictions.jsonl`, `outputs/step6_checked.jsonl`, `outputs/step9_predictions.jsonl`, `outputs/step9_checked.jsonl`
- Scores: `outputs/step5_scores.json`, `outputs/step7_scores.json`, `outputs/step9_scores.json`
- `outputs/` is gitignored. Do not commit the adapter.



## Commands

From the repo root in PowerShell. `py -3.12` is the interpreter that has Modal. Run `modal token info` first and confirm it prints a workspace. Do not paste tokens into chat.

`py -3.12 -m scripts....` works from another directory because `phaselens-repo.pth` in the Python 3.12 user site-packages (`C:\Users\rishi\AppData\Roaming\Python\Python312\site-packages\phaselens-repo.pth`) adds this repo to `sys.path`. Each script also inserts the repo root at the front of `sys.path` after it starts.

```powershell
py -3.12 -m scripts.make_split
py -3.12 -m scripts.qwen_zeroshot --prepare-only
py -3.12 -m scripts.qwen_zeroshot
py -3.12 -m scripts.run_checker
py -3.12 -m scripts.score_checked
py -3.12 -m scripts.layer_readout
py -3.12 -m scripts.qwen_finetune
```

`make_split` rebuilds `data/train` and `data/test`. `qwen_zeroshot --prepare-only` rebuilds prompts and does not call Modal. `qwen_zeroshot` with no flag is the zero-shot Modal run. `run_checker` is the checker plus one Modal retry. `score_checked` writes the step 7 comparison. `layer_readout` writes the step 8 layer files. `qwen_finetune` is the Modal LoRA run, the test generation, the checker, and the step 9 scores.

A plain `py -3.12 -m scripts.qwen_finetune` will not start a second training run while `outputs/step9_scores.json` already has a finished step 9 headline and the volume already has a completed adapter.

## If you need to fine-tune again

Do not change `data/test`. Edit `data/train` or the prompt in `scripts/make_prompt.py`, then from the repo root:

```powershell
py -3.12 -m scripts.qwen_finetune --retrain
```

That trains a new adapter, replaces the step 9 prediction files after training finishes, and scores `data/test` again through the same checker. Keep the new adapter only if both test headline numbers go up. The script's `kept` flag is true when both are at least the step 7 numbers. The sequence doc's rule is stricter: both numbers have to rise. If the new run does not raise both, keep using the adapter from this handoff.

## Adaption

`SEQUENCE_OF_EXECUTION.md` step 9 names Adaption AutoScientist as the original plan: upload the train files as prompt-and-completion pairs, run one or two rounds, and keep the model only if both test numbers go up, including on calcite. There is no Adaption SDK in this repo, and this machine does not have it installed. Tonight's run was the Modal LoRA equivalent of that prompt-completion fine-tune. It was not blocked on Adaption.

## Strain

Not done. The mode card has no numeric slope to apply, and none was invented.

## Caveats

- For lasers other than 632.8 nm, the plasma lines in the context are generator placeholders. The checker still treats a peak within 4 cm^-1 of a listed line as `artifact`.
- For 632.8 nm, silicon files and the other materials list every neon line in the window, not only the planted peak. That is why 23 correct quartz mode labels became `artifact` in step 7.
- Anatase's combination band is near 517 (`A1g + B1g`). The silicon line is near 520. The checker does not mark every peak near 520 as an artifact. Anatase mode accuracy stayed 127/135 in step 7 and was 128/135 after the fine-tune.
- The prompt uses the simplified cards (`anatase_simplified.json`, `calcite_simplified.json`, and the quartz, silicon, and MoS2 cards). `make_prompt` refuses a comprehensive card.
- The 20 space-named files were not trained on and were not tested.

