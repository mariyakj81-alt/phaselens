"""Write anatase/papers.csv from build_state.json + curated fields. Run: python -P make_csv.py"""
import os, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "anatase")
state = json.load(open(os.path.join(HERE, "build_state.json"), encoding="utf-8"))
byid = {v["folder"][:5]: (k, v) for k, v in state.items()}

# curated: id -> dict(ev, laser, sample, table, raw, found, notes)
C = {
"ANA01": dict(ev="text p.3: Raman lines at 151, 409, 515, 633 cm-1 assigned Eg/B1g/A1g(B1g)/Eg; Eg(2) 196 cm-1 resolves after 500 C anneal; Eg(1) blueshift+broadening vs size",
    laser="488", sample="TiO2 nanocrystals from tetrabutyl titanate hydrolysis, 6.8-27.9 nm after annealing 100-650 C, pressed pellets",
    table="N", raw="N", found="OpenAlex",
    notes="IOP PDF; size/annealing series (phonon confinement + nonstoichiometry); classic ref. Later scripted IOP requests hit a bot challenge (file kept from the first successful fetch)."),
"ANA02": dict(ev="text p.10: peaks at 143, 197, 397, 516, 637 cm-1 assigned Eg, Eg, B1g, A1g+B1g, Eg; Eg(1) shift/FWHM vs size fitted with phonon confinement",
    laser="514.5", sample="TiO2 nanocrystals by wet chemistry, ~7 nm and ~15 nm (XRD/TEM), Raman + PL",
    table="N", raw="N", found="WebSearch",
    notes="PDF is the arXiv preprint (0904.2264) of the J. Raman Spectrosc. 2009 article; confirm numbers against the VoR if citing."),
"ANA03": dict(ev="text p.2: Eg(1) ~143 (143-144 range), Eg(2) 197, B1g(1) 399, A1g/B1g(2) combined band, Eg(3) 639 cm-1; Eg(1) linewidth 12.1-13.7 cm-1 vs La doping",
    laser="514", sample="La-doped and undoped TiO2 nanopowders (sol-gel), anatase with brookite traces",
    table="N", raw="N", found="OpenAlex",
    notes="Serbian group (Scepanovic/Popovic). Proceedings paper, Acta Phys. Pol. A 115."),
"ANA04": dict(ev="text p.2: modes 143 (Eg1), 197 (Eg2), 399 (B1g1), 519 (A1g,B1g2), 639 (Eg3) cm-1; Eg(1) 143-144 cm-1, width 12.1-13.7; low-frequency Raman (442 nm)",
    laser="442; 514", sample="pure and La-doped TiO2 nanopowders by sol-gel (anatase + brookite fraction)",
    table="N", raw="N", found="OpenAlex",
    notes="Companion to ANA03 (adds low-frequency Raman, acoustic modes), Acta Phys. Pol. A 116."),
"ANA05": dict(ev="Table 1 (p.2): Eg(1) peak position and width vs nanoparticle size (28 nm 143.8 cm-1 up to ~148 cm-1 for smaller sizes); modified hard-confinement fit with w0 = 143.5-144 cm-1",
    laser="", sample="TiO2 nanocrystals: re-analysis of literature Raman data (hard-confinement model) of the anatase Eg(1) band vs size",
    table="Y", raw="N", found="OpenAlex",
    notes="Only Eg(1) is quantified; laser not stated (analysis of literature data). Kept for size-vs-position numbers."),
"ANA06": dict(ev="text p.2: experimental spectrum 3Eg at 143, 197, 639; 2B1g at 399, 519; A1g 513 cm-1; Eg(1) frequency/intensity/halfwidth vs laser irradiation energy",
    laser="488", sample="anatase TiO2 nanocrystal powders before/after pulsed laser irradiation (nonstoichiometry, surface strain, phonon confinement)",
    table="N", raw="N", found="OpenAlex",
    notes="Ukrainian journal (SPQEO). Its Table 1 gives lattice parameters only; Raman numbers are in text/figures."),
"ANA07": dict(ev="text p.7 + Fig.4: reference Eg(1) 144, Eg(2) 197, B1g(1) 399, A1g 513, B1g(2) 519, Eg(3) 638 cm-1; Eg(1)/Eg(2) shift up and Eg(1) width vs Ta content",
    laser="514.5", sample="Ta-doped (and Nb-doped) anatase TiO2 thin films by pulsed laser deposition on glass, vacuum annealed (0-10 at.% Ta)",
    table="N", raw="N", found="OpenAlex",
    notes="PDF is the accepted manuscript from the Politecnico di Milano repository (not the publisher VoR). Strong dopant series."),
"ANA08": dict(ev="Table 1: experimental vs literature anatase Raman-active modes at 514.5 nm; Table 2: position/width of the 143 cm-1 Stokes peak and Stokes/anti-Stokes areas vs temperature; Table 5: calibration at four wavelengths",
    laser="488; 514.5; 568.2; 647.1", sample="anatase TiO2 nanoparticles as Raman thermometer, four laser lines, temperature series",
    table="Y", raw="N", found="EuropePMC",
    notes="Best candidate for temperature dependence + multi-laser. Raw spectra not deposited. fulltext.xml has the tables."),
"ANA09": dict(ev="Fig.3b text: Eg(1) 147, Eg(2) 197 (shoulder), B1g 397, A1g/B1g 515, Eg(3) 640 cm-1; Table 4: Eg(1) position vs crystallite diameter",
    laser="514.5", sample="TiO2 nanoparticles by sol-gel/solvothermal (ethylene glycol route, anatase), Raman anti-Stokes/Stokes thermometry",
    table="Y", raw="N", found="EuropePMC",
    notes="SI is a PDF with extra spectra (SI/). Companion to ANA08."),
"ANA10": dict(ev="Tables 3-6: identification of calculated and measured anatase Raman peaks (Eg 144/197/640, B1g 399/519, A1g 513) for pure, REE-doped and Cu-doped TiO2",
    laser="532", sample="TiO2 nanocrystals from several synthesis routes, pure and REE/Cu-doped, with DFT-calculated bulk anatase/rutile Raman peaks",
    table="Y", raw="N", found="EuropePMC",
    notes="Raw data on request only. Includes DFT peak table for comparison. fulltext.xml has the tables."),
"ANA11": dict(ev="Table 1: bands with assignments 144 Eg(1), 199 Eg(2), 395 B1g(1), 514 A1g/B1g(2), 635 Eg(3) cm-1 (anatase nanotube arrays)",
    laser="325; 532", sample="anodic TiO2 nanotube arrays (4-7 um), in situ UV (325 nm) vs visible (532 nm) Raman",
    table="Y", raw="N", found="EuropePMC",
    notes="UV Raman gives ~24x larger signal than 532 nm. Table 1 is for 4-MBA-modified arrays but lists the anatase bands."),
"ANA12": dict(ev="text p.3: Li-poor anatase LixTiO2 bands at 141 (Eg), 195 (Eg), 396 (B1g), 512 (A1g), 522 (B1g), 628 cm-1 (Eg); five fitted modes 141/396/512/522/629 + ~200 cm-1",
    laser="532", sample="P-doped TiO2 (anatase) nanoparticles in Li half cells, in situ Raman + in situ XRD during lithiation",
    table="N", raw="N", found="EuropePMC",
    notes="Operando electrochemical series; SI PDF in SI/."),
"ANA13": dict(ev="Table 2: Raman band analysis (single grains/aggregates); text: anatase bands 638, 393, 516, 197 cm-1 (Eg, B1g, A1g/B1g, Eg) by deconvolution",
    laser="532", sample="natural hydrothermal TiO2 polymorphs (anatase/rutile/brookite) from Jebel Akhdar, Oman; micro-Raman of single grains",
    table="Y", raw="Y", found="EuropePMC",
    notes="Raw Raman spectra + EMP data are at EarthChem/IEDA doi:10.26022/IEDA/111495 (1495-1_ECL_Pinto_EMP_Raman_Oman.xlsx, 929 KB, CC-BY-SA). The download passes through a terms/disclaimer page, so the file is NOT downloaded: needs_manual for the data file only (see data/DATA_LINK.txt). Natural samples."),
"ANA14": dict(ev="text p.5: anatase mode at 145 cm-1 with weaker modes near 400, 510, 635 cm-1; Ti-6Al-4V (TA) samples show a weak peak at ~143 cm-1 (disordered layer)",
    laser="632.8", sample="anatase layers on Ti and Ti-6Al-4V dental implant screws after acid etching/anodization/thermal treatments",
    table="N", raw="N", found="EuropePMC",
    notes="Surface-treatment series on implants; spectra fitted with Lorentzians."),
"ANA15": dict(ev="text p.4: Eg 145 cm-1 plus B1g 395.0, A1g 515.4, Eg 638.1 cm-1 assigned; peak evolution with annealing temperature",
    laser="532", sample="anodic TiO2 nanotube arrays (TNTAs), amorphous -> anatase -> rutile on annealing",
    table="N", raw="N", found="EuropePMC",
    notes="ESI PDF in SI/. Laser line from Methods (LabRAM HR Evolution, 532)."),
"ANA16": dict(ev="text p.4: anatase target bands 144, 197, 398, 513, 638 cm-1 (Eg, Eg, B1g, A1g, Eg); mixed-phase films 144, 398 (A) and 443, 610 (R) cm-1",
    laser="514.5", sample="TiO2 thin films by femtosecond PLD at 25, 400, 600 C on silica/ITO (anatase-rutile mixtures)",
    table="N", raw="N", found="EuropePMC",
    notes="Phase-mixture films; the 800 nm laser is the fs deposition laser, Raman used Ar+ 514.5."),
"ANA17": dict(ev="text p.3: pure TiO2 films after 200 C anneal: Eg(LF) 144, B1g 395, Eg(HF) 638 cm-1; Ag-TiO2 phase transitions to 1000 C",
    laser="532", sample="Ag-doped TiO2 films by pulsed cathodic arc, annealed 200-1000 C",
    table="N", raw="N", found="EuropePMC",
    notes="Annealing series (amorphous -> anatase -> rutile)."),
"ANA18": dict(ev="text p.6: calcined titania Raman at 144, 197, 394, 515, 635 cm-1 = Eg(1), Eg(2), B1g, A1g, Eg(3); laser-modified as-anodized NTs show Eg(1) 156, A1g 510, Eg(3) 632 cm-1",
    laser="514", sample="anodic TiO2 nanotubes, calcined vs pulsed UV (355 nm) laser-annealed in different atmospheres",
    table="N", raw="N", found="EuropePMC",
    notes="355 nm is the processing laser; Raman excitation is Ar+ 514 nm."),
"ANA19": dict(ev="text p.12: A-TiProp anatase bands at 149, 401, 517, 642 cm-1 plus 200 cm-1 shoulder (blue-shifted vs bulk 144/197/399/513/519/639)",
    laser="532", sample="TiO2 nanoparticles by inverse microemulsion at 80 C: anatase, rutile or anatase/rutile/brookite mixtures",
    table="N", raw="N", found="EuropePMC",
    notes="Polymorph-mixture reference spectra (brookite bands also listed)."),
"ANA20": dict(ev="text p.4: Eg 145.9, 198.3, 643.0 cm-1 and B1g 397.3, 518.3 cm-1 (+A1g) for TiO2 inverse opal; commercial anatase powder Eg(1) 142.5; FWHM 12.9 cm-1",
    laser="632.8", sample="2D TiO2 inverse-opal monolayer films (pure anatase) calcined 300-550 C",
    table="N", raw="N", found="EuropePMC",
    notes="ESI PDF has a Raman 100-2000 cm-1 spectrum."),
"ANA21": dict(ev="text p.3: anatase powder reference lines 142, 390, 511, 637 cm-1 (Eg, B1g, A1g/B1g, Eg); Eg(1) shift/broadening in 3% Co-TiO2",
    laser="633", sample="Co-doped TiO2 anatase nanoparticles (6-10 nm) by wet chemistry, 0-3 % Co",
    table="N", raw="N", found="EuropePMC",
    notes="Dopant series."),
"ANA22": dict(ev="text p.6: Raman bands 146 (Eg), 197 (Eg), 397 (B1g), 522 (B1g), 640 (Eg) cm-1 for Ce/Eu-doped anatase films",
    laser="514.53", sample="Ce- and Eu-doped TiO2 thin films by sol-gel dip-coating on Si, annealed",
    table="N", raw="N", found="EuropePMC",
    notes="Raman is secondary to photocatalysis (13 Raman mentions) but the peak list with assignments is explicit. Year 2022 = Turk J Chem vol 46 (Crossref lists 2021 online-first)."),
"ANA23": dict(ev="text p.5: base TiO2 calcined 400 C: 144 (Eg), 197 (Eg), 392 (B1g), 515 cm-1...; 800 C/doped samples 143/197/396/514/637 cm-1 plus rutile 446, 611",
    laser="532", sample="sol-gel TiO2, Nb2O5 and Ru-modified oxides after pressure-assisted heat treatment (PAHT), 400 and 800 C",
    table="N", raw="N", found="EuropePMC",
    notes="'Pressure' is a processing step, not in situ Raman under pressure. SI PDF in SI/."),
"ANA24": dict(ev="text p.5: white anatase at 147/156, 199/204, 401, 520, 643 cm-1 vs red (vacancy-rich) anatase 396, 511, 634 cm-1; laser-induced amorphous -> anatase -> rutile conversion in situ",
    laser="532", sample="oxygen-vacancy-rich (red) amorphous TiO2 powders vs white TiO2; laser-power-driven conversion to anatase/rutile",
    table="N", raw="N", found="EuropePMC",
    notes="Defect engineering; SI docx in SI/. The 405 nm line is used for photo-exposure; Raman used 532."),
"ANA25": dict(ev="text p.5: anatase 395, 515, 638 cm-1 vs rutile 445, 612 cm-1 (core-shell nanofibers); factor-group modes 144/197/399/519/639 quoted",
    laser="325; 514.5", sample="electrospun TiO2 nanofibers calcined at different temperatures (anatase/rutile core-shell), UV (325) and visible (514.5) Raman",
    table="N", raw="N", found="EuropePMC",
    notes="UV vs visible Raman comparison (surface vs bulk phase)."),
"ANA26": dict(ev="text p.14: anatase 144/197/399/515/519 cm-1 (and 638 cm-1 vs rutile 612 cm-1 on annealing); anatase 400 and 198 cm-1 shift to lower wavenumber 400-640 C",
    laser="325", sample="sol-gel TiO2 thin films on Si annealed 400-800 C (anatase -> rutile), UV Raman at 325 nm",
    table="N", raw="N", found="EuropePMC",
    notes="Several numbers are literature reference values plus trends (weaker entry); SI PDF in SI/. Data on request."),
"ANA27": dict(ev="SI Table S2 + text p.8: Eg(1) 147.5 -> 143.4, B1g(1) 396.9 -> 395.1, Eg(3) 638.7 -> 636.1 cm-1 with Hf/Ti 0 -> 0.05; Fig.5 labels all six modes",
    laser="1064", sample="Hf-doped anatase TiO2 (Ti1-xHfxO2, x = 0-0.05) on carbon-fibre template by sol-gel, 500 C",
    table="Y", raw="Y", found="EuropePMC",
    notes="FT-Raman (Bruker RFS-100/S, Nd:YAG 1064 nm). Raw Raman = SigmaPlot workbook data/unzipped/Data/Fig5 Raman/*.JNB from Dryad doi:10.5061/dryad.gf63r (mirrored on Zenodo 5021745); proprietary .JNB format, not plain text. Other figure data trimmed."),
"ANA28": dict(ev="text p.3: Eg(1) frequency 143 -> 148 cm-1 and widening with NaBH4 reduction (23 -> 20 nm); Eg ~144 cm-1 examined for the blue titania series",
    laser="632.8", sample="blue (partially reduced) TiO2 from P25 + NaBH4, N2 treated; anatase/rutile mixtures with defects",
    table="N", raw="Y", found="EuropePMC",
    notes="Raw micro-Raman in Origin projects (Micro Raman BTs.opj/.opju, 7+3 MB) from Mendeley Data doi:10.17632/ggbktsx5xj (CC BY 4.0); Origin format, not plain text. Only Eg(1) is quantified in the text."),
"ANA29": dict(ev="text p.6: anatase-only product shows 139 (intense) and 646 cm-1 (weak) bands; brookite A1g 149, 249...; polymorph-specific Raman shifts for rutile/anatase/brookite",
    laser="532", sample="TiO2 nanoparticles by PIT nano-emulsion with calcination; phase-pure anatase, brookite, rutile (low-energy synthesis)",
    table="N", raw="N", found="EuropePMC",
    notes="Thermo DXR Raman microscope; the 633 nm in the PDF is the DLS laser. Reference spectra for three polymorphs; SI PDF in SI/."),
"ANA30": dict(ev="text p.4: 147 (Eg), 199 (Eg), 399 (B1g), 518 (A1g+B1g), 643 (Eg) cm-1 for undoped TiO2 at 400 C; dominant peak shifts 147 -> ~140 cm-1 with Cu/Sn doping",
    laser="785", sample="Cu/Sn-doped TiO2 nanoparticles (sol-gel, calcined 400/500/600 C) for printed films",
    table="N", raw="Y", found="EuropePMC",
    notes="Raman is a short subsection (7 mentions) with explicit assigned peaks; included for raw 785 nm spectra. Zenodo doi:10.5281/zenodo.21597241 (Zip.rar): data/Dataset-sheet_25July.xlsx sheet 'Raman-Fig 4' = raw spectra at 3 calcination temperatures; Tables.pdf and description.docx in SI/."),
"ANA31": dict(ev="text p.3: anatase identified by modes at 395, 510, 635 cm-1; relative intensity changes (395 vs 635) between samples and under ExoMars-like instrument settings",
    laser="532", sample="natural anatase-bearing hydrothermal samples (Iceland, Mars analogues) measured at ExoMars-RLS-like Raman parameters",
    table="N", raw="N", found="EuropePMC",
    notes="EXTRA. Geoscience sample type (natural anatase in mixed mineral assemblages); only 3 anatase bands quoted; SI PDF in SI/."),
"ANA32": dict(ev="NOT VERIFIED (paper PDF not downloaded). ASU dataset README: in situ Raman of TiO2 anatase -> rutile transformation, 532 nm excitation, furnace run with thermocouple temperatures",
    laser="532", sample="TiO2 (anatase to rutile) transformation monitored in situ by a custom Raman system during furnace heating / microwave heating",
    table="N", raw="Y", found="WebSearch",
    notes="EXTRA, needs_manual: J. Raman Spectrosc. 2022 (Wiley, CC BY-NC-ND) PDF returns 403 and Wiley is blocked in the Browser pane. Raw data downloaded from ASU Dataverse doi:10.48349/ASU/SCXUIW: JJ196 furnace run (spectra csv 70 MB, temperature .tab, pixel-to-wavenumber map, README). NOT downloaded for size: JJ196 background csv (93 MB), JJ192 microwave-run spectra (28 MB) and background (39 MB), MATLAB scripts."),
"ANA33": dict(ev="text p.4: anatase bands 146, 396, 515, 640 cm-1 assigned Eg, B1g, (A1g, B1g), Eg; with Fe doping Eg FWHM ~15 -> 21 cm-1 and Eg shifts ~146 -> 151 cm-1 (Fig. S2c)",
    laser="785", sample="Fe-doped TiO2 nanoparticles: anatase at <=10 at.% Fe, anatase/rutile mixtures at 15-20 at.%, rutile >=30 at.% (oxygen-vacancy-driven transformation)",
    table="N", raw="N", found="EuropePMC",
    notes="EXTRA (Raman is one of several probes, 22 mentions, but peaks are assigned and FWHM/shift trends are quantified). 785 nm excitation; SI PDF in SI/."),
}
OA = {"ANA02": "Y (arXiv preprint)", "ANA07": "Y (accepted manuscript, institutional repository)", "ANA32": "Y (CC BY-NC-ND per Crossref)"}
EXTRA_URLS = {
    "ANA13": "https://doi.org/10.26022/IEDA/111495",
    "ANA27": "https://doi.org/10.5061/dryad.gf63r; https://zenodo.org/records/5021745",
    "ANA28": "https://doi.org/10.17632/ggbktsx5xj",
    "ANA30": "https://doi.org/10.5281/zenodo.21597241",
    "ANA32": "https://doi.org/10.48349/ASU/SCXUIW; https://doi.org/10.1002/jrs.6478",
}
rows = []
for fid in sorted(byid):
    doi, v = byid[fid]
    m = v["meta"]
    folder = v["folder"]
    d = os.path.join(OUT, folder)
    cur = C[fid]

    def files(sub):
        base = os.path.join(d, sub)
        out = []
        if os.path.isdir(base):
            for r, _, fs in os.walk(base):
                for f in fs:
                    out.append(os.path.relpath(os.path.join(r, f), d).replace("\\", "/"))
        return sorted(out)

    si = files("SI")
    data = [x for x in files("data") if not x.endswith("DATA_LINK.txt")]
    has_pdf = os.path.exists(os.path.join(d, "paper.pdf"))
    fa = m.get("first_author", "")
    gv = m.get("given", "")
    first = (fa + ", " + gv) if gv else fa
    src = v.get("src_url") or v.get("spec", {}).get("src_url", "")
    srcs = [src] if src else []
    if fid in EXTRA_URLS:
        srcs.append(EXTRA_URLS[fid])
    if fid == "ANA32":
        srcs = [EXTRA_URLS[fid]]
    rows.append(dict(paper_id=fid, folder=folder, doi=doi, title=m.get("title", ""), first_author=first,
                     year=m.get("year"), journal=m.get("journal", ""), open_access=OA.get(fid, "Y"),
                     raman_evidence=cur["ev"], laser_nm=cur["laser"], sample_description=cur["sample"],
                     peak_table=cur["table"], raw_data=cur["raw"],
                     pdf_status="downloaded" if has_pdf else "needs_manual",
                     si_files=";".join(si), data_files=";".join(data), source_urls="; ".join(srcs),
                     found_via=cur["found"], notes=cur["notes"]))
cols = ("paper_id,folder,doi,title,first_author,year,journal,open_access,raman_evidence,laser_nm,"
        "sample_description,peak_table,raw_data,pdf_status,si_files,data_files,source_urls,found_via,notes").split(",")
with open(os.path.join(OUT, "papers.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows")
