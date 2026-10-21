# Sequence of execution

Do these steps in order. Each step ends with a concrete deliverable.

Phonopy is unused.

## 1. Make five mode cards

A mode card is a small text file for one material. It lists each Raman peak, the symmetry name of that vibration, the expected peak position, and which peaks are silent.

Use Valency to find one paper per material. Copy the numbers from the paper.

Materials: MoS₂, quartz, calcite, anatase, and the silicon substrate line.

**Done when:** five files exist, and a teammate has checked every number against the paper.

## 2. Build the peak finder

Input is two columns: Raman shift and intensity.

Remove the smooth fluorescence background with pybaselines. Find peak positions with `scipy.signal.find_peaks`. Output is a list of peak positions.

**Done when:** one simple spectrum goes in and a peak list comes out.

## 3. Write the spectrum maker

This script reads a mode card and writes a fake spectrum.

It puts a peak at each card frequency. It moves the MoS₂ peaks the way the Lee paper says they move with layer number. It adds noise, a fluorescence hump, and one laser-plasma line. It then runs the peak finder from step 2.

It saves the peak list and the correct answer for each peak. The correct answer is known because the script created the peak. A plasma line's answer is "artifact."

**Done when:** one command writes hundreds of these files.

## 4. Split the files into train and test

Train:

- Synthetic files from every material except calcite.
- Synthetic files from every laser wavelength except the one you hold out.
- Clean peak lists copied from the Valency papers.

Test:

- Every synthetic file from calcite.
- Every synthetic file from the held-out laser wavelength.
- The MoS₂ peak positions typed from the Lee paper, including the silicon line near 521 cm⁻¹.

RRUFF files are downloaded in step 10. They are test files. They stay out of train.

**Done when:** train and test are in separate folders. Nobody edits the test folder after this step.

## 5. Score Qwen with no training

Send Qwen the mode card and the peak list as plain text. Ask for a JSON list that pairs each peak with one symmetry name or with "artifact."

Run this on the test folder.

Record two numbers:

- The fraction of real peaks given the right symmetry name.
- The fraction of plasma lines and silicon lines marked "artifact."

**Done when:** those two numbers are written down.

## 6. Add the checker

After Qwen answers, a Python script checks the answer.

- One peak gets one label.
- A silent mode cannot be used.
- A peak far from the card frequency cannot take that mode's name.
- A peak on a plasma line or the silicon line is marked "artifact."

If the check fails, send the reason back to Qwen once.

**Done when:** a bad answer is either corrected or left as "unassigned."

## 7. Score again

Run step 5 plus the checker on the same test folder. Record the same two numbers.

**Done when:** the step 5 numbers and the step 7 numbers are side by side.

## 8. Add the layer and strain readout

Use only peaks the checker accepted.

For MoS₂, compute the gap between the out-of-plane peak and the in-plane peak. Read the layer number from the Lee paper's values for 1, 2, 3, 4 layers and bulk.

If both peaks moved the same way from the card positions, report that the sheet is strained. Use the slope copied onto the mode card in step 1.

**Done when:** the test MoS₂ spectra print a layer number.

## 9. Fine-tune only if step 7 is poor

Poor means many real peaks have the wrong symmetry name, or plasma lines are labeled as vibrations.

Upload the train files to Adaption as prompt-and-completion pairs. The prompt is the mode card plus the peak list. The completion is the correct JSON.

Run AutoScientist for one or two rounds. Score the new model on the same test folder, including calcite.

Keep the new model only if both test numbers go up. If they go down, keep the step 7 model.

If step 7 was already good, skip this step.

**Done when:** the model you will demo is chosen, and the test numbers for that model are saved.

## 10. Run one real RRUFF spectrum

Download one quartz Raman file from RRUFF. Run the peak finder, send Qwen the quartz card, and run the checker.

RRUFF does not provide symmetry labels. Compare the result by eye with the quartz paper from step 1.

**Done when:** that spectrum has a saved result.

## 11. Build the screen in marimo

One page.

A person loads a spectrum or picks a built-in example. The page shows:

- The raw curve.
- The removed background.
- The peak list.
- The symmetry name for each peak.
- A saved picture of how the atoms move for that mode.
- "artifact" on plasma and silicon lines.
- The layer or strain sentence.
- The paper citation from the mode card.

Deploy the page on a Hugging Face Space with the marimo template.

**Done when:** another person can open the link and run one example.

## 12. Submit

Record a video under four minutes at normal speaking speed. Show the MoS₂ layer example, then the example with fluorescence and a plasma line, then the quartz file.

Write one page: what the tool does, the two test numbers, the link to the page, and the link to the code.

Submit that page, the video link, and the code link in the hackathon form before 7:00 pm Central on October 22.
