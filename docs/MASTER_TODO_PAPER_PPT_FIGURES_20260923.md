# 论文 / PPT / 图件 待办总表（唯一交接入口）— 2026-09-23

> **本表自 2026-09-23 起是交接的唯一入口**。其余文档按"历史登记"保留（**不删除**），只在顶部各加一行指针；本表不重复它们的论证，只做汇总、指派与去重。
> 编辑纪律：本表**不改任何实验数值**；`experiments/**` 证据字段、`data/**`、`LICENSE`、`requirements_repro.txt`、版式母本、`figure_sources/**` 科学内容为**红线**；冻结表/扩展表哈希见 **E-13**。

**现状（10 行内）**

| # | 现状 |
|---|---|
| 1 | **权威稿**：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx` = **47 页 / 20 表 / 22 内嵌图 / 12 编号公式（142 原生数学对象）/ 34 文献 / 17,221 词**；SHA-256 `DDB6602E1AA792C60743D4354FE90BFFE923E4BFF796CEB36971BA2528E8353B`（**非字节可复现**，见 E-09）。 |
| 2 | **唯一可编辑源**：`scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}` + 同目录 `build.py`；生成物 `docs/paper_complete_review_20260920/English_Manuscript_Source.md` **禁止直接编辑**（会被下次构建覆盖）。 |
| 3 | **图件命名与绑定位置**：以 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` 为准（正文图号 ↔ 图源 PNG ↔ 生成脚本 ↔ 冻结数据 ↔ PPT 页 ↔ 日期）；正文实际嵌入的副本在 `docs/paper_complete_review_20260920/figures/`。 |
| 4 | **PPT 位置与页数**：`docs/paper_complete_review_20260920/All_Figures_Complete_20260920.pptx` = **58 页**（第 1–22 页＝图 1–8 与 S1–S5；第 23–58 页＝36 张逐类别多方法附录）；新 deck SHA-256 `48DD9180…`（72,193,447 B，2026-09-22 重出）。 |
| 5 | **PPT 内嵌的是位图**：仅第 1/2/3/12 页为原生形状；其余 54 页为整页 PNG，**不随源文件更新**，改图必须用绘图脚本重渲染后**重出 deck**（F14 的教训）。 |
| 6 | **字号门**：`figure_manifest.json` 的 `minimumPrintPtAt17cm` = **11.294 pt**；正文契约 Times New Roman 11 pt、图宽 17 cm（图 S4 合并后按 16 cm 入稿）。 |
| 7 | **改稿纪律（必须）**：改源文件 → 跑 `build.py` → **复测**「47 页 / 20 表 / 22 内嵌图 / 12 编号公式 / 142 数学对象 / 34 文献」；图件改动 → 重跑 `qa_layout.py` + `figure_font_gate.py --self-test`；图件改动 → **重出 58 页 deck** 并同步页码索引。 |
| 8 | **冻结基线（不得改）**：冻结共同区域表 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`、扩展表 `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B`、`data/splits/*/manifest.json`、版式母本 `9DB99E60…`、表 11 六列数值与表注。 |
| 9 | **规模口径**：页数/表数/图数/公式数/文献数是稳定口径；docx 的 SHA-256 只是"某一次构建的快照"（F21）。词数最近一次 = **17,221**（A14 更正后重建）。 |
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
| B-03 | 图 S6（协议敏感度）**未入正文** | `论文与图件问题汇总…:539`；`FIGURE_BINDING.md §十`；python-docx 实测 `Figure S6` 命中 0 | 若入稿：在 `figures.json` 增设 S6 条目 → 重跑 `build.py` → 复测页数/表数；同步 `FIGURE_BINDING.md` §十与 `ARTIFACT_INDEX.md`；**须写明 5 条限制**（同口径 448 子集只覆盖 36/144、区间只 pixel_ap、不构成排名、杠杆数字是只读聚合、拉伸族不在子集内） | 作者 | 中 | 待拍板 | — |
| B-04 | 新 S4 图内重复出现总标题与长说明（与正式图注重复） | `论文与图件问题汇总…:96`（F03） | 论文插图用**无图内标题版**；带标题的"讲解版"另存不用于入稿 | AI | 中 | 待做 | 改动后须重出 PPT+docx |
| B-05 | 新 S4 符号与术语未沿用正文（`I_TRI`/`I_BAL` 文本式公式；`L` 被称 local） | 同上 `:97`（F04） | 按正文数学排版与术语表统一；`L` 称 **independent**，不得称 local | AI | 中 | 待做 | B-04 |
| B-06 | 若执行整批改名，6–12 张图需改图内标签并重渲染 | `NAMING_MIGRATION_PLAN_20260922.md:119-136`（§3.4） | 按 §3.4 清单改 `build_methods.mjs`、`plot_primary.py`、`plot_extra.py`、`plot_supplementary_figures.py`；**必须绕开 `C.*` 颜色命名空间**（`build_methods.mjs` 里 143 处 `C.xxx` 是颜色常量）；改后重跑字号门 | AI | 高 | 待拍板 | A-21 |
| B-07 | 图件字号/版面门禁要求（改标签后可能因折行失败） | `FIGURE_BINDING.md:74-88`；`NAMING_MIGRATION_PLAN…:136` | 任何图改动后必跑 `qa_layout.py`（`TOTAL PROBLEMS: 0`）与 `figure_font_gate.py --self-test`（4/4）；注意 2026-09-22 实测 fig2 有 **2 处**、figS1 有 **6 处** `TEXT-OVERFLOW`（保守折行估计，非可见裁切）需复核 | AI | 中 | 待做 | A-01、B-06 |
| B-08 | 生成物与溯源 JSON 内仍是旧绝对路径 | `FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md:158`（§6-8）；F19 未做项 | `fig7_multimethod_*.json`×16、`FIGURE_SLIDE_INDEX.json`、`figures/primary_sources.json` 的 `source` 绝对路径需**改生成器后重出**（本轮刻意未做——手改会与生成器失配） | 作者 | 低 | 待拍板 | C-01 |
| B-09 | **本表新发现**：`FIGURE_BINDING.md` 未登记图 S3 的第 5/6 页面板（`panel_interaction_cases_p3/p4`） | `图件与PPT页码索引.md:18-19`（PPT 第 18/19 页 = p3/p4）vs `FIGURE_BINDING.md §一`（S3 只列到 `_p2`）；`docs/paper_complete_review_20260920/figures/` 内确有 p3/p4，`docs/figures_reference_matching_20260914/` 内**无** | 补登记 §一/§四：写清 p3/p4 的生成脚本、冻结数据、门禁与为何两处目录不一致；核实是否需把 p3/p4 同步回 `figures_reference_matching_20260914/` | AI | 中 | 待做（本表新发现） | — |
| B-10 | **本表新发现·未核实**：T13 把 Fig 5 记为 "(a/b/c)" 三页，盘上只有两页 | `论文与图件问题汇总…:399-413`（`budget_category(a/b/c)`）vs `docs/paper_complete_review_20260920/figures/` 只有 `fig5a_budget_seed.png`、`fig5b_categories.png`；PPT 第 6/7 页也只对两页 | 核对 `figures.json` 的 `budget_category` 分页键与 PPT 第 6/7 页，统一记法（**未核实哪一方为准**） | AI | 低 | 未核实 | — |

> **已完成、勿重做（图件侧）**：F01（图2(b) 紫框已对齐 `build_methods.mjs:323`，`fig2` SHA `AB1EB3FD…`）、F02（图3(b) 权重措辞，`fig3` SHA `57362409…`）、P04（S4 ±5% 参考带 vs 6.8%，首个 N=700，`figS4` SHA `C4D2D0A0…`）、图 S6 生成与门禁（`0C6F801C…`）、图 6/7 字号 11.5 pt 修复、图 S3 版面修正。详见第五节。

---

## 三、C 组：PPT（58 页 deck 与索引）

| 编号 | 问题（一句话） | 证据 | **具体怎么改** | 负责人 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|---|---|---|
| C-01 | deck 与论文必须同步；任何图改动后旧 deck 即过期 | `论文与图件问题汇总…:204-206`（F14 教训）；`FIGURE_BINDING.md:445-466`（§九） | 重出链：`node scripts/paper_complete_review_20260920/figure_sources/build_deck.mjs` → `assemble_deck.ps1` → `finalize.mjs`；重出后核对 **58 页 / 0 finding**，第 20 页＝收敛（v2）、第 21 页＝稳定性 | AI | 高 | 待做（每次图改动后必做） | A-01、A-19、B-04、B-06 |
| C-02 | 若执行 T09 整批改名，deck、主图母版与索引须一并重出 | `NAMING_MIGRATION_PLAN…:138-145`（§3.5） | 重出 58 页 deck（`All_Figures_Complete_20260920.pptx`）、`docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx`（图 1 图内文字），页码不变则只复核索引 | AI | 高 | 待拍板 | A-21 |
| C-03 | 页码索引须与 deck 一致 | `docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json`、`图件与PPT页码索引.md` | 每次重出后复跑并核对（2026-09-22 实测：重出后 `图件与PPT页码索引.md` 哈希未变，证此前手写同步与真实结果一致） | AI | 中 | 待做 | C-01 |
| C-04 | **可编辑性纪律**：deck 只有 4 页是原生形状 | `论文与图件问题汇总…:106` | 第 1/2/3/12 页可在 PowerPoint 直接改；其余 54 页为整页 PNG，改图**必须**用绘图脚本重渲染，不能指望在 PPT 里改数据 | 交接说明 | — | 纪律 | — |
| C-05 | deck 第 23–58 页＝36 张逐类别附录，与 B-01/B-02 的口径需同步 | `图件与PPT页码索引.md:27-58`；`FINAL_ACCEPTANCE…:250` | 若 B-01 选代表图入正文、B-02 界定"两种输出"，附录页说明与图注须同步声明覆盖范围与色标规则 | AI | 中 | 待做 | B-01、B-02 |
| C-06 | 两份同源 deck 现**已不同源**，易误用 | `FINAL_ACCEPTANCE…:128`；`PROJECT_CLEANUP_AUDIT_20260922.md:95-96` | 现役 = `All_Figures_Complete_20260920.pptx`（新，`48DD9180…`，72,193,447 B）；`All_Figures_Finalized_20260920.pptx`（旧，`6EBD92E9…`，71,604,011 B）仅作旧版锚点；重出时二者关系须写清或明确废弃其中一份 | AI | 低 | 待做 | C-01 |

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
| A13 | 复现性：无最短路径 / 无权重哈希 | 仍缺（`docs/MODEL_WEIGHTS.md` 不存在，P1-1…P1-7 全未执行） | **是** | 天级文档 + 打包 | E-07 / E-08 |
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
| E-07 | 缺权重清单与"从零到表"最短路径 | `EXPERIMENT_GAP…:55`（A13）；`FINAL_ACCEPTANCE…:426-431` | 新建 `docs/MODEL_WEIGHTS.md`：逐权重给 URL / 固定 revision 或 commit / SHA-256 / 许可（46 条清单在 `dist/replication_package_20260920/weights/README.md`）；并在可得性节给出最短路径 | AI | 高 | 待做（零 GPU） | E-08 |
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

---

## 六、"已完成、请勿重做"清单（含凭据，防止下游重复劳动或误改）

| # | 已闭环项 | 凭据（提交号 / 文件 / 实测值） |
|---|---|---|
| 1 | F01 图2(b) 紫框与填色对齐 | `scripts/…/figure_sources/build_methods.mjs:323` = `addRect(slide,"f2-j-shared-highlight",113+2*42,…)`；重渲染 `fig2_matching.png` SHA `AB1EB3FD2B5172051F658929327BF7E81EE9F0FF16D9BC4DC2F753F269EFCBFB`（改前 `DA1E2251…`） |
| 2 | F02 图3(b)"只有 B 权重变化"措辞更正（图内 + 图注 + 正文） | `build_methods.mjs:430`、`figure_sources/figures.json` 的 `constructions.caption`、`manuscript.md:111`；`fig3_constructions.png` SHA `57362409BC04B2C30800EA74A06299AC01D4EA546C6FA7AD4E203EE40F72D185` |
| 3 | P04 图 S4 的 ±5% 参考带与实测 6.8% 分开表述 | `scripts/figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` 新增 `REFERENCE_BAND=0.05` 与 `first_settled_n`；**5% 判据下实测首个 N = 700**；JSON `headline.first_n_inside_5pct_reference_band = 700`；`max_relative_width_deviation_N_ge_500 = 0.067669…` 未改；门禁 61 个 text artist 全 11.50 pt；`figS4_bootstrap_convergence.png` SHA `C4D2D0A0…` |
| 4 | F14 58 页 PPT 已重出（第 20/21 页＝收敛 v2 / 稳定性） | `All_Figures_Complete_20260920.pptx` SHA `48DD91800B714331…`（72,193,447 B，58 页，0 finding）；索引 `FIGURE_SLIDE_INDEX.json` `A943E389…`；`图件与PPT页码索引.md` 复跑后未变 |
| 5 | F15 三份同源 PPTX 已删其一；`.bak_20260922` 亦已删 | 原三份字节相同（71,604,011 B / `6EBD92E9…`）；删 `Main_Figure_Editable_20260920.pptx` 释放 ≈68.3 MB；`.bak_20260922` 于 09-22 清理删除（与 `All_Figures_Finalized_20260920.pptx` 逐字节相同） |
| 6 | F17 权威 docx 与版式母本从 git 对象逐字节恢复 | `18694B90…` / `9DB99E60…` 与文档所记完全一致（成因：`a08dc46` 把 `*.docx` 加入 `.gitignore`） |
| 7 | T11 摘要末句 GitHub URL 入稿 | `manuscript.md:11`；重建后 docx SHA `68477175EC6C3287…`；Word COM 47 页 / 17,200 词 |
| 8 | T15 摘要 URL 与 Data and Code Availability 矛盾消除 | `manuscript.md:224` 现写 "…The public repository holding the code and the reproduction materials is https://github.com/USEU117/reference-matching-interaction-ad; a permanent archive DOI … has not yet been established."；全文仅两处出现该 URL、**无相反表述** |
| 9 | T16 命名温和版（T09 的 2a）已落地 | Table 1/2 各增 `Full name` 列（`tables.json` 的 `design`/`models` 两键）+ 正文首现加粗（token `[C,J,L,B,B,S,C,D,A1,DUP,TRI,BAL,E1,E2,E3]`）+ 图注首现全称；**未改任何字母、未重渲染任何图、PPT 未重出** |
| 10 | A14 AnomalyCLIP 检查点来源**结案**（纠正"本项目自训"错说） | 第一手 `docs/reproduction_notes.md:13-23`（2026-07-25，与归档下载同日）：检查点随上游源码归档（commit `3911738c…`，ZIP SHA256 `533ED87B…`）；30 个 `epoch_*.pth` mtime 全为 `2025-07-08 03:59:38`，本项目目录 2026-07-24 才建立 ⇒ **非本项目训练**；正确口径＝"prompt learner 在辅助域按上游配方训练、目标域零样本"；已逐处纠正 `dist/…/weights/README.md`、`REPRODUCIBILITY_PACKAGE.md`（含包内副本）、`BASELINE_EXPANSION_PLAN_20260921.md`、`EXPERIMENT_GAP_ANALYSIS_20260922.md`、汇总 P11 等 |
| 11 | T17 → A14 后 Table 12 协议列与表注改为**准确**表述 | 协议列 = `native, zero-shot on the target domain (upstream auxiliary-domain-trained prompt learner)`；表注删除"provenance recorded in … PREFLIGHT.json"；旧含糊写法命中 **0**、新表述命中 **3**；Table 12 **9 行数值一个未动** |
| 12 | T18 / F18 B 线（统一输入几何子集）完成并过门禁 | `experiments/…/05_baselines_harmonised_20260922/**`（表 A 180 行、表 B、`HARMONISED_SUMMARY.json`、`protocol_leverage.json`、`PREFLIGHT.json`）+ `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`；协议杠杆 **0.1000**（PatchCore 自身两配置，144 单元）> 家族差异 **0.0265**，**3.8 倍**；仅切 PatchCore 配置使胜负翻转 **48/144 = 33.3%**；图 S6 四道门禁（102 artists 全 11.50 pt、0 互压/0 压图/0 出页）、PNG 重渲染逐字节相同（`0C6F801C…`）；复用 4 列与冻结表 max_abs_delta = **0.0** |
| 13 | 图 S4 合并入 Word（v2 第 1 页 + stability 第 2 页，16 cm） | 数值零改动（复用已渲染 PNG）；重复的 `figS4_bootstrap_stability_part2` 移入 `figures/superseded/`；v2 第 1 页 PNG `6A542164…`（后经 P04 修订为 `C4D2D0A0…`） |
| 14 | 扩展表入正文 Table 12（原 12–19 顺延为 13–20，全文 20 表） | `05_baselines_ext_20260921/baseline_common_region_ext.csv` 1188 行（= 冻结 864 逐行照抄 + 新 324），SHA `1C770129…`；表 11 六列数值与表注**一字未改** |
| 15 | 权威稿重建（47 页 / 20 表 / 22 内嵌图 / 12 公式 / 142 数学对象 / 34 文献 / 17,221 词） | 当前 docx SHA `DDB6602E…`；备份 `.bak_20260923`、`.bak_20260922`、`.bak_authoritative_20260921`、`.bak_before_T11_20260922` 均在盘 |
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

---

## 七、"需作者拍板"清单（本节为唯一决策入口）

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

---

## 八、推荐执行顺序（拓扑序 + 前置依赖 + 回退）

| 步 | 动作 | 前置依赖 | 回退方法 |
|---|---|---|---|
| **S0** | **冻结基线**：对 5 个源文件 + `build.py` + 4 个图源脚本 + 全部 PNG + 2 个 PPTX 计算 SHA-256 并落 `.bak_20260923` | 无 | 逐文件还原 `.bak_<日期>` |
| **S1** | **决策冻结**：命名是否整批改（T09）、S6 是否入稿、8 项写作欠缺是否补、作者元数据、表 A/B 是否入稿 | S0 | 决策记录本身即回退依据 |
| **S2** | **正文与表格改动**：A-02…A-20 写作项 + A-06（T12 段落）+ A-13（Table 12 协议列/表注）+ A-17 表注口径 | S1 | `git checkout -- scripts/paper_complete_review_20260920`；docx 用 `.bak_20260923` 还原 |
| **S3** | **图件改动与重渲染**：A-01（(c) 压缩）、A-19（下标样式）、B-04/B-05（S4 图内）、B-06（命名联动，若 S1 决定执行） | S2（命名定稿） | 还原 PNG + 图源脚本备份；重跑脚本即可重建 |
| **S4** | **图件门禁复跑**：`qa_layout.py`（0 problem）、`figure_font_gate.py --self-test`（4/4）、图 S6 四道门禁 | S3 | 门禁失败 → 回到 S3 调版面；若 1 轮内调不好，**中止整批改名**，保留温和版交付 |
| **S5** | **重建 docx 并复测**：`build.py` → 复测 47 页 / 20 表 / 22 内嵌图 / 12 编号公式 / 142 数学对象 / 34 文献 | S2 + S3 | 用 `.bak_20260923` 还原 docx；`build_validation.json` 由重建刷新 |
| **S6** | **重出 58 页 deck + 同步索引**：`build_deck.mjs` → `assemble_deck.ps1` → `finalize.mjs`；核对 `FIGURE_SLIDE_INDEX.json` 与 `图件与PPT页码索引.md` | S3（S4 通过） | 直接还原旧 deck（`All_Figures_Finalized_20260920.pptx` 可作旧版锚点） |
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
| 5 | **表号两套并存（不互斥）** | `ACCEPTANCE_20260920.md` §一 #8 的 `tables 18 / figures 8` 属**已冻结旧链**（`scripts/manuscript_build_20260914/`）；权威链为 20 表 / 22 内嵌图。 |
| 6 | **字号门两套覆盖对象** | `qa_layout.py` 的 `TOTAL PROBLEMS: 0` 覆盖 7 张母版图（最小 11.29 pt）；20260920 方法图的字号门是 `figure_manifest.json` 的 `minimumPrintPtAt17cm` = 11.294 pt。两处不可读成同一批图。 |
| 7 | **同名字符串冲突（已过时）** | `ISSUE_REGISTER` R-11 "超前 15 提交"、R-20 "只两个方法家族"、`SCI_STRING_AUDIT` 的 `sci_project`、`论文与图件问题汇总` §一/§七 的 `18694B90…` / 16,892 词均为**历史值**（各文件已加刷新行/总注）。 |

---

## 十、版本与入口约定

1. **本表是唯一交接入口**：`docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md`（2026-09-23 起）。新增待办请追加到本表 A–E 五组，不要另建平行台账。
2. **其余文档按"历史登记"保留，不删除**（含 GPT 生成的总结）。仅在以下两处已各加一行指针：
   - `docs/论文与图件问题汇总_仅复核_20260921.md`（登记表：T/P/F/A 编号的来源）
   - `docs/REMEDIATION_PLAN_20260920.md`
3. **权威链**（改稿只动这几个）：`scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json}` + `build.py`；产物 `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`（47 页 / 20 表 / 22 内嵌图 / 12 公式 / 34 文献）。
4. **已 superseded（勿改、勿据其写作）**：`docs/manuscript_reference_matching_20260914/`、`scripts/manuscript_build_20260914/`（见其 `SUPERSEDED_20260921.md`）；`docs/replication_package_20260920/` 是**交付副本**，不是编辑源。
5. **文档地图**：图件绑定 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`；页码索引 `docs/paper_complete_review_20260920/{FIGURE_SLIDE_INDEX.json, 图件与PPT页码索引.md}`；下游写作指令 `docs/FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md` §13；命名方案 `docs/NAMING_MIGRATION_PLAN_20260922.md`；B 线写作说明 `docs/METHOD_COMPARISON_HANDOFF_20260922.md`；投稿元数据 `docs/SUBMISSION_METADATA.md`。
