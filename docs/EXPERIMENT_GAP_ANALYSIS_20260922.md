# 实验欠缺盘点（只读分析）— 2026-09-22

- 目的：通读权威源，列出**全部主张与其证据**，对照在册开放项（T02/T03/T04/T05、P01/P03/P05/P06/P08、F05/F06）逐条核对"是否已有实验支撑"，产出"实验欠缺"表与 8 类易漏项的逐条结论。
- 口径：**本文件只做盘点与成本外推，未跑任何新实验、未用 GPU、未改动任何数值**。所有数字与路径均为盘上实读。
- 权威源：`scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}` + 同目录 `build.py`；交付稿 `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`。
- 成本锚点（用于外推，实读）：`experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines/SPEED_VRAM_BENCH.csv`、同目录 `_bench_speed_vram/run_final.log`、`.../05_baselines_ext_20260921/PREFLIGHT.json`。
- 说明：正文 `results.md §4.2.x` 与 `tables.json`/`figures.json` 的键一一对应；下表"现状证据"用 `文件:行` 或产物路径。

---

## 一 主张—证据总览

| # | 主张（摘要/贡献/结果） | 出处 | 支撑表图 | 证据（盘上） | 状态 |
| --- | --- | --- | --- | --- | --- |
| C1 | 受控分解：DUP/TRI/BAL × J/L 分离"改权重 / 加信息 / 换匹配" | manuscript.md:29-33；results.md:3-19 | Table 1、4、5、6 | `tables.json:design/main/matching/effects` | 有 |
| C2 | MPDD 的 S 交互 +0.772 / +0.595（98.75% 区间排除零） | abstract；results.md:33-39 | Table 7 | `tables.json:s_interaction` | 有 |
| C3 | BTAD 交互方向未定（点近零、区间跨零） | abstract；results.md:39 | Table 7、15 | `tables.json:s_interaction/generalization` | 有 |
| C4 | D（WRN50-2）四条交互全正（98.75% 排除零） | results.md:41-45 | Table 8、9 | `tables.json:d_full/d_interaction` | 有 |
| C5 | 编码器依赖：BTAD 上 D−S 配对差排除零，MPDD 未分辨 | results.md:49 | Table 10、16 | `tables.json:encoder_diff/encoders` | 有 |
| C6 | 支持预算 K 与类别条件改变交互方向（MPDD 随 K 增、BTAD 反号） | results.md:57-63 | Figure 5(a)(c) | `figures.json:budget_category` | 有 |
| C7 | 定性定位：最优/退化案例 + Otsu 轮廓（显示用） | results.md:69-77 | Figure 6、7 | `figures.json:cases_good/cases_bad` | 有 |
| C8 | 外部方法在"共同有效区域"上的上下文对照（六列冻结 + 三族扩展） | results.md:81-87 | Table 11、12 | `tables.json:baselines/baselines_ext` | 有 |
| C9 | 资源：历史阶段计时（部分仪器化）与新同机基准 | results.md:91-99、182-186 | Table 13、20，Figure 8、S5 | `tables.json:resources/benchmark`；`figures.json:resources/speed_vram` | 有（受限） |
| C10 | 额外编码器 E1–E3 迁移检查（scope 敏感） | results.md:135-143 | Table 16 | `tables.json:encoders` | 有 |
| C11 | 8 种子支持集变化（MPDD 恒正、BTAD 变号） | abstract；results.md:145-149 | Table 17、Figure 5(b) | `tables.json:seed_variance` | 有（仅 MPDD/BTAD） |
| C12 | 对应方式敏感性（canvas/Procrustes/置换/OT，MPDD 14/14 排除零） | results.md:153-165 | Table 18、19 | `tables.json:correspondence/correspondence_sensitivity` | 有 |
| C13 | 几何修正 + 共享操作消融（探索性，单条件） | results.md:169-175 | Figure S2、S3 | `figures.json:shared_op_ablation/extra_cases` | 有（探索性） |
| C14 | bootstrap 数值稳定性（S4，非训练收敛） | results.md:190-192 | Figure S4 | `figures.json:stability` | 有 |
| C15 | KSDD2 事前冻结的合取确认（四条 95% 区间排除零） | results.md:111-119 | Table 14 | `tables.json:ksdd2_confirmation` | 有 |
| C16 | 四数据集泛化（95/98.75/99.375% 三档） | results.md:123-131 | Table 15 | `tables.json:generalization` | 有 |
| C17 | "冻结=无目标域训练"（不含 loss–epoch） | abstract；§ Three-6；results.md:190 | Table 2 | `tables.json:models`（`0 target-trainable parameters`） | 有（口径待补，见 A03） |

**结论**：主链主张（C1–C5、C8、C15、C16）的证据链完整；欠缺集中在**呈现口径、跨方法可比性说明、复现性材料**三类，以及**少量已存在但未入稿的产物**（图像级指标、多方法定性图）。

---

## 二 实验欠缺表（主表）

> "成本量级"一律用第一节所列实测锚点外推，不空估。优先级：高=投稿/评审可直接追问；中=影响可读性或稳健性表述；低=已作为限制登记。

| 编号 | 欠缺内容 | 支撑哪条主张/表图 | 现状证据（文件:行 / 产物路径） | 补齐所需 | 成本量级（锚点外推） | 优先级 | 建议：补 / 不补（理由） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | **图像级指标未与像素级并列报告**：无 image AUROC / image AP 的系统表；仅在 §4.2.4 举一例 | C2/C5/C7（"图像级池化与像素排序回答不同问题"） | 正文仅 `results.md:53` 一处（BAL D L image AP 0.9372 vs A1 L 0.9468）；产物**已有**图像级字段：`05_baselines/patchcore/*/summary.csv`（`image_auroc,image_ap`）、`05_baselines/anomalydino_*/anomalydino_native_macro_*.csv`（`macro_image_auroc,macro_image_ap`）、`01_geometry/units/btad_s1_k8/*/metrics.csv` | **仅写作**（+一次小聚合） | 聚合脚本 + 1 表：CPU 分钟级（数据已落盘，无需重算分数） | 中 | **补**（写作层，零重跑；可正面回应"像素级优势是否等同图像级优势"） |
| A02 | 表 11/12 表注未**逐方法**给出协议（分辨率/画布/旋转/参考库构造）；SubspaceAD 256 vs 官方 672 的偏离未写入 | C8；P10 | `tables.json:446`（表 11 仅写 "Methods differ in backbone, resolution and augmentation"）；`tables.json:548`（表 12 有 Protocol 列但为粗标签）；`05_baselines_ext_20260921/PREFLIGHT.json` 的 `resolution_decision`（672 在 6 GB 卡 12 图 ≥15 min 未完成、5797/6144 MiB） | **仅写作** | 写作 + 表注扩写：小时级（事实已在 PREFLIGHT/DONE.json） | 高 | **补**（P10 明确要求写进协议列与补充材料；审稿人必问） |
| A03 | **"为何所有对比方法无需针对该数据集训练"无成体系说明**（当前只有零散一句） | C1/C17；T02；外部评审要求⑤ | `manuscript.md:162`（"全部冻结，故不适用训练曲线"）、`manuscript.md:202-206`、`results.md:190`；`tables.json:110-113`（`0 target-trainable parameters`）；权重/检查点事实见 `submission_repro_20260827/config/frozen_a1.json`、`05_baselines_ext_20260921/PREFLIGHT.json` | **仅写作** | 一段（中英）+ 引用盘上清单：小时级 | 高 | **补**（外部评审本轮明确要求；同时纠正 P01"无训练≠零计算"） |
| A04 | **跨方法稳定性比较缺失**：无 "共同性能指标 × 共同扰动条件" 下 PatchCore/AnomalyDINO/SubspaceAD/WinCLIP+/AnomalyCLIP 各配置的性能稳定性 | T03（替换图是否比较了所有方法的稳定性）、T02 | S4 只做 bootstrap 数值稳定性（`figures.json:86`）；Table 17 只覆盖本文 S 交互的 8 种子（`tables.json:1135`）；四个外部配置仅有 4 个条件单元（`EXT_CHECKS.json:9-19`），**无逐扰动结果** | **需新计算** | 需为每个方法定义共同指标+扰动并重跑逐单元：按 `PREFLIGHT.json` 冒烟 0.42 s/img(SubspaceAD@256)、0.18 s/img(WinCLIP)、0.69 s/img(AnomalyCLIP) 外推，144 单元 ≈ **1–3 h GPU/方法/条件**（单卡 6 GB 串行）；六方法两条件 ≈ **半天–1 天 GPU** | 中 | **不补**（理由：与本文"交互效应"主张无关；AI 辅助评审已接受用适用稳定性图替代并只要求说明对比标准，见 T03；若外部评审坚持，须先定义纵/横轴再评估） |
| A05 | **完整多方法对比图未进正文**（F05）：代表性检测图只在附件/PPT | C7/C8；外部评审要求⑥ | `figures.json` 无 multimethod 键；`manuscript.md:247` 仅以文字提到 "accompanying figure deck … 36 category-level comparisons"；图源在 `.tmp_complete_figures_20260920/qualitative/fig7_multimethod_*`（渲染产物已在盘） | **仅写作/图件**（选代表图入正文） | 选图 + 图注：小时级（PNG 已渲染，无需 GPU） | 高 | **补**（外部评审⑥明确"检测结果图是视觉评价的主要参考，应放实验结果分析"；素材已在盘） |
| A06 | **"所有案例都有两种输出"过宽**（F06）：逐类别附录无各方法预测轮廓 | AI 辅助评审"两种输出"要求 | 主文 5 案例有 J/L 热图 + L 轮廓（`figures.json:34-44`）；附录逐类别为 query+GT+六列热图（`figures.json:44` 末句）；逐方法轮廓未生成 | **需计算**（对多方法列做与主文同规则的阈值化后处理） | 阈值化+重渲染：与 A05 同一批图，**小时级 GPU/CPU**（后处理，非训练） | 中 | **部分补**：正文 5 案例已满足；附录按"两种输出"**重新界定覆盖范围或声明限制**（写作，低成本），是否补齐全部方法轮廓交作者 |
| A07 | **seed / 支持集方差只覆盖 MPDD 与 BTAD** | C11 / abstract "support-set analyses reveal meaningful variation" | `tables.json:1135-1191`（Table 17：8 seeds，仅 MPDD/BTAD，canonical masks）；MVTec AD/VisA 有 12 条件但无跨种子方差表；KSDD2 有 12 条件 | **仅写作**（可用已有逐条件数据算 SD）+ 若要 8-seed 版则**需计算** | 写作版：CPU 分钟级；8-seed 版：按 S5 外推 ≈ **数小时 GPU/数据集** | 中 | **补（写作版）**：至少报已有 seed 条件的离散度（成本极低）；8-seed 扩展**不补**（无主张依赖） |
| A08 | **full-pixel 无区间**（R-18）：全像素列只有点估计 | C4/C5/C16；已登记限制 | `tables.json:722`（"No full-pixel confidence intervals were computed"）；`results.md:105`（限制第四条） | **需新计算**（全像素池化上做 1000 次配对自助） | 全像素池 + 1000 重采样 × 4 数据集 × 多条件：**>1 天 CPU/内存密集**，无现成产物 | 低 | **不补**（已作为限制登记并已按措辞约束写入；补它改变不了任何主结论方向） |
| A09 | **同机证据范围受限**（P05/P06）：单机、MPDD 三类别、seed 0、K=1/4；无 query-only 延迟分布 | C9 | `SPEED_VRAM_BENCH.csv`（6 单元、432 次查询访问、含参考准备）；`results.md:186`（"no independent complete-process wall-clock or query-only latency distribution"） | **需新计算**（多数据集/查询端拆分） | 单方法全量按 A1 单方法 828 s×24 ≈ **5.5 h GPU/方法** | 低 | **不补**（保留为限制；已在正文说明边界，且不得改写成"端到端"） |
| A10 | **S5 首轮离群未披露**：PatchCore 128 首轮 30.527 s，最终表用重测 24.190 s | C9（Table 20 时间范围）；可复现性 | `_bench_speed_vram/run_final.log:42` = 30.527 s；`_bench_speed_vram/recheck/SPEED_VRAM_BENCH.csv` = 24.190 s；`_bench_speed_vram/SPEED_VRAM_BENCH.pass1.json` | **仅写作** | 一句话披露 + 指向 recheck：**分钟级** | 中 | **补**（成本近零；"min–max"作为唯一离散度指标时，首轮离群必须交代） |
| A11 | **共享操作未在多条件下消融**（S2 单条件、无区间） | C13；限制第六条 | `figures.json:58`（ABL-S/ABL-N/ABL-C，seed 0、K=1、单次运行，明确"exploratory、无区间"） | **需新计算** | 三消融 × 12 条件 × 区间：按 A1 单条件外推 ≈ **数小时 GPU** | 低 | **不补**（已在正文声明为探索性且不作为模块验证；补它引入新口径） |
| A12 | **权重/最优性不成立**：无"全局最优权重"证据 | 已在正文限定 | `results.md:7`（"not evidence that the selected weights … are globally optimal"） | 不适用 | — | 低 | **不补**（已正确限定，无需证据升级） |
| A13 | **复现性：无"从零到表"最短路径，无权重哈希**（R-03/R-04） | Data and Code Availability；§4.1.4 | `manuscript.md:200-206`（只述"reproduction uses manifests/specs/bootstrap streams"）；`manuscript.md:222-224`（"no repository URL or archive DOI is claimed"）；`submission_repro_20260827/` **有** `SHA256SUMS`、`SOURCE_COMMIT.txt`、`config/frozen_a1.json`，但**无** `MODEL_WEIGHTS.md`（权重 URL+revision+SHA256） | **仅写作 + 打包** | 权重清单 + 最短路径 + 源提交指针：**天级文档工作**（P1-1…P1-7 均未动） | 高 | **补**（投稿阻断项；审稿会问"给我一条能跑出表的路径"） |
| A14 | **AnomalyCLIP 检查点来源未核实**，直接影响 Table 12 该列口径 | C8；P11 | `05_baselines_ext_20260921/PREFLIGHT.json` 的 `checkpoint_rule_and_caveat`（自训 vs 上游 2024-12 日志未核）；`docs/BASELINE_EXPANSION_PLAN_20260921.md` 1.3–1.4 | **需作者确认**（非实验可解） | — | 高 | **登记待作者**（若确系自训，该列须标 "auxiliary-domain trained, zero-shot on the target"） |
| A15 | 与近期方法对照满足"3–4 个"口径 | C8；T07（已结案） | `tables.json:456-538`：AnomalyCLIP(ICLR 2024)、AnomalyDINO(2024)、WinCLIP+(NeurIPS 2023)、SubspaceAD(2025) + PatchCore | 不适用 | — | — | **不补**（复核确认已满足；T07 结案口径不变） |
| A16 | 统计口径（配对自助的区间层级 + 多重比较校正）已说明 | 全部区间 | `manuscript.md:188-198`（1000 次配对图像级自助、条件化于已观测类别与支持清单、98.75%/99.375% Bonferroni 家族、"no simultaneous guarantee"）；`tables.json:380/548/1045/1298` 各表注 | 不适用 | — | — | **不补**（已满足） |
| A17 | 共同区域口径（覆盖率）已写进正文 | C8 | `results.md:85`（76.56% / 70.49% / 76.56% / 59.07%，BTAD-03 ≈ 58.36%）；`tables.json:446` 表注 | 不适用 | — | — | **不补**（已满足；本轮以 `baseline_common_region.csv` 复算 mean=0.7656/0.7049/0.7656/0.5907 一致） |

**欠缺表摘要（判定）**

- **建议补（10 项）**：A01、A02、A03、A05、A07、A10（以上均"仅写作/仅图件"，零 GPU）＋ A13（写作+打包）；A06 部分补；A14 登记待作者。
- **建议不补（6 项）**：A04、A08、A09、A11、A12、A15/A16/A17（后三者已满足）。
- **其中"零重跑即可解决"的**：A01、A02、A03、A05、A06(部分)、A07(写作版)、A10、A13、A14 —— **占欠缺项的大多数**；真正需要新算力的只剩 A04（跨方法稳定性）、A06（附录全方法轮廓）、A08（full-pixel 区间）、A09（query-only 延迟）、A11（多条件消融），而这几项**均被判定为"不补/交作者"**。

---

## 三 八类易漏项逐条结论

| # | 核查项 | 结论 | 证据 |
| --- | --- | --- | --- |
| 1 | 图像级指标（如 image AUROC）与像素级**并列**报告？缺哪一种？ | **部分满足**。像素级（AP/AUROC）系统报告；**图像级缺并列表**，正文仅 `results.md:53` 一处举例。产物中 image 指标**已存在**（见 A01） | `results.md:188`（primary=pixel AP；pixel AUROC 为二级）；`results.md:53`；`05_baselines/patchcore/*/summary.csv` 表头含 `image_auroc,image_ap` |
| 2 | **共同区域**口径是否在正文说清（76.56% / 70.49%）？ | **已满足**。正文与表注均给出；本轮复算一致 | `results.md:85`；`tables.json:446`；复算 `baseline_common_region.csv`：mpdd 0.7656、btad 0.7049(min 0.5836)、mvtec 0.7656、visa 0.5907 |
| 3 | 每方法的协议（分辨率/画布/旋转/参考库构造）是否在表 11/12 表注**逐方法**给出？ | **部分满足**。分辨率部分隐含在配置名（`PatchCore 224/1024`、`128/256`、`SubspaceAD 256 fp16`、`WinCLIP+ 240`、`AnomalyCLIP zero-shot 518`）；表 12 有粗 Protocol 列；**旋转与参考库构造未逐方法写**，SubspaceAD 256↔672 偏离未写 | `tables.json:386-455`（表 11 无 Protocol 列）；`tables.json:456-556`；`05_baselines_ext_20260921/PREFLIGHT.json` |
| 4 | 随机性来源（seed / 支持集抽样）是否有**方差报告**？覆盖哪些数据集？ | **部分满足**。seed 方差 = Table 17（8 seeds，**仅 MPDD/BTAD**）；Table 4 有跨条件 SD 列；Table 17 末列为 between-seed SD / bootstrap 半宽。**MVTec AD / VisA / KSDD2 无跨种子方差**；支持集抽样有"conditional on the observed support manifests"说明 | `tables.json:1135-1191`；`tables.json:632`（Table 4 SD 说明）；`manuscript.md:192`（bootstrap 条件化） |
| 5 | 失败 / OOM / 退化案例是否登记（含图 S5 离群重测）？ | **部分满足**。主工作流**零失败**（`FAILURES.json` = `[]`；各方法 `*_failures_*.json` 均 `[]`）；退化案例有 Figure 7（2 例）；**S5 首轮离群（30.527 s）与重测（24.190 s）未在正文披露**；SubspaceAD@672 因显存跑不完属"未执行"（已记 PREFLIGHT） | `.../representation_matching_interaction_20260914/FAILURES.json`；`05_baselines/patchcore_failures_*.json`、`anomalydino_native_failures_*.json`；`_bench_speed_vram/run_final.log:42` vs `.../recheck/SPEED_VRAM_BENCH.csv` |
| 6 | 统计口径（配对自助的**区间层级**、多重比较是否需校正）是否明确？ | **已满足**。明确 1000 次**图像级**配对自助；区间在每个 replicate 内形成、再按类别/条件聚合后取分位；三个调整家族（4/4/4 与 8 格）用 98.75%/99.375% Bonferroni；明示"无同时保证"；full-pixel 无区间已声明 | `manuscript.md:188-198`；`tables.json:380`（S 家族）、`:548`（表 12 不是排名）、`:1045`（99.375% = 8 格）、`:1298`（sweep 无全族校正） |
| 7 | **复现性**：是否给出"从零到表"的最短路径与输入校验（权重哈希）？ | **缺失**。正文只述所用材料；**无**最短路径、**无**权重 SHA-256 清单；`submission_repro_20260827/` 有 `SHA256SUMS`/`SOURCE_COMMIT.txt` 但对应旧包，权威链未绑定 | `manuscript.md:200-206`、`:222-224`；`submission_repro_20260827/{SHA256SUMS,SOURCE_COMMIT.txt}`；`docs/REMEDIATION_PLAN_20260920.md` P1-1…P1-7 全部未执行 |
| 8 | 与**近期方法（近两三年）**对照是否满足"3–4 个"口径？ | **已满足（T07 结案，复核一致）**。四个近期方法 + PatchCore 经典 + 本文 A1 两列；外部评审"近两三年三四个比较先进的方法"标准已达标 | `tables.json:456-538`；`docs/论文与图件问题汇总_仅复核_20260921.md` §八 T07；`docs/ISSUE_REGISTER_20260920.md` §〇ter R-20 |

---

## 四 成本锚点（实读，用于外推）

| 锚点 | 数值 | 来源 |
| --- | --- | --- |
| 同机 bench：A1 J / A1 L 总量 | 197.118 s / 195.300 s（6 单元、432 次查询访问、含参考准备；峰值 2376.8 MiB） | `05_baselines/SPEED_VRAM_BENCH.csv:2-3` |
| 同机 bench：AnomalyDINO / +rotation | 30.959 s / 78.863 s（峰值 111.6 MiB） | 同上 `:4-5` |
| 同机 bench：PatchCore 128 / 224 | 24.190 s / 36.931 s（403.1 / 409.8 MiB） | 同上 `:6-7` |
| 单方法整段墙钟（含加载） | A1_J 828 s、A1_L 826 s、AnomalyDINO 153 s、+rot 343 s、PatchCore128 224 s、PatchCore224 299 s | `_bench_speed_vram/run_final.log:5-35` |
| 外部扩展冒烟吞吐 | SubspaceAD@256 0.4168 s/img；WinCLIP+ 0.18 s/img；AnomalyCLIP zs 0.69 s/img | `05_baselines_ext_20260921/PREFLIGHT.json`（`smoke` 字段） |
| SubspaceAD@672 不可行 | 12 图 ≥15 min 未完成、5797/6144 MiB（WDDM 换出） | `05_baselines_ext_20260921/PREFLIGHT.json` 的 `resolution_decision` |
| 外部三族合计 | 144/144 + 144/144 + 36/36，零失败零 OOM，GPU 合计约 185 min | `docs/论文与图件问题汇总_仅复核_20260921.md` §八 T06 |
| S5 重测 | PatchCore128 首轮 30.527 s → 重测 24.190 s | `_bench_speed_vram/run_final.log:42`、`_bench_speed_vram/recheck/SPEED_VRAM_BENCH.csv` |

---

## 五 与在册开放项的对照

| 在册项 | 本轮核对结论 |
| --- | --- |
| T02（loss–epoch 不可得） | 复核一致：无目标域优化循环故无 loss–epoch；**写成"不适用"可以，但不得写成"零计算/零准备"** → 对应 A03 |
| T03（替代图是否比较所有方法稳定性） | 复核一致：S4 只做 bootstrap 数值稳定性，未覆盖外部配置的性能稳定性 → 对应 A04（建议不补） |
| T04/T05（统一标准/协议说明） | 表 11/12 的**统一维度**已在表注给出（单元、查询集、区域、指标、统计）；**逐方法协议与协议偏离未写** → 对应 A02 |
| P01（无目标域训练≠所有方法从未训练） | 复核一致：预训练编码器与继承检查点仍带训练来源；参考库/coreset 属准备计算 → 对应 A03 |
| P03（S4 不证明训练收敛） | 复核一致：S4 图注已明写 "not training convergence"（`figures.json:86`）→ 已满足 |
| P05/P06（同机证据范围、阶段计时边界） | 复核一致：§4.2.14 已限定计时边界；缺 query-only 分布与多数据集 → 对应 A09（不补） |
| P08（稳定性计划书数值逻辑矛盾） | 复核：属文档层面矛盾（`REFERENCE_FIG_CONVERGENCE_PLAN.md` ~148 行），**不改变任何实验产物**；仍按"确认前不搬入论文"处理 |
| F05（完整多方法对比图未进正文） | 复核一致 → 对应 A05（建议补，外部评审⑥同向） |
| F06（"所有案例都有两种输出"过宽） | 复核一致 → 对应 A06（部分补） |

---

## 六 未做 / 不确定

1. **未跑任何实验、未用 GPU**；除文档外未改动任何数值；`baseline_common_region.csv` 保持 `3C83AB00…`（本轮已实算复核）。
2. **A04/A06/A08/A09/A11 的"若补"成本**只能按第一节锚点外推，未实测；且均需先定义"共同指标 × 共同扰动"口径才能评估。
3. **AnomalyCLIP 检查点来源（A14）**无法从盘上判定，需作者确认后决定 Table 12 该列标注。
4. **图像级指标的聚合口径**（逐类别/逐条件宏平均 vs replicate mean）未在盘上找到与主文像素级同口径的图像级区间产物 ⇒ A01 若要做**区间**仍需少量新算；本表只建议"点值并列"。
5. 本轮未复核 `experiments/**` 下与本文无关的历史工作流的失败登记，仅核查本文所用工作流。

---

## 七 2026-09-23 终检：A18 之前各条状态复核 + B 线（统一输入几何子集）新增欠缺

> 口径：只读复核与登记；**本轮未跑实验、未用 GPU、未改任何数值**。所有"仍缺/已满足"都给出盘上实读凭据。
> 新增条目续用 A 编号（A18–A23），与 B 线产物 `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/**` 及 `docs/METHOD_COMPARISON_HANDOFF_20260922.md` 交叉引用。

### 7.1 A01–A17 逐条状态（2026-09-23 复核）

| 编号 | 2026-09-22 判定 | 2026-09-23 状态 | 凭据（实读） |
| --- | --- | --- | --- |
| A01 图像级指标未并列 | 补（零重跑） | **仍缺** | 权威源 `results.md` 仅在 `:53`（举例）、`:65`、`:69`、`:163`（"image-level bootstrap"措辞）处提及图像级，**仍无系统并列表**；产物侧图像级字段仍在（`05_baselines/patchcore/*/summary.csv` 的 `image_auroc,image_ap` 等） |
| A02 表 11/12 逐方法协议表注 | 补（写作） | **主表仍缺；B 线已用另一种方式覆盖一部分** | 表 11/12 表注未改（`tables.json` 的 `baselines`/`baselines_ext`）；B 线把协议写进**新增子集表**的列名 + 表注模板 + `PREFLIGHT.json` 三处（见 `METHOD_COMPARISON_HANDOFF_20260922.md` §5.1）。**注意**：子集表**尚未入正文**，因此 A02 对正文的缺口不变 |
| A03 "为何对比方法无需目标域训练"无成体系说明 | 补（写作） | **仍缺（稿未落）** | `manuscript.md` grep `no target-domain` / `preparation computation` / `zero-computation` = **0**；T12 的中英段落仍只存在于 `docs/论文与图件问题汇总_仅复核_20260921.md` §八 T12 |
| A04 跨方法稳定性比较 | 不补 | **不补（结论不变）** | 无新证据；`METHOD_COMPARISON_HANDOFF_20260922.md` §6 未新增跨方法扰动实验 |
| A05 完整多方法对比图未进正文 | 补（图件） | **仍缺** | `figures.json` 仍无 multimethod 键；36 张 `fig7_multimethod_*` 仍在 PPT 第 23–58 页 |
| A06 "两种输出"覆盖范围 | 部分补（写作） | **仍缺（写作稿未落）** | 正文 5 案例不变；附录逐类别仍为 query+GT+六列热图 |
| A07 seed / 支持集方差只覆盖 MPDD 与 BTAD | 补（写作版） | **仍缺（写作稿未落）** | `tables.json` Table 17 仍仅 MPDD/BTAD；未新增 MVTec/VisA/KSDD2 跨种子离散度句 |
| A08 full-pixel 无区间 | 不补 | **不补（结论不变）** | `tables.json:722` 的限制句未改 |
| A09 同机证据范围受限 | 不补 | **不补（结论不变）** | §4.2.14 边界句未改 |
| A10 S5 首轮离群未披露 | 补（一句话） | **仍缺** | `results.md:184` 只报重测值 `24.190`，全文 grep `30.527` = **0**（首轮 30.527 s 仍未披露） |
| A11 共享操作多条件消融 | 不补 | **不补（结论不变）** | S2 仍为单条件、无区间 |
| A12 权重最优性不成立 | 不补（已限定） | **不补（已限定）** | 限定句未改 |
| A13 复现性：无最短路径/无权重哈希 | 补（写作+打包） | **仍缺** | `docs/MODEL_WEIGHTS.md` **不存在**（`Test-Path` = False）；`REMEDIATION_PLAN_20260920.md` 的 P1-1…P1-7 **全部仍未执行**（勾选清单未变） |
| A14 AnomalyCLIP 检查点来源未核实 | 登记待作者 | **仍待作者** | `05_baselines_ext_20260921/PREFLIGHT.json` 的 `checkpoint_rule_and_caveat` 未变；本轮未从盘上判定 |
| A15 与近期方法对照满足 3–4 个口径 | 不补（已满足） | **已满足（不变）** | 5 家族对照仍在 Table 12 |
| A16 统计口径已说明 | 不补（已满足） | **已满足（不变）** | 主表统计说明句未改 |
| A17 共同区域口径已写进正文 | 不补（已满足） | **已满足（不变）**；B 线另加一层证据 | 正文覆盖率句未改；B 线 `harmonised_common_region.csv` 的 36/36 单元 `region_grid` 与冻结表**完全相同**（`region_mode = frozen`） |

**小结（2026-09-23）**：A01/A02（正文部分）/A03/A05/A06/A07/A10/A13 共 8 项**仍缺且均为"仅写作/仅图件/打包"类，零 GPU**；A04/A08/A09/A11 维持"不补"；A12/A15/A16/A17 维持"已满足/已限定"；A14 仍待作者。**没有任何一项因 B 线而失效。**

### 7.2 B 线带来的新增欠缺（A18–A23）

| 编号 | 欠缺内容 | 支撑哪条主张/表图 | 现状证据（盘上） | 补齐所需 | 成本量级（实测锚点外推） | 优先级 | 建议：补 / 不补（理由） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A18 | **统一几何子集只覆盖 36/144 单元**（4 数据集 × 全部 36 类 × **seed 0 × K = 1**），非四数据集完整协议 | 子集表 A / 图 S6 的"严格化 A" | `HARM/harmonised_common_region.csv` = 180 行 = 5 方法列 × 36 单元；`PREFLIGHT.json → harmonised_run` | 需为表 11/12 的其余 108 单元补跑 PatchCore@448 | **实测锚点**：PatchCore@448 = 4 个 group / **52.4 min**（819.8 / 396.8 / 900.2 / 1027.2 s）⇒ 线性外推 144 单元约 **3.5 h GPU**（单卡 6 GiB 串行） | 中 | **不补**（子集定位本身就是"1/4 子集"，已写进表注模板与 `HARMONISED_SUMMARY.json`；补满只提高分辨率、不改变任何结论） |
| A19 | **区间只对 `pixel_ap` 计算**；`pixel_auroc` 只有宏平均点值 | 子集表 B | `HARM/harmonised_macro.csv` 列头只有 `interval_pixel_ap_lo/hi`；`HARMONISED_SUMMARY.json` 的 `interval` 字段只描述一种区间 | 复用同一 stride-8 抽样流改度量后复跑 `harmonised_common_region.py --mode eval` | CPU 级（B = 1000、stride-8，脚本已支持；未实测时长） | 低 | **不补（登记）**：AUROC 是次要指标，点值已在表内；若作者要求，属低成本可补项 |
| A20 | **WinCLIP+ / AnomalyCLIP 的 448 版本未跑**，属**代码级**排除（检查点/网络绑 240、变换与 37×37 网格绑 518） | 子集准入清单 | `HARM/PREFLIGHT.json`；`METHOD_COMPARISON_HANDOFF_20260922.md` §6.4 | 需插值位置编码 / 改 patch 网格 ⇒ 得到的不再是"发布的那个检查点配置" | 不是"跑一次"的成本：需改模型实现并重验，且会改变该列口径（可能数天级） | 低 | **不补**（会破坏"各自原生配置"的可比性；已在文档写明排除理由是代码级绑定点） |
| A21 | **SubspaceAD@448 仅有 2 图冒烟**（未做全量） | 子集准入清单的排除依据 | `HARM/smoke/subspacead_448.json`：btad/01、2 张查询图，峰值 **2433.5 MB**、**0.8181 s/图**、32×32 网格 | 全量 36 单元 | 按其 0.8181 s/图 × 各单元查询图数外推（未实测全量）；显存不是障碍 | 低 | **不补**（排除理由是**输入规则**——方形拉伸，而非显存或成本；跑全量也不会让它进子集） |
| A22 | **统一几何下 PatchCore 塌缩为一列**，子集内无法再展示"同一方法两配置"的协议敏感度 | 子集表 A / §1.3 协议杠杆 | `METHOD_COMPARISON_HANDOFF_20260922.md` §3.5；§7.4 已登记 | 需另立一列（例如 448 与 224 并列）→ 重跑 | 同 A18：约 **3.5 h GPU**（PatchCore@448 实测 52.4 min/36 单元） | 低 | **不补**（协议敏感度已由**图 S6** 与 `protocol_leverage.json` 的 0.1000 / 0.0265 / 33.3% 承担；子集表刻意只留一列） |
| A23 | **图 S6 未进入正文 docx** | 新增补充图 | 2026-09-23 python-docx 实测 `Figure S6 mentions: 0`；`figures.json` 无 S6 键 | 需在 `figures.json` 增设 S6 条目并重建 docx（页数/表数需复测） | 写作 + 一次重建：分钟级（脚本已存在，门禁已过） | 中 | **登记待作者**（是否把 S6 收进补充材料由作者定；编号不与 S1–S5 冲突，见 `FIGURE_BINDING.md` §十） |

### 7.3 B 线已满足、无需补的部分（避免重复建项）

| 项 | 凭据 |
| --- | --- |
| 复用列与冻结表**逐格一致**（可作"评估口径未漂移"的强证据） | `HARM/HARMONISED_SUMMARY.json → reused_column_parity_vs_frozen_table` 最大绝对差 **0.0**（A1 两列 + AnomalyDINO 两列） |
| 子集区域与冻结表**逐单元相同** | 36/36 个 (dataset, category) 的 `region_grid` = 392×392，`region_mode = frozen` |
| 协议杠杆数字可复算、且**只读** | `HARM/protocol_leverage.json` ← 只读聚合 `baseline_common_region_ext.csv` 的 `pixel_ap` 列；未重算分数图、未用 GPU |
| 图 S6 四道字号/版面门禁 | 2026-09-23 复跑：102 个 text artist 全部 **11.50 pt**、0 互压、0 压图、0 出页；重渲染 PNG 与在盘 PNG 逐字节相同（`0C6F801C…`） |
| 冻结表与扩展表未被触碰 | `baseline_common_region.csv` `3C83AB004420A4F8…`、`baseline_common_region_ext.csv` `1C77012971A4C2EB…` 与 `data/splits/*/manifest.json` 本轮前后一致 |

### 7.4 本节未做 / 不确定

1. 本节**未跑任何新实验、未用 GPU**；除文档外未改任何数值。
2. A18/A22 的"3.5 h"是**线性外推**（锚点：PatchCore@448 实测 52.4 min / 36 单元），未实测 144 单元。
3. A19 的 CPU 时长**未实测**（脚本支持，但本轮未跑）。
4. A23 是否入稿、以及补充材料的最终图号编排，属作者决定。

