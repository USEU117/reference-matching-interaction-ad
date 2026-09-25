# 论文 / PPT / 图件 待办总表（唯一交接入口）— 2026-09-23

> **2026-09-25 修订（9 月 26 日完成导出）**：现役源与交付使用 `20260925` 文件名；当前修订说明以 [投稿前复核](PRE_SUBMISSION_REVIEW_20260925_CN.md) 和 [修订与验收](paper_complete_review_20260920/修订说明与验收_20260925.md) 为准。老师已要求执行整批描述性命名，A-21、B-06、C-02 不再“待拍板”。下文 23/24 日统计及状态是历史快照。作者单位已确认合肥工业大学，具体期刊、通讯作者、资助及利益冲突待定。A08 全像素区间已完成，但须保留 DINOv2-S/14、MPDD/canonical BTAD 的适用范围。

> **2026-09-24 本轮交付更新**：现役改为 `paper_complete_review_20260920/Reference_Matching_Complete_English_20260924.docx`（56 页 / 23 表 / 28 图 / 154 数学对象 / 37 文献）与 `All_Figures_Complete_20260924.pptx`（64 页，原生页 1/2/3/16）。旧表中的 20260923 计数为历史快照，不再代表当前交付；详见 [本轮修订与验收](paper_complete_review_20260920/修订说明与验收_20260924.md)。作者元数据与 DOI 仍待补齐。


> **本表自 2026-09-23 起是交接的唯一入口**。其余文档按"历史登记"保留（**不删除**），只在顶部各加一行指针；本表不重复它们的论证，只做汇总、指派与去重。
> 编辑纪律：本表**不改任何实验数值**；`experiments/**` 证据字段、`data/**`、`LICENSE`、`requirements_repro.txt`、版式母本、`figure_sources/**` 科学内容为**红线**；冻结表/扩展表哈希见 **E-13**。
> **验收清单**：论文/PPT/图件**重新生成后**的完整核对清单见 [`docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`](REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md)（可自动核查项 + 需人工判定项 + 防回归项 + 判定模板；使用方式见该文件 §0）。

**现状（10 行内）**

| # | 现状 |
|---|---|
| 1 | **权威稿（现役）**：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx` = **55 页 / 23 表 / 27 内嵌图 / 12 编号公式（152 原生数学对象）/ 34 文献 / 19,434 词**；SHA-256 `9B3E15F56155FA4ABED5B5BF01A55FE22FF70DF7E063AD6B8C2180E844149245`（19,220,478 B，2026-09-23 **第四轮** fig4b 图注 / Table 16 表注收口后重出；**非字节可复现**，见 E-09）。<br>**上一快照**：`EB11FCA8…ACE41`（19,220,393 B，19,394 词；第三轮，2026-09-23）。<br>**历史锚点**：`…Reference_Matching_Complete_English_20260920.docx` = 47 页 / 20 表 / 22 内嵌图 / 142 数学对象 / 17,221 词（`DDB6602E…`），已被上一行取代但**保留在盘**。 |
| 2 | **唯一可编辑源**：`scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}` + 同目录 `build.py`；生成物 `docs/paper_complete_review_20260920/English_Manuscript_Source.md` **禁止直接编辑**（会被下次构建覆盖）。 |
| 3 | **图件命名与绑定位置**：以 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` 为准（正文图号 ↔ 图源 PNG ↔ 生成脚本 ↔ 冻结数据 ↔ PPT 页 ↔ 日期）；正文实际嵌入的副本在 `docs/paper_complete_review_20260920/figures/`。**2026-09-23 新增 §十一**：现役 revision23 入稿图集的口径、门禁复跑、哈希刷新与孤儿处置；**第三轮新增 §十二**：K-09 全量符号审计（152/152）、两处"登记未改"口径统一、本轮复测与门禁；**第四轮新增 §十三**：fig4b 图注与 Table 16 口径同步、图 S4 备注/索引一次重出、`docs/MODEL_WEIGHTS.md` 误记更正。 |
| 4 | **PPT 位置与页数**：`docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` = **63 页**（第 1–27 页＝27 个图面板；第 28–63 页＝36 张逐类别多方法附录）；SHA-256 `5C47F8FFFD16CD6AA6937A669593AFC3863435F0BB8ACF095001CED3F31B842C`（72,415,664 B，2026-09-23 **第四轮**：fig4b 图注与图 S4 备注/索引**一次重出**同步；fig4b 现居**第 5 页**）。<br>**上一快照**：`1AED6DDA…302D2C`（72,415,480 B，fig4b 重渲染后，2026-09-23；另存 `.bak_caption_20260923`）。<br>**历史锚点**：`All_Figures_Complete_20260920.pptx` = 58 页（`48DD9180…`），保留在盘。 |
| 5 | **PPT 内嵌的是位图**：仅第 **1/2/3/15** 页为原生形状（旧记 1/2/3/**12**，因新增面板使原生页后移）；其余 **59/63** 页为整页 PNG，**不随源文件更新**，改图必须用绘图脚本重渲染后**重出 deck**（F14 的教训）。 |
| 6 | **字号门**：现役入稿图以 `--layout-dir .tmp_revision_20260923/active_layouts --figures-dir docs/paper_complete_review_20260920/figures` 复跑 `qa_layout.py` → **TOTAL PROBLEMS: 0**（图 1/2/3/S1，最小 **11.29 pt**）；`figure_font_gate.py --self-test` **4/4**。正文契约 Times New Roman 11 pt、图宽 17 cm（**2026-09-23 实读**：python-docx 对现役 docx 的 27 个 `inline_shapes` 宽度集合 = `{17.0 cm}`，含图 S4；旧记"图 S4 合并后按 16 cm 入稿"为扩版前时点值，见 §六 #13 与 §11.4 N-4）。旧记的 `figure_manifest.json` `minimumPrintPtAt17cm` = 11.294 pt 仍成立（同一换算）。 |
| 7 | **改稿纪律（必须）**：改源文件 → 跑 `build.py` → **复测**「**55 页 / 23 表 / 27 内嵌图 / 12 编号公式 / 152 数学对象 / 34 文献**（词数只作快照）」；图件改动 → 重跑 `qa_layout.py`（现役 layout，0 problem）+ `figure_font_gate.py --self-test`（4/4）；图件改动 → **重出 63 页 deck** 并同步页码索引。 |
| 8 | **冻结基线（不得改）**：冻结共同区域表 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`、扩展表 `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B`、`data/splits/*/manifest.json`、版式母本 `9DB99E60…`、**表 11 六列数值**（表注冻结已于 2026-09-23 由作者解除：仅**追加**"非排名 / 各方法原生协议"两处限定，既有表注文字与六列数值不变）。 |
| 9 | **规模口径**：页数/表数/图数/公式数/文献数是稳定口径；docx 的 SHA-256 只是"某一次构建的快照"（F21）。词数最近一次 = **19,434**（2026-09-23 第四轮 fig4b 图注/S4 备注收口后重出；旧值 19,394 为第三轮、19,253 为 fig4b 重渲染后、17,221 为扩版前）。 |
| 10 | **本轮窗口**：未跑实验、未用 GPU、未提交、未推送；全部条目分 **A–E 五组**，共 **70 条**（其中 6 条为"待拍板/纪律"性质）。 |

---

## 一、A 组：论文正文与表格（改 `manuscript.md` / `results.md` / `tables.json` / `figures.json` 图注）

| 编号 | 问题（一句话） | 证据（文件:行 / 产物） | **具体怎么改** | 负责人 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|---|---|---|
| A-01 | 图 2(c)、图 3(c) 占位过大、空白多（各占全图下部约三成/近四成） | `docs/论文与图件问题汇总_仅复核_20260921.md:26` | 压缩 (c) 高度、缩短解释并靠近相关模块；**不得**用装饰或重复公式填空；改 `scripts/paper_complete_review_20260920/figure_sources/build_methods.mjs` 的 (c) 面板排版 → 重渲染 `fig2_matching.png`、`fig3_constructions.png` | AI | 中 | 待做 | 与 A-19、A-21 同批（同一脚本） |
| A-02 | 无 "loss 随 epoch" 曲线可展示（冻结推理无目标域优化循环） | 同上 `:27`；`tables.json:110-113`（`0 target-trainable parameters`） | 正文写一句"不适用"并指向图 S4；**禁止**把"无训练"写成"零计算 / 零准备"（成体系说明见 A-06） | AI | 高 | 待做 | A-06 |
| A-03 | 替代图（S4）未比较"所有方法"的性能稳定性 | 同上 `:28`；`figures.json:86` | 正文区分"本文统计估计的数值稳定性（S4）"与"所有对比配置的性能稳定性"；后者若坚持要求，需先定共同指标 + 共同扰动（成本见 D 组登记表 A04） | AI | 中 | 待做 | — |
| A-04 | 机器/软件/输入/计时范围的可比性说明缺失（"输入不同"≠"没在同一台机器测"） | 同上 `:29`、`:62`（P05） | 在 §4.2.14 附近写一小段：硬件同（RTX 3060 Laptop）、软件同（PyTorch 2.0.0+cu118/CUDA 11.8）、输入分辨率与增强仍不同、计时范围与限制；引用 `05_baselines/SPEED_VRAM_BENCH.json` | AI | 高 | 待做 | — |
| A-05 | 协议解释篇幅挤占"匹配与权重发现"主线 | 同上 `:30` | 正文只留一小段协议说明 + 短图注；逐方法配置与完整记录放补充材料（与 A-13 同一批） | AI | 中 | 待做 | A-13 |
| A-06 | 缺一段成体系的"为何对比方法无需针对这类数据集训练" | 同上 `:377` 起（T12，中英段落**已成稿**）；`EXPERIMENT_GAP_ANALYSIS_20260922.md:45`（A03） | 把 T12 的中英段落落到方法节末或限制节；须区分"目标域不做梯度优化 / 预训练编码器仍带训练来源 / 参考库构建属准备计算" | AI | 高 | 待做（零 GPU） | 引用 A-14 的 A14 结论 |
| A-07 | 结果章节持续追加、主线被切碎；long paper 定位未落到结构 | 同上 `:339`（T10）、`:103`（F10） | ① `§4.2.8 Discussion` 后移为独立 Discussion（Results 之后、Conclusion 之前）；② Results 按四组重排：主效应与交互 / 验证与确认 / 敏感性与稳健性 / 资源与限制；③ 纯审计型小节压成一段 + 指向补充材料；**不删关键限制** | AI | 中 | 待做 | A-05 |
| A-08 | "六个方法都不需要训练"过宽（含继承检查点与预训练来源） | 同上 `:34`（P01） | 限定为"本文实际评估的六个配置在目标数据上不做梯度优化"；保留 C 分支检查点的 VisA 来源与 in-domain 说明；参考库/coreset 记为准备计算 | AI | 高 | 待做 | A-06 |
| A-09 | "视觉分支无超参数"不准确 | 同上 `:42`（P02） | 改为"参数冻结、无目标域梯度训练、采用固定实验配置"；正文已列的分辨率/保留层/支持预算 K/σ=4/DPAM/阈值均须保留 | AI | 中 | 待做 | A-06 |
| A-10 | 新比较说明把 S5 阶段计时写成"同口径端到端测量" | 同上 `:68`、`:70`（P06） | 保留 §4.2.14 的限定（阶段计时之和，含参考库工作，排除初始化/指标/写盘）；纠正 `docs/COMPARISON_PROTOCOL_JUSTIFICATION.md` 第八节该句；显存继续区分进程内 allocated peak 与设备级监测 | AI | 高 | 待做（该草案未入稿） | — |
| A-11 | 新比较说明草案有 5 条论据不能直接搬入论文 | 同上 `:74-84`（P07） | 逐条纠正：①"统一分辨率即不可复现的新方法"→ 过强；②"local128 与 official224 都是原论文配置"→ 不能都称 published native；③"输出是 patch 级与图像级不能共同重采样"→ 本文比较的是定位图；④"外部基线表统一用同一套配对 bootstrap"→ Table 11 是点汇总；⑤"骨干、匹配规则等全部相同"→ 须补"除正在操纵的因素外" | AI | 高 | 待做 | — |
| A-12 | 稳定性计划书一处数值逻辑矛盾（加密 N 网格却使最大值变小） | 同上 `:86`（P08）；`docs/REFERENCE_FIG_CONVERGENCE_PLAN.md` ~148 行 | 核实该段是否实际改了数据/计算/区间范围；**确认前不搬入论文**（不改任何产物） | 作者 + AI | 低 | 待核实 | — |
| A-13 | 表 11/12 未**逐方法**给出协议；SubspaceAD 用 256 而非官方 672 未披露 | 同上 `:174-178`（P10）；`tables.json:446`、`:548`；`05_baselines_ext_20260921/PREFLIGHT.json` | 表注或补充材料逐方法写：分辨率、画布/输入几何、是否旋转、参考库/coreset 构造；写清 SubspaceAD 256 与官方 few-shot 672 的偏离及原因（672 在 6 GB 卡 12 图 ≥15 min 未完成，峰值 5797/6144 MiB）；**不得**把 256 写成"官方配置" | AI | 高 | 待做（零 GPU） | A-05 |
| A-14 | 图像级指标未与像素级并列报告 | `EXPERIMENT_GAP_ANALYSIS_20260922.md:43`（A01）；正文唯一举例 `results.md:53` | 新增一张图像级并列表（image AUROC / image AP 点值），与像素级并列，配一句"图像级池化与像素排序回答不同问题"；**不得**声称图像级也有区间 | AI | 中 | 待做（零 GPU） | — |
| A-15 | seed/支持集方差的覆盖范围未写清 | 同上 `:49`（A07）；`tables.json:1135-1191` | 写明跨种子方差**只有 MPDD 与 BTAD**（8 seeds）；MVTec AD / VisA / KSDD2 无跨种子方差表；至少报已有 seed 条件的离散度 | AI | 中 | 待做（零 GPU） | — |
| A-16 | 图 S5 计时中 PatchCore 128 首轮离群未披露 | 同上 `:52`（A10） | 一句话披露首轮 30.527 s 与最终采用的重测 24.190 s，并指向 `…/_bench_speed_vram/recheck/`；**不得**把 min–max 当完整离散度、不得写成端到端 | AI | 中 | 待做（零 GPU） | — |
| A-17 | 区间只对 `pixel_ap` 计算这一口径未入稿 | 同上 `:507`（P13）、`:159`（A19） | 若表 A/表 B 入稿，表注须写明"区间仅针对 `pixel_ap`；`pixel_auroc` 只有宏平均点值" | AI | 中 | 待做 | B-03 / D-14 |
| A-18 | 旋转增强收益的概括忽略了例外 | `docs/论文与图件问题汇总…:101`（F08） | §4.2.7 把 "improves" 限定为具体数据集或"大多数测试数据集"；保留 MVTec AD 0.5643→0.5637 的例外 | AI | 中 | 待做 | — |
| A-19 | 图 2 类别下标 c 的正斜体不一致（逐符号残留） | 同上 `:104`（F11） | 逐符号检查（PPT 第 2 页该下标 XML 为 `i=0`、第 1 页为 `i=1`）；改 `build_methods.mjs` 的字面量后重渲染 → 重出 PPT/docx | AI | 低 | 待做 | A-01 |
| A-20 | 第二、第三贡献仍有邻近重叠 | 同上 `:102`（F09） | 第二点限定为"表示与匹配的交互**设计与定义**"，第三点明确为"绝对效用与匹配敏感性的**条件性实证发现**"；不得宣称又提出未经实现的新模块 | AI | 低 | 待做 | — |
| A-21 | 单字母模块/层/方法名不便阅读（外部评审 T09） | 同上 `:284-337`；方案 `docs/NAMING_MIGRATION_PLAN_20260922.md` | 温和版**已落**（Table 1/2 增 `Full name` 列 + 首现加粗 + 图注全称）；**整批改名（方案 A / B）待作者拍板**，执行顺序 S0–S9 与回退见方案文件；若执行则须同步 6–12 张图、PPT、docx | 作者 | 高 | 待拍板 | B-06、C-02 |

> **A 组纪律**：不得写 `SOTA` / "全面领先" / 排名；区间不重叠只能作描述；表 A/表 B 与表 11/12 **不得混排**；`L` 一律称 **independent matching**（F04 已修，勿回退为 local）。

---

## 二、B 组：图件（改图源脚本 / 重渲染 / 绑定登记）

| 编号 | 问题（一句话） | 证据 | **具体怎么改** | 负责人 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|---|---|---|
| B-01 | 36 张逐类别多方法对比图**未进正文**（外部评审⑥：检测结果图应放结果分析） | `论文与图件问题汇总…:98`（F05）；`EXPERIMENT_GAP…:47`（A05）；`figures.json` 无 multimethod 键 | 从 36 张中选 **2–3 张代表图**（跨数据集 + 跨缺陷类型，含 query、GT、各方法热图，**本文列与 GT 相邻**）放进 §4.2.6 末或 §4.2.7；写明选择规则与色标规则；其余留补充材料（PNG 已在盘，**不需 GPU、不得重出**） | AI | 高 | 待做（零 GPU） | A-07 |
| B-02 | "所有案例都有两种输出"过宽（附录逐类别无各方法轮廓） | `论文与图件问题汇总…:99`（F06）；`figures.json:34-44` | 正文**界定覆盖范围**（"两种输出"只对正文 5 案例成立）或声明为限制；是否补齐全部方法轮廓见 D-02 | AI | 中 | 待做（零 GPU） | D-02 |
| B-03 | 图 S6（协议敏感度）**是否入正文** | `论文与图件问题汇总…:539`；`FIGURE_BINDING.md §十`；**2026-09-23 实读**：python-docx 对现役 docx（`…20260923.docx`）`'Figure S6' in p.text` 命中 **4**（旧记"命中 0"为扩版前时点值） | **已闭环（S6 已入稿）**：`figures.json` 已含 S6 条目，5 条限制写入 `Supplementary Protocol Tables` 与 Table S1 表注（同口径 448 子集只覆盖 36/144、区间只 pixel_ap、不构成排名、杠杆数字是只读聚合、拉伸族不在子集内）；与 §7.1 #2 一致 | AI | 中 | 已闭环（入稿） | — |
| B-04 | 新 S4 图内重复出现总标题与长说明（与正式图注重复） | `论文与图件问题汇总…:96`（F03） | 论文插图用**无图内标题版**；带标题的"讲解版"另存不用于入稿 | AI | 中 | 待做 | 改动后须重出 PPT+docx |
| B-05 | 新 S4 符号与术语未沿用正文（`I_TRI`/`I_BAL` 文本式公式；`L` 被称 local） | 同上 `:97`（F04） | 按正文数学排版与术语表统一；`L` 称 **independent**，不得称 local | AI | 中 | 待做 | B-04 |
| B-06 | 若执行整批改名，6–12 张图需改图内标签并重渲染 | `NAMING_MIGRATION_PLAN_20260922.md:119-136`（§3.4） | 按 §3.4 清单改 `build_methods.mjs`、`plot_primary.py`、`plot_extra.py`、`plot_supplementary_figures.py`；**必须绕开 `C.*` 颜色命名空间**（`build_methods.mjs` 里 143 处 `C.xxx` 是颜色常量）；改后重跑字号门 | AI | 高 | 待拍板 | A-21 |
| B-07 | 图件字号/版面门禁要求（改标签后可能因折行失败） | `FIGURE_BINDING.md:74-88`；`NAMING_MIGRATION_PLAN…:136` | 任何图改动后必跑 `qa_layout.py`（`TOTAL PROBLEMS: 0`）与 `figure_font_gate.py --self-test`（4/4）；注意 2026-09-22 实测 fig2 有 **2 处**、figS1 有 **6 处** `TEXT-OVERFLOW`（保守折行估计，非可见裁切）需复核 | AI | 中 | 待做 | A-01、B-06 |
| B-08 | 生成物与溯源 JSON 内仍是旧绝对路径 | `FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md:158`（§6-8）；F19 未做项 | `fig7_multimethod_*.json`×16、`FIGURE_SLIDE_INDEX.json`、`figures/primary_sources.json` 的 `source` 绝对路径需**改生成器后重出**（本轮刻意未做——手改会与生成器失配） | 作者 | 低 | 待拍板 | C-01 |
| B-09 | **本表新发现**：`FIGURE_BINDING.md` 未登记图 S3 的第 5/6 页面板（`panel_interaction_cases_p3/p4`） | `图件与PPT页码索引.md:18-19`（PPT 第 18/19 页 = p3/p4）vs `FIGURE_BINDING.md §一`（S3 只列到 `_p2`）；`docs/paper_complete_review_20260920/figures/` 内确有 p3/p4，`docs/figures_reference_matching_20260914/` 内**无** | 补登记 §一/§四：写清 p3/p4 的生成脚本、冻结数据、门禁与为何两处目录不一致；核实是否需把 p3/p4 同步回 `figures_reference_matching_20260914/` | AI | 中 | 待做（本表新发现） | — |
| B-10 | **本表新发现·未核实**：T13 把 Fig 5 记为 "(a/b/c)" 三页，盘上只有两页 | `论文与图件问题汇总…:399-413`（`budget_category(a/b/c)`）vs `docs/paper_complete_review_20260920/figures/` 只有 `fig5a_budget_seed.png`、`fig5b_categories.png`；PPT 第 6/7 页也只对两页 | 核对 `figures.json` 的 `budget_category` 分页键与 PPT 第 6/7 页，统一记法（**未核实哪一方为准**） | AI | 低 | 未核实 | — |

> **已完成、勿重做（图件侧）**：F01（图2(b) 紫框已对齐 `build_methods.mjs:323`，`fig2` SHA **`5156E610A1041FB08640960ED202475E1DEA4CD5EC254A85610308B9576C58E6`**（2026-09-23 重渲染后盘上实测；旧记 `AB1EB3FD…` 已过期））、F02（图3(b) 权重措辞，`fig3` SHA **`3F309ADB57D294E740F0C11E5085248A2CBB854F0E4932734758CF3A9AEDE6FD`**（旧记 `57362409…` 已过期））、P04（S4 ±5% 参考带 vs 6.8%，首个 N=700，`figS4_bootstrap_convergence` SHA **`6AFA2E49D6BCA74486BE8C4795B668BF732D1491A7B2017D1F7917A81583C0BF`**（旧记 `C4D2D0A0…` 已过期））、图 S6 生成与门禁（`0C6F801C…`）、图 6/7 字号 11.5 pt 修复、图 S3 版面修正。**哈希刷新依据**见 `FIGURE_BINDING.md §11.4`（9 处几何由 900 → 1060 单元重排而重渲染）。

---

## 三、C 组：PPT（63 页 deck 与索引）

| 编号 | 问题（一句话） | 证据 | **具体怎么改** | 负责人 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|---|---|---|
| C-01 | deck 与论文必须同步；任何图改动后旧 deck 即过期 | `论文与图件问题汇总…:204-206`（F14 教训）；`FIGURE_BINDING.md:445-466`（§九）；`All_Figures_Complete_20260923.pptx`（`5C47F8FF…`，72,415,664 B）、`FIGURE_SLIDE_INDEX.json` 实读 **63 条** | 重出链：`node scripts/paper_complete_review_20260920/figure_sources/build_deck.mjs` → `assemble_deck.ps1` → `finalize.mjs`；重出后核对 **63 页 / 0 finding**（2026-09-23 第四轮实测），第 **23** 页＝收敛（v2 合页）、第 **24** 页＝稳定性。**口径刷新**：旧记"58 页 / 第 20–21 页"为扩版前时点值，勿再据此判断 | AI | 高 | 待做（每次图改动后必做） | A-01、A-19、B-04、B-06 |
| C-02 | 若执行 T09 整批改名，deck、主图母版与索引须一并重出 | `NAMING_MIGRATION_PLAN…:138-145`（§3.5） | 重出 deck（**现役 63 页** `All_Figures_Complete_20260923.pptx`；旧记的 58 页 `All_Figures_Complete_20260920.pptx` 为扩版前锚点）、`docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx`（图 1 图内文字），页码不变则只复核索引 | AI | 高 | 待拍板 | A-21 |
| C-03 | 页码索引须与 deck 一致 | `docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json`、`图件与PPT页码索引.md` | 每次重出后复跑并核对（2026-09-22 实测：重出后 `图件与PPT页码索引.md` 哈希未变，证此前手写同步与真实结果一致） | AI | 中 | 待做 | C-01 |
| C-04 | **可编辑性纪律**：deck 只有 4 页是原生形状 | `论文与图件问题汇总…:106` | 第 **1/2/3/15** 页可在 PowerPoint 直接改（**2026-09-23 校**：旧记 1/2/3/**12** 因新增面板使原生页后移）；其余 **59/63** 页为整页 PNG，改图**必须**用绘图脚本重渲染，不能指望在 PPT 里改数据 | 交接说明 | — | 纪律 | — |
| C-05 | deck 第 28–63 页＝36 张逐类别附录，与 B-01/B-02 的口径需同步 | `图件与PPT页码索引.md:28-63`；`FINAL_ACCEPTANCE…:250`（**2026-09-23 校**：旧记"第 23–58 页"为 58 页 deck 时点值，现役 63 页 deck 附录为第 28–63 页） | 若 B-01 选代表图入正文、B-02 界定"两种输出"，附录页说明与图注须同步声明覆盖范围与色标规则 | AI | 中 | 待做 | B-01、B-02 |
| C-06 | 两份同源 deck 现**已不同源**，易误用 | `FINAL_ACCEPTANCE…:128`；`PROJECT_CLEANUP_AUDIT_20260922.md:95-96` | **2026-09-23 校**：现役 deck = `All_Figures_Complete_20260923.pptx`（**63 页**，`5C47F8FF…`，72,415,664 B）；扩版前锚点 = `All_Figures_Complete_20260920.pptx`（58 页，`48DD9180…`，72,193,447 B）；更早存量 = `All_Figures_Finalized_20260920.pptx`（`6EBD92E9…`，71,604,011 B）仅作旧版锚点；重出时三者关系须写清或明确废弃旧份 | AI | 低 | 待做 | C-01 |

---

## 四、D 组：实验补充（哪些补、哪些不补、成本锚点）

### 4.1 A01–A23 逐条登记（完整，避免漏项；来源 `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md`）

| A 编号 | 主题 | 2026-09-23 状态 | 零 GPU？ | 成本锚点（实读外推） | 落地到本表 |
|---|---|---|---|---|---|
| A01 | 图像级指标未并列 | 仍缺 | **是** | 聚合脚本 + 1 表，CPU 分钟级 | A-14 |
| A02 | 表 11/12 逐方法协议（含 SubspaceAD 256↔672） | 主表仍缺（B 线已把协议写进子集表列名/表注/PREFLIGHT） | **是** | 写作 + 表注扩写，小时级 | A-13 |
| A03 | 为何对比方法无需目标域训练 | 仍缺（稿未落） | **是** | 一段（中英），小时级 | A-06 |
| A04 | 跨方法稳定性比较 | 不补（结论不变） | 否 | 1–3 h GPU/方法/条件；六方法两条件 ≈ 半天–1 天 | D-01 |
| A05 | 完整多方法对比图未进正文 | 仍缺 | **是** | 选图 + 图注，小时级 | B-01 |
| A06 | "两种输出"覆盖范围 | 仍缺（写作稿未落） | 部分 | 后处理补轮廓：小时级 GPU/CPU | B-02 / D-02 |
| A07 | 方差只覆盖 MPDD/BTAD | 仍缺（写作稿未落） | **是** | 写作版 CPU 分钟级；8-seed 扩展不补 | A-15 |
| A08 | full-pixel 无区间 | 不补 | 否 | >1 天 CPU/内存密集 | D-03 |
| A09 | 同机证据范围受限 | 不补 | 否 | 单方法全量 ≈5.5 h GPU/方法 | D-04 |
| A10 | S5 首轮离群未披露 | 仍缺 | **是** | 一句话，分钟级 | A-16 |
| A11 | 共享操作多条件消融 | 不补 | 否 | 数小时 GPU | D-05 |
| A12 | 权重最优性不成立 | 不补（已限定） | — | — | D-06 |
| A13 | 复现性：无最短路径 / 无权重哈希 | **2026-09-23 第四轮已核实不缺**：`docs/MODEL_WEIGHTS.md`（逐权重 SHA-256）与 `docs/REPRODUCE_TO_TABLES.md` **均在盘**（`Test-Path` = True），稿件 `manuscript.md:224` 已引用；P1-1…P1-7 的其余项状态见 E-08 | **是** | 文档已在盘；E-08 打包项另计 | E-07 / E-08 |
| A14 | AnomalyCLIP 检查点来源 | **已结案**（2026-09-23） | — | — | 第五节 |
| A15 | 与近期方法对照满足 3–4 个口径 | 已满足（不变） | — | — | D-12 |
| A16 | 统计口径已说明 | 已满足（不变） | — | — | 纪律 |
| A17 | 共同区域口径已写进正文 | 已满足（不变） | — | — | 纪律 |
| A18 | 统一几何子集只覆盖 36/144 单元 | 不补 | 否 | PatchCore@448 实测 52.4 min/36 单元 ⇒ 144 单元 ≈3.5 h GPU | D-07 |
| A19 | 区间只算 `pixel_ap` | 不补（登记） | **是**（可低成本补） | CPU 级（B=1000、stride-8，脚本已支持，未实测时长） | D-08 / A-17 |
| A20 | WinCLIP+/AnomalyCLIP 的 448 未跑 | 不补 | 否 | 代码级排除，需改实现并重验（可能数天级） | D-09 |
| A21 | SubspaceAD@448 仅 2 图冒烟 | 不补 | 否 | 排除依据是输入规则（方形拉伸），非显存/成本 | D-10 |
| A22 | 统一几何下 PatchCore 塌缩为一列 | 不补 | 否 | 同 A18（≈3.5 h GPU） | D-11 |
| A23 | 图 S6 未进正文 | 未入稿，登记待作者 | **是** | 写作 + 一次重建，分钟级 | B-03 |

### 4.2 需决策的实验项

| 编号 | 问题（一句话） | 证据 | **具体怎么改 / 决策内容** | 负责人 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|---|---|---|
| D-01 | 跨方法稳定性比较缺失（无"共同指标 × 共同扰动"） | `EXPERIMENT_GAP…:46`（A04） | **不补**：与本文"交互效应"主张无关，AI 辅助评审已接受用适用稳定性图替代并只要求说明对比标准；若外部评审坚持，须先定义纵/横轴再评估（成本见 4.1） | 作者 | 中 | 不补（结论不变） | A-03 |
| D-02 | 附录逐类别图无各方法预测轮廓 | 同上 `:48`（A06） | **部分补**：正文 5 案例已满足；附录按"两种输出"重界定覆盖范围（写作，低成本）；**是否**为全部方法补轮廓（阈值化后处理，小时级 GPU/CPU）由作者定 | 作者 | 中 | 待拍板 | B-02 |
| D-03 | full-pixel 无区间 | 同上 `:50`（A08）；`tables.json:722` | **不补**：已作为限制登记；补它不改变任何主结论方向 | — | 低 | 不补 | 纪律（E-13） |
| D-04 | 同机证据限 MPDD 三类别 / seed 0 / K=1,4；无 query-only 延迟分布 | 同上 `:51`（A09） | **不补**：保留为限制；**不得**改写为端到端 | — | 低 | 不补 | A-04 |
| D-05 | 共享操作只有单条件、无区间 | 同上 `:53`（A11） | **不补**：已在正文声明探索性且不作模块验证 | — | 低 | 不补 | — |
| D-06 | 无"全局最优权重"证据 | 同上 `:54`（A12） | **不补**：正文已限定 | — | 低 | 不补 | — |
| D-07 | 统一几何子集只覆盖 36/144 单元 | 同上 `:158`（A18） | **不补**：子集定位本身已写进表注与 `HARMONISED_SUMMARY.json`；补满只提高分辨率、不改变结论 | — | 中 | 不补 | D-14 |
| D-08 | 子集表区间只对 `pixel_ap` | 同上 `:159`（A19）；`METHOD_COMPARISON_HANDOFF…:178` | **默认不补**（`pixel_auroc` 点值已在表内）；若作者要求，复用同一 stride-8 抽样流改度量后复跑 `harmonised_common_region.py --mode eval`（CPU 级） | 作者 | 低 | 待拍板 | D-14 |
| D-09 | WinCLIP+/AnomalyCLIP 的 448 版本未跑 | 同上 `:160`（A20） | **不补**：属代码级排除（检查点绑 240、变换与 37×37 网格绑 518）；改实现会破坏"各自原生配置"的可比性 | — | 低 | 不补 | — |
| D-10 | SubspaceAD@448 仅 2 图冒烟 | 同上 `:161`（A21） | **不补**：排除理由是输入规则（方形拉伸）；跑全量也不会让它进子集 | — | 低 | 不补 | — |
| D-11 | 统一几何下 PatchCore 塌缩为一列 | 同上 `:162`（A22） | **不补**：协议敏感度已由**图 S6** 与 `protocol_leverage.json`（0.1000 / 0.0265 / 3.8× / 33.3%）承担 | — | 低 | 不补 | B-03 |
| D-12 | P2 训练类基线（AdaptCLIP / PromptAD / EfficientAD / GLASS / UniVAD） | `论文与图件问题汇总…:157`（T07）；`BASELINE_EXPANSION_PLAN_20260921.md:118-133` | **已结案不做**：外部评审口径是"近两三年 3–4 个较先进方法"，现已含 AnomalyCLIP(ICLR 2024)、AnomalyDINO(2024)、WinCLIP+(NeurIPS 2023)、SubspaceAD(2025) + PatchCore + 本文 A1 两列；若日后要做，AdaptCLIP ≈8–12 h GPU（机制已就绪，可单方法/单单元重跑） | — | — | 已结案 | — |
| D-13 | 文献参照表（T08 / P0）是否纳入 | 同上 `:162`（T08）；`BASELINE_EXPANSION_PLAN…:95-103` | **降级为可选、零重跑**：只引原论文已发表数字，单列成表、与实测表**分栏不混排**；须补 4 个引用键（`adaptclip`/`remp_ad`/`efficientad`/`glass`）到 `references.json` | 作者 | 低 | 待拍板 | — |
| D-14 | 表 A / 表 B（统一 448 子集）是否入正文 | `FINAL_ACCEPTANCE…:169-212`；`METHOD_COMPARISON_HANDOFF…:10-76` | 若入稿：须写明 **7 条限制**（1/4 子集、统一协议 X = 短边 448、不构成排名、旧六列冻结未改、PatchCore 只一列、区域取冻结共同区域、复现边界）+ 区间只 `pixel_ap`；入稿后复测页数/表数 | 作者 | 中 | 待拍板 | A-17 |

> **成本锚点（外推用，实读）**：A1 J/L 同机 197.118 s / 195.300 s（含参考准备，峰值 2376.8 MiB）；AnomalyDINO canvas / +rotation 30.959 s / 78.863 s；PatchCore 128 / 224 24.190 s / 36.931 s；单方法整段墙钟 A1_J 828 s、A1_L 826 s、AnomalyDINO 153 s、+rot 343 s、PC128 224 s、PC224 299 s；外部扩展冒烟 SubspaceAD@256 0.4168 s/img、WinCLIP+ 0.18 s/img、AnomalyCLIP zs 0.69 s/img；外部三族合计 144/144 + 144/144 + 36/36、零失败零 OOM、GPU 合计约 185 min；PatchCore@448 = 52.4 min/36 单元（819.8/396.8/900.2/1027.2 s）。

---

## 五、E 组：元数据与交付

| 编号 | 问题（一句话） | 证据 | **具体怎么改** | 负责人 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|---|---|---|
| E-01 | 作者/单位/通讯作者缺失 | `docs/SUBMISSION_METADATA.md:15-17` | 填 `manuscript.md:3/5/7` 的 `[[AUTHORS]]`/`[[AFFILIATIONS]]`/`[[CORRESPONDING_AUTHOR]]`；ORCID 在投稿系统逐条填 | 作者 | 高 | 待作者 | — |
| E-02 | 资助信息缺失 | 同上 `:19` | 填 `manuscript.md:226` 的 `[[FUNDING]]`，或写 "This research received no external funding." | 作者 | 高 | 待作者 | — |
| E-03 | COI 声明（已填，需作者过目） | 同上 `:20`、`:49` | 现为 "The authors declare no competing interests."；若作者不能确认无商业/财务关联，改为"待作者确认" | 作者 | 中 | 已填待过目 | — |
| E-04 | 伦理声明（已填） | 同上 `:21` | 现为 "Not applicable; the study analyses industrial image data only…"；目标期刊有固定措辞则替换 | 作者 | 低 | 已填 | — |
| E-05 | 仓库 URL 已入稿，**归档 DOI 未取得** | `论文与图件问题汇总…:450-453`（T11/T15）；`SUBMISSION_METADATA.md:22,27` | 摘要末句与 Data and Code Availability 已含 `https://github.com/USEU117/reference-matching-interaction-ad`（全文仅此两处）；取得 Zenodo/等效 DOI 后回填 `manuscript.md:224`，**不得**再保留"no repository URL"式表述 | 作者 | 高 | URL 已入稿 / DOI 待作者 | — |
| E-06 | 许可：代码三段已补；数据集许可明细待定 | `AUTHORITATIVE_SOURCE_DIFF_20260921.md:176`；`SUBMISSION_METADATA.md:24` | 许可三段（MIT / 派生产物同许可 / 数据集许可独立）已入正文；是否补逐数据集许可明细（CC BY-NC-SA 4.0 等）由作者定 | 作者 | 低 | 已补（明细待拍板） | — |
| E-07 | 缺权重清单与"从零到表"最短路径 | `EXPERIMENT_GAP…:55`（A13）；`FINAL_ACCEPTANCE…:426-431`；**2026-09-23 第四轮实测** | **已落实（原登记为过期）**：`docs/MODEL_WEIGHTS.md` **在盘且达标**（逐权重 目标路径 / 字节数 / **SHA-256** / 获取方式 + 46 项实读的机器可读 `sha  bytes  path` 块），`docs/REPRODUCE_TO_TABLES.md` **在盘**（"从零到表"最短路径）；二者由 `scripts/paper_complete_review_20260920/finish_documentation23.py:31` 生成，稿件 `manuscript.md:224` 已引用（"checkpoint paths and hashes are recorded in `docs/MODEL_WEIGHTS.md`"） | AI | 高 | **已核实（在盘且达标）** | E-08 |
| E-08 | 复现包重打（P1-1…P1-7 **全部未执行**） | `REMEDIATION_PLAN_20260920.md:173-180` | ①补 `src/`+`configs/`+`methods/`（方案 (a)/(b) 需作者定）；②`requirements_repro.txt` 加 CUDA index 段（是否产出 lock 由作者定）；③`docs/MODEL_WEIGHTS.md`；④生成 `SOURCE_COMMIT.txt` + `SHA256SUMS`；⑤补 `paper_evidence_closeout_20260914/` 台账；⑥补 `seeds_extension_20260917/p0_support/`；⑦回填 `VD1_MANIFEST.json` 的 `manifest_sha256`（会改既有文件，需作者同意） | AI + 作者 | 高 | 待做 | E-07、P0 措辞定稿（已完成） |
| E-09 | F21 `build.py` 不是字节级可复现 | `论文与图件问题汇总…:520-525`；`FINAL_ACCEPTANCE…:151` | 实测连跑三次 docx SHA 三个值（内容度量一致）。若要"可复现校验值"：给 `build.py` 固定 docProps/时间戳，或改为对**内容**而非字节做校验；在此之前 docx SHA 只当快照 | 作者 | 中 | 待拍板 | — |
| E-10 | F22 自检门禁 2/69 失败（退出码 1） | 同上 `:527-534`；`ISSUE_REGISTER…:45` | ①`docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx` 不在盘（重建源 `.tmp_outline_20260914/` 在盘）→ 重建/放回，或把该检查点改为"缺失即跳过并记 caveat"；②冻结快照 3 处漂移（`_smoke` 下 2 个 `.npz` 缺失 + `REPORT_CN.md` 仅 mtime 变化）→ 是否把 `_smoke` 从冻结清单豁免。**注意**：该脚本会就地改写 `experiments/**/{SELFCHECK,READONLY_PROOF}.json`，运行后须 `git checkout --` 还原 | 作者 | 中 | 待拍板 | — |
| E-11 | 包内 `SHA256SUMS` 仍有 2 处既有漂移 | `FINAL_ACCEPTANCE…:160`（§6-10） | `experiments/…/seeds_extension_20260917/VD1_MANIFEST.json`（填值后未刷新清单）与 `requirements_lock.txt`；本轮范围外未动，是否修由作者定 | 作者 | 低 | 待拍板 | E-08 |
| E-12 | 仍写着"来源未核实/本项目重训"的 2 处（**红线区**） | `FINAL_ACCEPTANCE…:161`（§6-11） | ①`05_baselines_ext_20260921/PREFLIGHT.json` 的 `checkpoint_rule_and_caveat.caveat`；②`scripts/baseline_expansion_20260921/ext_run_anomalyclip.py:25-27` 的 docstring。二者是 09-21 审计留痕（证据字段/代码注释）；**A14 已结案**，结论以 `docs/reproduction_notes.md:13-23` 为准；是否改写待作者 | 作者 | 低 | 待拍板（红线） | — |
| E-13 | **冻结值清单**（不得改动） | `FINAL_ACCEPTANCE…:328-341` | 冻结共同区域表 `3C83AB00…`；扩展表 `1C770129…`；`data/splits/{btad,mpdd,mvtec,visa}/manifest.json`（4/4 与 `manifest.sha256` 匹配）；版式母本 `9DB99E60…`；表 11 六列数值与表注；图 1–8、S1–S5 的 PNG/PDF 与 PPT 内嵌位图（除 F01/F02/P04/F14 这批已获批改动）；`experiments/**` 证据字段；`data/**`、`LICENSE`、`requirements_repro.txt`、`figure_sources/**` 科学内容 | 交接纪律 | — | 纪律 | — |
| E-14 | 本地 `main` 有 2 个未推送提交 | `ISSUE_REGISTER_20260920.md:43` | 2026-09-23 实测 `main...origin/main [ahead 2]`（HEAD `4d7f640`；`e61d039`、`4d7f640` 未推送）；按要求**不提交、不推送**，是否推送由作者定 | 作者 | 低 | 待拍板 | — |
| E-15 | 提交信息层含身份串的 4 条提交（2 条含旧仓库名） | `SCI_STRING_AUDIT_20260922.md:143-183` | 改写需 `git filter-repo` + **强推**（会改写 `1b360bf` 之后全部提交 SHA）→ **须作者书面授权**；方案与命令见该文件 §4.3（其中 `cfcaca1` 为本地悬空提交、未公开，无需重写） | 作者 | 低 | 待拍板 | — |
| E-16 | 生成物绝对路径与约 51 处历史旧路径引用未清 | `SCI_STRING_AUDIT…:284`（§7）；`PROJECT_CLEANUP_AUDIT_20260922.md:483` | 生成物侧见 B-08；历史引用分布在 `docs/specs/**`、`.trae/**`、`experiments/**` 状态记录、脚本注释、归档区互引；批量改写会触及历史文档正文与脚本行为 → 待作者决定是否单开一轮 | 作者 | 低 | 待拍板 | B-08 |
| E-17 | `ISSUE_REGISTER` R-12（`dist/` 未跟踪且未被忽略）现象已不成立 | `ISSUE_REGISTER…:61`；`PROJECT_CLEANUP_AUDIT…:212` | `.gitignore:73` 现为 `dist/`；按"原文不改写 + 刷新行"体例，建议在 `ISSUE_REGISTER` §〇ter 补一行 R-12 刷新（本轮未改） | AI | 低 | 待补登记 | — |
| E-18 | 清理审计第二轮改动未提交 | `PROJECT_CLEANUP_AUDIT_20260922.md:543-561`（§E.8） | 待提交：3 个 `M`（`docs/README.md`、`docs/ARTIFACT_INDEX.md`、本审计报告）+ 158 条 `R`（归档重命名）+ 1 个新文件（`docs/archive_pre202609/README_ARCHIVE.md`）；建议提交信息见 §E.8；是否连 `.trae/` 一并纳入由作者定。**第一轮 42 文件删除已由作者提交 `ff6db31`** | 作者 | 中 | 待拍板 | — |
| E-19 | 版式母本被 `*.docx` 忽略，干净克隆无法复现终稿（R-22 / F17） | `论文与图件问题汇总…:248-253`（F17）；`REMEDIATION_PLAN_20260920.md:14`；`ISSUE_REGISTER…:41` | 版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx`（`9DB99E60…`）是**不可由源重建的二进制输入**；建议移出 `*.docx` 忽略范围（或保留受控副本）并登记进 `docs/ARTIFACT_INDEX.md` | 作者 | 中 | 待拍板 | — |
| E-20 | **现役 docx 是否留在 git 还是改走 Release** | **2026-09-23 收尾轮已入库**：`.gitignore:83` 加白名单 `!docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`，`git status` 显示 `??`（19,220,478 B，`9B3E15F5…`）；旧 docx 与 `.bak_*` 仍被忽略 | 留 git（现状：克隆即得权威稿）/ 移出转 Release（需改白名单）。记录见 `docs/GITHUB_COMPLIANCE_AUDIT_20260923.md` §4 | 作者 | 中 | 待拍板 | E-19 |
| E-21 | **是否启用 Git LFS** | tracked 16,105 文件 / 3,308,895,330 B（≈3.31 GB）；`.git` ≈ 6.62 GiB；`>50 MB` 的 tracked 文件 **3** 个（三个 pptx：69.1 / 68.8 / 68.3 MiB），无 `>100 MB` 文件；现 **10** 个 tag | 启用会改写历史对象、成本较高；是否启用由作者定 | 作者 | 中 | 待拍板 | E-20 |
| E-22 | **是否出 PDF** | 现役交付只有 docx（`…20260923.docx`）；投稿系统与长期归档常需 PDF | 是否出 PDF 由作者定（会新增一个二进制产物，是否入库需一并定） | 作者 | 低 | 待拍板 | — |
| E-23 | **是否打 `v1.0.0`** | `git tag` = **10** 个，最新 `reference-figures-20260920`（2026-09-20，**早于 09-23 扩版/收口**）；扩版后无新 tag | 若打 `v1.0.0`，须与 `SOURCE_COMMIT.txt` 对齐 | 作者 | 中 | 待拍板 | E-20 |
| E-24 | **`experiments/**` 与 `submission_repro_20260827/logs` 内本机绝对路径是否脱敏** | `git grep -l "My_github"` 命中 **1,503** 个 tracked 文件（含上述两处） | 两处属**红线/哈希登记**区：改动会使 `SHA256SUMS` / `VERSIONED_EVIDENCE.sha256` 失效；须作者书面决定是否单开一轮 | 作者 | 中 | 待拍板 | E-16 |

---

## 六、"已完成、请勿重做"清单（含凭据，防止下游重复劳动或误改）

| # | 已闭环项 | 凭据（提交号 / 文件 / 实测值） |
|---|---|---|
| 1 | F01 图2(b) 紫框与填色对齐 | `scripts/paper_complete_review_20260920/figure_sources/build_methods.mjs:323` = `addRect(slide, "f2-j-shared-highlight", 113 + 2 * 42, …)`（**2026-09-23 实读行号即 323**）；入稿副本 `docs/paper_complete_review_20260920/figures/fig2_matching.png` SHA **`5156E610A1041FB08640960ED202475E1DEA4CD5EC254A85610308B9576C58E6`**（252,820 B，2026-09-23 重渲染后盘上实测；旧记 `AB1EB3FD…` 已过期）。像素复核：紫框 `x∈[195.5,240.0]` 与填色格 `x∈[201.0,237.0]` 同列 100% 重合（清单 §5.4 A-07） |
| 2 | F02 图3(b)"只有 B 权重变化"措辞更正（图内 + 图注 + 正文） | `build_methods.mjs:**432**`（= `"Only the weight split changes: B 1/2→2/3, C 1/2→1/3."`；**2026-09-23 实读，行号由旧记的 430 校正为 432**）、`figure_sources/figures.json` 的 `constructions.caption`、`manuscript.md:111`；入稿副本 `docs/paper_complete_review_20260920/figures/fig3_constructions.png` SHA **`3F309ADB57D294E740F0C11E5085248A2CBB854F0E4932734758CF3A9AEDE6FD`**（253,976 B；旧记 `57362409…` 已过期） |
| 3 | P04 图 S4 的 ±5% 参考带与实测 6.8% 分开表述 | `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` 新增 `REFERENCE_BAND=0.05` 与 `first_settled_n`；**5% 判据下实测首个 N = 700**；JSON `headline.first_n_inside_5pct_reference_band = 700`；`max_relative_width_deviation_N_ge_500 = 0.067669…` 未改；门禁 61 个 text artist 全 11.50 pt。**入稿副本**（`docs/paper_complete_review_20260920/figures/figS4_bootstrap_convergence.png`）SHA **`6AFA2E49D6BCA74486BE8C4795B668BF732D1491A7B2017D1F7917A81583C0BF`**（539,436 B）；参考目录旧副本 `docs/figures_reference_matching_20260914/figS4_bootstrap_convergence.png` = `C4D2D0A0…`（857,202 B，已被入稿副本取代） |
| 4 | F14 PPT 已重出（**时点：58 页**，第 20/21 页＝收敛 v2 / 稳定性） | `All_Figures_Complete_20260920.pptx` SHA `48DD91800B714331…`（72,193,447 B，58 页，0 finding）；索引 `FIGURE_SLIDE_INDEX.json` `A943E389…`；`图件与PPT页码索引.md` 复跑后未变。**2026-09-23 校**：现役 deck 已是 **63 页** `All_Figures_Complete_20260923.pptx`（`5C47F8FF…`，第 23/24 页＝图 S4 两页），本条为扩版前时点值 |
| 5 | F15 三份同源 PPTX 已删其一；`.bak_20260922` 亦已删 | 原三份字节相同（71,604,011 B / `6EBD92E9…`）；删 `Main_Figure_Editable_20260920.pptx` 释放 ≈68.3 MB；`.bak_20260922` 于 09-22 清理删除（与 `All_Figures_Finalized_20260920.pptx` 逐字节相同） |
| 6 | F17 权威 docx 与版式母本从 git 对象逐字节恢复 | `18694B90…` / `9DB99E60…` 与文档所记完全一致（成因：`a08dc46` 把 `*.docx` 加入 `.gitignore`） |
| 7 | T11 摘要末句 GitHub URL 入稿 | `manuscript.md:11`；重建后 docx SHA `68477175EC6C3287…`；Word COM 47 页 / 17,200 词 |
| 8 | T15 摘要 URL 与 Data and Code Availability 矛盾消除 | `manuscript.md:224` 现写 "…The public repository holding the code and the reproduction materials is https://github.com/USEU117/reference-matching-interaction-ad; a permanent archive DOI … has not yet been established."；全文仅两处出现该 URL、**无相反表述** |
| 9 | T16 命名温和版（T09 的 2a）已落地 | Table 1/2 各增 `Full name` 列（`tables.json` 的 `design`/`models` 两键）+ 正文首现加粗（token `[C,J,L,B,B,S,C,D,A1,DUP,TRI,BAL,E1,E2,E3]`）+ 图注首现全称；**未改任何字母、未重渲染任何图、PPT 未重出** |
| 10 | A14 AnomalyCLIP 检查点来源**结案**（纠正"本项目自训"错说） | 第一手 `docs/reproduction_notes.md:13-23`（2026-07-25，与归档下载同日）：检查点随上游源码归档（commit `3911738c…`，ZIP SHA256 `533ED87B…`）；30 个 `epoch_*.pth` mtime 全为 `2025-07-08 03:59:38`，本项目目录 2026-07-24 才建立 ⇒ **非本项目训练**；正确口径＝"prompt learner 在辅助域按上游配方训练、目标域零样本"；已逐处纠正 `dist/…/weights/README.md`、`REPRODUCIBILITY_PACKAGE.md`（含包内副本）、`BASELINE_EXPANSION_PLAN_20260921.md`、`EXPERIMENT_GAP_ANALYSIS_20260922.md`、汇总 P11 等 |
| 11 | T17 → A14 后 Table 12 协议列与表注改为**准确**表述 | 协议列 = `native, zero-shot on the target domain (upstream auxiliary-domain-trained prompt learner)`；表注删除"provenance recorded in … PREFLIGHT.json"；旧含糊写法命中 **0**、新表述命中 **3**；Table 12 **9 行数值一个未动** |
| 12 | T18 / F18 B 线（统一输入几何子集）完成并过门禁 | `experiments/…/05_baselines_harmonised_20260922/**`（表 A 180 行、表 B、`HARMONISED_SUMMARY.json`、`protocol_leverage.json`、`PREFLIGHT.json`）+ `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`；协议杠杆 **0.1000**（PatchCore 自身两配置，144 单元）> 家族差异 **0.0265**，**3.8 倍**；仅切 PatchCore 配置使胜负翻转 **48/144 = 33.3%**；图 S6 四道门禁（102 artists 全 11.50 pt、0 互压/0 压图/0 出页）、PNG 重渲染逐字节相同（`0C6F801C…`）；复用 4 列与冻结表 max_abs_delta = **0.0** |
| 13 | 图 S4 合并入 Word（v2 第 1 页 + stability 第 2 页，**时点宽 16 cm**） | 数值零改动（复用已渲染 PNG）；重复的 `figS4_bootstrap_stability_part2` 移入 `figures/superseded/`；v2 第 1 页 PNG `6A542164…`（后经 P04 修订为 `C4D2D0A0…`，再经入稿重渲染为 `6AFA2E49…`）。**2026-09-23 校**：现役 docx 内图 S4 两页与其余 25 图宽度同为 **17.0 cm**（16 cm 为 09-21 时点值） |
| 14 | 扩展表入正文 Table 12（原 12–19 顺延为 13–20，全文 20 表） | `05_baselines_ext_20260921/baseline_common_region_ext.csv` 1188 行（= 冻结 864 逐行照抄 + 新 324），SHA `1C770129…`；表 11 六列数值与表注**一字未改** |
| 15 | 权威稿重建（**时点值 2026-09-22：47 页 / 20 表 / 22 内嵌图 / 12 公式 / 142 数学对象 / 34 文献 / 17,221 词**） | 该时点 docx = `…Reference_Matching_Complete_English_20260920.docx` SHA `DDB6602E1AA792C60743D4354FE90BFFE923E4BFF796CEB36971BA2528E8353B`（27,725,875 B，**2026-09-23 实读仍在盘**，作扩版前锚点）；备份 `.bak_20260923`、`.bak_20260922`、`.bak_authoritative_20260921`、`.bak_before_T11_20260922` 均在盘。**2026-09-23 时点值（现役）**：`…20260923.docx` = **55 页 / 23 表 / 27 内嵌图 / 12 公式 / 152 数学对象 / 34 文献 / 19,434 词**（`9B3E15F5…`，19,220,478 B） |
| 16 | F19 旧绝对路径在权威源与生成物中中性化 | `figures.json` 14 处 `path`/`parts` + 2 个生成 md 共 12 处 → 仓库相对路径；改后三文件 grep `My_github` = 0。**未做**：生成物溯源 JSON（见 B-08） |
| 17 | F20 禁忌词与"外部指导痕迹"复扫清零 | 改前 `docs/**` + `README.md` 共 **9 处 / 2 文件** → 改后 **0**；六个重点文件全部为 0 |
| 18 | T14 仓库改名完成 | `git remote -v` = `https://github.com/USEU117/reference-matching-interaction-ad.git`；旧物理目录名现为 junction（`docs/RENAME_LOG_20260922.txt`，9/9 检查 PASS） |
| 19 | R-05 / R-06 / R-07（措辞）/ R-08 / R-09 / R-10 已处置 | 新增根 `pytest.ini`（排除 `test_wave2a_probes.py`）→ `pytest tests -q` **260 passed / 0 failed**；`141/141` 已标注为 2026-09-02 历史快照；`true null` / `true zero effect` / `essentially zero on BTAD` 结论性文本清零；`ACCEPTANCE_20260920.md` 改为 `checks=71, passed=71`；`ARTIFACT_INDEX.md` 工作流 B 行更新 |
| 20 | R-11（推送部分，09-22 时点）/ R-12 已解决 | 09-22 实测 `origin/main..HEAD = 0`（HEAD `85d3207`）；`.gitignore:73` 现为 `dist/`。（09-23 又出现 2 个未推送提交 → E-14） |
| 21 | P0（一致性与措辞）全部执行完毕 | 勾选清单见 `REMEDIATION_PLAN_20260920.md`；P0 的 docx 重出与 `tables 18 / figures 8 / equations 12 / refs 34` 属**已冻结旧链**（`scripts/manuscript_build_20260914/`），与权威链并存不互斥 |
| 22 | P2-2 测试 collection 失败已处置 | 新增 `pytest.ini` 显式排除该模块；实跑 260 passed / 0 failed；`run_wave2a_build_reliability.py` 的 import **未改**（冻结探针） |
| 23 | 项目清理第一轮（42 文件 / 403.56 MiB）已提交 | 提交 `ff6db31`（"clean up duplicates and bring the status documents up to date"）；第二轮（19 + 8 文件 / 757.55 MiB + 158 条 archive rename）**未提交** → E-18 |
| 24 | `docs/figures_package_20260917/` 已归档、`docs/archive_pre202609/` 已建立 | `git mv` 158 条 rename、无 `D`；入口 `docs/archive_pre202609/README_ARCHIVE.md` |
| 25 | `sci` 字符串中性化（人工撰写面） | 路径层 13 项（3 项身份泄露已 `git mv`）；A 类人工可读面清零；B 类 67 处 → **8 处**（3 个哈希登记文档按规则保留）；提交信息层见 E-15 |
| 26 | 图 6/7 字号修复（7.1–9.3 pt → 11.50 pt）、图 S3 版面修正、图 S4 v2 改版、图 S6 编号无冲突登记 | `FIGURE_BINDING.md` §二/§四/§七/§十；`figure_font_gate.py --self-test` 4/4 |
| 27 | 外部方法家族 2 → **5**（PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AnomalyCLIP 零样本） | 三族 144/144 + 144/144 + 36/36，零失败零 OOM，GPU 合计约 185 min；"约 10 个方法"已由 F07/T07 更正为**举例非固定缺口** |
| 28 | **2026-09-23 呈现纪律补句**（A-14 / A-19 / C-02 / C-03） | `tables.json`：Table 4/5/8 表注补 `not a claim of best performance`（Table 1 同措辞，三处）；Table 11 表注**追加**"各配置按自身原生协议（分辨率/画布/旋转/参考库构造），本表提供背景而非排名"。`manuscript.md` §4.1.2 补"对照集合以正式基线清单为准，数量本身不是目标，约十个不是硬指标"。**六列数值与既有表注语义未改**（`baselines`/`baselines_ext` 的 `rows`/`headers` 与 `HEAD` 逐项 `identical=True`） |
| 29 | **2026-09-23 Table 11 表注冻结解除 + 语义边界回正** | `finish_text_revision23.py:21` 的 `if k=='baselines':continue` 冻结已删除（改为登记式注释）；VisA 边界改回**明确域内**（`manuscript.md:172`：`VisA remains in-domain frozen validation … does not provide unseen-domain evidence`）；`results.md:142` 的越界表述 `neither the sign nor the interval separation … depends on that constant` → `the zero-exclusion judgement of the interaction is preserved under that constant` |
| 30 | **2026-09-23 现役 1280×1060 版面门禁复跑 + 未引用媒体清理 + 孤儿删除 + 重建** | `qa_layout.py --layout-dir .tmp_revision_20260923/active_layouts --figures-dir docs/paper_complete_review_20260920/figures` → **TOTAL PROBLEMS: 0**（图 1 首轮 4 处，已按"只改盒几何、不改阈值、实测光栅中性"修复；修前/修后 PNG SHA 均为 `C179C22E…`）；`build.py` 新增 package 级未引用媒体清理（**pruned 8 个**，`word/media/*` 35 → 27，docx 32.5 MB → 19.17 MB）；孤儿 `figures/figS1_encoders_geometry.png` 登记后删除（见 `FIGURE_BINDING.md §11.5`）；重建后 **55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 34 文献 / 19,253 词** |
| 31 | **2026-09-23 收尾轮：图 1 生成器纳入版控** | 整链由 gitignored 的 `.tmp_figure_revision_20260920/build_main.mjs` 迁入 **`scripts/main_figure_20260920/`**（`build_main.mjs` → `patch_math.py` → `finalize_figure.mjs` → `export_slide.ps1` + `run_pipeline.ps1`）；输出改指现役图件目录；脚本内不再含禁忌词目录名。**复现命令** `powershell -File scripts/main_figure_20260920/run_pipeline.ps1`；实测输出 `fig1_framework.png` = `C7618E16B4CED2288D7A0DC392BE5578A3AB12BD3C4E210780B66B6D4941525A`（728,505 B，2560 × 2120），与入稿图**逐字节/逐像素相同**。登记见 `FIGURE_BINDING.md` §11.7、`ARTIFACT_INDEX.md` §八 8.1；旧目录**只登记、不删除** |
| 32 | **2026-09-23 收尾轮：A-07 / A-17 像素复核 + A-27 自检 + K-12 图源逐文件复审** | A-07：紫框 `x ∈ [391, 480] px`（版面 `[195.5, 240.0]`）与填色格 `x ∈ [402, 474] px`（版面 `[201.0, 237.0]`）**同列且 100% 重合**，框跨两行 ⇒ **通过**。A-17：deck 第 23/24 页内嵌位图与 `figS4_bootstrap_convergence/stability.png` **逐字节 + 逐像素相同**（`6AFA2E49…`/`B06F095A…`），且均在 docx `word/media/` ⇒ **通过**。A-27：`selfcheck.py` 实跑 **67/69**（2 项已登记既有失败），跑后**逐字节还原**、哈希与运行前一致、`git status -- experiments data` 为空 ⇒ **通过**。K-12：`build_methods.mjs` / `plot_extra.py` / `plot_supplementary_figures.py` / `build_figS4_*` 仅标签/几何/样式（**未触碰数值**）；**`plot_primary.py` 属数据来源变更** → 见 **§7.3 N-1**。三冻结哈希与 `data/splits/*` 全程不变 |
| 33 | **2026-09-23 续：N-1 结清（fig4b 重渲染 = 选项 (a)）+ 全图数值一致性扫查 + 清单新增 A-28 + 重出 deck/重建 docx** | **① fig4b 重渲染**：`plot_primary.py` 的 `fig4b` 段改按**现行表 8 行**组织（`(4)` 共享四条件在上、`(12)` 更宽口径在下，y 刻度如实标 `S (4)`…`E3 (12)`）→ 新 PNG `FA2DE6E4EF31C65ECCFF509EEBCD7C86CBEA1209F338DDD5C72F71863A7FCC13`（2342 × 2450，110 个 text artist **全 11.0 pt**，四道 `figure_font_gate` 全过）；脚本内**不再引用** `.tmp_figure_revision_20260920/tables.json`；`fig4a/5a/5b` 重渲染与盘上**逐字节相同**。**② 逐值核对**：图内 32 个点值/区间 vs docx encoders 表（**= Table 16**；N-1 里写的"表 15"为旧编号）**全部一致**。**③ 全图扫查**（fig4a↔T6、fig8↔T13、fig5a(b)↔T17、figS4↔T15/T14、figS6↔T11/T12）**均一致**；唯一登记项 = figS4 的 KSDD2 端点为 bootstrap 均值（+0.544/+0.344）而 T14 "Point" 为条件平均观测差（+0.539/+0.343）属**定义量不同**，未擅改。**④ 清单新增 A-28**（图内数值↔同文表格数值一致性）并给出首轮判定。**⑤ 重出 deck**：63 页，SHA `1AED6DDA…302D2C`（72,415,480 B），fig4b 在第 5 页且内嵌位图与盘上**逐字节相同**；索引 63 条 / 页码 md 63 行 / 原生页 `[1,2,3,15]`。**⑥ 重建 docx**：55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 12 公式 / 34 文献 / **19,253 词**；SHA `5C5DA8D5…F4A89`（19,220,095 B）；`fig4b` 内嵌 = `word/media/image13.png`。**⑦ 门禁**：`qa_layout.py` **0 problem**、`figure_font_gate --self-test` **4/4**、`pytest tests -q` **260 passed**。**红线**：冻结表 `3C83AB00…`、扩展表 `1C770129…`、母本 `9DB99E60…`、`data/splits`、`git status -- experiments data` 全程不变 |
| 34 | **2026-09-23 第三轮（本轮）：K-09 全量符号审计 + 两处"登记未改"口径统一 + 重建复测** | **① K-09 全量（原为抽查）**：`.tmp_revision_20260923/k09_math_audit.py` 逐对象遍历 **152 个 `m:oMath` / 413 个数学 run**，按稿件自述符号规范判定 → **违规 2 处、均已修正**：式 (11) 与式 (12) 的 `A_{t,u}` 原为斜体（`i`），应为**粗斜体**（`bi`，`A` 是整幅输出图）；改 `build.py` 的 `eq(11)`/`eq(12)` 与 LaTeX 镜像字典（→ `\boldsymbol{A}_{t,u}`）。重建后重跑同一审计：**152 对象 / 0 违规**，样式计数 `i 228→226`、`bi 25→27`（恰为 2 个 run）。灰区 4 项（`J(p)`/`L(p)`/`K=1`/`K=4` 的括号与等号并入斜体 run、`R_b` 直立算子）无规范条文可判违规，**登记不改**。**② 两处口径统一（不改数值）**：figS4 的 KSDD2 端点 = `bootstrap_mean`、Table 14 "Point" = `point_delta`，**不同定义量**（源 CSV 两列俱在，Δ=+0.0052/+0.0015 pp）⇒ 图注 + 表 14 表注各补一句（`figures.json` / `tables.json`）；Table 17 末列经 CSV 八 seed 复算确认 = **逐 seed 复现均值的 sd ÷ 中位个体 95% 自助半宽** = 0.4795/0.3655/0.6833/0.6489 → 表值 **0.48/0.37/0.68/0.65**（用 "SD across seeds" 列则得 0.51/0.37/0.69/0.65）⇒ 表值无误、改写表注把公式与**95%** 层级写清。**③ 重建复测**：docx `EB11FCA8…ACE41`（19,220,393 B）= **55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 12 公式 / 34 文献 / 19,394 词**；备份 `.bak_symbols_20260923`；`qa_layout.py` **0 problem**、`figure_font_gate --self-test` **4/4**、`pytest tests -q` **260 passed**；**无图件改动 ⇒ 未重出 deck**。登记见 `FIGURE_BINDING.md` §十二 |
| 35 | **2026-09-23 第四轮：fig4b 图注口径同步 + 图 S4 备注同步（一次 deck 重出）+ 验收记录更正** | **① fig4b 图注**（`figures.json` 的 `effects.continuation_caption`）：由"All five encoders use seeds 0, 1 and K = 1, 4 … points are **observed condition means** … wider scope 仅另列于表"改为"shared four-condition scope 与 wider twelve-condition scope 并列、(4)=seeds 0,1×K=1,4、(12)=seeds 0,1,2×budgets 1,2,4,8、points 为 **bootstrap replicate means**、98.75% 配对区间且 **每个 encoder 与 scope 各一个四比较族**、E1–E3 探索性且 **无联合族校正**、跨编码器比较用共享四条件范围"；`tables.json` 的 `encoders.note` 同口径微调一处（"four cells" → "four cells **in that scope**"）；`plot_primary.py` 的 `primary_sources.json` 描述同步。**未改任何数值**；`tables.json` 的 `rows`/`headers` 未动。重跑 `plot_primary.py`：`fig4a/fig4b/fig5a/fig5b` 的 PNG **逐字节不变**（`fig4b` = `FA2DE6E4…FCC13`）。**② deck 一次重出**（63 页）：`build_deck.mjs` → `assemble_deck.ps1` → `finalize_deck.mjs`，`finding_count = 0`，新 SHA `5C47F8FF…B842C`（72,415,664 B）；**59 个位图页内嵌图与盘上 PNG 逐字节相同（59/59）**、其余 5 个媒体全属原生页 1（原生页 `[1,2,3,15]`）；`FIGURE_SLIDE_INDEX.json` 63 条、**63/63 页备注含现行图注**（slide 5 新 fig4b 图注、slide 23 现行 S4 图注）；`图件与PPT页码索引.md` 逐字节未变。**③ 重建 docx**：**55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 12 公式 / 34 文献 / 19,434 词**，SHA `9B3E15F5…9245`。**④ 验收记录更正**：`FINAL_REPAIR_AND_ACCEPTANCE_20260923.md` §10.6 第 4 项由"`docs/MODEL_WEIGHTS.md` 不在盘"改为"**在盘且达标**"（`Test-Path`=True，生成于 `finish_documentation23.py:31`），并新增"**旧版验收 JSON/早期待办状态不作为最新文件凭证**"口径。**⑤ 门禁**：`qa_layout.py` **0 problem**、`figure_font_gate --self-test` **4/4**、`pytest tests -q` **260 passed**；三冻结哈希与 `data/splits/*` 全程不变。详见 `FIGURE_BINDING.md` §十三、`FINAL_REPAIR_AND_ACCEPTANCE_20260923.md` §十一 |

> **§六 凭据时效说明（2026-09-23 校，逐条复核后添加）**：本节各行是**某次构建/某轮收尾的时点快照**。凡涉及 docx/deck 的 SHA 与页/表/图/词数，一律以 **§现状** 的现役口径为准（docx `…20260923.docx` = 55 页 / 23 表 / 27 内嵌图 / 12 公式 / 152 数学对象 / 34 文献 / 19,434 词，`9B3E15F5…`；deck `All_Figures_Complete_20260923.pptx` = 63 页，`5C47F8FF…`）。本轮已**就地刷新**过期凭据：#1（fig2 哈希 `AB1EB3FD…`→`5156E610…`）、#2（fig3 哈希 `57362409…`→`3F309ADB…`，行号 430→432）、#3（figS4 哈希 `C4D2D0A0…`→`6AFA2E49…`）、#4（58 页 deck→63 页）、#13（图 S4 宽 16 cm→17 cm）、#15（47 页 / 20 表 / 22 图 →向现役口径并列）。**未逐一刷新**的其他行（如 #7、#11 的 47 页 docx、#12 的 B 线哈希）保留原值，均标注为历史时点，**不得据此判定当前交付件**。

---

## 七、"需作者拍板"清单（**2026-09-23 第三轮后仅保留 1 项：作者元数据**）

| # | 待拍板事项 | 事实 / 选项 | 关联 |
|---|---|---|---|
| A | **作者元数据**（作者/单位/通讯/ORCID/资助）与 COI 是否保留现句 | 占位 `[[AUTHORS]]`/`[[AFFILIATIONS]]`/`[[CORRESPONDING_AUTHOR]]`/`[[FUNDING]]` 均在 `manuscript.md`；伦理与 COI 已有安全默认（本轮未动） | E-01…E-04 |

> **归档 DOI 已移出"待拍板"**：作者执行步骤（GitHub Release → Zenodo 集成 → 取 DOI）与**逐处回填清单**已备于 `docs/SUBMISSION_METADATA.md` 的「**归档 DOI 获取步骤（作者执行）**」一节（含平台选择、许可与元数据核对、8 条回填点）；稿件保持如实表述 "a permanent archive DOI … has not yet been established"（`manuscript.md:226`，本轮**未改**、未虚构）。原 B 行保留在 **7.2**。
> 原 §七 的其余 18 项**已移出"待拍板"**，逐条收尾状态见 **7.1**，原文行保留在 **7.2**（不改写）。

### 7.1 原 §七 各行的收尾状态（2026-09-23）

| 原 # | 收尾状态（不删除原行，仅标注） |
|---|---|
| 1 | **移出待拍板**：T09 整批改名**未执行**（温和版在位）；延期至 major revision，**非阻断** |
| 2 | **已闭环**：图 S6 已入稿（清单 A-23 通过） |
| 3 | **已闭环/部分延期**：8 项写作欠缺按现役稿落实（清单 §1 通过）；未落项见 §3 关联条目，**非阻断** |
| 4 | **保留在 §七**（= A 行） |
| 5 | **已移出待拍板**：归档 DOI 的作者执行步骤与回填清单已备（`docs/SUBMISSION_METADATA.md`「归档 DOI 获取步骤（作者执行）」）；稿件保持如实表述、未虚构 DOI，**非阻断** |
| 6 | **移出待拍板**：`build.py` 非字节可复现**已按"内容口径 + SHA 只作快照"写成文档**（E-09）；是否再改 `build.py` 由作者定，**非阻断** |
| 7 | **已执行并复核**：`selfcheck.py` 于 2026-09-23 实跑 **67/69**（2 项已登记既有失败）并**逐字节还原**（清单 A-27 通过）。是否重建旧提纲 / 豁免 `_smoke` 快照仍可由作者定，**非阻断** |
| 8 | **移出待拍板**：包内 `SHA256SUMS` 2 处漂移（E-11），**非阻断** |
| 9 | **移出待拍板**：`PREFLIGHT.json` / `ext_run_anomalyclip.py` 的 09-21 留痕（E-12）——A14 已结案，留痕保留，**非阻断** |
| 10 | **移出待拍板**：提交信息层重写需 `git filter-repo` + 强推（E-15），**非阻断**、须书面授权 |
| 11 | **移出待拍板**：本地未推送提交（E-14），**非阻断** |
| 12 | **移出待拍板**：表 A/表 B 与文献参照表是否入稿（D-13/D-14/A-17），**非阻断** |
| 13 | **移出待拍板**：R-22 版式母本移出 `*.docx` 忽略范围（E-19），**非阻断** |
| 14 | **移出待拍板**：清理第二轮改动是否提交（E-18），**非阻断** |
| 15 | **移出待拍板**：生成物绝对路径与历史引用清理（B-08/E-16），**非阻断** |
| 16 | **移出待拍板**：`methods/` 处置方案 (a)/(b)（E-08），**非阻断** |
| 17 | **移出待拍板**：数据集许可明细（E-06），**非阻断** |
| 18 | **移出待拍板**：BTAD 口径科研判断追认（已在稿），**非阻断** |
| 19 | **移出待拍板**：`.tmp_revision_20260922/` 等 scratch 是否删（E-18），**非阻断** |
| 20 | **移出待拍板**：三处重复图件集留哪一处（B-09/E-18），**非阻断** |

### 7.2 原决策清单（**保留原文，状态见 7.1**）

| # | 待拍板事项 | 事实 / 选项 | 关联 |
|---|---|---|---|
| 1 | **T09 是否执行整批改名** | 温和版已落（加列 + 首现强调 + 图注全称）；整批改名有**方案 A**（只改文字标签，推荐）与**方案 B**（连公式一起改，`J`/`L` 风险最高）；也可只做方案 A 且 J/L 与公式不动，把整批留到 major revision | A-21、B-06、C-02 |
| 2 | **S6 是否入稿**（或留补充材料） | docx 内 `Figure S6` 命中 0；入稿须写 5 条限制并复测页数/表数 | B-03 |
| 3 | **8 项写作欠缺是否补** | A01 / A02 / A03 / A05 / A06 / A07 / A10 / A13（均零 GPU）；逐条"怎么写"见 `FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md` §13 | A-06、A-13、A-14、A-15、A-16、B-01、B-02、E-07 |
| 4 | **作者元数据**（作者/单位/通讯/ORCID/资助）与 COI 是否保留现句 | 占位 `[[AUTHORS]]`/`[[AFFILIATIONS]]`/`[[CORRESPONDING_AUTHOR]]`/`[[FUNDING]]` 均在 `manuscript.md`；伦理与 COI 已有安全默认 | E-01…E-04 |
| 5 | **归档 DOI 平台**与是否审稿阶段公开代码 | URL 已入摘要与可得性节；DOI 未建立；`manuscript.md:224` 现写 "a permanent archive DOI … has not yet been established" | E-05、E-08 |
| 6 | **`build.py` 非字节可复现是否接受**（F21） | 连跑三次 docx SHA 三个值、内容度量一致；接受则文档只记内容口径，不接受则需改 `build.py` 固定 docProps/时间戳或改内容校验 | E-09 |
| 7 | **`selfcheck.py` 2/69 两项如何处置**（F22） | ①大纲 docx 是否重建/放回，或把检查点改为"缺失即跳过并记 caveat"；②冻结快照 3 处漂移（`_smoke` 2 个 `.npz` 缺失 + `REPORT_CN.md` 仅 mtime 变化）是否从冻结清单豁免 | E-10 |
| 8 | **包内 `SHA256SUMS` 2 处既有漂移是否修** | `VD1_MANIFEST.json`（填值后未刷新清单）与 `requirements_lock.txt` | E-11 |
| 9 | **`PREFLIGHT.json` 里 09-21 审计留痕是否改写** | `checkpoint_rule_and_caveat.caveat` 与 `ext_run_anomalyclip.py` docstring 仍写"本项目重训"；A14 已结案，二者为红线区证据字段/代码注释 | E-12 |
| 10 | **提交信息层 4 条含身份串（2 条含旧仓库名）是否重写历史** | 需 `git filter-repo` + 强推（会改写 `1b360bf` 之后全部 SHA），须书面授权 | E-15 |
| 11 | **本地 2 个未推送提交是否推送** | `main...origin/main [ahead 2]`（HEAD `4d7f640`） | E-14 |
| 12 | **表 A / 表 B 是否入正文**；文献参照表（T08）是否做 | 表 A/B 须带 7 条限制 + 区间只 `pixel_ap`；文献参照表零重跑、须分栏且补 4 个引用键 | D-13、D-14 |
| 13 | **R-22：版式母本移出 `*.docx` 忽略范围 + 登记 `ARTIFACT_INDEX.md`** | 母本不可由源重建；否则干净克隆无法复现 Word 终稿 | E-19 |
| 14 | **清理第二轮改动是否提交**（158 `R` + 3 `M` + 1 新文件）；`.trae/` 是否纳入 | 建议提交信息见 `PROJECT_CLEANUP_AUDIT_20260922.md` §E.8 | E-18 |
| 15 | **生成物绝对路径 / 约 51 处历史旧路径引用是否清** | 需改生成器后重出图与 deck；历史引用含脚本注释与红线区状态记录 | B-08、E-16 |
| 16 | **`methods/` 在复现包内的处置方案 (a)/(b)** 与各预训练权重再分发许可 | 影响 E-08 第 ① ⑦ 两条 | E-08 |
| 17 | **数据集许可明细与仓库内路径指引是否补入正文** | 旧稿有（CC BY-NC-SA 4.0 / CC BY 4.0、`data/README.md`、`docs/specs/`、`REPRODUCIBILITY_PACKAGE.md`），权威稿有意从简 | E-06 |
| 18 | **BTAD 口径的科研判断追认**（已按用户指示执行全文替换） | "点估计接近零、区间跨零，当前数据不足以确定交互方向"；作者需追认该定位（是否接受"非零效应"） | A 组口径（已在稿） |
| 19 | **`.tmp_revision_20260922/` 现在只剩 4 个小文件（0.11 MiB）是否删**；`.tmp_*` 其余约 445 MiB 可回收面 | 纯 gitignored，属"作者意图" | E-18 关联 |
| 20 | **三处重复图件集"留哪一处"**（清理审计 S1/S9） | 现役链只认 `docs/figures_reference_matching_20260914/`；`docs/manuscript_reference_matching_20260914/figures/` 被脚本读写（红线）；包视图已归档 | B-09、E-18 |

### 7.3 本轮复审新增发现（**1 条：N-1 已由作者裁决为选项 (a) 并结清**；属"清单外新发现"，不并入 §七）

| # | 新发现 | 事实 / 证据 | 状态 |
|---|---|---|---|
| **N-1** | **`plot_primary.py` 的数据来源被 revision23 换表；入稿图 fig4b 与 encoders 表在"四条件口径"的点值上不一致**（**编号更正**：记录里写的"Table 15"为 20260921 前旧编号；现役 docx 的 23 表中 **encoders 表 = Table 16**） | `git diff 51b3cec 01886e9` 显示该脚本把数据源由 `.tmp_figure_revision_20260920/tables.json` 改为 `scripts/paper_complete_review_20260920/tables.json`；两源 `encoders` 表不同（旧 5 行 `S +0.767` vs 新 8 行 `S (4) +0.695`）。实测：旧入稿 `fig4b_matched_encoders.png`（`057AF4D0…`）**恰等于用旧表渲染**，用现表渲染为 `AE1145D7…` | **已解决（作者批准选项 (a)，2026-09-23）**：`fig4b` 已按现行表 **8 行**（`(4)` 共享四条件 + `(12)` 更宽口径两组）重渲染（`plot_primary.py` 的 `fig4b` 段改写 + 同步 y 轴刻度）；新 PNG `FA2DE6E4…FCC13`（2342 × 2450，全 11.0 pt，四道门禁全过）；**逐值核对：图内 32 个点值/区间 vs Table 16 → 全部一致**。deck 重出（63 页，fig4b 第 5 页，内嵌位图逐字节相同）、docx 重建（55 页 / 23 表 / 27 内嵌图 / 19,253 词）并复测通过。详见 `FIGURE_BINDING.md` §11.9、`REVIEW_CHECKLIST…` §1 A-28 / §7 N-1、`FINAL_REPAIR_AND_ACCEPTANCE_20260923.md` §九 |

---

## 八、推荐执行顺序（拓扑序 + 前置依赖 + 回退）

| 步 | 动作 | 前置依赖 | 回退方法 |
|---|---|---|---|
| **S0** | **冻结基线**：对 5 个源文件 + `build.py` + 4 个图源脚本 + 全部 PNG + 2 个 PPTX 计算 SHA-256 并落 `.bak_20260923` | 无 | 逐文件还原 `.bak_<日期>` |
| **S1** | **决策冻结**：命名是否整批改（T09）、S6 是否入稿、8 项写作欠缺是否补、作者元数据、表 A/B 是否入稿 | S0 | 决策记录本身即回退依据 |
| **S2** | **正文与表格改动**：A-02…A-20 写作项 + A-06（T12 段落）+ A-13（Table 12 协议列/表注）+ A-17 表注口径 | S1 | `git checkout -- scripts/paper_complete_review_20260920`；docx 用 `.bak_20260923` 还原 |
| **S3** | **图件改动与重渲染**：A-01（(c) 压缩）、A-19（下标样式）、B-04/B-05（S4 图内）、B-06（命名联动，若 S1 决定执行） | S2（命名定稿） | 还原 PNG + 图源脚本备份；重跑脚本即可重建 |
| **S4** | **图件门禁复跑**：`qa_layout.py`（0 problem）、`figure_font_gate.py --self-test`（4/4）、图 S6 四道门禁 | S3 | 门禁失败 → 回到 S3 调版面；若 1 轮内调不好，**中止整批改名**，保留温和版交付 |
| **S5** | **重建 docx 并复测**：`build.py` → 复测 **55 页 / 23 表 / 27 内嵌图 / 12 编号公式 / 152 数学对象 / 34 文献**（2026-09-23 现役口径；旧记的 47 页 / 20 表 / 22 图 / 142 对象为扩版前时点值） | S2 + S3 | 用 `.bak_20260923` 还原 docx；`build_validation.json` 由重建刷新 |
| **S6** | **重出 deck（现役 63 页）+ 同步索引**：`build_deck.mjs` → `assemble_deck.ps1` → `finalize.mjs`；核对 `FIGURE_SLIDE_INDEX.json` 与 `图件与PPT页码索引.md` | S3（S4 通过） | 直接还原旧 deck（`All_Figures_Complete_20260920.pptx` / `All_Figures_Finalized_20260920.pptx` 可作旧版锚点） |
| **S7** | **复测与一致性**：`pytest tests -q`（260 passed）、冻结表/扩展表哈希、`data/splits` 清单、`selfcheck.py`（失败项按 S1 决策处置；**运行后须 `git checkout --` 还原其就地改写的两个 JSON**） | S5 + S6 | 冻结值不一致 → 立即停手并回退；`experiments/**` 用 `git checkout --` 还原 |
| **S8** | **文档与元数据同步**：`README.md`、`docs/ARTIFACT_INDEX.md`、`FIGURE_BINDING.md`、`HANDOVER_20260919.md`、`SUBMISSION_METADATA.md` + 复现包重打（E-08）+ DOI 回填 | S7 | 文档类只增指针/刷新行，可逐文件回退 |

> **数值安全底线**：全流程 `git diff` **不应出现 `experiments/**` 与 `data/**`**；`baseline_common_region.csv` 必须全程保持 `3C83AB00…`，扩展表保持 `1C770129…`。

---

## 九、全面性核对结论（用户明确要求）

### 9.1 "只在一份文档出现、别处缺失"的条目

| # | 条目 | 唯一出处 | 别处状态 | 处置 |
|---|---|---|---|---|
| 1 | F12 逐图落盘硬门通过，但各方法覆盖单元数不等（AnomalyCLIP 零样本只有 36 单元、**不能与四条件行配对**） | `docs/论文与图件问题汇总…:194-198` | 未进 `REMEDIATION_PLAN` / `ISSUE_REGISTER` 总表；已落在 Table 12 表注（`FINAL_ACCEPTANCE…:211`） | 已由 A-13 承接 |
| 2 | F13 共同区域"未变"是巧合而非结构性保证 | 同上 `:200-202` | 未进 REMEDIATION/ISSUE_REGISTER | 已在 A-13 表注纪律中体现；本表登记 |
| 3 | F19 **未做项**：生成物溯源 JSON 仍含旧绝对路径 | 同上 `:489-493` + `FINAL_ACCEPTANCE…:158` | 未进 REMEDIATION/ISSUE_REGISTER | 本表 **B-08** |
| 4 | F21 `build.py` 非字节可复现 | 同上 `:520-525` | `FINAL_ACCEPTANCE` §4/§6 有，`ISSUE_REGISTER` **无**，`REMEDIATION` 仅指针 | 本表 **E-09** |
| 5 | P09–P14（扩展表表注措辞 / SubspaceAD 分辨率 / AnomalyCLIP 来源 / WinCLIP 低分 / 区间只 pixel_ap / 词数口径） | 同上 §八 与 §八·续 | REMEDIATION/ISSUE_REGISTER 均无（仅词数口径在 §〇ter 有一行） | 本表 A-13、A-17、已完成 #11/#15 |
| 6 | A18–A23（B 线新增欠缺） | `EXPERIMENT_GAP…:154-163` + `FINAL_ACCEPTANCE…:110` | REMEDIATION/ISSUE_REGISTER 无 | 本表 D-07…D-11、B-03 |
| 7 | R-22（版式母本被 `*.docx` 忽略） | `REMEDIATION_PLAN…:14`、`ISSUE_REGISTER…:41`（"**建议编号** R-22"） | **未正式列入** `ISSUE_REGISTER` §一 问题总表（R-01…R-21） | 本表 **E-19** |
| 8 | 清理审计建议清单 S1–S11 与未执行清单 U1–U10 | `PROJECT_CLEANUP_AUDIT_20260922.md:284-300`（S）、`:497-510`（U） | 未进任何其他台账 | 本表第五节"需拍板"#19/#20 |
| 9 | 提交信息层重写方案（filter-repo + 强推） | `SCI_STRING_AUDIT_20260922.md:143-183` | `FINAL_ACCEPTANCE…:157`（§6-7）有引用 | 本表 **E-15** |
| 10 | `BASELINE_EXPANSION_PLAN` 的 D1–D6（需作者决定） | `BASELINE_EXPANSION_PLAN_20260921.md:154-163` | 仅该文件；D5 已被 T06/T07 决策关闭但未回头勾选 | 本表 D-12/D-13、第五节 #16 |
| 11 | B 线两份文档的"未完成/不确定"（HANDOFF §6 六条、PRESENTATION_PLAN §7 四条） | `METHOD_COMPARISON_HANDOFF…:175-182`、`METHOD_COMPARISON_PRESENTATION_PLAN…:232-241` | `FINAL_ACCEPTANCE` §7 部分索引 | 本表 D-07…D-11、A-17 |
| 12 | `SUBMISSION_METADATA` 第 11 项（数据集许可明细）与第 14 项（仓库/归档链接） | `docs/SUBMISSION_METADATA.md:24,27` | `AUTHORITATIVE_SOURCE_DIFF` §9-需决定 2 有；`FINAL_ACCEPTANCE` §13 **未含** | 本表 E-05、E-06、第五节 #17 |
| 13 | **本表新发现**：`FIGURE_BINDING.md` 未登记图 S3 第 5/6 页面板（`panel_interaction_cases_p3/p4`），且两处图件目录不一致 | `图件与PPT页码索引.md:18-19` vs `FIGURE_BINDING.md §一`；目录实测 | **任何文档均未记录** | 本表 **B-09** |
| 14 | **本表新发现**：T13 记 Fig 5 为 "(a/b/c)" 三页，盘上只有 `fig5a`/`fig5b` 两页（PPT 第 6/7 页也只两页） | `论文与图件问题汇总…:399-413` vs 目录实测 | 未核实 | 本表 **B-10（未核实）** |

### 9.2 "同一问题在不同文档里编号不同"的映射（旧编号 → 总表编号）

| 旧编号（来源文档） | 总表编号 | 备注 |
|---|---|---|
| T01 / T02 / T03 / T04 / T05 | A-01 / A-02 / A-03 / A-04 / A-05 | T04 与 P05 为同一问题 |
| T06 | 已完成 #27 | 外部家族 2→5 |
| T07 | D-12 | "方法数量"结案口径 |
| T08 | D-13 | 文献参照表（Zero 重跑、可选） |
| T09 | **A-21 + B-06 + C-02** | 一条决策、三处落地 |
| T10 / T11 / T12 / T13 | A-07 / 已完成 #7 / **A-06 / B-01 + B-02** | T12 与 EXPERIMENT_GAP 的 A03 是同一件事；T13 与 A05/A06 是同一处图件缺口 |
| T14 / T15 / T16 / T17 / T18 | 已完成 #18 / #8 / #9 / #11 / #12 | T18 的"是否入稿"落到 B-03 |
| P01 / P02 / P03 / P04 / P05 | A-08 / A-09 / 已完成（已满足）/ #3 / A-04 | P03 图注已写 "not training convergence" |
| P06 / P07 / P08 / P09 / P10 | A-10 / A-11 / A-12 / 已完成 #11 / A-13 | P09 已按条件式表述落地 |
| P11 / P12 / P13 / P14 | 已完成 #10 / 纪律（不用于排名）/ A-17 / 已完成 #15 | P11 = A14 结案 |
| F01 / F02 / F03 / F04 / F05 / F06 / F07 / F08 / F09 / F10 / F11 | #1 / #2 / B-04 / B-05 / B-01 / B-02 / 纪律（"约 10 个"非缺口）/ A-18 / A-20 / A-07 / A-19 | — |
| F12 / F13 / F14 / F15 / F16 / F17 | A-13（表注）/ 纪律 / #4 / #5 / **未使用（编号保留）** / #6 | F16 因 PPT 重出成功而未登记 |
| F18 / F19 / F20 / F21 / F22 | B-03 + #12 / #16 + B-08 / #17 / **E-09** / **E-10** | — |
| A01 / A02 / A03 / A04 / A05 / A06 / A07 | A-14 / A-13 / A-06 / D-01 / B-01 / B-02 + D-02 / A-15 | A 编号与 `ISSUE_REGISTER` 的 R 编号互不重叠 |
| A08 / A09 / A10 / A11 / A12 / A13 | D-03 / D-04 / A-16 / D-05 / D-06 / **E-07 + E-08** | A13 是"写作 + 打包"，跨 A/E 组 |
| A14 / A15–A17 / A18 / A19 / A20 / A21 / A22 / A23 | 已完成 #10 / 已满足（不补）/ D-07 / D-08 + A-17 / D-09 / D-10 / D-11 / **B-03** | — |
| R-01…R-15（复现包/测试/哈希） | **E-08**（P1-1…P1-7）；R-05/R-06 等已处置项见 #19/#22 | — |
| R-16 / R-17 / R-18 / R-19 / R-20 / R-21 / R-22 | E-01 + E-05 / 第五节 #5 / 纪律（full-pixel）/ A-10 / 纪律（5 家族、禁 SOTA）/ 纪律（correspondence 不等效）/ **E-19** | R-22 未正式入 `ISSUE_REGISTER` §一 总表 |
| R-11 / R-12 / R-13 / R-14 | E-14（+已解决部分 #20）/ **E-17** / E-08 / E-08（第 ⑦ 条） | — |
| D1–D6（BASELINE_EXPANSION §5） | 第五节 #16 / #12 / #12 / D-13 / D-14 / 未验证项 → 本表对应条 | — |
| S1–S11（清理审计建议） | 第五节 #19/#20 | 建议清单，未执行 |
| U1–U10（清理第二轮未执行） | 第五节 #19/#20 | 未执行 |
| R1–R10（`NAMING_MIGRATION_PLAN` §5 风险） | **与 `ISSUE_REGISTER` 的 R-01…R-21 字符冲突**，见下 | — |

### 9.3 编号冲突与口径冲突（需下游注意）

| # | 冲突 | 说明与建议 |
|---|---|---|
| 1 | **`P0/P1/P2/P3` 两套含义** | `REMEDIATION_PLAN_20260920.md` 的 P0–P3 是**阶段**（一致性与措辞 / 复现包 / 版本发布点 / 投稿元数据）；`论文与图件问题汇总` 的 P01–P14 是**问题**。引用时必须写全（如 "REMEDIATION P1-3"）。 |
| 2 | **`R1–R10` 两套含义** | `NAMING_MIGRATION_PLAN_20260922.md` §5 的 R1–R10 是**改名风险**；`ISSUE_REGISTER_20260920.md` 的 R-01–R-21 是**问题**。本表统一用 R-0x 指后者。 |
| 3 | **`S` 两套含义** | `NAMING_MIGRATION_PLAN` 的 S0–S9 是**改名执行步骤**；`PROJECT_CLEANUP_AUDIT` 的 S1–S11 是**建议删除清单**；论文图号 S1–S6 是**补充图**。 |
| 4 | **`A` 两套含义** | `EXPERIMENT_GAP_ANALYSIS_20260922.md` 的 A01–A23 是**实验欠缺**；`FIGURE_BINDING.md` §六/§九 的 `A1` 是**双编码器锚（方法名）**。 |
| 5 | **表号两套并存（不互斥）** | `ACCEPTANCE_20260920.md` §一 #8 的 `tables 18 / figures 8` 属**已冻结旧链**（`scripts/manuscript_build_20260914/`）；权威链为 **23 表 / 27 内嵌图**（2026-09-23 实读）。 |
| 6 | **字号门两套覆盖对象** | `qa_layout.py` 的 `TOTAL PROBLEMS: 0` 覆盖 7 张母版图（最小 11.29 pt）；20260920 方法图的字号门是 `figure_manifest.json` 的 `minimumPrintPtAt17cm` = 11.294 pt。两处不可读成同一批图。 |
| 7 | **同名字符串冲突（已过时）** | `ISSUE_REGISTER` R-11 "超前 15 提交"、R-20 "只两个方法家族"、`SCI_STRING_AUDIT` 的 `sci_project`、`论文与图件问题汇总` §一/§七 的 `18694B90…` / 16,892 词均为**历史值**（各文件已加刷新行/总注）。 |

---

## 十、版本与入口约定

1. **本表是唯一交接入口**：`docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md`（2026-09-23 起）。新增待办请追加到本表 A–E 五组，不要另建平行台账。
2. **其余文档按"历史登记"保留，不删除**（含 GPT 生成的总结）。仅在以下两处已各加一行指针：
   - `docs/论文与图件问题汇总_仅复核_20260921.md`（登记表：T/P/F/A 编号的来源）
   - `docs/REMEDIATION_PLAN_20260920.md`
3. **权威链**（改稿只动这几个）：`scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}` + `build.py`；产物 `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`（**55 页 / 23 表 / 27 内嵌图 / 12 公式 / 152 数学对象 / 34 文献 / 19,434 词**；旧 `…20260920.docx` 的 47 页 / 20 表 / 22 图 / 142 对象 / 17,221 词为扩版前历史值）。
4. **已 superseded（勿改、勿据其写作）**：`docs/manuscript_reference_matching_20260914/`、`scripts/manuscript_build_20260914/`（见其 `SUPERSEDED_20260921.md`）；`docs/replication_package_20260920/` 是**交付副本**，不是编辑源。
5. **文档地图**：图件绑定 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`；页码索引 `docs/paper_complete_review_20260920/{FIGURE_SLIDE_INDEX.json, 图件与PPT页码索引.md}`；下游写作指令 `docs/FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md` §13；命名方案 `docs/NAMING_MIGRATION_PLAN_20260922.md`；B 线写作说明 `docs/METHOD_COMPARISON_HANDOFF_20260922.md`；投稿元数据 `docs/SUBMISSION_METADATA.md`。

---

## 十一、历史文档收口映射（2026-09-23 新增）

> **本节目的**：把此前两份"尚未收口的历史待办/问题文档"逐条清点，判定为 **已完成（给凭据）/ 仍待办（已并入本表，标新旧编号映射）/ 已作废（给理由）**，做到**不丢条目**。原文一律**不改写**，只在这两份文件顶部各加一行**收口声明**（本轮已加）。旧编号体系说明见 **§九 9.2 / 9.3**。

### 11.1 `docs/论文与图件问题汇总_仅复核_20260921.md`

**清点结果（共 68 个登记单元）**：**已完成/已闭环 22**、**仍待办（已并入）30**、**纪律/不补（已作废或降级）10**、**未使用 1**、**计划/校验类（由 §八 执行顺序承担）5**。逐条映射：

| 旧编号 | 主题（一句话） | 判定 | 去向 |
|---|---|---|---|
| T01 | 图2(c)/图3(c) 占位过大 | 仍待办 | **A-01** |
| T02 | 无 loss–epoch 曲线可展示 | 仍待办 | **A-02** |
| T03 | 替代图 S4 未比较所有方法稳定性 | 仍待办 | **A-03** |
| T04 | 机器/软件/输入/计时可比性说明缺失 | 仍待办 | **A-04**（= P05） |
| T05 | 协议解释篇幅挤占主线 | 仍待办 | **A-05** |
| T06 | 外部家族 2→5（"方法太少"落地） | 已完成 | **§六 #27** |
| T07 | 外部评审 2026-09-22 口径（近两三年 3–4 个） | 已结案 | **D-12**（不做） |
| T08 | 文献参照表是否纳入 | 降级可选 | **D-13**（待拍板） |
| T09 | 命名规范（整批改名） | 仍待办（待拍板） | **A-21 + B-06 + C-02** |
| T10 | long paper 篇幅与组织 | 仍待办 | **A-07** |
| T11 | 摘要末句给仓库 URL | 已完成 | **§六 #7** |
| T12 | "为何对比方法无需目标域训练"成体系说明 | 仍待办 | **A-06**（= EXPERIMENT_GAP A03） |
| T13 | 检测/定性图进正文结果分析 | 仍待办 | **B-01 + B-02**（= A05/A06） |
| T14 | 仓库改名 | 已完成 | **§六 #18** |
| T15 | 摘要 URL 与 Data and Code 矛盾消除 | 已完成 | **§六 #8** |
| T16 | 命名温和版落地 | 已完成 | **§六 #9** |
| T17 | Table 12 协议列/表注改准确表述 | 已完成 | **§六 #11** |
| T18 | B 线统一输入几何子集 | 已完成 | **§六 #12** + **B-03** |
| P01 | 无目标域训练 ≠ 从未训练 | 仍待办 | **A-08** |
| P02 | 冻结 ≠ 无超参数 | 仍待办 | **A-09** |
| P03 | S4 不证明训练收敛/所有方法稳定 | 已满足 | 已满足（图注 "not training convergence"）；纪律 K-08/M-06 |
| P04 | ±5% 参考带 vs 实测 6.8% | 已完成 | **§六 #3** |
| P05 | 同机证据范围受限 | 仍待办 | **A-04** |
| P06 | S5 阶段计时不可写成端到端 | 仍待办 | **A-10** |
| P07 | 新比较说明 5 条论据不能直接搬入 | 仍待办 | **A-11** |
| P08 | 稳定性计划书数值逻辑矛盾 | 待核实（未搬入） | **A-12** |
| P09 | 扩展表表注措辞须与盘上证据一致 | 已完成 | **§六 #11**（条件式表述已落） |
| P10 | SubspaceAD 256↔672 必须披露 | 仍待办 | **A-13**（= A02）；已落 Table S2 表注 |
| P11 | AnomalyCLIP 检查点来源未核实 | 已结案 | **§六 #10**（A14） |
| P12 | WinCLIP 低分已交叉核实、不得用于排名 | 纪律 | **§六 #28**（不排名） |
| P13 | 区间只对 `pixel_ap` | 已核对无冲突 | **A-17**（表注口径） |
| P14 | 词数口径 16,969→17,200 | 已完成 | **§六 #15**（后并入时点刷新） |
| F01 | 图2(b) 高亮含义不一致 | 已完成 | **§六 #1** |
| F02 | 图3(b)"只有 B 权重变化" | 已完成 | **§六 #2** |
| F03 | 新 S4 图内重复总标题 | 仍待办 | **B-04** |
| F04 | 新 S4 符号/术语未沿用正文 | 仍待办 | **B-05** |
| F05 | 外部多方法对比图未进 Word | 仍待办 | **B-01** |
| F06 | "所有案例都有两种输出"过宽 | 仍待办 | **B-02** |
| F07 | 方法数量不能按"约 10 个"硬判缺项 | 纪律 | **§九 9.2**（F07 = 纪律） |
| F08 | 旋转增强收益概括忽略例外 | 仍待办 | **A-18** |
| F09 | 第二/第三贡献邻近重叠 | 仍待办 | **A-20** |
| F10 | 结果章节持续追加、主线被切碎 | 仍待办 | **A-07**（= T10） |
| F11 | 图2 类别下标正斜体不一致 | 仍待办 | **A-19** |
| F12 | 逐图落盘硬门过，但各方法覆盖单元数不等 | 仍待办 | **A-13**（表注）/ **§九 9.1 #1** |
| F13 | 共同区域"未变"是巧合非保证 | 纪律 | **§九 9.1 #2** |
| F14 | 58 页 PPT 未重出 | 已完成（含扩版后 63 页） | **§六 #4**（时点值）+ **C-01** |
| F15 | 三份同源 PPTX 已删其一 | 已完成 | **§六 #5** |
| F16 | （编号保留） | 未使用 | **§九 9.2**（F16 未使用） |
| F17 | 权威 docx 与版式母本不在盘 | 已完成 | **§六 #6** |
| F18 | 图 S6 编号/登记/门禁 | 已完成 | **§六 #12** + **B-03** |
| F19 | 旧绝对路径中性化 | 已完成（生成物溯源面另计） | **§六 #16 + B-08** |
| F20 | 禁忌词与"外部指导痕迹"复扫清零 | 已完成 | **§六 #17** |
| F21 | `build.py` 非字节可复现 | 待拍板 | **E-09** |
| F22 | 自检门禁 2/69 失败 | 待拍板 | **E-10** |
| A14 | AnomalyCLIP 检查点来源 | 已结案 | **§六 #10** |
| A23 | 图 S6 是否入稿 | 已闭环（已入稿，docx 命中 4） | **B-03** |
| A14/A23/T09 登记 | 登记块 | 见各行 | 已并入 A14→#10、A23→B-03、T09→A-21 |
| §五 已落实 1–9 | Related Work 连续、贡献定位、主图多支持图、seed/K/配对、五案例、三线表、S2 探索性、11/9.5pt+17cm、符号体系 | 防回归 | **§四 K-01…K-15** |
| §六 后续处理顺序 | 计划（仅供计划） | 计划 | **§八 推荐执行顺序** |
| §七 校验 | 时点哈希（09-21） | 历史时点 | 见 **§现状** / §六 时效说明 |

> **注**：§一（复核对象与版本关系）、§七（不修改原文件校验）为**版本/哈希登记**，不是独立待办；其 09-21 时点值由 **§现状** 取代（`18694B90…` / 47 页 / 16,892 词 → `9B3E15F5…` / 55 页 / 19,434 词）。

### 11.2 `docs/REMEDIATION_PLAN_20260920.md`

**清点结果（共 46 个登记单元）**：**已完成 9**、**仍待办（已并入）14**、**待拍板（已并入）12**、**纪律/限制保留 4**、**作者信息类 7**。逐条映射：

| 旧编号 | 主题 | 判定 | 去向 / 总表编号 |
|---|---|---|---|
| P0-1 | 统一 BTAD 口径 | 已完成（科研判断追认待作者） | **§六 #19** / A 组口径（已在稿） |
| P0-2 | 验收报告 69/71→71/71 | 已完成 | **§六 #19** |
| P0-3 | `ARTIFACT_INDEX.md` B 行旧结论替换 | 已完成 | **§六 #19** |
| P0-4 | `141/141` 标注为历史快照 | 已完成 | **§六 #19** |
| P0 验收 | 结论性文本清零 + 重出 docx | 已完成 | **§六 #21** |
| P1-1 | 补 `src/` + `configs/` + `methods/` | 仍待办 | **E-08**（① ） |
| P1-2 | `requirements_repro.txt` 补 CUDA index | 仍待办 | **E-08**（② ） |
| P1-3 | 新增 `docs/MODEL_WEIGHTS.md` | 已完成（原登记过期） | **E-07**（已在盘且达标） |
| P1-4 | 生成 `SOURCE_COMMIT.txt` + `SHA256SUMS` | 仍待办 | **E-08**（④ ） |
| P1-5 | 补 `paper_evidence_closeout_20260914/` 台账 | 仍待办 | **E-08**（⑤ ） |
| P1-6 | 补 `seeds_extension_20260917/p0_support/` | 仍待办 | **E-08**（⑥ ） |
| P1-7 | 回填 `VD1_MANIFEST.json` 的 `manifest_sha256` | 仍待办（会改既有文件） | **E-08**（⑦ ）+ **E-11** |
| P1 验收 | 包内 `import industrial_ad` / 抽查 20 项 SHA / `+cu118` | 仍待办 | **E-08** |
| P2-1 | 处置 3 个 tracked 修改 | 待拍板 | **E-18** |
| P2-2 | 修测试 collection 失败 | 已完成 | **§六 #22**（`pytest.ini`，260 passed） |
| P2-3 | `.gitignore` 处理 `dist/` | 已完成（现象消失） | **E-17**（`.gitignore:73` = `dist/`） |
| P2-4 | 打新 tag 并核对 `SOURCE_COMMIT.txt` | 待拍板 | **E-18 / E-11** |
| P2-5 | 推送（需作者点头） | 已完成（推送部分） | **§六 #20**（09-22 时点 `=0`；09-23 又超前 2 → **E-14**） |
| P2-6 | 归档取得 DOI | 待作者 | **E-05** |
| P2 验收 | `pytest` N passed / `git status` 干净 / tag 对齐 | 部分已完成 | **§六 #19/#22** + **E-14 / E-18** |
| P3-1 | 作者/单位/通讯/ORCID | 待作者 | **E-01** |
| P3-2 | 资助信息 | 待作者 | **E-02** |
| P3-3 | 利益冲突声明 | 已填待过目 | **E-03** |
| P3-4 | 伦理审查声明 | 已填 | **E-04** |
| P3-5 | 数据/代码可得性（URL + DOI + 许可） | 部分待作者 | **E-05**（URL 已入稿 / DOI 待作者） |
| P3-6 | 是否审稿阶段公开代码 | 待作者 | **E-05**（关联） |
| 需作者信息 1–4 | 作者列表/资助/COI/伦理 | 待作者 | **E-01…E-04** |
| 需作者信息 5 | 仓库地址 + 归档 DOI 平台 | 待作者 | **E-05** |
| 需作者信息 6 | 发布包许可 | 待作者 | **E-06** |
| 需作者信息 7 | `methods/` 处置方案 (a)/(b) | 待拍板 | **E-08** |
| 需作者信息 8 | 预训练权重再分发许可 | 待拍板 | **E-08** |
| 需作者信息 9 | 审稿阶段是否公开代码 | 待作者 | **E-05** |
| 需作者信息 10 | BTAD 口径追认 | 已在稿 / 待追认 | A 组口径（§七 已移出） |
| 需作者信息 11 | 是否回改 `VD1_MANIFEST.json` | 待拍板 | **E-08**（⑦ ）/ **E-11** |
| 需作者信息 12 | 是否推送本地 `main` | 已办结（09-22）；09-23 复现 | **§六 #20** → **E-14** |
| 限制 R-18 | full-pixel 只有点估计 | 纪律（限制保留） | **D-03** |
| 限制 R-19 | 效率数据为部分阶段计时 | 纪律（限制保留） | **A-10 / D-04** |
| 限制 R-20 | 外部对比"两个家族"（已过时→5 家族） | 纪律（限制保留、口径刷新） | **D-12** / §六 #27 |
| 限制 R-21 | correspondence 只证明零排除保持 | 纪律（限制保留） | **§九 9.2**（R-21 = 纪律） |
| 检查清单（checkbox） | P0-1…P3 勾选 | 汇总 | 见各行；未勾选项 = **E-07 / E-08 / E-14 / E-18 / E-05 / E-17** |

> **注**：`REMEDIATION_PLAN` 的 `R-01…R-22` 与 `ISSUE_REGISTER_20260920.md` 同编号；`R-*`（问题）→ 本表 **E-08 / E-14 / E-17 / E-19** 等的映射见 **§九 9.2**。

### 11.3 其他"仍自称入口/待办"的文档（第三份及以后）——已加指针

> 全文检索（`docs/**` 与根目录）：**仅本表**自称"唯一交接入口"。下列文档含"接手入口/入口/待办/下一步"等表述，已按"**加指针、不改原文**"处理：

| 文档 | 自称形态 | 处置（本轮已加） |
|---|---|---|
| `docs/README.md:3` | "接手入口（2026-09-19）：HANDOVER_20260919.md" | 顶部加指向本表的指针行 ✓ |
| `docs/HANDOVER_20260919.md:6` | "配套索引：ARTIFACT_INDEX.md" | 顶部加指向本表的指针行 ✓ |
| `docs/ARTIFACT_INDEX.md:5` | "配套：交接正文见 HANDOVER_20260919.md" | 顶部加指向本表的指针行 ✓ |
| `docs/archive_pre202609/README_ARCHIVE.md:6-16` | "当前权威入口（只看这三处）" | 加指向本表的指针行 ✓ |
| `README.md:29`（根） | "open issues and remediation plan → ISSUE_REGISTER / REMEDIATION_PLAN" | 将该行注明"待办已并入本表" ✓ |
| `docs/README_HISTORY_pre20260920.md`、`docs/CURRENT_DYNAMIC_FUSION_STATUS.md` | 2026-08 旧主线"当前状态" | **不改**（`docs/README.md` §2 已标 historical）；仅登记 |
| `docs/AI_HANDOFF_*_CN.md`（20260911–20260914，7 份）、`docs/PROJECT_HANDOFF_AND_INNOVATION_STATUS_20260914_CN.md`、`docs/PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md` | 历史任务书/评审，"接手入口" | **不改原文**（历史登记）；本轮不列入待办入口 |
| `docs/ISSUE_REGISTER_20260920.md` | "问题归档"（非待办入口） | 保留；其 `R-*` 已由 **§九 9.2** 映射进本表 |

### 11.4 证据缺口与口径刷新登记（本轮逐条复核）

| # | 项 | 事实 / 处理 |
|---|---|---|
| **N-4** | 图 S4 入稿宽度：本表 §现状 #6 与 §六 #13 旧记"16 cm"，**现役 docx 实读 27 图全为 17.0 cm** | 已就地刷新（§现状 #6、§六 #13）；旧值为 09-21 时点 |
| **N-5** | `MASTER_TODO` §三（C 组标题/C-01/C-02/C-04/C-05/C-06）、§八 S5/S6、§九 9.3#5 仍写"58 页 deck / 第 20–21 页 / 原生页 1/2/3/12 / 20 表 22 图" | 已就地刷新为 63 页 / 第 23–24 页 / 原生页 1/2/3/15 / 23 表 27 图 |
| **N-6** | 本表 §六 #2 凭据行号 `build_methods.mjs:430` | 实读为 **:432**（已校正） |
| 证据缺口-1 | **A-12**（稳定性计划书"加密 N 网格却使最大值变小"） | **出处待补**：`docs/REFERENCE_FIG_CONVERGENCE_PLAN.md` 约 148 行的该段数值逻辑，本轮**未回原脚本/产物核实**（检索范围：`REFERENCE_FIG_CONVERGENCE_PLAN.md` 文本层面；未查 gen 脚本与 JSON）；**确认前不搬入论文** |
| 证据缺口-2 | **B-09**（图 S3 p3/p4 未登记 + 两处图件目录不一致） | 部分可核：`docs/paper_complete_review_20260920/figures/` 内确有 `panel_interaction_cases_p3/p4`（PNG+PDF，见本轮目录清单），`docs/figures_reference_matching_20260914/` 内**无**；`FIGURE_BINDING.md §一/§四` 是否已补登记**未逐行核** |
| 证据缺口-3 | **B-10**（Fig 5 记 "(a/b/c)" 三页 vs 盘上两页） | **未核实哪一方为准**（本轮仅确认 `docs/…/figures/` 有 `fig5a_budget_seed.png`、`fig5b_categories.png` 两页） |
| 证据缺口-4 | **D-13**（文献参照表须补 4 个引用键） | 实读 `scripts/…/references.json` **无** `adaptclip`/`remp_ad`/`efficientad`/`glass` 键 → 该表**尚未做**，D-13 仍为待拍板（可选） |
| 证据缺口-5 | **E-15 / E-19 / E-11 / E-12** 等红线区/历史提交层项 | 属"待作者拍板"，本轮**未重核**（不碰 `experiments/`、不重写历史）；状态沿用原登记 |

> **计数（§十一）**：`论文与图件问题汇总` **68 项** = 已完成/闭环 22 + 仍待办 30 + 纪律/不补 10 + 未使用 1 + 计划/校验 5；`REMEDIATION_PLAN` **46 项** = 已完成 9 + 仍待办 14 + 待拍板 12 + 纪律/限制 4 + 作者信息 7。**仍待办/待拍板条目全部已在本表有对应编号，无遗漏**。新增登记 **N-4…N-6**（口径/凭据刷新，均已就地修正）+ **5 处证据缺口**（如实标注，见上表）。

---

## 十二、2026-09-24 执行追加（M1–M6；本表其余内容一字未改）

> 完整记录见 [`docs/PAPER_REVISION_EXECUTION_20260924_CN.md`](PAPER_REVISION_EXECUTION_20260924_CN.md)。本节只做摘要与**口径刷新**，不改写本表任何既有行。本轮未跑实验、未用 GPU、未提交、未推送。

### 12.1 本轮执行（对应来源：`docs/PAPER_REVISION_HANDOVER_20260924_CN.md` 的 M1–M6）

| M | 内容 | 本轮结论 | 落地位置 |
|---|---|---|---|
| M1 | 表 11/12 表注**指向 Table S2** + 点名 SubspaceAD 256↔672 偏离 | **本轮执行**（原为未做） | `tables.json` 的 `baselines.note` / `baselines_ext.note` 各**追加一句**；**六列数值与其余字段一字未动** |
| M2 | 复现性（权重清单 / 最短路径 / 正文引用） | **已达标，未改** | `docs/MODEL_WEIGHTS.md`、`docs/REPRODUCE_TO_TABLES.md`、`manuscript.md:224,226`（与 E-07 一致） |
| M3 | Figure 7 续页补多方法对比图 | **本轮执行（+1 张 BTAD category 01）** | `figures.json` 的 `cases_bad.parts` / `part_captions`；`results.md:69` 描述同步（three→four / 33→32） |
| M4 | S5 首轮离群（30.527 s）披露 | **已做，未改** | `results.md:159`（对应 A-16 可判"已落"） |
| M5 | Discussion §5 点名同期 training-free 扩展并声明 scope | **本轮执行** | `results.md` §5 末追加一段（HyperFSAD / ReMem / DuoAD；**不同轴、不冲突、future work、不削弱 `0 target-trainable parameters`**；无 `SOTA/outperforms/state-of-the-art`） |
| M6 | A01 状态回填 | **本轮执行** | `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` §7.1 的 A01 行 = **部分满足（2026-09-24 回填）** + 追加"复核刷新"小结 |

### 12.2 口径刷新（**新旧并存，判断以本节为准**）

| 项 | 旧口径（本轮重建前，实测复核一致） | **新口径（2026-09-24 重建后，实测）** |
|---|---|---|
| 现役 docx | `Reference_Matching_Complete_English_20260923.docx`，SHA-256 `9B3E15F5…9245`，**55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 12 编号公式 / 34 文献 / 19,434 词** | 同名文件重出，SHA-256 **`820E8CD629B782B2575C26782B96E69A4390377E3EC41E27FEE1C7E3C0F9488A`**，**56 页 / 23 表 / 28 内嵌图 / 153 数学对象 / 12 编号公式 / 34 文献 / 19,729 词**（23 张表仍全部单页） |
| 备份 | — | `.bak_preM_20260924`（重建前件，仍在盘） |
| deck | `All_Figures_Complete_20260923.pptx`，63 页 | **未变、无需重出**：M3 新增的 BTAD 面板**本就在 deck 第 28 页**，未增删任何 slide；`FIGURE_SLIDE_INDEX.json` 仍 63 条、`图件与PPT页码索引.md` 仍 63 行 |
| 门禁 | — | `qa_layout.py` **0 problem**、`figure_font_gate --self-test` **4/4**、`pytest tests -q` **260 passed** |
| 红线 | — | 冻结共同区域表 `3C83AB00…`、扩展表 `1C770129…`、版式母本 `9DB99E60…` 未变；`0 target-trainable parameters` 仍在；`SOTA`/`outperforms` = 0；`state-of-the-art` 仅 2 处**否定语境**；`READONLY_PROOF.json` 的 `verdict` 未变 |
| 校验脚本 | `validate_revision23.py` 期望 27 图、整键比对表 11 | 已同步为 **28 图**、`Table11_values_unchanged`（只比对 `headers`/`rows`）；**该脚本本轮仍无法跑完**：在第 4 个 check `no_experiment_data_changes` 处中止（并行流程改了 `experiments/**`，非本轮所为），故 `REVISION_VALIDATION_20260923.json` **未重生成**，其数值仍是旧时点快照 |

### 12.3 本节新增的"登记过期"提示

- **A-16（S5 离群）/ A-14（图像级并列）/ B-01（多方法图入正文）/ A-13（逐方法协议）** 四条在 §一 / §四 4.1 中的"待做（零 GPU）"状态**已过期**，现役稿已落地（证据见 §十二 12.1 与 `PAPER_REVISION_EXECUTION_20260924_CN.md` §三）。
- **§现状 #1 / REVIEW_CHECKLIST A-22** 的"55 页 / 27 内嵌图 / 152 数学对象 / 19,434 词"为**重建前口径**；判断现役交付件请用 §12.2 的新口径。
- **§三 C-01/C-03/C-05/C-06、§八 S5/S6** 中的"每次图改动后必重出 deck"**本轮不触发**（本轮未改任何 deck 侧图件；论文侧仅新增对**既有**面板的引用）。

---

## 十三、2026-09-24 第二轮追加（A-01/A-19/B-04/B-05 图件；A-12/B-09/B-10 核实；C 组预注册；重建）— 本表其余内容一字未改

> 完整记录见 [`docs/PAPER_REVISION_EXECUTION_20260924_CN.md`](PAPER_REVISION_EXECUTION_20260924_CN.md) **§十三**；预注册见 [`docs/PREREGISTRATION_20260924_CN.md`](PREREGISTRATION_20260924_CN.md)。本轮未跑新实验、未用 GPU 计算、未改任何冻结数值、未提交/推送；未回退并行流程的任何改动。

### 13.1 本节对 §一/§三/§四 相关编号的状态刷新（只追加状态，不改原文）

| 编号 | 原状态 | 本轮（2026-09-24 第二轮） |
|---|---|---|
| A-01 图 2(c)/图 3(c) 压缩 | 待做 | **已执行**：`build_methods.mjs` 的 (c) 带高 232→176（图 2）、286→220（图 3），解释贴近公式；(b) 高亮几何与文字语义未动 |
| A-19 图 2 类别下标 `c` 正斜体 | 待做 | **复核为"已一致"，未改字面量**：图 2 的独占 `c` run 全为 `i=1`（斜体，与图 1 及正文一致），评审所述"第 2 页 i=0"在现役产物不复现 |
| B-04 图 S4 图内重复总标题/长说明 | 待做 | **复核为"已消除"**：S4 两页脚本均无 `suptitle`/`fig.text`；入稿用无图内标题版 |
| B-05 图 S4 符号/术语（`L` 称 local） | 待做 | **复核为"已消除"**：S4 用 `$I_{\mathrm{TRI}}$` 数学排版并写 `L denotes independent matching`；图脚本全文无把 `L` 称 local 的描述 |
| B-07 图件字号/版面门禁 | 待做 | **已过**：`qa_layout.py` **0 problem**（现役 layout，最小 11.29 pt）；`figure_font_gate.py --self-test` **4/4**。2026-09-22 记的 `fig2 ×2 / figS1 ×6 TEXT-OVERFLOW` 只在**过期 layout** 上复现，现役 layout 为 0 |
| A-12 稳定性计划书数值逻辑 | 待核实 | **不成立**（现役文本已写明"加密不会收紧上界"；数据/计算/区间范围均未改）；仅在该段加一句复核原委 |
| B-09 图 S3 第 5/6 页登记 + 两目录不一致 | 未核实 | **核实成立并补齐登记**（`FIGURE_BINDING.md §十四`）；`_p3`/`_p4` 只在现役入稿目录 |
| B-10 Fig 5 分页记法 | 未核实 | **以 2 页为准**（3 面板：(a)(b) 第 1 页、(c) 第 2 页）；只改记法 |
| A04/A08/A09/A11/A18/A22（D 组/§8.2） | 不补 / 待作者 | **分类完成**：A09/A18 属**文案限制句且已在稿**（零 GPU，无需新增）；A04/A08/A11/A22 **真需新计算且 > 2 h** → **只留预注册**（未跑） |

### 13.2 口径刷新（**判断以本节为准**）

| 项 | 改前（开工实读） | **改后（本轮实测）** |
|---|---|---|
| 现役 docx | `…_20260924.docx`，SHA `A8E3C129…7B92` | 同名文件重出，SHA **`77864633FD7672660243017B0A13C6F9A6860B519B99A1255B4A65205E2839F6`**，**56 页 / 23 表 / 28 内嵌图 / 154 数学对象 / 12 编号公式 / 37 文献 / 19,947 词**（23/23 表单页）。**23 表 / 28 图 / 56 页 三项不变**；数学对象/文献/词数的差异来自**并行流程**（references.json 34→37 等），非本轮图件改动 |
| 对比起点 `…_20260923.docx` | — | 仍在盘：`820E8CD6…9488A`，**56 / 23 / 28 / 153 / 12 / 34 / 19,729** |
| 图 2 / 图 3 PNG | `69D22086…` / `3F309ADB…` | **`F60EBC88…` / `F44656C4…`**；`figS1_encoders.png` 重渲染后**逐字节相同**（`FE182E11…`） |
| deck | `All_Figures_Complete_20260924.pptx`，`724F24E5…`，**64 页**，索引 63 条（与 md 64 行不一致） | 重出为 **64 页**，`CF889CAC…`（72,418,403 B），`finding_count = 0`；**`FIGURE_SLIDE_INDEX.json` 与 `图件与PPT页码索引.md` 均 64 条/行**（不一致已消除）；位图页 **60/60 与盘上 PNG 逐字节相同**；native 页 [1,2,3,16] |
| 本轮改动的 deck 页数注意 | 任务书基线 63 页 | 开工前已是 64 页（并行流程遗留）；本轮重出**保持 64**，未删页 |
| 门禁 | — | `qa_layout.py` **0 problem**、`figure_font_gate.py --self-test` **4/4**、`pytest tests -q` **260 passed** |
| 红线 | — | 冻结共同区域表 `3C83AB00…`（实为 `05_baselines_multi_dataset/baseline_common_region.csv`）、扩展表 `1C770129…`、版式母本 `9DB99E60…` 未变；表 11 六列与 HEAD 逐项相同；A1 parity `k2 0.343706` / `k4 0.388328` 未变；`0 target-trainable parameters` 仍在；`SOTA`/`outperforms`/`全面领先` = 0；`state-of-the-art` = 2 处**否定语境**；`READONLY_PROOF.json` 的 `verdict` 未变 |

### 13.3 本节新增的"登记过期"提示

- **§一 A-01/A-19/B-04/B-05/B-07** 与 **§四(4.1) A-12/B-09/B-10** 的"待做/未核实"状态**已过期**，按 §13.1 刷新。
- **§12.3 的 `A-22`**（"55 页 / 27 内嵌图 / 152 数学对象 / 19,434 词"）为**更早口径**；现役判断用 §13.2。注意 **`A-22` 在 `EXPERIMENT_GAP_ANALYSIS_20260922.md §7.2` 另有一义**（"统一几何下 PatchCore 塌缩为一列"，≈3.5 GPU 卡时）——两者不是同一件事，见 `PREREGISTRATION_20260924_CN.md §2.4`。
- **§三 C-01/C-03** 的"图件改动后必重出 deck 并复核索引"：**本轮已触发并执行**（图 2/3 原生页改动）：deck 重出 + 索引同步 + 逐页位图哈希核对全部完成。

---

## 十四、2026-09-24/25 收口清单追加（**本表其余内容一字未改**）

> 本节只做指针与计数，不重复论证、不改写上文任何行。

- **新增文档**：[`docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md`](PROJECT_CLOSURE_AUDIT_20260924_CN.md) —— 把上述 A–E 五组、`EXPERIMENT_GAP` A01–A23、`ISSUE_REGISTER` R-01–R-21、`REVIEW_CHECKLIST` §1/§2/§4、`PAPER_REVISION_*` M1–M6、`PREREGISTRATION`（A04/A11/A08/A22）、`REMAINING_REVIEW` 1–5 项**逐条清点、归类、给归属**，并**交叉核对**文档间状态冲突后统一为盘上实读。
- **计数（该文件 §〇）**：**已完成 12 组（覆盖 43 项验收）/ 需作者决定 18 / 需新写脚本·新实验 6（其中 A08 本轮执行中）/ 已作废·不补 13 组 / 仍无法核实 6 / 并行流程进行中 1**。
- **本轮之后仍开放的全部事项**：共 **22 条**（该文件 §四），其中**唯一可能被本轮执行闭环**的是 **#8 A08（full-pixel 区间）**；其余为**作者决策**（元数据、DOI、权重许可、表 A/B、命名修订的交付件重建等）或**超 2 h 的新计算**（A04/A11/A22）。
- **交叉核对新增发现（该文件 §三）**：13 处状态不一致已统一，其中影响判断的 4 处为 —— **① A01**（`§4.1`"仍缺" vs `EXPERIMENT_GAP §7.1`"部分满足" → 以后者为准）；**② 图 S6**（`§4.1`"未入稿" vs `§13.1`"已入稿" → 已入稿，docx 命中 4）；**③ deck 页数**（`§三/§八` 63 vs `§13.2` 64 → 现役 **64**，需同步 §三/§八）；**④ 命名修订**（本表"待拍板" vs `PRE_SUBMISSION_REVIEW_20260925_CN.md`"本轮已改名" → 源与图表层已改、现役 docx 未改）。
- **纪律**：本节未改任何实验数值、未动 `experiments/**`、未提交/推送；新增文本**不含**身份与称谓类禁用词。
```

---

## 十五、2026-09-25 A08（full-pixel 区间）**已完成**追加（**本表其余内容一字未改**）

> 本节**只追加**。本表内与 A08 相关的既有行——§4.1 登记表的 `A08` 行（"不补"）、§4.2 的 **D-03** 行（"不补"）、§九 9.2 的 `A08 → D-03` 映射、§十三 13.1 末行的 `A04/A08/A09/A11/A18/A22` 分类行——**一律未改动**；凡与 A08 现状冲突处，**以本节为准**（A08 已由"不补"转为 **已完成**）。

- **结论**：A08（full-pixel / stride-1 区间）**已完成**；原判"不补（结论不变）"作废，改为"本轮已执行并验收"。终产物落盘 mtime = **2026-09-25 16:28**（实读）。
- **命令**：
  ```
  .venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_fullpixel_ci.py --mode run --resume --stride 1 --replicates 1000 --datasets mpdd btad --output experiments\prereg_20260924\out\A08
  .venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\e1_report.py --dir experiments\prereg_20260924\out\A08 --strides 1
  ```
- **并行度 / 加速 / 收尾**：**6 shard** 并行、**20/20 单元、96/96 类别实例**；makespan **6502 s** vs 串行估算 **31136 s** ⇒ **实测加速 4.79×**（`state/A08_parallel_progress.json` 末行 `rate=4.7886`）；收尾为单实例 **N=1 纯汇总 6.1 s**（20/20 skipped、只跳不重算）。
- **产物**（`experiments/prereg_20260924/out/A08/`）：`point_stride1.csv` **56,941 B / `9A7F6F1846BCB9BE…`**；`replicate_stride1.npz` **1,963,505 B / `C96AFF40F09FAF8B…`**；`interaction_by_grid.csv` **2,271 B / `0DBFD0283D744350…`**；`E1_STATUS_stride1.json`（759 B）；`E1_REPORT_SUMMARY.json`（92 B）。
- **结构完整性**：`point_stride1.csv` = 1 表头 + **1248 行**（= 12×6×13 + 8×3×13 = 936 + 312），列 `dataset,seed,shot,category,method,pixel_ap`；0 空/NaN、0 重复键。
- **结论核对（98.75% 配对区间）**：MPDD `I_TRI` = **+0.007853 / +0.007741 / +0.007624**、`I_BAL` = **+0.006074 / +0.006172 / +0.006154**（stride 1/4/8 **三点均排除零**）；BTAD `I_TRI` = **−0.000169**、`I_BAL` = **−0.000864**（98.75% **均跨零**，与既有定位一致）。
- **两项如实登记**：① **BTAD 无归档可比对象**（归档 `E1_fullpixel_ci/` 只有 MPDD 的 stride-4/8）；② **`E_BAL_J`（MPDD）在 stride 1/4 排除零、stride 8 跨零**（符号始终为负，区间随网格变粗而变宽，未平滑）。
- **红线复核**：归档 `E1_fullpixel_ci/`、`p4_fullpixel/` **未改动**（`git status` 变更条目 **0 / 0**）；三个冻结哈希 `3C83AB00…` / `1C770129…` / `9DB99E60…` **未变**。
- **出处（完整记录）**：`docs/PREREGISTRATION_20260924_CN.md` **§五**、`docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md` **§二.1 C13**（该文件已把 A08 从"需新写脚本/新实验"移入"已完成"）。
- **纪律**：本节未改任何实验数值、未动 `experiments/**`、未提交/推送；新增文本**不含**身份与称谓类禁用词。

---

## 十六、2026-09-25 接手"命名修订轮"收尾（**只追加，本表其余内容一字未改**）

> 并行流程"2026-09-25 命名修订轮"（新标签如 `Dual-encoder baseline`）在 **17:18:50** 后停写，遗留"`All_Figures_Complete_20260925.pptx` 未生成 + `results.md` 两句 full-pixel 说明被 17:13 重写覆盖"。本节只记录接手完成的盘上实测；与本节冲突处**以本节为准**。

- **deck 补出**：`docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx`，**64 页 / 76,633,287 B / SHA-256 `0D9E5CB7667773C129BC1D90A95959DB70B20D050E173B1E88585982A077EA6F`**，`finalize_deck.mjs` **`finding_count = 0`**。
  - 前置补件：`docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260925.pptx`（**707,997 B / `9054C77F1D63E1FE5D0A127AE5BB063C716A5DAC3E3F05F50DFE89C17A24D71E`**），由 `finalize_figure.mjs` 从命名轮 `candidate_math.pptx` 产出。
  - 链路：`build_deck.mjs`（Built 64 slides）→ `assemble_deck.ps1`（Assembled 64 slides with native diagrams）→ `finalize_deck.mjs`。
  - 同步：`FIGURE_SLIDE_INDEX.json` **64 条**；`图件与PPT页码索引.md` **64 行**；deck 内 **61 个 `ppt/media/*`**，**60 个位图页与盘上 PNG 逐字节相同（60/60）**，原生页 `[1,2,3,16]` 非位图。
- **命名轮自带验收**：`check_delivery.py` **146 项全过** → `{"passed":146,"pages":60,"words":20465,"references":37,"math_objects":154}`；接手前它自报的唯一缺口是 `all_Word_images_match_current_sources`（命名轮 17:17 重渲染的 5 张图未进 17:16 的 docx）。
- **docx 复测**（`build.py`）：**60 页 / 23 表 / 28 内嵌图 / 154 原生数学对象 / 12 编号公式 / 37 文献 / 20,465 词**；SHA-256 `BCB9A086D8E5963C…C02139`（23,673,134 B）；改前备份 `…20260925.docx.bak_pre_handover_1755`（23,616,285 B）；23 张表全部单页。
- **两句落地**（`scripts/paper_complete_review_20260920/results.md` :56 / :174）：docx 空白归一化命中 `per-pixel (stride-one) resolution`、`zero-exclusion judgements are unchanged`、`full-pixel intervals are computed only for` **3/3**；**无** `full-pixel intervals remain unavailable`。
- **门禁**：`qa_layout.py` **TOTAL PROBLEMS: 0**；`figure_font_gate.py --self-test` **4/4**；`pytest tests -q` **260 passed**。
- **红线**：`3C83AB00…` / `1C770129…` / `9DB99E60…` ✓；A1 parity `k2 0.343706` / `k4 0.388328` ✓；`0 target-trainable parameters` ✓；新增文本禁用词 0 命中；**未 git add / commit**。
- **命名轮是否仍在写**：最后写盘 **17:18:50**（`scripts/paper_complete_review_20260920/figure_sources/build_methods.mjs`）；17:53 / 17:57 / 18:09 / 18:23 四次抽查**无**计算进程；`results.md` 未被再次覆盖（mtime 17:59:34）。
- **未做 / 不确定**：未重出 `paper.pdf` 与 `.tmp_revision_20260925/preflight/`（Word COM `Fields.Update()`+`ExportAsFixedFormat` 本机两次 >10 min 无输出，改跑等价 `Repaginate`+`ComputeStatistics` 写 `word_review.json`）。详见 `docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md §七`。

---

## 十七、2026-09-25 第三轮追加（**只追加，本表其余内容一字未改**）：paper.pdf 重出 + 措辞订正 + E-08 处置

> 完整记录见 [`docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md`](PROJECT_CLOSURE_AUDIT_20260924_CN.md) **§八**。与本节冲突处**以本节为准**（尤其 §十六 末行"未重出 `paper.pdf`"与 §十五/A08 相关的"60 页"口径）。

> **编号说明（2026-09-26 订正）**：本节与下文另一节（A22 / A04 / A11 执行结果）此前**同用「十七」**；现**本节保留 §十七**、那一节改为 **§十八**，**两节内容均一字未改**。两节主题不同：本节 = paper.pdf 重出 + 措辞订正 + E-08 处置；§十八 = A22 / A04 / A11 执行结果。

### 17.1 paper.pdf（已产出；口径刷新）

| 项 | 值（实读） |
|---|---|
| 产物 | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.pdf` |
| 页数 / 体积 / SHA-256 | **61 页 / 10,875,228 B / `89497729A950EF0DFB4AC9379B5E5664CAC106A561ADD9E2138C7B5B3C26718E`** |
| 生成引擎 | **WPS Office Writer COM**（`KWPS.Application` → `ExportAsFixedFormat(path,17)`，**11.5 s**；PDF 元数据 `Creator = WPS 文字`） |
| docx 自身页数 | **61**（Word COM `ComputeStatistics(2)`，**4.9 s**）⇒ PDF 与 docx **页数一致**；23 表仍全部单页 |
| Word 路径 | `ExportAsFixedFormat`（5 次尝试，2/12 参数、打印/屏幕优化、两种打印机）**11–45 分钟无输出**；同一 docx 的 Word 统计 4.9 s、一页对照文档导出 4.9 s ⇒ 仅该文档导出停滞 |
| 配方 | `scripts/paper_complete_review_20260920/export_review.ps1` 已改为 `-Engine wps`（默认）+ Word 统计；写 `.tmp_revision_20260925/pdf_export.json` |

> **口径刷新**：§十五（A08 追加）与 §十六 中沿用的"**60 页**"为**订正前**口径；措辞订正后 docx = **61 页 / 20,505 词**，判断请用本节。

### 17.2 措辞订正（过度概括 → 限定表述）

- **落点** `scripts/paper_complete_review_20260920/results.md:57`：原 `… so the zero-exclusion judgements are unchanged, and these per-pixel intervals are narrower than on the sparse grid.` → 新（限定）`… The zero-exclusion judgements for the two primary MPDD interactions and the two BTAD interactions are unchanged. At the 98.75% level their per-pixel intervals are narrower than the stride-eight intervals for the two MPDD interactions, whereas the two BTAD intervals are of comparable width to their stride-eight counterparts, one marginally narrower and the other wider by about 1%.`
- **原句不准确之处**：98.75% 区间宽实读（`prereg_20260924/out/A08/interaction_by_grid.csv` 与 `limitation_closure_20260915/A_btad03_corrected/interaction_dataset_stride8.csv`）—— MPDD 两项 stride-1 更窄；BTAD `I_TRI` 略窄（0.004726 < 0.004788）、`I_BAL` **略宽约 1.4%**（0.004789 > 0.004724）⇒ 不能写"全部更窄"。
- **`unchanged` 限定**：`E_BAL_J` 在 stride 1/4 排除零、stride 8 跨零，故该判断只限定在两项主交互及其 BTAD 对应项。
- **数值/表格/图件/文献一字未动**；docx 内新句命中、旧断言消失（空白归一化实读）。

### 17.3 复测与门禁

- **docx**（`build.py`）：**61 页 / 23 表 / 28 内嵌图 / 154 原生数学对象 / 12 编号公式 / 37 文献 / 20,505 词**；SHA-256 `E0D5462B347C4C44B5999D476DE26CFDCF35034438831D6A0861D004D8BA72F4`（23,673,208 B）。
- **交付验收** `check_delivery.py`：**146/146 全过** → `{"passed":146,"pages":61,"words":20505,"references":37,"math_objects":154}`。
- **门禁**：`qa_layout.py` **0 problem**；`figure_font_gate.py --self-test` **4/4**；`pytest tests -q` **260 passed**。
- **红线**：未改任何实验数值/冻结产物；未 `git add / commit`；新增文本禁用词 0 命中；未把"跨零"写成"零效应"。

### 17.4 E-08（复现包）状态刷新

- **处置**：包内**只放 URL + revision + SHA-256 清单，不放权重本体**（引用 `docs/MODEL_WEIGHTS.md` 46 项）。
- **已补**：`docs/REPRODUCE_TO_TABLES.md` 的"E-08 复现包"小节；`docs/REPRODUCIBILITY_PACKAGE.md` **§8**。
- **仍待作者拍板**（对应 §十一 的"需作者信息 7/8/11"与 §九 9.2）：`methods/` 的 (a)/(b) 方案、`VD1_MANIFEST.json` 的 `manifest_sha256` 回填、以及"是否再分发权重本体"。
- **§十一 检查清单**：`E-08` 仍为**部分闭环**（文档/清单侧完成，权重本体侧待作者决定）；`E-14 / E-18 / E-05 / E-17` 状态不变。

---

## 十八、2026-09-25 A22 / A04 / A11 执行结果（**只追加，本表其余内容一字未改**）

> **编号说明（2026-09-26 订正）**：本节**原编号为「十七」**，与上文 **§十七**（paper.pdf 重出 + 措辞订正 + E-08 处置）重复；现**本节改为 §十八**，上文 §十七 与其内容**一字未改**。两节主题不同，互指见各自首行。

> 作者批准执行 `docs/PREREGISTRATION_20260924_CN.md` 的 **A22 / A04 / A11**（§4.1 表内 A22/A04/A11 三行、§4.2 的 D-01/D-05/D-11 原登记为"不补（结论不变）"）。本轮按**预注册登记的口径**执行；三项**全部纯 CPU**（复用既有冻结 dump / canonical 特征），**未动 GPU**，全部新产物落 `experiments/prereg_20260924/out/A{22,11,04}/`，**未覆盖**任何既有目录。完整记录见 `docs/PREREGISTRATION_20260924_CN.md §七 / §八`（A11 见其追加节）与 `docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md §九`。

- **A22（§4.1 / D-11「统一几何下 PatchCore 塌缩为一列」）→ 已完成**：新脚本 `scripts/prereg_20260924/a22_patchcore_second_column.py`，**零重跑、零 GPU**（复用盘上既有原生 dump，在同一冻结区域网格上重采样重算），墙钟 **2078 s**；产物 `out/A22/` 六件（`A22_second_column.csv` 46,606 B、`A22_second_column_macro.csv` 1,849 B、`A22_collapse_vs_parallel.csv` 9,041 B、`A22_checks.json` 4,163 B、`A22_geometry.json` 16,840 B、`A22_STATUS.json` 2,411 B）。**契约核对逐行精确**：448 列 vs `harmonised_common_region.csv` **36 行 max|Δ|=0.0**；原生 224/128 列 vs `baseline_common_region.csv` **72 行 max|Δ|=0.0**。**结论**：36/36 单元上 448 ≠ 224、448 ≠ 128 ⇒「塌缩」是子表**单一输入几何前提**所致而非数值巧合；与 Figure S6 契约的 **128−224 差值符号 4/4 一致**。**⚠ 待作者追认**：把两张原生几何列并入"单一输入几何子表"属**前提变更**（区域未重裁、单元集不变，每行带 `geometry` 与 `NATIVE geometry - admitted only by the premise change`）。
- **A04（§4.1 / D-01「跨方法稳定性」）→ 已完成（口径待追认）**：新脚本 `scripts/prereg_20260924/a04_cross_method_stability.py`，墙钟 **520 s**、零 GPU；产物 `out/A04/` 五件（`A04_point_values.csv` 131,079 B / 432 行、`A04_stability.csv` 16,398 B / 64 行、`A04_cross_config.csv` 4,395 B / 8 行、`A04_checks.json` 18,611 B、`A04_STATUS.json` 2,569 B）。**契约核对**：六配置的**共同区域**读数 vs `baseline_common_region.csv` **216 行 max|Δ|=0.0**。**结论**：输入几何扰动下四个画布帧配置 Δ 一致为正（32/32 配置-组为正），两个 PatchCore 列 Δ≈0 且区间跨零 ⇒ **§2.1 成功判据判为"扰动下方向不一致"**（按 §2.1 如实报告，未改口径/未缩范围/未把跨零写成零效应）。**⚠ 待作者追认 4 项**：纵横轴定义、原生帧实现、区间网格、样本范围（MVTec AD / VisA 未纳入，因登记的原生帧产物只覆盖 MPDD/BTAD）。
- **A11（§4.1 / D-05「共享操作多条件消融」）→ 已启动，产物待回填**：新脚本 `scripts/prereg_20260924/a11_shared_op_ablation_multi.py`（**不改**既有 `e2_shared_op_ablation.py` / `e2_abl_s_addendum.py`，**不写**既有 `E2_shared_op_ablation/`），队列 `experiments/prereg_20260924/run_queue_a11.ps1`。口径 = 3 消融（ABL-S/ABL-N/ABL-C）+ baseline × seed 0、1 × K 1、2、4、8 ×（MPDD development / BTAD holdout），区间实现与抽样流**直接 import** 既有 `e1_fullpixel_ci`（`default_rng([20260913, dataset_id, category_id, replicate])`）。**门禁已过**：`--mode check` **21/21 pass、max|d|=9.5e-07**；单元级抽查与归档单条件交互 **max|Δ|=1.7e-18**。**一次失败已登记**：首版队列的 RAM 停止规则（单点 93%）在 19:12:42 因一次瞬时 95.4% 误杀两 shard（无 checkpoint 损失），已改为"连续 3 次 ≥96%"并重启；`sum_peak_ws`≈8.0 GB、`system_used` 峰值 82.8%、**显存 0 MiB**。**最终产物与结论见 `PREREGISTRATION_20260924_CN.md` 的 A11 追加节与 `PROJECT_CLOSURE_AUDIT_20260924_CN.md §九`。**
- **纪律**：三项均**不构成排名**（无 `SOTA / outperforms / state-of-the-art / 全面领先`）、`0 target-trainable parameters` 未受影响、**未在 KSDD2 上做任何新探索**；三个冻结哈希实读未变；**未 git add / commit**；本节新增文本禁用词自查 **0 命中**。

---

## 十九、2026-09-26 A11（共享操作多条件消融）**已完成**追加（**只追加，本表其余内容一字未改**）

> **摘要＋指向**：上文 **§十八** 记 A11 时状态为"已启动，产物待回填"。全量运行已于 **2026-09-26 01:46:24** 结束、收尾产出于 **01:46:41** 落盘 ⇒ A11 转为**已完成（含证据）**。完整数值见 [`docs/PREREGISTRATION_20260924_CN.md`](PREREGISTRATION_20260924_CN.md) **§九**；分类与计数刷新见 [`docs/PROJECT_CLOSURE_AUDIT_20260924_CN.md`](PROJECT_CLOSURE_AUDIT_20260924_CN.md) **§九 / §十**。

- **规模与耗时**：4 变体（baseline / ABL-S / ABL-N / ABL-C）× seed 0、1 × K = 1、2、4、8 × 2 数据集 ⇒ **16 单元 / 2,304 点单元格 / 128 条件行 / 16 汇总行**；2 路 shard **并行 20,995 s（≈5.83 h，纯 CPU，显存 0 MiB）**，收尾 `--mode assemble` 约 **17 s**。对比 §2.2 的 GPU 估算 ≈4–8 卡时：**成本估算未改，只登记实际值**。
- **产物**（`experiments/prereg_20260924/out/A11/`）：`ablation_metrics_multi.csv` **116,666 B**、`replicate_multi.npz` **3,873,040 B**、`interaction_by_ablation_condition.csv` **15,450 B**、`A11_multi_vs_single_condition.csv` **3,298 B**、`A11_STATUS.json` **1,054 B**（SHA-256 见预注册 §9.2）；单元检查点 **16 件**。
- **结构 / 口径**：三张 CSV **0 空 / 0 NaN / 0 重复键**；`replicate_multi.npz` = **512** 条长度 **1,000** 的宏平均数组。`stride = 8`、`replicates = 1000`、区间 = 逐单元**配对**宏平均后的 **2.5/97.5 百分位**、抽样流 `default_rng([20260913, dataset_id, category_id, replicate])`；**独立复算 128 + 16 行 max|Δ| ≤ 5.2e-18**。
- **多条件 vs 原单条件（探索性）**：**MPDD 8/8 行**区间排除零、与单条件同号；**BTAD 8/8 行**区间**全部跨零**（方向未定，**不得**读作"零效应"），其中 4 行反号 —— 但 `baseline`（**未消融**参考）在 BTAD `I_TRI` 上同样反号，故**反号不能单归于消融**。按 §2.2 判据：MPDD 三个消融均 ≥6/8 且无"反号且排除零" ⇒ 成立；BTAD 上 **ABL_C 触发**"反号且区间排除零"（I_TRI 3 + I_BAL 2）⇒ 按登记口径如实报告"该共享操作在部分条件下改变方向"，**不升格为"模块已验证"，也不降级为"模块无效"**。
- **装配缺陷已登记并订正（未改任何实验数值）**：首轮 `assemble` 因两处记账缺陷产出**空派生表**（日志 `0 condition rows; 0 aggregate rows`）—— ① `INTERACTIONS` 使用带 `_L` / `_J` 后缀的构造名，与点表 `construction` 列（无后缀）不匹配；② `_archived_single_condition()` 逐行覆盖、只留最后一个类别。订正后 `ablation_metrics_multi.csv` / `replicate_multi.npz` / `A11_STATUS.json` **逐字节未变**（SHA-256 与首轮清单相同），改变的只有两张派生表；**未重跑任何单元**。
- **需与结论同读的口径事实**：`I_TRI` 上 **ABL_C 与 baseline 逐格相同**（`naive_alpha` 在 `TRI` / `DUP` 槽位上与 `branch_weights` 数值一致）⇒ ABL_C 的可分辨信息只在 `I_BAL`；BTAD 每单元仅 3 类、区间宽约 3.0e-3–4.4e-3，可分辨程度低于 MPDD（6 类），**本轮不据此给跨数据集结论**。
- **红线**：`E2_shared_op_ablation/` 变更 **0** 项（`git status --porcelain`）；三个冻结哈希未变；**不构成排名**、不含领先或最优类措辞；`0 target-trainable parameters` 未受影响；**未在 KSDD2 上做任何新探索**；本节新增文本禁用词自查 **0 命中**。
