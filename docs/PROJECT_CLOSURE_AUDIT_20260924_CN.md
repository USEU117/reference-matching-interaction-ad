# 项目收口清单（Project Closure Audit）— 2026-09-24（2026-09-25 盘上实读刷新）

- **性质**：把本项目**所有仍开放的事项**逐条清点、归类、给出归属与理由的**唯一"有无遗漏"验收依据**。
- **来源（逐份读完，不遗漏）**：
  `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md`（含 §十一/§十二/§十三收口映射）、
  `docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`、
  `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md`（A01–A23）、
  `docs/PAPER_REVISION_EXECUTION_20260924_CN.md`（M1–M6 + §八 + §十三）、
  `docs/PREREGISTRATION_20260924_CN.md`、
  `docs/ISSUE_REGISTER_20260920.md`（R-01–R-21）、
  `docs/FINAL_REPAIR_AND_ACCEPTANCE_20260923.md`、
  `docs/GITHUB_COMPLIANCE_AUDIT_20260923.md`、
  `docs/FOLDER_CONSOLIDATION_20260923.md`、
  `docs/PAPER_REVISION_HANDOVER_20260924_CN.md`（M1–M6）、
  `docs/REMAINING_REVIEW_AFTER_AI_20260923.md`（1–5 项）；
  另**增读**盘上最新一份 `docs/PRE_SUBMISSION_REVIEW_20260925_CN.md`（2026-09-25，事实上的最新一轮记录）。
- **编号口径**：总表以 `MASTER_TODO` 的 **A-/B-/C-/D-/E-** 为**主编号**（该表自称"唯一交接入口"）；括号内给出其他体系的别名（`EXPERIMENT_GAP` 的 A01–A23、`ISSUE_REGISTER` 的 R-xx、清单 §1/§2/§4 的 A-/M-/K-、`PAPER_REVISION_*` 的 Mx、Txx/Pxx/Fxx）。
- **证据规则**：每条结论给 `文件:行` / 实测值 / 哈希 / 命令输出；凡文档间状态冲突，一律**统一为 2026-09-25 盘上实读**（见 §三）。
- **边界**：本文件**不改任何判据/口径/最终产物名**，**不覆盖归档产物**，**不动 `experiments/**` 他人产物**，**未 git add/commit/push**，**未实现 GPU port**。
- **新增文本禁用词自查**：本文件新增文本**不含**身份与称谓类禁用词（引用其他轮次记录时一律称"**外部评审（指导方）**"）。

---

## 〇、结论速览（一页看完）

| 归类 | 条数 | 含义 |
|---|---:|---|
| **已完成（有凭据）** | **16 组 / 覆盖 43 项验收** | 见 §二.1（C13 = A08；**2026-09-26 新增 C14 = A11**；A22 / A04 见 §九） |
| **需作者决定** | **18** | 见 §一、§二.2（其中 #5 = A04 的 4 项**待追认设计决定**、#6 = A22 的 1 项**待追认前提变更**；A11 无新增待追认项） |
| **需新写脚本 / 新实验** | **2**（A06 / E-08） | 见 §二.3（**2026-09-26 刷新**：A04 / A11 / A22 已移出） |
| **已作废 / 不补** | **13 组** | 见 §二.4 |
| **仍无法核实** | **6** | 见 §二.5 |
| **与本轮并行流程相关（进行中）** | **1** | 2026-09-25 命名修订轮，见 §二.6 |

> **一句话**：项目当前**无阻断项**（三个冻结哈希与 `data/splits/*` 实测未变，见 §二.1 C7）；真正开放的是 **(a) 作者只能自己提供的信息（元数据/DOI/权重许可/若干拍板，含 A22 / A04 的待追认设计决定）**、**(b) 复现包重打与若干发布策略**、**(c) 唯一尚未执行的新实验 = A06（附录为全部方法补轮廓，仅在作者要求时做）**。原"超 2 h 的新计算"四项 **A04 / A08 / A11 / A22 均已执行完毕**（A08 见 §二.1 C13 与 §五；**A11 见 §二.1 C14 与 §十**；A22 / A04 见 §九）。上述之外的历史欠缺项**要么已在稿、要么已作废**。

---

## 一、开放事项总表（**本轮之后仍开放的全部事项**）

> 只列**仍未闭环**者；已完成项见 §二.1，不再重复。

| # | 编号（别名） | 事项（一句话） | 归属 | 依据（文件:行 / 实测） | 下一步 |
|---|---|---|---|---|---|
| 1 | **E-01…E-04**（R-16、§七A） | 作者元数据（作者/单位/通讯/ORCID/资助）与 COI/伦理是否保留现句 | **作者** | `PRE_SUBMISSION_REVIEW_20260925_CN.md:23`（已确认作者 Yuening Li、单位 Hefei University of Technology；学院/详细地址/邮编未给，不代填）；`FINAL_REPAIR…§五`（4 个占位仍在） | 作者补 4 处占位后我方可重建 |
| 2 | **E-05**（R-16/R-17、P3-5/P3-6） | 归档 DOI（Zenodo/等效）取得并回填；审稿阶段是否公开代码 | **作者** | `SUBMISSION_METADATA.md`「归档 DOI 获取步骤（作者执行）」已备；稿件仍如实写 "a permanent archive DOI … has not yet been established" | 作者按步骤取 DOI → 8 条回填点 |
| 3 | **A-21 / B-06 / C-02**（T09） | 命名：单字母/短代码 → **完整模型名或描述性配置名** | **已完成决策，交付件待重建**（进行中，见 §二.6） | 盘上实读：`scripts/paper_complete_review_20260920/figure_sources/display_labels.py`（**未跟踪**，1,830 B，映射 `A1→Dual-encoder baseline` 等）；`English_Manuscript_Source.md` 含新名 **5 处**；**但**现役 docx 内 `Dual-encoder baseline` = **0**、`Equal-weight replacement` = 1（属旧"温和版"） | 由进行中的命名轮重建 docx/deck 后复核 |
| 4 | **E-08**（R-01/R-02/R-04/R-13/R-14/R-15、M2、P1-1…P1-7） | 复现包重打：补 `src/`+`configs/`+`methods/`、`requirements_repro.txt` 补 CUDA index、`SOURCE_COMMIT.txt`+`SHA256SUMS`、`paper_evidence_closeout` 台账、`seeds_extension/p0_support/`、回填 `VD1_MANIFEST.json` | **作者 + 我方** | `EXPERIMENT_GAP…§二 A13`；`ISSUE_REGISTER…R-01/02/04/13/14/15`；**权重再分发许可**未定（`docs/MODEL_WEIGHTS.md` 已声明本包不分发权重） | ① 作者定 `methods/` 方案 (a)/(b) 与权重许可；② 我方按方案补包 |
| 5 | **D-01 / A04**（T03、PREREG §2.1） | 跨方法稳定性 —— **已执行（2026-09-25，见 §九.2）**；仍开放的是**待作者追认的 4 项设计决定**（纵横轴定义、原生帧实现、区间网格、样本范围） | **作者** | `PREREGISTRATION_20260924_CN.md §八`；产物 `experiments/prereg_20260924/out/A04/` 五件；`A04_STATUS.json → design_decisions_pending_ratification` | 追认后作正式读数（追认前只作补充） |
| 6 | **A-22 / D-11 / gap A22**（PREREG §2.4/§4.2） | 统一几何子集内让 PatchCore 保留**两配置列** —— **已执行（2026-09-25，见 §九.1）**；仍开放的是**待作者追认的 1 项前提变更** | **作者** | `PREREGISTRATION…§七`；产物 `experiments/prereg_20260924/out/A22/` 六件；`A22_STATUS.json → premise_change_pending_ratification` | 追认前两新列只作补充读数，不得并入统一几何子表正文 |
| 7 | **D-14 / A-17**（METHOD_COMPARISON_HANDOFF） | 表 A / 表 B（统一 448 子集）是否入正文；入稿须带 7 条限制 | **作者** | `MASTER_TODO…D-14`；`EXPERIMENT_GAP…§7.3`（子集已就绪、未入稿） | 作者拍板 |
| 8 | **D-13**（T08） | 文献参照表是否纳入 | **作者**（可选、零重跑） | `MASTER_TODO…D-13`；`EXPERIMENT_GAP…§11.4 证据缺口-4`：`references.json` **无** `adaptclip/remp_ad/efficientad/glass` 键 ⇒ 该表**尚未做** | 作者拍板；若做须补 4 个引用键 |
| 9 | **D-08** | 子集表 `pixel_auroc` 区间是否补 | **作者**（低成本可补） | `EXPERIMENT_GAP…§7.2 A19`：现仅 `pixel_ap` 有区间；CPU 级 | 作者要求则复用同一 stride-8 抽样流 |
| 10 | **E-09**（F21） | `build.py` 非字节可复现是否接受 | **作者** | `MASTER_TODO…E-09`：连跑三次 docx SHA 三个值、内容度量一致 | 接受→只记内容口径；不接受→改固定 docProps |
| 11 | **E-10**（F22、R-？） | `selfcheck.py` 2/69 两项如何处置 | **作者** | `FINAL_REPAIR…§8.4`：实跑 `checks=69, passed=67`；失败 = ①大纲 docx 不在盘 ②冻结快照 `_smoke` 3 处漂移 | 作者定"重建大纲 / 豁免 `_smoke`" |
| 12 | **E-19 / E-20 / E-21 / E-22 / E-23** | 版式母本移出 `*.docx` 忽略；现役 docx 留 git 还是 Release；是否 LFS；是否出 PDF；是否打 `v1.0.0` | **作者** | 盘上实读：`.gitignore:83` 白名单**仍指向 `…20260923.docx`**，而**现役交付是 `…20260924.docx`**（`git ls-files` 显示两者均被跟踪、SHA `77864633…`）；`git check-attr filter` = **unspecified（未启用 LFS）**；`git tag` = **10** | 作者逐项拍板 |
| 13 | **E-16 / E-24 / B-08 / E-12** | `experiments/**` 与日志内本机绝对路径是否脱敏；生成物溯源 JSON 旧路径；`PREFLIGHT.json`/`ext_run_anomalyclip.py` 的 09-21 留痕 | **作者**（红线区） | `GITHUB_COMPLIANCE…§4#5`：`git grep "My_github"` 命中 **1,503** tracked 文件；改动会使 `SHA256SUMS`/`VERSIONED_EVIDENCE.sha256` 失效 | 作者书面决定是否单开一轮 |
| 14 | **E-18** | 清理第二轮改动是否提交；`.trae/` 是否纳入 | **作者** | 盘上实读：`git status` **R=0**（归档已落地并提交）；当前未提交 = **70 M / 35 ??**（见 §三 冲突 12） | 作者定提交范围 |
| 15 | **E-06**（P3-6） | 数据集许可明细是否补入正文 | **作者** | `MASTER_TODO…E-06`：三段许可已入正文；明细待定 | 作者拍板 |
| 16 | （§七2#18 / R-07） | BTAD 口径科研判断追认（已在稿） | **作者** | `ISSUE_REGISTER…R-07`：措辞已统一为"点估计接近零、区间跨零，方向未定"；"是否接受该定位"归作者 | 作者追认 |
| 17 | （§七2#20 / B-09） | 三处重复图件集"留哪一处" | **作者**（低） | `FOLDER_CONSOLIDATION_20260923.md`：现役链只认 `docs/figures_reference_matching_20260914/`；历史图件已归档 | 作者拍板是否再删 |
| 18 | **E-11** | 包内 `SHA256SUMS` 2 处既有漂移是否修 | **作者**（低） | `MASTER_TODO…E-11`：`VD1_MANIFEST.json`、`requirements_lock.txt` | 作者拍板 |
| 19 | （GITHUB_COMPLIANCE §4#6） | 未跟踪并行产物 `docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md` 的 **2 处非中性称谓**是否中性化后入库 | **作者** | 盘上实读：该文件 `git ls-files` = **未跟踪**；`GITHUB_COMPLIANCE…§3.5` 记其含 2 处非中性词（非本轮引入） | 入库前处理 |
| 20 | （§2.6 见下） | 2026-09-25 命名修订轮的**完成度与验收**（重建 docx/deck、门禁复跑、索引同步） | **并行流程**（本轮不介入） | `PRE_SUBMISSION_REVIEW_20260925_CN.md`；盘上 `codex-runtimes` 进程正在渲染 `fig7_multimethod_mvtec` | 由该轮自行收口，我方只读登记 |

> **本表刷新（2026-09-25）**：原 #8「A08（full-pixel 区间）」已**完成**，移出本表、登记于 §二.1 **C13**；其后各行编号顺移一位（原 #9–#22 → 现 #8–#21）。本表仍只列**未闭环**事项。
>
> **本表刷新（2026-09-26）**：原 #6「D-05 / A11」已**完成**，移出本表、登记于 §二.1 **C14**；其后各行编号再顺移一位（原 #7–#21 → 现 #6–#20）。同时把原 #5（D-01 / A04）与原 #7（A-22 / D-11）由"**是否执行**"改写为"**已执行；仍开放的是待作者追认的设计决定**"（依据 §九.1 / §九.2，该节 2026-09-25 已记三项均已执行）。本表仍只列**未闭环**事项。

---

## 二、分类明细

### 二.1 已完成（给凭据，防重复劳动）

| # | 已闭环项 | 凭据（文件:行 / 实测值 / 哈希） |
|---|---|---|
| C1 | **清单全量验收通过**：§1 A-01…A-28 = **28/0/0/0**，§4 K-01…K-15 = **15/0/0/0**（合计 **43 通过**） | `FINAL_REPAIR_AND_ACCEPTANCE_20260923.md §10.5`；`REVIEW_CHECKLIST…§7 第三轮增补` |
| C2 | **M1–M6 全部处置**（表注指向 Table S2 + SubspaceAD 点名；复现性文档；Figure 7 续页 +BTAD；S5 离群；Discussion 点名 HyperFSAD/ReMem/DuoAD；A01 回填） | `PAPER_REVISION_EXECUTION_20260924_CN.md §一/§二`；本轮实测 `results.md` 含 `30.527`×1、`covers MPDD and BTAD only`×1、`HyperFSAD|ReMem|DuoAD`×1；`manuscript.md` 含 `preparation computation`×1 |
| C3 | **A-01 / A-12 / A-19 / B-04 / B-05 / B-07 / B-09 / B-10** 已执行或复核为"无需改" | `MASTER_TODO…§13.1/§13.4`；`PAPER_REVISION_EXECUTION…§13.1/§13.4`（fig2 `F60EBC88…`、fig3 `F44656C4…`；S1 逐字节未变 `FE182E11…`） |
| C4 | **现役重建（2026-09-24）**：docx = **56 页 / 23 表 / 28 内嵌图 / 154 数学对象 / 12 编号公式 / 37 文献 / 19,947 词**；deck = **64 页** | 本轮实测：`Reference_Matching_Complete_English_20260924.docx` SHA-256 = **`77864633FD7672660243017B0A13C6F9A6860B519B99A1255B4A65205E2839F6`**，python-docx `tables=23 / inline=28`；`All_Figures_Complete_20260924.pptx` SHA-256 = **`CF889CACF7CE868DBC76AC05B0986D1E62F0A884113CCFC3F09F681EC8F9E137`**；`FIGURE_SLIDE_INDEX.json` = **64 条** |
| C5 | **B-03 / A23 图 S6 已入稿** | 本轮实测 docx 内 `Figure S6` 命中 **4**；`SOTA` = **0**；`all cases` = **0**（A-15 口径成立） |
| C6 | **E-07 复现性文档已在盘且达标**（原登记"过期/误记"） | 本轮实测 `Test-Path docs/MODEL_WEIGHTS.md` = **True**（159 行、19 处 SHA-256 提及）、`docs/REPRODUCE_TO_TABLES.md` = **True**；`FINAL_REPAIR…§10.6#4` 已更正；`REMAINING_REVIEW…§3` 同结论 |
| C7 | **红线未破（实测复核）** | 冻结共同区域表 = **`3C83AB00…A0B8BB`** ✓；扩展表 = **`1C770129…73EC4B`** ✓；版式母本 = **`9DB99E60…8FB837`** ✓（三者本轮实算一致） |
| C8 | **发布合规三件套已入库** | 盘上实读：`CITATION.cff`、`THIRD_PARTY_NOTICES.md`、`.gitattributes` **均已在跟踪**（不在 `git status` 的 `??` 列表中）；`GITHUB_COMPLIANCE_AUDIT_20260923.md §2.3/§2.4` |
| C9 | **E-14（本地未推送提交）已不再成立** | 本轮实测 `git status -sb` = **`## main...origin/main`**（**无 `[ahead N]`**，已同步）；`MASTER_TODO…E-14` 记的 "ahead 2" 为旧值 |
| C10 | **目录归并已落地并提交** | 盘上实读：`git status` **R=0**；`docs/archive_pre202609/figures/` 与 6 个历史稿件/评审目录已就位（`FOLDER_CONSOLIDATION_20260923.md §2` 的 52 条 `git mv` 已进入历史） |
| C11 | **ISSUE_REGISTER 的复现/测试/措辞类大多已处置** | `ISSUE_REGISTER…§〇bis/§〇ter`：R-05/R-06/R-07(措辞)/R-08/R-09/R-10 已处置；R-11(推送)/R-12 已解决；R-20 口径刷新为 5 家族 |
| C12 | **FOLDER_CONSOLIDATION 的引用更新与例外登记** | `FOLDER_CONSOLIDATION…§3.1/§3.2`：现役链与导航文档引用已更新；剩余命中全在"历史记录类 + 归档内部 + 红线区 `experiments/**`"（允许例外） |
| **C13** | **A08 full-pixel（stride-1）区间 —— 本轮已完成（原判"不补"）** | 产物 `experiments/prereg_20260924/out/A08/`：`point_stride1.csv`（56,941 B，SHA-256 `9A7F6F1846BCB9BE…`）、`replicate_stride1.npz`（1,963,505 B，`C96AFF40F09FAF8B…`）、`interaction_by_grid.csv`（2,271 B，`0DBFD0283D744350…`）、`E1_STATUS_stride1.json`（759 B）、`E1_REPORT_SUMMARY.json`（92 B）。**规模**：20/20 单元、96/96 类别实例；6 shard 并行，实测加速 **4.79×**（makespan 6502 s vs 串行估 31136 s，`state/A08_parallel_progress.json` 末行 `rate=4.7886`）；收尾 N=1 **纯汇总 6.1 s**（20/20 skipped，只跳不重算），终产物落盘 mtime 2026-09-25 16:28。**结构**：`point_stride1.csv` = 1 表头 + **1248 行**（12×6×13 + 8×3×13），0 空/NaN、0 重复键。**结论核对**：MPDD `I_TRI` = +0.007853 / +0.007741 / +0.007624、`I_BAL` = +0.006074 / +0.006172 / +0.006154（stride **1/4/8 三点均排除零**）；BTAD `I_TRI` = −0.000169、`I_BAL` = −0.000864（98.75% **均跨零**，与既有定位一致）。**如实记录**：BTAD 无归档可比对象（归档 `E1_fullpixel_ci/` 只有 MPDD stride-4/8）；`E_BAL_J`（MPDD）在 stride **1/4 排除零、stride 8 跨零**（网格敏感性，未平滑）。详见 `PREREGISTRATION_20260924_CN.md §五`。 |
| **C14** | **A11 共享操作多条件消融 —— 2026-09-26 已完成（原判"不可运行 / 需新写脚本"）** | 产物 `experiments/prereg_20260924/out/A11/`：`ablation_metrics_multi.csv`（116,666 B，SHA-256 `F96C998046FCDFD32977E8F8831AD20794E8907CB702554242C78E6938CDEC01`）、`replicate_multi.npz`（3,873,040 B，`7FC433A2E6FE79AACFD3816F086709F9C46FDB425B6F68FD02BD69D36ADC168A`）、`interaction_by_ablation_condition.csv`（15,450 B，`AF38B29A242928AFA7B74422F8F1CD88B39EB7B311E10AB7FF3CB0FCFD851CBD`）、`A11_multi_vs_single_condition.csv`（3,298 B，`2527D1AD7FBDF1D05B84EFF2DCAF74668155E06851718B72CF8DEF982880C3CB`）、`A11_STATUS.json`（1,054 B）；单元检查点 **16 件**。**规模**：4 变体 × seed 0、1 × K 1、2、4、8 × 2 数据集 = **2,304 点单元格 / 128 条件行 / 16 汇总行**；2 路 shard **并行 20,995 s（≈5.83 h，纯 CPU，显存 0 MiB）**，收尾 `assemble` 约 17 s。**结构**：三张 CSV **0 空 / 0 NaN / 0 重复键**；`replicate_multi.npz` = 512 条长度 1,000 的宏平均数组。**结论（探索性）**：MPDD **8/8 行**区间排除零且与单条件同号；BTAD **8/8 行**区间**全部跨零**（方向未定，**不得**读作"零效应"），其中 4 行反号，但 `baseline`（**未消融**参考）在 BTAD `I_TRI` 上同样反号 ⇒ **反号不能单归于消融**。**账目**：128 个条件行里区间排除零 **70** 个，其中 9 个符号与单条件参照相反（**全部在 BTAD**）。**装配缺陷已登记并订正**：首轮 `assemble` 产出空派生表（`0 condition rows; 0 aggregate rows`），原因为 ① `INTERACTIONS` 用带 `_L`/`_J` 后缀的构造名与点表 `construction` 列不匹配、② `_archived_single_condition()` 逐行覆盖只留最后一个类别；订正后 `ablation_metrics_multi.csv` / `replicate_multi.npz` / `A11_STATUS.json` **逐字节未变**（SHA-256 与首轮清单相同），**未重跑任何单元**、**未写 `E2_shared_op_ablation/`**（变更 0 项）。详见 `PREREGISTRATION_20260924_CN.md §九` 与本文件 **§十**。 |

### 二.2 需作者决定

即 §一 的 **#1–#6、#7–#15、#17–#19**（编号已按 2026-09-26 刷新顺移；共 **18** 条，与原口径一致）。其中**具体决策点**明确列出：

- **作者元数据**：`[[AUTHORS]]`（已确认 Yuening Li / 李越宁）、`[[AFFILIATIONS]]`（Hefei University of Technology / 合肥工业大学；**学院、详细地址、邮编未提供**）、`[[CORRESPONDING_AUTHOR]]`、`[[FUNDING]]`、COI 与伦理句 —— **禁止代填**。
- **归档 DOI**：作者执行步骤已备（GitHub Release → Zenodo 集成 → 取 DOI → 8 条回填点）。
- **整批改名 A-21/B-06/C-02**：外部意见已提出、**已在源与图表层执行**（见 §二.6），交付件待重建。
- **权重再分发许可**：决定复现包**是否打包权重本体**（否则只写 URL+revision+SHA-256）。
- **deck 64 vs 63 页**：现役 `…20260924.pptx` = **64 页**（`CF889CAC…`）；`…20260923.pptx` = 63 页；`MASTER_TODO §三` 仍写 63 ⇒ 需以 64 为现役并同步 §三/§八。
- **A04 的共同指标定义**：需先定"纵轴（共同指标）× 横轴（共同扰动）"，否则无从执行。→ **2026-09-25 已由执行轮选定 4 项设计决定**（见 §九.2），现为**待作者追认**，不再阻塞执行。
- **A11 / A22 是否新写脚本**：原判现成脚本均**不可运行**（硬编码 seed0 / 会覆盖既有产物 / 假定短边 448）。→ **已各自新写脚本并执行完毕**：A22 见 §九.1（另有 1 项前提变更待追认）；**A11 见 §二.1 C14 与 §十**（口径按 §2.2 登记执行，**无新增待追认项**）。

### 二.3 需新写脚本 / 新实验

> **2026-09-26 刷新**：原 X1（A04）、X2（A11）、X3（A22）**均已新写脚本并执行完毕**，移出本表（A04 / A22 见 §九.2 / §九.1；**A11 见 §二.1 C14 与 §十**）。本表只剩 **2** 项。

| # | 事项 | 缺什么 | 成本估算 | 为什么现在不做 |
|---|---|---|---|---|
| X1 | **A06 附录为全部方法补轮廓** | 需按正文同规则做阈值化后处理 | 小时级 GPU/CPU | 仅在作者要求时做（正文 5 案例已满足） |
| X2 | **E-08 复现包重打** | 需补 `src/`/`configs/`/`methods/`、CUDA index、`SOURCE_COMMIT.txt`+`SHA256SUMS`、台账、`p0_support/`、`VD1_MANIFEST` 回填 | 天级文档/打包 | 卡在**权重再分发许可**（作者决策） |

### 二.4 已作废 / 不补（给理由与出处）

| # | 事项 | 理由 / 出处 |
|---|---|---|
| N1 | gap **A09**（同机证据范围受限）→ D-04 | 保留为限制、已在稿；不得改写为端到端（`EXPERIMENT_GAP…§7.1 A09`） |
| N2 | gap **A11** → D-05 | 原记**"不补（结论不变）"**（`MASTER_TODO…D-05`）。**2026-09-26 已由"不补"转为"已完成"**：另立脚本按预注册 §2.2 口径全量执行，见 **§二.1 C14 与 §十**；本条保留为历史记录 |
| N3 | gap **A12**（权重最优性）→ D-06 | 已在正文限定（`results.md:7`） |
| N4 | gap **A18**（子集只覆盖 36/144）→ D-07 | 子集定位本身即"1/4 子集"；补满只提高分辨率 |
| N5 | gap **A20**（WinCLIP+/AnomalyCLIP@448）→ D-09 | 代码级绑定（检查点 240 / 网格 518），改了就不再是"原生配置" |
| N6 | gap **A21**（SubspaceAD@448 仅 2 图冒烟）→ D-10 | 排除依据是**输入规则**（方形拉伸），非显存/成本 |
| N7 | gap **A22**（子集内 PatchCore 塌缩一列）→ D-11 | 协议敏感度已由 **图 S6** + `protocol_leverage.json`（0.1000 / 0.0265 / 3.8× / 33.3%）承担 |
| N8 | gap **A15/A16/A17** | 已满足（3–4 个近期方法口径 / 统计口径 / 共同区域口径） |
| N9 | **D-12**（P2 训练类基线 AdaptCLIP 等） | 已结案不做（外部口径 3–4 个近期方法已达标） |
| N10 | **D-13**（文献参照表） | 降级为可选、零重跑（只剩"补 4 个引用键"，见 §一#10） |
| N11 | **R-05 / R-06 / R-07(措辞) / R-08 / R-09 / R-10 / R-12** | 已处置（`ISSUE_REGISTER…§〇bis`） |
| N12 | **F16** | 编号保留、未使用（`MASTER_TODO…§九 9.2`） |
| N13 | **A-12**（稳定性计划书"加密 N 网格却使最大值变小"） | **矛盾不成立**：现役文本写的是"加密不会改变或收紧 N≥500 上界"；数据侧仅 11 点网格，`max_abs_estimate_deviation_N_ge_500 = 1.265e−04` 与表逐值一致（`PAPER_REVISION_EXECUTION…§13.4`） |

### 二.5 仍无法核实（说明已尝试的检索范围）

| # | 项 | 已尝试的范围 | 缺什么 |
|---|---|---|---|
| U1 | **M-13 文献 DOI/卷期/大小写逐条统一** | 只对 `references.json` 做**年份分布**统计（2024–2026 = 20/34 = 58.8%，低于 70–80% 参考区间，非硬指标） | 未逐条比对 34 条文献的 DOI/期刊缩写/作者大小写 |
| U2 | **A-05 位图内嵌标题（是否 100% 无图内标题）** | 核了原生页 XML 无 `Figure N` + 绘图脚本无生效 `suptitle`（机器旁证） | **未做 OCR**，无法 100% 排除整页位图内的标题像素 |
| U3 | **2026-09-25 命名修订轮的完成度与验收** | 读 `PRE_SUBMISSION_REVIEW_20260925_CN.md`；实测源/图表已含新名、交付 docx 未含 | 该轮**仍在进行**（盘上有活动渲染进程），无最终计数/门禁记录 |
| U4 | **旧版验收 JSON 是否最新** | 已按"旧版验收 JSON 与早期待办状态**不作为最新文件凭证**"口径处理（`FINAL_REPAIR…§11` 提示） | `REVISION_VALIDATION_20260923.json` 数值仍为旧时点，脚本因并行流程卡在 `no_experiment_data_changes` 未重生成 |
| U5 | **全新克隆能否复现 deck 链** | 本机可跑通（`FINAL_REPAIR…§11.7#1`） | deck 链依赖 artifact-tool + PowerPoint COM + 本机插件缓存（跨机路径未验证） |
| U6 | **`docs/requirements_notes_20260912/`、`docs/submission_reproducibility_20260826/` 是否归档** | `FOLDER_CONSOLIDATION…§6`：二者**不在该轮任务清单内**，被 `docs/README.md` 与 `REVIEW_CHECKLIST` 引用 ⇒ **保守未动** | 归档判定需作者/后续轮确认 |

### 二.6 与本轮并行流程相关（进行中，本轮只读登记）

- **2026-09-25 命名修订轮**：`PRE_SUBMISSION_REVIEW_20260925_CN.md`（未跟踪）记"本轮把阅读层名称改为完整模型名称或描述性配置名称"；盘上证据 = `scripts/…/figure_sources/display_labels.py`（未跟踪）、`scripts/…/.tmp_revision_20260925/`（未跟踪）、一批图件 `M`（`fig1_framework.png`、`figS6_protocol_paper_part*`、`multimethod/*`、`qualitative_*`）；**且本轮观察期内有 `codex-runtimes` 的 pwsh/python 正在渲染 `fig7_multimethod_mvtec`**（实测命令行，非我方进程）。
- **对我方的影响**：该轮**正在写 `docs/**` 与图件**，故本项目现役 docx/deck 可能在本轮观察期内被其重建；本清单的"交付件哈希"以**实测时点**为准。
- **我方纪律**：不介入、不覆盖、不回退其改动。

---

## 三、交叉核对：文档间状态不一致 → 统一为盘上实读

| # | 事项 | 文档 A 的说法 | 文档 B 的说法 | **盘上实读（统一口径）** |
|---|---|---|---|---|
| 1 | **A01 图像级并列**（gap A01 / MASTER A-14） | `MASTER_TODO…§4.1`：**"仍缺"** | `EXPERIMENT_GAP…§7.1`：**"部分满足（2026-09-24 回填）"**；`PAPER_REVISION_EXECUTION…§3.1`："已做（部分满足）" | **以 B 为准**：`results.md:165` 有 "Image-level metrics…Table 21"、`tables.json` 有 `image_metrics`（two anchors，无区间）⇒ **部分满足** |
| 2 | **图 S6 是否入稿**（gap A23 / B-03） | `MASTER_TODO…§4.1 A23`：**"未入稿，登记待作者"** | `MASTER_TODO…§13.1` / `PAPER_REVISION_EXECUTION…§3.3`：**"已入稿"** | **已入稿**：本轮实测 docx 内 `Figure S6` 命中 **4** |
| 3 | **S5 首轮离群**（gap A10 / A-16） | `MASTER_TODO…§4.1 A10`：**"仍缺"** | `MASTER_TODO…§12.1 M4` / `PAPER_REVISION_EXECUTION…§3.1`：**"已做"** | **已披露**：本轮实测 `results.md` 含 `30.527`×1 |
| 4 | **A-01/A-19/B-04/B-05/B-07** | `MASTER_TODO…§一/§二`：**"待做 / 待核实"** | `MASTER_TODO…§13.1`：**"已执行 / 复核为无需改 / 已过"** | **以 §13.1 为准**（fig2 `F60EBC88…`、fig3 `F44656C4…`；S1 逐字节未变） |
| 5 | **E-07 / A13 复现性文档** | `FINAL_REPAIR…§10.6#4`（旧）：**"`MODEL_WEIGHTS.md` 不在盘"** | `REMAINING_REVIEW…§3` / `FINAL_REPAIR…§11.5`：**"在盘且达标"** | **在盘且达标**：本轮实测 `Test-Path` = **True**（159 行、19 处 SHA-256） |
| 6 | **deck 页数** | `MASTER_TODO…§三/§八`：**63 页** | `MASTER_TODO…§13.2/§13.3` / `PAPER_REVISION_EXECUTION…§13.3`：**64 页** | **64 页为现役**（`…20260924.pptx`，`CF889CAC…`，索引 64 条）；`…20260923.pptx` = 63 页为上一快照 ⇒ **需同步 §三/§八** |
| 7 | **docx 规模口径** | `MASTER_TODO…§现状`：**55 页 / 27 内嵌图 / 152 对象 / 19,434 词**（20260923） | `PAPER_REVISION_EXECUTION…§13.2`：**56 / 28 / 154 / 19,947**（20260924） | **以 20260924 为准**（SHA `77864633…`，实测 23 表 / 28 图） |
| 8 | **A04 / A11 / A22 处置** | `MASTER_TODO…D-01/D-05/D-11`：**"不补（结论不变）"** | `PREREGISTRATION…§二/§4.2–4.4`：**"真需新计算、只预注册（>2 h）"** | **统一为"未跑、已预注册、待作者点头"**（不补 = 现在不跑；预注册 = 已备好跑法）。**2026-09-26 更新**：三项**均已执行完毕**——A22 见 §九.1、A04 见 §九.2、**A11 见 §二.1 C14 与 §十**；A22 / A04 另带回**待作者追认的设计决定**（§九.1 / §九.2），A11 无 |
| 9 | **A08 full-pixel** | `MASTER_TODO…D-03`：**"不补"** | `PREREGISTRATION…§2.3`："已登记脚本，>2 h 不当场跑" | **本轮已完成**（终产物落盘 2026-09-25 16:28）：20/20 单元、96/96 类别实例，6 shard 实测加速 **4.79×**；产物/结构/结论核对见 **§二.1 C13** 与 `PREREGISTRATION…§五` |
| 10 | **命名整批改名** | `MASTER_TODO…A-21/B-06/C-02` + `§七/§13`：**"待拍板（未执行，温和版在位）"** | `PRE_SUBMISSION_REVIEW_20260925_CN.md`：**"本轮把阅读层名称改为完整/描述性名称"** | **源与图表层已改、交付 docx 未改**：`manuscript.md` 有描述性名、`English_Manuscript_Source.md` 新名 5 处、`display_labels.py` 在位；docx 内 `Dual-encoder baseline` = **0** |
| 11 | **本地未推送提交**（E-14 / R-11） | `MASTER_TODO…E-14`：**"ahead 2"** | `ISSUE_REGISTER…§〇ter`：09-23 又超前 2 | **已同步**：本轮实测 `## main...origin/main`（无 ahead） |
| 12 | **清理第二轮归档是否提交**（E-18 / FOLDER_CONSOLIDATION §8） | `FOLDER_CONSOLIDATION…§8`：**"52 R 未提交"** | `GITHUB_COMPLIANCE…§3.1`：`git status` 无 `D/R` | **已提交**：本轮实测 `git status` **R=0**；未提交项 = **70 M / 35 ??**（当前为并行流程与历史轮次的累积） |
| 13 | **`plot_primary.py` 数据来源**（K-12 / N-1） | `FINAL_REPAIR…§8.1`：**"需作者裁决"** | `FINAL_REPAIR…§九` / `MASTER_TODO…§7.3`：**已按选项 (a) 结清** | **已结清**：fig4b 已按现行表 8 行重渲染（`FA2DE6E4…FCC13`），32/32 与 Table 16 一致 |

---

## 四、"本轮之后仍开放的全部事项"（汇总，去重后共 20 条）

> 与 §一 逐行对应；此处只给 **编号 + 归属**，便于验收勾选。**编号已按 2026-09-26 刷新顺移**（A11 移出；原 #7–#21 → 现 #6–#20）。

1. E-01…E-04 作者元数据/COI/伦理 —— **作者**
2. E-05 归档 DOI + 审稿期公开 —— **作者**
3. A-21/B-06/C-02 命名修订的重建与验收 —— **并行流程（进行中）**
4. E-08 复现包重打（含权重许可）—— **作者 + 我方**
5. D-01/A04 —— **已执行**；开放的是**待作者追认 4 项设计决定** —— **作者**
6. A-22/D-11 —— **已执行**；开放的是**待作者追认 1 项前提变更** —— **作者**
7. D-14/A-17 表 A/表 B 是否入稿 —— **作者**
8. D-13 文献参照表 —— **作者**
9. D-08 `pixel_auroc` 区间 —— **作者**
10. E-09 `build.py` 非字节可复现 —— **作者**
11. E-10 `selfcheck` 2/69 —— **作者**
12. E-19/E-20/E-21/E-22/E-23 版式母本 + git/Release + LFS + PDF + tag —— **作者**
13. E-16/E-24/B-08/E-12 绝对路径与留痕 —— **作者**
14. E-18 第二轮改动提交范围 —— **作者**
15. E-06 数据集许可明细 —— **作者**
16. BTAD 口径追认 —— **作者**
17. 三处重复图件集留哪一处 —— **作者**
18. E-11 包内 SHA256SUMS 漂移 —— **作者**
19. `INNOVATION_DIRECTION_LIBRARY` 非中性称谓是否中性化后入库 —— **作者**
20. 仍无法核实 6 项（U1–U6）—— **需补工具/后续轮**

> **A08（full-pixel 区间）已移出本清单**（原 #8）：2026-09-25 已完成，证据见 **§二.1 C13**。
>
> **A11（共享操作多条件消融）已移出本清单**（原 #6）：2026-09-26 已完成，证据见 **§二.1 C14 与 §十**。

---

## 五、本轮对 A08 执行与观察（原与本清单 #8 对应；**A08 已闭环，见 §二.1 C13**；详见启动/监控记录）

- **决定路数 N**：`N = clamp(floor(free_GiB), 3, 6)`；启动前实测可用内存 = **2.797 GiB** ⇒ `floor = 2` ⇒ **N = 3**（且 free < 3 GB，已按要求提示）；启动前确认**无其它 python 计算进程**。
- **启动**：`powershell -File experiments\prereg_20260924\state\A08_parallel_launch.ps1 -Shards 3 -StaggerSec 300 -Resume`（2026-09-25T10:20:01 起，错峰 300 s；shard 1/2 已起，shard 3 于 10:30:01 起）。
- **监控**：单一实例 `A08_parallel_monitor.ps1 -IntervalSec 60 -MaxMinutes 1440`（输出 `state/A08_parallel_progress.json`）。
- **观察期健康度 / 进度 / ETA**：见 `experiments/prereg_20260924/state/A08_parallel_progress.json` 与下方交付报告（N、各 PID、日志路径、units_done/20、ETA）。
- **收尾（仅当 20/20 `complete:true`）**：N=1 纯汇总 → `e1_report.py --dir … --strides 1` → 记录三产物路径/字节/SHA-256 并对 `point_stride1.csv` 做结构抽查。
- **收尾完成（2026-09-25 16:28 实读）**：本轮最终以 **6 shard**（非启动时的 3）跑完 **20/20 单元、96/96 类别实例**（`state/A08_parallel_workers.json`、`state/A08_parallel_launch.out`），makespan **6502 s**、实测加速 **4.79×**；随后单实例 N=1 纯汇总 **6.1 s**（20/20 skipped、只跳不重算）→ `e1_report.py --strides 1`。三产物路径/字节/SHA-256 与结构抽查见 **§二.1 C13**；结论核对表见 `PREREGISTRATION_20260924_CN.md §五`。**A08 已由"执行中"转为"已完成"**，本清单 §一/§四 已相应移除该项。

---

## 六、本轮未做 / 不确定

1. 本文件为**只读清点 + 文档增量**，**未跑新实验**（**A08 为本轮执行项**，已闭环，见 §五 与 §二.1 C13）、**未用 GPU 训练**、**未改任何冻结数值**、**未改判据/口径/产物名**、**未提交/推送**、**未实现 GPU port**。
2. 交付件计数（docx/deck 页表图）为**实测时点值**；若 §二.6 的并行命名轮在同一时段重建，数值可能随之刷新。
3. §三 的"统一口径"以**本文件写作时的盘上实读**为准；若后续轮次再改，需按 `FINAL_REPAIR…§11` 的"旧版验收 JSON 不作凭证"原则重新核。
4. §一 的"需作者决定"条数为**去重后**计数，与方法论文档中的分项编号不是一一映射。
5. 本轮**未复核** `experiments/**` 内与本文无关的历史工作流的失败登记。

*本文件写于 2026-09-24（标题日期），盘上实读时点为 2026-09-25；所有 `文件:行` 与哈希均可按 §一/§二 的引用复跑核验。*

---

## 七、2026-09-25 接手"命名修订轮"收尾（**只追加**；不改上文任何一字）

> 背景：并行流程"**2026-09-25 命名修订轮**"把方法名改成新标签（如 `Dual-encoder baseline`）并重建 docx，但在 **17:18:50 之后停止写盘**，遗留两件：① 未生成 `All_Figures_Complete_20260925.pptx`；② `results.md` 的两句 full-pixel 说明被 17:13 的重写覆盖。本节记录接手完成后的**盘上实读**结果。

1. **命名轮自带的交付验收 `check_delivery.py`（`.tmp_revision_20260925/check_delivery.py`）要求**：`figures.json` 与 `tables.json` 行数/数值/列宽（合计 17 cm）不变；三个冻结哈希不变；docx **23 表 / 28 内嵌图**、28 个 `figures.json` 源图与 Word 内嵌图**逐字节相同**、无未解析 `{{`/`[@`、含 `Hefei University of Technology`、Word 内无废弃配置码 `A1|DUP|TRI|BAL|E1|E2|E3`；`37` 条已解析文献、`#### 2.` 不分裂、含 `hyperfsad/remem/duoad`；deck **64 页 == 索引 64 条**且 **64/64 页备注含现行图注**、原生页 = `[(1,framework),(2,matching),(3,constructions),(16,encoders_geo)]`；23 张表全部单页（`word_review.json`）。
   - **接手前它自报的缺口**：脚本在 `all_Word_images_match_current_sources` 断言失败 —— 定位为**命名轮在 17:17 重新渲染了 5 张图**（`fig1_framework.png`、`fig2_matching.png`、`fig3_constructions.png`、`fig4b_matched_encoders.png`、`fig8_resources.png`，mtime 17:17:15–17:17:35），而 docx 构筑于 **17:16:09**，故其内嵌的是改名前版本；deck 则**根本未生成**。
2. **deck 补出**：`docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx`，**64 页 / 76,633,287 B / SHA-256 `0D9E5CB7667773C129BC1D90A95959DB70B20D050E173B1E88585982A077EA6F`**；`finalize_deck.mjs` **`finding_count = 0`**（packageIntegrity 与 presentationLayout 均 0）。
   - 先补齐缺失的 slide-1 原生源：`docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260925.pptx`（**707,997 B / SHA-256 `9054C77F1D63E1FE5D0A127AE5BB063C716A5DAC3E3F05F50DFE89C17A24D71E`**，`packageIntegrity.finding_count = 0`），由 `finalize_figure.mjs`（`FIG1_SCRATCH=.tmp_revision_20260925/fig1`）从**命名轮已生成**的 `candidate_math.pptx`（17:17:22）产出；随后 `build_deck.mjs`（Built 64 slides）→ `assemble_deck.ps1`（Assembled 64 slides with native diagrams）→ `finalize_deck.mjs`。
   - 同步件：`FIGURE_SLIDE_INDEX.json` **64 条**（61,110 B）；`图件与PPT页码索引.md` **64 行**（表头即"现役文件：All_Figures_Complete_20260925.pptx"）。
   - 内嵌图核对：deck 内 **61 个 `ppt/media/*`**；**60 个位图页与盘上 PNG 逐字节相同（60/60）**；差异仅 **原生页 [1,2,3,16]**（可编辑方法图，非位图）。
3. **两句 full-pixel 落点**（`scripts/paper_complete_review_20260920/results.md`；`Select-String` 行号，`Read` 工具行号少 1）：
   - **A（像素/网格分辨率敏感性段）**：`results.md:56` —— 句组以 `… Existing full-pixel points retain the same directions as the stride-eight aggregate interaction points; this is a useful numerical sensitivity check …` 起，含 `The check does not remove that concern: the same units were re-evaluated at per-pixel (stride-one) resolution, where the two primary MPDD interactions remain positive with intervals excluding zero and the two BTAD interactions stay close to zero with intervals spanning zero, so the zero-exclusion judgements are unchanged, and these per-pixel intervals are narrower than on the sparse grid.` 与 `One secondary effect excludes zero only at the finer grids and spans zero at the coarsest grid, and the per-pixel results are provided with the reproduction materials rather than entering the main tables.`
   - **B（限制段）**：`results.md:174` —— `… full-pixel intervals are computed only for the two primary DINOv2-S/14 interactions and are provided with the reproduction materials rather than in the main tables, and …`
   - **docx 内命中**（空白归一化 `re.sub(r"\s+"," ",text)`）：`per-pixel (stride-one) resolution` ✓、`zero-exclusion judgements are unchanged` ✓、`full-pixel intervals are computed only for` ✓（**3/3**）；且**不含** `full-pixel intervals remain unavailable`。
   - **口径红线**：新增文本**未**出现 `SOTA/outperforms/state-of-the-art/全面领先`（全文 2 处 `state-of-the-art` 均为**既有否定式免责句**"makes no … state-of-the-art claim"，改前 `.bak_pre_handover_1755` 同处同文）；未把"区间跨零"写成"零效应"；未声称区间进主表；未改任何数值。
   - **一处取舍**：为与给定句 `narrower than on the sparse grid` 相容，删去 17:13 重写引入的 `The stride-one intervals are narrower than the archived stride-eight intervals only for MPDD.`（与给定句直接冲突）；17:13 重写的其余内容保留。
4. **docx 复测**（`build.py`，输出同名）：**60 页 / 23 表 / 28 内嵌图 / 154 原生数学对象 / 12 编号公式 / 37 文献 / 20,465 词**（Word COM `ComputeStatistics`）；**23,673,134 B / SHA-256 `BCB9A086D8E5963CCBC72C03FA855DAACA5E098F960875E3C99C75C939C02139`**。改前同名文件已备份 `…20260925.docx.bak_pre_handover_1755`（23,616,285 B）。23 张表**全部单页**（`tablePages` start==end）。相对重建前（23 表 / 28 图）表图数**不变**；词数 20,403 → 20,465（同一 Word 口径）。
5. **验收跑通**：`check_delivery.py` **146 项全过**，输出 `{"passed":146,"pages":60,"words":20465,"references":37,"math_objects":154}`；`.tmp_revision_20260925/validation.json` 的 146 个 checks **全为 true**（含 `all_Word_images_match_current_sources`、`64_slides`、`slide_1..64_caption_synced`、`four_native_diagrams`、`all_tables_single_page`）。
6. **门禁**：`qa_layout.py`（现役 layout）**TOTAL PROBLEMS: 0**（8 张，最小 11.29 pt）；`figure_font_gate.py --self-test` **4/4**（`self-test passed: 4 controls behaved as required`）；`pytest tests -q` **260 passed**（1 warning）。
7. **红线复核**：冻结哈希 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` ✓、`1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B` ✓、`9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837` ✓；A1 control parity `k2 0.343706` / `k4 0.388328` 未变（`experiments/dynamic_fusion/innovation_breadth_20260908/*/RESULTS_s0_k2.json`、`…k4.json` 的 `frozen_ref`；`tests/test_freeze_a1_mpdd.py` 在 260 passed 内）；docx 含 `0 target-trainable parameters` ✓；**未 git add / commit**。
8. **并发复查**：命名轮最后写盘 **2026-09-25 17:18:50**（`scripts/paper_complete_review_20260920/figure_sources/build_methods.mjs`）；17:53 / 17:57 / 18:09 / 18:23 四次进程抽查（`Win32_Process` python/pythonw/codex/node）**均无**计算进程；`results.md` 未再被覆盖（两处编辑复查仍在，mtime 17:59:34）。
9. **未做 / 不确定**：① **未重出 `paper.pdf` 与 `.tmp_revision_20260925/preflight/`**——`export_review.ps1` 的 `Fields.Update()` + `ExportAsFixedFormat` 在本机两次长时间（>10 min）无输出，遂改跑**等价 Word COM**（`Repaginate` + `ComputeStatistics` + `Tables`）写 `word_review.json`（页/词/表/表页口径与脚本一致，实测 5.7 s）；② 位置 A 的宽度措辞按**给定原文**保留，但据盘上数据 BTAD `I_BAL` 的 stride-1 区间宽（0.004789）**略宽于** stride-8（0.004733）——属既有微差，**未改数值**，仅此登记。

---

## 九、A22 / A04 / A11 执行结果（**只追加**；上文各节一字未改）

> 背景：作者批准执行 `docs/PREREGISTRATION_20260924_CN.md` 的 **A22 / A11 / A04** 三项。三项**全部纯 CPU**（复用盘上既有冻结 dump / canonical 特征 / 已有 map），**不触碰 GPU**；全部新产物落 `experiments/prereg_20260924/out/A{22,11,04}/`，**未覆盖** `E1_fullpixel_ci/`、`05_baselines*`、`E2_shared_op_ablation/` 等既有目录。数值与凭据详见 `PREREGISTRATION_20260924_CN.md` **§七（A22）** 与 **§八（A04）**；A11 见本节末尾与预注册文件后续追加节。

### 9.1 A22（统一几何下 PatchCore 两原生配置并列）——**已完成（含证据）**

- **口径/设计决定**：指标 = 冻结共同区域 macro `pixel_ap`；三列 = `PatchCore_harmonised448` / `native_official224` / `native_local128`；**零重跑、零 GPU**（复用盘上既有原生 dump，在同一冻结区域网格上重采样重算）；区间沿用统一几何子表自身约定（`default_rng([seed, shot, replicate])` + `weighted_auroc_ap`，stride-8，B=1000）。
- **前提变更（待作者追认）**：把两张**原生几何**列并入"单一输入几何（短边 448）"子表——正是这条前提造成"两原生配置塌缩为一列"；区域不重裁、单元集不变（4 数据集 × 全部类别 × seed 0 × K = 1 = 36 类别单元），每行带 `geometry` 与 `NATIVE geometry - admitted only by the premise change` 注记，并写入 `A22_STATUS.json → premise_change_pending_ratification`。
- **命令 / 成本**：`python scripts/prereg_20260924/a22_patchcore_second_column.py --output experiments/prereg_20260924/out/A22 --datasets btad mpdd mvtec visa --seeds 0 --shots 1 --bootstrap 1000`；**墙钟 2078 s（34.6 min）**，**显存 0 MiB**（对比 §2.4 估 ≈3.5 GPU 卡时）。
- **产物**（`out/A22/`）：`A22_second_column.csv` **46,606 B**、`A22_second_column_macro.csv` **1,849 B**、`A22_collapse_vs_parallel.csv` **9,041 B**、`A22_checks.json` **4,163 B**、`A22_geometry.json` **16,840 B**、`A22_STATUS.json` **2,411 B**（SHA-256 前 16 见预注册 §7.3）。
- **契约核对**：新列 `PatchCore_harmonised448` 与 `harmonised_common_region.csv` **36 行 max|Δ| = 0.0**；两原生列与 `baseline_common_region.csv` **72 行 max|Δ| = 0.0**（**逐行 bitwise 相等**）。
- **结论**：36/36 单元上 448 与 224、448 与 128 **均不相等**（<1e-9 判据 0 个相同）⇒"塌缩"是**子表几何前提**所致，非数值巧合；与 Figure S6 契约**符号 4/4 一致**（128−224 四数据集同为负）。
- **未做**：未计算"两列之差"的配对区间（§2.4 未登记）。

### 9.2 A04（跨方法稳定性）——**已完成（含证据；口径待作者追认）**

- **口径/设计决定（4 项待追认）**：纵轴 = 冻结共同区域 macro `pixel_ap`；横轴 = **输入几何**（共同区域 − 自身原生帧）+ 第二类**参考增强**（AnomalyDINO rotation − canvas）；六配置；样本 MPDD + BTAD × 全部类别 × seed 0、1 × K 1、4（4 组 / 36 类别单元 / 432 读数）；配对单位 = 图像；抽样流 `default_rng([20260913, dataset_id, category_id, replicate])`；个体 95% + Bonferroni 1−0.05/6。待追认项 = ① 纵横轴定义本身（`EXPERIMENT_GAP` D-01 自述未定）② "原生帧"实现 ③ 区间网格（近小网格改用全网格）④ 样本范围。
- **命令 / 成本**：`python scripts/prereg_20260924/a04_cross_method_stability.py --output experiments/prereg_20260924/out/A04 --datasets mpdd btad --seeds 0 1 --shots 1 4 --bootstrap 1000`；**墙钟 520 s（8.7 min）**，**显存 0 MiB**（对比 §2.1 估 8–16 GPU 卡时）。脚本支持 `--resume`（首跑一处组装断言崩溃后**未重算已完成单元**）。
- **产物**（`out/A04/`）：`A04_point_values.csv` **131,079 B / 432 行**、`A04_stability.csv` **16,398 B / 64 行**、`A04_cross_config.csv` **4,395 B / 8 行**、`A04_checks.json` **18,611 B**、`A04_STATUS.json` **2,569 B**；`units/` 检查点 **36 个**。
- **契约核对**：六配置的**共同区域**读数与 `baseline_common_region.csv` **216 行 max|Δ| = 0.0**；原生帧侧与历史拼装的 `baseline_native_frame.csv` 为**诊断性**对照（PatchCore ≤1.3e-3；A1/AnomalyDINO 0.022–0.070，**如实登记、不声称复现**）。
- **结论**：输入几何扰动下，四个画布帧配置（A1_J/A1_L/AnomalyDINO canvas/rotation）Δ 一致为正（32/32 配置-组为正，95% 多数排除零）；**两个 PatchCore 列 Δ≈0、区间跨零**（其原生帧就是冻结共同区域 = 官方 224 裁剪矩形，扰动近退化）。⇒ **§2.1 成功判据判为"扰动下方向不一致"**（8/8 组非六配置同向），按 §2.1"结果不利时的处理"**如实报告，未改口径、未缩范围、未把跨零写成零效应**；第二类扰动（参考增强）方向一致为负（15/16 格）。
- **缺失（如实列出）**：MVTec AD / VisA 未纳入（登记的原生帧产物只覆盖 MPDD/BTAD）；未做 seed 扰动；未做跨配置显著性检验。

### 9.3 A11（共享操作多条件消融）——**已完成（含证据）**（2026-09-26 刷新）

- **口径/设计决定**：3 消融（ABL-S/ABL-N/ABL-C）+ baseline × seed 0、1 × K 1、2、4、8 = 8 条件 × 2 数据集（MPDD development / BTAD holdout），全部 32 个 cell/单元；消融实现**直接 import** 既有 `e2_shared_op_ablation`（`score_j` / `compose_l` / `SLOTS` / 权重组），区间实现与抽样流**直接 import** 既有 `e1_fullpixel_ci`（`replicate_weights` / `profile_from_blocks` / `pooled_ap_auroc_multi`，流 = `default_rng([20260913, dataset_id, category_id, replicate])`）；新脚本 `scripts/prereg_20260924/a11_shared_op_ablation_multi.py`（**不改**原脚本、**不写**既有 `E2_shared_op_ablation/`）。
- **门禁**：`--mode check` 用既有 `e2` 模块重算归档 map，**21/21 pass，max|d| = 9.537e-07**（脚本自带 1e-6 容差）；单元级抽查与归档 `interaction_by_ablation.csv` 的单条件交互**逐格 max|Δ| = 1.7e-18**。
- **队列**：`experiments/prereg_20260924/run_queue_a11.ps1`（2 个不相交 shard：`--datasets mpdd` / `--datasets btad`，均为 seed 0,1 × K 1,2,4,8；每单元 checkpoint + `--resume`；15 s 采样显存/系统内存；**RAM 停止规则改为连续 3 次 ≥96%**——首版 93% 单点阈值曾在 19:12:42 因一次瞬时 95.4% 误杀两 shard，已修正并如实登记）。
- **截至 2026-09-25 20:45 实读**：`out/A11/units/` 已落 `mpdd_s0_k1`、`mpdd_s0_k2`、`btad_s0_k1` 三个单元 checkpoint（1.52 MB / 1.52 MB / 0.75 MB）；2 解释器在跑；`sum_peak_ws` ≈ 8.0 GB、`worst_peak_ws` ≈ 6.7 GB、`system_used` 峰值 82.8%（均低于停止规则）；**显存 0 MiB**（gpu_used 1.32 GB 为桌面基线）。
- **2026-09-26 收尾实读（本节最新值）**：全量运行止于 **01:46:24**（两 shard 各 **20,995 s**，16 单元 / 2,304 点单元格 / 128 条件行 / 16 汇总行），收尾 `--mode assemble` 于 **01:46:41** 落盘。产物与 SHA-256、结构核验、装配缺陷订正、多条件 vs 单条件逐条对照、口径与随机流、红线与限制：**见 §二.1 C14 与 §十**，以及 `PREREGISTRATION_20260924_CN.md §九`。**A11 已由"执行中"转为"已完成"。**

### 9.4 分类计数刷新（对照 §〇）

| 归类 | §〇 原值 | 本轮（A22/A04）之后 | **2026-09-26（A11 完成后，现役口径）** | 说明 |
|---|---:|---:|---:|---|
| **已完成（有凭据）** | 13 组 / 43 项 | 15 组（+A22、+A04） | **16 组**（+C14 = A11） | 见 §二.1 C13 / C14 与 §九 |
| **需作者决定** | 18 | 18 | **18** | A22 带 1 项、A04 带 4 项**待追认设计决定**；**A11 无新增待追认项** |
| **需新写脚本 / 新实验** | 5（A04/A11/A22/A06/E-08） | 3（A11 执行中 / A06 / E-08） | **2（A06 / E-08）** | A04、A11、A22 均已移出（见 §二.3） |
| **已作废 / 不补** | 13 组 | 13 组 | **13 组** | 未动（N2 的 A11 条目改写为"已转为已完成"，见 §二.4） |
| **仍无法核实** | 6 | 6 | **6** | 未动 |
| **与本轮并行流程相关** | 1 | 1 | **1** | 未动（2026-09-25 命名修订轮，见 §二.6） |

- **§一 开放事项总表**：原 #5（D-01/A04）、#6（D-05/A11）、#7（A-22）三项已执行；**2026-09-26 刷新后**该表编号顺移为 **#5 = A04、#6 = A22**（两者只余**待追认的设计决定**），**A11 整行移出**（登记于 §二.1 **C14**）。
- **红线**：三个冻结哈希实读未变；`E1_fullpixel_ci/`、`p4_fullpixel/`、`05_baselines*`、`E2_shared_op_ablation/` 均只读；**未 git add / commit**；新增文本禁用词自查 **0 命中**。
- **出处**：`PREREGISTRATION_20260924_CN.md` §七（A22）/ §八（A04）/ **§九（A11）**；`MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` §十八（及 **§十九 = A11 已完成**）；脚本 `scripts/prereg_20260924/`。

---

## 八、2026-09-25 收尾追加（**只追加**）：paper.pdf 重出 + 措辞订正 + E-08 处置

> 本节只记录本轮盘上实测，不改动上文任何文字。上文 **§七 第 9 条**的"未重出 `paper.pdf`"与"宽度措辞按给定原文保留"两处，**以本节为准**。

### 8.1 paper.pdf 重出（已产出；引擎为 WPS，Word 路径失败）

- **产物**：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.pdf`，**61 页 / 10,875,228 B / SHA-256 `89497729A950EF0DFB4AC9379B5E5664CAC106A561ADD9E2138C7B5B3C26718E`**；PDF 元数据 `Creator = WPS 文字`（`pypdf` 实读）。
- **页数口径**：措辞订正后 docx 自身为 **61 页**（Word COM `ComputeStatistics(2)`，**4.9 s** 实测；词数 20,465 → **20,505**）；因此 PDF 61 页与 docx **一致**。任务书预设的"60 页"是**订正前**口径。23 张表仍全部单页（`start==end`）。
- **Word 引擎失败（如实登记）**：`ExportAsFixedFormat` 在本机对该文档**始终不产出文件**。共 **5 次**尝试——2 参数形式、12 参数并关闭 `DocStructureTags`、`OptimizeFor` 打印/屏幕两种、默认打印机/PDF 打印机——每次 **11–45 分钟无输出、无异常**，Word 进程稳定占用约 **30–40% 单核**、无模态对话框（`tasklist /v` 窗口标题仅为 `HardwareMonitorWindow`）。对照证据：**同一 docx** 的 Word COM 统计过程 **4.9 s** 完成；**一页对照 docx** 经同一调用 **4.9 s** 导出成 PDF ⇒ PDF 子系统与文档模型均正常，仅该文档的导出停滞。超时后为腾出机器曾终止这些 Word 进程（诊断要素已记于本条）。
- **可用工具链**：本机已装 **WPS Office**（`KWPS.Application` / `wps.exe` 注册于 App Paths，`New-Object -ComObject KWPS.Application` 实读成功）；`Get-Command` 探测 **未见** `soffice` / `pandoc` / `gswin64c`。`KWPS.Application` 打开该 docx 后 `ExportAsFixedFormat(path,17)` **11.5 s** 写出上述 PDF（脚本端到端 16.9 s，含 Word 统计）。
- **配方落盘**：`scripts/paper_complete_review_20260920/export_review.ps1` 已改为 **`-Engine wps`（默认）**：WPS 出 PDF + Word COM 统计写 `word_review.json`；保留 `-Engine word` 分支（注释标明本机会停滞）；另写 `.tmp_revision_20260925/pdf_export.json`（`engine/elapsedSec/pdfBytes/docxPages`）。改前件 `export_review.ps1.bak_pre_pdf_1848`。**未改任何打印机默认设置**（`HKCU\...\Windows\Device` 实读仍为 `Lenovo LJ2206W`）。
- **复现性提示**：WPS 输出含生成时间戳，**逐次重导 SHA 会变**（本轮两次同为 10,875,228 B，SHA `7C2F4337…` → `89497729…`），与既有 E-09 记录的 docx 非字节级可复现同源。

### 8.2 措辞订正（过度概括 → 限定表述）

- **落点**：`scripts/paper_complete_review_20260920/results.md:57`（`Read` 工具行号）。
  - **原**：`… so the zero-exclusion judgements are unchanged, and these per-pixel intervals are narrower than on the sparse grid.`
  - **新**：`… The zero-exclusion judgements for the two primary MPDD interactions and the two BTAD interactions are unchanged. At the 98.75% level their per-pixel intervals are narrower than the stride-eight intervals for the two MPDD interactions, whereas the two BTAD intervals are of comparable width to their stride-eight counterparts, one marginally narrower and the other wider by about 1%.`
- **为何原句不准确（盘上 98.75% 区间宽实读）**：
  - stride-1：`experiments/prereg_20260924/out/A08/interaction_by_grid.csv`（:2 MPDD `I_TRI` 0.006616、:3 `I_BAL` 0.005604；:9 BTAD `I_TRI` 0.004726、:10 `I_BAL` **0.004789**）。
  - stride-8：`…/limitation_closure_20260915/E1_fullpixel_ci/interaction_by_grid.csv`（:2 MPDD `I_TRI` 0.008654、:3 `I_BAL` 0.008410）与 `…/A_btad03_corrected/interaction_dataset_stride8.csv`（:2 BTAD `I_TRI` 0.004788、:3 `I_BAL` **0.004724**）。
  - 结论：MPDD 两项**更窄**；BTAD `I_TRI` **略窄**（0.004726 < 0.004788）、`I_BAL` **略宽约 1.4%**（0.004789 > 0.004724）⇒ "全部更窄"是过度概括。
- **同时限定 `unchanged`**：`E_BAL_J`（MPDD 次要不平衡效应）在 stride 1/4 排除零、stride 8 跨零（`interaction_by_grid.csv` 的 `ci9875_excludes_zero` 实读），故"zero-exclusion judgements are unchanged"只允许**限定在两项主交互及其 BTAD 对应项**；紧随其后的 `One secondary effect …` 句保留。
- **数值未动**：本处只改措辞，未改任何数字、表列、图件或文献。
- **docx 内命中**（空白归一化 `re.sub(r"\s+"," ",text)`）：新句 `zero-exclusion judgements for the two primary MPDD interactions` ✓、`one marginally narrower and the other wider by about 1%` ✓；旧断言 `narrower than on the sparse grid` **已消失** ✓（`python-docx` 实读）。

### 8.3 docx 复测与门禁（本轮实测）

- **docx 复测**（`build.py` 重建同名件）：**61 页 / 23 表 / 28 内嵌图 / 154 原生数学对象 / 12 编号公式 / 37 文献 / 20,505 词**；SHA-256 **`E0D5462B347C4C44B5999D476DE26CFDCF35034438831D6A0861D004D8BA72F4`**（23,673,208 B）；改前备份 `…20260925.docx.bak_pre_wordingfix_1848`（23,673,134 B）。
- **交付验收**：`.tmp_revision_20260925/check_delivery.py` **146/146 全过** → `{"passed":146,"pages":61,"words":20505,"references":37,"math_objects":154}`。
- **三项门禁**：`qa_layout.py` **TOTAL PROBLEMS: 0**（最小 11.29 pt）；`figure_font_gate.py --self-test` **4/4**（`self-test passed: 4 controls behaved as required`）；`pytest tests -q` **260 passed**（1 warning，SciPy/NumPy 版本提示）。

### 8.4 E-08 处置（最保守口径）与待决项

- **处置**：复现包**只放 URL + revision + SHA-256 清单，不放权重本体**；清单直接引用 `docs/MODEL_WEIGHTS.md`（46 项，不重抄）。
- **已补文档**：`docs/REPRODUCE_TO_TABLES.md` 新增"E-08 复现包：环境 → 权重获取 → splits → 运行 → 期望输出"小节；`docs/REPRODUCIBILITY_PACKAGE.md` 新增 **§8**（清单要点 + 待决项）。二者均改前备份 `…bak_pre_e08_1848`。
- **待决项**：**D1** 权重本体不再分发（本轮按此处置）；**D2** 若作者同意再分发，需加入 46 个权重**本体** + 逐项许可 + `THIRD_PARTY_NOTICES.md` 条款 + `SHA256SUMS` 重打（本机实读合计 **12,858,068,253 B ≈ 12.0 GiB**）；**D3** 其余子项（`methods/` 的 (a)/(b) 方案、`VD1_MANIFEST.json` 的 `manifest_sha256` 回填）待拍板。
- **纪律**：未把 `dist/`、权重、数据集加入 git；**未 `git add / commit`**；未改任何实验数值或冻结产物；本节新增文本不含禁用词，也未把"跨零"写成"零效应"。

---

## 十、2026-09-26 A11（共享操作多条件消融）**已完成**（**只追加**；上文各节除 §〇/§一/§二.2/§二.3/§二.4/§三/§四/§九.3/§九.4 的**计数与编号刷新**外，其余一字未改）

> 背景：`PREREGISTRATION_20260924_CN.md` §4.3 原判 A11"**不可运行**"（既有脚本只跑 seed 0、无区间、配套脚本会覆盖既有产物）。执行轮另立脚本 `scripts/prereg_20260924/a11_shared_op_ablation_multi.py`，全量运行已结束。**完整数值、结构核验、逐条对照、口径与随机流、限制**见 `PREREGISTRATION_20260924_CN.md` **§九**；本节只给验收要点与红线。

### 10.1 已闭环（含证据）

- **规模 / 耗时**：4 变体（baseline / ABL-S / ABL-N / ABL-C）× seed 0、1 × K 1、2、4、8 × 2 数据集 ⇒ **16 单元 / 2,304 点单元格 / 128 条件行 / 16 汇总行**；2 路 shard **并行 20,995 s（≈5.83 h，纯 CPU，显存 0 MiB）**，收尾 `--mode assemble` 约 **17 s**。运行止于 **2026-09-26 01:46:24**，产出于 **01:46:41** 落盘。
- **产物**（`experiments/prereg_20260924/out/A11/`）：`ablation_metrics_multi.csv` **116,666 B / `F96C9980…CDEC01`**；`replicate_multi.npz` **3,873,040 B / `7FC433A2…ADC168A`**；`interaction_by_ablation_condition.csv` **15,450 B / `AF38B29A…851CBD`**；`A11_multi_vs_single_condition.csv` **3,298 B / `2527D1AD…80C3CB`**；`A11_STATUS.json` **1,054 B / `869F595B…A0E8203`**；单元检查点 **16 件**。
- **结构**：三张 CSV **0 空 / 0 NaN / 0 重复键**；`replicate_multi.npz` = **512** 条长度 **1,000** 的宏平均数组。口径：`stride = 8`、`replicates = 1000`、区间 = 逐单元**配对**宏平均后的 **2.5/97.5 百分位**、抽样流 `default_rng([20260913, dataset_id, category_id, replicate])`；**独立复算 128 + 16 行 max|Δ| ≤ 5.2e-18**。
- **结论（探索性，不构成排名）**：**MPDD 8/8 行**区间排除零、与单条件同号；**BTAD 8/8 行**区间**全部跨零**（方向未定，**不得**读作"零效应"），其中 4 行反号 —— 但 `baseline`（**未消融**参考）在 BTAD `I_TRI` 上同样反号 ⇒ **反号不能单归于消融**。128 个条件行中区间排除零 **70** 个，其中 9 个符号与单条件参照相反（**全部在 BTAD**）。按预注册 §2.2 判据：MPDD 三个消融均 ≥6/8 且无"反号且排除零" ⇒ 成立；BTAD 上 **ABL_C 触发**"反号且区间排除零" ⇒ 如实报告"该共享操作在部分条件下改变方向"，**不升格为"模块已验证"，也不降级为"模块无效"**。
- **需与结论同读**：`I_TRI` 上 **ABL_C 与 baseline 逐格相同**（`naive_alpha` 在 `TRI` / `DUP` 槽位上与 `branch_weights` 数值一致）⇒ ABL_C 的可分辨信息只在 `I_BAL`；BTAD 每单元仅 3 类、可分辨程度低于 MPDD（6 类）。

### 10.2 装配缺陷（**自查发现、已登记并订正；未改任何实验数值**）

- 首轮队列在 01:46:41 自动装配，日志末行 `assembled 2304 point cells from 16 units (0 missing); 0 condition rows; 0 aggregate rows` ⇒ 产出**仅表头（121 B）**与**空表（5 B）**两张派生表。
- 两处起因：① `INTERACTIONS` 用**带 `_L` / `_J` 后缀**的构造名，与点表 `construction` 列的**无后缀** `A1 / BAL / DUP / TRI` 不匹配 ⇒ 每条交互被键检查跳过；② `_archived_single_condition()` 逐行覆盖、**只留最后一个类别**（BTAD `03` / MPDD `tubes`），使"原单条件"参照不是数据集宏平均。
- **订正后逐字节证明未改数值**：`ablation_metrics_multi.csv`、`replicate_multi.npz`、`A11_STATUS.json` 三件的 SHA-256 与首轮清单**完全相同**；改变的只有上述两张派生表；**未重跑任何单元**。订正的内证：`archived_vs_recomputed_abs_delta` 由 **1e-3–1e-2** 降到 **≤3.98e-08**。
- **清单口径提示**：`state/A11_execution.json → artifacts` 记的是 **01:46:41 首轮装配**的字节/SHA，其两张派生表条目（121 B / 5 B）**不是**订正后的现役值；现役值以 `PREREGISTRATION_20260924_CN.md §9.2` 为准（该状态文件未改动，以保留首轮记录）。

### 10.3 第五节的红线复核（实读）

- `experiments/dynamic_fusion/limitation_closure_20260915/E2_shared_op_ablation/`：`git status --porcelain` 变更条目 **0**；`E1_fullpixel_ci/`、`05_baselines*`、`p4_fullpixel/` 均只读。
- 三个冻结哈希实读未变：`3C83AB00…A0B8BB`、`1C770129…73EC4B`、`9DB99E60…8FB837`。
- **未改任何实验数值**；禁用词自查 **0 命中**；未把"区间跨零"写成"零效应"。

### 10.4 本文件本轮实际改动（**为保持清账一致，非"只追加"**）

1. **§〇**：分类计数表刷新（已完成 13 → **16 组**；需新写脚本/新实验 5 → **2**）+ "一句话"刷新。
2. **§一**：**A11 行移出**、其后各行**编号顺移**（原 #7–#21 → 现 #6–#20）；原 #5（A04）/ #7（A22）由"是否执行"改写为"已执行；仍开放的是待作者追认的设计决定"；新增 **2026-09-26 刷新说明**。
3. **§二.1**：新增 **C14 = A11**（含产物 / SHA-256 / 结论 / 缺陷 / 红线）。
4. **§二.2**：A04 口径、A11/A22 脚本两条**决策点**刷新（不再阻塞执行）。
5. **§二.3**：X1–X3（A04 / A11 / A22）移出，余 **X1 = A06、X2 = E-08**（表内只剩 2 项）。
6. **§二.4**：**N2（gap A11 → D-05）**改写为"已由'不补'转为已完成"，保留为历史记录。
7. **§三 #8**：A04 / A11 / A22 处置追加"三项均已执行完毕"。
8. **§四**：清单由 **21 条 → 20 条**（A11 移出、编号顺移），并加移出说明。
9. **§九.3 / §九.4**：A11 由"执行中"改为**已完成**；计数表增加 **2026-09-26 现役口径**列。
10. **本节（§十）**：新增。

### 10.5 未做 / 不确定

1. 本轮**未重跑任何 A11 单元**，也**未**改动 `e2_shared_op_ablation.py` / `e2_abl_s_addendum.py`（只读）与 `E2_shared_op_ablation/`（写入 0 项）。
2. 本轮**未**把 A11 产物并入正文 / 补充材料 / 图件；是否进稿属作者决定。
3. 本轮**未给跨数据集的一般结论**（BTAD 8/8 行跨零、可分辨程度低于 MPDD；`I_TRI` 上 ABL_C 与 baseline 逐格相同）。
4. 本轮**未**触发 RAM 停止规则以外的任何中断；§九.3 记的 2026-09-25 19:12:42 一次 RAM 规则误杀属前一轮已登记事项，其修正版在本次运行中未再触发。
