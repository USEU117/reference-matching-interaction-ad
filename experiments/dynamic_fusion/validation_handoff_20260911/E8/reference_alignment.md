# E8-8 Reference alignment: manuscript 33 vs working BibTeX 30

Rule: **do not fabricate bibliographic information the user has not supplied.**
This reconciliation records what exists, what is missing, and does not block any
independent experiment.

## 1. Counts

- `docs/manuscript_english_polished_20260906/English_content.md`, section
  `## References` (lines 381-445): **33 numbered entries**.
- `docs/paper_writing_preparation_20260830/references/curated_references.bib`:
  **30 `@` entries** (verified by counting `^@`).
- `docs/manuscript_english_polished_20260906/reference_number_map.json`: a
  33-entry old->new renumbering map (`13->26`, `17->27`, `28->33`, rest shifted
  by `14->13 ... 27->25`). It carries no bibliographic fields itself.
- Other `.bib` files in the repo
  (`docs/introduction_research_20260825/references.bib` = 8 entries,
  `.../references_latest_20260826.bib` = 12 entries) are strict subsets of the
  curated file and add nothing for the missing entries.

## 2. Mapping result

**Matched: 25 of 33.**

| manuscript # | bib key | manuscript # | bib key |
|---|---|---|---|
| 3 | damm2025anomalydino | 20 | ma2025aaclip |
| 5 | guo2026seaclip | 21 | zhu2025faprompt |
| 6 | zhang2024realnet | 22 | ma2025rempad |
| 8 | defard2021padim | 24 | ma2026papl |
| 9 | roth2022patchcore | 25 | jiang2025clipdino |
| 12 | li2026fastref | 26 | oquab2024dinov2 |
| 13 | gu2025univad | 27 | radford2021clip |
| 14 | lendering2026subspacead | 29 | jezek2021mpdd |
| 15 | jiang2026dcpsfr | 30 | mishra2021vtadl |
| 16 | jeong2023winclip | 31 | bergmann2019mvtec |
| 17 | zhou2024anomalyclip | 32 | zou2022spot |
| 18 | li2024promptad | 33 | wang2024realiad |
| 19 | zhu2024inctrl | | |

**Missing from every `.bib` in the repo: 8 entries** - `[1]`, `[2]`, `[4]`,
`[7]`, `[10]`, `[11]`, `[23]`, `[28]`. (Grep for their titles, e.g. `SLSG`,
`DMMGNet`, `Billion-scale`, in the curated bib returns no match.)

**Present in the bib but not cited by the manuscript: 5 entries** -
`park2026moeclip`, `hou2026visualad`, `hu2026fbclip`, `seo2026anoco`,
`lee2026anople`.

## 3. What is available and what is genuinely absent for the 8 missing entries

For all eight, the manuscript text **does** carry author initials, title, venue
abbreviation, volume, year and a DOI; the journal entries carry an article number
instead of a page range. What is **not** available anywhere in the repo is the
BibTeX entry/key itself and the authors' **full names** (and, for most, an
official paper landing-page URL).

| # | first author (as written) | venue / vol / art. | DOI |
|---|---|---|---|
| 1 | M. Yang et al. | Pattern Recognit., vol. 156, Art. 110862, 2024 | 10.1016/j.patcog.2024.110862 |
| 2 | A. Luo et al. | Neurocomputing, vol. 610, Art. 128622, 2024 | 10.1016/j.neucom.2024.128622 |
| 4 | J. Zhou et al. | Pattern Recognit., vol. 173, Art. 112759, 2026 | 10.1016/j.patcog.2025.112759 |
| 7 | Y. Bai et al. | Knowl.-Based Syst., vol. 302, Art. 112397, 2024 | 10.1016/j.knosys.2024.112397 |
| 10 | Z. Hu et al. | Chin. J. Aeronaut., vol. 38, no. 3, Art. 103098, 2025 | 10.1016/j.cja.2024.06.007 |
| 11 | S. Wei et al. | Knowl.-Based Syst., vol. 300, Art. 112168, 2024 | 10.1016/j.knosys.2024.112168 |
| 23 | L. Xu et al. | Adv. Eng. Inform., vol. 68, pt. C, Art. 103792, 2025 | 10.1016/j.aei.2025.103792 |
| 28 | J. Johnson, M. Douze, H. Jegou | IEEE Trans. Big Data, vol. 7, no. 3, pp. 535-547, 2021 | 10.1109/tbdata.2019.2921572 |

Missing fields to supply: BibTeX entry + key, full author names, and (for seven
of the eight) an official paper URL. Entry `[28]` additionally already has a page
range in the manuscript.

## 4. One textual inconsistency (not a missing entry)

Manuscript `[14]` spells the first author "E. Bondarev", while
`curated_references.bib` has `Bondarau, Egor`. One of the two must be corrected
during copy-editing; the correct commercial form was not determined from the
repo and is **not** guessed here. This is already noted in
`docs/project_review_20260910/paper_audit.md:34`.

## 5. Consequences

- The manuscript is internally consistent (33 cited, 33 listed); the gap is
  between the manuscript list and the working `.bib`, so a BibTeX-driven build
  would drop 8 citations until they are added.
- Filling these entries requires author-supplied or publisher metadata; it is a
  copy-editing/preparation task and is explicitly **not** allowed to delay any
  independent experiment.
- No `.bib` file and no manuscript file was modified by this round.
