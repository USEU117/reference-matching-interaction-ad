# 项目整体验收（2026-09-20 早晨）

一句话结论：**通过。** 夜间批次 2 的 36 项检查在 B 节口径修订与补齐之后**仍全部成立**；
图件门禁、工作流 B 的锚点门、索引一致性、构建校验全部通过；仓库状态干净。
唯一的非通过项是 `selfcheck.py` 的**两条既有失败**（与本次无关，见下）。

## 一、总表

| # | 检查项 | 期望 | 实测 | 判定 |
|---|---|---|---|---|
| 1 | 夜间批次 2 验收（重跑） | verdict=pass / 36 检查 | `verdict=pass phases=8 checks=36`（exit 0） | **pass** |
| 2 | 仓库自检 `selfcheck.py` | 仅两条已知失败 | 69/71 通过；两条失败为**既有**：① 硬编码"official PatchCore 完成全部单元（=8）"，而 official224 现为 16 单元；② "read-only inputs were not written" 指向 `outputs/**/canonical/*.npz`（未触碰） | pass-with-note |
| 3 | 图件版面 `qa_layout.py` | 0 problem | `TOTAL PROBLEMS: 0`；最小字号 **11.29 pt**（下限 11.0） | **pass** |
| 4 | 字号门自测 `figure_font_gate.py --self-test` | 4 组对照符合预期 | exit 0 | **pass** |
| 5 | 工作流 B 口径锚点 `ANCHOR_CHECK.json` | 双门为真 | `pass_offline=True, pass_local=True`（identity ci9875 = [+0.001930,+0.011602] / [+0.000783,+0.009617]） | **pass** |
| 6 | 共同区域表行数 | 864 数据行 | **864**（与 `FIGURE_BINDING`/`ARTIFACT_INDEX`/`HANDOVER` 一致） | **pass** |
| 7 | claim→evidence 台账 | 含 C1–C17、列完整 | **17 行 × 10 列**，末三项 C15/C16/C17 | **pass** |
| 8 | 稿件构建校验 | tables 18 / figures 8 / equations 12 / refs 34 | 一致（`references` 为 34 键映射，含 `ksdd2:34`） | **pass** |
| 9 | 仓库状态 | 无意外未提交 | HEAD `df51d7c`；6 个 tag；17 项未提交**全部是刻意不入库**的大目录（`canonical/`、`units/`、`series/`、`.trae/` 等） | **pass** |
| 10 | 资源 | 无残留进程、内存充裕 | 0 个 python 进程；可用内存 5.42 GB | **pass** |

## 二、与 `VALIDATION_20260918.md` 的差异点（那份报告仍成立，但需知道这些变化）

1. **工作流 B 的口径已修订并重跑**：区间改为主研究口径（逐自助副本作差后聚合）。MPDD 由"14 条中 2 条跨零"变为 **14/14 全部排除零**；BTAD 14/14 仍跨零。论文摘要与结论中"软混合失去区间分离"的说法**已被证伪并改写**。
2. 正文表格由 **17 → 18 张**（新增表 18：正则系数网格 + 12 条件编码器行）；页数 **38/39**（Word 实测，加入表 18 后由 37/38 增加）。
3. 共同区域表由 703 → **864** 行（local128 补齐 + VisA 的 AnomalyDINO dump 补齐 48/48），四数据集各 6 个方法列。
4. 图 7 的 MVTec 与 VisA 均已重出为 6 列；`FIGURE_BINDING.md` 已同步。
5. **一处仍与正文口径相反**：`experiments/dynamic_fusion/paper_evidence_closeout_20260914/CLAIM_EVIDENCE_LEDGER.csv` 的 **C16 行**仍写"零排除判定对软混合替换不稳健"及旧区间（该文件是实验产物台账，本轮按要求未改）。**建议下一轮单独修订该行**（改为新口径区间 + 结论），否则台账与正文不一致。

## 三、本次验收未覆盖 / 需人决策

1. **C16 台账行**（见上）——建议下一轮改。
2. `selfcheck.py` 的两条既有失败：第①条是判据过期（应把期望单元数从 8 改为按状态文件计数），第②条需确认 `outputs/**/canonical` 是否属于"只读输入"的定义范围。均**非本次引入**。
3. 数据/代码可得性的 **3 个占位**（仓库地址、归档 DOI、发布包许可）与 MPDD/BTAD 许可的补录，需作者决定。
4. 三个 scratch 目录（`_maskfix_smoke`、`_regression_check`、`_smoke_canonical`，合计约 1.12 GB）仍待作者决定去留。
5. 本报告未重跑各工作流的**计算**（只跑门禁与校验）；数值正确性由 B 的 `ANCHOR_CHECK`、A 的四门、以及支撑材料审计中 17 组"正文数字 ↔ 产物"逐条核对覆盖。
