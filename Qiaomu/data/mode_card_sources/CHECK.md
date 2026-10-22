# Mode card check (2026-10-21, checker agent)

This sheet checks the **curated expected modes** (positions, widths, paper labels) of the two primary-paper cards in `primary_v1/` against their source tables. `scripts/build_mode_cards.py` copies these values unchanged into `mode_cards_simplified/<material>.json`, `mode_cards_comprehensive/<material>_comprehensive.json` and their repo-root copies in `mode_cards/`, and `scripts/validate_project.py` confirms they still match. Human teammate sign-off is still pending.

Method: the table pages were rendered at 300 dpi (`_check/cal_p4_table_crop.png`, `_check/ana_p3_table_crop.png`, plus full pages) and read by eye, and compared with the PDF text layer. No numbers were changed.

## calcite (primary_v1/calcite_v1.json;  Bischoff, Sharma, MacKenzie 1985, Table 1, printed p.584, row "Calcite")

Table prints frequency (upper) and halfwidth (lower, FWHM per the text on p.583). Columns in the paper: T, L, v4, v1, v3, 2 x v2.

| mode | card value (cm-1: position / halfwidth; label) | value in paper | OK? |
|---|---|---|---|
| Eg(T) | 154 / 6.2; "T" | 154* / 6.2; T | OK |
| Eg(L) | 281 / 10.1; "L" | 281 / 10.1; L | OK |
| nu4 | 711 / 3.6; "v4" | 711 / 3.6; v4 | OK |
| nu1 | 1085 / 2.5; "v1" | 1085 / 2.5; v1 | OK |
| nu3 | 1434 / 2.0; "v3" | 1434 / 2.0; v3 | OK |
| 2nu2 | 1748 / 3.6; "2 x v2" | 1748 / 3.6; 2xv2 | OK |

source_paper: citation (authors, 1985, Am. Mineral. 70, 581-589, title) OK; location "Table 1 (p.584), row Calcite" OK; laser_nm 488 OK (488.0 nm Ar+ laser, powdered samples, Experimental procedures).
Problems: none. (The asterisk on 154 is the table footnote "Upper value is frequency, lower value is halfwidth", not a caveat on the value.)

## anatase (primary_v1/anatase_v1.json;  Ishioka & Petek 2012, PRB 86, 205201, Table I, Raman columns, PDF p.3)

Table prints Raman frequency, HWHM, assignment. (The separate transient-reflectivity columns, e.g. 195, 395, 507, 637, are not used by the card.)

| mode | card value (cm-1: position / HWHM; label) | value in paper | OK? |
|---|---|---|---|
| Eg(1) | 145 / 5; "Eg (nu6)" | 145 / 5; Eg(v6) | OK |
| Eg(2) | 199 / 2; "Eg (nu5)" | 199 / 2; Eg(v5) | OK |
| B1g(1) | 396 / 10; "B1g (nu4)" | 396 / 10; B1g(v4) | OK |
| A1g+B1g(2) | 517 / 11; "B1g (nu2) / A1g (nu3)" | 517 / 11; B1g(v2)/A1g(v3) | OK |
| Eg(3) | 638 / 11; "Eg (nu1)" | 638 / 11; Eg(v1) | OK |

source_paper: citation (Ishioka et al., 2012, PRB 86, 205201, title) OK (second author is H. Petek); location "Table I, PDF p.3" OK; laser_nm 532 OK ("Separate Raman scattering measurements are performed with 532 nm excitation"; the 400 nm light is the pump-probe, not the Raman laser); natural anatase single crystal OK (Section II).
Problems: none.
