# 论文最终修改交接（Paper Revision Handover）— 2026-09-27

> **本文件是当前唯一执行入口。** 上一份交接（[`docs/PAPER_REVISION_HANDOVER_20260924_CN.md`](PAPER_REVISION_HANDOVER_20260924_CN.md) 的 M1–M6）已在 2026-09-26/27 两轮里**全部结清**，逐条证据见 §2；本轮待办为 **T1–T6**。
> 性质：**写作 / 图件 / 打包层，零 GPU**；不改动任何冻结数值、产物或实验结果。
> 目标读者：未参与本项目的独立 AI（Codex）。文档自包含，读完即可定位每一条改动。
> 配套：审核与规划见 [`docs/FINAL_SUBMISSION_AUDIT_20260927_CN.md`](FINAL_SUBMISSION_AUDIT_20260927_CN.md)（含第二方复核附录与阶段规划）。

---

## 0 一句话任务

按 **T1–T6** 修改 **5 个源文件** → 重跑 `build.py` 重建 docx → 重出 PDF → 重建完整 deck → 刷新交付包；全程守住 §5 的 9 条禁做约束，并按 §6 复测门禁数字。

---

## 1 权威源与产物（改哪里、出什么）

| 角色 | 路径 |
|---|---|
| 正文（摘要 / §1–3 / §7） | `scripts/paper_complete_review_20260920/manuscript.md` |
| 结果与讨论（§4–§6） | `scripts/paper_complete_review_20260920/results.md` |
| 表数据与表注 | `scripts/paper_complete_review_20260920/tables.json` |
| 图索引与绑定 | `scripts/paper_complete_review_20260920/figures.json` |
| 文献键 | `scripts/paper_complete_review_20260920/references.json` |
| 构建脚本 | `scripts/paper_complete_review_20260920/build.py` |
| 构建用格式母本 | `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx`（只提供样式/页脚，正文会被丢弃） |
| **构建输出（现役稿）** | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.docx` |
| 图源目录 | `docs/paper_complete_review_20260920/figures/`（含 `multimethod/`） |
| 完整图件 deck | `docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx` |
| 交付包（单一入口） | `docs/FINAL_SUBMISSION_20260926/`（`README.md` 记 4 件的来源与 SHA-256） |
| 复现入口 / 权重清单 | `docs/REPRODUCE_TO_TABLES.md`、`docs/MODEL_WEIGHTS.md` |

> **不要直接改** `docs/paper_complete_review_20260920/English_Manuscript_Source.md`——它是拼装镜像。改动一律落在上表 5 个源文件，再重跑 `build.py`。

---

## 2 已完成，不要重做（含证据）

| 项 | 证据（2026-09-27 实测） |
|---|---|
| **M1** 表 11/12 表注指向 S2 + SubspaceAD 偏离点名 | `tables.json` 的 `baselines` 与 `baselines_ext` 的 `note` 均含 “Table S2” |
| **M2** 权重清单 + 复现包 + 正文最短路径 | `docs/MODEL_WEIGHTS.md`、`docs/REPRODUCE_TO_TABLES.md` 存在；`dist/replication_package_20260920/` 含 `src/ methods/ configs/ weights/`；`manuscript.md` §7 已指向这两份文档 |
| **M3** Figure 7 补 BTAD/VisA 面板 | `figures.json` 有 4 条 `multimethod` 路径（mpdd metal_plate / mvtec grid / visa pcb1 / btad 01） |
| **M4** PatchCore 首轮离群披露 | `results.md` L159：“initial 30.527-second total … the reported 24.190-second value is the documented re-measurement” |
| **M5** 点名 2026 最新工作 | `manuscript.md` L47（相关工作：Hyper-FSAD / ReMem / DuoAD）+ `results.md` L181（讨论段） |
| **M6** A01 状态核实 | 已闭合为 **Table S3**（图像级 95% 区间）；原句 “no image-level interval is claimed” 在现役 docx 中 **0 命中** |
| **命名迁移**（导师要求：不用字母代表模块） | 正文 / 表 / 公式描述性下标 / PPT 文本框：旧代号 `A1 DUP TRI BAL`、`B/S/C/D`、`J/L` **0 命中**（`J(p)`/`L(p)`/`r_{b,L}` 作为已定义匹配函数按英文稿保留）。**例外：栅格图内文字见 T1** |
| **Otsu 轮廓缺陷** | 已修（累计量按像素数归一）；3 张定性图 + 4 张多方法面板已重出；现役 docx 的 **28/28** 内嵌图与图源逐张哈希一致 |

---

## 3 当前基线（改完必须复测这些数字）

现役 docx（`2026-09-27 01:20`，23,951,588 B）：**24 张表**（Table 1–21 + S1 + S2 + S3）、**28** 个内嵌图像对象、**155** 个原生数学对象、322 段。
现役 PDF：**61 页**（`2026-09-26 10:00`，**落后 docx 一批**）。
完整 deck：**64 页 = 28 页论文图件 + 36 页类别附录**（`2026-09-26 09:48`，**落后一批**）。
冻结参照（**不可变**）：A1 control macro Pixel-AP k2 `0.343706` / k4 `0.388328`（容差 3e-4）。

---

## 4 待办 T1–T6

### T1 Figure 7 重出面板的 `n/a` 列与图注口径（**最高优先，需人眼确认**）

- **定位**：`docs/paper_complete_review_20260920/figures/multimethod/*.png`（4 张正文面板）、`results.md` L69 图注、`tables.json` 的 `baselines` / `baselines_ext`
- **现状**：09-27 重出后的面板切换到新版数据口径——逐样本像素 AP 只有 **2 个受控配置**有值，另 **4 个外部方法**进入同目录 JSON 的 `per_sample_pixel_ap_na`（4 项）。09-26 那一代“六列齐全”的面板**不在磁盘上**，只保留在 `docs/FINAL_SUBMISSION_20260926/` 的 docx 与本包 PDF 内。
- **改法（两步）**：
  1. 人眼打开那 4 张面板，确认 4 个外部方法列**是否印出 `n/a`**（文字是烤进栅格的，脚本 grep 不到）。
  2. 若印出，二选一：
     - **(a) 加图注说明（建议）**：在 `results.md` L69 图注末尾补一句，例如 “The four external families are shown as continuous maps only: per-sample pixel AP on the common valid region is reported for the two controlled configurations, because the external families are scored under their own native protocols (Table S2).”
     - **(b) 换回六列齐全面板**：从交付包 docx 中抽出 `word/media/` 里对应的 4 张图，按同名覆盖 `figures/multimethod/` 下 4 个文件。
- **验收**：面板、图注、表 11/12 三者口径一致；`figures.json` 路径未变；重建 docx 后这 4 图哈希与图源一致。
- **风险**：选 (b) 会把栅格图内标签退回旧代号（`ADino` / `PC-128` / `A1 J`），与命名要求冲突；选 (a) 需确认“外部方法不报共同区域像素 AP”与表 11/12 口径不矛盾。**默认建议 (a)。**

### T2 §4.2.3 的绝对表述收窄（A04 已完成探索性检查）

- **定位**：`results.md`，grep `no common metric-by-perturbation`（现 **1** 处）
- **现状**：原句为 “…no common metric-by-perturbation experiment was produced for that purpose, so no cross-method stability curve is reported”；而 A04 产物已在 `experiments/prereg_20260924/out/A04/`（`A04_STATUS.json`、`A04_stability.csv`、`A04_point_values.csv`、`A04_cross_config.csv`、`units/`；覆盖 6 配置、MPDD+BTAD、432 读数、64 条稳定性记录）。
- **改法**：改为范围限定句——本文主分析（§4.2 受控矩阵）不含按扰动展开的跨方法比较；一项覆盖 6 个配置、MPDD 与 BTAD 的**探索性**几何/参考扰动检查（A04，**未并入主分析、不覆盖全部外部配置**）另行归档。
- **验收**：绝对表述归零或改为非绝对；**不得**把 A04 写成定稿证据。
- **风险**：措辞若丢掉 “exploratory / outside the primary matrix”，等于引入未确认的设计口径。

### T3 共享操作贡献的表述收窄（A11 已完成多条件消融）

- **定位**：`results.md`，grep `does not quantify how much each of them contributes`（现 **1** 处）
- **现状**：该绝对句与 A11 产物并存（`experiments/prereg_20260924/out/A11/`：`A11_multi_vs_single_condition.csv`、`ablation_metrics_multi.csv`、`interaction_by_ablation_condition.csv`、`replicate_multi.npz`；16 单元 / 2,304 单元格），A11 自身标注“未并入正文”。
- **改法**：收窄为“本文主分析把这些共享操作**固定而非消融**，因此不将其作为已验证模块”，并给出扩展消融的归档位置。
- **验收**：不再暗示“没有任何量化结果”；不宣称普适模块贡献。

### T4 重出 PDF / 重建 deck / 刷新交付包

- **现状**：docx 已是 09-27 版（24 表 / 28 图同步 / 含 S3），但 **PDF（09-26 10:00，61 页）** 与 **deck（09-26 09:48，64 页）** 落后一批；`docs/FINAL_SUBMISSION_20260926/` 里的 docx 与 PDF 也落后。
- **改法**：
  1. 重出 PDF（与现役 docx 同一次构建）。
  2. 重建 `All_Figures_Complete_20260925.pptx`，并同步 `docs/paper_complete_review_20260920/图件与PPT页码索引.md`（页序：第 1、2、3、16 页为原生可编辑方法图，其余为科学绘图）。
  3. 用最新 docx / PDF / 主图刷新交付包 4 件，并更新 `docs/FINAL_SUBMISSION_20260926/README.md` 的 **SHA-256、页数、冻结时间与「本包状态」**。
- **验收**：README 的 4 个 SHA-256 与实际文件一致；docx ↔ PDF ↔ deck ↔ 图源**四方一致**；除作者侧 3 处外无占位符。
- **风险**：交付包内 `.docx` 被 `.gitignore`（`*.docx`）忽略、不入库——克隆后按 README 指回上游路径取，**不要** `git add -f` 强行入库（见 §5.9）。

### T5 作者侧事项（非 AI 可决，留给作者）

- 稿件内 **3 处显式占位符**：`[[CORRESPONDING_AUTHOR]]`（作者块）、`[[FUNDING]]`、`[[COMPETING_INTERESTS_TO_BE_CONFIRMED]]`（§7）。单位只写到 Hefei University of Technology，缺学院 / 详细地址 / 邮编 / 通讯邮箱。
- **无资助、无利益冲突也必须由作者确认后写明**（不能留空）。
- 目标期刊未定（“中科院四区 SCI”是方向不是刊物）。选刊后再定：正文 / 补充材料拆分、字数、图表上限、模板、图像分辨率、highlights / cover letter / 图文摘要、归档 DOI（`manuscript.md` §7 已写明 DOI 尚未建立）。

### T6（可选）导师关心的“全方法稳定性”覆盖

- **现状**：`Figure S4` 图注已**诚实限定**为“固定 bootstrap 样本的数值稳定性，不代表训练收敛、也不是全方法稳定性比较”（**保留，不要改宽**）。
- 若要补：用统一条件下各配置的**支持集 / 随机种子稳定性**对比（T2 的 A04 是其中一类素材）。
- **禁止**：为冻结推理配置制造 loss 曲线；不得把 S4 改名包装成“全方法稳定性”。

---

## 5 硬约束（禁做清单）

1. **不得把方法对比写成排名**：禁 `SOTA / state-of-the-art / outperforms / 全面领先`；保持 “context table rather than a ranking” 口径。
2. **不得改动任何冻结数值或产物**：A1 定义、control parity（k2 `0.343706` / k4 `0.388328`）、`tables.json` / `figures.json` 的数值字段。
3. **不得削弱 `0 target-trainable parameters`**：任何引入训练 / 自适应组件的做法都不进当前论文。
4. **不得把“区间跨零”写成“零效应”**（R-07）：统一为“点估计接近零、区间跨零，当前数据不足以确定方向”。
5. **不得在 KSDD2 上做新探索**：它是确认集，已报告。
6. **不得在没有预注册的情况下先跑再看**。
7. **不得改写冻结的 read-only 输入**：`READONLY_PROOF.json` 的 `verdict` 必须保持 `no frozen read-only input was written`。
8. **不得直接改拼装镜像**：只改 `scripts/paper_complete_review_20260920/` 的 5 个源文件，再重跑 `build.py`。
9. **不得绕过 `.gitignore` 强加 docx**：仓库策略是**只跟踪一份权威 docx**（白名单见 `.gitignore`）。

---

## 6 重建与验收

```powershell
cd <repo>
python scripts/paper_complete_review_20260920/build.py
```

复测门禁（与 §3 基线逐项对比，变化必须能解释）：

- [ ] 表数 **24**、内嵌图 **28**、数学对象 **155**
- [ ] 28 张内嵌图与 `figures.json` 绑定路径**逐张哈希一致**
- [ ] control parity 两值未变；全文无 `SOTA|outperforms`；`0 target-trainable parameters` 仍在
- [ ] `Read-only proof` verdict 未变
- [ ] 门禁自检 `python scripts/representation_matching_interaction_20260914/selfcheck.py`——**已知 2/69 失败项**（`read-only inputs were not written`、`manuscript: the updated outline exists`），先确认是否仍失败再决定是否一并修

---

## 7 需要人决定的事

1. **T1** 走 (a) 加图注说明，还是 (b) 换回六列齐全面板？
2. **T2 / T3** 只“收窄表述”，还是把 A04 / A11 正式并入正文与补充材料？
3. **T6** 导师是否接受“全方法稳定性”保留为已知范围外？
4. 权重再分发许可（M2 遗留）：打包权重本体，还是只写来源 URL + revision + SHA-256？
5. 选刊与 DOI 政策（决定 T5 的后续格式工作）。

---

## 8 参考数字（自查用）

| 项 | 值 | 出处 |
|---|---|---|
| A1 control macro Pixel-AP k2 / k4 | `0.343706` / `0.388328` | `AXIS_LEDGER_AND_CLOSURE_CN.md` |
| 共同区域覆盖率 | MPDD 76.56% / BTAD 70.49%（min 58.36%）/ MVTec 76.56% / VisA 59.07% | `results.md`；`baseline_common_region.csv` |
| PatchCore128 首轮 / 重测 | 30.527 s / 24.190 s | `results.md` L159 |
| SubspaceAD 256↔672 偏离 | 672 在 6GB 卡 12 图 ≥15min 未完成、5797/6144 MiB | `PREFLIGHT.json` 的 `resolution_decision` |
| 外部方法家族数 | 5（PatchCore / AnomalyDINO / SubspaceAD / WinCLIP+ / AnomalyCLIP） | Table 12 |
| 图像级区间自由度 | 1000 次分层图像重采样；288 单元点估计核验 | `experiments/prereg_20260924/out/A01/A01_IMAGE_LEVEL_INTERVALS.json` |

---

## 9 仓库状态（2026-09-27）

- HEAD `572271a`，**与 `origin/main` 同步**，工作区**干净**。
- 遗留卫生问题（不影响修改，可选清理，**动手前先确认**）：
  - `.gitignore` 的 docx 白名单仍指向 `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`，而现役是 `..._20260925.docx`；
  - 仓库跟踪了 5 个历史 deck（`All_Figures_Complete_20260920/23/24/25.pptx`、`All_Figures_Finalized_20260920.pptx`）与 `scripts/paper_complete_review_20260920/.tmp_revision_20260925/worker_plots_backup/`（临时备份被误入库）；
  - 根目录 `.tmp_*` 共约 **2.4 GB**（已被 ignore，不影响提交，但可清理）。

---

*本文档为只读分析产出，不含新实验、未用 GPU、未改任何数值。所有行号与计数基于 2026-09-27 盘上状态（commit `572271a`）。*
