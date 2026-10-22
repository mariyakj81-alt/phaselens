"""Per-paper hand-written fields for anatase/papers_new_A.csv (keyed by final ANA id). Everything else (title, authors, year, journal, DOI, files) is read from fulltext.xml and the folder.
'loc' = phrase used to find the PDF page of the main Raman sentence; '@p' in ev is replaced by 'p.<page>'."""
S = {}
def add(i, laser, sample, ev, loc, table="N", raw="N", notes=""):
    S[f"ANA{i:03d}"] = dict(laser=laser, sample=sample, ev=ev, loc=loc, table=table, raw=raw, notes=notes)

add(34, "532",
    "Anodic TiO2 nanotube layers on Ti (TNT) and cathodically self-doped TNT (SD-TNT, -1.5 V, 450 min) calcined 450/550/650 C for 1 h; confocal Raman imaging of anatase/rutile regions",
    "text @p: anatase Eg 132, Eg 185, B1g 383, A1g+B1g 506 and 626 cm-1 for TNT and SD-TNT calcined at 450 and 550 C (Fig. 3a,b, modes indexed on the spectra); rutile 432 (Eg) and 617 (A1g) at 650 C; Eg(1) (~135 cm-1) deconvolution used for the vacancy estimate",
    "display the five Raman-active modes of anatase at 132",
    notes="Measured positions are well below the usual 144/197/399/513/639 (Eg(1) at 132); the paper does not discuss why. Raman: WITec Alpha300+, 532 nm, 2 cm-1 resolution, 10 s x 30 scans. SI Fig. S1 shows the light/dark regions probed.")
add(35, "514",
    "Fe-decorated anodic TiO2 nanotube arrays modified by pulsed Nd:YAG laser re-solidification (fluence 0-200 mJ/cm2) and calcination",
    "text @p: anatase Eg(1) 144, Eg(2) 196, Bg(1) 395, Ag(1) 515, Eg(3) 634 cm-1 (Fig. 5); Eg(1) position 144.4, 143.8, 146.5, 146.5, 145.8, 144.9 cm-1 for 0, 40, 80, 120, 160, 200 mJ/cm2 (Fig. 5b); rutile 447 and 612 cm-1 appear at higher fluence",
    "five main peaks at 144, 196, 395, 515, and 634",
    notes="Eg(1) position vs laser fluence is given in text with one decimal. Renishaw inVia, 514 nm, 5 mW. Paper labels the modes Bg(1)/Ag(1) (not B1g/A1g).")
add(36, "532",
    "TiO2/Al2O3 nanolaminates (Al-doped TiO2 thin films) grown by plasma-enhanced ALD on p-Si(100); 0, 0.4, 1.2 % Al(P) crystalline (anatase), 1.6 and 3.2 % amorphous",
    "Table 3 @p: Eg 151/152/153, B1g 404/403/405, A1g 527/527/528, Eg 647/647/648 cm-1 (+-1) with FWHM 19-21, 26-31, 26-29, 30-31 cm-1 for 0/0.4/1.2 % Al(P); text quotes A1g 519, B1g 397, Eg 144 and 636 cm-1",
    "Peak Position (cm-1) FWHM (cm-1) Integrated Area", table="Y",
    notes="Fitted (Lorentzian/Voigt) positions in Table 3 are 5-10 cm-1 above the literature values quoted in the text (519/397/144/636), consistent with the oxygen over-abundance discussed in the paper; use Table 3. Excitation 532 nm, <10 mW, resolution <1 cm-1.")
add(37, "325;442;514",
    "Sol-gel Ag-TiO2 nanocoatings spin-coated on glass and annealed at 650 C; Ag enrichment 0, 0.5, 1.5, 2.5 %",
    "Table 4 @p (Fig. 6): Eg(1) 144.49/144.49/143.35/143.04, Eg(2) 197.61/-/196.48/196.17, Bg(1) 398.75/397.66/397.66/396.26, Ag(1) 516.23/516.22/516.23/515.93, Eg(3) 638.20/639.27/639.27/637.92, B2g 794.60/790.44/792.52/797.42 cm-1 for 0/0.5/1.5/2.5 % Ag (with intensities)",
    "143-144, 196-197, and 638-639", table="Y",
    notes="PDF page 1 is the Elsevier COVID-19 resource-centre notice; the article starts on p.2. Renishaw inVia with 325, 442 and 514 nm lasers is stated but the paper does not say which line gave Fig. 6/Table 4. Table 4 also lists unassigned bands at 564-567 and 1095-1098 cm-1.")
add(38, "785",
    "Amorphous TiO2 thin films (5, 32, 64, 100, 200 nm) made by room-temperature ion-plasma assisted e-beam deposition on Si and annealed 250-800 C; crystallization onset vs thickness",
    "text @p: anatase Eg ~141.5 cm-1 (expected position for 785 nm excitation), Eg(2) 194, and 394 and 637 cm-1 (anatase or brookite) for the 200 nm film after 800 C; Fig. 8f gives the Eg peak position vs annealing temperature and thickness (140.5-142.5 cm-1 scatter at 800 C), spectrometer broadening from the Si 520 cm-1 line FWHM 3.46 cm-1",
    "Eg mode at ~141.5",
    notes="Eg(1) position/FWHM vs annealing temperature and film thickness (Fig. 8, SI Fig. S5 raw 200 nm 800 C vs Si substrate). Positions of the weak modes are overlapped by Si substrate bands (460, 618-675 cm-1). Renishaw InVia, 785 nm, 100-200 cm-1 windows.")
add(39, "488",
    "TiO2-Fe3O4 photocatalysts (Fe3O4 wt% series) made by conventional hydrothermal (H_) and microwave (M_) treatment",
    "text @p: anatase Eg 140, Eg 195, B1g 395, B1g+A1g 520, Eg 640 cm-1 for reference H_TiO2/M_TiO2; Fig. 3: position and FWHM of the Eg(143 cm-1) band vs wt% Fe3O4 (no shift for conventional, shift to higher wavenumber and broadening for microwave samples)",
    "five characteristic bands were observed at 140",
    notes="Eg position and FWHM values are in Fig. 3 only (no numeric table); 488 nm Ar-ion laser, Renishaw inVia, deconvolution in WiRE. Magnetite bands (210, 271, 385 cm-1) are in the same spectra.")
add(40, "514",
    "Sol-gel dip-coated TiO2-SiO2 binary coatings on Si annealed 400-900 C",
    "text @p: first broad Eg band ~151 cm-1 after 600 C; at 900 C well-defined Eg ~143 cm-1 plus 197 and 394 cm-1; Fig. 1: Eg shifts from 151 to 143 cm-1 while FWHM decreases from 64 to 14.9 cm-1 with annealing temperature",
    "a well-defined Eg line at ~143",
    notes="Annealing series with Eg position and FWHM (size/phonon-confinement behaviour); the numbers 151/143 and 64/14.9 are in the text, the full curves are in Fig. 1. Jobin-Yvon HR-800, 514 nm, <0.1 mW at the sample, spectral resolution 0.65 cm-1, Si wafer calibration.")
add(41, "532",
    "Sn4+- and Sn2+-doped titania from thermal hydrolysis of Ti peroxo-complexes with SnCl4/SnCl2 (TiSn40x and TiSn20YY series, Sn content and calcination varied)",
    "text @p (Figs. 3, 4): anatase Eg 145, Eg 199, B1g 399, B1g+A1g 515, Eg 638 cm-1 for TiSn401-407; Raman shift of the Eg band 145.3 to 150.6 cm-1 with Sn4+ content; Eg ~147 cm-1 roughly constant in the TiSn2YY series; rutile 147/440/612 and brookite 246/321/364 cm-1 in other samples",
    "specific vibration modes are located at 145 cm",
    notes="Dopant series with Eg shift 145.3-150.6 cm-1 given in text. Thermo DXR microscope, 532 nm, 3-4 mW. Mixed anatase/brookite/rutile samples, only the anatase-dominated ones are relevant.")
add(42, "785",
    "Carbon-containing titania nanopowders (sol-gel, diethanolamine as carbon source) heat treated 300-700 C (TD400-TD700) with commercial anatase and rutile references",
    "text @p (Fig. 4): commercial anatase Eg 143.1 cm-1 (FWHM 14.5), B1g 393.3, A1g+B1g 513.4, Eg 635.3 cm-1; TD400 Eg 148.3 cm-1 (FWHM 18.5, overlapped with brookite A1g 153); TD475-TD600 Eg blue-shifted to 146.8 cm-1 (overlapped with rutile B1g 142.3); Table 1 lists Raman data for anatase and rutile of all samples",
    "curve (a) shows a strong sharp peak", table="Y",
    notes="Size/phase series with Eg position and FWHM and a blue shift attributed to stress/oxygen deficiency. Laser line (785 nm) is given in the Methods; Table 1 combines XRD sizes, Rietveld fractions and Raman data.")
add(43, "532",
    "Ti-Ni-O nanotube arrays on Ti-Ni shape-memory alloy by pulse anodization in glycerol electrolyte, annealed 450-800 C",
    "text @p (Figs. 5, 6): Raman peaks around 146, 244, 288, 406, 437 and 607 cm-1 after 500 C (146 and 406 anatase, 244/437/607 rutile); 147, 406 and 628 cm-1 at 450 C; the 147 cm-1 anatase peak red-shifts and weakens from 450 to 800 C",
    "Raman peaks around 146, 244, 288, 406, 437 and 607",
    notes="Annealing-temperature series (450-800 C); Ni doping moves the anatase bands away from 144/399/639 (paper's own explanation). Bruker Senterra, 532 nm. No SI.")
add(44, "514;530;633;800;850;900",
    "Ag-TiO2 (Ag@TiO2) nanocomposites from Ag and sol-gel anatase nanoparticles (OP4 and two-step samples) and anatase reference nanoparticles for Raman nanothermometry; power- and temperature-dependent Stokes/anti-Stokes spectra",
    "text @p: anatase ~148, 399, 516, 635 cm-1 (and 143 cm-1 Eg normalisation band); Table 2: Eg Raman peak 143.8 (TiO2, 530 nm, from ref. 58), 148.6 (Ag@TiO2, 530 nm, ref. 58), 149.1/149.4/149.7 (Ag@TiO2, 800/850/900 nm), 146.1 cm-1 (TiO2, 800 nm); input-power series at 530 and 633 nm",
    "characteristic peaks of anatase, black line, are found at the frequencies", table="Y",
    notes="Several excitation wavelengths and laser-power/temperature series on one anatase system. The text labels the four anatase peaks as Eg(1), B1g, Ag+Eg, Eg(2), which is not the standard order. Table 2 rows tagged [58] come from the authors' earlier paper. SI PDF (Fig. S2) shows commercial anatase.")
add(45, "532",
    "TiO2 flakes from molten salt hydrates (LiBr/H2O/TTIP) calcined at 400 C; in situ Raman during calcination (2 C/min, Harrick cell) and thermal-stability runs",
    "text @p (Fig. 1): anatase Eg 145, 198, 399, 518, 639 cm-1 after calcination; before calcination the Eg band is at 150 cm-1 and shifts to 155 cm-1 with heating and broadens, 399/518/639 cm-1 shift to lower wavenumbers; 2D-Raman correlation peaks at ~148 and 160 cm-1 (brookite deconvolution of the 145 cm-1 band)",
    "The main band shown in Figure 1a and located at 145",
    notes="Temperature-resolved (in situ heating, 25-600 C) Raman of anatase with deconvolution of anatase/brookite near 145-160 cm-1. HORIBA LabRAM HR Evolution, 532 nm, 80 mW source with 25-50 % filter. SI PDF has the 2D-Raman maps (Fig. S3) and reference spectra (Fig. S2).")
add(46, "633",
    "Ti plates structured by single-step nanosecond laser treatment (1.95 and 2.5 mJ/pulse regimes, P_0.4 and P_0.5 surfaces) forming mixed anatase/rutile oxide layers",
    "text @p and Table 3: anatase Eg 146, B1g 394, A1g 512, Eg 635 cm-1; rutile B1g 141, Eg 244, Eg 442, A1g 610 cm-1",
    "For anatase, vibrational modes were observed at 146", table="Y",
    notes="Raman is a phase check on laser-oxidised Ti (spot and mapping modes, Renishaw inVia, 633 nm); Table 3 repeats the bands quoted in the text. Anatase and rutile coexist.")
add(47, "532",
    "P-, N-, C-doped TiO2 nanoparticles (T3, T5, T7-NPs, waste-valorised synthesis) vs P25 for self-cleaning paints",
    "text @p (Fig. S4 in SI): Eg(1) 144 cm-1 for P25, red-shifted and broadened to ~150 cm-1 for T3-, T5-, T7-NPs; Eg(2) ~196 (P25) and ~200 cm-1 (T7); B1g(1) and Eg(3) of T7-NPs at 390 and 632 cm-1; A1g/B1g(2) of T3-, T5-NPs near 496 cm-1",
    "it displayed a red shift and peak broadening",
    notes="Size/doping dependence of the Eg(1) position and width, numbers in text, spectra in SI Fig. S4. Confocal micro-Raman with 532 nm diode laser. The paper says 'Source data are provided with this paper' but the PMC SI bundle holds only the SI PDF, so no spectra were obtained.")
add(48, "514",
    "Sol-gel Zr-doped TiO2 (0, 1, 3, 5 % Zr) nanopowders and films scratched from FTO (DSSC photoanodes)",
    "text @p: anatase Eg(1) 145, Eg(2) 196, B1g(1) 398, A1g/B1g(2) 519, Eg(3) 639 cm-1; SI Table S2: Eg(1) position, FWHM and phonon lifetime (FTO nanoparticles 144.7/146.3/146.8/146.4 cm-1, FWHM 13.6-20.2; powders 143.5/145.8/146.7/146.4 cm-1)",
    "Intense peaks at about 145, 196, 398, 519, and 639", table="Y",
    notes="Dopant series with tabulated Eg(1) position, FWHM and phonon lifetime in SI Table S2 (Fig. S3 fits). Renishaw inVia, 514 nm.")
add(49, "514.5;532",
    "Pure and Y-N (co)doped sol-gel TiO2 powders and dip-coated thin films on glass beads (2 % Y-N), annealed 400 C",
    "text @p (Fig. 4a,b): dominant Eg 144 cm-1, weak Eg 197 and 638 cm-1, B1g ~395 and A1g+B1g ~517 cm-1; band broadening for Y-N codoped TiO2 (phonon confinement/strain), N doping broadens the 395/517/638 cm-1 peaks of the powders",
    "The dominant Eg observed at 144",
    notes="Powders measured at 532 nm (Horiba SuperHead), thin films at 514.5 nm (JY T64000). Numbers are approximate band positions from the text; widths only qualitative.")
add(50, "514.5",
    "Pristine and N-doped (0.5-4.5 wt% N) triphase (anatase-rutile-brookite) TiO2 nanotubes by anodization, annealed",
    "text @p (Fig. 2): anatase Eg 148, B1g 402, A1g/B1g 515, Eg 630 cm-1 for the as-annealed nanotubes with slight shifts on N doping; rutile Eg ~448 and ~240 cm-1, brookite ~245/322/360 cm-1",
    "Raman modes of anatase phase appear at 148, 402, 515 and 630",
    notes="Dopant series with small shifts; Renishaw inVia, 514.5 nm (the 325 nm He-Cd line was used for photoluminescence only). Brookite and rutile bands present in the same spectra.")
add(51, "",
    "Sol-gel spin-coated pure, Al-, Y- and Gd-doped TiO2 thin films on glass annealed at 500 C",
    "text @p (Figs. 9, 10): pure TiO2 Eg 144.913, B1g 398.918, A1g+B1g 517.139, Eg 636.698 cm-1; 1 wt% Al Eg 144.913, 3 wt% Al 145.723 cm-1; Y-doped (1/4/5 wt%) 144.913/395.864/517.139/636.698 and Gd-doped (2/4/5 wt%) 144.913/395.953/514.128/636.698 cm-1",
    "Raman spectrum of the pure TiO2 at a spectral range of 100", table="N",
    notes="Dopant series quoted to 3 decimals in text (spectral resolution is not stated, so the decimals are over-precise). The paper does not state the Raman instrument or laser line.")
add(52, "",
    "BiOI/TiO2 nanotube arrays (BiOI/TNAs) by SILAR-ultrasonication on anodic TNAs, several SILAR variants",
    "text @p (Fig. 14): TNAs anatase Eg 143.97, B1g 396.8, B1g(A1g) 513.98, Eg 636.45 cm-1; 20-BiOI/TNAs Bi-I 88.27, Eg printed '14 611' (probably 146.11), B1g 397.10, 516.93, Eg 639.19 cm-1",
    "Raman shift of TiO2 anatase, vibration stretching symmetry",
    notes="Positions quoted to 2 decimals for several SILAR variants. HORIBA HR Evolution is named but the excitation line is not stated in the paper. Dryad dataset doi:10.5061/dryad.1vhhmgqx6 (Figure_7-12 csv) needs a login for download (HTTP 401) so it was not downloaded; it does not list the Raman figure.")
add(53, "532",
    "Defective TiO2 from microwave-assisted reduction of P25 with L-ascorbic acid (PAs series) vs parent P25",
    "text @p (Fig. 4a): P25 Eg 141.3, 192.1, 636.3 cm-1, B1g 392.4, A1g 512.2 cm-1; all PAs samples show the five anatase modes with a slight blue shift",
    "P25 sample demonstrated the Raman-active modes of Eg (141.3",
    notes="Decimal positions for P25 and shifts for the reduced samples are in text/Fig. 4; Horiba XploRA PLUS, 532 nm.")
add(54, "514",
    "Reactively dc-magnetron sputtered TiO2 films on Si (amorphous, vacuum-annealed anatase, NH3-annealed N-doped anatase, 600 C) used as supports for Au nanoparticles",
    "text @p: anatase Eg 142.3, B1g 394.4, Eg 634.9 cm-1 after 600 C vacuum/NH3 annealing; NH3-annealed film Eg shifts to 143.0 cm-1 with a larger FWHM; A1g/B1g(2) hidden by the Si 520 cm-1 line",
    "peaks positioned at 142.3, 394.4, and 634.9",
    notes="Film on Si: strong Si lines at ~520 and ~303 cm-1 hide the 513-519 cm-1 anatase band. Horiba LabRam HR, 514 nm. SI PDF is MDPI supplementary data.")
add(55, "785",
    "Solvothermal Ir-decorated TiO2 (Ir-TiO2-A, -B, -C by Ir precursor amount) for visible-light water splitting",
    "text @p (Fig. 1b): blue shift of B1g 395.8, A1g 516.0, Eg 638.9 cm-1 (largest for Ir-TiO2-C); red shift at the 141.4 cm-1 Eg band for all samples",
    "blue shift at 395.8",
    notes="Dopant-series shifts quoted in text only (spectra in Fig. 1b). Horiba confocal Raman, 785 nm. Short Raman paragraph.")
add(56, "532",
    "Phase-selective TiO2 coatings (anatase, rutile, mixed) on additive-manufactured and wrought titanium by direct laser surface modification; commercial anatase/rutile powders as reference",
    "text @p (Fig. 3a): anatase Eg 145, 198, B1g 399, A1g+B1g 516, Eg 638 cm-1; rutile 241, 445, 610 cm-1; mixed-phase samples show both sets",
    "Anatase samples showed clear Raman peaks at 145, 198",
    notes="Raman of laser-grown anatase coatings on Ti (Horiba HR, 532 nm, 10x objective); commercial powder spectra in SI. Peaks are given as one list without assignment per sample.")
add(57, "405",
    "Undoped, Cu-doped and Zn-doped TiO2 anatase nanocrystals (sol-gel, defect-mediated band gap tuning)",
    "text @p (Fig. 2): undoped TiO2 Eg 144, Eg 196, B1g 398, A1g+B1g 520, Eg 640 cm-1; the most intense Eg(1) 144 cm-1 mode blue-shifts and broadens slightly with Cu/Zn doping",
    "Raman spectrum of T-P nanocrystals exhibits peaks",
    notes="Dopant series; 405 nm excitation (Horiba LabRAM HR800, 1800 g/mm) is unusual for anatase (near-resonant). Eg(1) shift values are in Fig. 2(b) only; Rietveld Table 1 gives lattice parameters.")
add(58, "633;785",
    "P25 TiO2 impregnated with Co (0.1, 0.3, 0.5, 1 %) vs undoped P25; 633 and 785 nm Raman at two laser powers each",
    "text @p (Fig. 2, Table 2, Table S1): Eg 143/144/144, 196/198/197, 638/638/637 and B1g 396 cm-1 for P25 (literature)/P25 (this work)/Co(0.1%)/TiO2; at 633 nm and 21 mW the 141 cm-1 band red-shifts by 6 cm-1 and the 517 and 640 cm-1 bands blue-shift by 4-5 cm-1; Table S1 lists the 143 cm-1 peak vs laser line and power",
    "a red shift of 6 cm", table="Y",
    notes="Strongest condition-dependence in the batch: laser-line (633 vs 785 nm) and laser-power effects on position and FWHM of the Eg band, fitted with WITec Project 5.2. Table 2 mixes literature and measured wavenumbers (rows labelled). SI PDF contains Table S1.")
add(59, "514.5",
    "Mixed SiO2/TiO2 (SiTi) catalysts, neat and after H2 reduction (500 C) or low-temperature plasma treatment (defect generation)",
    "text @p: Eg 144 (sharp), 195 (shoulder), 638 cm-1; B1g 397 and A1g+B1g 515 cm-1; plasma treatment broadens the peaks and raises the B1g (397)/Eg ratio",
    "The sharp peak at a wavenumber of 144 cm",
    notes="Positions are approximate band centres from the text (no fit table); the plasma-treatment broadening is qualitative. Renishaw inVia, 514.5 nm. SI PDF is MDPI supplementary data.")
add(60, "532",
    "TiO2 anatase sub-microspheres by flash microwave-assisted solvothermal (FMS) synthesis (acid and precursor concentration series; 300-600 C calcination series)",
    "Table 1 @p: crystallite size 4.3-38.4 nm with Eg(I) 147.9/147.0/144.1/142.5/142.8 cm-1, Eg(I) FWHM 22.9/19.7/16.1/13.6/10.4 cm-1, B1g 392.7-399.0, A1g 514.2-516.8, Eg(III) 640.0/641.7/638.9/637.4/627.3 cm-1 for untreated/300/400/500/600 C; SI Table S2: Eg(I), FWHM, A1g, B1g, Eg(III) vs acid (0.5-2 M) and precursor (20-160 mM) concentration",
    "Table 1 Crystallite size (diameter), principal Raman bands", table="Y",
    notes="Best size-series entry here: Eg(1) position and FWHM against XRD crystallite size and calcination temperature in Table 1; 600 C values marked with * (anatase/rutile overlap). Raman 532 nm; WPPM size analysis in SI.")
add(61, "532",
    "Anatase TiO2 nanosheets with metastable dual vacancies: Thin-VO vs Thick-VO (surface-defect-engineered) photocatalysts for CO2 photomethanation; in situ Raman under CO2/light",
    "text @p (Fig. 2e in text, Fig. 1e in Source Data): anatase peaks at 144, 394, 514 and 636 cm-1 for both samples (Eg, B1g, A1g, Eg); principal Eg peak red-shifted in Thin-VO (144 cm-1) vs Thick-VO (146 cm-1); in situ Raman (Fig. 3d) intensity of the 144 cm-1 peak vs time",
    "Raman characterizations show similar peaks appearing at 144, 394, 514", raw="Y",
    notes="RAW SPECTRA: Source Data xlsx SI/41467_2025_65748_MOESM5_ESM.xlsx sheet 'Figure 1' cols H-J = Raman shift, Thick-Vo, Thin-Vo (1217 points, 51-1400 cm-1, normalised); exported to data/Fig1e_Raman_Thick-Vo_Thin-Vo.csv (maxima 146.35 and 143.92 cm-1). Source Data labels this Fig. 1e while the text calls it Fig. 2e. Sheet 'Figure 3' holds the in situ Raman intensity-vs-time kinetics, not spectra. LabRAM Soleil, 532 nm. SI MOESM2 xlsx holds DFT structure files.")
add(62, "532",
    "Ni4Mo nanoparticles on TiO2 (anatase) supports for alkaline hydrogen oxidation; TiO2, TiO2-H2-400 and Ni4Mo/TiO2",
    "text @p (SI Fig. S13): TiO2 Eg 140, Eg 195, B1g 393, A1g+B1g 511, Eg 635 cm-1; Eg blue-shifts from 140 (TiO2) to 150 cm-1 (Ni4Mo/TiO2) with broadening (compressive strain); no shift for TiO2 treated in H2 at 400 C",
    "Raman spectroscopy study of TiO2 shows six Raman-active modes",
    notes="Metal-support interaction shows up as a 10 cm-1 Eg(1) blue shift. Spectra are only in SI Fig. S13 (MOESM1 pdf); in situ electrochemical Raman used Renishaw Via, 532 nm. SI MOESM2 appears to be the peer-review file.")
add(63, "785",
    "TiO2 layers (~200 nm) by e-beam deposition on Si at room temperature and 227 C, annealed in UHV and in O2 at 850 C",
    "text @p (Fig. 2a): after annealing three new peaks at 142 (Eg(1)), 395 (B1g(1)) and 636 cm-1 (Eg(3)) of anatase; the 514 cm-1 line is anatase A1g+B1g(2) overlapped with the Si wafer",
    "three new peaks are observed at 142, 395, and 636",
    notes="Annealing atmosphere series (UHV vs O2, 850 C); Si wafer lines at 303, 514 and 940-980 cm-1 overlap. 785 nm near-infrared laser. No SI.")
add(64, "532",
    "Nano-size P25 TiO2 heat treated 700-900 C in air (anatase to rutile transformation, oxygen-vacancy shifts)",
    "text @p (Fig. 2): as-received P25 anatase Eg at 148 cm-1 (higher than stoichiometric TiO2); anatase Eg ~145 cm-1 intensity falls with heating temperature but is still visible at 900 C; ~143 cm-1 Eg band shifts to higher wavenumber and ~447 cm-1 rutile Eg to lower wavenumber with increasing vacancy concentration",
    "anatase Eg Raman mode (approx. 145",
    notes="Anatase-to-rutile transition series with vacancy-related Eg shifts (values mostly approximate in text, curves in Fig. 2). RAMANtouch, 532 nm, Si calibration. SI: supplementary docx and review history PDF.")
add(65, "514.5",
    "Fe-doped TiO2 nanoparticles (Fe@TiO2, hydrothermal) with varying Fe doping (structural distortion, hematite at 3 wt% Fe)",
    "text @p (Fig. 2): anatase Eg 144, Eg 196, B1g 392, A1g 520, Eg 638 cm-1; hematite lines 225, 245, 298, 409, 611 cm-1 appear at 3 wt% Fe; Fig. S4b: I410(Fe2O3 Eg)/I144(anatase Eg) ratio",
    "from 144 (Eg), 196 (Eg), 392 (B1g), 520",
    notes="Peaks quoted for the undoped/lightly doped reference; Fe-induced shifts are not tabulated. Horiba LabRAM ARAMIS, 514.5 nm (Methods). SI docx has Fig. S4.")
add(66, "1064",
    "TiO2 nanoparticles peptized with acetic (ace), nitric (nit) and sulfuric (sul) acids, calcined at 500 C; anatase/rutile ratio and size",
    "text @p (Fig. 3): Eg band 141.5 cm-1 for TiO2-ace, shifted to 146 (TiO2-nit) and 150 cm-1 (TiO2-sul) as particle size drops; literature anatase 143/195/395/512/638 and rutile 145/445/611/826 quoted for comparison",
    "TiO2-ace sample exhibited Eg band at 141.5",
    notes="Size series with Eg(1) position; only FT-Raman (Bruker Equinox 55 + FRA106/S, 1064 nm Nd:YAG, 200 mW) in the set. Positions from text and Fig. 3.")
add(67, "532",
    "Hydrolysates of Ti-, Zr- and Ti,Zr-pillaring solutions (lyophilised and calcined 500-800 C): amorphous titania, brookite, anatase, rutile",
    "text @p (Fig. 2): lyophilised Ti-0.1 broad bands ~150, 260, 440, 670, 930 cm-1; brookite 155, 327, 634 cm-1; after 500 C anatase 143, 196, 398, 515, 639 cm-1; at higher temperature rutile 143 (weak), 236, 449, 610 cm-1 (anatase remnants in Ti-0.1-800 raise the 143 cm-1 band)",
    "dominated by the bands at 143, 196, 398, 515 and 639",
    notes="Calcination-temperature series covering amorphous -> brookite -> anatase -> rutile; Thermo DXR, 532 nm, 6 mW, 2 cm-1 resolution. Zr-containing samples have no anatase.")

# --- re-key after ANA046 (Barylyak 2026) was swapped out: old 047..067 -> 046..066, new paper becomes ANA067 ---
_old = dict(S); S.clear()
for _k, _v in _old.items():
    _n = int(_k[3:])
    if _n == 46: continue
    S[f"ANA{(_n - 1 if _n > 46 else _n):03d}"] = _v
add(67, "457;532;633;750;785",
    "Single- and multilayered Ti3C2Tx MXene flakes degraded by increasing laser power density (10 kW/cm2 to ~1.6 MW/cm2) at 457, 532, 633, 750 and 785 nm, forming anatase TiO2 nanoparticles; furnace-oxidised reference at 500 C",
    "text @p: anatase identified by its most intense Eg band at 154 cm-1 (blue-shifted at low power density, attributed to defects/oxygen deficiency) with B1g 406 and Eg 633 cm-1; TiO2 formation at 550 kW/cm2 (633 nm), 330 kW/cm2 (532 nm) and 390 kW/cm2 (457 nm); at 500 C only anatase bands at 154, 406 and 633 cm-1 are observed (Fig. 7A)",
    "The anatase phase was identified by the most intense band at 154",
    notes="Anatase here is a laser- or thermally-induced oxidation product of Ti3C2Tx, so the Eg(1) band is blue-shifted/broadened (154 cm-1) and a MXene band is also listed at 154 cm-1 for fresh flakes (Table 1); identification rests on its growth at 330-550 kW/cm2 and the 406/633 cm-1 companions. Laser-power and excitation-wavelength dependence (resonance Raman at 750/785 nm for the MXene). Only the anatase numbers are relevant.")
