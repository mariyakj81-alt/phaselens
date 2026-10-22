# Sequence of Execution

**1. Make five mode cards.**
A mode card is a small text file for one material. It lists each Raman peak, the symmetry name of that vibration (E′ or A₁′ for MoS₂), the expected peak position, and which peaks are silent. Use Valency to find one paper per material and copy the numbers from the paper. The five materials are MoS₂, quartz, calcite, anatase, and the silicon substrate line. Done when five files exist and a teammate has checked every number against the paper.

**2. Build the peak finder.**
Input is two columns: Raman shift and intensity. Remove the smooth fluorescence background with pybaselines. Find peak positions with scipy. Output is a list of peak positions. Done when you can feed it one simple spectrum and get the peak list back.

**3. Write the spectrum maker.**
This script reads a mode card and writes a fake spectrum. It puts a peak at each card frequency, moves the MoS₂ peaks the way the Lee paper says they move with layer number, adds noise, adds a fluorescence hump, and adds one laser-plasma line. Then it runs the peak finder from step 2. It saves the peak list and the correct answer for each peak. The correct answer is known because the script created the peak. A plasma line’s answer is “artifact.” Done when you can press run and get hundreds of these files.

**4. Split the files into train and test.**
Put most of the fake files in train. Hold out two groups for test: fake spectra from one laser wavelength you left out, and every fake spectrum from one material, such as calcite. Also make a tiny real test: type in the MoS₂ peak positions from the Lee paper, including the silicon line near 521 cm⁻¹. Done when train and test are in separate folders and nobody changes the test folder after this.

**5. Score Qwen with no training.**
Send Qwen the mode card and the peak list as plain text. Ask it to return a JSON list that pairs each peak with one symmetry name or with “artifact.” Run this on the test folder. Score two numbers: the fraction of real peaks given the right symmetry name, and the fraction of plasma and silicon lines marked “artifact.” Done when those two numbers are written down.

**6. Add the checker.**
After Qwen answers, a short Python script checks the answer. One peak gets one label. A silent mode cannot be used. A peak far from the card frequency cannot take that mode’s name. A peak on a plasma line or the silicon line is marked “artifact.” If the check fails, send the reason back to Qwen once. Done when bad answers are either fixed or left as “unassigned.”

**7. Score again.**
Run step 5 plus the checker on the same test folder. Write down the same two numbers. Done when you can compare them with the step 5 numbers.

**8. Add the layer and strain readout.**
Use only peaks the checker accepted. For MoS₂, compute the gap between the out-of-plane peak and the in-plane peak, and read the layer number from the Lee paper’s values for 1, 2, 3, 4 layers and bulk. If both peaks moved the same way from the card positions, report that the sheet is strained and cite the slope you copied in step 1. Done when the test MoS₂ spectra print a layer number.

**9. Fine-tune only if step 7 is poor.**
Poor means many real peaks have the wrong symmetry name, or plasma lines are being called vibrations. Upload the train files to Adaption as prompt-and-completion pairs. The prompt is the mode card plus the peak list. The completion is the correct JSON. Run AutoScientist for one or two rounds. Score the new model on the same test folder. Keep it only if both test numbers go up, including the held-out material. If they go down, keep the step 7 model. If step 7 was already good, skip this step.

**10. Run one real RRUFF spectrum.**
Download one quartz Raman file from RRUFF. Run the peak finder, send Qwen the quartz card, run the checker, and show the labels. This file has no official symmetry labels, so you compare the result by eye with the quartz paper from step 1. Done when that spectrum has a saved result.

**11. Build the screen in marimo.**
One page. A person loads a spectrum or picks a built-in example. The page shows the raw curve, the removed background, the peak list, the symmetry name for each peak, and a saved picture of how the atoms move for that mode. It also shows “artifact” on plasma and silicon lines, the layer or strain sentence, and the paper citation from the mode card. Deploy that page on a Hugging Face Space with the marimo template. Done when someone else can open the link and run one example.

**12. Submit.**
Record a video under four minutes at normal speed. Show the MoS₂ layer example, then the example with fluorescence and a plasma line, then the quartz file. Write one page: what it does, the two test numbers, the link to the page, and the link to the code. Submit that page, the video link, and the code link in the hackathon form before 7:00 pm Central on October 22.
