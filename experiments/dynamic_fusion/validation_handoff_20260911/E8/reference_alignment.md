# E8-8 Reference alignment: manuscript 33 cited vs working BibTeX

Rule: **do not fabricate bibliographic information.** Fields that were not in the
repo were retrieved from an authoritative bibliographic source (Crossref REST API),
and the retrieval is recorded below; nothing is inferred, guessed or invented.

Status: **closed** (2026-09-12). The working `.bib` now carries an entry for every
citation the manuscript lists.

## 1. Counts

- `docs/manuscript_english_polished_20260906/English_content.md`, section
  `## References` (lines 381-445): **33 numbered entries**.
- `docs/paper_writing_preparation_20260830/references/curated_references.bib`:
  **38 `@` entries** after this round (was 30).
- `docs/manuscript_english_polished_20260906/reference_number_map.json`: a
  33-entry old->new renumbering map (`13->26`, `17->27`, `28->33`, rest shifted
  by `14->13 ... 27->25`). It carries no bibliographic fields itself.
- Other `.bib` files in the repo
  (`docs/introduction_research_20260825/references.bib` = 8 entries,
  `.../references_latest_20260826.bib` = 12 entries) are strict subsets of the
  curated file and add nothing.

## 2. Mapping result

**Matched: 33 of 33** (was 25 of 33).

| manuscript # | bib key | manuscript # | bib key |
|---|---|---|---|
| 1 | yang2024slsg | 18 | li2024promptad |
| 2 | luo2024dmmgnet | 19 | zhu2024inctrl |
| 3 | damm2025anomalydino | 20 | ma2025aaclip |
| 4 | zhou2026oneshot | 21 | zhu2025faprompt |
| 5 | guo2026seaclip | 22 | ma2025rempad |
| 6 | zhang2024realnet | 23 | xu2025mfcr |
| 7 | bai2024dpfd | 24 | ma2026papl |
| 8 | defard2021padim | 25 | jiang2025clipdino |
| 9 | roth2022patchcore | 26 | oquab2024dinov2 |
| 10 | hu2025aft | 27 | radford2021clip |
| 11 | wei2024fewshotonline | 28 | johnson2021faiss |
| 12 | li2026fastref | 29 | jezek2021mpdd |
| 13 | gu2025univad | 30 | mishra2021vtadl |
| 14 | lendering2026subspacead | 31 | bergmann2019mvtec |
| 15 | jiang2026dcpsfr | 32 | zou2022spot |
| 16 | jeong2023winclip | 33 | wang2024realiad |
| 17 | zhou2024anomalyclip | | |

**Still present in the bib but not cited by the manuscript: 5 entries** -
`park2026moeclip`, `hou2026visualad`, `hu2026fbclip`, `seo2026anoco`,
`lee2026anople`. These are intentional related-work spares, not a defect.

## 3. Closure of the 8 previously missing entries

On 2026-09-12 the eight entries that existed in no `.bib` file were added to
`curated_references.bib`. The manuscript text carried author initials, title,
venue abbreviation, volume, year and DOI for all eight; the missing fields were
the BibTeX entry/key, the authors' **full given names**, and (for seven) an
official landing URL. Those were retrieved from the **Crossref REST API**
(`https://api.crossref.org/works/<doi>`), which is the DOI registration agency's
own metadata, so no field is author-supplied hearsay.

Retrieved values (all eight re-queried and confirmed on 2026-09-12):

| # | bib key | full author list | venue / vol / no / art. | year | DOI |
|---|---|---|---|---|---|
| 1 | `yang2024slsg` | Minghui Yang, Jing Liu, Zhiwei Yang, Zhaoyang Wu | Pattern Recognition, 156, Art. 110862 | 2024 | 10.1016/j.patcog.2024.110862 |
| 2 | `luo2024dmmgnet` | Aoshuang Luo, Guojun Wen, Yahui Cheng, Shuang Mei, Hongbo Dong, Xingyue Liu | Neurocomputing, 610, Art. 128622 | 2024 | 10.1016/j.neucom.2024.128622 |
| 4 | `zhou2026oneshot` | Jiayin Zhou, Waikeung Wong, Fangjian Liao | Pattern Recognition, 173, Art. 112759 | 2026 | 10.1016/j.patcog.2025.112759 |
| 7 | `bai2024dpfd` | Yuhu Bai, Jiangning Zhang, Zhaofeng Chen, Yuhang Dong, Yunkang Cao, Guanzhong Tian | Knowledge-Based Systems, 302, Art. 112397 | 2024 | 10.1016/j.knosys.2024.112397 |
| 10 | `hu2025aft` | Zhengnan Hu, Xiangrui Zeng, Yiqun Li, Zhouping Yin, Erli Meng, Leyan Zhu, Xianghao Kong | Chinese Journal of Aeronautics, 38(3), Art. 103098 | 2025 | 10.1016/j.cja.2024.06.007 |
| 11 | `wei2024fewshotonline` | Shenxing Wei, Xing Wei, Zhiheng Ma, Songlin Dong, Shaochen Zhang, Yihong Gong | Knowledge-Based Systems, 300, Art. 112168 | 2024 | 10.1016/j.knosys.2024.112168 |
| 23 | `xu2025mfcr` | Luo Xu, Delong Han, Gang Li, Mingle Zhou, Jin Wan, Min Li | Advanced Engineering Informatics, 68, Art. 103792 | 2025 | 10.1016/j.aei.2025.103792 |
| 28 | `johnson2021faiss` | Jeff Johnson, Matthijs Douze, Herve Jegou | IEEE Trans. Big Data, 7(3), pp. 535-547 | 2021 | 10.1109/TBDATA.2019.2921572 |

Notes on the two entries where the manuscript and Crossref both describe a
non-page locator:

- Journal entries whose manuscript locator is an **article number** (entries 1,
  2, 4, 7, 10, 11, 23) are stored with `pages = {<article no.>}`, matching the
  existing `ma2026papl` convention in the same file. Crossref reports the same
  value in both `page` and `article-number` for these records.
- Entry 23's manuscript text reads "vol. 68, pt. C, Art. no. 103792". Crossref
  exposes volume 68 and article 103792 but no part designator, so the `pt. C`
  qualifier was **not** written into the bib (it cannot be sourced). The entry
  is otherwise complete.
- Entry 28 is the only one with a real page range (535-547), which the
  manuscript already carried and Crossref confirms.

## 4. [14] author-name inconsistency: resolved

Manuscript `[14]` reads "C. Lendering, E. Akdag, and E. **Bondarev**", while the
bib previously had `Bondarau, Egor`. The manuscript spelling is correct: the
CVPR 2026 SubspaceAD paper (`SubspaceAD: Training-Free Few-Shot Anomaly
Detection via Subspace Modeling`, Lendering / Akdag / Bondarev, Eindhoven
University of Technology) uses **Bondarev**. `curated_references.bib` was
corrected to `Bondarev, Egor` on 2026-09-12; the manuscript needed no change.

## 5. Consequences

- The manuscript is internally consistent (33 cited, 33 listed) **and** the
  working `.bib` now resolves all 33, so a BibTeX-driven build no longer drops
  the eight citations.
- 5 uncited spares remain in the bib by design (see §2); they affect no build.
- The only residual, explicitly recorded, non-sourced element is the `pt. C`
  part designator for entry 23 (see §3).
- This reconciliation is a copy-editing task and was never allowed to gate any
  independent experiment. No numeric result in E1-E8 depends on it.

## 6. Files touched in this closure

- `docs/paper_writing_preparation_20260830/references/curated_references.bib`
  (+8 entries, [14] author corrected; 30 -> 38 entries).
- This file.
