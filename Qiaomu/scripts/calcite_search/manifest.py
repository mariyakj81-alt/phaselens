# Curated manifest for calcite/papers.csv. Order = CAL01..; extras flagged in notes.
# fields: slug (stage dir), surname (folder), first_author, year, journal, oa, evidence, laser, sample, peak_table, raw, found_via, notes
E = []


def add(**k):
    E.append(k)


add(slug="10.1007_bf03170928", title="Raman spectra of the second order in crystals. Part I: Calcite", surname="Krishnan", first_author="R. S. Krishnan", year=1945,
    journal="Proceedings of the Indian Academy of Sciences - Section A", oa="Y",
    evidence="p.3: seven lines 155, 221, 282, 709, 1084, 1434, 1749 cm-1 reviewed; Table I (p.5): first-order calcite lines, lattice 155.5/283.9 (Eg) and internal 711.8, 1085.6, 1433.8 cm-1 compared with Cabannes-Osborne and Rasetti; second-order spectrum (p.10, p.19)",
    laser="435.8;404.6 (Hg arc lines)", sample="Single-crystal calcite (Iceland spar), photographic spectra, first- and second-order Raman, room temperature",
    peak_table="Y", raw="N", found_via="WebSearch",
    notes="Classic. Free PDF from Indian Academy of Sciences site (ias.ac.in/public/Volumes/seca). Springer DOI has no scriptable OA PDF.")
add(slug="10.1007_bf03045968", title="The Raman spectrum of calcite and its interpretation", surname="Krishnamurti", first_author="D. Krishnamurti", year=1957,
    journal="Proceedings of the Indian Academy of Sciences - Section A", oa="Y",
    evidence="p.4: five conspicuous shifts 155, 282, 712, 1086 and 1436 cm-1; p.12: 1749 cm-1 overtone; weak second-order lines tabulated (pp.4-19)",
    laser="435.8;253.65 (Hg arc lines)", sample="Single-crystal calcite, long-exposure photographic Raman spectra with Hg 4358 and 2536.5 A excitation, interpretation of first- and second-order lines",
    peak_table="Y", raw="N", found_via="OpenAlex",
    notes="Classic memoir (Raman Research Institute Memoir 100). Free PDF from ias.ac.in.")
add(slug="am1985_70_581", surname="Bischoff", first_author="William D. Bischoff", year=1985, journal="American Mineralogist", oa="Y",
    evidence="Table (p.4): peak positions and halfwidths of 154-155, 281, 711, 1085, 1434, 1748 cm-1 for calcite and synthetic/biogenic Mg-calcites vs mol% MgCO3",
    laser="488.0", sample="Synthetic and biogenic (echinoderm etc.) magnesian calcites, dolomite and magnesite; carbonate-ion disorder from lattice-mode halfwidths",
    peak_table="Y", raw="N", found_via="WebSearch",
    notes="No DOI (Am. Mineral. 70, 581-589). Authors Bischoff, Sharma, Mackenzie. Free PDF from minsocam.org archive. Foundational Mg-calcite Raman reference.")
add(slug="10.1557_proc-205-253", surname="Exarhos", first_author="Gregory J. Exarhos", year=1990, journal="MRS Proceedings", oa="Y",
    evidence="p.5 text: external lattice mode at 156 cm-1 at ambient; Fig.1 frequency map vs P and T; calcite I to CaCO3-II and III transformations in a diamond anvil cell",
    laser="488", sample="Single calcite crystal (c-axis oriented) in resistively heated Merrill-Bassett diamond anvil cell, up to ~40 kbar and several hundred K, time-resolved Raman",
    peak_table="N", raw="N", found_via="OpenAlex",
    notes="OSTI/OCR scan (garbled text; numbers mostly in figures). High-pressure and high-temperature condition.")
add(slug="am1991_76_641", surname="Urmos", first_author="J. Urmos", year=1991, journal="American Mineralogist", oa="Y",
    evidence="Table (p.3): band positions (halfwidths) 154, 281, 711, 1085, 1434, 1748 cm-1 for calcite, 9.9 mol% Mg-calcite, white and pink Corallium; 2nu2 overtone 1748",
    laser="488.0;514.5", sample="Biogenic Mg-calcite (deep-sea precious corals Corallium) vs synthetic calcite and 9.9 mol% Mg-calcite",
    peak_table="Y", raw="N", found_via="WebSearch",
    notes="No DOI (Am. Mineral. 76, 641-646). Authors Urmos, Sharma, Mackenzie. Free PDF from minsocam.org archive.")
add(slug="10.1186_1467-4866-8-8", surname="JorgeVillar", first_author="Susana E. Jorge Villar", year=2007, journal="Geochemical Transactions", oa="Y",
    evidence="p.3 text and Fig.3 caption: calcite bands 1086, 712, 281 and 157 cm-1 recorded at 785 nm",
    laser="785;514", sample="Biocolonised hot-spring travertine terrace layers, Svalbard (calcite plus scytonemin, hematite, quartz, graphite)",
    peak_table="N", raw="N", found_via="EuropePMC",
    notes="Field/natural sample; calcite listed in text. Full text XML from Europe PMC.")
add(slug="10.2465_jmps.080714", surname="Noguchi", first_author="Naoki Noguchi", year=2009, journal="Journal of Mineralogical and Petrological Sciences", oa="Y",
    evidence="p.3 text: intrinsic calcite bands at 281, 713 and 1085 cm-1; aragonite 1084 and 208 cm-1 (p.4)",
    laser="488", sample="Powdered calcite, aragonite and quartz binary mixtures (calibration curves), rotating sample stage",
    peak_table="N", raw="N", found_via="Crossref",
    notes="J-STAGE open access. Quantitative mixture analysis, calcite/aragonite polymorph comparison.")
add(slug="10.5194_bg-8-3761-2011", surname="Nehrke", first_author="Gernot Nehrke", year=2011, journal="Biogeosciences", oa="Y",
    evidence="p.3: calcite identified by lattice modes 155 (T) and 282 (L) cm-1 and internal modes 711 (nu4) and 1085 (nu1) cm-1 (Fig.2a); aragonite 152/206",
    laser="532;785", sample="Shell of Nerita undata (gastropod): outer calcite and inner aragonite layers, confocal Raman mapping",
    peak_table="N", raw="N", found_via="OpenAlex", notes="Biogenic calcite, Raman imaging.")
add(slug="10.1016_j.saa.2013.08.014", surname="Sun", first_author="Junmin Sun", year=2014, journal="Spectrochimica Acta Part A", oa="Y",
    evidence="p.2/p.9: calcite bands at 1088, 715, 278 and 157 cm-1 (plus 1440) and dolomite differences; lattice region 500-100 cm-1 (Fig.4)",
    laser="633", sample="Natural calcite and dolomite mineral samples (comparison of Raman bands, lattice modes and internal modes)",
    peak_table="N", raw="N", found_via="OpenAlex",
    notes="Author version from QUT ePrints. Published 2014 (vol. 117, p.158); online 2013.")
add(slug="10.1063_1.4871900", surname="DeLaPierre", first_author="Marco De La Pierre", year=2014, journal="The Journal of Chemical Physics", oa="Y",
    evidence="Tables S1-S3 in OA PDF (pp.3, 9): calc vs exp single-crystal calcite at 300 K and 80 K: Eg 155.4/282.0/712.5/1436.5, A1g 1086.5, overtone 1749 cm-1, with polarised intensities",
    laser="", sample="Single-crystal and powder calcite (and aragonite) at 80 K and room temperature; ab initio CRYSTAL calculations vs measured Raman",
    peak_table="Y", raw="N", found_via="OpenAlex",
    notes="Open-access author manuscript from AperTO (Univ. Torino) with supplementary tables inside the PDF; excitation wavelength not stated in the OA PDF text. SSHADE band list derived from this paper (10.26302/SSHADE/BANDLIST_RAMAN_CALCITE). Low-temperature and single-crystal diversity.")
add(slug="10.1371_journal.pone.0091021", surname="Higuchi", first_author="Tomihiko Higuchi", year=2014, journal="PLoS ONE", oa="Y",
    evidence="p.3: calcite spectrum peaks at ~159, ~284, ~717 and ~1091 cm-1 vs aragonite ~155/208/705/1087 (Fig.1c,d); p.2 lists overlapping and mineral-specific peaks",
    laser="532", sample="Juvenile Acropora tenuis coral skeletons grown at different Mg/Ca (aragonite vs calcite seas)",
    peak_table="N", raw="N", found_via="EuropePMC", notes="Biogenic Mg-calcite in coral; Raman peak values quoted in Results.")
add(slug="10.2138_am-2016-5714", surname="Perrin", first_author="Jonathan Perrin", year=2016, journal="American Mineralogist", oa="Y",
    evidence="Table (p.33): OCN calcite crystal T 155.5, L 282, nu4 711.8, nu1 1086, nu3 1435.6, 2nu2 1748.7 cm-1 with FWHM; synthetic Mg-calcites and comparison with Bischoff 1985",
    laser="514.5;532", sample="Synthetic magnesian calcites (graded mol% MgCO3), natural calcite and dolomite single crystals; peak position and width vs Mg content",
    peak_table="Y", raw="N", found_via="OpenAlex", notes="Free PDF (MSA public access, includes appendices; 47 pages).")
add(slug="10.1016_j.conbuildmat.2017.01.008", surname="Yue", first_author="Yanfei Yue", year=2017, journal="Construction and Building Materials", oa="Y",
    evidence="Table 1 (p.4): calcite lattice 154/281, nu1 1085, nu3 1434, nu4 711 cm-1 (literature); p.11: bench Raman of calcite 1085, 280, 712, 1436 cm-1",
    laser="514.5", sample="CaCO3 reagent (calcite) powder and carbonated Portland cement paste; optical-fibre vs bench Raman",
    peak_table="Y", raw="N", found_via="SemanticScholar", notes="Accepted manuscript from White Rose eprints.")
add(slug="10.1039_c8ra06608f", surname="Xu", first_author="Ben Xu", year=2018, journal="RSC Advances", oa="Y",
    evidence="ESI Fig.S8/S1: Raman of 13C-enriched calcite powders: nu1 1084, nu4 710, lattice 278 and 151 cm-1; nu4 shifts with 13C content (main text is mostly FTIR)",
    laser="633", sample="Calcite powders with 1% to 100% 13C isotopic enrichment (IR and Raman) plus DFT",
    peak_table="N", raw="N", found_via="OpenAlex;EuropePMC",
    notes="Isotope-substituted calcite. Raman data are in the ESI PDF (SI/). Main article mentions Raman only 4 times.")
add(slug="10.5741_gems.55.3.406", surname="XuH", first_author="Hanyue Xu", year=2019, journal="Gems & Gemology", oa="Y",
    evidence="p.9: white part of imitation shows Raman peaks 150, 280, 712 and 1085 cm-1 assigned to calcite lattice, bending and symmetric stretching modes (plus Al(OH)3 at 1000/1600)",
    laser="532", sample="Pressed gibbsite and calcite rhodochrosite imitation vs natural rhodochrosite (gem materials)",
    peak_table="N", raw="N", found_via="OpenAlex", notes="Gemmological sample; calcite mode assignments given in text.")
add(slug="10.1038_s41598-020-60031-4", surname="Nekvapil", first_author="Fran Nekvapil", year=2020, journal="Scientific Reports", oa="Y",
    evidence="Table (p.5): calcite T 154/155, L 281/282/284, nu4 712/714 cm-1 measured at 532, 632.8, 785, 830, 1064 nm; text p.6: nu1 1085-1088 cm-1",
    laser="532;632.8;785;830;1064", sample="Blue crab (Callinectes sapidus) claw cuticle: Mg-calcite with astaxanthin, multi-wavelength Raman",
    peak_table="Y", raw="N", found_via="EuropePMC",
    notes="Best multi-laser comparison of calcite peak positions in one paper. SI docx included.")
add(slug="10.1038_s41598-020-66831-y", surname="ClaraSaracho", first_author="Alexandra Clarà Saracho", year=2020, journal="Scientific Reports", oa="Y",
    evidence="p.3: calcite nu1 1085 cm-1 (FWHM 7 cm-1) and external modes 155 and 280 cm-1; vaterite 1076/1088 doublet",
    laser="532.05", sample="CaCO3 (calcite and vaterite) from strain-specific ureolytic bacterial precipitation, surface vs interior of aggregates",
    peak_table="N", raw="N", found_via="EuropePMC", notes="Microbially induced carbonate precipitation. SI PDF included (SI Table S1 covers organic D/G bands, not calcite).")
add(slug="10.1098_rsos.200725", surname="Metzler", first_author="Rebecca A. Metzler", year=2020, journal="Royal Society Open Science", oa="Y",
    evidence="p.6: 2-day barnacle exoskeleton shows calcite peaks at 282, 714 and 1086 cm-1 (3-day and 6-day also)",
    laser="785", sample="Exoskeleton of juvenile barnacles (Amphibalanus amphitrite) 1 h to 6 d after metamorphosis; calcite onset by Raman",
    peak_table="N", raw="Y", found_via="EuropePMC",
    notes="Raw Raman spectra (.txt and Renishaw .wdf, 5 barnacle ages) from Dryad dataset 10.5061/dryad.brv15dv7g (Zenodo mirror 4135137, Metzler_Raman.tgz). SI xlsx is EDS only.")
add(slug="10.2138_am-2020-7404", surname="Farsang", first_author="Stefan Farsang", year=2021, journal="American Mineralogist", oa="Y",
    evidence="Table 2 (p.5): ambient Raman-active modes of calcite T 158, L 284, nu4 713, nu1 1088, nu3 1438, overtone 1751 cm-1 (Eg, Eg, Eg, A1g, Eg); Tables 3-4 (pp.7-8): calcite dnu/dP (0-5 GPa) and dnu/dT (25-500 C)",
    laser="532.05", sample="Calcite, dolomite, magnesite etc. in hydrothermal diamond anvil cell up to 6 GPa and 500 C; anharmonicity",
    peak_table="Y", raw="N", found_via="OpenAlex",
    notes="Green OA copy (Empa DORA). New measurements here are mostly for the other calcite-/aragonite-group carbonates; the calcite P/T data are carried over from Farsang 2018 (10.2138/am-2018-6442, needs_manual). High-pressure and high-temperature condition.")
add(slug="10.3389_feart.2022.907967", surname="Zhao", first_author="Xia Zhao", year=2022, journal="Frontiers in Earth Science", oa="Y",
    evidence="p.3 text: calcite-I external modes ~160 and ~280 cm-1 and nu4 ~720 cm-1 at high P; cc-II ~150/280/720; cc-III/IIIb more nu4 peaks; aragonite ~160/220",
    laser="532", sample="CaCO3 (calcite I, II, III, IIIb, VI) and aragonite in externally heated DAC to 12 GPa and 400 C, anhydrous and hydrous media",
    peak_table="N", raw="N", found_via="OpenAlex",
    notes="Approximate peak positions (text and figures only): weakest peak-number evidence, kept for high-pressure polymorph diversity. Companion Chin. Phys. B 2022 calcite-III paper (10.1088/1674-1056/ac6157, data on ScienceDB 10.57760/sciencedb.01838) is needs_manual.")
add(slug="10.1007_s44211-022-00119-1", surname="Urashima", first_author="Shu-hei Urashima", year=2022, journal="Analytical Sciences", oa="Y",
    evidence="Table 2 (p.5): calcite T 154.6+-0.9, L 280.9+-0.9, nu4 711.6+-0.8, nu1 1086.0+-0.8 cm-1; also magnesite, siderite, rhodochrosite, dolomite",
    laser="532", sample="Natural calcite-group and dolomite-group carbonate minerals from many localities, micro-Raman, linear relations between peak frequencies",
    peak_table="Y", raw="N", found_via="OpenAlex;EuropePMC", notes="Cation-substitution trends; SI docx included.")
add(slug="10.1098_rsos.220773", surname="LaroucheBilodeau", first_author="Charles Larouche-Bilodeau", year=2022, journal="Royal Society Open Science", oa="Y",
    evidence="Table (p.10): L, nu4, nu1 peak positions per species (e.g. Pisaster 284/717/1088) and Mg calibration L=280.7+0.29x, nu4=711.9+0.19x, nu1=1086.1+0.18x (mol% MgCO3)",
    laser="514.5", sample="Acorn worm (enteropneust) ossicles and echinoderm reference (Pisaster) Mg-calcite; polymorph and Mg content from Raman",
    peak_table="Y", raw="Y", found_via="Crossref",
    notes="Raw Raman spectra (two-column Wave/Intensity txt for several species) from Zenodo 10.5281/zenodo.5103052 (CC-BY) saved in data/. ESM on figshare.")
add(slug="10.1038_s41598-023-39842-8", surname="Toffolo", first_author="Michael B. Toffolo", year=2023, journal="Scientific Reports", oa="Y",
    evidence="Table 1 (p.4): average Raman shifts T 155.2, L 281.7, nu4 712.8, nu1 1087 cm-1 (chalk) and other geogenic/anthropogenic calcites with sd; FWHM analysis; p.3 lists T/L/nu4 Eg and nu1 A1g",
    laser="532", sample="Geogenic (chalk, limestone) vs anthropogenic (plaster, ash, archaeological) calcites; band position and FWHM crystallinity metrics, two gratings",
    peak_table="Y", raw="N", found_via="OpenAlex;EuropePMC", notes="Best-fit reference for T/L/nu4/nu1 position and FWHM with Eg/A1g labels. Raw data on request only.")
add(slug="10.1039_d3an00441d", surname="Calandra", first_author="Sara Calandra", year=2023, journal="The Analyst", oa="Y",
    evidence="Table 2 (p.5): wavenumbers/intensities/areas of L 282, nu4 712, nu1 1086 cm-1 (and T 156); Table 4 (p.9): FWHM of L, nu4, nu1 for geogenic and anthropogenic calcite",
    laser="785", sample="Geogenic calcite (marbles, limestones) vs anthropogenic calcite (mortars, plasters); Raman plus machine-learning classification",
    peak_table="Y", raw="N", found_via="OpenAlex",
    notes="PDF from an OA repository location listed by OpenAlex. ESI on RSC site not retrieved (RSC blocks scripted access).")
add(slug="10.1039_d3ra05179j", surname="Kim", first_author="Deborah Kim", year=2023, journal="RSC Advances", oa="Y",
    evidence="p.7: micro-Raman of calcite 714, 1090, 1440 cm-1 and 1758 cm-1 combination band; ESI Table S5 lists calcite 714 (nu4), 1090 (nu1), 1440 (nu3), 1758 (combination)",
    laser="532", sample="Calcite within dust/mineral thin films (aluminosilicates, carbonates, sulfates) measured by micro-Raman, ATR-FTIR, O-PTIR, AFM-IR",
    peak_table="Y", raw="N", found_via="EuropePMC", notes="Calcite is one of several phases; peak table is in the ESI PDF (SI/).")
add(slug="10.1371_journal.pone.0312495", surname="EscamillaRoa", first_author="Elizabeth Escamilla-Roa", year=2024, journal="PLoS ONE", oa="Y",
    evidence="p.9: calcite bands at 280, 711 and 1084 cm-1 (aragonite 705 cm-1) in Fig.5C and Fig.6C micro-Raman spectra",
    laser="785", sample="Calcite/aragonite crystals precipitated from CaCl2 with perchlorate and sulphate brines (Mars Jezero analogue)",
    peak_table="N", raw="Y", found_via="EuropePMC",
    notes="Raw micro-Raman spectra as semicolon-separated CSV (Fig4c, Fig5c, Fig6c CaCl2; Fig10c FeSO4; Fig11c NiSO4) plus XRD CSVs in PLOS SI S3 zip, copied to data/.")
add(slug="10.2343_geochemj.gj24023", surname="Inoue", first_author="Yuki Inoue", year=2024, journal="Geochemical Journal", oa="Y",
    evidence="p.3: 12C16O3 nu1 peak at ~1085 cm-1 and 12C16O2 18O peak at ~1065 cm-1 resolved; Table 1: peak-ratio statistics vs exposure time; 18O ratio from Raman",
    laser="532", sample="Calcite reference crystals: Raman peak ratios of oxygen isotopologues at various exposure times and gratings",
    peak_table="N", raw="N", found_via="OpenAlex",
    notes="Isotope (18O) condition; companion 17O paper (SAA 2026, 10.1016/j.saa.2026.128616) is needs_manual.")
add(slug="10.1021_acs.cgd.4c01063", surname="Barbosa", first_author="Natercia Barbosa", year=2025, journal="Crystal Growth & Design", oa="Y",
    evidence="p.16: calcite lattice 155 and 283, nu4 713, nu1 1086 cm-1 vs aragonite 154/206/706 and vaterite 1075/1091 cm-1",
    laser="785", sample="In situ micro-Raman of CaCO3 precipitation (amorphous, vaterite, aragonite, calcite) in solution time series",
    peak_table="N", raw="N", found_via="OpenAlex", notes="Accepted manuscript from UNIGE archive-ouverte (public access).")
add(slug="10.1038_s41598-025-14083-z", surname="Dubey", first_author="Anant Aishwarya Dubey", year=2025, journal="Scientific Reports", oa="Y",
    evidence="p.7: calcite precipitate shows nu1 1089, nu4 715 and lattice 156 and 262 cm-1 (Suppl. Fig. S3a); vaterite nu4 doublet 739/749 and nu1 doublet 1075/1090 cm-1",
    laser="532", sample="Bacterially induced CaCO3 precipitates (calcite and vaterite) on different mineral substrates with biofilm/EPS, single-point Raman (WITec, Nd:YAG 532 nm, 50 mW)",
    peak_table="N", raw="N", found_via="EuropePMC",
    notes="Replaced the weaker Jimenez Bonales 2013 paper. Calcite peak numbers in text; SI PDF has spectra (Fig. S3).")
add(slug="10.1177_00037028251330654", surname="Lellinger", first_author="Dirk Lellinger", year=2025, journal="Applied Spectroscopy", oa="Y",
    evidence="Fig.5 caption (p.8): calcite CRM peaks at 155.5, 282, 711.8, 1085 and 1435.6 cm-1 fitted on ten instruments; FWHM of 1085 band 3.9-11.7 cm-1 (Voigt), ASTM E2529",
    laser="514;532;633;785", sample="Certified calcite reference material measured on 11 Raman systems (interlaboratory), peak position/FWHM fitting error vs line shape",
    peak_table="N", raw="Y", found_via="EuropePMC",
    notes="Raw spectra (Ne, Si, polystyrene, calcite) in NeXus .nxs from Zenodo 10.5281/zenodo.13387413 (CC-BY), saved in data/. Interlaboratory and multi-laser condition.")
add(slug="10.1038_s41467-025-67899-8", surname="Su", first_author="Min Su", year=2025, journal="Nature Communications", oa="Y",
    evidence="p.2: calcite nu1 1087, nu4 712 and L 285 cm-1 grow during Ca(OH)2 carbonation; Source Data xlsx has raw Raman spectra (Fig.1b, S1, S2, S4, S11, S17)",
    laser="532", sample="Ca(OH)2 carbonation in nanoscale interfacial water films forming calcite; in situ Raman, MCR-ALS",
    peak_table="N", raw="Y", found_via="EuropePMC",
    notes="EXTRA. Raw Raman spectra in Source Data workbook (SI MOESM6 xlsx, copied to data/) and as txt files in Supplementary Data 1 (rar, extracted to SI/unzipped and copied to data/SupplementaryData1_Raman_txt).")
add(slug="10.1007_s44211-025-00731-x", surname="Urashima", first_author="Shu-hei Urashima", year=2025, journal="Analytical Sciences", oa="Y",
    evidence="Fig.2b (p.3): terrestrial calcite spectrum labelled T 157, L 283, nu4 712, nu1 1089 cm-1; Y980115 carbonate spectra vs dolomite",
    laser="532", sample="Terrestrial calcite/dolomite reference and carbonates in CY carbonaceous chondrite Yamato 980115",
    peak_table="N", raw="N", found_via="OpenAlex", notes="EXTRA. Same group/protocol as the 2022 Anal. Sci. paper.")
add(slug="10.1002_jrs.70059", surname="Conner", first_author="Kyle Conner", year=2025, journal="Journal of Raman Spectroscopy", oa="Y", nopdf=True,
    evidence="Not verified (PDF blocked). Title: red (785 nm) vs blue (457 nm) lasers for Raman of synthetic and natural calcium carbonate; Zenodo data have raw spectra by figure",
    laser="785;457", sample="Synthetic and natural calcium carbonate samples (calcite etc.), two excitation wavelengths",
    peak_table="", raw="Y", found_via="OpenAlex",
    notes="EXTRA, needs_manual: Wiley PDF behind Cloudflare. Raw spectra + R code downloaded from Zenodo 10.5281/zenodo.17033032 (CC-BY, 24 MB zip, also unzipped in data/). Evidence/peak fields come from title and data only; verify against the PDF once downloaded manually.")
