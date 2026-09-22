# 项目整体验收（2026-09-20 早晨）

> **最后刷新时间：2026-09-20 12:58（Asia/Shanghai）**，工作区 HEAD = `841b478`（annotated tag `final-20260920`；`git describe --tags --dirty` = `final-20260920-dirty`）。
> 刷新范围：只更新**文档一致性与措辞**相关的条目（自检数值、C16 台账描述、仓库状态、构建校验复跑），**未重跑任何工作流的计算**。下文凡"实测"均为本次刷新时在盘上实读或实际执行所得；凡沿用原记录者已注明。
> 逐条问题编号见 `docs/ISSUE_REGISTER_20260920.md`（R-01…R-21），计划见 `docs/REMEDIATION_PLAN_20260920.md`。

一句话结论：**通过。** 夜间批次 2 的 36 项检查在 B 节口径修订与补齐之后**仍全部成立**；
图件门禁、工作流 B 的锚点门、索引一致性、构建校验全部通过。
**本次刷新后已无"非通过项"**：原先记录的两条 `selfcheck.py` 既有失败现已消除，自检为 **71/71 全过**。

## 一、总表

| # | 检查项 | 期望 | 实测 | 判定 |
|---|---|---|---|---|
| 1 | 夜间批次 2 验收（重跑） | verdict=pass / 36 检查 | `verdict=pass phases=8 checks=36`（exit 0） | **pass** |
| 2 | 仓库自检 `selfcheck.py` | 全过 | **`checks=71, passed=71, failed=[]`**（2026-09-20 实读 `experiments/dynamic_fusion/representation_matching_interaction_20260914/SELFCHECK.json`）；原先记录的两条既有失败已消除：① 期望单元数改为按状态文件计数（实读 `units=16, statuses=['completed']`）；② `read-only inputs were not written` 现记 `passed=true`（`1642 frozen data artefacts unchanged`） | **pass**（刷新前记为 pass-with-note 69/71） |
| 3 | 图件版面 `qa_layout.py` | 0 problem | `TOTAL PROBLEMS: 0`；最小字号 **11.29 pt**（下限 11.0）〔本次未重跑，沿用原记录〕 | **pass** |
| 4 | 字号门自测 `figure_font_gate.py --self-test` | 4 组对照符合预期 | exit 0〔本次未重跑，沿用原记录〕 | **pass** |
| 5 | 工作流 B 口径锚点 `ANCHOR_CHECK.json` | 双门为真 | `pass_offline=true, pass_local=true, pass=true`；identity ci9875 = `[+0.001930, +0.011602]` / `[+0.000783, +0.009617]`（本次实读复核，与首版一致） | **pass** |
| 6 | 共同区域表行数 | 864 数据行 | **864**（与 `FIGURE_BINDING`/`ARTIFACT_INDEX`/`HANDOVER` 一致） | **pass** |
| 7 | claim→evidence 台账 | 含 C1–C17、列完整 | **17 行 × 10 列**，末三项 C15/C16/C17 | **pass** |
| 8 | 稿件构建校验 | tables 18 / figures 8 / equations 12 / refs 34 | **一致**（2026-09-20 因 BTAD 措辞修订**重出 docx** 后复跑 `build.py`：`tables=18, figures=8, display_equations=12, references=34 键`，含 `ksdd2:34`） | **pass** |
| 9 | 仓库状态 | 无意外未提交 | HEAD `841b478`；**8 个 tag**；`git status --porcelain` 共 **50** 行，其中 tracked **modified 3 个**（`README.md`、`NEW/READONLY_PROOF.json`、`NEW/SELFCHECK.json`），其余未跟踪项均为刻意不入库或本轮产物（`dist/`、`canonical/`、`units/`、`.trae/`、各轮 `.bak*` 等） | **pass**（刷新前记为 HEAD `df51d7c`、6 tag、17 项未提交，已过期） |
| 10 | 资源 | 无残留进程、内存充裕 | 0 个 python 进程；可用内存 5.42 GB〔沿用原记录〕 | **pass** |

## 二、与 `VALIDATION_20260918.md` 的差异点（那份报告仍成立，但需知道这些变化）

1. **工作流 B 的口径已修订并重跑**：区间改为主研究口径（逐自助副本作差后聚合）。MPDD 由"14 条中 2 条跨零"变为 **14/14 全部排除零**；BTAD 14/14 仍跨零。论文摘要与结论中"软混合失去区间分离"的说法**已被证伪并改写**。
2. 正文表格由 **17 → 18 张**（新增表 18：正则系数网格 + 12 条件编码器行）；页数 **38/39**（Word 实测，加入表 18 后由 37/38 增加）。
3. 共同区域表由 703 → **864** 行（local128 补齐 + VisA 的 AnomalyDINO dump 补齐 48/48），四数据集各 6 个方法列。
4. 图 7 的 MVTec 与 VisA 均已重出为 6 列；`FIGURE_BINDING.md` 已同步。
5. **【已完成】**原第 5 条"一处仍与正文口径相反"已消除：`CLAIM_EVIDENCE_LEDGER.csv` 的 **C16 行**现已更新为新口径（MPDD 主口径 `14/14` 全部排除零、最弱格 OT ε=0.05 的 `I_BAL` 下界 `+0.000063`；BTAD `14/14` 仍跨零、判定不变），并把"沿用旧口径（对 4 个条件点值取分位）的区间与'软混合跨零'结论"写入**禁止用法**列。
   - **凭据（2026-09-20 实读）**：`experiments/dynamic_fusion/paper_evidence_closeout_20260914/CLAIM_EVIDENCE_LEDGER.csv` 第 17 行（C16）；口径修订的实测与新旧 14 行对照见 `experiments/dynamic_fusion/limitation_closure_20260915/B_correspondence/REPORT_CN.md` §10.8。

## 三、本次验收未覆盖 / 需人决策

1. ~~**C16 台账行**（见上）——建议下一轮改。~~ → **已完成（2026-09-20）**：见 §二.5，凭据为台账第 17 行实读。
2. ~~`selfcheck.py` 的两条既有失败~~ → **已完成（2026-09-20）**：`SELFCHECK.json` 现有 `checks=71, passed=71, failed=[]`；第①条判据已改为按状态文件计数（实读 `units=16`），第②条现为 `passed=true`。两条均**非本次刷新引入**，也非本次刷新消除（属更早的判据修订），此处仅同步事实。
3. 数据/代码可得性的 **3 个占位**（仓库地址、归档 DOI、发布包许可）与 MPDD/BTAD 许可的补录，**仍需作者决定**（未变；见 `docs/REMEDIATION_PLAN_20260920.md` P3）。
4. 三个 scratch 目录（`_maskfix_smoke`、`_regression_check`、`_smoke_canonical`，合计约 1.12 GB）**仍待作者决定去留**；2026-09-20 复核**仍然存在**：
   - `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/_maskfix_smoke`
   - `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/_regression_check`
   - `experiments/dynamic_fusion/seeds_extension_20260917/_smoke_canonical`
5. 本报告未重跑各工作流的**计算**（只跑门禁与校验）；数值正确性由 B 的 `ANCHOR_CHECK`、A 的四门、以及支撑材料审计中 17 组"正文数字 ↔ 产物"逐条核对覆盖。**2026-09-20 的刷新同样只做"重出 docx + 门禁复跑"，未重跑任何计算。**
6. **（刷新增补）** 本轮另有两类改动属于本报告范围外但影响一致性，登记在此备查：
   - 测试入口：仓库根新增 `pytest.ini` 界定正式范围（`tests/` 递归，显式排除单个文件 `tests/innovation_v6_dgsafe/test_wave2a_probes.py`），2026-09-20 实测 **260 passed / 0 failed / 0 errors**；原"141/141 passed"已在相关文档就地标注为 2026-09-02 历史快照。详见 `tests/README.md`。
   - BTAD 统计措辞：全文统一为"点估计接近零、区间跨零，当前数据不足以确定交互方向"，禁止 `true null` / `true zero effect` / `essentially zero` 三种强断言（正文与台账均已清零；审计登记/计划两份过程文档中以引号引用这些字符串用于指认，属刻意保留）。

## 四、2026-09-22 状态追加（只记变化，上文与上文判定不改写）

1. **推送已完成（R-11 的推送部分）**：2026-09-22 实测 `git rev-list --count origin/main..HEAD` = **0**，`main` 跟踪 `origin/main` 且已同步（HEAD `de25a22`）。§一 #9 所记"HEAD `841b478`、8 tag、tracked modified 3 个"为 2026-09-20 的历史值，现基线已变（当前 HEAD `de25a22`；工作区有本轮收口改动，未提交、未推送）。
2. **§一 #8 的口径需注明**：该行的 `tables 18 / figures 8 / equations 12 / refs 34` 来自**已冻结的旧链** `scripts/manuscript_build_20260914/build.py`（与 `docs/manuscript_reference_matching_20260914/build_validation.json` 实读一致）。**权威交付稿**走 `scripts/paper_complete_teacher_review_20260920/build.py`，2026-09-22 重建实测 **20 表 / 22 内嵌图 / 12 编号公式 / 142 原生数学对象 / 34 文献 / 47 页 / 16,969 词**（docx SHA-256 `F3CAE3B491A99F8649E8900756D60C75163DDAA43B715F73D271308038DC44ED`）。两处数字对应**不同构建链**，并存不互斥。
3. **§一 #3 / #4 的覆盖对象**：#3 的 `qa_layout.py` = `TOTAL PROBLEMS: 0`（最小 11.29 pt）对应 `scripts/figures_reference_matching_20260914/layouts` 下 7 张**旧版面**图。2026-09-22 对 20260920 方法图（`layout-1/2/3.json`）跑同一门禁的结果是：fig3 = 0、fig2 = 2、figS1 = 6 处 `TEXT-OVERFLOW`（均为文本框高度不足的保守折行估计，改前改后相同，非本轮引入）；该批图的字号门是 `scripts/paper_complete_teacher_review_20260920/figure_sources/figure_manifest.json` 的 `minimumPrintPtAt17cm` = **11.294 pt**（≥ 11 pt 通过）。
4. **新增阻断项（建议编号 R-22）**：本轮开始时 `docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx` 与 `build.py` 依赖的版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` **均不在盘上**（`a08dc46` 将 `*.docx` 加入 `.gitignore` 后消失），`build.py` 首次执行报 `FileNotFoundError`。已从 git 对象逐字节恢复并 SHA-256 校验一致（`18694B90EE47BBE2…` / `9DB99E60CD3024D1…`）后完成重建。**母本为不可由源重建的二进制输入**，建议移出忽略范围或保留受控副本并登记。详见 `docs/论文与图件问题汇总_仅复核_20260921.md` §八 F17。
5. **图件侧收口 + PPT 重出（上文未覆盖）**：F01（图2(b) 紫框与填色对齐）、F02（图3(b) 权重措辞：图内 `build_methods.mjs:430`、图注 `figures.json` `constructions.caption`、正文 `manuscript.md:111`）、P04（图 S4 面板 (b) 的 ±5% 参考带与实测 6.8% 分开表述；5% 判据下实测首个 N = **700**）已改并重渲染；F14 的 58 页 PPT 已重出（`All_Figures_Complete_20260920.pptx` SHA-256 `48DD91800B714331…`，第 20/21 页＝收敛／稳定性）。数据未改：`baseline_common_region.csv` SHA-256 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` 前后一致；#6 的共同区域表仍 864 行。
