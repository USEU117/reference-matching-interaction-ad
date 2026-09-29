# 历史自检缺口影响说明（2026-09-28，只读核查）

> 依据：`docs/PAPER_COMPLETION_20260928_CN.md` 第 3 条四步中的第 ①② 步（找备份记录来源与校验值 → 登记缺口与影响核查）；
> 处置纪律取自 `docs/paper_evidence_completion_20260927/legacy_selfcheck/SELFCHECK.json` evidence_lines[3]：
> **不修改旧自检记录、不伪造缺失文件、不把文件恢复到旧位置冒充旧时点状态**。
>
> 本轮操作范围：**只读检索**（git 历史、盘上文件、冻结清单、既有登记文档）。唯一写入是本说明文件。
> 未执行：git 提交/暂存、旧报告改写、缺失文件回填、任何实验。

---

## 1 权威记录：67/69 具体是哪两条失败

| 项 | 值 |
|---|---|
| 运行结果 | `checks = 69, passed = 67, failed = 2`，退出码 1 |
| 失败 ① | `read-only inputs were not written during this delivery` |
| 失败 ② | `manuscript: the updated outline exists` |
| 报告文件 | `docs/paper_evidence_completion_20260927/legacy_selfcheck/SELFCHECK.json`（SHA-256 `12712E01DBBE46894F9179E36B42A33166399237F3DD11103EE9BB3DAE0FDDBF`，12,863 B；与 `engineering_audit.json:445`、`:908` 登记值一致）；同目录 `READONLY_PROOF.json`（`5CD8D714C579C4D0A64B4FAC8D1001AF73119D681182D5116B7ED7C4B4559D97`，26,645 B；无既有登记，本说明实测首次登记） |
| 运行前备份 | 仓库根 `.bak_selfcheck_20260923/{SELFCHECK.json, READONLY_PROOF.json}`（`SELFCHECK.json` 12,665 B / `C664A309BC6719DCB0D4E349C6608D89E01A703D3B6B9D8242985930BD5FF74E`；`READONLY_PROOF.json` 25,994 B / `914312038FC72FD1B496FC5F9868FA1C37E8B7B09F8987186B507EE3E3D78B75`；被 `.gitignore:77 *.bak*` 覆盖） |
| 既有登记 | `docs/ARTIFACT_INDEX.md:285`；`docs/FINAL_REPAIR_AND_ACCEPTANCE_20260923.md:396-400`；`docs/论文与图件问题汇总_仅复核_20260921.md:541-542` |

SELFCHECK.json 中两条失败的原始 detail（逐字）：

```
FAIL read-only inputs were not written during this delivery
  modified=[
    {..._smoke\units\mpdd_s0_k2\bracket_black\evaluation_scores.npz, why: missing},
    {..._smoke\units\mpdd_s0_k2\bracket_black\patch_scores.npz, why: missing},
    {...\unified_fusion_paper_support_20260913\REPORT_CN.md,
     why: size 10029 -> 10029; mtime delta 760387.799s}]
FAIL manuscript: the updated outline exists
  新主题论文详细提纲_外部评审版_20260914_更新版.docx: path absent
```

失败机理（脚本实读）：
- 失败 ① 由 `scripts/representation_matching_interaction_20260914/selfcheck.py:317-340` 产生：遍历
  `experiments/dynamic_fusion/representation_matching_interaction_20260914/00_protocol/INPUT_FREEZE.json`
  的冻结条目做只读校验，缺失或 mtime 漂移即计入 `modified`，非空则整条检查 FAIL。
- 失败 ② 由 `selfcheck.py:494-499` 产生：要求
  `docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx`
  存在且 > 40,000 字节。其后 500-512 行的两条内容检查是**条件检查**（两份提纲都在盘才计入），
  当时因文件缺失未计入 69 项——这也是"69 项"这个分母的由来。

---

## 2 缺口一：`_smoke` 下两个 NPZ —— **不可恢复，登记为历史追溯缺口**

### 2.1 冻结记录（校验值仍完整留档，来源可追）

| 字段 | evaluation_scores.npz | patch_scores.npz |
|---|---|---|
| 相对路径 | `experiments/dynamic_fusion/unified_fusion_paper_support_20260913/_smoke/units/mpdd_s0_k2/bracket_black/` | 同左 |
| size | 11,326,699 B | 5,871,773 B |
| sha256 | `0b2bcbe7393e4241f9f9db53083ea3358d7ffe7e05e282f3a35e88b7f084a54c` | `45ee7a8d930e479c2500103114ea57c42cff003e785554ac8c543d1eb4756dbd` |
| 冻结 mtime_utc | 2026-09-13T12:34:53.690628+00:00 | 2026-09-13T12:34:45.818250+00:00 |
| 双重留档 | `00_protocol/INPUT_FREEZE.json`（label `R_study`）与同目录 `ARTIFACT_MANIFEST.json` 均有同值记录 | 同左 |

### 2.2 备份检索结论（四路全空）

1. **git 历史**：`git log HEAD -- <两路径>` 无任何提交记录（从未入库）。原因：`.gitignore:38 *.npz`
   全局忽略。`git status --porcelain -- .../unified_fusion_paper_support_20260913` 输出为空
   （被忽略文件不产生 ` D` 条目，故与"工作区无删除"的既有登记一致）。
2. **本仓库盘上**：全盘递归检索 `evaluation_scores.npz` / `patch_scores.npz`，命中均在
   `p1_matrix/`、`seeds_extension_20260917/`、`confirmation_ksdd2_20260918/` 等**其他目录**，
   `_smoke/units/mpdd_s0_k2/bracket_black/` 下不在其中；该单元现存 11 个文件
   （冻结清单 13 项 − 缺失 2 项 = 11，`reference_permutations.npz`、`sample_pairs.npz` 等仍在）。
3. **另一工作区**：`d:\STUDY\My_github\sci_project\...\_smoke\units\mpdd_s0_k2\bracket_black`
   同样只有 11 个文件、缺同两个 NPZ（`DONE.json` 内的绝对路径显示该冒烟最初在 sci_project 工作区跑出）。
4. **发布/复现包与外部盘**：`dist/release_candidate_20260927`、`dist/replication_package_20260920`
   内的 NPZ 均属 `prereg_20260924` 等其他实验，无此二文件；OneDrive 候选路径
   `D:\OneDrive_Yinghua\桌面\交互式参考匹配` 不存在。

**结论**：四路检索皆空 → **不可恢复**。按纪律不伪造、不回填，正式登记为历史追溯缺口；
其 size+sha256 冻结记录保留在 INPUT_FREEZE.json / ARTIFACT_MANIFEST.json 中，可作为"曾经存在且未被篡改"的证据。

### 2.3 伴生漂移项：`REPORT_CN.md` —— **内容未变，仅 mtime 漂移**

- 冻结：size 10029、sha256 `4be30fbce1d54a7de7b86950885491d2c76e9730707b0a2453804e5ecf59558b`、mtime 2026-09-13T16:56:13Z。
- 本轮实测：size 10029、sha256 **完全相同**、mtime 2026-09-22T12:09:20Z（漂移 760,387.8 s ≈ 8.8 天）。
- **判定：内容字节级未变，仅时间戳变化**（属既有登记的"只读证明误报"成分，不构成内容风险）。

### 2.4 影响核查：对当前论文结果 **无影响**

- `_smoke` 是冒烟自测夹具，不是结果：与 `docs/ARTIFACT_INDEX.md:131-133` 对同族冒烟目录的定性一致
  （"其内容从来不是结果""引用时不是结果""明确不得引用其数字"）。
- 论文的数值结果来自 `p1_matrix/`、`p4_fullpixel/`、`EXT/`、`NEW/` 等目录，**完整在盘**；
  `p1_matrix/units/mpdd_s0_k2/bracket_black/evaluation_scores.npz` 存在，与 `_smoke` 同名单元互不相干。
- 代码引用面：全仓 `.py` 中对该冒烟 NPZ 的引用只有
  `scripts/paper_evidence_completion_20260927/engineering_audit.py:56-59`（`SCRATCH_RELATIVE`，
  登记性审计用途）；`selfcheck.py` 不直接引用，仅经 INPUT_FREEZE 遍历触发。
  无任何论文表/图/统计脚本读取 `_smoke` 下的 NPZ。
- **影响面**：论文结果 = 无；证据完整性 = 冻结校验值仍留档；唯一实质影响是
  **失败 ① 在现状下重跑必然复现**（除非按第 5 节处置）。

---

## 3 缺口二：旧提纲"更新版" docx —— **内容级可恢复，字节同一性不可证明**

### 3.1 现状

- `docs/paper_outline_review_20260914/` 与 `docs/paper_outline_teacher_review_20260914/`
  两个目录**均不在盘**；全盘无任何 `*提纲*.docx`。
- 期望路径：`docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx`
  （检查要求 > 40,000 B）。

### 3.2 git 检索（**更正此前登记中"git 对象也没有"的说法**）

| blob | 字节数 | SHA-256（本轮实测） | git 路径（旧名） |
|---|---|---|---|
| `3022c4fe87791c57eadb8131b534a5529bfd6fe6` | 64,732 | `287b7a03ea54915bfa6d187b573fe29f42b52809d4497960e7f663435eb28fcf` | `docs/paper_outline_teacher_review_20260914/新主题论文详细提纲_导师审阅版_20260914_更新版.docx` |
| `6f7e3edca8d772bc1526551219c087e29e2ebb08` | 73,801 | `de5a76d40678fd071b0b863ca533374c2b049c413fef06ec4600d33fa26436cb` | 同目录 `…_导师审阅版_20260914.docx`（原版） |

时间线（`git log HEAD` 实测）：
- `377d8c6`（2026-09-15 00:07 +0800）**加入**两份 docx（旧目录旧文件名）；
- `5e57c92`（2026-09-19 07:35 +0800）**从 git 删除**（此后新名 docx 从未入库）；
- `a887633`（2026-09-22 20:29 +0800，"rename the review artefact folders"）只改了
  `PAPER_OUTLINE_*_CN.md` 等 Markdown 与目录命名，**不含任何 docx**；
- `git log HEAD --name-only` 全程未出现新名路径
  `docs/paper_outline_review_20260914/…_外部评审版….docx`。

**因此**：`docs/FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md:153` 与
`docs/论文与图件问题汇总_仅复核_20260921.md:541` 中"该 docx 从未被 git 跟踪、**git 对象里也没有**"
的表述需要更正为：**新名路径下确实从未入库；但旧名路径下两份同源 docx 的 git 对象存在、可取回**。
本说明不改写那两份历史文档，更正以本文件为准。

### 3.3 内容级验证（对 `selfcheck.py:507-511` 判据的实测）

| 判据（脚本原文） | blob `3022c4fe`（更新版） | blob `6f7e3edc`（原版） |
|---|---|---|
| `"条件性交互" in body_new` | ✅ 命中 | ❌ 不含（符合原件判据） |
| `"0.77 和 0.60" in body_new` | ✅ 命中 | ❌ 不含 |
| `"仍在验证" not in body_new` | ✅ 不含 | 含（原版确有旧措辞） |
| `"当前直接交互推断尚未完成" not in body_new` | ✅ 不含 | — |
| `body_new != body_old` | ✅ 不同（21,662 vs 15,283 字符） | — |

即：**两条内容检查（507-512 行）所需的两份文档内容，在 git 对象中完整、判据全部吻合**。

### 3.4 无法证明的部分（如实登记）

- 缺失文件用"**外部评审**版"命名，git blob 用"**导师审阅**版"命名；blob 正文含"导师"、不含"外部评审"
  （`a887633` 的中性化改名发生在 docx 已从 git 删除之后，盘上是否同步改写过正文无从对证）。
- 仓库内**没有**缺失文件的任何留档 SHA-256（`194681CF…` 等已登记哈希属权威稿 docx，非提纲）。
- → **结论：内容判据级可恢复；与缺失文件的字节同一性不可证明。** 不得据此外推"文件已找回"。

### 3.5 仍在盘的重建源（第二条恢复途径）

```
.tmp_outline_20260914/
  build.py          7,896 B  （2026-09-14 14:28）
  artifact.md       1,651 B  （2026-09-14 14:26）
  render_native.py    961 B  （2026-09-14 14:27）
  word.pdf        654,012 B  （2026-09-14 14:29）
  render/
```

- 另有 `scripts/outline_update_20260914/update_outline.py`（其声明输入即缺失的外部评审版原版）。
- 已知限制 F21（`FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md:152`）：`build.py` **非字节可复现**
  （连跑三次 docx SHA 三个值）→ 重建产物**无法**与任何历史 SHA 对齐，只能做内容级校验。

### 3.6 影响核查：对当前论文结果与稿件 **无影响**

- 提纲是**规划文档**，不参与任何统计、图表或结论生成。当前权威稿
  `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_*.docx`
  （git 跟踪；哈希已登记于 `论文与图件问题汇总…:557/570`）完整在盘。
- 受影响的只是**指针与检查**：
  | 位置 | 性质 |
  |---|---|
  | `selfcheck.py:494-499` 检查 ② | 现状下重跑必然 FAIL（与 ① 同理） |
  | `docs/README.md:88` | 指向不存在目录的索引行（悬空指针） |
  | `experiments/…/REPORT_CN.md:26,190` | 历史交付记录里的路径（红线区，不改） |
  | `scripts/paper_evidence_completion_20260927/finalize_new.py:285` | 输出文案中的路径描述 |
  | `experiments/…/RUN_SUMMARY.json:50` | 旧目录名指针，已按"历史记录里的旧值"登记不改 |

---

## 4 结论汇总

| 缺口 | 可恢复性 | 对论文结果/稿件的影响 | 对自检门禁的影响 | 处置 |
|---|---|---|---|---|
| `_smoke` 两个 NPZ（17.2 MB 冒烟产物） | **不可恢复**（git 未入库、双工作区/发布包/外部盘皆无） | **无**（冒烟非结果；真实结果目录完整；无代码/图表引用） | 失败 ① 重跑必现 | 登记为历史追溯缺口，校验值留档于冻结清单 |
| `REPORT_CN.md` mtime 漂移 | 不需恢复 | **无**（sha256 与冻结值完全一致，内容未变） | 计入失败 ① 的 `modified` | 判定为仅时间戳漂移，登记说明 |
| 提纲"外部评审版_更新版"docx | **内容级可恢复**（旧名 blob `3022c4fe`，判据 4/4 吻合）；字节同一性**不可证明** | **无**（规划文档；权威稿完整） | 失败 ② 重跑必现 | 登记缺口 + 更正旧登记"git 对象也没有"的表述；是否重建/放回待作者决定 |

**总体判定**：历史自检 67/69 的两条失败均**不触及论文的任何数值结果、图表或稿件正文**；
它们是"冻结清单对冒烟产物的完整性校验"与"规划文档指针"两个证据层面的缺口。
既有登记（`ARTIFACT_INDEX.md:285`、`FINAL_REPAIR_AND_ACCEPTANCE_20260923.md:396-400`）对失败
的描述**与原始报告一致**，本说明的增量为：四路备份检索结论、REPORT_CN.md 内容未变的实证、
提纲 git 对象的可取回性及其判据验证、以及对"git 对象也没有"一处旧表述的更正。

## 5 建议的后续步骤（本轮未执行，待授权）

按 `PAPER_COMPLETION_20260928_CN.md` 第 3 条四步，剩余两步为：

1. **新日期目录重跑**：以 `--report-dir` 把自检输出写入新的日期目录并标注"本次重新验证"，
   旧报告 `legacy_selfcheck/` 原样保留。预期失败仍为同两条（除非先做第 2 项处置）。
2. **建立新基线**：对当前稿件/输入/脚本/交付件计算新 SHA-256 基线，旧基线不动。
3. **需作者二选一的处置**（本说明不代决策，且均禁止伪造回旧时点状态）：
   - a) **登记豁免**：把两个 `_smoke` NPZ 与缺失提纲在冻结清单/检查中的角色改为
     "缺失即记 caveat"（改的是**今后的检查逻辑**，不改旧报告）；
   - b) **重建/放回**：从 git blob 或 `.tmp_outline_20260914` 重建提纲到**新日期目录**并在说明中
     记录来源与校验值；NPZ 不可重建（冒烟配置与随机性未冻结到可重放程度），只能走 a)。
