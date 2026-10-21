# Architecture

A measured Raman spectrum goes in. Each peak comes out with a symmetry name, or with the label "artifact." Layer number and strain are calculated from the accepted names.

## Pieces, in the order data moves

### 1. Spectrum in

Every spectrum is two columns: Raman shift and intensity. It also has a laser wavelength.

Three kinds of file enter here:

- Fake spectra written by the spectrum generator.
- Clean peak lists copied from papers found with Valency.
- RRUFF files, and the MoS₂ positions typed from Lee et al. 2010.

Which of these are train and which are test is fixed in the README.

### 2. Peak finder

pybaselines removes the smooth fluorescence background. `scipy.signal.find_peaks` returns the peak positions. The output is a peak list: position, height, and width.

The same peak finder runs on generated spectra and on real spectra.

### 3. Mode card

One JSON file per material. Five materials: MoS₂, quartz, calcite, anatase, and the silicon substrate line.

Each card contains:

- The point group.
- Each Raman-active vibration: symmetry name, a one-line description of the atomic motion, and the expected peak position.
- Vibrations that are silent for this measurement.
- Instrument lines for the laser wavelength, and the silicon line near 521 cm⁻¹.

spglib checks a CIF when we have one. The check is that the crystal's point group is the point group written on the card.

For MoS₂, monolayer labels are E′ and A₁′ (point group D3h). Bulk labels for the same motions are E2g and A1g (point group D6h). The card stores both.

Valency is used while writing the card. It finds the paper. A person copies the frequencies from the paper onto the card and saves the citation.

### 4. Assignment

Qwen receives plain text: the mode card and the peak list. It returns JSON. Each peak is paired with one symmetry name, or with "artifact."

### 5. Checker

A Python script checks Qwen's JSON.

- One peak gets one label.
- A silent mode cannot be used.
- A peak far from the card frequency cannot take that mode's name.
- A peak that sits on a plasma line or the silicon line is "artifact."

If a check fails, Qwen gets the reason once and answers again. A peak that still fails stays "unassigned."

### 6. Readout

Python computes this from peaks the checker accepted.

- **Layers.** The gap between the MoS₂ out-of-plane peak and the in-plane peak is compared with the Lee et al. 2010 values for 1, 2, 3, 4 layers and bulk.
- **Strain.** If both accepted peaks moved the same way from the card positions, report that, using the slope copied onto the mode card.

### 7. Screen

A marimo page shows the raw curve, the removed background, the peak list, the symmetry name, a saved drawing of the atomic motion, any "artifact" labels, the layer or strain sentence, and the paper citation. The page is hosted on a Hugging Face Space.

## Train path

The spectrum generator reads a mode card and writes a fake curve. It places a peak at each card frequency, moves the MoS₂ peaks the way the Lee paper says they move with layer number, adds noise, adds a fluorescence hump, and adds one laser-plasma line. The peak finder from piece 2 turns that curve into a peak list. The label for each peak is known because the script placed the peak. A plasma line is labeled "artifact."

Those files, minus the held-out material and the held-out laser, plus the clean peak lists from the Valency papers, are the training data. Adaption AutoScientist fine-tunes Qwen on them only after a zero-shot test score is recorded and that score is poor.

## Test path

The test folder holds:

- Every synthetic file from the held-out material.
- Every synthetic file from the held-out laser wavelength.
- RRUFF files.
- The typed Lee et al. 2010 MoS₂ peak list.

Qwen still receives the mode card for the material being tested. The card is context. The spectrum is the test item.
