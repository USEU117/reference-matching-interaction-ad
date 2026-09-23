# 目录归并记录：`docs/` 历史图件与历史稿件/评审目录 —— 2026-09-23

> 范围：仅 `docs/` 顶层的历史图件目录与历史稿件/评审目录。
> 方式：**只 `git mv`（归档，不删除；保留 git 历史）**；不 `git add`、不 `git commit`、不推送。
> 基线：`HEAD = 65485e4`（`main [origin/main]`）；执行前后 `git status --porcelain -- experiments data` 为空。
> 未用 GPU、未跑实验、未改任何研究结论 / 论文源 / 图件数值。

---

## 0. 根因

上一轮（2026-09-22）的清理报告 `docs/PROJECT_CLEANUP_AUDIT_20260922.md` **§A.4 结论**把三处同批图件目录
（`docs/figures_package_20260917/`、`docs/figures_reference_matching_20260914/`、
`docs/manuscript_reference_matching_20260914/figures/`）判为"**不是无条件可删**……故 A 节只给建议"。
那一轮**只执行了白名单内的 `.tmp_*` 重复副本删除**（同报告 §已执行 #3/#4/#8）与 §E 的图件包/旧文档归档，
**从未把 `docs/` 顶层的历史图件目录与历史稿件目录真正归并**。因此 `docs/` 顶层长期残留 5 个图件文件夹 + 多个历史稿件/评审目录。

本轮把"建议"落成"执行"：**归档而非删除**，零信息损失、可逆。

---

## 1. 现状调查（逐目录：文件数 / 字节 / tracked / 被引用处 / 判定）

判定口径：
- **现役（保留原位）**：被现役论文构建链（`scripts/paper_complete_review_20260920/build.py`、
  `scripts/figures_reference_matching_20260914/qa_layout.py` 与 `sync_to_manuscript.py`、deck 链）读取，或在任务"现役"清单内。
- **历史（归档）**：历史图件/稿件/评审材料，且**不被任何 tracked 脚本或配置按路径读取**。
- **tracked** 列 = `git ls-files docs/<dir> | measure -Line`。

| 目录 | 文件数 | 字节 | tracked | 被引用（`file:line`） | 判定 |
|---|---:|---:|---:|---|---|
| `figures_reference_matching_20260914/` | 125 | 170 426 237 | 125 | `qa_layout.py:169`、`sync_to_manuscript.py:31`、`figure_sources/{plot_extra.py:16,build_methods.mjs:11}`、`FIGURE_BINDING.md` | **现役·保留** |
| `figures_contour_notation_20260911/` | 7 | 15 009 382 | 7 | `docs/README.md:90`；`docs/requirements_notes_20260912/*`（历史）；`experiments/**`（红线） | **历史·归档** |
| `figures_expanded_20260910/` | 7 | 13 669 532 | 7 | `docs/README.md:120`；`PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md`；`archive_pre202609/README_ARCHIVE.md:49` | **历史·归档** |
| `figures_redraw_20260910/` | 7 | 9 732 062 | 7 | `docs/README.md:120`；`project_review_20260910/paper_audit.md`；`experiments/**`（红线） | **历史·归档** |
| `figures_revision_20260905/` | 7 | 4 627 518 | 7 | `docs/README.md:120`；`SCI_STRING_AUDIT_20260922.md:90`；`experiments/**`（红线） | **历史·归档** |
| `main_figure_redraw_20260910/` | 3 | 3 689 784 | 3 | `docs/README.md:120`；`archive_pre202609/README_ARCHIVE.md:49`；`experiments/**`（红线） | **历史·归档**（任务现状未点名，但同属 DCFnet 历史图件） |
| `main_figure_revision_20260920/` | 5 | 2 228 195 | 5 | `scripts/main_figure_20260920/build_main.mjs` | **现役·保留** |
| `manuscript_reference_matching_20260914/` | 114 | 166 610 394 | 114 | `scripts/manuscript_build_20260914/{build.py:50,build_cn_docx.py:28,figures.json}`、`scripts/figures_reference_matching_20260914/sync_to_manuscript.py:32`、`night2_validate_20260918.py:43` | **脚本读写·保留** |
| `manuscript_polished_20260919/` | 3 | 13 472 663 | 3 | `scripts/paper_complete_review_20260920/build.py:15`、`validate_revision23.py:16`、`.gitignore:83` | **现役读取·保留** |
| `manuscript_english_polished_20260906/` | 5 | 6 754 887 | 5 | `scripts/manuscript_build_20260914/{build.py:53,build_cn_docx.py:61}`、`finalize_e8.py:27` | **脚本读取·保留** |
| `manuscript_chinese_review_20260907/` | 2 | 49 330 | 2 | `scripts/validation_handoff_20260911/finalize_e8.py:29` | **脚本读取·保留** |
| `manuscript_revision_20260905/` | 4 | 116 514 | 4 | 仅历史文档互引 | **历史·归档** |
| `manuscript_review_20260906/` | 5 | 122 186 | 5 | 仅历史文档互引 | **历史·归档** |
| `manuscript_round2_20260906/` | 5 | 3 452 085 | 5 | 仅历史文档互引 | **历史·归档** |
| `manuscript_updated_20260919/` | 3 | 85 638 | 3 | `ISSUE_REGISTER_20260920.md:127`、`REMEDIATION_PLAN_20260920.md:55`（历史） | **历史·归档** |
| `project_review_20260910/` | 3 | 46 301 | 3 | `docs/README.md:110`、`docs/specs/…20260915.md:94`；历史互引 | **历史·归档** |
| `requirements_notes_20260905/` | 1 | 36 995 | 1 | `docs/README.md:111`、`REVIEW_CHECKLIST…20260923.md:211`、`SCI_STRING_AUDIT_20260922.md` | **历史·归档** |
| `paper_writing_preparation_20260830/` | 139 | 38 974 544 | 93 | `scripts/build_manuscript_figure_package.py:34`、`configs/*/gate_probe.json:4`、`src/…/innovation_v4_diagnostics/__init__.py:3` | **脚本/配置读取·保留** |
| `introduction_research_20260825/`、`specs/`、`paper_complete_review_20260920/`、`archive_pre202609/` | — | — | — | 现役 | **现役·保留** |
| `requirements_notes_20260912/`、`submission_reproducibility_20260826/` | — | — | — | 任务清单外 | **未在范围·保留** |

> 说明：`docs/` 顶层的"图件文件夹"实际有 5 个历史 + 2 个现役（`figures_reference_matching_20260914/`、
> `main_figure_revision_20260920/`）+ 1 个空目录。任务现状点名 5 个（含 4 个 `figures_*`），
> 本次把同批的 `main_figure_redraw_20260910/` 一并归档，以满足"顶层图件文件夹只剩 1 个现役"的复验口径。

---

## 2. 实际执行的 `git mv` 清单（52 条 rename，0 删除）

新建目录：`docs/archive_pre202609/figures/`。

### 2.1 历史图件目录（5 个 → `docs/archive_pre202609/figures/`）

| # | 原路径 | 新路径 | 文件数 | 字节 |
|---|---|---|---:|---:|
| 1 | `docs/figures_contour_notation_20260911/` | `docs/archive_pre202609/figures/figures_contour_notation_20260911/` | 7 | 15 009 382 |
| 2 | `docs/figures_expanded_20260910/` | `docs/archive_pre202609/figures/figures_expanded_20260910/` | 7 | 13 669 532 |
| 3 | `docs/figures_redraw_20260910/` | `docs/archive_pre202609/figures/figures_redraw_20260910/` | 7 | 9 732 062 |
| 4 | `docs/figures_revision_20260905/` | `docs/archive_pre202609/figures/figures_revision_20260905/` | 7 | 4 627 518 |
| 5 | `docs/main_figure_redraw_20260910/` | `docs/archive_pre202609/figures/main_figure_redraw_20260910/` | 3 | 3 689 784 |

### 2.2 历史稿件 / 评审目录（6 个 → `docs/archive_pre202609/`）

| # | 原路径 | 新路径 | 文件数 | 字节 |
|---|---|---|---:|---:|
| 6 | `docs/manuscript_revision_20260905/` | `docs/archive_pre202609/manuscript_revision_20260905/` | 4 | 116 514 |
| 7 | `docs/manuscript_review_20260906/` | `docs/archive_pre202609/manuscript_review_20260906/` | 5 | 122 186 |
| 8 | `docs/manuscript_round2_20260906/` | `docs/archive_pre202609/manuscript_round2_20260906/` | 5 | 3 452 085 |
| 9 | `docs/manuscript_updated_20260919/` | `docs/archive_pre202609/manuscript_updated_20260919/` | 3 | 85 638 |
| 10 | `docs/project_review_20260910/` | `docs/archive_pre202609/project_review_20260910/` | 3 | 46 301 |
| 11 | `docs/requirements_notes_20260905/` | `docs/archive_pre202609/requirements_notes_20260905/` | 1 | 36 995 |

合计：**52 个文件 / 50 587 997 B（≈48.24 MiB）**；`git status` 显示 **52 条 `R`（rename）、0 条 `D`**。
移动前后逐目录文件数与字节数**完全一致**（§4.3 给复测）。

---

## 3. 引用更新清单

### 3.1 已更新（5 个当前状态/导航/现役目录内的文档）

| 文件:行 | 内容 |
|---|---|
| `docs/README.md`（新增"目录归并指针"；§1.4、§2、§3 共 5 行） | 把 `figures_*`/`main_figure_redraw_20260910/`/`manuscript_*`/`project_review_20260910/`/`requirements_notes_20260905/` 的相对链接改到 `archive_pre202609(…/figures/)` 新路径 |
| `docs/archive_pre202609/README_ARCHIVE.md`（第 49 行 + 新增"## 归档清单（2026-09-23）"四/五/六节） | 更新图件包比对路径；登记本轮 11 个归档目录与未移动项 |
| `docs/specs/remaining_experiments_full_closure_plan_20260915.md:94` | `docs/project_review_20260910/repro_audit.md` → `docs/archive_pre202609/project_review_20260910/repro_audit.md` |
| `docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md:211` | `docs/requirements_notes_20260905/…` → `docs/archive_pre202609/requirements_notes_20260905/…` |
| `docs/manuscript_polished_20260919/需求核对与创新性精修说明.md:56,57,59` | `manuscript_revision_20260905`、`manuscript_updated_20260919` → 归档新路径 |
| `docs/PROJECT_CLEANUP_AUDIT_20260922.md`（顶部，只加指针，不改原文） | 指向本文件 |

### 3.2 旧路径残留（`git grep` 仍命中）—— 逐类例外与理由

`git grep -c -E "docs/figures_contour_notation_20260911|docs/figures_expanded_20260910|docs/figures_redraw_20260910|docs/figures_revision_20260905|docs/main_figure_redraw_20260910|docs/manuscript_revision_20260905|docs/manuscript_review_20260906|docs/manuscript_round2_20260906|docs/manuscript_updated_20260919|docs/project_review_20260910|docs/requirements_notes_20260905"` 结果：

| 类别 | 文件（命中数） | 例外理由 |
|---|---|---|
| ① 本报告与上一轮审计（**历史审计类**） | `docs/PROJECT_CLEANUP_AUDIT_20260922.md`(12)、`docs/SCI_STRING_AUDIT_20260922.md`(8) | 审计报告的**原始记录**，改写会破坏其"记录当时事实"的语义（任务允许历史审计类保留） |
| ② 历史交接/计划/复核文档（**日期快照**） | `AI_HANDOFF_VALIDATION_AND_INNOVATION_20260911_CN.md`(3)、`FIXED_FUSION_MECHANISM_NOVELTY_ADDENDUM_20260912_CN.md`(1)、`PAPER_OUTLINE_REVIEW_20260914_CN.md`(1)、`PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md`(12)、`RESEARCH_DIRECTION_RECOMMENDATION_REVIEW_20260912_CN.md`(1)、`REMEDIATION_PLAN_20260920.md`(2)、`ISSUE_REGISTER_20260920.md`(3) | 均为各自**轮次**的历史记录，写法本身是"当时路径" |
| ③ 归档区**内部互引** | `archive_pre202609/README_ARCHIVE.md`(11，含新表刻意保留的"原路径")、`archive_pre202609/{figures/figures_revision_20260905/…md(1), manuscript_review_20260906/01_…(3)/02_…(1), manuscript_revision_20260905/00_…(5), project_review_20260910/{innovation_audit.md(3),paper_audit.md(6)}}` | 已随目录一并归档；其自述的历史路径按"归档原样保留"，不改正文 |
| ④ 未在任务清单内、仍在原位的 `docs/requirements_notes_20260912/**`(7) | 3 个 `.md` | 任务未要求移动/改写；属 2026-09-12 历史需求记录 |
| ⑤ **红线区** `experiments/**`(17) | `confirmation_ksdd2_20260918/F_SPEC.json`、`validation_handoff_20260911/E{0,6,8}/*` | **硬约束禁止改动 `experiments/**`**，只能保留 |
| ⑥ 行内**裸目录名**（无 `docs/` 前缀，如 `FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md` 提到 `figures_expanded_20260910`） | 未逐一统计 | 同 ②，历史说明性提及 |

> 结论：**现役链、`docs/README.md`、`archive_pre202609/README_ARCHIVE.md` 主表、`docs/specs/`、
> 现役 `manuscript_polished_20260919/` 内的引用均已更新**；剩余命中全部落在"历史记录类 + 归档内部 + 红线区"，
> 正是任务允许的例外，且**不存在被现役流程按路径读取的悬空引用**。

---

## 4. 复验

### 4.1 目录结构

| 检查项 | 结果 |
|---|---|
| `docs/` 顶层**图件文件夹** | 只剩现役 `figures_reference_matching_20260914/`（125 文件）；其余 5 个历史图件目录已在 `docs/archive_pre202609/figures/` |
| `docs/archive_pre202609/figures/` | 含 `figures_contour_notation_20260911/`、`figures_expanded_20260910/`、`figures_redraw_20260910/`、`figures_revision_20260905/`、`main_figure_redraw_20260910/` |
| `docs/archive_pre202609/` | 新增 6 个历史稿件/评审目录（与既有 `figures_package_20260917/`、旧文档并列） |
| 移动的 52 个文件 | 文件数/字节逐目录与移动前一致（如 `figures_contour_notation_20260911` 7 files / 15 009 382 B；`requirements_notes_20260905` 1 file / 36 995 B） |

### 4.2 现役图件与入稿件哈希不变

| 文件 | SHA-256 |
|---|---|
| `docs/figures_reference_matching_20260914/fig1_framework.png` | `579A41B82638F7A40068344A2578EC77C6CE167E90D1F326348D562785E9062E` |
| `docs/figures_reference_matching_20260914/fig2_matching.png` | `12AB28217910D2C1DCED1D5A33E4890D834DDAEE1033478DCF203037B2736B61` |
| `docs/figures_reference_matching_20260914/fig8_resources.png` | `9B67794A1C26F13D99C0B73F9F9B5DAB34F4F07E9516E1D54CA90F57E762E0C5` |
| `docs/figures_reference_matching_20260914/figS1_encoders.png` | `4447AF3DAF6635B02BD4C131F92F30DD8F96D7976A11E3C0AF4B26A2FC4C9D5F` |
| 版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` | `9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837`（**未变**） |

> 三个冻结哈希与 `data/splits/*`（本轮前后一致）：
> 冻结表 `experiments/…/05_baselines_multi_dataset/baseline_common_region.csv` = `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` ✓；
> 扩展表 `…/05_baselines_ext_20260921/baseline_common_region_ext.csv` = `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B` ✓；
> 母本 = `9DB99E60…8FB837` ✓；`git status --porcelain -- experiments data` = **空**（含 `data/splits`）。

### 4.3 门禁（`.venv-anomalyclip`，Windows，无 GPU）

| 检查 | 命令 | 结果 |
|---|---|---|
| 单元测试 | `python -m pytest tests -q` | **260 passed**, 1 warning（SciPy/NumPy 版本提示），106 s |
| 版式 QA | `python scripts/figures_reference_matching_20260914/qa_layout.py` | **TOTAL PROBLEMS: 0** |
| 字体门禁自检 | `python scripts/figures_reference_matching_20260914/figure_font_gate.py --self-test` | **self-test passed: 4 controls behaved as required** |

> **未重建 docx / deck**：本轮只移动历史目录，不触碰任何现役输入/产物，故无必要重建。

---

## 5. 可逆性说明

全部移动均为 `git mv`（保留历史、无内容改动）。反向还原只需把 §2 的 `原路径 ← 新路径` 对调即可，例如：

```powershell
git mv docs/archive_pre202609/figures/figures_contour_notation_20260911 docs/figures_contour_notation_20260911
git mv docs/archive_pre202609/manuscript_review_20260906 docs/manuscript_review_20260906
# 其余 9 条同理（§2 表逐行对调）
```

因未 `git add` / `git commit`，还原也可直接 `git restore --staged --worktree` 相关路径，或对未提交的重命名执行反向 `git mv`。
§3.1 的 5 处引用更新需一并对调回旧路径（仅 `docs/README.md`、`archive_pre202609/README_ARCHIVE.md`、
`docs/specs/…20260915.md:94`、`REVIEW_CHECKLIST…20260923.md:211`、`manuscript_polished_20260919/需求核对与创新性精修说明.md`）。

---

## 6. 未移动项及理由（尤其"被现役流程读取"）

| 目录 | 为何未移动（证据 `file:line`） |
|---|---|
| `docs/manuscript_polished_20260919/` | **被现役构建链读取**：`scripts/paper_complete_review_20260920/build.py:15`（`REF=…/Reference_Matching_English_Polished_20260919.docx`）、`validate_revision23.py:16`（SHA 断言 `9DB99E60…`）；且 `.gitignore:83` 有反忽略规则 `!docs/manuscript_polished_20260919/*.docx`，移动会使母本重新变成被忽略文件。母本为**不可由源重建的二进制输入**，属冻结红线 |
| `docs/manuscript_reference_matching_20260914/` | **被脚本读写**：`scripts/manuscript_build_20260914/build.py:50`（默认 `out_dir`）、`build_cn_docx.py:28,56`、`figures.json`（13 处图路径）、`scripts/figures_reference_matching_20260914/sync_to_manuscript.py:32`（写入目标）、`scripts/limitation_closure_20260915/night2_validate_20260918.py:43`。与上一轮审计 §E.5 U1 的"红线：脚本读写路径"裁定一致 |
| `docs/manuscript_english_polished_20260906/` | **被脚本按路径读取**：`scripts/manuscript_build_20260914/build.py:53`、`build_cn_docx.py:61`、`scripts/validation_handoff_20260911/finalize_e8.py:27` |
| `docs/manuscript_chinese_review_20260907/` | **被脚本按路径读取**：`scripts/validation_handoff_20260911/finalize_e8.py:29` |
| `docs/paper_writing_preparation_20260830/` | **被脚本/配置读取**：`scripts/build_manuscript_figure_package.py:34`（`PREP = ROOT/"docs"/"paper_writing_preparation_20260830"`）、`configs/innovation_v5_casf/gate_probe.json:4`、`configs/innovation_v6_dgsafe/wave0_protocol.json:4`（`task_book`）、`src/industrial_ad/innovation_v4_diagnostics/__init__.py:3` |
| `docs/requirements_notes_20260912/`、`docs/submission_reproducibility_20260826/` | 不在任务给定的历史清单内（前者被 `docs/README.md` 与 `REVIEW_CHECKLIST…` 引用为需求原始材料；后者含 `VERSIONED_EVIDENCE.sha256` 逐条登记其它文档的 SHA+路径），**保守未动** |
| `docs/figures_reference_matching_20260914/`、`docs/main_figure_revision_20260920/`、`docs/paper_complete_review_20260920/`、`docs/introduction_research_20260825/`、`docs/specs/`、`docs/archive_pre202609/` | 任务明列的现役目录，原位不动 |

> 另：`docs/` 顶层还留有 1 个 **0 文件的空遗留目录**（名称含非中性词），不在任务清单内、无内容可归档，本轮**未处理**。

---

## 7. 观察与风险

1. **工作区存在并行改动**：本轮执行期间，`git status` 出现若干**非本任务产生**的 `M` 文件
   （`README.md`（仓库根）、`docs/ARTIFACT_INDEX.md`、`docs/HANDOVER_20260919.md`、
   `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md`、`docs/REMEDIATION_PLAN_20260920.md`、
   `docs/论文与图件问题汇总_仅复核_20260921.md`）与新增 `?? scripts/innovation_breadth_20260908/probe_breadth12.py`。
   这些在会话开始时**不存在**，判断为**并行流程**所为，本任务**未触碰**它们。
2. **现役 docx 哈希变化非本轮所致**：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`
   当前 SHA-256 = `DDB6602E…`（上一轮审计记为 `F3CAE3B4…`），系 2026-09-23 其它流程重建的结果，与本轮移动无关（本轮未动该目录）。
3. **`.gitignore` 反忽略规则**：`!docs/manuscript_polished_20260919/*.docx` 依赖该固定路径，故该目录**不得**随意移动（已在 §6 说明）。
4. **旧路径批量改写**：若后续希望把 §3.2 的"历史记录类"引用也清零，需要一次专门的"历史引用批量改写"（会改到历史正文，需作者同意），不在本轮范围。

---

## 8. 交付摘要（供提交参考；**本轮未提交**）

`git status --porcelain` 中与本任务相关者：
- **52 条 `R`**（§2 全部 `git mv`）
- **`M`**：`docs/README.md`、`docs/archive_pre202609/README_ARCHIVE.md`、
  `docs/specs/remaining_experiments_full_closure_plan_20260915.md`、
  `docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`、
  `docs/manuscript_polished_20260919/需求核对与创新性精修说明.md`
- **新增 `??`**：`docs/FOLDER_CONSOLIDATION_20260923.md`（本文件）

建议提交信息：`archive the pre-2026-09 figure and manuscript folders under docs/archive_pre202609`。
