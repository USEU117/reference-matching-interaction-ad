# 新稿（20260923 修订）按《核对清单》逐条核查报告 — 2026-09-23

> **本文件性质**：只读核查记录 + 一份新报告。**未改动任何稿件/产物**，未改实验数值，未跑实验，未用 GPU，未提交。
> **核查对象（最新稿）**：`docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx`
> **核对依据**：`docs/REVIEW_CHECKLIST_FOR_REGENERATED_PAPER_20260923.md`（§1 27 条 / §2 17 条 / §3 6 条 / §4 15 条 = 65 条）
> **工具**：python-docx / python-pptx(zip+lxml) / Word COM `ComputeStatistics` / PIL+numpy / 清单给出的 PowerShell 命令

---

## §0 最新稿认定（路径 / mtime / SHA-256 / 与上一版关系）

### 0.1 判定方法与候选扫描

- 扫描范围：`docs/**`（含未跟踪文件），排除 `.bak*`、`.tmp*`、`archive_pre202609/`、`figures_*`、`paper_writing_preparation_*` 等历史区；按 mtime 降序取候选，并核对内容特征（标题、`n=1..7` 章节、23 表 / 27 图结构）。
- 扫描命令：`Get-ChildItem -Path docs -Recurse -File -Include *.docx,*.md,*.json,*.pptx | Sort-Object LastWriteTime -Descending`

### 0.2 认定结果

| 项 | 值 |
|---|---|
| **认定的"最新稿"（交付 docx）** | `d:\STUDY\My_github\sci_project\docs\paper_complete_review_20260920\Reference_Matching_Complete_English_20260923.docx` |
| mtime | **2026-09-23 16:15:30** |
| 大小 | 32,489,505 B（32.5 MB） |
| **SHA-256** | **`7C686C7F58D585CD35C7DC125A4742D22CE74825D86767251B77AE71F2CF7DC5`**（与 `REVISION_VALIDATION_20260923.json:147` 自报值一致） |
| 同批"最新稿"（配套） | 可编辑源 `scripts/paper_complete_review_20260920/{manuscript.md, results.md, tables.json, figures.json, references.json, build.py}`；docx 源 `docs/paper_complete_review_20260920/English_Manuscript_Source.md`（16:15:30）；图件 deck `docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx`（16:15:38，SHA `893F0F2A…2FB896`）；自报校验 `…/REVISION_VALIDATION_20260923.json`（16:17:05） |
| 与上一版关系 | **同一目录下新增文件（非覆盖）**。上一版 `Reference_Matching_Complete_English_20260920.docx` 仍在（mtime 2026-09-23 10:20:06，27,725,875 B，SHA `DDB6602E1AA792C60743D4354FE90BFFE923E4BFF796CEB36971BA2528E8353B`）。新版 deck 亦为新增（旧 `All_Figures_Complete_20260920.pptx` 保留）。 |
| 唯一性 | **无多个候选歧义**：`docs/` 下 16:00 之后被改动的 .docx 只有这一个；`.pptx` 只有 `All_Figures_Complete_20260923.pptx`；无更晚的 docx/md 稿件候选。 |

### 0.3 与上一版基线的规模差异（Word COM 实测 + python-docx）

| 口径 | 清单基线（20260920） | 最新稿（20260923） | 差异 |
|---|---|---|---|
| 页数（Word COM `ComputeStatistics(2)`） | 47 | **55** | +8 |
| 表数（python-docx / Word COM） | 20 | **23** | +3（新增 Table 21 图像级指标、Table S1 同口径子集、Table S2 逐方法协议） |
| 内嵌图（`inline_shapes`） | 22 | **27** | +5 张文件 / +7 个版面（Fig 7 增 3 张类别面板、图 S3 增 p3/p4、图 S6 两页） |
| 原生数学对象（`m:oMath`） | 142 | **152** | +10 |
| 编号公式 | 12 | 12 | 0 |
| 文献 | 34 | 34 | 0 |
| 词数（Word COM `ComputeStatistics(0)`） | 17,221 | **19,169** | +1,948 |
| PPT deck 页数 | 58 | **63** | +5（第 1–27 页 = 27 图面板；第 28–63 页 = 36 张逐类别附录） |

**结构变化摘要**：新增 `§5 Discussion` 独立章节（正文 1–4、5、6、7 连续）；Results 按四组重排（4.2.1 主效应与交互 / 4.2.2 验证与确认 / 4.2.3 敏感性与稳健性 / 4.2.4 资源与限制）；新增 `## Supplementary Protocol Tables`（Table S1/S2）；Table 11 表注与六列数值**字节级未改**（`git show HEAD` 比对 `baselines`/`baselines_ext` 两键 `identical=True`）。

---

## §1 清单 §1（可自动核查，27 条）逐条判定

> 判定取值：`通过` / `部分通过` / `不通过` / `未核实`。每条含"执行了什么 / 实测结果"。

### 1.1 A-01 … A-14

| 编号 | 检查项 | 执行了什么 | 实测结果 | 判定 |
|---|---|---|---|---|
| A-01 | 摘要末句仓库 URL | `Select-String manuscript.md 'github.com/USEU117'`；python-docx 读 `paragraphs[5]` | 源侧 **2 处**（manuscript.md:11 摘要、:226 可得性节）；docx `paragraphs[5].text` 以 `…available at https://github.com/USEU117/reference-matching-interaction-ad.` 结束；docx 内 URL 出现在段 5 与段 240 | **通过** |
| A-02 | 摘要 URL 与 Data and Code Availability 不矛盾 | `Select-String -Pattern 'no repository URL\|no archive DOI\|has not yet been established\|is claimed'` | 命中仅 manuscript.md:226 的 `a permanent archive DOI for the complete study has not yet been established`（允许且应保留）；`no repository URL` / `no … is claimed` **0 命中** | **通过** |
| A-03 | Table 1/2 均有 `Full name` 列 | `Select-String tables.json 'Full name'`；python-docx 统计"表头第 2 列 == Full name" | 源侧 `design`/`models` 两键；docx 内命中表索引 **[0, 1]**（恰 2 张） | **通过** |
| A-04 | 正文单字母首现带全称且加粗/斜体 | python-docx 收集 `run.bold and len(token)≤3`；并逐段找首现 | 加粗短 token 集合 = `{A1, B, BAL, C, D, DUP, E1, E2, E3, J, L, S, TRI}`（= 清单预期集合，完全一致）；C/J/L 正文首现在 §2/§3.1 为加粗；B 首现 §3.2 `duplicate the **B** descriptor`、S/D 首现 §3.4 均加粗；图注（Fig 1）首现给全称 `B and C denote DINOv2-B … S and D denote DINOv2-S and WideResNet50-2`。**未执行整批改名**，故按"首现强调"判据 | **通过** |
| A-05 | 图内无重复总标题（F03） | 原生图：解压 deck `slide{1,2,3,15}.xml` 搜 `a:t` 含 `Figure \d`；matplotlib 图：核 `figure_sources/*.py,*.mjs` 是否残留 `suptitle`/`Figure N` 标题；manifest 顶部元素 | 第 1/2/3/15 页幻灯片上**无** `Figure N` 文本（仅面板标签，如 Fig 2 顶部元素 `(a) One query patch and the common candidate set`，y=18/size=36）；绘图脚本中 `suptitle` 仅出现在"被正则删掉"的补丁语句里（`plot_extra.py:40,46`），无生效总标题 | **通过**（机器旁证 + 源脚本核验；未做 OCR） |
| A-06 | 图内符号/术语与正文一致 | `Select-String figures.json,*.mjs,'local matching'`（并扩大到 manuscript.md / English_Manuscript_Source.md） | `local matching` **0 命中**（docx 正文 `.lower().count()` 亦 0）；`I_TRI`/`I_BAL` 在 `tables.json`/正文均以 `$I_{TRI}$` 数学对象书写，docx 内为原生 `m:oMath`（152 个） | **通过** |
| A-07 | 图 2(b) 高亮与图例自洽（F01） | `Select-String build_methods.mjs 'f2-j-shared-highlight'`；`Get-FileHash fig2_matching.png` | 机制项命中：`build_methods.mjs:323 addRect(slide,"f2-j-shared-highlight", 113 + 2*42, 512, 42, 102, "none", C.violetLine, 3)` → 偏移量 = `113+2*42` ✓；**但哈希不符**：盘上 `fig2_matching.png` = `5156E610A1041FB08640960ED202475E1DEA4CD5EC254A85610308B9576C58E6`，清单（及 `MASTER_TODO…:69` "已完成勿重做"）记录为 `AB1EB3FD2B5172051F658929327BF7E81EE9F0FF16D9BC4DC2F753F269EFCBFB` | **部分通过**（机制在位、记录哈希已被 revision23 重渲染取代；未复核紫框 x∈[195.5,240.0] 与填色格 x∈[200,238] 的像素重合） |
| A-08 | 图 3(b) 权重表述准确（F02） | `Select-String` 新/旧表述；`Get-FileHash fig3_constructions.png` | 旧表述（`only B` / `only the B weight`）**0 命中**；新表述为"图内字面量 + 图注 + 正文"三处语义一致：`build_methods.mjs:432 "Only the weight split changes: B 1/2→2/3, C 1/2→1/3."`、`figures.json:13 "(b) A1 to DUP changes only how the fixed weights are split…"`、`manuscript.md:111 "Comparing DUP with A1 changes only how the fixed weights are split…"`（字面串"Only the weight split changes"仅 1 处，其余 2 处为同义改写）；**哈希不符**：盘上 = `3F309ADB57D294E740F0C11E5085248A2CBB854F0E4932734758CF3A9AEDE6FD`，清单记录 = `57362409BC04B2C30800EA74A06299AC01D4EA546C6FA7AD4E203EE40F72D185` | **部分通过** |
| A-09 | 图 2 类别下标斜体一致（F11） | 解压 `All_Figures_Complete_20260923.pptx`，读 slide1/2/3 中 `a:t == "c"` 的 run 的 `rPr/@i` | slide1: `{'1'}`、slide2: `{'1'}`（全斜体）、slide3 无 `c` 下标 run；`i="0"` 残留 **0** | **通过** |
| A-10 | 图 2(c)/3(c) 空白与文字密度 | 核 `REVISION_VALIDATION_20260923.json.panel_c_measurements` + 自算 ink；核 `figure_manifest.json` 中 (c) 带文本元素数 | fig2 c_height_fraction **0.2189 ≤ 0.22**、fig3 **0.2698 ≤ 0.28**；c 区 ink（RGB<140）**0.0406 / 0.0654 ≥ 0.02**（自算复现一致）；(c) 区非空文本元素 **2 / 4 ≤ 4**（`section-c` + 说明；fig3 为 `section-c` + `f3-effects-title` + `f3-interactions-title` + `f3-pairing-note`）；内容为"序约束说明 / 四对比命名"，非重复公式填空 | **通过**（备注：`c_height_fraction` 由声明的面板几何 `h/1060` 得出，非从像素反测） |
| A-11 | 图件字号门 | `python scripts\figures_reference_matching_20260914\qa_layout.py`；`figure_font_gate.py --self-test`；`python scripts\harmonised_20260922\build_figS6_protocol_sensitivity.py --out-dir <TEMP>` | `qa_layout`：`TOTAL PROBLEMS: 0`，各图 min = **11.29 / 11.50 pt**（floor 11.0）；self-test：`self-test passed: 4 controls behaved as required`；figS6 生成：102 text artists **11.50 pt**（floor 11.5）+ 无重叠/无出界；`figure_manifest.json → minimumPrintPtAt17cm` = **11.294291338582678**（位于 `.tmp_complete_figures_20260920/methods/`）。**但**：`qa_layout.py` 默认 `--layout-dir=scripts/figures_reference_matching_20260914/layouts`（frame **1280×900**）与 `--figures-dir=docs/figures_reference_matching_20260914`，而当前入稿图件在 `docs/paper_complete_review_20260920/figures/`（frame **1280×1060**，如 fig2 为 2560×2120）；逐文件哈希比对：入稿图件与门禁目录版本**全部不同**（fig1/2/3/8/S1/S2/S4/S5 均 diff） | **部分通过**（门本身 0 问题、self-test 4/4、manifest 11.294 达标；但门未在当前入稿渲染上复跑——见 §6 高优先项） |
| A-12 | 正文字号 / 表字号 / 图宽 | python-docx：`styles['Normal']`、表格 run 字号、`inline_shapes[i].width` | 正文 Times New Roman **11.0 pt** ✓；表单元 run 字号集合 = **[9.5]** ✓；27 个内嵌图宽度集合 = **[17.0 cm]**（S4 亦 17 cm，**非**清单要求的"S4 合并版 16 cm"） | **部分通过** |
| A-13 | 三线表 | 逐表解析 `tblBorders`/`tcBorders`，统计非 `nil` 的 left/right/insideV/insideH | 23 张表 **非 nil 边框命中 0**（表级 top/bottom 与表头下横线由 `tcBorders` 直接给出） | **通过** |
| A-14 | A1 对照行加粗且注明非统计最优 | python-docx 读 Table 1 行/运行加粗；逐表核表注是否含"非最优"类限定 | Table 1 第 2 行（A1）整行 `bold=True` ✓，表注含 `not a claim of best performance` ✓。**带 A1 加粗行的表中 3 张缺限定语**：Table 4 `main` 表注仅 "Bold identifies the A1 anchor."、Table 5 `matching` 同、Table 8 `d_full` 仅 "Bold identifies A1."（Table 11 有 `not a statistical superiority claim`、Table 20 有 `not the fastest or best result`、Table 21 有 `not statistically optimal`、Table S1/S2 有 `not optimal`） | **部分通过** |

### 1.2 A-15 … A-27

| 编号 | 检查项 | 执行了什么 | 实测结果 | 判定 |
|---|---|---|---|---|
| A-15 | 案例图"两种输出"且范围界定（F06） | `Select-String figures.json 'two outputs\|contour\|all cases'`；读 results.md/figures.json 相关段落 | 明写界定："The initial five A1 cases are the only main-text examples that show both a continuous map and a predicted contour."、"The two-output presentation of a continuous map plus a predicted contour applies only to the five main-text A1 cases in Figures 6 and 7."；Fig 7 续页图注写明 "No method-specific thresholded contours are supplied on this page."；**无**"所有案例都有两种输出"式表述 | **通过** |
| A-16 | 主图可编辑（PPT 原生形状） | 解压 deck，统计每页 `p:sp` / `p:pic` | 原生页 = **[1, 2, 3, 15]**（sp=122/133/74/65，pic=6/0/0/0）；其余 **59 页**为整页单图（sp=0, pic=1）。与清单的"第 1/2/3/12 页原生"不同（第 12 页现为 Fig 7 位图，原生页移到第 15 页） | **通过**（边界如实标注：59/63 为整页 PNG，不随源更新） |
| A-17 | PPT 与论文同版 | 读 `FIGURE_SLIDE_INDEX.json`、`图件与PPT页码索引.md`、deck 实际页数 | deck = **63 页**（清单要求 58）、索引 = **63 条**（自洽）、`图件与PPT页码索引.md` = 63 行表（自洽）；但"第 20 页 = 收敛 v2、第 21 页 = 稳定性"已不成立：现 **第 23 页 = figS4_bootstrap_convergence、第 24 页 = figS4_bootstrap_stability**（第 20/21 页为 S3 的 p4/p5）；docx 内 S4 两页与索引第 23/24 页为同源文件 | **部分通过** |
| A-18 | 禁写清单扫描 | `Select-String English_Manuscript_Source.md -Pattern 'SOTA\|state-of-the-art\|…\|FPS'`；逐命中判语境 | 命中 5 处，**全部为否定语境**：`:81 not a hyperparameter-free system`、`:297 not evidence that … globally optimal`、`:497 makes no ordering, interval, significance-test or state-of-the-art claim`、`:514 not end-to-end per-image latencies`、`:783 makes neither a ranking nor a state-of-the-art claim`；docx 正文命中 4 处，语境同上。肯定断言 **0** | **通过** |
| A-19 | 表 11/12/子集表均写"不构成排名" | `Select-String tables.json 'ranking'` | Table 12 表注 `is not a ranking` ✓；Table S1 表注 `This is not a ranking or a significance comparison.` ✓；**Table 11 表注无 ranking 字样**（仅有 `Bold identifies A1, not a statistical superiority claim.`）；正文有等价表述（`manuscript.md:184 … does not isolate the matching factor or support a comprehensive cross-method ranking.`） | **部分通过** |
| A-20 | 逐方法协议（含 SubspaceAD 256↔672） | 读 `tables.json.method_protocols`（Table S2）+ `manuscript.md` 补充节 | Table S2 逐方法列出 9 个配置的输入几何 / 增强 / 参考构造；表注写明 `SubspaceAD uses 256-pixel fp16 inputs without augmentation; its upstream few-shot script specifies 672 pixels and aug_count = 30 … The local 256 setting is therefore explicitly a deviation.`；表 12 protocol 列写明 `native, zero-shot on the target domain (upstream auxiliary-domain-trained prompt learner)`；正文另附上游 ZIP SHA256 与 commit | **通过** |
| A-21 | 冻结值未漂移（红线） | `Get-FileHash` ×3；`git status --porcelain -- data/splits`、`-- experiments data` | 冻结表 `3C83AB00…A0B8BB` ✓；扩展表 `1C770129…73EC4B` ✓；版式母本 `9DB99E60…8FB837` ✓；`data/splits` 与 `experiments`+`data` 输出**均为空** | **通过** |
| A-22 | 规模口径复测 | python-docx（表/图/math/refs）+ Word COM（页/词） | **23 表 / 27 内嵌图 / 152 数学对象 / 34 文献 / 55 页 / 19,169 词**；清单判据为 `20 表 / 22 内嵌图 / 142 数学对象 / 34 文献 / 47 页` | **不通过**（口径已系统性扩大；非冻结值违规，`experiments/**`、`data/**` 未动） |
| A-23 | 图 S6 入稿且口径一致 | `python -c "…sum('Figure S6' in p.text…)"`；读补充节 | `Figure S6` 命中 **4**（≥1，入稿）；5 条限制在 `Supplementary Protocol Tables` 与 Table S1 表注同时写明：①短边 448 同口径子集 ✓ ②36 / 144 单元 ✓ ③区间只针对 pixel AP（非 AUROC）✓ ④`makes neither a ranking nor a state-of-the-art claim` ✓ ⑤方形拉伸族 SubspaceAD / WinCLIP+ / zero-shot AnomalyCLIP 被排除 ✓ | **通过** |
| A-24 | 图 S5 首轮离群披露 | `Select-String results.md '30.527'` | 命中 1 处（`results.md:159`）：明确区分首轮 `30.527 s` 与重测 `24.190 s`，并指向 `…/_bench_speed_vram/recheck/`；同段声明 min–max 只是该受限流程的观测范围 | **通过** |
| A-25 | 生成物旧绝对路径残留 | `Select-String figures.json, English_Manuscript_Source.md -Pattern 'My_github'`；并扩查 `fig7_multimethod_*.json`、`FIGURE_SLIDE_INDEX.json`、`primary_sources.json`、`portable_metadata_revision23.json` | 人工可读面 **0 命中**；**生成器溯源面亦 0 命中**（清单预期"可能仍有残留并需登记"的情况本轮不存在） | **通过** |
| A-26 | 单元测试 | `.venv-anomalyclip\Scripts\python.exe -m pytest tests -q` | **`260 passed, 1 warning in 47.48s`**（0 failed） | **通过** |
| A-27 | 仓库自检 | **未执行** | `scripts\representation_matching_interaction_20260914\selfcheck.py:339,516` 会就地把 `experiments/dynamic_fusion/representation_matching_interaction_20260914/{READONLY_PROOF.json, SELFCHECK.json}` 写回。任务硬约束"不改动任何稿件与产物"，且清单要求的"跑完必须 `git checkout --` 还原"本身便是破坏性操作，故**主动不执行** | **未核实**（未执行；原因见左） |

---

## §2 清单 §2（语义/人工判定，17 条）

| 编号 | 判定项 | 依据（页/表/图/行） | 判定 |
|---|---|---|---|
| M-01 | 对比方法为何无需在目标域训练（成体系、区分零梯度≠零计算） | `manuscript.md:186` 独立整段（约 200 词）：①目标域无梯度优化/无目标损失 ②预训练编码器与继承检查点**仍带上游训练来源**，含 `the separate zero-shot AnomalyCLIP baseline uses an upstream auxiliary-domain-trained prompt learner … zero-shot on the target domain` 与 `They were not trained by this project` ③参考库/coreset/特征编码属**准备计算**；并显式写 `no target-domain gradient update should not be read as no previous training, no preparation work or no configuration choices`；VisA in-domain 在 §4.1.1 单列 | **通过** |
| M-02 | 图 2(c)/3(c) 信息密度合理、不靠装饰填空 | (c) 面板文本元素 2 / 4 个，内容为"序约束 L≤J 及其含义"与"四对比命名 + 配对说明"，靠近其所属模块；删去后序约束与对比定义将无处解释 | **通过** |
| M-03 | long paper 篇幅与组织 | 标题层级实测：`4.2.1 Main Effects and Interactions / 4.2.2 Validation and Confirmation / 4.2.3 Sensitivity and Robustness / 4.2.4 Resources and Limits`（四组）→ `5 Discussion`（独立，位于 Results 之后 Conclusion 之前）→ `6 Conclusion` → `7 Data and Code Availability`；纯审计小节（几何核对、稳定性）压成段并指向 Fig S2/S3/S4 | **通过** |
| M-04 | 检测/定性图进正文结果分析 | Fig 7 续页 3 张代表图：MPDD metal_plate（表面/划痕）、MVTec AD grid（纹理/胶）、VisA pcb1（电路），跨数据集 + 跨缺陷类型；含 query、GT、各方法热图；图注写明 `Query and GT are followed immediately by the two A1 columns`；选择规则 `largest AP spread across the six displayed configurations, with ties broken by sample identity` 与色标规则 `one shared magma minimum–maximum range` 均写明；其余 33 张留附录 | **通过** |
| M-05 | 解释篇幅不挤占主线 | 逐方法配置移入 Table S2（补充材料）✓；正文 §4.1.2 为单段 ✓。**但**本版把 VisA 边界表述改写：`finish_text_revision23.py:13-14` 将原句 `the inherited checkpoint still carries its training-data provenance, so removing text at inference does not turn an in-domain dataset into an unseen-domain test.` 换成 `… We retain the historical in-domain designation for VisA conservatively, without attributing the C descriptors to prompt learning or claiming an untouched-domain test.`，§4.1.1 另加 `This designation is not evidence that the prompt checkpoint changes C descriptors.` | **部分通过**（篇幅无问题；但属清单列明的"为消解旧稿冲突而放宽已澄清的边界表述"形态，需作者确认口径与其他段落一致） |
| M-06 | 稳定性替代图表述边界 | `figures.json.stability` 图注 + `results.md:151`：写明 1000 是参照值非真值；±5% 参考带**不是**预设通过标准；实测最大偏离 6.8%（N≥500）、17.1%（N≥200）；前缀相互依赖；显式声明"不代表训练收敛、也不代表所有对比方法稳定" | **通过** |
| M-07 | S5 计时边界 | `results.md:155-161` + `benchmark` 表注：明说为**阶段计时之和**（含参考库工作，排除模型/数据装载、指标评估、写盘）；`not end-to-end per-image latencies`；显存区分进程内 allocated peak 与 1 Hz nvidia-smi 设备级观测；未出现 ms/image、FPS | **通过** |
| M-08 | 区间口径 | `baselines`/`s_interaction`/`harmonised` 表注：区间只针对 `pixel_ap`；full-pixel `No full-pixel confidence intervals were computed`；子集表明写 `marginal 95% intervals, and are neither family-adjusted nor paired cross-method difference intervals` | **通过** |
| M-09 | BTAD 口径 | `results.md:111`：`the current data are insufficient to determine the direction of the interaction there`；`tables.json.generalization` 表注 `must not be read as four consistent significant replications`；全文无 `true null` / `essentially zero` | **通过** |
| M-10 | correspondence 表述 | BTAD 段写作 `All fourteen intervals span zero, so on this dataset neither replacing the correspondence nor changing the amount of smoothing in the transport rule changes the judgement` ✓；**但** MPDD 段写作 `so that a reader can see that neither the sign nor the interval separation of the interaction depends on that constant.`（`results.md:143`）——"the interval separation … does not depend on that constant"强于清单允许的"零排除判定保持" | **部分通过** |
| M-11 | 命名可读性 | Table 1/2 有 `Full name` 列；正文首现加粗 + 括注全称（B/S/C/D、A1/DUP/TRI/BAL、J/L、E1–E3）；Fig 1 图注亦给全称 | **通过** |
| M-12 | 摘要压缩与缩写展开 | 摘要展开 `Metal Parts Defect Detection (MPDD)`、`BeanTech Anomaly Detection (BTAD)`，未堆层号/型号；`Keywords:` 恰 **5** 个（few-shot anomaly localization / frozen visual encoders / normal reference matching / fixed feature fusion / representation interaction）；MVTec AD 与 VisA 属公知缩写 | **通过** |
| M-13 | 参考文献年份与格式 | `references.json` 34 条年份分布：2019×2, 2021×7, 2022×2, 2023×3, 2024×7, 2025×6, 2026×7 → **2024–2026 = 20/34 = 58.8%**（2023–2026 = 67.6%），低于清单参考区间 70–80%；DOI 是否统一**未核实**（未逐条比对 DOI/卷期/大小写） | **部分通过**（非硬指标，但不达标；未因凑比例删出处） |
| M-14 | 表内最优标记规则 | 表注对"加粗 = 锚点"的限定语在 3 张含 A1 加粗行的表中缺失（Table 4/5/8，见 A-14）；其余 6 张均写明非最优 | **部分通过** |
| M-15 | 阈值轮廓后处理披露 | `results.md:65,71`：明说 min–max 归一 + 256-bin Otsu（并列取最小极大 bin）、`τ_vis is a visualization rule, not a universal fixed operating threshold`、`No ground-truth outline is substituted for a predicted output`、`A deployment threshold would require separate calibration` | **通过** |
| M-16 | 引言 gap 与 "first" 自洽 | 引言设问 `what makes the additional representation useful?` + `we isolate a specific unresolved attribution problem in dense industrial localization`；贡献 3 条围绕受控归因/交互定义/条件性发现；全文无未核查 "first"、无"上限/全局最优"断言 | **通过** |
| M-17 | 消融图只含真消融 | Fig S2 仅 `ABL-S`（去高斯平滑）/`ABL-N`（去分支归一化，改平方欧氏）/`ABL-C`（分数融合→朴素拼接）；`DINO-only`/`CLIP-image-only` 不在消融图内，单分支被定位为 `Single-branch paths diagnose descriptor quality`（诊断/控制组） | **通过** |

---

## §3 清单 §3（方法覆盖与对照，6 条）

| 编号 | 要求 | 实测 | 判定 |
|---|---|---|---|
| C-01 | "近两三年 3–4 个较先进方法" | 表 12 三个新增家族 + 表 11 两列：WinCLIP+（2023）、AnomalyCLIP zero-shot（2024）、AnomalyDINO（`references.json` 记 **2025**）、SubspaceAD（记 **2026**）、PatchCore（2022，经典对照）。标"近期（2024–2026）"者 = **4 个 ≥ 3** | **通过** |
| C-02 | 说明"数量以正式对照集合为准，不以约 10 个为硬指标" | 全文与表注**未找到**该同义句；最接近者为 `manuscript.md:184` `This comparison assesses practical configurations and does not isolate the matching factor or support a comprehensive cross-method ranking.`（只否定"排名"，未声明"数量非目标/以正式集合为准"） | **部分通过** |
| C-03 | 协议差异如实声明（三处） | ② Table 12 标题与表注：`under their own native protocols`、`the three added families keep their native input resolutions and protocols` ✓；③ Table S1 + 补充节：`short side of 448 pixels, the frozen common valid region and the same rank-based pooled metric for 36 of the 144 category units`，并写明**谁不能进**（`The square-stretch families SubspaceAD, WinCLIP+ and zero-shot AnomalyCLIP are excluded`）✓；① **Table 11 表注未明写"各方法原生协议（6 配置冻结）"**，仅写 `Methods differ in backbone, resolution and augmentation.`（"冻结"字样在 Table 12 表注内：`the frozen values of Table 11, copied row by row and not recomputed`） | **部分通过** |
| C-04 | 消融 vs 控制组分组清楚 | 真消融（Fig S2 的 ABL-S/N/C）与单分支诊断（B/S/C 单支）、控制组（`DUP` 重复控制、`DINO-only` 式单编码器）分列于不同图/表；`missing-ablation` 清单语义由 `§5 Discussion` 第七条承担（`the operations that every construction shares … are held fixed rather than ablated at the primary scope`） | **通过** |
| C-05 | loss–epoch 曲线适用性说明 | `results.md:151` `Because the pipeline uses frozen encoders and no target-domain optimizer, a training loss or epoch-convergence curve is not defined.` + `they do not establish model convergence` + 明确替代图适用范围 | **通过** |
| C-06 | 显存/推理速度证据图 | Fig S5 + Table 20：同机同软件（RTX 3060 Laptop / PyTorch 2.0.0+cu118 / CUDA 11.8）；单位写明（s、MiB = 2^20 B）；区分建库成本与查询成本；明标阶段计时之和、非端到端、非 ms/image | **通过** |

---

## §4 清单 §4（防回归 15 条）

| 编号 | 保持项 | 实测 | 判定 |
|---|---|---|---|
| K-01 | Related Work 连续、无 2.1/2.2/2.3 分节 + 跨类别比较评价 | Heading 列表仅 `2 Related Work`（无子节）；末段 `Taken together, prior work explains how … our study connects them through a factorized comparison …` 为跨类别总结 | **通过** |
| K-02 | 贡献不靠"完成实验评估"充当、无未证明全面领先 | 3 条贡献为"受控分解 / 交互设计与定义 / 条件性实证发现"；`provide evidence for evaluating those choices together without claiming a universal encoder advantage`；`SOTA`/全面领先 0 命中 | **通过** |
| K-03 | 主图输入与 Problem Statement 一致 | Fig 1 图注：`(a) K normal support images form a fixed, aligned reference bank`、`(b) The query follows the same frozen feature path`；并处理 K=1 示例的歧义：`Multiple support thumbnails illustrate the general input, not that example's support count.`；`The second image panel is a thresholded display … not another learned output.` | **通过** |
| K-04 | seed/K/配对单位/数据集角色/适用范围；VisA 不包装成未见域 | §4.1.1：`Seeds 0, 1 and 2 crossed with K equal to 1, 2, 4 and 8 yield twelve dataset-level support conditions`；`The same supports and query images are used by every method in a paired comparison`；Table 3 角色列（Development / External frozen validation / **In-domain frozen validation** / Separate confirmation）；`does not provide independent unseen-domain evidence because VisA retains the conservative in-domain role` | **通过** |
| K-05 | KSDD2 确认与探索性分开 | `Before any KSDD2 feature file existed, the specification frozen at 11:59 UTC on 18 September 2026 required all four S and D interactions to be positive …`；`the confirmation set remains separate from the exploratory adjustment families`；`deliberately does not enter the four-dataset table` | **通过** |
| K-06 | 案例选择说明 + 红色空心放大框 + 失败案例保留 | Fig 6 图注：`Red hollow rectangles define identical GT-centered visual crops, enlarged below.`（框为空心线框、未填充）✓；`The cases are selected by extreme stored per-image AP changes from the fixed closeout candidate list.` ✓；Fig 7 保留 2 个 degradation 案例并解释 | **通过** |
| K-07 | 三线表；A1 加粗并说明非统计最优 | 三线表 ✓（A-13）；A1 加粗 ✓；限定语 3 张表缺失（A-14） | **部分通过** |
| K-08 | S2 探索性共享操作措辞 | Fig S2 图注：`The scope is a single condition, seed 0 with K = 1, and one run per ablation, so no interval exists and none is drawn; the panel is therefore exploratory and does not show that a shared operation has been validated.`；`§5` 第七条第 3 点重申未验证模块 | **通过** |
| K-09 | 符号体系不回退 | docx 内 152 个原生数学对象；抽查 eq1–eq12 与正文：`x`/`g`/`A`/`a`/`M` 为粗斜体（`m:sty=bi`）、`J(p)`/`L(p)`/`G(p)` 为斜体、`J`/`L` 作规则标签在 `labelindex()` 内用直立体；`I_TRI`/`I_BAL` 为数学对象 | **通过**（抽查，未逐符号审计全部 152 个对象） |
| K-10 | 命名温和版不回退 | Table 1/2 `Full name` 列在 ✓；正文首现加粗/括注在 ✓；图注首现全称在 ✓ | **通过** |
| K-11 | `L` 一律称 independent matching | `local matching` 0 命中（源与 docx 双向核）；`L` 的定义句为 `**L** (independent matching)` | **通过** |
| K-12 | 冻结基线不得改动 | 冻结表/扩展表/母本哈希 ✓、`experiments/**`+`data/**` git 差异为空 ✓、表 11 六列与表注字节未改 ✓、`LICENSE`/`requirements_repro.txt` 未见改动。**但** `git status` 显示多张图件相对上一版再次变更且**不在清单已获批清单（F01/F02/P04/F14）内**：`figures/figS1_encoders.png`（modified）、`figures/fig2/fig3`（F01/F02，获批）、`figures/figS4_bootstrap_convergence.{png,pdf}`（F14/P04，获批）；另 `figure_sources/{build_methods.mjs, plot_primary.py, plot_extra.py, plot_supplementary_figures.py, README.md}` 与 `figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` 均被改写。逐文件哈希比对显示入稿图件与旧目录版本**8 张全部不同** | **部分通过**（红线项未破；但图源/图件再变更超出清单已批准的 4 项，需确认） |
| K-13 | 数值安全底线 | `git status --porcelain -- experiments data` **输出为空**；三张冻结哈希全程不变 | **通过** |
| K-14 | 许可三段保留 | §7 `Licensing is split three ways`：代码 MIT / 派生产物同许可 / 数据集许可独立且不再分发 | **通过** |
| K-15 | 作者/元数据占位与安全默认 | docx 占位集合恰为 `{AFFILIATIONS, COMPETING_INTERESTS_TO_BE_CONFIRMED, CORRESPONDING_AUTHOR, FUNDING}`；无 `{{…}}`；COI/伦理为安全默认句；`d.core_properties.author = 'Yuening Li'` | **通过** |

---

## §5 汇总计数

| 分组 | 通过 | 部分通过 | 不通过 | 未核实 | 合计 |
|---|---|---|---|---|---|
| §1 A-01…A-27 | 18 | 7 | 1 | 1 | 27 |
| §2 M-01…M-17 | 13 | 4 | 0 | 0 | 17 |
| §3 C-01…C-06 | 4 | 2 | 0 | 0 | 6 |
| §4 K-01…K-15 | 13 | 2 | 0 | 0 | 15 |
| **合计** | **48** | **15** | **1** | **1** | **65** |

| 项 | 值 |
|---|---|
| 阻断项（按清单定义：冻结值 K-12/K-13、禁写 A-18、协议 C-03） | **无**（K-13 通过；A-18 通过；C-03 仅"部分通过"，未构成阻断） |
| 是否可直接进入下一轮（写作/投稿） | **不能直接进入**。理由：①A-22/A-17/A-16 的规模与 deck 口径与现行"唯一交接入口"文档（47 页/20 表/22 图/58 页 deck）冲突，需先定口径；②A-11 的字号/版式门未在当前入稿图件上复跑；③A-14/A-19/C-02/C-03 等呈现纪律条目需补一句话级修订 |
| 部分通过项清单 | A-07, A-08, A-11, A-12, A-14, A-17, A-19, M-05, M-10, M-13, M-14, C-02, C-03, K-07, K-12 |
| 不通过项清单 | A-22 |
| 未核实项清单 | A-27 |

---

## §6 阻断级 / 高严重度问题清单（按严重度排序）

> 说明：按清单自身定义**无"阻断"**；下表按"是否必须先处理才能交付"排序。

| # | 严重度 | 问题 | 位置 / 证据 | 建议改法 |
|---|---|---|---|---|
| 1 | **高** | **字号/版式门未覆盖当前入稿图件**：`qa_layout.py` 默认跑 `scripts/…/layouts`（frame **1280×900**）与 `docs/figures_reference_matching_20260914`，而现行入稿渲染为 **1280×1060**、与门禁目录版本**8 张全不同**（fig1/2/3/8/S1/S2/S4/S5）。当前入稿的 `fig2/fig3/figS1/fig8/figS5` 的 `TOTAL PROBLEMS: 0` 属**旧渲染**结论 | `scripts/figures_reference_matching_20260914/layouts/fig2_matching.layout.json`（frame 1280×900）；`docs/paper_complete_review_20260920/figures/fig2_matching.png` = 2560×2120；哈希逐张对比结果 | 用 `build_methods.mjs` 重出对应 `.layout.json` 后以 `--layout-dir/--figures-dir` 指向 `docs/paper_complete_review_20260920/figures` 复跑 `qa_layout.py`，并在 `FIGURE_BINDING.md` 记录新 frame 与 min pt |
| 2 | **高** | **规模口径与现行交接文档冲突**：新稿 55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 19,169 词、deck 63 页，而 `MASTER_TODO_PAPER_PPT_FIGURES_20260923.md:11,14,17,175,183,235`、`FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md:14,130,229,370`、`NAMING_MIGRATION_PLAN_20260922.md:18` 仍以 "47 页 / 20 表 / 22 内嵌图 / 142 数学对象 / 34 文献 / 17,221 词 / 58 页 deck" 为权威口径 | Word COM 实测（55 / 19,169 / 23 / 27 / 152）；`REVISION_VALIDATION_20260923.json` 自报与实测一致 | 由作者拍板"接受扩版"或"回到基线口径"；若接受，则同步更新上述交接文档与清单 A-22/A-17 的判据值（**不改任何数值**） |
| 3 | 中高 | **图源/图件再次变更超出清单已批准的 4 项**：`git status` 显示 `figS1_encoders.png`、`figure_sources/{build_methods.mjs, plot_primary.py, plot_extra.py, plot_supplementary_figures.py}`、`figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py` 被改写；清单 K-12 的例外只列 F01/F02/P04/F14 | `git status --porcelain`（M 项）；`figS1_encoders.png` SHA `FE182E11F8679468797FB764F762123A4C60329B15F12D6A666DE527B3744418` | 在 `ISSUE_REGISTER` / `MASTER_TODO` 登记为"revision23 获批范围外变更"，逐项说明是"新几何面板（E1–E3 入图）"还是重渲染；补入例外清单 |
| 4 | 中 | **图 2/图 3/图 S4 记录哈希已过期**："已完成勿重做"记录 `AB1EB3FD…`（fig2）/`57362409…`（fig3）/`C4D2D0A0…`（figS4），盘上为 `5156E610…` / `3F309ADB…` / `6AFA2E49…` | `MASTER_TODO_PAPER_PPT_FIGURES_20260923.md:69`；`Get-FileHash` | 更新记录哈希并注明"因 (b)/(c) 面板几何由 900→1060 单元重排而重渲染" |
| 5 | 中 | **A1 加粗行缺"非最优"限定**（Table 4/5/8） | `tables.json` 的 `main`/`matching`/`d_full` 表注 | 三处表注各补一句（沿用 Table 1 的 `Bold identifies the study anchor, not a claim of best performance.`）→ 重跑 `build.py`、复测规模 |
| 6 | 中 | **Table 11 表注无"不构成排名"** | `tables.json.baselines.note`（与 HEAD 字节相同，非本轮回归） | 补 `and is not a ranking`（注意：`baselines` 目前被 `finish_text_revision23.py:21` 显式列为"冻结表注，不得改"，需作者先解除该冻结再改） |
| 7 | 中 | **C-02/C-03 呈现纪律缺口**：无"数量不以约 10 个为硬指标"的同义句；Table 11 未明写"各方法原生协议" | `manuscript.md:184`；`tables.json.baselines.note` | 各补半句；C-03 的 ① 建议放在 Table 11 表注（须先解冻）或 §4.2.2 正文 |
| 8 | 中 | **M-05/M-10 语义边界**：VisA 表述被改写为"保守保留历史指定"；correspondence 句写"interval separation 不依赖该常数" | `finish_text_revision23.py:13-14`；`results.md:143` | 作者确认 VisA 口径；M-10 句改为"零排除判定在各变体下保持" |
| 9 | 中低 | **PPT/索引口径未与旧文档同步**：deck 63 页、原生页 1/2/3/15、S4 在 23/24 页 | `图件与PPT页码索引.md`、`FIGURE_SLIDE_INDEX.json`（自洽）vs `MASTER_TODO…:14,15,172`、`AUTHORITATIVE_SOURCE_DIFF_20260921.md:220` | 更新引用 58 页/第 20–21 页/第 12 页原生 的旧文档 |
| 10 | 中低 | **M-13 年份覆盖**：2024–2026 = 58.8%（<70–80%） | `references.json` 年份计数 | 非硬指标；若要提升，补 2024–2026 新文献（不得删必需出处） |
| 11 | 低 | **docx 内 8 个未被引用的图片部件残留**：`rId10–rId17 → word/media/image1..8.png`（`w:drawing` 计数 27，image rels 35） | `word/_rels/document.xml.rels`；文件 32.5 MB | 构建时对媒体部件做 package 级清理（无正文引用即丢弃），或接受为模板残留并登记 |
| 12 | 低 | **孤立产物**：`docs/paper_complete_review_20260920/figures/figS1_encoders_geometry.png` 未被 `figures.json` / `FIGURE_SLIDE_INDEX.json` 引用 | 两处 JSON 均无该路径 | 如为中间稿，移入 `superseded/` 或登记用途 |

---

## §7 清单外新发现（清单未覆盖）

| # | 位置 | 事实 + 证据 | 严重度 | 建议 |
|---|---|---|---|---|
| N-1 | docx 包 `word/_rels/document.xml.rels` | 35 个 image 关系 vs 正文 27 个 `w:drawing`；`image1..image8.png` 无引用（rId10–rId17） | 低 | 同 §6#11 |
| N-2 | `docs/paper_complete_review_20260920/figures/figS1_encoders_geometry.png` | 未被任何索引引用 | 低 | 同 §6#12 |
| N-3 | `MASTER_TODO_PAPER_PPT_FIGURES_20260923.md:11,14,17,175,183,235`、`FINAL_ACCEPTANCE_AND_HANDOFF_20260922.md:14,130,370`、`NAMING_MIGRATION_PLAN_20260922.md:18` | 仍写 47 页 / 20 表 / 22 图 / 142 对象 / 58 页 deck，与新交付件（55/23/27/152/63）矛盾；`MASTER_TODO` 自称"唯一交接入口" | 中 | 同步口径（§6#2） |
| N-4 | `MASTER_TODO_PAPER_PPT_FIGURES_20260923.md:69` | 记录 fig2 `AB1EB3FD…` / fig3 `57362409…` / figS4 `C4D2D0A0…`，与盘上不符 | 中 | 同 §6#4 |
| N-5 | `scripts/paper_complete_review_20260920/finish_text_revision23.py:21` | 代码中显式写 `if k=='baselines': continue # frozen Table 11 note, byte-for-byte unchanged` —— 即 Table 11 表注被**程序性冻结**，导致 A-19 的"不构成排名"无法在不改该表注的前提下补齐 | 中 | 若决定补 A-19，须先由作者解除该冻结，或把该限定写入 §4.2.2 正文/Table 12 表注（现已有） |
| N-6 | `results.md:69` vs `图件与PPT页码索引.md:34–69` | 正文写"其余 33 张留附录"，deck 附录实为 **36 页**（slides 28–63，含正文已用的 metal_plate/grid/pcb1） | 低 | 口径自洽（36−3=33），但建议在图注或索引中显式说明"附录含正文所用 3 张的全集" |
| N-7 | 清单 §1 A-17 / A-12 / A-16 的判据值 | 判据写"deck 58 页 / 第 20–21 页 / 原生页 1/2/3/12 / 图 S4 按 16 cm"；新稿为 63 页 / S4 在 23–24 页 / 原生页 1/2/3/15 / S4 = 17 cm | 低 | 更新清单判据（清单本身是验收模板，非被核对象） |
| N-8 | `C-01 判定模板`（清单 §3） | 模板记 AnomalyDINO 2024、SubspaceAD 2025；`references.json` 记 2025、2026 | 低 | 同步年份，避免与文献表冲突 |
| N-9 | `results.md:143` | `neither the sign nor the interval separation of the interaction depends on that constant` | 中 | 同 §6#8（M-10） |
| N-10 | 交叉引用完整性（正面发现） | 正文 `Table 1..21 + S1/S2` 全部有对应表题且被引用；`Figure 1..8 + S1..S6` 全部有图题且被引用；**无悬空引用、无未被引用的表/图** | — | 无需动作（登记为已核查项） |

---

## §8 与上一版基线的回归对比（先前已满足项是否被破坏）

| 先前已满足项 | 新稿状态 | 是否破坏 |
|---|---|---|
| 冻结表/扩展表/版式母本哈希不变（K-12/K-13） | `3C83AB00…` / `1C770129…` / `9DB99E60…` 全对；`experiments/**`+`data/**` git 差异为空 | **未破坏** |
| 表 11 六列数值与表注冻结不改 | `git show HEAD` 与现盘 `tables.json` 的 `baselines`、`baselines_ext` 两键 `identical=True` | **未破坏** |
| 禁写清单（SOTA / 零计算 / FPS / 全局最优…） | 5 处命中全为否定语境 | **未破坏** |
| Related Work 无分节、Discussion 独立、Results 四组 | 层级实测符合 | **未破坏** |
| `L` = independent matching | `local matching` 0 命中 | **未破坏** |
| Table 1/2 `Full name` 列、正文首现强调 | 均在 | **未破坏** |
| 三线表 | 23 张表 0 处非 nil 边框 | **未破坏** |
| 案例选择说明 + 红色空心放大框 + 失败案例保留 | 图注逐条在 | **未破坏** |
| KSDD2 确认与探索性分列 | 段落与表注均在 | **未破坏** |
| S2 探索性措辞、S4 数值稳定性口径 | 均在（S4 图注本轮被重写，口径更完整） | **未破坏** |
| 摘要末句 URL、VisA in-domain 定位 | 均在（VisA 措辞被改写，见 M-05） | 措辞变更，定位未破坏 |
| 作者/安全默认占位 | 4 个占位符精确匹配 | **未破坏** |
| **列表：先前已通过、本版被削弱的项** | ① A-19 的"三表都写不构成排名"从未包含表 11（非回归，但会暴露为缺口）；② A-14 的"非最优限定"由 Table 1 独有扩到多表后，仍有 3 张缺（非回归，是覆盖面不足）；③ **真正被本版改变的**：VisA 边界表述（`finish_text_revision23.py:13-14`，M-05）、correspondence 一句（`results.md:143`，M-10）、图 S4 宽度 16→17 cm、deck 58→63 页、原生页 12→15、图 S1/S2/S5 等重渲染 | **2 处语义表述 + 4 处版式/口径被本版改写**，需作者确认 |

---

## §9 建议的返修顺序（含证据）

| 顺位 | 动作 | 触发文件 | 影响面 |
|---|---|---|---|
| 1 | **定口径**：确认接受 55 页/23 表/27 图/152 对象/63 页 deck，还是回退到 47/20/22/142/58 | `MASTER_TODO…:11,14,17`、`FINAL_ACCEPTANCE…:14`、`NAMING_MIGRATION_PLAN…:18`、清单 A-22/A-17 | 只改文档口径，**不改数值**；决定后续是否需重出 |
| 2 | **重跑图件门禁**：以现行 `build_methods.mjs` 生成的新 `.layout.json` + `docs/paper_complete_review_20260920/figures` 复跑 `qa_layout.py`（要求 `TOTAL PROBLEMS: 0`）与 `figure_font_gate.py --self-test`（4/4） | `scripts/figures_reference_matching_20260914/qa_layout.py`（frame 900→1060） | 若失败 → 重渲染入稿图 → **重出 63 页 deck** → **重建 docx** → 复测规模 |
| 3 | **补三处表注限定语**（Table 4/5/8 的 A1 非最优） | `tables.json` 的 `main`/`matching`/`d_full` | 轻量；重建 docx 后复测 55 页/23 表 |
| 4 | **补 A-19/C-02/C-03 表述**：Table 11 表注"非排名 + 原生协议"（须先解除 `finish_text_revision23.py:21` 的程序性冻结）或改写到 §4.2.2 正文；补"数量以正式对照集合为准" | `tables.json.baselines.note`、`manuscript.md:184`、`results.md:73-79` | 轻量；重建 docx |
| 5 | **确认 M-05/M-10 措辞**：VisA 边界句与 correspondence 句 | `finish_text_revision23.py:13-14`（已生效的替换）、`results.md:143` | 轻量；重建 docx |
| 6 | **同步 deck 口径引用**：58→63 页、第 20/21 页→第 23/24 页、原生页 12→15 | `MASTER_TODO…`、`AUTHORITATIVE_SOURCE_DIFF_20260921.md:220`、`FINAL_ACCEPTANCE…` | 文档only |
| 7 | **登记 revision23 获批范围外的图源/图件变更**（figS1、build_methods.mjs、plot_*.py、build_figS4…py）与记录哈希刷新 | `ISSUE_REGISTER_20260920.md`、`MASTER_TODO…:69` | 文档only |
| 8 | **清理/登记 docx 内 8 个未引用媒体部件**与 `figS1_encoders_geometry.png` | `build.py`（媒体清理）、`figures/` | 低优先；重建 docx 后复测 |
| 9 | 返修后的**必跑链条**（引用 `MASTER_TODO` S5/S6）：重渲染图 → `qa_layout.py` + `figure_font_gate.py --self-test` → 重出 63 页 deck + 同步索引 → `build.py` 重建 docx → 复测"页/表/图/公式/文献/词数"→ 复测三张冻结哈希与 `git status -- experiments data` | — | 全链条 |

**附加纪律核对**：本报告未引入新数值、未改写 `experiments/**` 证据字段与 `data/**`（实测 git 差异为空）、未修改任何稿件。

---

## §10 未核实 / 需作者处

| 项 | 状态 | 说明（用了什么方法 / 缺什么） |
|---|---|---|
| **A-27 仓库自检** | **未核实（未执行）** | `selfcheck.py:339,516` 会就地改写 `experiments/…/{READONLY_PROOF.json, SELFCHECK.json}`；任务硬约束禁止改动产物，故未跑。如需"67/69"基线复核，请在允许写盘的窗口执行并在跑后 `git checkout --` 该两文件 |
| **A-07 像素复核** | 部分 | 已核 `113+2*42` 与 PNG 哈希；**未**逐个像素验证"紫框 x∈[195.5,240.0] 与填色格 x∈[200,238] 重合"（需对 2560×2120 渲染做像素级定位，本轮未做） |
| **A-05 图内标题** | 通过（机器旁证） | 方法：核原生页 XML 无 `Figure N` 文本 + 核绘图脚本无生效 `suptitle`；**未做 OCR**，无法 100% 排除位图内嵌标题 |
| **M-13 DOI/卷期/大小写统一** | 未核实 | 只统计了年份分布（58.8%）；未逐条比对 34 条文献的 DOI、期刊缩写、作者大小写 |
| **K-09 全符号审计** | 部分 | 抽查 eq1–eq12 与关键段落；未逐一遍历 152 个 `m:oMath` 的每个 `m:sty` |
| **`FIGURE_BINDING.md` 是否已登记 S3 p3/p4 与 S4 新几何** | 未核实 | 清单登记项 B-09 原为"待做"；本轮只核了 `figures.json` / `FIGURE_SLIDE_INDEX.json` / 页码索引三者自洽，未逐行读 `FIGURE_BINDING.md §一/§四` 的 S3/S4 条目 |
| **表 12 `AnomalyCLIP` 行 protocol 单元格是否超宽** | 未核实 | 该列宽 3.6 cm、文本约 100 字符；需 Word 目视或按 `qa_layout` 类方法估算折行，本轮未做 |
| **`data/splits/*/manifest.json` 与 `LICENSE`/`requirements_repro.txt` 是否被改** | 通过（间接） | 以 `git status --porcelain -- experiments data` 为空 + 全局 `git status` 未见 `LICENSE`/`requirements_repro.txt` 判定 |
| **是否接受"扩版"为最终投稿口径** | **待作者拍板** | 直接影响 A-22/A-17/A-16 的最终判定与 §9 顺位 1 |
| **Table 11 表注冻结是否解除** | **待作者拍板** | 见 §7 N-5；不解除则 A-19 只能部分通过 |

---

**（报告结束。本文件为本次核查新增的唯一产物；未改动任何稿件、图件、表格或实验数据。）**
