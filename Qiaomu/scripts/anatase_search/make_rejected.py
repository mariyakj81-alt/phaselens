"""Write anatase/candidates_rejected.csv (doi,title,reason). Run: python -P make_rejected.py"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "anatase", "candidates_rejected.csv"))
R = [
# --- downloaded, read, and rejected on content ---
("10.1039/d0ra02929g", "Laser-induced crystallization of anodic TiO2 nanotube layers (Sopha 2020)", "Downloaded+verified PDF, but Raman only confirms anatase; anatase peak positions are quoted from the literature (144/197/399/519/639), no measured numbers"),
("10.3390/polym8030068", "Structural and Spectroscopic Characterization of A Nanosized Sulfated TiO2 Filler (Allodi 2016)", "Downloaded; measured Raman limited to intensity ratios of ~639/518 cm-1 bands; mode positions are literature values"),
("10.1038/s41598-022-26343-3", "Deep-learning framework for fully-automated recognition of TiO2 polymorphs based on Raman spectroscopy (Bhattacharya 2022)", "Downloaded; deep-learning classifier on RRUFF spectra, reports no anatase peak table (only ~150, 200, 445, 611 cm-1 mentions); data = RRUFF database"),
("10.3390/nano13182584", "Characterization and Comparison of WO3/WO3-MoO3 and TiO2 nanostructures (Cifre-Herrando 2023)", "Downloaded; Raman minor (8 mentions; TiO2 peaks 145/397/520/635 only). NOTE raw Raman CSV exists at Zenodo doi:10.5281/zenodo.18659833 if raw spectra are wanted"),
("10.1098/rsos.181578", "TiO2 thin films by ultrasonic spray pyrolysis as photocatalytic material for air purification (Dundar 2019)", "Downloaded; Raman minor (8 mentions; 143/197/396/637 cm-1). NOTE raw Raman xlsx at Dryad doi:10.5061/dryad.b24p647 (Raman Spectroscopy.xlsx, 75 KB)"),
("10.1063/1.1619212", "Temperature dependent optical studies of Ti1-xCoxO2 (Guha 2003)", "Downloaded (arXiv); Raman minor (only 398/515 cm-1 discussed, 16 mentions), focus is optical/magnetic"),
("10.3390/ma16020639", "Low-Temperature Synthesis of Cu-Doped Anatase TiO2 Nanostructures via Liquid Phase Deposition (Honda 2023)", "Downloaded; Raman minor (18 mentions; 152/404/513/634 cm-1 assigned), laser not stated; dropped in favour of stronger entries"),
("10.3390/nano11092311", "Strain and Grain Size Determination of CeO2 and TiO2 Nanoparticles (Canchanya-Huaman 2021)", "Downloaded; only the Eg(1) 144 cm-1 band (785 nm) is used for a size fit; no peak table or other modes"),
("10.3390/nano13121856", "On the Origin of Raman Activity in Anatase TiO2 (Nano)Materials: An Ab Initio Investigation (Taudul 2023)", "Computational (DFT) study; no new experimental Raman spectra"),
("10.1038/srep10928", "Phase stability frustration on ultra-nanosized anatase TiO2 (Patra 2015)", "Downloaded; Raman only supporting (7 mentions), no mode table"),
("(various)", "Several photocatalysis/SERS PMC papers screened by full-text mode-number scoring (e.g. PMC7029928 Ishigaki 2020, PMC8074931 Chen 2021, PMC10300691 Kasuma 2023, PMC13019392, PMC12261510)", "Raman is a minor afterthought (<=15 mentions) or lacks measured anatase peak numbers; not kept"),
("10.1038/s41467-017-00016-6", "Strongly bound excitons in anatase TiO2 single crystals and nanoparticles (Baldini 2017)", "Optical spectroscopy, not Raman peak data"),
("10.3390/ma3031509", "High-Pressure Study of Anatase TiO2 (Jacimovic 2010)", "Transport/XRD under pressure; Raman mentioned once, no spectra"),
("10.1016/j.ssc.2004.12.007; 10.1088/0953-8984/17/4/017", "Ferromagnetism at 300 K in spin-coated Co/Fe-doped anatase and rutile TiO2 films (Suryanarayanan 2004/2005)", "Downloaded (arXiv); Raman minor (10-11 mentions)"),
("10.1179/1743676111Y.0000000059; 10.1016/j.surfcoat.2011.01.007", "Hanaor et al. mixed-phase TiO2 powders/thin films", "Downloaded (arXiv); Raman minor (7-16 mentions)"),
# --- not downloadable by script (publisher block / challenge); candidates for manual download ---
("10.1088/0953-8984/20/8/085212", "Lattice vibration fundamentals in nanocrystalline anatase investigated with Raman scattering (Wang 2008, J. Phys.: Condens. Matter)", "needs_manual: IOP bot challenge (validate.perfdrive.com) after first requests; strong Raman paper"),
("10.1088/1681-7575/acf76d", "Quantification of TiO2 anatase and rutile polymorphs in binary mixtures by Raman spectroscopy (Sacco 2023, Metrologia)", "needs_manual: IOP bot challenge"),
("10.1088/0022-3727/38/9/014", "Infrared study of laser synthesized anatase TiO2 nanopowders (Grujic-Brojcin 2005)", "needs_manual: IOP bot challenge (and IR focus)"),
("10.1088/2515-7639/ab749c", "Mo doped TiO2: impact on oxygen vacancies, anatase phase stability and photocatalytic activity (Kumaravel 2020)", "needs_manual: IOP bot challenge"),
("10.1088/1742-6596/1220/1/012021", "Stimulated Raman scattering in anatase TiO2 (Watanabe 2019)", "needs_manual: IOP bot challenge"),
("10.2298/sos0901067s", "Characterization of anatase TiO2 nanopowder by variable-temperature Raman spectroscopy (Scepanov 2009, Sci. Sinter.)", "not downloaded: doiserbia.nb.rs times out from this network; good temperature-dependence paper (retry later or manual)"),
("10.12693/aphyspola.116.51", "Use of Phonon Confinement Model in Simulation of Raman Spectra of Nanostructured Materials (Grujic-Brojcin 2009)", "Downloaded; only Eg(1) ~144 cm-1 model fits, no laser stated; kept out of the final 30 (could be restored)"),
("10.1080/17458080.2012.689018", "Influence of particle size on the phonon confinement of TiO2 nanoparticles (Venkatachalam 2012)", "needs_manual: Taylor & Francis 403"),
("10.1063/1.4938085", "Anomalous behavior of B1g mode in highly transparent anatase nano-crystalline Nb-doped TiO2 (Gaur 2015, AIP Advances)", "needs_manual: AIP 403"),
("10.1063/1.4824355", "High spatial resolution Raman thermometry analysis of TiO2 microparticles (Lundt 2013)", "needs_manual: AIP 403"),
("10.1063/1.4992130", "A fast-reliable methodology to estimate the concentration of rutile or anatase phases of TiO2 (Ricardo 2017)", "needs_manual: AIP 403"),
("10.1016/j.rinp.2018.03.008", "Strain and grain size of TiO2 nanoparticles from TEM, Raman spectroscopy and XRD (Kibasomba 2018)", "needs_manual: ScienceDirect 403 (open access article)"),
("10.1016/j.rinp.2019.01.054", "Characterisation of titanium oxide layers using Raman spectroscopy and optical profilometry (Ekoi 2019)", "needs_manual: ScienceDirect 403 (open access article)"),
("10.1007/s11534-005-0009-3", "Structural study of TiO2 thin films by micro-Raman spectroscopy (Niilisk 2006)", "needs_manual: De Gruyter HTTP 202 / Springer client challenge"),
("10.1186/2228-5326-3-55; 10.1186/2228-5326-3-25", "Choudhury et al. Local structure modification of TiO2 nanoparticles / Cu-doped TiO2 (Int. Nano Lett. 2013)", "needs_manual: Springer 'Client Challenge' page instead of PDF"),
("10.1103/physrevb.61.14414", "High-pressure polymorphs of anatase TiO2 (Arlt 2000)", "needs_manual: APS 403 (high-pressure Raman)"),
("10.1103/physrevb.71.184302", "Finite-size and pressure effects on the Raman spectrum of nanocrystalline anatase TiO2 (Swamy 2005)", "needs_manual: APS 403 (high-pressure + size)"),
("10.1103/physrevb.70.134102", "Effect of grain size on structural transitions in anatase TiO2: a Raman spectroscopy study at high pressure (Hearne 2004)", "needs_manual: APS 403"),
("10.1103/physrevb.81.174305", "Vibrational dynamics of anatase TiO2: polarized Raman spectroscopy and ab initio calculations (Giarola 2010)", "needs_manual: APS 403 (single crystal)"),
("10.1143/jpsj.48.1661", "Temperature dependence of the Raman spectrum in anatase TiO2 (Ohsaka 1980)", "needs_manual: JPS 403 (temperature-dependent classic)"),
("10.1002/jrs.1250070606", "Raman spectrum of anatase, TiO2 (Ohsaka 1978)", "needs_manual: Wiley 403 (classic reference)"),
("10.1016/0022-4596(82)90006-8", "Raman spectra of titanium dioxide (Balachandran and Eror 1982)", "needs_manual: Elsevier/ScienceDirect (classic reference)"),
("10.1021/jp962747a", "Raman spectroscopy as a morphological probe for TiO2 aerogels (Kelly 1997)", "needs_manual: ACS 403 (size-effect classic)"),
("10.1016/s0022-3697(00)00229-8", "Raman spectroscopy and phase transition of anatase TiO2 under high pressure (Sekiya 2001)", "needs_manual: Elsevier"),
("10.1039/c2cp42763j", "Raman spectra of titanium dioxide (anatase, rutile) with identified oxygen isotopes 16, 17, 18 (Frank 2012)", "needs_manual: RSC 403 (SI pdf is public at rsc.org/suppdata/cp/c2/c2cp42763j)"),
("10.1021/acs.jpcc.8b04987", "Influence of Brookite Impurities on the Raman Spectrum of TiO2 Anatase Nanocrystals (Ceballos-Chuc 2018)", "needs_manual: ACS 403; SI is on figshare (article 6984806)"),
("10.1021/acs.jpcc.4c06154", "Pressure Effects on the Optoelectronic Property of Nanocrystalline Anatase with Different Sizes (Liu 2024)", "needs_manual: ACS 403"),
("10.1103/physrevb.111.104108", "Kinetic control of high pressure phase transitions in anatase TiO2 (Chen 2025)", "needs_manual: APS 403"),
("10.1002/jrs.6478", "Development of a Raman spectroscopy system for in situ monitoring of microwave-assisted inorganic transformations (Jamboretz 2022)", "KEPT as ANA32 with pdf_status=needs_manual (Wiley 403; Browser pane blocks Wiley); raw spectra downloaded"),
("10.1021/acsanm.3c00047", "In-situ Raman spectroscopy of Li+ and Na+ storage in anodic TiO2 nanotubes (2023)", "ACS PDF blocked; an accepted manuscript PDF + figure JPEGs are public at RepOD doi:10.18150/AUUQR7 (Manuscript_TiO2.pdf) - available as a replacement/extra; no raw spectra there"),
("10.1016/j.jelechem.2021.115579", "Photoelectrochemical response of TiO2/ZnO2 nanotubes annealed under different atmospheres (2021)", "needs_manual: Elsevier 403; Raman minor, but raw Raman CSV at Zenodo doi:10.5281/zenodo.18697537"),
("10.1002/jrs.1394", "Identification of anatase in archaeological materials by Raman spectroscopy (Middleton 2005)", "needs_manual: Wiley 403"),
("10.1002/jrs.773", "Blue shift of Raman peak from coated TiO2 nanoparticles (Xu 2001)", "needs_manual: Wiley 403"),
("10.1002/jrs.1566", "Phonon confinement studies in nanocrystalline anatase-TiO2 thin films by micro Raman spectroscopy (Balaji 2006)", "needs_manual: Wiley 403"),
("10.1063/1.2061894", "Raman spectroscopy characterization of titania nanoparticles produced by flame pyrolysis (Li Bassi 2005)", "needs_manual: AIP 403"),
("10.1063/1.120648", "Phonon confinement effects in the Raman scattering by TiO2 nanocrystals (Bersani 1998)", "needs_manual: AIP 403"),
("10.1021/jp9046193", "Raman line shapes of optical phonons of different symmetries in anatase TiO2 nanocrystals (Sahoo 2009)", "needs_manual: ACS 403"),
("10.1016/j.vibspec.2004.05.006", "Size effects in the Raman spectra of TiO2 nanoparticles (Choi 2004)", "needs_manual: ScienceDirect 403"),
("10.1002/jrs.2427", "Titanium dioxide synthesized using titanium chloride: size effect study using Raman spectroscopy and photoluminescence (Gupta 2009)", "KEPT as ANA02 using the arXiv preprint; publisher VoR (Wiley) not downloaded"),
("10.1016/j.cplett.2012.10.082", "Effect of annealing temperature on Raman spectra of TiO2 nanoparticles (Mathpal 2012)", "needs_manual: ScienceDirect (not attempted; Elsevier blocked)"),
]

ATT = {"10.1088/0953-8984/20/8/085212","10.1088/1681-7575/acf76d","10.1088/0022-3727/38/9/014","10.1088/2515-7639/ab749c","10.1088/1742-6596/1220/1/012021",
       "10.1080/17458080.2012.689018","10.1063/1.4938085","10.1016/j.rinp.2018.03.008","10.1007/s11534-005-0009-3","10.1186/2228-5326-3-55; 10.1186/2228-5326-3-25",
       "10.1103/physrevb.61.14414","10.1103/physrevb.71.184302","10.1143/jpsj.48.1661","10.1002/jrs.1250070606","10.1021/jp962747a","10.1039/c2cp42763j","10.2298/sos0901067s"}
R2 = []
for doi, title, reason in R:
    if reason.startswith("needs_manual: ") and doi not in ATT:
        reason = "needs_manual (not attempted; " + reason[len("needs_manual: "):] + " - same publisher blocked scripted PDF access in tests)"
    R2.append((doi, title, reason))
R = R2
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["doi", "title", "reason"])
    w.writerows(R)
print(len(R), "rows ->", OUT)
