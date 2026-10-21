"""Write calcite/candidates_rejected.csv. python -P build_rejected.py SCRATCH PROJECT_ROOT"""
import sys, os, json, csv, glob, html, re

SC, ROOT = sys.argv[1], sys.argv[2]
titles = {}


def put(doi, t):
    if doi and t and doi.lower() not in titles:
        titles[doi.lower()] = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()


for p in ["cands1.json", "cands2.json", "s2cands.json", "epmc1.json", "epmc2.json", "funnel.json"]:
    fp = os.path.join(SC, p)
    if os.path.exists(fp):
        d = json.load(open(fp))
        items = d.items() if isinstance(d, dict) else [("", v) for v in d]
        for k, v in items:
            if isinstance(v, dict):
                put(v.get("doi") or (k if k.startswith("10.") else ""), v.get("title"))
for fp in glob.glob(os.path.join(SC, "stage", "*", "result.json")):
    r = json.load(open(fp))
    put(r.get("doi"), r.get("title"))

R = []


def rej(doi, reason, title=None):
    R.append((doi, title or titles.get(doi.lower(), ""), reason))


NM = "needs_manual: "
# blocked / needs_manual (valuable but not retrievable without bypassing a bot challenge or paywall)
rej("10.2138/am-2018-6442", NM + "American Mineralogist/GSW returned a JS interstitial (202) and doi.org timeouts; no scriptable OA copy found. Companion Farsang 2020 is kept (CAL20)")
rej("10.1016/j.pepi.2018.05.002", NM + "ScienceDirect bot challenge; no repository copy (CaCO3 phase diagram to 50 GPa, Bayarjargal 2018)")
rej("10.1039/c4cp01772b", NM + "RSC articlepdf blocked by Cloudflare (temperature-sensitive modes of CaCO3 minerals, Xu 2014)")
rej("10.1016/j.saa.2021.119980", NM + "Elsevier blocked; HAL copy (hal-05224353) protected by Anubis proof-of-work bot check, not bypassed")
rej("10.1016/j.matdes.2025.114165", NM + "Elsevier 503/blocked; HAL copy (hal-05305254) behind Anubis bot check")
rej("10.1002/jrs.6810", NM + "Wiley Cloudflare challenge (Mg-calcite thermometer in mortars, Zollner 2025)")
rej("10.3390/min13020188", NM + "MDPI returns Access Denied to scripted requests (calcite reverse transition to 873 K)")
rej("10.3390/min13111358", NM + "MDPI/preprints.org Access Denied (Revisiting the Raman spectra of carbonate minerals)")
rej("10.3390/min8060221", NM + "MDPI Access Denied (Borromeo 2018, calcite Raman in flooded chalk)")
rej("10.3390/pr13113413", NM + "MDPI Access Denied (crab shell Mg-calcite, Lazar 2025)")
rej("10.3390/w15142591", NM + "MDPI Access Denied (biogenic powder from crustacean waste, Nekvapil 2023)")
rej("10.3390/min10060522", NM + "MDPI Access Denied (rose-like calcite crystal clusters)")
rej("10.3390/cryst13010051", NM + "MDPI Access Denied (calcite from Fujian, Raman peak tables likely)")
rej("10.3390/cryst16050297", NM + "MDPI Access Denied (yellow/pink calcite)")
rej("10.3390/cryst16080523", NM + "MDPI Access Denied (blue calcite)")
rej("10.3390/cryst13010048", "Downloaded and verified but dropped: mostly 18O DFT/vaterite focus, experimental calcite peak numbers sparse in main text (SI Tables S3/S4 on MDPI not retrievable)",
    "Evaluating the Effect of 18O Incorporation on the Vibrational Spectra of Vaterite and Calcite")
rej("10.1016/j.saa.2026.128616", NM + "ScienceDirect bot challenge (Raman detection of 17O substitution in calcite, Inoue 2026)")
rej("10.1016/j.pss.2021.105356", NM + "ScienceDirect bot challenge (deep-UV 248 nm Raman library of 62 minerals incl. calcite, SHERLOC)")
rej("10.1002/jrs.6174", NM + "Wiley blocked; BAM OPUS copy (opus4.kobv.de/opus4-bam/files/53761) behind Anubis bot check (Schmid 2021, Raman spectra of Ca and Mg carbonates)")
rej("10.1002/jrs.4622", NM + "Wiley paywall/Cloudflare; no OA copy (Schmid 2014/15 Part 1)")
rej("10.1007/bf00202245", NM + "Springer Client Challenge page; EPFL Infoscience record has metadata only (Gillet 1993 Raman of carbonates part I, high P-T calcite)")
rej("10.1016/0016-7037(96)00178-0", NM + "Elsevier; EPFL record has no file (Gillet 1996, 18O-substituted calcite vibrational spectra)")
rej("10.1007/bf02847889", NM + "Pramana 1981 (Sood) Springer Client Challenge; IAS repository link dead")
rej("10.1007/bf03050551", NM + "Bhagavantam 1940 (crystal orientation, calcite Raman) Springer challenge; IAS PDF URL not located")
rej("10.1088/0022-3719/7/24/015", NM + "IOP Radware bot captcha (Rutt & Nicola 1974 Raman spectra of carbonates of calcite structure)")
rej("10.1155/2013/254964", NM + "Hindawi/Wiley 403 (Raman spectroscopy of Iranian calcite, pulsed laser)")
rej("10.1002/jrs.70211", NM + "Wiley Cloudflare (CaRPP carbonate Raman processing tool, DeCarlo 2026); Zenodo data/demos 2.9 GB not downloaded")
rej("10.1021/acssensors.6c01924", NM + "ACS Cloudflare; raw data on Zenodo 10.5281/zenodo.19868283 (195 MB zip, not downloaded). Calcite/vaterite Raman polymorph labels",
    "Raman-Grounded Deep Learning for Calcium Carbonate Polymorph Sensing during Microfluidic Biomineralization")
rej("10.1111/gbi.12424", NM + "Wiley Cloudflare; HAL copy behind Anubis. Achromatium ACC vs calcite; raw Raman txt on Zenodo 10.5281/zenodo.4295976 (24 MB, not downloaded; ACC focus)")
rej("10.1111/sed.13170", NM + "Wiley Cloudflare (fibrous calcite cement); Raman spectra deposited at PANGAEA 10.1594/PANGAEA.964859")
rej("10.1088/1674-1056/ac6157", NM + "IOP Radware captcha; raw Raman spectra of calcite-III on ScienceDB 10.57760/sciencedb.01838 (JS-only download page, not scripted)")
rej("10.2138/am-2022-8406", NM + "GSW 403 (octocoral Raman, Conner 2023)")
rej("10.2138/am.2013.4305", NM + "no OA copy located (portable Raman of multi-mineral carbonate powders)")
rej("10.1002/jrs.5156", NM + "Wiley paywall (Borromeo 2017 Mg estimation in Mg-calcite)")
rej("10.1002/jrs.5893", NM + "Wiley paywall (calcite/Mg-calcite/dolomite Raman pressure sensors)")
rej("10.1089/ast.2009.0388", NM + "Liebert paywall; HAL record closed (Rividi 2010 carbonate composition by micro-Raman)")
rej("10.1021/cg800368u", NM + "ACS paywall; HAL record closed (Carteret 2009 lattice phonon Raman polymorphs)")
rej("10.1016/j.vibspec.2017.12.005", NM + "Elsevier paywall (anhydrous CaCO3 polymorph quantification)")
rej("10.1080/05704928.2020.1729170", NM + "Taylor & Francis; Jyvaskyla repository 503; supplement on figshare 10.6084/m9.figshare.11887848")
rej("10.1016/j.gca.2015.12.006", NM + "Elsevier; CSIC handle server returned 500 (ikaite to calcite Raman)")
rej("10.1039/c5ce00441a", NM + "RSC blocked (ACC film pseudomorphic transformation)")
rej("10.1029/2025gl118919", NM + "Wiley Cloudflare (calcite-aragonite-calcite gorgonian skeleton)")
rej("10.1103/physrevb.28.2172", NM + "APS paywall (photoelastic constants of calcite from first-order Raman)")
rej("10.1063/1.1746944", NM + "AIP paywall (Low frequency Raman spectrum of calcite, 1948)", "Low Frequency Raman Spectrum of Calcite")
rej("10.1063/1.1674881", NM + "AIP paywall (Raman spectrum of CaCO3 at high pressures, 1971)", "Raman Spectrum of Calcium Carbonate at High Pressures")
rej("10.1127/ejm/4/2/0389", NM + "Schweizerbart paywall (Gillet 1992 HP-HT calcite, aragonite, dolomite)")
rej("10.1002/jrs.4929", NM + "Wiley; Parma repository (hdl 11380/1315677) returned HTML only (carbonation of lime paste)")
rej("10.1016/j.gca.2016.10.048", NM + "Elsevier; no PDF at repository link (organo-carbonate Raman in chondrites)")
# verified PDFs rejected on content
rej("10.5194/se-13-1495-2022", "Downloaded and verified PDF but calcite only mentioned twice and no calcite peak positions in text (carbonate Raman spectral parameters in thrust sheets); not a calcite peak table")
rej("10.2138/am-2016-5558", "Theory only (first-principles Raman of calcite under differential stress); no measured spectra")
rej("10.3390/nano10112275", "DFT study of carbonate vibrational spectra; compiles literature values, no new Raman measurements")
rej("10.3390/s21113644", "First-principles carbonates under pressure; theory only")
rej("10.1371/journal.pone.0199695", "Stimulated Raman imaging of foraminifera: only the Mg-calcite ~1092 cm-1 resonance is quoted; raw data on PANGAEA 10.1594/PANGAEA.882289 but no peak table")
rej("10.1371/journal.pone.0204577", "Raman only briefly used for aragonite-calcite transformation; no calcite peak numbers")
rej("10.1038/s41598-019-56144-0", "Raman not reported with peak numbers (microbial carbonate, XRD focus)")
rej("10.1038/s41598-020-73870-y", "Raman peaks quoted only for ACC (1084) and vaterite; no calcite peak numbers")
rej("10.1038/s41598-025-14083-z", "Valid (calcite 1089, 715, 156, 262 cm-1 in text; SI Fig S3) but weaker than kept papers; held in reserve (532 nm, MICP)")
rej("10.1016/j.saa.2013.06.121", "Downloaded and verified (Zenodo author copy) but calcite peak numbers are only figure labels and the generic ~1085 cm-1 band in text; Raman used for kinetics. Replaced by Dubey 2025; raw-free")
rej("10.3390/md18020123", "Valid (biogenic calcite 1083, 1433, 711, 279 cm-1) but laser not stated and weaker than kept papers; held in reserve")
rej("10.3390/ijms222212588", "Calcite identified mainly by FTIR/NEXAFS; Raman peak numbers not given")
rej("10.3389/feart.2019.00051", "Raman not central; no calcite peak positions")
rej("10.3389/fmicb.2018.00796", "Raman used for phase ID only; peak numbers not given")
rej("10.1038/s41467-018-07601-3", "Coral aragonite Raman (peak widths); calcite only as RRUFF reference link")
rej("10.1111/gcb.14579", "Aragonite-focused in vivo Raman; no calcite peak table")
rej("10.1111/gcb.12351", "Valid but weak (only nu1 ~1089 cm-1 position/width of coralline algal Mg-calcite, 785 nm); held in reserve")
rej("10.1098/rsos.231280", "Raman nu1 ~1088 cm-1 used as Mg proxy; no peak table or other modes")
rej("10.1038/s41598-021-92235-7", "Raman confirms calcite with few numbers (1085/1086/155), not a peak study")
rej("10.3390/ma15196616", "Raman confirms bacterial calcite in mortar with a few numbers; weak")
rej("10.3390/ma14071798", "Carbonation profile in cement: nu1 1085 cm-1 only (514.5 nm); weak")
rej("10.1111/jmi.13084", "Cement carbonation Raman mapping: calcite 280/1085 mentioned only for mapping")
rej("10.3390/ma18225119", "Raman on aged crustacean-waste carbonates, few numbers (1085/154); weak")
rej("10.3390/ma19030624", "Valid but weak (calcite 151, 275, 712, 1085 cm-1 in a meteorite); held in reserve")
rej("10.3390/biomimetics10040211", "Valid but weak (spicule peaks 281-283, 707-720, 1087-1088 cm-1); held in reserve")
rej("10.3390/ani13132231", "Pearl Raman (aragonite/vaterite dominant); calcite numbers limited")
rej("10.3390/foods13162607", "Food application; Raman peak numbers for calcite not reported")
rej("10.3390/microorganisms9081691", "MICP; Raman peak numbers minimal")
rej("10.1021/acsomega.5c06632", "Raman maps in pre-salt silica spheres; calcite bands only named (1086, 713)")
rej("10.1021/acsomega.1c03285", "Only nu1 1085 cm-1 (785 nm) quoted for Mg-calcite drug carrier")
rej("10.1038/s41598-022-12379-y", "Geology paper; calcite Raman numbers incidental")
rej("10.1038/s41598-018-19485-w", "Soluble salts in Pompeii house; calcite Raman incidental")
rej("10.1038/s41598-022-06721-7", "Otolith mineralogy (aragonite); calcite incidental")
rej("10.3390/nano11113099", "Raman/XANES of biogenic carbonate environments; calcite peak numbers minimal")
rej("10.1016/j.dib.2016.04.019", "Data in Brief on mineral precipitation protocol; only one calcite peak (1086)")
rej("10.1039/d4ra07137a", "Microchannel CaCO3 polymorphs; Raman minor (156 only)")
rej("10.1021/acs.langmuir.5c01363", "Langmuir CaCO3 nucleation with MEG; Raman minor")
rej("10.1039/d5ra05023e", "CaO CO2-capture 18O labelling; Raman calcite peaks incidental; Zenodo data are TGA/MS")
rej("10.1038/s42003-025-09065-w", "Raman used only to identify calcite/vaterite (no calcite peak numbers); SI xlsx has raw Raman spectra but fails the peak-number criterion")
rej("10.1038/s41598-022-13731-y", "Coralline algae mineralogy; Raman only quotes calcite 284 cm-1 as marker")
rej("10.1371/journal.pone.0113150", "Download failed verification (PDF title/Raman mismatch); mantle-cell ACC paper, not calcite peak data")

out = os.path.join(ROOT, "calcite", "candidates_rejected.csv")
seen = set()
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["doi", "title", "reason"])
    for doi, t, reason in R:
        if doi in seen:
            continue
        seen.add(doi)
        w.writerow([doi, t, reason])
print(len(seen), "rows;", sum(1 for d, t, r in R if not t), "without title")
