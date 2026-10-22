# Specs of accepted papers (agent B), in acceptance order = ANA068, ANA069, ...
# Placeholders {p:REGEX} in text fields are replaced by the 1-based PDF page where REGEX first occurs (resolved in build_B.py).
START = 68
SPECS = []


def add(**k):
    SPECS.append(k)


add(pdf="Giarola2010/paper.pdf", doi="10.1103/physrevb.81.174305",
    title="Vibrational dynamics of anatase TiO2: Polarized Raman spectroscopy and ab initio calculations",
    first_author="Giarola, M.", surname="Giarola", year=2010, journal="Physical Review B",
    open_access="Y (publisher version posted by the authors' university repository IRIS Univr, APS permission note on p.1)",
    raman_evidence="Table II p.{p:Observed and calculated wave numbers} (observed, this work): Eg(1) 143, Eg(2) 198, B1g(1) 395, B1g(2) 512, A1g 518, Eg(3) 639 cm-1; polarized backscattering spectra of one microcrystal separate A1g from B1g(2)",
    laser_nm="514.5",
    sample_description="Natural anatase crystal (Maddalena pit, Beura, Italy); polarized micro-Raman (Porto notation) on a single ~10x12x15 um microcrystal picked from the mosaic crystal, room temperature, backscattering",
    peak_table="Y", source_urls="https://iris.univr.it/bitstream/11562/342058/1/Vibrational%20dynamics%20of%20anatase%20TiO.pdf; https://doi.org/10.1103/PhysRevB.81.174305",
    found_via="WebSearch",
    notes="Single-crystal (microcrystal) polarized Raman plus ab initio phonons; Table II also lists literature columns (Refs. 20-22) and calculated values, skip those. PDF is the APS-published version hosted in the Verona repository (pages 1-2 are the repository's APS-permission cover notice, the article starts on PDF p.3, so the PDF page numbers quoted here count the cover pages). Earlier listed in candidates_rejected.csv as needs_manual (APS 403); obtained from the repository instead.")

add(pdf="Ishioka/paper.pdf", doi="10.1103/physrevb.86.205201",
    title="Raman generation of coherent phonons of anatase and rutile TiO2 photoexcited at fundamental absorption edges",
    first_author="Ishioka, Kunie", surname="Ishioka", year=2012, journal="Physical Review B",
    open_access="Y (author-posted publisher PDF, NIMS eprints)",
    raman_evidence="Table I p.{p:TABLE I} (Raman columns, anatase): 145 (HWHM 5) Eg, 199 (2) Eg, 396 (10) B1g, 517 (11) B1g/A1g doublet, 638 cm-1 (11) Eg; coherent-phonon (transient reflectivity) frequencies 4.36/5.85/11.83/15.21/19.09 THz = 145/195/395/507/637 cm-1",
    laser_nm="532",
    sample_description="(101)-oriented natural anatase single crystal (SurfaceNet), as received, ambient; spontaneous Raman in backscattering (resolution 0.7 cm-1); coherent phonons by 10 fs 400 nm pump-probe",
    peak_table="Y", source_urls="https://www.nims.go.jp/ldynamics/eprints/PhysRevB.86.205201.pdf; https://doi.org/10.1103/PhysRevB.86.205201",
    found_via="WebSearch",
    notes="Single crystal. Time-domain impulsive Raman (400 nm, polarization dependence vs crystal rotation) plus spontaneous 532 nm Raman for Table I; rutile data in the same table are not anatase.")

add(pdf="Kyoto_SRS/paper.pdf", doi="10.1088/1742-6596/1220/1/012021",
    title="Stimulated Raman scattering in anatase TiO2",
    first_author="Watanabe, M.", surname="Watanabe", year=2019, journal="Journal of Physics: Conference Series",
    open_access="Y (CC BY 3.0; copy in Kyoto University repository)",
    raman_evidence="p.{p:Results and discussion}: lowest Eg phonon at 137 cm-1 at 5 K (sharp, intense), B1g 395 cm-1 and Eg 640 cm-1 quoted in text; Fig. 1 (spontaneous 5 K spectrum) labels symmetries Eg, Eg, B1g, A1g+B1g, Eg without numbers; higher-order Stokes lines at 2x and 3x the Eg shift (Figs. 2-3)",
    laser_nm="632.8;639;395",
    sample_description="Unoriented single crystals of anatase grown by chemical transport reactions, in a He flow cryostat at 4-5 K; spontaneous Raman with cw He-Ne 632.8 nm (1.96 eV); stimulated Raman with OPA pulses at 1.94 eV (639 nm, off resonance) and 3.14 eV (395 nm, resonance)",
    peak_table="N", source_urls="https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/a27113d0-dd50-43a1-8a43-8acdff060879/content; https://doi.org/10.1088/1742-6596/1220/1/012021",
    found_via="WebSearch",
    notes="Cryogenic (4-5 K) single-crystal data. Only three mode positions are in the text (137, 395, 640 cm-1) and the Eg(1) at 137 cm-1 is the low-temperature value (about 144 at room temperature). The 1.94/3.14 eV lines are pulsed SRS pump wavelengths, not cw Raman. Earlier listed in candidates_rejected.csv as needs_manual (IOP); obtained from the Kyoto repository.")

add(pdf="arxiv_keep/1610.08044.pdf", doi="10.1021/acs.nanolett.5b02663",
    title="'Black' TiO2 nanotubes formed by high energy proton implantation show noble-metal-co-catalyst free photocatalytic H2-evolution",
    first_author="Liu, Ning", surname="Liu", year=2015, journal="Nano Letters",
    open_access="Y (arXiv preprint 1610.08044)",
    raman_evidence="p.{p:mild blue shift}: Eg(1) of anatase nanotubes 144 cm-1 (non-implanted) -> 146 cm-1 (H+-implanted) with FWHM 13 -> 16 cm-1; on the (001) anatase single crystal the Eg bands at 144 and 636 cm-1 grow relative to B1g/A1g after implantation (SI Figs. S5/S6, PDF p.{p:Fig. S5})",
    laser_nm="632",
    sample_description="Anodic TiO2 nanotubes (anatase after annealing) with the tube tops H+-implanted at high energy; (001) anatase single crystal before/after H-implantation; Spex 1403 spectrometer, HeNe 632 nm line",
    peak_table="N", source_urls="https://arxiv.org/abs/1610.08044; https://doi.org/10.1021/acs.nanolett.5b02663",
    found_via="arXiv",
    notes="Includes an anatase single crystal (SI Fig. S5, spectra only, no peak table). arXiv preprint of the Nano Lett. paper (DOI from Crossref title match); SI figures are inside the arXiv PDF. Laser line given as 632 nm in the paper.")

add(pdf="arxiv_keep/1902.04137.pdf", doi="10.1039/c7ta08074c",
    title="Large area photoelectrodes based on hybrids of CNT fibres and ALD-grown TiO2",
    first_author="Moya, A.", surname="Moya", year=2017, journal="Journal of Materials Chemistry A",
    open_access="Y (arXiv preprint 1902.04137, accepted-manuscript style)",
    raman_evidence="p.{p:Eg1 mode, shifts from 150}: anatase bands at 147 (Eg1), 199 (Eg2), 395 (B1g), 514 (A1g), 636 cm-1 (Eg3); Eg1 shifts from 150 to 147 cm-1 as TiO2 thickness increases (10-80 nm); residual tensile strain 0.7-2 % in TiO2",
    laser_nm="532",
    sample_description="Monocrystalline anatase TiO2 layers (10-80 nm) deposited by ALD on CNT fibres (conformal coating); Renishaw spectrometer, 5.3 mW, 1 um spot",
    peak_table="N", source_urls="https://arxiv.org/abs/1902.04137; https://doi.org/10.1039/C7TA08074C",
    found_via="arXiv",
    notes="Thickness series (strain / Eg1 position). Peak positions are in the text of p.4; spectra only in figures.")

add(pdf="arxiv_keep/1705.01701.pdf", doi="10.1039/c7nr01305a",
    title="Molecularly-thin anatase field-effect transistors fabricated through the solid state transformation of titania nanosheets",
    first_author="Sekizaki, S.", surname="Sekizaki", year=2017, journal="Nanoscale",
    open_access="Y (arXiv preprint 1705.01701)",
    raman_evidence="p.{p:main peak of the anatase phase, Eg}: Eg(1) appears at ~142 cm-1 after annealing; observed at 142 cm-1 for multilayer and bulk-like films but absent for the monolayer; Eg(1)/Si-peak intensity ratio vs annealing (Fig. 1b); B1g(1) also seen (Fig. 1c)",
    laser_nm="488",
    sample_description="Anatase films, 0.7 nm to ~10 nm thick, made by annealing Ti0.87O2 nanosheets on SiO2/Si; micro-Raman with Ar laser 488 nm, ~0.3 mW",
    peak_table="N", source_urls="https://arxiv.org/abs/1705.01701; https://doi.org/10.1039/C7NR01305A",
    found_via="arXiv",
    notes="Thickness-dependent Eg(1); Eg(1) quoted as ~142 cm-1 (low, thin-film value); Si substrate lines (300, 520 cm-1) share the spectra.")

add(pdf="2503.19520/paper.pdf", doi="arXiv:2503.19520",
    title="On Tailoring Structural and Optoelectronic Properties of TiO2 Thin Films Synthesized via 'Room' Temperature High Power Impulse Magnetron Sputtering (HiPIMS)",
    first_author="Chacko, Aarati", surname="Chacko", year=2025, journal="arXiv preprint (Empa / ETH Zurich)",
    open_access="Y (arXiv preprint; also ETH Research Collection)",
    raman_evidence="p.{p:Most of the Raman peaks observed}: anatase modes at 144 (Eg), 400 (B1g), 520 (A1g), 640 (Eg) cm-1, rutile contribution near 600; Figs. 6-7 plot the position and width of the 144 cm-1 Eg(1) mode versus %O2 and total pressure (blue shift = fewer defects)",
    laser_nm="532",
    sample_description="TiO2 thin films by room-temperature HiPIMS, varying O2 fraction and total pressure; Raman and PL measured on films grown on uncoated polished sapphire substrates (SEM/TEM on Si, ellipsometry on Pt/sapphire); Raman 532 nm (PL 488 nm)",
    peak_table="N", source_urls="https://arxiv.org/abs/2503.19520; http://hdl.handle.net/20.500.11850/742392",
    found_via="arXiv",
    notes="Eg(1) position/FWHM trends are in figures (Figs. 6-7), not in a table; the nominal mode list in the text is literature-style. SI tables are in the same PDF (p.33-35). Doi column holds the arXiv ID because no journal DOI exists.")

add(pdf="10.3390_chemosensors12090191/paper.pdf", doi="10.3390/chemosensors12090191",
    title="Near-Infrared Multiwavelength Raman Anti-Stokes/Stokes Thermometry of Titanium Dioxide",
    first_author="Zani, Veronica", surname="Zani", year=2024, journal="Chemosensors",
    open_access="Y",
    raman_evidence="p.{p:centered at 143, 197, 397, 515 and 640}: Stokes peaks at 143, 197, 397, 515, 640 cm-1 = Eg(1), Eg(2), B1g(1), B1g(2)+A1g, Eg(3) (800 nm); Eg(1) at 143 cm-1 with FWHM 7 cm-1; p.{p:centered at 143, 400, 515 and 640}: Stokes 143, 400, 515, 640 and anti-Stokes counterparts at the same shift with negative sign",
    laser_nm="785;800;980",
    sample_description="Commercial anatase TiO2 powder (large crystallites, diffuse reflectance >90 % in the NIR) used as Raman thermometer; Stokes and anti-Stokes spectra at three NIR excitation wavelengths, temperature series",
    peak_table="N", source_urls="https://mdpi-res.com/d_attachment/chemosensors/chemosensors-12-00191/article_deploy/chemosensors-12-00191.pdf; https://doi.org/10.3390/chemosensors12090191",
    found_via="Crossref",
    notes="Laser-wavelength dependence (785, 800 and 980 nm) of anatase Stokes and anti-Stokes spectra; Raman shifts are stated to be independent of the excitation wavelength. Same group as ANA008 but a different paper. PDF from the MDPI CDN (mdpi-res.com).")

add(pdf="mdpi_cat13671/paper.pdf", doi="10.3390/catal13040671",
    title="3D Flower-like TiO2 Nanostructures: Anatase-To-Rutile Phase Transformation and Photoelectrochemical Application",
    first_author="Kusior, Anna", surname="Kusior", year=2023, journal="Catalysts",
    open_access="Y",
    raman_evidence="p.{p:After 15 min of oxidation}: after 15 min oxidation a strong 144 cm-1 Eg appears; after annealing at 450 C anatase 144 Eg, 197 Eg, 398 B1g, 513 A1g, 519 (A1g/B1g), 640 Eg plus small rutile 375, 448, 610 cm-1; intensity ratio 610/635 cm-1 vs reaction time tracks the anatase-to-rutile transition (Fig. 3)",
    laser_nm="488",
    sample_description="Flower-like TiO2 nanostructures by Ti oxidation (different reaction times/thicknesses) and annealing in different atmospheres; anatase-to-rutile transformation; WITec Alpha 300M, 488 nm, 50-1000 cm-1",
    peak_table="N", source_urls="https://mdpi-res.com/d_attachment/catalysts/catalysts-13-00671/article_deploy/catalysts-13-00671.pdf; https://doi.org/10.3390/catal13040671",
    found_via="Crossref",
    notes="Anatase-to-rutile transformation series; anatase modes are quoted in text with literature-style labels (519 called A1g) next to the measured spectra. PDF from the MDPI CDN (mdpi-res.com).")

add(pdf="2005.01488/paper.pdf", doi="10.1002/adma.201604747",
    title="Noble-Metal-Free Photocatalytic Hydrogen Evolution Activity: The Impact of Ball Milling Anatase Nanopowders with TiH2",
    first_author="Zhou, Xuemei", surname="Zhou", year=2017, journal="Advanced Materials",
    open_access="Y (arXiv preprint 2005.01488)",
    raman_evidence="p.{p:144.4}: anatase Eg 144.4, Eg 196.4, B1g 394.5, A1g 515.1, Eg 636.8 cm-1; ball-milling series with rutile Eg 446/A1g 619 cm-1 overlapping; enlarged 100-200 cm-1 region (Fig. {p:Enlarged Raman spectra from 100 to 200})",
    laser_nm="532",
    sample_description="Commercial anatase nanopowder (nominal 20 nm) ball-milled with TiH2 for different times; Raman 532 nm (PL 375 nm)",
    peak_table="N", source_urls="https://arxiv.org/abs/2005.01488; https://doi.org/10.1002/adma.201604747",
    found_via="arXiv",
    notes="Ball-milling series; the main anatase paragraph gives five measured positions for the starting powder, trends are in the Eg(1) enlargement.")

add(pdf="2411.08515/paper.pdf", doi="10.1016/j.jciso.2025.100150",
    title="Effect of pH on photocatalytic degradation of Methylene Blue in water by facile hydrothermally grown TiO2 Nanoparticles under Natural Sunlight",
    first_author="Saint, Uttama Kumar", surname="Saint", year=2025, journal="JCIS Open",
    open_access="Y (arXiv preprint 2411.08515; journal is open access)",
    raman_evidence="p.{p:148.6}: sample S1 Eg 148.6, B1g 400.3, B1g+A1g 515.6, Eg 637.5 cm-1 + minor Eg 198.8; sample S2 143.4, 394.7, 514.4, 636.9 + minor 195.9 cm-1; FWHM of the Eg(1) mode 21.5 cm-1 (S1) -> S2 smaller",
    laser_nm="633",
    sample_description="Hydrothermally grown anatase TiO2 nanoparticles, two synthesis pH values (S1, S2); HORIBA LabRAM HR Evolution, 633 nm, room temperature",
    peak_table="N", source_urls="https://arxiv.org/abs/2411.08515; https://doi.org/10.1016/j.jciso.2025.100150",
    found_via="arXiv",
    notes="Two samples with different crystallite size/defects give Eg(1) at 148.6 vs 143.4 cm-1; arXiv preprint (DOI from Crossref title match, a SSRN copy also exists).")

add(pdf="arxiv_keep/2512.24219.pdf", doi="arXiv:2512.24219",
    title="Increased Covalence and V-center mediated Dark Fenton-Like Reactions in V-doped TiO2: Mechanisms of Enhanced Charge-Transfer",
    first_author="Kumari, Manju", surname="Kumari", year=2025, journal="arXiv preprint (IIT Indore)",
    open_access="Y (arXiv preprint)",
    raman_evidence="p.{p:For the TV0 sample, these modes were observed at 143}: undoped sample TV0 modes at 143 Eg, 195 Eg, 396 B1g, 514 A1g, 519 B1g, 637 cm-1 Eg; p.{p:blue-shift upon V-doping}: Eg(1) 143 cm-1 blue-shifts and FWHM of all phonons grows with V doping (Fig. 2b)",
    laser_nm="633",
    sample_description="Anatase TiO2 (TV0) and V-doped TiO2 nanoparticles; HORIBA LabRAM HR Evolution, 633 nm",
    peak_table="N", source_urls="https://arxiv.org/abs/2512.24219",
    found_via="arXiv",
    notes="All six anatase modes named with the doublet resolved (514 A1g, 519 B1g); doping series in Fig. 2.")

add(pdf="1909.04623/paper.pdf", doi="arXiv:1909.04623",
    title="New and fast route to black TiO2 based on hollow cathode H2 plasma",
    first_author="Godoy Jr., A.", surname="Godoy", year=2019, journal="arXiv preprint (ITA, Brazil)",
    open_access="Y (arXiv preprint)",
    raman_evidence="p.{p:139.5}: five modes at 139.5, 199.0, 390.5, 513.3, 632.6 cm-1 for all samples (Voigt fits, Gaussian width fixed at 1.6 cm-1); sample set = pristine anatase films and H2-plasma treated black TiO2",
    laser_nm="532",
    sample_description="Anatase TiO2 films by magnetron sputtering on glass and c-Si, annealed 450 C 2 h, then treated in hollow-cathode H2 RF plasma (black TiO2); Raman 532 nm, <10 mW",
    peak_table="N", source_urls="https://arxiv.org/abs/1909.04623",
    found_via="arXiv",
    notes="Mode positions are 3-7 cm-1 below the usual values (139.5 vs 144), measured on thin films; the same group published the work as Catalysts 2020 (10.3390/catal10030282) under a different title, which was not used.")

add(pdf="0811.0466/paper.pdf", doi="10.1088/0957-4484/20/1/015604",
    title="Hierarchically organized nanostructured TiO2 for photocatalysis applications",
    first_author="Di Fonzo, F.", surname="DiFonzo", year=2009, journal="Nanotechnology",
    open_access="Y (arXiv preprint 0811.0466)",
    raman_evidence="p.{p:Raman peaks at 143}: after 400 C annealing anatase at 143, 197, 399, 519, 639 cm-1 with rutile 447, 612 cm-1 growing with deposition pressure up to 100 Pa; Eg(1) 143.6 cm-1 (FWHM 13) for 10 Pa vs 146.3 cm-1 (FWHM 16) for 100 Pa films",
    laser_nm="514.5",
    sample_description="Nanostructured TiO2 films by reactive pulsed laser deposition in air background pressure 10-100 Pa, as-deposited (amorphous) and annealed 1 h at 400 C in air",
    peak_table="N", source_urls="https://arxiv.org/abs/0811.0466; https://doi.org/10.1088/0957-4484/20/1/015604",
    found_via="arXiv",
    notes="Size/pressure series with Eg(1) position and FWHM in the text (domain size trend); as-deposited films are amorphous or disordered.")

add(pdf="EEJP_ALD/paper.pdf", doi="10.26565/2312-4334-2025-1-27",
    title="Optical Performance and Crystal Structure of TiO2 Thin Film on Glass Substrate Grown by Atomic Layer Deposition",
    first_author="Turdaliev, Temur K.", surname="Turdaliev", year=2025, journal="East European Journal of Physics",
    open_access="Y",
    raman_evidence="p.{p:well-defined peaks at frequencies of 143}: peaks at 143, 194, 392, 514, 637 cm-1; 143/194/637 = Eg, 394 = B1g, 514 = A1g+B1g doublet (factor-group analysis)",
    laser_nm="",
    sample_description="TiO2 thin film on glass by atomic layer deposition, anatase by XRD and Raman; one spectrum (Fig. 3)",
    peak_table="N", source_urls="https://periodicals.karazin.ua/eejp/article/download/24388/22761",
    found_via="WebSearch",
    notes="Raman excitation wavelength is not stated in the PDF (checked Methods); literature values 144/194/397/517/513/639 are quoted separately next to the measured ones.")

add(pdf="10.3390_app11010143/paper.pdf", doi="10.3390/app11010143",
    title="Few-Layered MoS2 Nanoparticles Covering Anatase TiO2 Nanosheets: Comparison between Ex Situ and In Situ Synthesis Approaches",
    first_author="Santalucia, Rosangela", surname="Santalucia", year=2021, journal="Applied Sciences",
    open_access="Y",
    raman_evidence="p.{p:the four bands at 144}: pure TiO2 nanosheets bands at 144 Eg, 396 B1g, 514 A1g, 636 cm-1 Eg; p.{p:split into two components}: 396 band splits into 407 and 385 cm-1 (MoS2 A1g/E12g) in MoS2/TiO2 (ex situ 407/385, in situ 406/386)",
    laser_nm="514.5",
    sample_description="Anatase TiO2 nanosheets (pretreated at 873 K) and MoS2/TiO2 hybrids from ex situ and in situ synthesis; Renishaw inVia, Ar+ 514.5 nm",
    peak_table="N", source_urls="https://mdpi-res.com/d_attachment/applsci/applsci-11-00143/article_deploy/applsci-11-00143.pdf; https://doi.org/10.3390/app11010143",
    found_via="Crossref",
    notes="Only the anatase bands of the TiO2 nanosheets and the TiO2-MoS2 overlap region are relevant; MoS2 bands at 385/407 are not anatase. Appl. Sci. 2021, 11, 143 (Crossref online date 2020).")

add(pdf="bjnano9-21/paper.pdf", doi="10.3762/bjnano.9.21",
    title="Bombyx mori silk/titania/gold hybrid materials for photocatalytic water splitting: combining renewable raw materials with clean fuels",
    first_author="Krüger, Stefanie", surname="Kruger", year=2018, journal="Beilstein Journal of Nanotechnology",
    open_access="Y",
    raman_evidence="p.{p:151 cm-1}: nanoparticulate anatase bands at 151 (most intense Eg), 209, 409, 509 and 630 cm-1 (Au-containing hybrids intensify 209, 409, 630); bulk-anatase reference values 144/197/640, 400/519, 513 cm-1 quoted separately",
    laser_nm="532",
    sample_description="Silk/titania(/Au) hybrids with anatase nanoparticles (TPS_Aux, TS_Aux series); Raman 532 nm, 14 mW, NA 0.9 objective",
    peak_table="N", si=[("SI_Kruger/si.pdf", "2190-4286-9-21-S1.pdf")],
    source_urls="https://www.beilstein-journals.org/bjnano/content/pdf/2190-4286-9-21.pdf; https://doi.org/10.3762/bjnano.9.21",
    found_via="WebSearch",
    notes="Nanoparticle Eg(1) at 151 cm-1 is strongly blue-shifted vs bulk (size/silk matrix); 519/513 overlap noted; first sentence lists literature bulk values, use the later measured ones.")

add(pdf="nat_s41598-024-61701-3/paper.pdf", doi="10.1038/s41598-024-61701-3",
    title="Enhanced optical and electrochemical properties of FeBTC MOF modified TiO2 photoanode for DSSCs application",
    first_author="Moloto, William", surname="Moloto", year=2024, journal="Scientific Reports",
    open_access="Y",
    raman_evidence="p.{p:142.7}: TiO2 Eg 142.7 and 635.6, B1g 396.5, A1g 514.1 cm-1; Eg 142.7 decreases in intensity and blue-shifts with 2-8 % FeBTC loading (Fig. 6a)",
    laser_nm="532",
    sample_description="Anatase TiO2 and TiO2-FeBTC MOF composites (2, 4, 6, 8 %); Witec Alpha 300, 532 nm, 100x",
    peak_table="N", si=[("sup_Moloto/41598_2024_61701_MOESM1_ESM.docx", "41598_2024_61701_MOESM1_ESM.docx")],
    source_urls="https://www.nature.com/articles/s41598-024-61701-3.pdf; https://doi.org/10.1038/s41598-024-61701-3",
    
    found_via="WebSearch",
    notes="Composite series; blue shifts with MOF loading are described for all bands but exact shifted values are only in Fig. 6a.")

add(pdf="1702.07586/paper.pdf", doi="10.1016/j.nanoso.2017.03.006",
    title="Electrical Transport Properties of Polycrystalline and Amorphous TiO2 Single Nanotubes",
    first_author="Stiller, Markus", surname="Stiller", year=2017, journal="Nano-Structures & Nano-Objects",
    open_access="Y (arXiv preprint 1702.07586)",
    raman_evidence="p.{p:148 cm}: annealed (anatase) single nanotube Raman Eg bands at 148 and 633 cm-1 (Raman map of the 148 cm-1 band, Fig. 1e), blue-shifted against the bulk 144/639 cm-1 quoted from Ohsaka",
    laser_nm="532",
    sample_description="Anodic TiO2 nanotubes on Ti foil, annealed to anatase, isolated single nanotubes; WITec alpha300R+ confocal Raman, 532 nm, ~3 mW",
    peak_table="N", source_urls="https://arxiv.org/abs/1702.07586; https://doi.org/10.1016/j.nanoso.2017.03.006",
    found_via="arXiv",
    notes="Raman is a supporting measurement (two anatase positions, Raman image); amorphous tubes show no bands.")

add(pdf="1112.5231/paper.pdf", doi="10.1016/j.jallcom.2008.03.137",
    title="Ethylene glycol-mediated synthesis of nanoporous anatase TiO2 rods and rutile TiO2 self-assembly chrysanthemums",
    first_author="Li, Quanjun", surname="Li", year=2009, journal="Journal of Alloys and Compounds",
    open_access="Y (arXiv preprint 1112.5231)",
    raman_evidence="p.{p:Eg \\(143 cm-1\\)}: anatase rods Raman peaks 143 (Eg), 195, 395, 515, 638 cm-1 (the paper's own assignment: 195 B1g, 395 A1g, 515 B1g); rutile chrysanthemums 143 (B1g), 237 (2-phonon), 442 (Eg), 610 cm-1 (A1g)",
    laser_nm="514.5",
    sample_description="Nanoporous anatase TiO2 rods from titanium glycolate calcined in air; rutile chrysanthemums after vacuum calcination (400 C); Renishaw inVia, 514.5 nm",
    peak_table="N", source_urls="https://arxiv.org/abs/1112.5231; https://doi.org/10.1016/j.jallcom.2008.03.137",
    found_via="arXiv",
    notes="Mode labels are mis-assigned in the paper (195 B1g, 395 A1g, 515 B1g); positions are measured. Rutile positions listed alongside are not anatase.")

add(pdf="korea2004/paper.pdf", doi="10.5012/bkcs.2004.25.3.426",
    title="Characterization of Raman Spectra of Size-Selected TiO2 Nanoparticles by Two-Dimensional Correlation Spectroscopy",
    first_author="Choi, Hyun Chul", surname="Choi", year=2004, journal="Bulletin of the Korean Chemical Society",
    open_access="Y",
    raman_evidence="p.{p:Synchronous cross peaks}: 2D-correlation cross peaks at 638, 515, 397 cm-1 (synchronous) and 641, 517, 398 cm-1 (asynchronous); all bands shift to higher wavenumber with decreasing size (samples ~30, ~12, ~7 nm); Fig. 1 spectra of the three size-selected samples",
    laser_nm="1064",
    sample_description="Size-selected TiO2 nanoparticles (A ~30 nm, B ~12 nm, C ~7 nm) from titanium isopropoxide hydrolysis, calcined 450 C 1 h; Bruker FRA 106/S FT-Raman, Nd:YAG 1.5 W (1064 nm)",
    peak_table="N", source_urls="https://koreascience.kr/article/JAKO200402727211737.pdf",
    found_via="WebSearch",
    notes="Size series (30/12/7 nm); Raman positions appear only as 2D-correlation cross-peak positions in text; sample C (~7 nm) is TiO2-II-like per the authors. Laser given as Nd:YAG (1064 nm for FT-Raman).")

add(pdf="OSTI1511373/paper.pdf", doi="10.1063/1.4824355",
    title="High spatial resolution Raman thermometry analysis of TiO2 microparticles",
    first_author="Lundt, Nils", surname="Lundt", year=2013, journal="Review of Scientific Instruments",
    open_access="Y (UC Berkeley eScholarship copy)",
    raman_evidence="p.{p:Figure 3 displays}: Fig. 3 nu6 (Eg) phonon spectra at several temperatures (peak broadens and shifts to higher wavenumbers with temperature); calibration of the Eg peak position vs temperature on anatase microparticle powder heated with a thermocouple (PDF p.5-6)",
    laser_nm="532",
    sample_description="Anatase TiO2 microparticle powder (heated-stage calibration) and microparticles on a Si-N membrane micro-heater; WiTec alpha300 confocal Raman, cw Nd:YAG 532 nm",
    peak_table="N", source_urls="https://escholarship.org/content/qt9p87f7vt/qt9p87f7vt.pdf; https://www.osti.gov/pages/servlets/purl/1511373",
    found_via="WebSearch",
    notes="Temperature dependence of the Eg (nu6) peak position (calibration on heated powder, then micro-heater measurements); the numbers are mostly in figures and fit equations. Earlier listed in candidates_rejected.csv as needs_manual (AIP); obtained from eScholarship.")

add(pdf="OSTI1436470/paper.pdf", doi="10.1063/1.5024418",
    title="Atomically engineered epitaxial anatase TiO2 metal-semiconductor field-effect transistors",
    first_author="Kim, Brian S. Y.", surname="Kim", year=2018, journal="Applied Physics Letters",
    open_access="Y (accepted manuscript on OSTI)",
    raman_evidence="p.{p:Clear anatase peaks}: anatase peaks at B1g 399, A1g+B1g doublet 516, Eg 639 cm-1 observed on the devices (Fig. 2b)",
    laser_nm="532",
    sample_description="Epitaxial anatase TiO2 (001) films on LaAlO3 (pulsed laser deposition) in metal-semiconductor FET devices",
    peak_table="N", source_urls="https://www.osti.gov/servlets/purl/1436470",
    found_via="WebSearch",
    notes="Epitaxial anatase film; Raman is a short confirmation (three bands quoted, Eg(1) not in the quoted set); laser 532 nm taken from the Methods sentence.")

add(pdf="10.3897_aldj.2.117753/paper.pdf", doi="10.3897/aldj.2.117753",
    title="Crystalline as-deposited TiO2 anatase thin films grown from TDMAT and water using thermal atomic layer deposition with in situ layer-by-layer air annealing",
    first_author="Wooding, Jamie P.", surname="Wooding", year=2024, journal="Atomic Layer Deposition",
    open_access="Y",
    raman_evidence="p.{p:both the Eg \\(145}: anatase Eg 145 and 636 cm-1, B1g 394 cm-1 for 25/50 nm TDMAT/H2O/air ALD films at 180-200 C (A1g 514 hidden by the Si 521 line); the 50 nm TDMAT/H2O films without air pulses show only the Si line (amorphous); Fig. 2 panels with Eg/B1g markers",
    laser_nm="488",
    sample_description="TiO2 ALD films (10-50 nm) from TDMAT/H2O with or without an extra air (O2) pulse at 180-200 C on Si; Renishaw InVia Qontor, 488 nm, 10 % power",
    peak_table="N", source_urls="https://doi.org/10.3897/aldj.2.117753",
    found_via="Crossref",
    notes="As-deposited crystallinity versus temperature/thickness; films on Si, so the Si 521 line overlaps A1g/B1g(2). PDF obtained through the Pensoft download link of the DOI landing page.")

add(pdf="10.3389_fmats.2021.714835/paper.pdf", doi="10.3389/fmats.2021.714835",
    title="Synthesis of Different Sizes TiO2 and Photovoltaic Performance in Dye-Sensitized Solar Cells",
    first_author="Mahmoud, Sawsan A.", surname="Mahmoud", year=2021, journal="Frontiers in Materials",
    open_access="Y",
    raman_evidence="p.{p:146 \\(Eg\\)}: small anatase bands at 146 (Eg), 185 (Eg), 401 (B1g), 518 (A1g), 634 (Eg) cm-1 in samples R0, R10, R20, R30 (Fig. 7A); rutile/other bands 243, 431 cm-1 in the same spectra",
    laser_nm="532",
    sample_description="TiO2 particles of different sizes (water-content series R0-R30, nitrogen-modified) by sol-gel; Raman 532 nm",
    peak_table="N", source_urls="https://www.frontiersin.org/journals/materials/articles/10.3389/fmats.2021.714835/pdf",
    found_via="Crossref",
    notes="Size series made by water content; one band list is given for the four samples together.")

add(pdf="arxiv_keep/2510.22296.pdf", doi="arXiv:2510.22296",
    title="Enhanced magnetic and optical properties of oxygen deficient TiO2-δ nanoparticles synthesized by environment-friendly green route using whole plant extract of Phyllanthus niruri",
    first_author="Mishra, Latika", surname="Mishra", year=2025, journal="arXiv preprint",
    open_access="Y (arXiv preprint)",
    raman_evidence="p.{p:147, 199 and 641}: anatase Eg(1) ~147, Eg(2) 199, Eg(3) 641, B1g ~398, A1g+B1g 517 cm-1 (Fig. 5)",
    laser_nm="532",
    sample_description="Oxygen-deficient anatase TiO2-delta nanoparticles by green synthesis with Phyllanthus niruri extract; Princeton Instruments Acton 2500i, 532 nm; spectra at three positions",
    peak_table="N", source_urls="https://arxiv.org/abs/2510.22296",
    found_via="arXiv",
    notes="Single sample; Eg(1) at 147 cm-1 is blue-shifted by size/oxygen vacancies (the paper compares with literature).")
