# Manifest for mos2/, quartz/, silicon/ papers.csv and candidates_rejected.csv.
# Paths are relative to the project root. laser_nm values are joined by ';'.

PAPERS = []
REJECTED = []


def paper(**k):
    PAPERS.append(k)


def rej(material, doi, title, reason):
    REJECTED.append(dict(material=material, doi=doi, title=title, reason=reason))


# ---------------------------------------------------------------- MoS2
paper(
    material="mos2", paper_id="MOS001", folder="mos2/MOS001_Lee2010", doi="10.1021/nn1003937",
    title="Anomalous Lattice Vibrations of Single- and Few-Layer MoS2",
    first_author="Changgu Lee", year="2010", journal="ACS Nano", open_access="Y",
    raman_evidence=("Fig. 2b (PDF p.11, plot only, no table): E2g1 and A1g frequencies and their difference vs "
                    "thickness for 1-6 layers and bulk; p.3 text: 1L E2g1 at ~384 cm-1 and the 1L frequency "
                    "difference is ~3 cm-1 smaller than the 2L value; Fig. 2a spectra 1L-6L and bulk (360-430 cm-1); "
                    "Fig. 3b (p.12) linewidths (p.5 text: E2g1 ~2.1 cm-1 independent of thickness, A1g 3 -> 6 cm-1 "
                    "for 6L -> 2L); Fig. 4b (p.13) supported vs suspended 1L-4L; p.6 Methods: the Si Raman band at "
                    "520 cm-1 was used as internal frequency reference"),
    laser_nm="514.5;532",
    sample_description=("Mechanically exfoliated 1-6 layer and bulk 2H-MoS2 (natural molybdenite) on 285 nm SiO2/Si, "
                        "layer number from contact-mode AFM; suspended 1L-4L over 1-1.5 um holes; ambient, backscattering"),
    peak_table="N", raw_data="N", pdf_status="downloaded",
    source_urls="https://doi.org/10.1021/nn1003937;https://arxiv.org/abs/1005.2509;https://arxiv.org/pdf/1005.2509",
    found_via="WebSearch",
    notes=("paper.pdf is the arXiv v1 preprint (arXiv:1005.2509, 14 May 2010; 14 pages, same title without the hyphen), "
           "not the ACS version of record. The ACS article and its Supporting Information (freestanding vs supported "
           "linewidths) are behind the ACS paywall: needs_manual if the published version is required. Frequencies exist only as "
           "plotted markers in Fig. 2b: pixel reading of the embedded image (axis ticks as scale), +/-0.2 cm-1, digitize again before use: "
           "E2g1 1L ~384.3, 2L ~383.2, 3L ~382.7, 4L ~382.3, 5L ~382.3, 6L ~382.2, bulk ~382.0; A1g 1L ~403.0, 2L ~404.8, "
           "3L ~405.8, 4L ~406.7, 5L ~406.9, 6L ~407.0, bulk ~407.4; difference (red markers) 1L ~18.9, 2L ~21.6, 3L ~23.3, "
           "4L ~24.2, 5L ~24.6, 6L ~24.8, bulk ~25.3 cm-1. 514.5 nm for Figs. 2-3 (supported on "
           "SiO2/Si), 532 nm for the suspended samples (Fig. 4). OSTI records 1168183 and 1384202 exist (DOE funding) but hold no full text."),
)
paper(
    material="mos2", paper_id="MOS002", folder="mos2/MOS002_Lloyd2016", doi="10.1021/acs.nanolett.6b02615",
    title="Band Gap Engineering with Ultralarge Biaxial Strains in Suspended Monolayer MoS2",
    first_author="David Lloyd", year="2016", journal="Nano Letters", open_access="Y",
    raman_evidence=("SI Table S1 (PDF p.24): E2g1 / A1g Raman shift rates under biaxial strain in cm-1 per %: monolayer "
                    "-5.2 / -1.7, bilayer -4.2 / -1.3, trilayer -3.0 / -0.7; main text (PDF p.8): unstrained E2g1 at 385 "
                    "and A1g at 405 cm-1, shift rates -5.2 (E2g1) and -1.7 (A1g) cm-1/%, Grueneisen parameters 0.68 "
                    "(E2g1) and 0.21 (A1g); SI p.23: mode separation ~19 cm-1 (1L), 21.7 (2L), 23.7 (3L); Fig. 2c strain "
                    "dependence of both peaks; both modes soften"),
    laser_nm="532",
    sample_description=("CVD-grown (and exfoliated) monolayer, bilayer and trilayer MoS2 membranes suspended over 8 um "
                        "holes in SiOx/Si, biaxial strain from a pressure difference across the membrane, 0 to 5.6 %"),
    peak_table="Y", raw_data="N", pdf_status="downloaded",
    source_urls=("https://doi.org/10.1021/acs.nanolett.6b02615;https://arxiv.org/abs/1608.04264;"
                 "https://open.bu.edu/items/11aefc07-09f9-4dc9-a672-a54a35d616bd;"
                 "https://open.bu.edu/bitstreams/5bf70f43-d3ef-44c4-a5f9-ce12c363390c/download"),
    found_via="WebSearch",
    notes=("paper.pdf is the Boston University OpenBU author copy (35 pages = 1 repository cover page + main text + SI; "
           "same text as arXiv:1608.04264). Strain is biaxial, so both peaks shift in the same direction (the readout "
           "case in ARCHITECTURE.md). The ACS Nano-Letters correction Nano Lett. 2019, 19, 7548 (doi "
           "10.1021/acs.nanolett.9b03591) exists; its content could not be read (ACS blocked), so check whether it changes "
           "the strain scale before copying the slopes."),
)
paper(
    material="mos2", paper_id="MOS003", folder="mos2/MOS003_Conley2013", doi="10.1021/nl4014748",
    title="Bandgap Engineering of Strained Monolayer and Bilayer MoS2",
    first_author="Hiram J. Conley", year="2013", journal="Nano Letters", open_access="Y",
    raman_evidence=("PDF p.4 text: unstrained monolayer A'1 (out-of-plane) at 403 cm-1 and E' (in-plane) at 384 cm-1; "
                    "uniaxial tensile strain 0-2.2 %: A' shows no measurable shift, E' splits into E'+ and E'-; E'- shifts by "
                    "4.5 +/- 0.3 cm-1/% (1L) and 4.6 +/- 0.4 (2L), E'+ by 1.0 +/- 1 (1L) and 1.0 +/- 0.9 (2L); p.5 "
                    "Gruneisen parameter 1.1 +/- 0.2; Fig. 2 (p.5) peak positions vs strain"),
    laser_nm="532",
    sample_description=("Exfoliated monolayer (4 devices) and bilayer (3 devices) MoS2 on SU8/polycarbonate beam, "
                        "uniaxial tensile strain 0-2.2 % in a four-point bending apparatus, room temperature"),
    peak_table="N", raw_data="N", pdf_status="downloaded",
    source_urls="https://doi.org/10.1021/nl4014748;https://arxiv.org/abs/1305.3880;https://arxiv.org/pdf/1305.3880",
    found_via="WebSearch",
    notes=("paper.pdf is the arXiv version (arXiv:1305.3880, 12 pages), not the ACS version of record; the ACS "
           "Supporting Information (bilayer Raman data, first-principles details) was not downloaded (ACS blocked). "
           "Uniaxial strain: E' splits and A' does not move, so this paper gives no A1' slope; Lloyd 2016 (MOS002) gives both "
           "slopes for biaxial strain. Shift magnitudes are copied as printed; Fig. 2 shows both E' branches moving to lower "
           "wavenumber with tensile strain."),
)

rej("mos2", "", "A note on the existence of global solutions for reaction-diffusion equations with almost-monotonic nonlinearities",
    "wrong paper: arXiv:1212.2826, the ID suggested in the brief for Rice et al. 2013, is a mathematics paper (math.AP), downloaded and deleted; the real Rice paper has no arXiv preprint found")
rej("mos2", "10.1103/PhysRevB.87.081307", "Raman-scattering measurements and first-principles calculations of strain-induced phonon shifts in monolayer MoS2",
    "needs_manual: Rice et al. PRB 87, 081307 (2013), uniaxial strain on polymer-sandwiched MoS2 (E2g1 ~385.3 and A1g ~402.4 cm-1). APS paywall; no arXiv version found; the Bath Pure PDF (researchportal.bath.ac.uk/files/9964242/Wolverson_PRB_2013_87_e081307.pdf) answered 403 and the Limerick Pure page has no file; not retried")

# ---------------------------------------------------------------- quartz
paper(
    material="quartz", paper_id="QTZ001", folder="quartz/QTZ001_KingmaHemley1994", doi="",
    title="Raman spectroscopic study of microcrystalline silica",
    first_author="Kristina J. Kingma", year="1994", journal="American Mineralogist", open_access="Y",
    raman_evidence=("Table 1 (printed p.271 = PDF p.3): Raman-active phonon frequencies of alpha quartz with mode symmetry, "
                    "cm-1: 128 E(LO+TO), 206 A1, 265 E(LO+TO), 355 A1, 394 E(TO), 401 E(LO), 450 E(TO), 464 A1, 511 E(LO), "
                    "696 E(LO+TO), 796 E(TO), 808 E(LO), 1069 E(TO), 1085 A1, 1162 E(LO+TO), 1230 E(LO) (values of Hemley "
                    "1987, ambient); same table lists 19 moganite bands (129-1177); Fig. 2 spectra of moganite and "
                    "pure-quartz chalcedony (Hope, Arizona) with laser plasma/air lines marked by asterisks"),
    laser_nm="514.5",
    sample_description=("Micro-Raman of microcrystalline silica (Gran Canaria moganite, Californian chalcedony, pure quartz "
                        "chalcedony from Hope, Arizona); quartz column of Table 1 is single-crystal alpha quartz at ambient "
                        "conditions, quoted from Hemley (1987)"),
    peak_table="Y", raw_data="N", pdf_status="downloaded",
    source_urls="https://msaweb.org/AmMin/AM79/AM79_269.pdf;http://www.minsocam.org/ammin/AM79/AM79_269.pdf",
    found_via="WebSearch",
    notes=("No DOI (Am. Mineral. 79, 269-273; authors K. J. Kingma and R. J. Hemley). Free PDF from the Mineralogical "
           "Society of America archive; the OCR text layer is poor (author names and table order garbled), so read Table 1 "
           "from a page render. Footnote of Table 1: 1-2 cm-1 differences between the table values (Hemley 1987) and peak "
           "positions in Figs. 1-2 come from small temperature differences. Moganite column is not needed for the quartz "
           "card."),
)
paper(
    material="quartz", paper_id="QTZ002", folder="quartz/QTZ002_Umari2001", doi="10.1103/PhysRevB.63.094305",
    title="Raman scattering intensities in alpha-quartz: A first-principles investigation",
    first_author="P. Umari", year="2001", journal="Physical Review B", open_access="Y",
    raman_evidence=("Table IV (printed 094305-3 = PDF p.3): Gamma-point frequencies of alpha quartz by symmetry; "
                    "experimental room-temperature column (Ref. 14, Masso et al. 1970): A1 207, 356, 464, 1085; E(TO) 128, "
                    "265, 394, 450, 697, 795, 1072, 1162; E(LO) 128, 265, 401, 509, 697, 807, 1162, 1235 cm-1; extra columns "
                    "with the present DFT frequencies, a previous DFT calculation (Gonze 1992) and experiment extrapolated to "
                    "0 K; A2 (IR-active) rows included; Table VI: calculated Raman intensities per mode vs experimental "
                    "relative intensities of Ref. 14"),
    laser_nm="",
    sample_description=("First-principles (DFT, LDA) alpha-quartz, space group P3121 (D3), compared with literature "
                        "single-crystal Raman data; no measurements by the authors"),
    peak_table="Y", raw_data="N", pdf_status="downloaded",
    source_urls=("https://doi.org/10.1103/PhysRevB.63.094305;https://infoscience.epfl.ch/record/141691;"
                 "https://infoscience.epfl.ch/bitstreams/60c36ddb-8e19-42b3-9958-6c49ca1fec9b/download"),
    found_via="WebSearch",
    notes=("Cross-check for QTZ001 (A1/E/TO/LO labels). Theory paper: the experimental frequencies are literature values "
           "(Masso, She and Edwards, Phys. Rev. B 1, 4179 (1970), room temperature) and must be cited as such. The publisher "
           "PDF is hosted by EPFL Infoscience. The alpha-quartz space group is quoted as P3121 here and as the P3221 setting "
           "in the Kihara CIF (structures/quartz.cif)."),
)

rej("quartz", "10.1103/PhysRevB.35.8316", "High-pressure Raman study of the vibrational modes in AlPO4 and SiO2 (alpha-quartz)",
    "needs_manual: Jayaraman, Wood and Maines, PRB 35, 8316 (1987); APS paywall, repository.ias.ac.in record gave 404, no open copy found")
rej("quartz", "10.1103/PhysRev.161.903", "Long-wavelength optical phonons in quartz",
    "not retrieved: Scott and Porto, Phys. Rev. 161, 903 (1967), the classic polarized single-crystal A1/E TO/LO table; APS paywall, no open copy found by web search")
rej("quartz", "", "DTIC report AD0658342 (title not retrieved; search snippet: four A1 modes near 207, 355, 466, 1081 cm-1 and eight E modes)",
    "needs_manual: apps.dtic.mil/sti/pdfs/AD0658342.pdf answered 403 to a scripted request; not retried")
rej("quartz", "", "Ab initio studies of phonon softening and high pressure phase transitions of alpha-quartz SiO2 (arXiv:cond-mat/0601489)",
    "downloaded and read (Choudhury and Chaplot); calculated TO/LO and A1 frequencies vs pressure with group-theory labels, no measured ambient frequencies; Umari 2001 gives a cleaner calculated-vs-experiment table")

# ---------------------------------------------------------------- silicon
paper(
    material="silicon", paper_id="SIL001", folder="silicon/SIL001_Wang2023", doi="10.3390/coatings13040793",
    title="Effect of High-Temperature Annealing on Raman Characteristics of Silicon Nanowire Arrays",
    first_author="Shanshan Wang", year="2023", journal="Coatings", open_access="Y",
    raman_evidence=("Fig. 5b (PDF p.6): spectrum of a monocrystalline Si reference with printed labels 302.06, 520.05 and "
                    "964.48 cm-1; text (PDF p.7): sharp symmetric first-order peak of monocrystalline silicon at 520.05 cm-1 "
                    "(triply degenerate Gamma25 optical phonon) and two very weak broad peaks at 302.06 and 964.48 cm-1; "
                    "Table 1 (PDF p.11) FWHM of the TO peak of four SiNW samples (8.6-19.9 cm-1, not of the wafer)"),
    laser_nm="532",
    sample_description=("Monocrystalline Si reference measured with HORIBA XploRA PLUS, plus ordered/disordered "
                        "Si nanowire arrays made by metal-assisted chemical etching, before and after annealing"),
    peak_table="N", raw_data="N", pdf_status="downloaded",
    source_urls=("https://doi.org/10.3390/coatings13040793;"
                 "https://mdpi-res.com/d_attachment/coatings/coatings-13-00793/article_deploy/coatings-13-00793.pdf"),
    found_via="WebSearch",
    notes=("Open access (MDPI, CC BY); the only open paper found that prints measured Si first-order and both second-order "
           "positions together. LABEL TRAP: the text calls 302.06 cm-1 '2TO' and 964.48 cm-1 '2TA' (reversed); by frequency "
           "302 is the 2TA band and 964 the 2TO band, the usual assignment. No wafer FWHM is given. The sample is a lab Si "
           "reference, so the 520.05 value carries the instrument calibration of that spectrometer."),
)
paper(
    material="silicon", paper_id="SIL002", folder="silicon/SIL002_Iatsunskyi2014", doi="10.1117/12.2051489",
    title="Raman spectroscopy of nanostructured silicon fabricated by metal-assisted chemical etching",
    first_author="Igor Iatsunskyi", year="2014", journal="Proceedings of SPIE 9132 (Nanophotonics V)", open_access="Y",
    raman_evidence=("PDF p.4 (printed 913217-3): c-Si first-order Gamma25 phonon at 520.0 +/- 1.0 cm-1, FWHM 3.5 cm-1 (quoted as "
                    "the bulk reference); Fig. 2 (PDF p.5) labelled spectrum 100-1100 cm-1 with TA(X), TA(L), 2TA(X) near 300, "
                    "LO(L), LTO(Gamma), TO(X)+TA(X), TO(Sigma)+TA(Sigma), 2LO(L), 2TO; text (PDF p.6): 2TA(X) near 300, 2TA(L) "
                    "230, 2LO(L) 830, TO(X)+TA(X) 630, 2TO band split into 930-940 2TO(X), 945-955 2TO(W) and 980 2TO(L) cm-1"),
    laser_nm="488;514;633",
    sample_description=("Nanostructured Si (metal-assisted chemically etched, 15-45 nm hillocks by AFM) on mono-Si wafers; "
                        "Renishaw micro-Raman, room temperature; the 520.0/3.5 values are the bulk c-Si reference"),
    peak_table="N", raw_data="N", pdf_status="downloaded",
    source_urls=("https://doi.org/10.1117/12.2051489;"
                 "https://smyntynava.onu.edu.ua/docs/2014/Raman%20spectroscopy%20of%20nanostructured%20silicon.pdf"),
    found_via="WebSearch",
    notes=("PDF is the author-hosted copy (Odessa Mechnikov University site), with a ResearchGate cover page and SPIE "
           "download watermark. The first-order and 2TA/2TO numbers describe nanostructured Si (shifted 1-2 cm-1 down and "
           "broadened), only the 520.0 +/- 1.0 and 3.5 cm-1 are bulk values and they are quoted from literature, not "
           "measured here. The text refers to a 'table 1' of critical-point frequencies that is not in this version. "
           "Use as a cross-check of the second-order labels (2TA, 2TO(X/W/L)), not as the source of the 520.5 line."),
)
paper(
    material="silicon", paper_id="SIL003", folder="silicon/SIL003_Parker1967", doi="10.1103/PhysRev.155.712",
    title="Raman Scattering by Silicon and Germanium",
    first_author="J. H. Parker Jr.", year="1967", journal="Physical Review", open_access="N",
    raman_evidence=("From the APS abstract only (full text not read): single-crystal Si at 300 K with an argon laser, "
                    "first-order optical mode at 520.2 +/- 0.5 cm-1, full width at half intensity 4.6 cm-1, a second-order "
                    "band near 950 cm-1; Ge 300.7 +/- 0.5 cm-1"),
    laser_nm="",
    sample_description="Single-crystal Si and Ge, 300 K, argon-ion laser (line not read)",
    peak_table="Y", raw_data="N", pdf_status="needs_manual",
    source_urls="https://doi.org/10.1103/PhysRev.155.712",
    found_via="WebSearch",
    notes=("Classic reference with exactly the numbers the card needs (520.2 +/- 0.5 and width 4.6 cm-1 at 300 K, 950 cm-1 "
           "second-order band). APS paywall: the APS full-text endpoint answered 401 not authorized and no open copy was "
           "found, so the folder is empty; download it by hand through Caltech access. Evidence above is from the abstract, "
           "verify against the full text, including the laser line and the Table of second-order features."),
)

rej("silicon", "10.1002/jrs.6630", "Verification of Si wafer first-order phonon peaks for reliable calibration of Raman microscopes",
    "needs_manual: Itoh, J. Raman Spectrosc. 55, 377 (2024); Wiley, no open licence (TDM licence only), Wiley blocks scripted download; first-order peak position/width of Si wafers vs temperature and laser (532/633/785 nm), no second-order spectrum")
rej("silicon", "10.1103/PhysRevB.7.3685", "Multiphonon Raman spectrum of silicon",
    "not retrieved: Temple and Hathaway, PRB 7, 3685 (1973), the standard second-order Si reference; APS paywall, no open copy found by web search")
rej("silicon", "", "A non-destructive analytic tool for nanostructured materials: Raman and photoluminescence spectroscopy (arXiv:cond-mat/0406096)",
    "downloaded and read (Singha, Dhar, Roy); measured Si first-order line 521.9 +/- 0.01 cm-1 (Lorentzian, 488 nm), FWHM 4.4 cm-1, but this is 1.4 cm-1 above the usual 520.5 (the authors quote 522 from the literature) and the weak 2TO is shown only as an inset figure without numbers")
rej("silicon", "", "Combined Raman spectroscopy and electrical transport measurements in ultra-high vacuum down to 3.7 K (arXiv:2410.03271)",
    "downloaded and read; Si F2g line measured at 521.63 cm-1 (5 K) and 518.50 cm-1 (300 K) with 532 nm, 5 mW: the 300 K value is 2 cm-1 below the usual 520.5, no second-order spectrum, no width")
rej("silicon", "10.1038/s41598-017-07682-y", "Ab Initio Approach to Second-order Resonant Raman Scattering Including Exciton-Phonon Interaction",
    "downloaded and read (Gillet et al., Sci. Rep. 7, 7344, 2017); ab initio second-order Si spectrum, text only mentions bands near 950, 980 and 1030 cm-1 versus excitation energy, no first-order value, no tabulated frequencies")
rej("silicon", "", "Nano-Raman spectroscopy of silicon surfaces (arXiv:1002.2692)",
    "downloaded and read; 2TA and 2TO are only labelled on a figure, text says 'peak at 520 cm-1', no numbers")
rej("silicon", "", "Influence of the thickness of Si and Ge films deposited on Si3N4/SiO2/Si substrates (arXiv:2201.04948)",
    "downloaded and read; polycrystalline films, mentions 2TA(c-Si) at ~300 cm-1 and TO at ~520 cm-1 only as round numbers")
rej("silicon", "", "Versatile Confocal Raman Imaging Microscope Built from Off-the-Shelf Opto-Mechanical Components (PMC9786121, Sensors 2022)",
    "read via Europe PMC XML; Si calibration chip peak quoted as 520.9 cm-1 from a reference and TO/2TO as 520 and 970 cm-1, an instrument paper with no spectrum analysis of Si")
