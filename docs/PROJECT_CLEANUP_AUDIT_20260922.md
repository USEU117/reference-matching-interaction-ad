# 项目清理审计（重复 / 时效性 / 精简）— 2026-09-22

> 范围：全仓（`D:\STUDY\My_github\sci_project`），Windows / PowerShell，只读扫描 + 白名单删除 + 时效性更新。
> 基线：`HEAD = 85d3207`，`main → origin/main` 且已同步（`origin/main..HEAD` = 0），10 tags，工作区除本任务新增/删除项外无其他改动。
> 交付原则：**只执行可证明信息无损失的删除**（每条都给逐字节同哈希或"内容可再生"的凭据）；拿不准的一律只列清单。
> 未做：git 提交、推送、GPU、实验、任何已发布产物的修改。

---

## 0. 约定的红线（本次全部遵守）

未触碰：`experiments/**` 下的 csv/json/npz 汇总与逐图产物、`data/**`（含 `data/splits/*/manifest.json`）、权威稿 `docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx`、版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx`、`LICENSE`、`requirements_repro.txt`、`figure_sources/**`、`dist/**`。

**删除前"三查"方法**（用于本报告每一条已执行项）：
1. 全仓 grep 路径 / 文件名（排除 `.git`、`.venv*`、`methods/`、`outputs/`）；
2. 校验文档是否记录哈希 / 引用：`论文与图件问题汇总_仅复核_20260921.md`、`ISSUE_REGISTER_20260920.md`、`REMEDIATION_PLAN_20260920.md`、`ACCEPTANCE_20260920.md`、`VALIDATION_20260918.*`、`ARTIFACT_INDEX.md`、`FIGURE_BINDING.md`、`AUTHORITATIVE_SOURCE_DIFF_20260921.md`、`dist/replication_package_20260920/SHA256SUMS`、`submission_repro_20260827/SHA256SUMS`；
3. 是否存在逐字节相同副本（SHA-256 实算，非按体积推断）。

---

## A. 逐字节重复文件（按 SHA-256 分组）

### A.1 扫描方法

先按文件体积找碰撞组（同体积才有可能是同内容），再对碰撞组内文件实算 SHA-256 —— 避免对约 720 GiB 工作区无差别哈希。扫描集合 = `docs/`、`dist/`、`scripts/`、`src/`、`configs/`、`patches/`、`tests/`、`submission_repro_20260827/`、`experiments/summaries/`、`data/splits/`、`data/README.md`、`.trae/`、`tools/`、全部 `.tmp_*/`、以及仓库根文件。

| 指标 | 实测 |
|---|---|
| 参与体积碰撞筛查的文件 | 6 870 |
| 体积碰撞组 | 1 582 |
| 实算 SHA-256 的文件 | 4 365 |
| **同哈希 ≥2 份的组** | **1 509** |
| 冗余字节（每组只留一份后的可释放量） | **1 289 262 563 B ≈ 1 229.6 MiB** |

未纳入哈希的目录（属机器本地缓存，非"文档重复"问题，且体量过大）：`outputs/`（480 403.9 MiB）、`experiments/dynamic_fusion/`（185 743.9 MiB，其中 `canonical/`、`units/`、`series/` 为 `.npz` 缓存）、`methods/`（12 855 MiB）、`data/`（39 143.3 MiB）。

### A.2 冗余分布（按顶层目录）

| 顶层 | 参与重复组的文件数 | 其中字节量 |
|---|---:|---:|
| `.tmp_complete_figures_20260920` | 242 | 246 MiB |
| `.tmp_revision_20260922` | 6 | 95.4 MiB |
| `.tmp_figure_revision_20260920` | 43 | 12.6 MiB |
| 其余 `.tmp_*`（21 个目录） | 139 | 约 42 MiB |
| `dist/` | 1 503 | 417.4 MiB |
| `docs/` | 721 | 943.8 MiB |
| `scripts/` | 759 | 9.7 MiB |
| `src/` / `configs/` / `data/` / `experiments/` / `submission_repro_20260827` / `LICENSE` | 113 | 约 1.9 MiB |

### A.3 体量最大的重复组（实算，前 15）

| 体积 | 份数 | 路径（同哈希） | 结论 |
|---:|---:|---|---|
| 68.85 MiB | 3 | `docs/paper_complete_teacher_review_20260920/All_Figures_Complete_20260920.pptx`（tracked，现役 58 页 deck）／`.tmp_complete_figures_20260920/assembled.pptx`／`.tmp_revision_20260922/snapshot/All_Figures_before.pptx` | 前两份**已删** `.tmp` 副本（见 §已执行 #4/#8） |
| 68.29 MiB | 2 | `docs/.../All_Figures_Complete_20260920.pptx.bak_20260922`／`docs/.../All_Figures_Finalized_20260920.pptx`（tracked） | **已删** `.bak`（见 §已执行 #3） |
| 26.44 MiB | 2 | `docs/.../Reference_Matching_Complete_English_20260920.docx`（**权威稿**）／`.tmp_revision_20260922/snapshot/Reference_Matching_before.docx` | **不删**（snapshot 是本次会话的手工快照，见 §建议清单） |
| 11.54 MiB | 3 | `.tmp_contour_notation_20260911/draft.pptx`／`docs/figures_contour_notation_20260911/DCFnet_Figures_Contour_Notation_20260911_final.pptx`（tracked）／`dist/...` | **已删** `.tmp` 副本 |
| 10.09 MiB | 4 | `.tmp_teacherfig_20260910/draft.pptx`／`docs/figures_teacher_revision_20260910/DCFnet_Figures_Expanded_20260910.pptx`（tracked）／`docs/figures_package_20260917/06_previous_theme_DCFnet/`／`dist/...` | **已删** `.tmp` 副本 |
| 7.71 MiB | 5 | `figS3_extra_cases_panels.png`：`docs/figures_package_20260917/01_main_figures/`、`docs/figures_reference_matching_20260914/`、`docs/manuscript_reference_matching_20260914/figures/` + `dist/` 两份 | 见 §建议清单 |
| 6.95 MiB | 5 | `figS3_extra_cases_panels.pdf`：同上 5 处 | 见 §建议清单 |
| 6.36 MiB | 3 | `.tmp_allfig_20260910/draft.pptx`／`docs/figures_redraw_20260910/DCFnet_All_Figures_Editable_20260910_v2.pptx`（tracked）／`dist/...` | **已删** `.tmp` 副本 |
| 5.75 / 5.66 MiB | 各 2 | `docs/paper_writing_preparation_20260830/figures_20260830/qualitative_local_only/Fig09|Fig08_*.png` ≡ `dist/...` | 见 §建议清单 |
| 3.95–2.62 MiB | 各 2 | `.tmp_complete_figures_20260920/{qa_doc_final_sheets,qa_doc_sheets}/doc_0{1,2,3,4,5}.png` | 同目录内重复；现役目录，未动 |
| 3.37 / 3.03 MiB | 各 5 | `panel_interaction_cases_p2.{png,pdf}`、`panel_interaction_cases.png`：三个 `docs` 图件目录 + `dist/` 两份 | 见 §建议清单 |
| 3.19 MiB | 各 3 | `.tmp_{manuscript_english_polished_20260906,manuscript_round2_20260906,dcfnet_figures_20260905}/draft.pptx` ≡ 对应 `docs/**` 的 tracked pptx | **已删** 3 个 `.tmp` 副本 |
| 2.55 MiB | 4 | `.tmp_mainfig_20260910/draft.pptx` ≡ `docs/main_figure_redraw_20260910/…` ≡ `docs/figures_package_20260917/06_previous_theme_DCFnet/…` ≡ `dist/...` | **已删** `.tmp` 副本 |

其余 1 494 组为小块重复（`__init__.py`、`.log.err`、`fig7_multimethod_*` 逐图渲染、`submission_repro_20260827` 内部 json 双份等），模式与上表一致：**`dist/` 交付副本 + 三个 `docs` 图件目录 + `.tmp_*` 渲染中间件**。

### A.4 A 节结论

1. 重复的根因只有三类：① `docs/figures_package_20260917/`、`docs/figures_reference_matching_20260914/`、`docs/manuscript_reference_matching_20260914/figures/` 三处保存**同一批图件**；② `dist/replication_package_20260920/` 是交付副本，1 503 个文件在仓内另有逐字节同源；③ `.tmp_*/draft.pptx`、`presentation.json` 等构建中间件。
2. 逐字节重复合计 **1 229.6 MiB**，其中 `dist/`（417.4 MiB，交付物）与 `docs/` 三处图件集（943.8 MiB）占 99%，但这部分**不是无条件可删**（见 §建议清单），故 A 节只给建议。
3. 明确白名单内的重复副本已执行删除（见 §已执行）。

---

## B. 超大文件（>20 MiB，全仓 2 237 个）

### B.1 分布

| 顶层 | >20 MiB 文件数 | 合计 | 跟踪状态 | 建议 |
|---|---:|---:|---|---|
| `outputs/` | 1 160 | 475 002.8 MiB | 忽略（`.gitignore:23`） | **保留**（canonical / PatchCore / 逐图缓存，`ARTIFACT_INDEX.md` §4.1 明示"盘上必须有"） |
| `experiments/dynamic_fusion/` | 1 017 | 165 695.5 MiB | 忽略（`*.npz` 等） | **保留**（逐单元 npz 是唯一副本，见 `ARTIFACT_INDEX.md` §4.3） |
| `methods/` | 34 | 8 697.3 MiB | 忽略（`.gitignore:16`） | **保留**（vendored 源码 + 上游 zip） |
| `docs/` | 5 | 215.9 MiB（清理后） | 见下 | 见下 |
| `.tmp_*` | 10 | 678.6 MiB | 忽略（`/.tmp_*/`） | 除现役目录外**建议删除**（见 §建议清单） |
| `data/downloads/KolektorSDD2.zip` | 1 | 813.6 MiB | 忽略 | **保留**（F 的输入压缩包） |

### B.2 `docs/` 内 >20 MiB（逐个列出）

| 路径 | 体积 | tracked | 被引用 | 建议 |
|---|---:|---|---|---|
| `docs/paper_complete_teacher_review_20260920/All_Figures_Complete_20260920.pptx` | 68.85 MiB | 是 | `论文与图件问题汇总` F14、`图件与PPT页码索引.md` | **保留**（现役 58 页 deck，2026-09-22 重出，SHA `48DD9180…`） |
| `docs/paper_complete_teacher_review_20260920/All_Figures_Finalized_20260920.pptx` | 68.29 MiB | 是 | `AUTHORITATIVE_SOURCE_DIFF_20260921.md:272`（明示"保留"） | **保留**（旧 deck，被指定为语义更清楚的名字保留） |
| `docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx` | 26.44 MiB | 否（`*.docx` 忽略） | 全部文档 | **保留（红线）** —— 权威稿 |
| `docs/paper_complete_teacher_review_20260920/…docx.bak_20260922` | 26.40 MiB | 否 | `论文与图件问题汇总` §八 | **保留**（= 唯一"重建前"版本 `18694B90…`；该 docx 曾整份从盘上消失，见 F17，留作恢复点） |
| `docs/paper_complete_teacher_review_20260920/…docx.bak_authoritative_20260921` | 25.89 MiB | 否 | `论文与图件问题汇总` §一/§七/§八 | **保留**（同上，09-21 权威版） |

> `docs/figures_package_*.zip`（任务提到的 177.82 MB 那个）**已不在盘上**：`docs/` 下无任何 `*.zip`。`.gitignore:80` 的 `docs/figures_package_*.zip` 现为无效规则（无害，可留）。

### B.3 `.tmp_*` 内 >20 MiB（建议删除，未执行）

| 路径 | 体积 | 性质 |
|---|---:|---|
| `.tmp_contour_notation_20260911/presentation.json` | 149.30 MiB | 渲染中间件（嵌 base64 图） |
| `.tmp_teacherfig_20260910/presentation.json` | 129.60 MiB | 同上 |
| `.tmp_allfig_20260910/presentation.json` | 81.11 MiB | 同上 |
| `.tmp_revision_20260922/snapshot/All_Figures_before.pptx` | 68.85 MiB | ≡ 现役 `docs/.../All_Figures_Complete_20260920.pptx` |
| `.tmp_complete_figures_20260920/all_images.pptx` | 68.62 MiB | **现役目录**，保留 |
| `.tmp_dcfnet_figures_20260905/presentation.json` | 40.58 MiB | 渲染中间件 |
| `.tmp_manuscript_english_polished_20260906/presentation.json` | 40.59 MiB | 同上 |
| `.tmp_manuscript_round2_20260906/presentation.json` | 40.58 MiB | 同上 |
| `.tmp_mainfig_20260910/presentation.json` | 32.59 MiB | 同上 |
| `.tmp_revision_20260922/snapshot/Reference_Matching_before.docx` | 26.44 MiB | ≡ 权威稿（本次会话快照） |

---

## C. 过程性 / 已被取代的文档

### C.1 每轮交接 / 变更记录类（`docs/` 根目录 66 个 `.md` + `docs/specs/`）

| 文件 / 目录 | 体积 | 文件数 | 最后修改 | 被引用 | 建议 |
|---|---:|---:|---|---|---|
| `docs/AI_HANDOFF_*_CN.md`（7 个：REFERENCE_COUPLING_PILOT_20260912、VALIDATION_AND_INNOVATION_20260911、NEXT_STAGE_AFTER_SEED1_REVIEW_20260913、STATISTICS_AND_INDEPENDENT_REPLICATION_20260913、REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914、UNIFIED_PAPER_AND_SUPPORT_EXPERIMENTS_20260913） | 约 0.6 MiB | 7 | 2026-09-11 ~ 09-14 | `docs/README.md` §1.1 列为 current 规格 | **保留**（"最新规格 S0–S9 阶段定义"仍是实验口径依据）；但**其"最新"标注已过期**，见 §D |
| `docs/HANDOVER_20260919.md` | 0.1 MiB | 1 | 2026-09-19 | `README.md` 文档地图、`ARTIFACT_INDEX.md` | **保留**（当前交接正文） |
| `docs/PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md` | — | 1 | 09-14 | `docs/README.md`、`ARTIFACT_INDEX.md` §2.2 列"旧主线" | **保留**（历史证据，已声明不代表当前结论） |
| `docs/OVERNIGHT_HANDOFF_20260908_CN.md`、`docs/.trae`/`docs/specs` 的 `night_run_handover_20260917.md` | 约 0.15 MiB | 3 | 09-08 / 09-17 | `ARTIFACT_INDEX.md` §五 | **保留**（`_night2_20260918` 验收链引用） |
| `docs/REMEDIATION_PLAN_20260920.md` / `docs/ISSUE_REGISTER_20260920.md` | 约 0.1 MiB | 2 | 09-20（含 09-22 刷新节） | `README.md`、多处 | **保留**（当时在册的唯一问题台账） |
| `docs/paper_complete_teacher_review_20260920/论文与图件最终验收报告_20260920.md` | 0.02 MiB | 1 | 09-20 | `BASELINE_EXPANSION_PLAN_20260921.md:3` | **保留**（本轮已加 09-22 追注，见 §D） |
| 根目录 `PLAN.md`（473 行）、`SECOND_STAGE_PLAN.md`、`NEXT_ACTIONS.md`、`HANDOFF.md`、`PROJECT_STATUS.md`、`GPU_OVERNIGHT_PLAN.md`、`AUTO_GPU_SCHEDULER.md` | 约 0.3 MiB | 7 | 2026-08 为主 | `PLAN.md` 被 `build_progress_report.py` 引用 | **需作者决定**：属 2026-08 旧主线计划，`docs/README.md` 已声明"不代表当前结论"。**建议**：整批移入 `docs/archive_pre20260920/`（保留可查），或删除；本轮不动 |
| `docs/REPRODUCIBILITY_PACKAGE.md`、`docs/SUBMISSION_METADATA.md`、`docs/GITHUB_METADATA.md`、`docs/COMPARISON_PROTOCOL_JUSTIFICATION.md` | 约 0.1 MiB | 4 | 09-19 ~ 09-21 | `README.md`、`ARTIFACT_INDEX.md` | **保留**（仍是投稿前操作口径） |
| `docs/dynamic_fusion_*.md`（11 个）+ `docs/analyze_*` / `cpu_*` / `project_state_reconciliation_20260809.md` / `v2_*` / `visa_*` | 约 0.5 MiB | 20+ | 2026-08 | 仅历史互引 | **需作者决定**：2026-07~08 旧探索线文档，`ARTIFACT_INDEX.md` §2.2 已标"勿据其结论写作"。建议同上归档 |

### C.2 已被取代的旧链（**明确不删，列"需作者决定"**）

| 项 | 体积 | 文件数 | 最后修改 | 被引用 | 建议 |
|---|---:|---:|---|---|---|
| `docs/manuscript_reference_matching_20260914/` | 158.87 MiB | 113 | 09-22 | `README.md`、`SUPERSEDED_20260921.md`、`AUTHORITATIVE_SOURCE_DIFF_20260921.md`、`submission_repro_20260827` | **保留**（`SUPERSEDED_20260921.md` 第 28 行明写"**不要删除本目录**：审计、对照与回溯需要它"）。其 `figures/` 与另两处逐字节重复（约 130 MiB），可考虑删重复副本 —— 见 §建议清单 |
| `scripts/manuscript_build_20260914/` | 0.2 MiB | 8 | 09-20 | `SUPERSEDED_20260921.md`、`REMEDIATION_PLAN` 跨文档口径矛盾表 | **保留**（历史证据 + `build_validation.json` 的再生成链） |
| `scripts/outline_update_20260914/`、`scripts/innovation_breadth_20260908/` 等 2026-07~08 探针脚本 | 约 40 MiB(`scripts/` 全部) | 1 137 | — | `ARTIFACT_INDEX.md` §2.2 | **保留**（负结果探针属历史证据） |

### C.3 scratch / 临时目录

| 目录 | 体积 | 文件数 | 最后修改 | 被引用（grep 实测） | 建议 |
|---|---:|---:|---|---|---|
| `.tmp_complete_figures_20260920/` | 311.1 MiB | 338 | 2026-09-22 | **是**：`scripts/paper_complete_teacher_review_20260920/figure_sources/plot_primary.py:7,11`（输出目录 + `import plot_fonts`） | **保留（现役工作目录，禁删）** |
| `.tmp_figure_revision_20260920/` | 15.9 MiB | 76 | 09-20 | **是**：同上 `plot_primary.py:9` 读 `tables.json` | **保留（禁删）** |
| `.tmp_revision_20260922/` | 95.4 MiB | 6 | 09-22 | 仅本报告 | **需作者决定**：本次会话的 `snapshot/`（2 个与交付件逐字节相同的副本 + `论文与图件问题汇总` 副本）。**未删** |
| `.tmp_english_manuscript_20260914/` | 8.5 MiB | 56 | 09-14 | `ARTIFACT_INDEX.md:122`（原写"待确认"）、`FIGURE_BINDING.md:146`（现写"**已废弃**"） | **保留**：`ARTIFACT_INDEX.md` 的原"待确认"已在 §D 就地更正；目录内小文本为历史源，体积小 |
| 其余 23 个 `.tmp_*/`（`allfig`、`contour_notation`、`dcfnet_figures`、`dcfnet_ppt`、`lesson_*`、`mainfig`、`manuscript_*`、`outline`、`teacherfig`、`tencent`、`crossref`、`univad`、`pilot2`、`provenance_probe`、`next`、`baseline_plan`、`english_qualitative`） | 约 1 040 MiB | 约 900 | 2026-09-03 ~ 09-14 | **仅有小文件被文档引用**：`.tmp_allfig_20260910/validation-v2.json`（`project_review_20260910/paper_audit.md:11`）、`.tmp_teacherfig_20260910/prepare.py`、`.tmp_contour_notation_20260911/revise.py`（`E8/figure_version_binding.md:14-15`）、`.tmp_univad/probe_cosine.py`（`scripts/validation_handoff_20260911/univad_stage2_eval.py:100` 注释） | **建议删除大文件、保留小文本**（白名单 #3 口径）：>20 MiB 的渲染中间件约 500 MiB + 其余 png/pdf 约 300 MiB。**未执行**（见 §建议清单） |
| `experiments/.../confirmation_ksdd2_20260918/_smoke_round2/` | 79.1 MiB | 24 | 09-18 | `ARTIFACT_INDEX.md` §4.2 行 132：「**明确不得引用其数字**……不是结果」 | **未删**：位于 `experiments/`（红线区），虽有白名单授权且有索引背书，仍交作者决定 |
| `experiments/.../generalization_mvtec_visa_20260915/_maskfix_smoke/`、`_regression_check/` | 约 0 MiB | 各 1 | 09-15 | `ARTIFACT_INDEX.md` §4.2 行 131 | **未删**（同为 `experiments/` 红线区，且几乎不占空间） |
| `experiments/.../seeds_extension_20260917/_smoke_canonical/` | 约 0 MiB | 1 | 09-17 | 同上 | 同上 |
| `experiments/.../unified_fusion_paper_support_20260913/_smoke/` | 16.8 MiB | 13 | 09-13 | 同上 | 同上 |
| `docs/figures_package_20260917/05_superseded/`、`docs/paper_complete_teacher_review_20260920/figures/superseded/` | 6.24 + 0.32 MiB | 9 + 2 | 09-14 ~ 09-20 | `FIGURE_BINDING.md`、`论文与图件问题汇总` F15 | **保留**（`docs/manuscript_reference_matching_20260914/figures/superseded/` 的 9 个同哈希副本**已删**，见 §已执行 #5） |
| `experiments/dynamic_fusion/{innovation_*,v2,v3*,v4_*,rcec_v1}/` | — | — | 2026-07~08 | `ARTIFACT_INDEX.md` §4.2 行 135 | **保留**（索引明写"保留作历史"） |

### C.4 C 节结论

- 真正"可删且无价值"的过程性文档集中在 **仓库根目录的 7 个 2026-08 计划类 `.md`** 与 **`docs/` 下 20+ 个 `dynamic_fusion_*`/`cpu_*`/`visa_*` 旧主线文档**；它们既不被当前写作引用，也已被 `docs/README.md`/`ARTIFACT_INDEX.md` 标为历史。**建议归档而非直接删除**（约 0.8 MiB，收益在整洁而非空间），本轮**未动**。
- `.tmp_*` 是最大的可回收面（约 1.4 GiB），但其中 **2 个目录是现役图件链的工作目录**（`plot_primary.py` 实读依赖），故只能按"删大留小"执行，且必须逐个核对引用。本轮**未执行**。
- 所有 `_smoke_*` 位于 `experiments/` 红线区，虽被索引明示"不是结果"，仍**未删**。

---

## D. 时效性过期内容

### D.1 已就地更新 / 标注（12 处，逐条给改前改后）

| # | 文件:行 | 改前（现值） | 改后 | 依据 |
|---|---|---|---|---|
| 1 | `README.md:44`（英文） | `Manuscript (English source plus Chinese parallel text) and figure sources: docs/manuscript_reference_matching_20260914/. Current build: 18 tables / 8 figures / 12 display equations / 34 references` | 改为指向权威稿 `docs/paper_complete_teacher_review_20260920/…docx` + `scripts/paper_complete_teacher_review_20260920/build.py`；**47 pages / 20 tables / 8 main figures plus S1–S5 (22 embedded images) / 12 equations / 34 references / 16,969 words**；旧链标注 superseded | 权威源已换链（`论文与图件问题汇总` §一、§八 T06/T07；`REMEDIATION_PLAN` §执行状态）；`16,969 词` 见 `论文与图件问题汇总` §八"2026-09-22 权威稿重建结果"（Word COM 实测） |
| 2 | `README.md:85`（中文） | `论文当前稿……当前构建规模 18 表 / 8 图 / 12 公式 / 34 文献` | 同步改为 **47 页 / 20 表 / 8 主图 + S1–S5（22 内嵌图）/ 12 编号公式 / 34 文献 / 16,969 词**，旧链标 superseded | 同上 |
| 3 | `docs/论文与图件问题汇总_仅复核_20260921.md:103`（F10） | `当前46页、19表适合资料审阅` | 保留原句 + 括注「**2026-09-22 校**：权威稿重建后实为 **47 页、20 表**」 | 同文档 §八；§四按该文档自定"原文保留"纪律，故用括注而非改写 |
| 4 | `docs/论文与图件问题汇总_仅复核_20260921.md:271`（跨文档矛盾表 C 行） | `（HEAD de25a22）` | `（HEAD 85d3207，2026-09-22 复测；de25a22 为首次记录时的 HEAD）` | `git rev-list --count origin/main..HEAD` = 0，`git branch -vv` 显示 `main [origin/main]` |
| 5 | `docs/论文与图件问题汇总_仅复核_20260921.md:243`（F14 行） | `旧 deck 保留为 …pptx.bak_20260922（另有字节相同的 All_Figures_Finalized_20260920.pptx）` | 追加「**2026-09-22 清理**：该 `.bak_20260922` 已删除（与后者逐字节相同），保留后者」 | SHA-256 实算 `6EBD92E9…`，71,604,011 B，两份相同 |
| 6 | `docs/论文与图件问题汇总_仅复核_20260921.md:273`（跨文档矛盾表 E 行） | `README.md 记 18 tables / 8 figures …是否改口径由作者定（…未动其它内容）` | 改为「**2026-09-22 已改口径**：README 中英两处现指向 20260920 链……」 | 即本表 #1/#2 |
| 7 | `docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md:3` | `权威稿 = …（46 页 / 19 表 / 8 主图 / S1–S5 / 34 文献）` | 保留原句 + 追加「**2026-09-22 校**：已重建为 47 页 / 20 表 / 22 内嵌图 / 16,969 词，SHA `F3CAE3B4…`；本文件其余 46 页/19 表/约 10,993 词均为 09-21 历史值」 | 同 #1 |
| 8 | `docs/manuscript_reference_matching_20260914/SUPERSEDED_20260921.md:10` | `现行权威稿 = 46 页 / 19 表 / …约 10,796 词` | 追加「**2026-09-22 校**：现行权威稿为 47 页 / 20 表 / 22 内嵌图 / 16,969 词」 | 同 #1；该文件是"哪些是当前"的索引件，必须标 |
| 9 | `docs/manuscript_reference_matching_20260914/SUPERSEDED_20260921.md:13` | `缺 19 表 …权威稿独有的 Table 19 = …` | 追加「**2026-09-22 校**：原 Table 12–19 顺延为 **13–20**，全文 **20 表**」 | `ARTIFACT_INDEX.md` §6.5；`论文与图件问题汇总` §八 已落实项 4 |
| 10 | `docs/ARTIFACT_INDEX.md:122` | ``/.tmp_*/` … **但** `.tmp_english_manuscript_20260914/build.py` 是 `FIGURE_BINDING.md` §3 列出的正文构建入口 —— …**待确认**` | 改为「**已澄清（2026-09-22）**：`FIGURE_BINDING.md` §3 已把入口更正为受控脚本 `scripts/manuscript_build_20260914/build.py`（原文注明旧的 `.tmp_...` 已废弃）」+ 增补"`.tmp_complete_figures_20260920/`、`.tmp_figure_revision_20260920/` 是现役工作目录，不得删除" | `FIGURE_BINDING.md:146` 原文；`plot_primary.py:7,9,11` 实读 |
| 11 | `docs/ARTIFACT_INDEX.md:66` / `:136` | `docs/manuscript_reference_matching_20260914/*.bak{,2,3}_20260919 …多轮重建的正文备份` / `*.bak{,2,3}_20260919 …可保留，引用时勿当产物` | 两处均注「**2026-09-22 已删除**（23 个）+ 该链可由 `build.py`/`build_cn_docx.py` 从同目录 `.md` 重建」；并注明 `experiments/` 下的 6 个按红线**保留** | 本报告 §已执行 #1 |
| 12 | `docs/README.md:5` | `最后整理：2026-09-14。` | 追加「**当前状态指针（2026-09-22 追加，下表原文不改写）**」段：权威交付稿、唯一可编辑源、稿件口径已被哪两份文档取代 | `docs/README.md` 是 `docs/` 阅读入口；其 §0/§1 指向的仍是 2026-09-14 规格，需一句指针避免误导 |

### D.2 第二轮同批更新（发布点 / 仓库名 / 方法数量）

| # | 文件:行 | 改前 | 改后 | 依据 |
|---|---|---|---|---|
| 13 | `docs/ISSUE_REGISTER_20260920.md:38` | `…已同步（HEAD de25a22）` | `…已同步（HEAD 85d3207，2026-09-22 复测；de25a22 为首次记录时的 HEAD）` | git 实测 |
| 14 | `docs/REMEDIATION_PLAN_20260920.md:13` | `…（HEAD de25a22，2026-09-22 实测）` | `…（HEAD 85d3207，2026-09-22 复测；de25a22 为该条首次记录时的 HEAD）` | 同上 |
| 15 | `docs/REMEDIATION_PLAN_20260920.md:140` | `12. 是否同意推送本地 main（超前远端 15 个提交）并推送 tags。` | `12. ~~…~~ —— **已办结**（2026-09-22 实测 origin/main..HEAD = 0，tags 已在远端）。` | `git rev-list --count origin/main..HEAD` = 0；10 tags 已在远端 |
| 16 | `docs/SUBMISSION_METADATA.md:40` | `远端 USEU117/sci_project（拟改名 USEU117/reference-matching-interaction）` | `远端**已改名**为 USEU117/reference-matching-interaction-ad（旧地址自动重定向）；本地 origin 已指向新 URL` | `README.md:3`（HEAD `85d3207` 提交信息即"state the repository's actual name rather than the intended one"）；`git remote -v` |
| 17 | `docs/GITHUB_METADATA.md:5` | `改名前后对照：…（远端改名由人手动做）` | 追加「**远端改名已完成**：本地 origin 已指向新 URL，`origin/main..HEAD` = 0；§3 网页步骤保留作记录，重跑无意义」 | 同上 |
| 18 | `docs/paper_complete_teacher_review_20260920/论文与图件最终验收报告_20260920.md:36` 后 | `…但尚未达到导师曾建议的约 10 个公开方法规模` | 保留原句 + 追加「**2026-09-22 追注**：外部方法家族 2 → **5**（PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AnomalyCLIP 零样本），单列 Table 12；导师 09-22 明确"近两三年三四个比较先进的方法比较合适"，"约 10 个"不再是缺口，P2 结案」 | `论文与图件问题汇总` §八 T06/T07；`ISSUE_REGISTER` R-20 刷新行；`REMEDIATION_PLAN` §执行状态 |
| 19 | `scripts/limitation_closure_20260915/_night2_20260918/ACCEPTANCE_20260920.md:51` | `…（HEAD de25a22）。…（当前 HEAD de25a22；…）` | `…（HEAD 85d3207；本条首次记录时为 de25a22）。…（工作区有收口改动，未提交、未推送）` | git 实测 |

**合计更新 19 处，涉及 8 个文件。**

### D.3 复核后判定"保留不改"的旧值（历史事实，非当前状态）

| 文件:行 | 旧值 | 保留理由 |
|---|---|---|
| `docs/AUTHORITATIVE_SOURCE_DIFF_20260921.md:83,238` | `19 表`、`约 10,993 词` | 09-21 轮次的历史记录，文件第 4 行已加总注说明 |
| `docs/论文与图件问题汇总_仅复核_20260921.md:11,133,217,260` | `16,892 词`（09-21 晚实测） | 该轮次记录；同文件 §八"2026-09-22 权威稿重建结果"已给当前值 `16,969 词`；文件自定"前文不改写" |
| `docs/论文与图件问题汇总_仅复核_20260921.md:100（F07）、149、BASELINE_EXPANSION_PLAN_20260921.md:3,4,132` | `约10个`、`只有两个外部家族` | 均已在原文中自我更正（F07「应予纠正」、line 4「F07 已更正」）；且 `line 3` 是**引用触发句**（引用不该改写） |
| `docs/DYNAMIC_FUSION_NEXT_STEPS.md:7` | `当前基线提交 ac5c2f1 …超前 origin/main 1 个提交` | 2026-08 旧主线文档（`ARTIFACT_INDEX.md` §2.2 已声明"不代表当前结论"），"当前"是其当时的当前 |
| `docs/HANDOFF.md:58`、`PLAN.md:44`、`tools/rename_folder_to_reference_matching_interaction.ps1`、`AI_HANDOFF_*.md` 中的 `sci_project` | 路径字样 | 是**本地物理路径**（磁盘目录确实仍叫 `sci_project`，`D:\STUDY\My_github\reference-matching-interaction` 是指向它的 junction）。仓库**名**的表述 README 已正确 |
| `docs/manuscript_review_20260906/01_…md:47`、`docs/manuscript_revision_20260905/00_…md:131`、`docs/project_review_20260910/paper_audit.md`、`ACCEPTANCE_20260920.md:28-29` | `9 张表`、`8 幅图`、`46 张页面图`、`19 个表格` | 各自轮次的交付记录（09-05/09-06/09-10/09-20），属历史 |
| `docs/ISSUE_REGISTER_20260920.md:60`（R-11 首行）、`:147-153` | `超前远端 15 提交`、`未推送` | 09-20 原始登记；同文件 §〇ter 已加 09-22 刷新行判定"已解决" |
| `docs/ISSUE_REGISTER_20260920.md:61`（R-12 `dist/` 未跟踪且未被 `.gitignore` 覆盖） | — | **该现象已不成立**：`.gitignore:73` 现为 `dist/`。本轮只在报告登记，未改该表（避免与"原文不改写 + 刷新行"体例冲突），**建议作者在 §〇ter 补一行 R-12 刷新** |
| `experiments/**/state.json`、`reconciliation/*/state.md` 中的 `ahead 1`、`46129a7` | — | `experiments/` 红线区，且是当时的状态快照 |

### D.4 一致性复扫（更新后）

全仓再 grep `46 页` / `19 表` / `未推送` / `ahead 1[0-9]` / `尚未进入交付` / `约 10 个`：

- **`46 页` / `19 表` 残留 6 处**，全部已由 D.1 新增的总注/括注覆盖（`AUTHORITATIVE_SOURCE_DIFF_20260921.md:3,83,238`；`论文与图件问题汇总:103,133,217`；`SUPERSEDED_20260921.md:10,13`）——见 D.3 保留理由。
- **`未推送` / `ahead 15` 残留 3 处**：`ISSUE_REGISTER_20260920.md:60,147,153`（09-20 原始登记，已被同文件 §〇ter 刷新行判定"已解决"）、`docs/REMEDIATION_PLAN_20260920.md:24`（阶段表里"自动整理 + 作者决定 push"，属阶段定义非状态声明）。
- **`尚未进入交付` 0 处**（`论文与图件问题汇总:20` 已明确"该记载已不成立"）。
- **`约 10 个` 残留 4 处**：均为"已更正/引用触发"语境（见 D.3）。
- **`16,892 词` 残留 3 处**：09-21 晚轮次记录（同文件 §八已给 16,969）。

---

## 已执行删除清单（42 个文件，423 161 829 B）

「三查」逐条结论：**(a) 引用** = 全仓 grep 路径；**(b) 校验文档** = 上列 8 类审计/哈希文档逐项核对（无一处记录被删文件的哈希为"当前值"）；**(c) 唯一副本** = SHA-256 实算。

### #1 `docs/manuscript_reference_matching_20260914/*.bak*` —— 23 个文件，约 220.07 MiB

删除前：23 files / 220.07 MiB。其中 **7 个是 git 已跟踪文件**：`build_validation.json.bak4_20260919`、`build_validation.json.bak5_20260919`；`English_Manuscript_Source.md.bak2_20260919`、`bak5_20260919`、`bak_20260919`；`中文对照内容.md.bak2_20260919`、`bak_20260919`。其余 16 个未跟踪（`*.docx.bak6…9_2026xx` 共 8 个，以及 `build_validation.json.bak6…9`、`English_Manuscript_Source.md.bak6…9` 共 8 个）。

| 查项 | 结论 |
|---|---|
| (a) 引用 | 仅 `ARTIFACT_INDEX.md:66/136` 以**通配形式**提及并注明"非当前值 / 引用时勿当产物"；无脚本读写（grep 无命中） |
| (b) 校验文档 | 无任何 SHA256SUMS / 验收文档记录这些 `.bak` 的哈希；`论文与图件问题汇总:272` 明确它们是"多轮重建的正文备份" |
| (c) 唯一副本 | **非唯一内容**：该 2026-09-14 链的 docx 由 `scripts/manuscript_build_20260914/build.py` + `build_cn_docx.py` 从同目录 `manuscript.md` / `中文对照内容.md` / `tables.json` / `figures.json` / `references.json` 重建（脚本 docstring 实读确认）；且该目录整体已标 `SUPERSEDED_20260921.md` |
| 保留规则 | 保留 `English_Manuscript_Source.md`、`中文对照内容.md`、`论文精读讲解.md`、`build_validation.json`、`figures/`（正文源与对照材料，`SUPERSEDED_20260921.md` §"仍然有用的东西"明列） |

### #2 `docs/manuscript_reference_matching_20260914/figures/superseded/` —— 9 个文件，6.24 MiB

保留 `docs/figures_package_20260917/05_superseded/` 的同名副本（9/9 SHA-256 逐一致，`Compare-Object` 结果为空）。

### #3 `docs/paper_complete_teacher_review_20260920/All_Figures_Complete_20260920.pptx.bak_20260922` —— 68.287 MiB

白名单 #1 + #2。**逐字节相同副本保留**：`docs/paper_complete_teacher_review_20260920/All_Figures_Finalized_20260920.pptx`（均 71,604,011 B，SHA-256 `6EBD92E9B38A295896ADAC821B17064173828C804794B2AE53D74D0E26C26C26`）。该同源关系由 `论文与图件问题汇总:243` 自己记录。

### #4 `.tmp_*/draft.pptx` × 6 + `.tmp_complete_figures_20260920/assembled.pptx` —— 7 个文件，40.11 MiB + 68.85 MiB

| 删除项 | 体积 | 保留的同哈希 tracked 副本 | SHA-256（前 16） |
|---|---:|---|---|
| `.tmp_contour_notation_20260911/draft.pptx` | 11.541 MiB | `docs/figures_contour_notation_20260911/DCFnet_Figures_Contour_Notation_20260911_final.pptx` | `070AA5E86BC021B3` |
| `.tmp_teacherfig_20260910/draft.pptx` | 10.089 MiB | `docs/figures_teacher_revision_20260910/DCFnet_Figures_Expanded_20260910.pptx` | `EB1D965DD26650F9` |
| `.tmp_allfig_20260910/draft.pptx` | 6.360 MiB | `docs/figures_redraw_20260910/DCFnet_All_Figures_Editable_20260910_v2.pptx` | `0571440658E25788` |
| `.tmp_dcfnet_figures_20260905/draft.pptx` | 3.193 MiB | `docs/figures_revision_20260905/DCFnet_主图与分图_课堂修订完整版_20260905_v2.pptx` | `63519A9B7350241C` |
| `.tmp_mainfig_20260910/draft.pptx` | 2.545 MiB | `docs/main_figure_redraw_20260910/DCFnet_Main_Figure_Editable_20260910.pptx` | `5F46E64AE107C87C` |
| `.tmp_manuscript_english_polished_20260906/draft.pptx` | 3.193 MiB | `docs/manuscript_english_polished_20260906/DCFnet_Figure_Source_Polished_20260906_final.pptx` | `3665D550F574944D` |
| `.tmp_manuscript_round2_20260906/draft.pptx` | 3.193 MiB | `docs/manuscript_round2_20260906/DCFnet_Editable_Figures_Second_Revision_20260906_v2.pptx` | `0036871E6EA62BE6` |
| `.tmp_complete_figures_20260920/assembled.pptx` | 68.849 MiB | `docs/paper_complete_teacher_review_20260920/All_Figures_Complete_20260920.pptx`（tracked） | `48DD91800B714331` |

(a) 引用：`assembled.pptx` / `draft.pptx` 全仓 grep **无脚本读写命中**（`assemble_deck.ps1` 只"写"不"读"）；(b) 校验文档：未被任何哈希清单记录；(c) 唯一副本：上表逐字节相同副本均在 tracked 的 `docs/**` 中保留。

### #5 `.tmp_complete_figures_20260920/All_Figures_Complete_20260920.pptx.validation.json.bak_20260920` —— 0.004 MiB

白名单 #2；同目录存在非 `.bak` 的 `…Finalized….validation.json` 与 `…Complete….validation.json`（`.bak` 为 09-20 中间态）。`plot_primary.py` 依赖目录本身，但**不读该 `.bak`**（grep 实测）。

### 删除项统计

| 分组 | 文件数 | 释放（MiB） | tracked / untracked |
|---|---:|---:|---|
| #1 `docs/…20260914/*.bak*` | 23 | 220.07 | 7 / 16 |
| #2 `docs/…20260914/figures/superseded/` | 9 | 6.24 | 9 / 0 |
| #3 `docs/…/All_Figures_Complete….pptx.bak_20260922` | 1 | 68.29 | 0 / 1 |
| #4 `.tmp_*/draft.pptx` + `assembled.pptx` | 8 | 108.96 | 0 / 8 |
| #5 `.tmp_…/….validation.json.bak_20260920` | 1 | 0.004 | 0 / 1 |
| **合计** | **42** | **403.56** | **16 tracked / 26 untracked** |

> tracked-path 计 16 个（`git status` 显示 16 条 ` D`）；其余 26 个被 `.gitignore` 的 `*.docx` / `*.bak*` / `/.tmp_*/` 忽略。**未提交**（按任务要求），需作者决定是否 `git add -u` 后提交。

---

## 建议删除清单（**未执行**，需作者决定）

按"收益 / 风险"排序，每条给证据与理由：

| # | 条目 | 体积 | 证据 | 为何未删 |
|---|---:|---|---|---|
| S1 | `docs/manuscript_reference_matching_20260914/figures/` 中与 `docs/figures_reference_matching_20260914/`、`docs/figures_package_20260917/` **逐字节相同**的那批图（`fig7_multimethod_*`、`panel_interaction_cases*`、`figS3_extra_cases*`、`panel_canvas_coverage` 等） | 约 130 MiB | SHA-256 实算；`AUTHORITATIVE_SOURCE_DIFF_20260921.md:160` 与 `ARTIFACT_INDEX.md` §3.2 均把"逐类别多方法 36 张"记为权威稿侧图件 | 三处都自称"图件包"，"该保留哪一处"是**版式/交付口径**问题（`FIGURE_BINDING.md` 行绑定的是 `figures_reference_matching_20260914/`），非纯技术判断 |
| S2 | `dist/replication_package_20260920/` | 449.25 MiB（2 489 文件） | 其 1 503 个文件在仓内存在逐字节相同副本；`README.md:*`、`GITHUB_METADATA.md:109`、`ISSUE_REGISTER` R-12 均引用 | 它是**已交付的复现包**（含 `SHA256SUMS`、`SOURCE_COMMIT.txt`），删掉即失去交付物。**建议**：确需腾空间时可整体移出仓库到外部归档，而不是删其中文件 |
| S3 | `.tmp_*` 中 >20 MiB 的渲染中间件（8 个 `presentation.json` 等，见 §B.3） | 约 502 MiB | 均为同目录 `build.mjs` / `*.mjs` 的中间产物；`.tmp_crossref/verify_figure_manifest.py` 等小文件才是被引用项 | 白名单 #3 要求"证实无引用"；这些目录内**确有被文档引用的小文件**，需逐目录逐文件核对（本轮只核到目录级 → 判"拿不准"） |
| S4 | `.tmp_revision_20260922/snapshot/`（`All_Figures_before.pptx`、`Reference_Matching_before.docx`） | 95.29 MiB | 两份都与现役交付件**逐字节相同** | 是本次会话（09-22）**手工留的 before 快照**，且 `Reference_Matching_before.docx` 与权威稿同为 `F3CAE3B4…`；删除无信息损失，但会话快照属"作者意图"，不代删 |
| S5 | `experiments/dynamic_fusion/confirmation_ksdd2_20260918/_smoke_round2/` | 79.08 MiB | `ARTIFACT_INDEX.md` §4.2 行 132：「**明确不得引用其数字**（F_SPEC 已写明：建立在合成 B/C 特征上，不是结果）」；其 `p0_support/support_manifest_ksdd2.json` 与非 smoke 目录逐字节相同 | 位于 `experiments/**`（红线区；保护范围含"csv/json/npz 汇总与逐图产物"）。索引虽背书，仍不代作者删实验目录 |
| S6 | `experiments/.../generalization_mvtec_visa_20260915/{_maskfix_smoke,_regression_check}/`、`seeds_extension_20260917/_smoke_canonical/`、`unified_fusion_paper_support_20260913/_smoke/` | 16.8 MiB | `ARTIFACT_INDEX.md` §4.2 行 131：「属冒烟，引用时不是结果」 | 同上（红线区） |
| S7 | 根目录 2026-08 计划类文档（`PLAN.md`、`SECOND_STAGE_PLAN.md`、`NEXT_ACTIONS.md`、`HANDOFF.md`、`PROJECT_STATUS.md`、`GPU_OVERNIGHT_PLAN.md`、`AUTO_GPU_SCHEDULER.md`）与 `docs/dynamic_fusion_*.md`、`docs/cpu_*.md`、`docs/visa_*`、`docs/v2_*`、`docs/*_20260809.md` 等 20+ 个旧主线文档 | 约 0.8 MiB | `docs/README.md` §0 声明"不代表当前结论"；`ARTIFACT_INDEX.md` §2.2 行 72 | 属"作者是否还要留历史"的判断；`.tar.gz`/归档优于直接删。**建议**移入 `docs/archive_pre20260920/` |
| S8 | `.tmp_*` 中其余 ≤20 MiB 的可再生渲染件（png/pdf，约 300 MiB） | 约 300 MiB | 同 S3 | 同 S3 |
| S9 | `docs/figures_package_20260917/`（127 文件，181.4 MiB）中与 `docs/figures_reference_matching_20260914/` 重复的部分 | 约 165 MiB | SHA-256 实算 | 该目录是"打包视图"，删成员会破坏包的完整性 |
| S10 | `experiments/dynamic_fusion/{innovation_*,v2,v3*}/`（2026-07~08 负结果线） | 数十 GiB（含 npz） | `ARTIFACT_INDEX.md` §4.2 行 135 明写"**保留**作历史" | 索引已裁决保留；且属红线区 |
| S11 | `.trae/`（`documents/night_run_handover_20260917.md` 及副本） | 0.1 MiB | `ARTIFACT_INDEX.md` §五 指向它；`docs/specs/` 有副本 | 是编辑器/助手过程目录，`git status` 显示为未跟踪；`ARTIFACT_INDEX.md` 明确引用，**不删**（仅登记） |

---

## 体积统计（清理前 / 后）

| 指标 | 清理前 | 清理后 | 变化 |
|---|---:|---:|---:|
| 工作区文件数（排除 `.git`、`.venv*`） | 158 872 | 158 830 | **−42**（仅计删除；本报告 +1 后为 158 831） |
| 工作区体积（同上） | 756 427 081 684 B | 756 003 919 855 B | **−423 161 829 B（−403.56 MiB）**（本报告约 30 KB 已计入"后"值） |
| `git ls-files` 跟踪文件数（index，未提交） | 16 047 | 16 047 | 0 |
| 磁盘上实际存在的 tracked 路径 | 16 047 | 16 031 | −16（`git status` 16 条 ` D`） |
| tracked 工作区体积 | 3 091 MiB | 3 084.4 MiB | −6.6 MiB |
| git 仓库体积（`.git/`） | 6 565.4 MiB | 6 565.4 MiB | 0（未提交，对象未回收） |
| `docs/` | 1 245.5 MiB / 816 files | 950.9 MiB / 783 files | **−294.6 MiB / −33 files** |
| `.tmp_complete_figures_20260920/` | 379.95 MiB / 340 files | 311.10 MiB / 338 files | −68.85 MiB |
| 其余 `.tmp_*` 合计 | 约 1 213 MiB | 约 1 105 MiB | −108.96 MiB |

> 两点必须说清：
> 1. **释放主要在 gitignored 侧**（397.0 MiB / 26 files），tracked 侧只有 6.6 MiB。因此 `git` 仓库不会变小（除非作者提交后 `git gc`，且即使那样也只回收这 6.6 MiB 的对应对象）。工作区体积的 99.9% 是 `outputs/`（480 403.9 MiB）、`experiments/`（185 746.2 MiB）、`data/`（39 143.3 MiB）、`methods/`（12 855 MiB）、`.git`（6 565.4 MiB）等**机器本地缓存与数据集**，全部在本次红线之外。
> 2. 全仓体积对比用同一脚本口径测（`Get-ChildItem -Recurse -File -Force`，排除 `\.git\` / `\.venv`）：文件数 −42、字节 −423 161 829，与逐条删除记录**完全吻合**（42 个文件、403.56 MiB）。

---

## 未做 / 不确定

1. **未哈希 `outputs/`、`experiments/dynamic_fusion/`、`methods/`、`data/`**（合计约 718 GiB）。理由：它们是机器本地缓存/数据集，A 节关心的是"仓库内容里的重复文档"，且全量哈希不可行。⇒ 这些目录内可能仍有重复 npz/日志，**未排查**。可加分项：对 `experiments/**/*.json|csv`（小文件）单独做一次体积碰撞 + 哈希。
2. **`.tmp_*` 只做到目录级引用核查，未逐文件**。白名单 #3 要求"grep 证明无引用且其中无唯一 json/md/csv 证据"；我确认了 `.tmp_*` 内**存在**被文档/脚本引用的唯一小文件（4 处），因此对整目录判定为"拿不准"→ 只列 S3/S4/S8，未删。若作者同意按"删大留小"执行，建议先跑一次 `git add -A` 之外的独立备份，再逐目录比对。
3. **`docs/` 三处图件集的"留哪一处"未裁决**（S1/S9）：这是版式交付口径问题，非技术可证问题。
4. **`dist/` 未动**（S2）：交付副本，删即失交付物。
5. **16 条 tracked 删除未提交**：按任务"不做 git 提交"要求保留在工作区。若作者决定提交，注意这 16 条会使仓库 tracked 体积 −6.6 MiB。
6. **`experiments/` 下的 `_smoke_*` 与 `*.bak_20260919` 未删**（S5/S6）：红线优先于白名单。
7. **`.gitignore` 的两条"死规则"未清理**：`docs/figures_package_*.zip`（盘上已无该 zip）、`data/visa_candle_smoke/` 等可能已不存在。未验证全部规则，仅在 §B.2 记录 `figures_package_*.zip` 这条。
8. **`ISSUE_REGISTER_20260920.md` R-12**（"`dist/` 未跟踪且未被 `.gitignore` 覆盖"）现象已不成立（`.gitignore:73` 为 `dist/`），但该表**未加刷新行**。本轮未改（体例上应由作者在 §〇ter 追加），见 §D.3。
9. **文档"最新/current"标注体系未统一**：`docs/README.md`（2026-09-14 整理）、`ARTIFACT_INDEX.md`（09-19）、`HANDOVER_20260919.md`（09-19）、`ISSUE_REGISTER`/`REMEDIATION_PLAN`（09-20 + 09-22 刷新行）、`论文与图件问题汇总`（09-21 + 09-22）**共 5 套并存的状态口径**。本轮只用"指针 + 括注"补了最关键处，没有做整体重构（那是另一次独立任务）。
10. **未处理 `.trae/`、`.vs/`、`.pytest_cache/`、各 `__pycache__/`**：`.trae/` 被 `ARTIFACT_INDEX.md` 引用故保留；其余为可再生的编辑器/工具缓存（合计 < 1 MiB），无清理价值。

---

## 附：本次扫描的可复现命令

```powershell
# 1) 体积碰撞组 → SHA-256 分组
$files = ...                                              # 见正文 A.1 的目录集合
$files | Group-Object Length | Where-Object { $_.Count -ge 2 } |
  ForEach-Object { $_.Group } |
  ForEach-Object { [pscustomobject]@{ Hash=(Get-FileHash $_.FullName -Algorithm SHA256).Hash; Rel=$_.FullName } } |
  Group-Object Hash | Where-Object { $_.Count -ge 2 }

# 2) 工作区体积（排除 .git / .venv*）
(Get-ChildItem -Recurse -File -Force |
  Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch '\\\.venv' } |
  Measure-Object Length -Sum)

# 3) 发布点核对
git rev-list --count origin/main..HEAD ; git branch -vv ; git status --porcelain
```

---

# §E 2026-09-22 第二轮执行

> 起点：本报告第一轮（§已执行 42 个文件 / 403.56 MiB）**已由作者提交**为 `ff6db31`
> （"clean up duplicates and bring the status documents up to date"），
> `main [origin/main]`、`origin/main..HEAD = 0`、工作区仅 `?? .trae/`。
> 本节记录第二轮四项清理（`.tmp_*` 渲染中间件 / `_smoke_*` 大件 / 三处重复图件集 / 2026-08 旧文档归档）。
>
> **本轮红线遵守情况**：未触碰任何已发布实验产物（`experiments/**` 的 csv/json/npz 汇总与逐图证据）、
> 冻结输入（`data/**`）、权威稿、版式母本、`LICENSE`、`requirements_repro.txt`、`figure_sources/**`、
> `dist/**`；未做 git 提交、未推送、未用 GPU、未跑实验。**凡被脚本读写的路径一律保留**（见 §E.5）。

## E.1 任务 1：`.tmp_*` 渲染中间件 —— 已执行 19 个文件 / 662.51 MiB

「三查」逐条结论：

| 查项 | 结论 |
|---|---|
| (a) 全仓 grep 路径/文件名 | `presentation.json` 全仓命中**仅本审计报告**；`draft-raw.pptx` / `superseded-*.pptx` / `All_Figures_before.pptx` / `Reference_Matching_before.docx` 在报告外**零命中**（`docs/paper_complete_teacher_review_20260920/figures/multimethod/*.json` 引用的是 `.tmp_complete_figures_20260920\qualitative\*`，属**保留项**） |
| (b) 校验文档哈希登记 | 未被 `VERSIONED_EVIDENCE.sha256`、`submission_repro_20260827/SHA256SUMS`、`论文与图件问题汇总`、`ISSUE_REGISTER`、`ACCEPTANCE_20260920`、`VALIDATION_20260918.*`、`ARTIFACT_INDEX`、`FIGURE_BINDING` 的任一条记录为当前值 |
| (c) 逐字节同源 | `snapshot/` 两份**SHA-256 实算与现役交付件完全相同**（见下表）；`presentation.json` 是 `build.mjs` 的 `JSON.stringify(p.toProto())` 纯序列化中间件（`.tmp_contour_notation_20260911/build.mjs` 末行实读），同目录 `draft-raw.pptx` 才是可编辑源、`finalize.mjs` 只吃 `draft.pptx`，故删除 `.json` 不动任何链；`draft-raw.pptx`/`superseded-*.pptx` 是各轮 finalize 之前的候选件，其**成品均在 tracked 的 `docs/**` 保留**（§已执行 #4 已核过同源关系） |

| # | 路径 | 字节 | 判据 |
|---|---|---:|---|
| 1 | `.tmp_contour_notation_20260911/presentation.json` | 156 552 738 | 中间件，无引用 |
| 2 | `.tmp_teacherfig_20260910/presentation.json` | 135 892 827 | 同上 |
| 3 | `.tmp_allfig_20260910/presentation.json` | 85 054 721 | 同上 |
| 4 | `.tmp_dcfnet_figures_20260905/presentation.json` | 42 555 044 | 同上 |
| 5 | `.tmp_manuscript_english_polished_20260906/presentation.json` | 42 559 203 | 同上 |
| 6 | `.tmp_manuscript_round2_20260906/presentation.json` | 42 555 228 | 同上 |
| 7 | `.tmp_mainfig_20260910/presentation.json` | 34 172 146 | 同上 |
| 8 | `.tmp_revision_20260922/snapshot/All_Figures_before.pptx` | 72 193 447 | ≡ `docs/paper_complete_teacher_review_20260920/All_Figures_Complete_20260920.pptx`，SHA-256 均为 `48DD91800B714331…`（实算） |
| 9 | `.tmp_revision_20260922/snapshot/Reference_Matching_before.docx` | 27 724 755 | ≡ **权威稿** `docs/…/Reference_Matching_Complete_English_20260920.docx`，SHA-256 均为 `F3CAE3B491A99F86…`（实算） |
| 10–19 | `draft-raw.pptx` ×7（`contour_notation` 12 095 989 / `teacherfig` 10 580 200 / `allfig` 6 670 820 / `dcfnet_figures` 3 349 057 / `manuscript_english_polished` 3 349 179 / `manuscript_round2` 3 349 110 / `mainfig` 2 668 796）＋ `superseded-v1.pptx` 6 668 948、`superseded-final-v1.pptx` 3 347 969、`superseded-first-figures.pptx` 3 348 210 | 55 428 278 | 各轮 finalize 之前的候选/被取代件；同目录 `build.mjs`/`build_figures.mjs` 与同目录 `*.json` 输入均在盘，成品在 tracked `docs/**` |
| | **合计** | **694 688 387（662.51 MiB）** | |

## E.2 任务 2：`_smoke_*` —— 已执行 8 个文件 / 95.05 MiB（保留全部小证据）

`ARTIFACT_INDEX.md` §4.2 行 131/132 已声明"属冒烟，引用时不是结果"。grep **确认目录本身被引用**
（`confirmation_ksdd2_20260918/SMOKE_TEST.md`、`F_SPEC.json:399-400` 指向 `smoke_d_branch.py` 与
`SMOKE_RESULTS.json`），故**目录与全部 ≤1 MB 的 json/md/csv 证据一律保留**，只删可再生的 npz/npy 大件。

| 路径 | 字节 | 判据 |
|---|---:|---|
| `…/_smoke_round2/canonical/B/ksdd2_s0_k8/ksdd2.npz` | 11 269 616 | 冒烟夹具（`smoke_fixture=True`），可由 `smoke_d_branch.py` 重生 |
| `…/_smoke_round2/canonical/C/ksdd2_s0_k8/ksdd2.npz` | 22 535 856 | 同上 |
| `…/_smoke_round2/out/features/query/ksdd2_ksdd2.npy` | 6 635 648 | D 支真实编码特征缓存（可再生） |
| `…/_smoke_round2/out/features/ref/ksdd2_s0_ksdd2.npy` | 17 694 848 | 同上 |
| `…/_smoke_round2/out_run/features/query/ksdd2_ksdd2.npy` | 6 635 648 | **与 `out/features/query/` 逐字节相同**（SHA-256 `F759521831011252…`） |
| `…/_smoke_round2/out_run/features/ref/ksdd2_s0_ksdd2.npy` | 17 694 848 | **与 `out/features/ref/` 逐字节相同**（SHA-256 `963F315E7F7DF68C…`） |
| `…/unified_fusion_paper_support_20260913/_smoke/units/mpdd_s0_k2/bracket_black/evaluation_scores.npz` | 11 326 699 | 冒烟单元分数缓存 |
| `…/unified_fusion_paper_support_20260913/_smoke/units/mpdd_s0_k2/bracket_black/patch_scores.npz` | 5 871 773 | 同上 |
| | **合计 99 664 936（95.05 MiB）** | |

**保留**：`_smoke_round2/{smoke_d_branch.py, SMOKE_RESULTS.json, p0_support/support_manifest_ksdd2.json,
out*/D_BRANCH_SPEC.json, out*/feature_manifest.csv, out_run/new_method_metrics.csv, out_run/unit_status.csv,
out_run/resource_usage.json, out_run/units/**/metrics.csv|flip_stats.csv|per_image.csv|region_stats.csv|
evaluation_scores.npz(188 KB)|patch_scores.npz(64 KB)|sample_pairs.npz(3 KB)}`
与 `_smoke/units/**/{configurations.json, coupling_controls.csv, DONE.json, flip_stats.csv, invariants.json,
metrics.csv, per_image.csv, progress.json, region_stats.csv, reference_permutations.npz, sample_pairs.npz}`；
其余 8 个 `_smoke*` 目录（`generalization_mvtec_visa_20260915/{_maskfix_smoke,_regression_check}`、
`seeds_extension_20260917/_smoke_canonical`、`representation_matching_interaction_20260914/_patchcore_{local128,official224}_smoke`、
`v4_vision_text_20260819/05_v2_smoke`、`20260730_visa_s0_k1_smoke_*`）**全部 ≤65 KB，整体保留**。

## E.3 任务 3：三处重复图件集「只留一处」—— 保留 1 处 + 归档 1 处 + 保留 1 处，**释放 0 B**

先用**逐文件 SHA-256** 对 `docs/figures_reference_matching_20260914/`（122 个文件，161.83 MiB）做保留基准：

| 候选 | 文件数 | 与保留处同哈希 | 仅在候选处 | 处置 |
|---|---:|---:|---:|---|
| `docs/manuscript_reference_matching_20260914/figures/` | 108 | **108** | 0 | **未执行删除**（见下） |
| `docs/figures_package_20260917/` | 127 | 108 | 19 | **整包归档**（见下） |

1. **保留处 = `docs/figures_reference_matching_20260914/`**。依据：`FIGURE_BINDING.md` 就在此目录；
   所有图脚本的 `--out-dir` 默认值、`sync_to_manuscript.py` 的 `DEFAULT_SRC`
   （`scripts/figures_reference_matching_20260914/sync_to_manuscript.py:31`）都指向它；
   `scripts/paper_complete_teacher_review_20260920/figure_sources/{plot_extra.py:16, plot_supplementary_figures.py:26,
   build_methods.mjs:11}` **实读**它的 `figS2_*.json`、`figS4_*.json`、`style.mjs`。
2. **`docs/manuscript_reference_matching_20260914/figures/` 不删**（108/108 与保留处逐字节相同，但**红线优先**）：
   - `scripts/manuscript_build_20260914/figures.json` 显式登记 `docs/manuscript_reference_matching_20260914/figures/*.png`
     （13 处），`build.py:219-224` 按该 json **解析并加载**这些图片 ⇒ **脚本读路径**；
   - `sync_to_manuscript.py`（`DEFAULT_DST`，`:32`）与 `build_cn_docx.py`（`FIGS` 默认 `<out-dir>/figures`）
     ⇒ **脚本写路径**；
   - `FIGURE_BINDING.md:48` 明记它是"本稿实际嵌入的副本"。
   ⇒ 属"任何被脚本读写的路径"，按红线**保留**，未尝试"移到保留处再删目录"。
3. **`docs/figures_package_20260917/` → `docs/archive_pre202609/figures_package_20260917/`（`git mv`，127 个文件）**：
   108 个文件在保留处有逐字节同源；另 10 个 `06_previous_theme_DCFnet/**` 在
   `docs/figures_teacher_revision_20260910/`、`docs/figures_redraw_20260910/`、`docs/main_figure_redraw_20260910/`
   有逐字节同源（实算）；**剩 9 个只在包内存在**，且正是 `FIGURE_BINDING.md` §五 按名字列出的"已移入 superseded"
   清单（`main_figure_final_20260915.{png,pptx}`、`main_figure_reviewed_20260915.{png,pptx}`、
   `main_figure_fixed_support_matching_20260914.{png,pptx}`、`interaction_intervals.png`、`interaction_by_budget.png`、
   `qualitative_mpdd_matching_improvements.png`）。因"只在待删处有"的文件不得删除、又是自成一体的"图件包"，
   按任务 3 第 3 条**改为归档而非直删**（`05_superseded/` 的 9 个唯一副本一并原样保留在归档内）。

> **释放量 0 B**（任务 3 预估的"约 130 MiB"落在 `manuscript_reference_matching_20260914/figures/`，
> 该处被红线判为脚本读写路径）。三处重复的**歧义已消除**：现役链只认 `figures_reference_matching_20260914/`，
> 另一个只在归档区、一个在正文源链（脚本输入，必需）。

## E.4 任务 4：2026-08 旧主线与过程文档归档 —— `git mv` 158 条重命名 / 31 个文件 + 1 个目录

新建 `docs/archive_pre202609/`，入口说明 [`README_ARCHIVE.md`](archive_pre202609/README_ARCHIVE.md)
（写明"不代表当前结论；当前权威入口 = `README.md` / `docs/HANDOVER_20260919.md` / `docs/ARTIFACT_INDEX.md`"，
并附完整归档清单、未归档理由、已知遗留链接）。

| 组 | 数量 | 原路径 → 新路径 |
|---|---:|---|
| 根目录 2026-08 计划类 | 7 | `PLAN.md`、`SECOND_STAGE_PLAN.md`、`NEXT_ACTIONS.md`、`HANDOFF.md`、`PROJECT_STATUS.md`、`GPU_OVERNIGHT_PLAN.md`、`AUTO_GPU_SCHEDULER.md` → `docs/archive_pre202609/`（同名） |
| `docs/` 旧主线/过程文档 | 24 | `cpu_preparation_and_late_gpu_window_plan_20260803.md`、`cpu_work_completion_report_20260803.md`、`current_period_execution_plan_20260803.md`、`dynamic_fusion_ablation_and_visualization_20260809.md`、`dynamic_fusion_design.md`、`dynamic_fusion_development_analysis_20260803.md`、`dynamic_fusion_experiment_protocol.md`、`dynamic_fusion_final_validation_audit_20260808.md`、`dynamic_fusion_k2_k4_completion_report_20260804.md`、`dynamic_fusion_scientific_analysis_20260809.md`、`dynamic_fusion_seed0_diagnostic_analysis_20260804.md`、`dynamic_fusion_selected_candidate_pixel_evaluation_20260805.md`、`dynamic_fusion_temperature_margin_sensitivity_20260805.md`、`dynamic_fusion_v2_development_and_gpu_plan_20260810.md`、`DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md`、`DYNAMIC_FUSION_NEXT_STEPS.md`、`mvtec_results_scope_and_main_table_template_20260808.md`、`prediction_schema.md`、`project_state_reconciliation_20260809.md`、`related_literature_screening_2026_20260810.md`、`representative_literature_and_validation_plan_20260810.md`、`sources.md`、`v2_data_preparation_and_freeze_20260810.md`、`visa_experiment_protocol_and_results_draft_20260804.md` → `docs/archive_pre202609/`（同名） |
| 图件包（任务 3 归档侧） | 127 | `docs/figures_package_20260917/` → `docs/archive_pre202609/figures_package_20260917/` |

**归档口径**：`docs/*.md` 以 `mtime ≤ 2026-08-31` 为客观判据（全部为 2026-07-25 ~ 2026-08-27），
另加 §C/§D.3 点名的两个大写 `DYNAMIC_FUSION_*.md` 旧"权威计划"。
`git status` 显示 **158 条 `R`（rename）**，无 `D`，历史保留。

**链接修复**：全仓 grep 后，**当前状态类文档中共 2 处**需要改路径，均已修：

| 文件:行 | 改前 | 改后 |
|---|---|---|
| `docs/README.md:107` | `[DYNAMIC_FUSION_NEXT_STEPS.md](DYNAMIC_FUSION_NEXT_STEPS.md)`、`[DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md](…)`、`dynamic_fusion_*.md` | `archive_pre202609/…`（三个都改，并注明"2026-09-22 已移入 archive_pre202609/"） |
| `docs/ARTIFACT_INDEX.md:160` | `docs/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md` | `docs/archive_pre202609/DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md` |

根 `README.md`、`docs/HANDOVER_20260919.md`（其 `PLAN.md` 指 `experiments/…/limitation_closure_20260915/PLAN.md`，
非根 `PLAN.md`）、`docs/SUBMISSION_METADATA.md`、`docs/GITHUB_METADATA.md` **经 grep 确认无相关引用，未改**。

**未修的旧路径引用**：约 **51 处 / 38 个文件**，全部属"历史记录类"，按任务约定不动，分布为：
① `docs/specs/**`、`.trae/documents/**` 过程目录（2 处）；
② `docs/` 内的历史/被取代文档（`README_HISTORY_pre20260920.md`、`CURRENT_DYNAMIC_FUSION_STATUS.md`、
`current_dynamic_fusion_status.json`、`introduction_research_20260825/**`、`paper_writing_preparation_20260830/**`、
`submission_reproducibility_20260826/README.md` 等）；
③ `experiments/**` 的状态/审计记录（`v3_*`、`v3_3*`、`v4_vision_text_20260819/**`、
`reconciliation/*/link_check.json`、`freeze/a1_mpdd_w05/phase7_post_freeze_20260817.md`、`dynamic_fusion/README.md`）；
④ 脚本注释/docstring 与测试断言文本（`scripts/limitation_closure_20260915/a1_btad03_corrected_grid.py:21`、
`scripts/unified_fusion_paper_support_v1/export_k8_cache.py:143`、`scripts/p1_d_fairness_table.py:187`、
`scripts/validation_handoff_20260911/finalize_e8.py:83`、`tests/test_v4_contracts.py:4`、
`src/industrial_ad/fusion/v3_3_clean.py:3` 等）；
⑤ 归档区内部互引（`DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md` ↔ `DYNAMIC_FUSION_NEXT_STEPS.md`，
两者现在同目录，原文的 `docs/` 前缀写法不再成立）。

## E.5 未执行清单与原因（**拿不准的一律未动**）

| # | 条目 | 体积 | 为何未执行 |
|---|---|---:|---|
| U1 | `docs/manuscript_reference_matching_20260914/figures/` | 158.61 MiB | **被脚本读写**：`scripts/manuscript_build_20260914/figures.json`+`build.py:219-224` 读、`sync_to_manuscript.py --apply`/`build_cn_docx.py` 写。108/108 逐字节同源，但红线"不得删除被脚本读写的路径"优先 —— 这是任务 3 释放量归零的唯一原因 |
| U2 | `.tmp_univad/pydensecrf_src/build/**`（12 个 `.obj` 等）＋ `.tmp_univad/dl/*.tar.gz` | 39.6 + 3.0 MiB | 是 vendored C++ 源码的 MSVC 构建产物/下载缓存，**不属"渲染中间件"口径**；且目录本身被 `scripts/validation_handoff_20260911/univad_stage2_eval.py:100` 注释引用，只做登记 |
| U3 | `.tmp_*` 内 >1 MB 的成稿渲染 PDF（`manuscript_20260905` 5 个、`english_manuscript_20260914` 2 个、`manuscript_{review,round2,chinese_review,english_polished}_*` 各 1–2 个） | 约 26 MiB | 各轮成稿的 Word→PDF 渲染快照，非"构建中间件"；再生依赖本机 Word/WPS COM，且各轮 docx 已不在盘 ⇒ 判"拿不准"保留 |
| U4 | `.tmp_complete_figures_20260920/**`（`qa_doc_sheets`/`qa_doc_final_sheets`/`qa_ppt_sheets` 及 `qualitative/`、`plots/`、`all_images.pptx`、`CambriaMath.ttf`、`word.pdf`） | 311.10 MiB | **现役权威图件链工作目录**（`ARTIFACT_INDEX.md:122` 声明"不得删除"；`plot_primary.py:7,9,11` 实读写，`build_deck.mjs:25` 写 `all_images.pptx`）。其中 `qa_doc_sheets/` 与 `qa_doc_final_sheets/` 互为逐字节副本（6 对），但属该轮 QA 证据且目录现役 ⇒ 未动 |
| U5 | `.tmp_lesson_20260912/teacher_docx_extract.json`（1.33 MB） | 1.33 MB | 唯一抽取证据，源 docx 不在盘 ⇒ 保留（虽略超 1 MB 阈值） |
| U6 | `docs/{PAPER_SUBMISSION_HANDOFF_AND_REPRODUCIBILITY_PLAN_20260826, PRE_MANUSCRIPT_READINESS_AUDIT_20260827, PROJECT_PROGRESS_AND_MANUSCRIPT_PLAN_FOR_SUPERVISOR_EN_20260827}.md` | 约 46 KB | 被 `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256`（第 3/11/12 行）**登记了 SHA-256 + 路径**；移动会使该哈希清单路径失效 ⇒ 三查(b) 拦下 |
| U7 | `docs/remp_ad_adaptclip_audit.md`、`docs/reproduction_notes.md` | 约 17 KB | mtime 属 2026-07~08，但当前文档仍以它们为依据/出处：`docs/BASELINE_EXPANSION_PLAN_20260921.md:84`、`docs/论文与图件问题汇总_仅复核_20260921.md:157`、`docs/environment_matrix.md:72,75`（**这 3 个文件不在任务给的 6 个"当前状态类文档"清单内**，移动会造成未授权的断链）⇒ 保留原位 |
| U8 | 其余 8 个 `_smoke*` 目录（合计 ≤65 KB） | 0.07 MiB | 全是唯一 json/csv 小证据（`export_report_*.json`、`PAPER_C_RUN_SUMMARY.json` 等），按任务 2 第 2 条必须留下 |
| U9 | `dist/replication_package_20260920/` | 449.25 MiB | 已交付复现包（含 `SHA256SUMS`、`SOURCE_COMMIT.txt`），删即失交付物（沿用第一轮 S2 结论） |
| U10 | `.tmp_revision_20260922/snapshot/` 剩余小文件（`figures.json` 17.8 KB、`tables.json` 34.4 KB、`build.py` 18.0 KB、`论文与图件问题汇总_仅复核_20260921.md` 40.9 KB） | 0.11 MiB | ≤1 MB 且属本次会话快照证据，按"留小"口径保留 |

## E.6 释放与体积统计（口径同本文 §体积统计）

| 指标 | 清理前（本轮起点） | 清理后 | 变化 |
|---|---:|---:|---:|
| 本轮**显式删除**字节 | — | — | **794 353 323 B = 757.55 MiB**（任务 1：694 688 387；任务 2：99 664 936） |
| 工作区体积（`Get-ChildItem -Recurse -File -Force`，排除 `\.git\`/`\.venv*`） | 756 003 963 240 B | 755 209 640 090 B | **−794 323 150 B（−757.53 MiB）**（净额 = 删除 794 353 323 − 本轮新增/改写的 md 30 173 B） |
| 工作区文件数（同口径） | 158 831 | 158 805 | **−26**（删除 27 个 + 新增 `README_ARCHIVE.md` 1 个） |
| `docs/` | 997 179 500 B / 784 files | 997 308 171 B / 792 files | +128 671 B / **+8 files**（根目录 7 个 `.md` 移入 + `README_ARCHIVE.md`；本轮在 `docs/` 内**零删除**） |
| `docs/archive_pre202609/`（新建） | — | 190 531 692 B / 159 files | 归档区（= 127 图件包 + 24 旧文档 + 7 根文档 + 1 README） |
| `git ls-files` 跟踪文件数（index） | 16 031 | 16 031 | 0（全部为 rename，无增删） |
| `.tmp_*` 合计（28 个目录，实算） | 1 229.47 MiB / 1 849 files | 566.97 MiB / 1 830 files | **−662.51 MiB / −19 files**（= 任务 1 全部） |
| `docs/` 三处图件集 | 501.84 MiB | 320.44 MiB（`docs/` 内） + 181.40 MiB（归档） | 现役 `docs/` 内 −181.40 MiB（移到归档），全仓 0 |

> 释放全部发生在 **gitignored 侧**（`.tmp_*`、`*.npz`/`*.npy`），因此 git 对象库不变；
> 归档是 `git mv`，`git status` 只有 rename，没有删除。

## E.7 交付一致性复核（在盘实读）

| 复核项 | 结果 |
|---|---|
| 权威稿 `docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx` | **在盘**，SHA-256 `F3CAE3B491A99F86…`（= 09-22 重建版，未变） |
| 版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` | **在盘**，SHA-256 `9DB99E60CD3024D1…` |
| 现役 deck `All_Figures_Complete_20260920.pptx` / `All_Figures_Finalized_20260920.pptx` | **在盘**（72 193 447 / 71 604 011 B） |
| `LICENSE`、`requirements_repro.txt`、`scripts/paper_complete_teacher_review_20260920/figure_sources/` | **在盘** |
| `.tmp_complete_figures_20260920/{plot_fonts.py, plots/*, qualitative/fig7_multimethod_*}`、`.tmp_figure_revision_20260920/tables.json` | **全部在盘**（现役链未被触碰） |
| `docs/figures_reference_matching_20260914/{FIGURE_BINDING.md, figS2_*.json, figS4_*.json}`、`docs/manuscript_reference_matching_20260914/figures/fig1_framework.png` | **全部在盘** |
| `_smoke_round2/{smoke_d_branch.py, SMOKE_RESULTS.json, p0_support/support_manifest_ksdd2.json}`、`_smoke/units/**/metrics.csv` | **全部在盘** |
| `.tmp_allfig_20260910/validation-v2.json`、`.tmp_contour_notation_20260911/revise.py`、`.tmp_teacherfig_20260910/prepare.py`、`.tmp_univad/probe_cosine.py`、`.tmp_crossref/verify_figure_manifest.py`、`.tmp_english_manuscript_20260914/build.py` | **全部在盘**（第一轮 S3 点名的"被文档引用的小文件"一个没少） |
| `docs/archive_pre202609/{README_ARCHIVE.md, PLAN.md, DYNAMIC_FUSION_NEXT_STEPS.md, figures_package_20260917/05_superseded/main_figure_final_20260915.pptx}` | **在盘** |
| 例外说明 | 复核脚本初版把 `figure_sources` 写成根目录路径（实为 `scripts/paper_complete_teacher_review_20260920/figure_sources/`）、把 `figures.json` 写成 `docs/manuscript_reference_matching_20260914/`（实为 `scripts/manuscript_build_20260914/figures.json`）——两处为**复核脚本自身的路径笔误**，与本次清理无关，已实读纠正 |

## E.8 git status 摘要（供作者提交，**本轮未提交**）

```
$ git status --porcelain | Measure-Object -Line      → 163
$ git status --porcelain | %{ $_.Substring(0,2) } | Group-Object
  M   3    docs/README.md、docs/ARTIFACT_INDEX.md（链接修复）、docs/PROJECT_CLEANUP_AUDIT_20260922.md（本 §E）
  R 158    git mv 重命名（127 图件包 + 24 docs 旧文档 + 7 根文档）
  ??  2    .trae/（本轮之前就存在）、docs/archive_pre202609/README_ARCHIVE.md（新增）
$ git rev-list --count origin/main..HEAD → 0 ; git branch -vv → main [origin/main]
```

完整的 158 条 `R` 形如 `R  docs/figures_package_20260917/… -> docs/archive_pre202609/figures_package_20260917/…`、
`R  docs/DYNAMIC_FUSION_NEXT_STEPS.md -> docs/archive_pre202609/DYNAMIC_FUSION_NEXT_STEPS.md`、
`R  PLAN.md -> docs/archive_pre202609/PLAN.md` 等；**无 `D`**（本轮两处删除全在 gitignored 侧）。

**待提交清单**：3 个 `M`（`docs/README.md`、`docs/ARTIFACT_INDEX.md`、`docs/PROJECT_CLEANUP_AUDIT_20260922.md`）、
158 个 `R`、1 个新文件（`docs/archive_pre202609/README_ARCHIVE.md`）。
建议提交信息：`archive the pre-2026-09 mainline docs and de-duplicate the temporary render middleware`。
（`git add -A` 前请确认 `.trae/` 是否要一并纳入——它**不在**本轮改动范围内。）

## E.9 剩余建议（未执行）

1. **`.tmp_*` 还有约 445 MiB 可回收面**：`.tmp_univad` 构建产物（42.6 MiB）、各轮成稿 `.pdf`（约 26 MiB）、
   `.tmp_complete_figures_20260920` 的 `qa_*` 表（约 60 MiB，其中两套 `doc_sheets` 互为逐字节副本）与
   `.tmp_*` 内 ≤1 MB 的页面渲染 png（约 100 MiB）。这些要么超出口径、要么落在现役目录，需作者逐项裁决。
2. **`.tmp_revision_20260922/` 现在只剩 4 个小文件**（0.11 MiB）。若作者确认本次会话快照不再需要，
   可整目录删除（纯 gitignored）。
3. **任务 3 的空间收益可另议**：若作者愿意接受"临时把 `docs/manuscript_reference_matching_20260914/figures/` 移出
   再由 `sync_to_manuscript.py --apply` 重生"（脚本可重建，108/108 同源），可回收 158.61 MiB；
   本轮因红线判为脚本读写路径而未动。
4. **归档区内部互引未修**（`DYNAMIC_FUSION_DESIGN_REVIEW_AND_NEXT_PLAN.md` ↔ `DYNAMIC_FUSION_NEXT_STEPS.md`），
   以及 `docs/specs/**`、`.trae/documents/**`、`experiments/**`、脚本注释里的旧 `docs/` 路径；
   如需彻底清理，建议单独一轮"历史引用批量改写"（会改到历史文档正文，需作者同意）。
5. **`.gitignore` 死规则仍在**：`docs/figures_package_*.zip`（盘上无该 zip，且源目录已归档）。
6. 本轮**未做**：任何 git 提交/推送；任何 GPU/实验运行；`outputs/`、`experiments/dynamic_fusion/`、`methods/`、
   `data/`、`dist/` 的哈希与清理。
