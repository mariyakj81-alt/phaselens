# Additional specs appended after those in specs_B.py (same format; {p:REGEX} = PDF page of REGEX)
from specs_B import add

# ---- papers with deposited raw Raman spectra (Zenodo) ----
add(pdf="10.3390_nano13182584/paper.pdf", doi="10.3390/nano13182584",
    title="Characterization and Comparison of WO3/WO3-MoO3 and TiO2/TiO2-ZnO Nanostructures for Photoelectrocatalytic Degradation of the Pesticide Imazalil",
    first_author="Cifre-Herrando, Mireia", surname="CifreHerrando", year=2023, journal="Nanomaterials",
    open_access="Y",
    raman_evidence="p.{p:anatase phase of TiO2 are observed}: pure TiO2 nanostructure (annealed 450 C, 1 h) shows the anatase peaks at 145, 397, 520, 635 cm-1 (Fig. 2b: 145 cm-1 is the strongest); the TiO2-ZnO hybrid shows no peaks because of ZnO fluorescence; raw spectra of TiO2 and TiO2-ZnO in data/01.-Raman csv UTF8.csv",
    laser_nm="488",
    sample_description="Anodic TiO2 nanostructures (pure TiO2 and TiO2-ZnO hybrid) annealed 450 C for 1 h; Witec alpha 300R confocal Raman, 488 nm, 420 uW",
    peak_table="N", raw_data="Y",
    data=[("zen18659833/01.-Raman csv UTF8.csv", "01.-Raman csv UTF8.csv"), ("zen18659833/README mod2.txt", "README_zenodo_18659833.txt")],
    si=[("sup_Cifre/nanomaterials-13-02584-s001.zip", "nanomaterials-13-02584-s001.zip", "unzip")],
    source_urls="https://mdpi-res.com/d_attachment/nanomaterials/nanomaterials-13-02584/article_deploy/nanomaterials-13-02584.pdf; https://doi.org/10.5281/zenodo.18659833",
    found_via="DataCite",
    notes="Raw spectra from the authors' Zenodo deposit 10.5281/zenodo.18659833 (ODC-By): semicolon-separated CSV with decimal commas, side-by-side blocks WO3, W+0.001/0.01/0.1 Mob, TiO2, TiO2-ZnO (shift/intensity pairs, first rows have negative shifts); only the TiO2 block is anatase. Earlier rejected as 'Raman minor' in candidates_rejected.csv but kept now because the raw spectrum is deposited. The README is a dataset description that lists author contact data.")

add(pdf="dundar2019/paper.pdf", doi="10.1098/rsos.181578",
    title="TiO2 thin films by ultrasonic spray pyrolysis as photocatalytic material for air purification",
    first_author="Dundar, Ilona", surname="Dundar", year=2019, journal="Royal Society Open Science",
    open_access="Y",
    raman_evidence="p.{p:The Raman spectra showed bands at 143}: Raman bands at 143 (Eg), 197 (Eg), 396 (B1g) and 637 cm-1 (Eg) for TiO2 films deposited at 250, 350 and 450 C on window glass and annealed 500 C for 1 h (Fig. 3b); no rutile/brookite bands; raw spectra in data/Raman Spectroscopy.xlsx",
    laser_nm="532",
    sample_description="TiO2 films by ultrasonic spray pyrolysis on window glass at 250, 350, 450 C, annealed 1 h at 500 C in air; HORIBA Jobin Yvon HR800 micro-Raman, 532 nm, 5 mW, 10 um spot",
    peak_table="N", raw_data="Y",
    data=[("dundar2019/Raman Spectroscopy.xlsx", "Raman Spectroscopy.xlsx")],
    source_urls="https://pmc-oa-opendata.s3.amazonaws.com/PMC6408371.1/PMC6408371.1.pdf; https://doi.org/10.5061/dryad.b24p647; https://doi.org/10.5281/zenodo.4949999",
    found_via="DataCite",
    notes="Raw Raman xlsx (Sheet1: shift column plus three intensity columns TiO2/W.G-250/350/450, ~1550 points from 50 cm-1) from the Dryad deposit (CC0), taken from its Zenodo mirror 4949999 because the Dryad download needs a token now. Earlier rejected as 'Raman minor' in candidates_rejected.csv but kept now because the raw spectra are deposited. PDF from the NIH PMC open-access bucket.")

add(pdf="", pdf_status="needs_manual", doi="10.1016/j.jelechem.2021.115579",
    title="Influence of annealing atmosphere on photoelectrochemical response of TiO2 nanotubes anodized under controlled hydrodynamic conditions",
    first_author="Blasco-Tamarit, E.", surname="BlascoTamarit", year=2021, journal="Journal of Electroanalytical Chemistry",
    open_access="N (article is paywalled; the raw data are open, ODC-By)",
    raman_evidence="no paper PDF: the authors' Zenodo README states Raman on a WITec confocal Raman microscope with the 633 nm laser at 420 uW; data/02. Raman tests csv utf8.csv holds nine spectra (0, 2500, 5000 rpm anodization rotation x annealing in Ar, air, N2)",
    laser_nm="633",
    sample_description="TiO2 nanotubes by anodization of Ti at 55 V for 30 min under rotating-disk hydrodynamic conditions (0, 2500, 5000 rpm), then annealed in air, nitrogen or argon; WITec confocal Raman, 633 nm, 420 uW",
    peak_table="N", raw_data="Y",
    data=[("zen18697537/02. Raman tests csv utf8.csv", "02. Raman tests csv utf8.csv"), ("zen18697537/README.txt", "README_zenodo_18697537.txt")],
    source_urls="https://doi.org/10.5281/zenodo.18697537; https://doi.org/10.1016/j.jelechem.2021.115579",
    found_via="DataCite",
    notes="needs_manual: Elsevier PDF not retrievable (403 in the first run). Kept for the raw spectra (sample, atmosphere, rotation speed and laser are all stated in the Zenodo README; CSV is semicolon-separated with decimal commas, columns paired shift/intensity). No anatase peak numbers are known from the paper, they must come from fitting the raw spectra. Zenodo record title is 'Photoelectrochemical response of TiO2/ZnO2 nanotubes annealed under diferent atmospheres [Dataset]'.")

# ---- additional MDPI papers (journals outside PMC, found through Crossref abstracts) ----
add(pdf="10.3390_inorganics13050133/paper.pdf", doi="10.3390/inorganics13050133",
    title="Synthesis of Titanium Dioxide Photoanodes by Anodization in a Sodium Chloride Electrolyte",
    first_author="Del Angel-Hernandez, Beatriz", surname="DelAngelHernandez", year=2025, journal="Inorganics",
    open_access="Y",
    raman_evidence="Table 3 p.{p:Raman shifts obtained and the associated crystalline structure}: anatase Raman signals at 139.6, 393.4, 513, 639 cm-1 for the Ti-P15 and Ti-P20 anodized samples (Fig. 10, series Ti-P0 ... Ti-P20)",
    laser_nm="532",
    sample_description="Ti plates anodized in NaCl electrolyte (samples Ti-P0, P4, P6, P8.5, P10, P15, P20 = increasing anodization parameter), anatase in P15/P20; B&W Tek MicroRaman i-Plus, 532 nm",
    peak_table="Y", source_urls="https://mdpi-res.com/d_attachment/inorganics/inorganics-13-00133/article_deploy/inorganics-13-00133.pdf; https://doi.org/10.3390/inorganics13050133",
    found_via="Crossref",
    notes="Compact table of measured anatase positions; the positions are 4-5 cm-1 below the usual values (139.6 vs 144, 393.4 vs 399), probably a spectrometer calibration/strain offset.")

add(pdf="10.3390_coatings9060357/paper.pdf", doi="10.3390/coatings9060357",
    title="The Effects of Thermal and Atmospheric Pressure Radio Frequency Plasma Annealing in the Crystallization of TiO2 Thin Films",
    first_author="Xu, Yu", surname="Xu", year=2019, journal="Coatings",
    open_access="Y",
    raman_evidence="p.{p:original sample and P1 are amorphous}: as-prepared film and plasma sample P1 amorphous, P2 and P3 show anatase bands at 144, 197, 399, 515, 639 cm-1 (Fig. 6a)",
    laser_nm="532",
    sample_description="Amorphous TiO2 films crystallized by thermal or atmospheric-pressure RF plasma annealing (samples P1-P3, increasing plasma treatment); Raman 532 nm, 5 mW, 100-800 cm-1",
    peak_table="N", source_urls="https://mdpi-res.com/d_attachment/coatings/coatings-09-00357/article_deploy/coatings-09-00357.pdf; https://doi.org/10.3390/coatings9060357",
    found_via="Crossref",
    notes="Amorphous-to-anatase crystallization series; mode labels in the paper (Eg, Eg, A1g, B1g, Eg) follow the literature order for 144/197/399/515/639.")

add(pdf="10.3390_coatings14111362/paper.pdf", doi="10.3390/coatings14111362",
    title="Synthesis and Characterization of TiO2 Thin Films Modified with Anderson-Type Polyoxometalates (Ni, Co, and Fe)",
    first_author="Vallejo, William", surname="Vallejo", year=2024, journal="Coatings",
    open_access="Y",
    raman_evidence="p.{p:five of the six expected vibrational modes}: anatase film shows five modes at 148 (Eg), 200 (Eg), 400 (B1g), 522 (A1g/B1g), 645 cm-1 (Eg) (Fig. 2), with a dominant 148 cm-1 band and no rutile",
    laser_nm="780",
    sample_description="Anatase TiO2 thin films (sol-gel/dip coating) alone and modified with Anderson-type NiPOM/CoPOM/FePOM; Thermo Scientific DXR3 Raman, 780 nm",
    peak_table="N", source_urls="https://mdpi-res.com/d_attachment/coatings/coatings-14-01362/article_deploy/coatings-14-01362.pdf; https://doi.org/10.3390/coatings14111362",
    found_via="Crossref",
    notes="Near-infrared (780 nm) excitation; all anatase bands are 2-6 cm-1 above the usual values (148 vs 144, 645 vs 639), as in nanocrystalline films. POM bands at 500-1600 cm-1 are not anatase.")

add(pdf="10.3390_coatings13030647/paper.pdf", doi="10.3390/coatings13030647",
    title="Synergistic Effects of Multiple Heterojunctions and Dopant Atom for Enhancing the Photocatalytic Activity of C-Modified Zn-Doped TiO2 Nanofiber Film",
    first_author="Lu, Y.", surname="Lu", year=2023, journal="Coatings",
    open_access="Y",
    raman_evidence="p.{p:Figure 5a shows the Raman}: all nanofiber films show anatase bands at about 147 (Eg), 399 (B1g), 519 (A1g+B1g), 637 cm-1 (Eg) (Fig. 5a, UV excitation); the 147 and 519 cm-1 bands are tracked across the C-modified/Zn-doped samples",
    laser_nm="325",
    sample_description="Electrospun TiO2 nanofiber films: pure, Zn-doped and C-modified Zn-doped (anatase after calcination); Raman with 325 nm UV laser (D band of carbon weak at this wavelength)",
    peak_table="N", source_urls="https://mdpi-res.com/d_attachment/coatings/coatings-13-00647/article_deploy/coatings-13-00647.pdf; https://doi.org/10.3390/coatings13030647",
    found_via="Crossref",
    notes="UV (325 nm) excitation; positions are given as 'approximately'; doping/carbon-modification series in one figure. No ZnO or rutile bands detected.")
