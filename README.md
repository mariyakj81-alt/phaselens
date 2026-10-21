# Raman mode assignment

This project assigns each peak in a Raman spectrum to a symmetry name, then reads layer number or strain from those assignments.

Read these two docs before writing code:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [SEQUENCE_OF_EXECUTION.md](SEQUENCE_OF_EXECUTION.md)

## Data: what goes where

A **mode card** is a small text file for one material. It lists each allowed vibration, its symmetry name, and its expected peak position. Qwen receives the mode card as context for every spectrum, in training and in testing. The mode card is not the dataset split.

Papers found with **Valency** are the source of the mode card numbers. Copy the published peak positions out of those papers. Those copied peak lists are clean training examples.

| Data | Source | Split |
| --- | --- | --- |
| Synthetic spectra from every material and laser except the held-out ones | Spectrum generator, then the peak finder | **Train** |
| Clean peak lists copied from the Valency papers | The five papers used to write the mode cards | **Train** |
| Synthetic spectra from one held-out material (calcite) | Same generator | **Test** |
| Synthetic spectra from one held-out laser wavelength | Same generator | **Test** |
| RRUFF Raman files | [RRUFF](https://rruff.info) downloads | **Test** |
| MoS₂ peak positions typed from Lee et al. 2010, including the silicon line near 521 cm⁻¹ | The Lee paper | **Test** |

RRUFF files have a mineral name and a measured curve. They do not have symmetry-name labels. Use them as real inputs and compare the output by eye to the paper for that mineral.

After the train/test split, leave the test folder unchanged.

## Libraries

Install the Python packages with:

```bash
pip install -r requirements.txt
```

| Library | Import / package name | Job in this project |
| --- | --- | --- |
| pybaselines | `pybaselines` | Remove the smooth fluorescence background from a spectrum |
| SciPy | `scipy.signal.find_peaks` | Turn the cleaned curve into a list of peak positions |
| NumPy | `numpy` | Store the shift and intensity columns |
| spglib | `spglib` | Read a crystal structure and check that its point group matches the mode card |
| marimo | `marimo` | The demo page: spectrum in, labeled peaks out |
| Qwen | Hugging Face model weights, called in the assignment step | Read the mode card plus the peak list and return a JSON label for each peak |
| Valency | [app.valency.io](https://app.valency.io) | Find the paper for each mode card and keep the citation |
| Adaption AutoScientist | [docs.adaptionlabs.ai](https://docs.adaptionlabs.ai/autoscientist/overview/) | Fine-tune Qwen on the train files, only if the zero-shot test score is poor |
| Hugging Face Spaces | marimo Space template | Host the demo page |

Phonopy is not part of this build.
