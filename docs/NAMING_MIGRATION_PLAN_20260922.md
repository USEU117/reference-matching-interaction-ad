# T09 命名规范化迁移方案（2026-09-22，**只出方案，不执行**）

> **执行状态已更新**：老师后续已明确要求整批修改，20260925 修订已同步描述性名称。以下“只出方案”“待拍板”均为历史记录；最新状态见 [修订与验收](paper_complete_review_20260920/修订说明与验收_20260925.md)。

> 触发：AI 辅助评审/外部评审（T09 原话要点）——对比的模块/层/方法**不要用 `B`/`C`/`D` 这类单字母**，要用**全称或能代表功能的词**；审稿专家要"所见即所得"，不愿为看懂一个字母全文检索；且正文首现直接给字母、又不加粗/斜体，不便阅读。
> 边界：本文件**只做映射、影响盘点、执行顺序与风险评估**。本轮**未执行任何改名**（未改 `manuscript.md` / `results.md` / `tables.json` / `figures.json` / `build.py` / 图源脚本 / 任何图 / PPT）。
> 已完成的部分仅为 **2a 温和版**（见 §0），与本源方案不冲突、可保留。
> 所有"含义"均**实读自盘上内容**，依据列到 `文件:行`；读不到的一律写"未核实"。

---

## 0 已完成（2a 温和版，本轮实际改动，供 2b 衔接）

| 落点 | 内容 |
| --- | --- |
| `tables.json` → `design`（Table 1） | 新增 `Full name` 列（第 2 列）：`A1`=Dual-encoder anchor (DINOv2-B + AnomalyCLIP visual)、`DUP`=Duplicate-weight control (copy of B, no new encoder)、`TRI`=Equal-weight replacement (S or D in the copied slot)、`BAL`=Balanced replacement (S or D in a quarter slot)；表注补一句定义 B/S/C/D 与 J/L |
| `tables.json` → `models`（Table 2） | 新增 `Full name` 列：B/S/C/D/E1–E3 给描述性全称；Alignment/Normalization/Memory and scoring/Output/Optimization 五行给 "Shared …" / "No target optimization" 全称 |
| `manuscript.md`（正文首现加粗 + 括注） | `:47` **C**；`:69` **J**/**L**；`:77` **B**；`:107` **B/S/C/D** + **A1/DUP/TRI/BAL**；`:162` **E1/E2/E3** |
| `figures.json`（图注首现加全称） | framework(J/L/DUP/TRI/BAL/A1)、matching(J/L)、constructions(A1/DUP/TRI/BAL/B/C/S/D)、effects(S)、effects-continuation(S)、cases_good(A1/L/J)、cases_bad(A1)、extra_cases part2(B/S)、speed_vram(A1/B/C) |
| 未动 | 图内标签、公式、PPT、任何数值（**2026-09-23 校**：重建后规模已扩版为 **55 页 / 23 表 / 27 内嵌图 / 152 数学对象 / 34 文献 / 19,253 词**；本行原记的 20 表 / 22 内嵌图 / 142 数学对象 / 47 页为 2026-09-22 时点值，按"过程记录不改写"保留） |

**2a 的验收口径**：只做"加列 + 首现强调 + 图注加全称"，**不改任何字母本身**，因此与本源方案（整批改名）是**叠加关系**，不是替代关系。

---

## 1 现有符号体系（实读，含义与依据）

| 符号 | 现含义（实读） | 依据 `文件:行` |
| --- | --- | --- |
| `B` | DINOv2 ViT-B/14 冻结 patch 特征，768 维，short side 448 | `scripts/paper_complete_review_20260920/tables.json:62-64`；`manuscript.md:107` |
| `S` | DINOv2 ViT-S/14 冻结 patch 特征，384 维 | `tables.json:68-70` |
| `C` | AnomalyCLIP 视觉分支（CLIP ViT-L/14 + DPAM，518×518，投影后保留第 24 层，768 维） | `tables.json:74-76`；`manuscript.md:47`（"denoted C"） |
| `D` | WideResNet50-2（ImageNet-1K，layer2+layer3 拼接，1536 维，对齐到 B 画布） | `tables.json:80-82` |
| `E1`/`E2`/`E3` | 原版 DINO ViT-S/8（384）/ ConvNeXt-Tiny（576）/ Swin-Tiny（576），探索性替换 | `tables.json:86-102`；`manuscript.md:162` |
| `A1` | 双编码器锚：B 1/2 + C 1/2（"dual-encoder anchor"） | `tables.json:11-14`；`manuscript.md:35,107` |
| `DUP` | 复制控制：B 1/3 + B copy 1/3 + C 1/3，不加新信息、只改权重分配 | `tables.json:17-20`；`manuscript.md:111` |
| `TRI` | 等权替换：B 1/3 + (S 或 D) 1/3 + C 1/3，槽位权重不变 | `tables.json:23-26`；`manuscript.md:111` |
| `BAL` | 平衡替换：B 1/4 + (S 或 D) 1/4 + C 1/2，保持 C 与非 C 总量 | `tables.json:29-33`；`manuscript.md:113` |
| `J` | 联合匹配：先按候选求和各分支距离，再取最小 | `manuscript.md:87-89`；`build.py:238` 式(3) |
| `L` | 独立匹配：各分支先取各自最近邻，再加权求和 | `manuscript.md:91-95`；式(4) |
| `I_TRI` / `I_BAL` | 两条直接匹配交互 `E(L) − E(J)` | `tables.json:334-385`；`build.py:238` 式(8)(9) |
| `E_{q,t}` / `ΔI_q` | 表示效应 / 编码器差 | `build.py:238` 式(6)(7)(10) |
| `A_t`, `s_img,t`, `M_vis,t` | 异常图 / 图像级分数 / 显示掩膜（非模块名，**不在改名范围**） | `manuscript.md:69,143-151` |

**不在改名范围**（避免误伤）：`$b$` 分支索引、`$c$` 类别、`$K$` 支持预算、`$p$`/`$r$`/`$u$` 位置索引、`$H$`/`$W$` 画布尺寸、`ABL-S`/`ABL-N`/`ABL-C`（共享操作消融名，其中 `C` 指 concatenation，**不是** C 分支）、`KSDD2`/`MPDD`/`BTAD` 等数据集缩写、`ADino`/`PC` 图例缩写。

---

## 2 改名映射表（旧 → 建议名 → 含义 → 依据）

> 两套方案并列，供作者二选一。**方案 A** 为"标签可读化"（推荐，改动可控）；**方案 B** 为"公式符号也一并改"（彻底，但风险最高的是 J/L）。

| 旧名 | 方案 A 建议名（正文/表/图一致） | 方案 B（连公式一起改） | 含义 | 依据 `文件:行` | 风险 |
| --- | --- | --- | --- | --- | --- |
| `B` | `DINOv2-B`（首现 **DINOv2-B visual branch**） | 同 A | DINOv2-B 冻结视觉编码器 | `tables.json:62-64`；`manuscript.md:107` | 低 |
| `S` | `DINOv2-S`（首现 **DINOv2-S visual branch**） | 同 A | DINOv2-S 冻结视觉编码器 | `tables.json:68-70` | 低 |
| `C` | `AnomalyCLIP-visual`（首现 **AnomalyCLIP visual branch**） | 同 A | AnomalyCLIP 视觉分支（只用视觉描述子） | `tables.json:74-76`；`manuscript.md:47` | 中（`build_methods.mjs` 里 `C` 同时是**颜色命名空间** `C.blueFill`，须逐处判读，见 §3.3） |
| `D` | `WRN50-2`（首现 **WideResNet50-2 branch**） | 同 A | WideResNet50-2 分支 | `tables.json:80-82` | 低（图内已用 `WRN50-2`，`build_methods.mjs:515`） |
| `E1` | `DINOv1-S/8`（首现 **original DINO ViT-S/8**） | 同 A | 探索性额外编码器 | `tables.json:86-89`；`manuscript.md:162` | 中（下标长度） |
| `E2` | `ConvNeXt-T` | 同 A | 探索性额外编码器 | `tables.json:92-95` | 中 |
| `E3` | `Swin-T` | 同 A | 探索性额外编码器 | `tables.json:98-101` | 中 |
| `A1` | `DualAnchor`（首现 **dual-encoder anchor**） | 同 A | 双编码器锚（DINOv2-B + AnomalyCLIP visual） | `tables.json:11-14`；`manuscript.md:35` | 中（全表行名 + `A1 J`/`A1 L` 组合行） |
| `DUP` | `DuplicateCtrl`（首现 **duplicate-weight control**） | 同 A | 复制权重控制 | `tables.json:17-20` | 中（公式 `E_{DUP,t}`、表 4/5/6 行名） |
| `TRI` | `EqualWReplace`（首现 **equal-weight replacement**） | 同 A | 固定槽位权重下替换真实编码器 | `tables.json:23-26` | 中（公式 `E_{TRI,t}`、`I_TRI`、`TRI D J` 等行名） |
| `BAL` | `BalancedReplace`（首现 **balanced replacement**） | 同 A | 保持 C 与非 C 总量的替换 | `tables.json:29-33` | 中（公式 `E_{BAL,t}`、`I_BAL`） |
| `J` | 正文/表/图用 `joint`（首现 **joint matching**） | 公式也改为 `joint`（`J(p)` → `joint(p)`） | 联合匹配 | `manuscript.md:69,87-89`；`build.py:238` 式(3)(5) | **高**（深嵌公式与排版字典） |
| `L` | 正文/表/图用 `indep`（首现 **independent matching**）；**不要叫 local**（F04 已修，勿回退） | 公式也改为 `indep`（`L(p)` → `indep(p)`） | 独立匹配 | `manuscript.md:69,91-95`；式(4)(5) | **高** |
| `I_TRI` / `I_BAL` | `I_equal` / `I_balanced`（或保留 `I` 并加下标全称） | 同左 | 两条直接交互 | `tables.json:334-385`；式(8)(9) | **高**（出现在 6 张图与 11 张表） |
| `E_{q,t}` / `ΔI_q` | `Effect(q,t)` / `EncoderDiff` | 同左 | 表示效应 / 编码器差 | 式(6)(7)(10) | 中 |

**组合行名**（改名后需逐条重写，当前形态实读）：`A1 J`/`A1 L`、`DUP J`/`DUP L`、`TRI J`/`TRI L`、`BAL J`/`BAL L`、`TRI D J`/`TRI D L`、`BAL D J`/`BAL D L`、`S (4)`/`D (4)`/`E1 (12)`…（`tables.json: main/d_full/encoders`）。

---

## 3 影响清单（实读计数 + 逐点落位）

### 3.1 计数（单字母 `B/S/C/D/J/L` + 多字母 `A1/DUP/TRI/BAL/E1–E3`）

计入规则：词边界（前后不得为 `[A-Za-z0-9_]`），**允许连字符相邻**（故 `B/S`、`C-grid`、`A1-J`、`ABL-C` 等复合形态一并计入）；已剔除 `D:\` 盘符与路径字面量。**含少量非标签 token**（如代码标识符、`ABL-C`），仅作量级参考。

| 文件 | 单字母合计 | 分项 | 多字母合计 | 分项 |
| --- | ---: | --- | ---: | --- |
| `manuscript.md` | 63 | B15 C9 D14 J1 L5 S19 | 30 | A1:4 BAL:6 DUP:7 E1:3 E2:1 E3:3 TRI:6 |
| `results.md` | 99 | B9 C11 D23 J8 L18 S30 | 97 | A1:19 BAL:20 DUP:6 E1:8 E2:11 E3:9 TRI:24 |
| `tables.json`（caption/headers/rows/note） | 120 | B15 C11 D28 J18 L19 S29 | 106 | A1:18 BAL:33 DUP:7 E1:6 E2:5 E3:5 TRI:32 |
| `figures.json`（caption/continuation/part/note） | 54 | B11 C9 D5 J6 L6 S17 | 30 | A1:9 BAL:4 DUP:4 E1:3 E2:2 E3:3 TRI:5 |
| `build.py` | 29 | J10 L11 S4 D4 | 34 | A1:5 BAL:12 DUP:5 TRI:12 |
| `figure_sources/build_methods.mjs` | 201 | B26 C143 D9 J6 L6 S11（**C 的 143 处绝大多数是颜色命名空间 `C.xxx`，非标签**） | 39 | A1:6 BAL:10 DUP:5 E1:4 E2:2 E3:3 TRI:9 |
| `figure_sources/plot_primary.py` | 15 | 轴标签/图例为主 | 12 | 同左 |
| `figure_sources/plot_extra.py` | 7 | 含 `rec`/`xs` 等假阳性 | 4 | 图例 `MPDD/ BTAD I_TRI` |
| `figure_sources/plot_supplementary_figures.py` | 2 | 1 处为 marker `"D"`（假阳性） | 4 | `I_TRI`/`I_BAL`、`A1\nJ`、`A1\nL` |
| `figure_sources/build_deck.mjs` | 4 | 图注拼接字符串 | 2 | — |

**受影响表格（实读 20 张表中 19 张含符号）**：`design`、`models`、`protocol`（表头 `S conditions`/`D conditions`）、`matching`、`effects`、`s_interaction`、`baselines`、`baselines_ext`、`main`、`d_full`、`d_interaction`、`encoder_diff`、`resources`、`ksdd2_confirmation`、`generalization`、`encoders`、`seed_variance`、`correspondence`、`correspondence_sensitivity`、`benchmark`（`benchmark` 行名为 `A1 J`/`A1 L`）。

### 3.2 `build.py` 公式排版硬编码（**必须同步改，否则公式报错或排版错位**）

| 行 | 现内容（实读） | 改名后动作 |
| --- | --- | --- |
| `:47` | `labelindex`：`re.split(r'(TRI\|BAL\|DUP\|A1\|img\|vis\|J\|L\|S\|D)',t)` | 正则内的 `TRI\|BAL\|DUP\|A1\|J\|L\|S\|D` 全部替换；注意保留 `img`/`vis` |
| `:48-58` | `sym()`：`\mathcal{R}_c`、`N_cd`、`nN_cd`、`\tau_{vis}` 特判；`b in ['TRI','BAL','DUP','A1','R']`（`:57`）控制直立体 | `:57` 白名单同步；若 J/L 改名，需新增/删除对应特判 |
| `:63,73-76` | `limit()`/`configuration()`/`performance()`/`effect()`/`parg()` | 依赖 `labelindex`，跟随生效；`effect()` 的 `E` 基符号见 §2 决策 |
| `:78-102` | `eq(1..12)`：式(3)(4) 生成 `J`/`L` 函数名（`:87`），式(5) `G(p)=J(p)−L(p)`（`:89`），式(6)(7) `TRI/DUP`、`BAL/A1`（`:91`），式(8)(9) `I_{TRI}`/`I_{BAL}`（`:94`），式(10) `q ∈ {TRI, BAL}`（`:95`） | 逐式改字面量 |
| `:238` | `equations` LaTeX 字典（12 条，`\mathrm{TRI}` 等） | 12 条 LaTeX 同步；若改 J/L 需同时改 `:238` 的 `J(p)`/`L(p)`/`G(p)=J(p)-L(p)` |

> 门禁：改后 `native_math_objects` 必须仍为 **142**（`build_validation.json`），否则说明有数学串被拆散。

### 3.3 `figure_sources/build_methods.mjs` 图内标签（**属 2b，本轮未改**）

| 行 | 现内容（实读） | 说明 |
| --- | --- | --- |
| `:296,307` | 图 2 公式 `J(p)` / `L(p)` | 方法图公式 |
| `:317,318,326,327` | 图 2 分支行标签 `"B"` / `"C"`（J 面板与 L 面板各一组） | 分支标签 |
| `:348,349` | 图 2 `G(p)=J(p)−L(p)≥0` | 公式 |
| `:391-394` | 图 3 四个构造 `id: "A1"/"DUP"/"TRI"/"BAL"` + 行内文字 `"B  DINOv2-B"`、`"B copy"`、`"C visual"`、`"extra S or D"` | 构造与槽位标签 |
| `:473-484` | 图 3 图内公式 `E_{TRI,t}`/`E_{BAL,t}`/`I_{TRI}`/`I_{BAL}`（含 `TRI`/`DUP`/`BAL`/`A1`/`L`/`J` 字面量） | 公式 |
| `:512-515` | 图 S1 分支卡片 `id: "B"/"C"/"S"/"D"`（title 已是 `DINOv2-B`/`AnomalyCLIP`/`DINOv2-S`/`WRN50-2`） | 分支卡片 |
| `:547-549` | 图 S1 `id: "E1"/"E2"/"E3"`（title `DINO ViT-S/8`/`ConvNeXt-Tiny`/`Swin-Tiny`） | 探索性编码器 |
| `C.*`（全文） | `C.blueFill`/`C.amberLine`… 来自 `scripts/figures_reference_matching_20260914/style.mjs` | **颜色命名空间，禁止批量替换** |

### 3.4 需重渲染的图（按含义分档）

| 图 | 文件 | 生成脚本 | 是否需要改图内内容 |
| --- | --- | --- | --- |
| Fig 1 framework | `docs/paper_complete_review_20260920/figures/fig1_framework.png` | **可编辑母本** `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx`（README 明确） | 需要（B/C/S/D、A1、J/L 等图内文字） |
| Fig 2 matching | `…/fig2_matching.png` | `build_methods.mjs`（`:296-349`） | 需要 |
| Fig 3 constructions | `…/fig3_constructions.png` | `build_methods.mjs`（`:391-484`） | 需要 |
| Fig 4a/4b effects | `…/fig4a_representation_effects.png`、`fig4b_matched_encoders.png` | `plot_primary.py`（`:21` y 轴 `E_{BAL,L}`/`E_{TRI,J}` 等；`:27` 编码器刻度 `E3/E2/E1/D/S`） | 需要 |
| Fig 5a/5b/5c budget/seed/category | `…/fig5a_budget_seed.png`、`fig5b_categories.png` | `plot_primary.py`（`:38,52` `I_TRI`/`I_BAL` 图例与刻度） | 需要 |
| Fig 6/7 定性 | `…/qualitative_improvements_part1/2.png`、`qualitative_mpdd_matching_degradations.png` | `plot_extra.py`（面板标题 `A1-J`/`A1-L`） | 需要 |
| Fig 8 resources | `…/fig8_resources.png` | `plot_extra.py` | 复核（未检出标签，重渲染即可） |
| Fig S1 encoders | `…/figS1_encoders.png` | `build_methods.mjs`（`:512-549`） | 需要 |
| Fig S2 ablation | `…/figS2_shared_op_ablation.png` | `plot_extra.py`（`:23` x 刻度 `Baseline/ABL-S/ABL-C/ABL-N`，**ABL 名不改**） | 复核 |
| Fig S3 六个面板 | `…/panel_c_to_b_shift.png`、`panel_canvas_coverage.png`、`panel_interaction_cases*.png` | `plot_extra.py` | 需要（逐图案例标注含 `A1`/`J`/`L`） |
| Fig S4 stability | `…/figS4_bootstrap_convergence.png`、`figS4_bootstrap_stability.png` | `plot_supplementary_figures.py`（`:43,44` `I_TRI`/`I_BAL` 数学文本） | 需要 |
| Fig S5 speed/VRAM | `…/figS5_speed_vram.png` | `plot_supplementary_figures.py`（`:55,56` `A1\nJ`/`A1\nL`） | 需要 |

**字号门禁**：`figure_manifest.json` 的 `minimumPrintPtAt17cm` = **11.294 pt**。改名后标签变长，必须重跑 `qa_layout.py`／字号门，否则可能因折行/缩小而失败（参考：现状 fig2 有 2 处、figS1 有 6 处保守折行估计 `TEXT-OVERFLOW`）。

### 3.5 需重出的 PPT

| 产物 | 路径 | 说明 |
| --- | --- | --- |
| 图件总 deck（58 页） | `docs/paper_complete_review_20260920/All_Figures_Complete_20260920.pptx` | 用 `build_deck.mjs` → `assemble_deck.ps1` → `finalize.mjs` 链路重出；第 1/2/3/12 页为原生可编辑方法图 |
| 同源副本 | `docs/paper_complete_review_20260920/All_Figures_Finalized_20260920.pptx` | 与上一份字节级同源，需同步 |
| 主图可编辑母本 | `docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx` | 改 Fig 1 的图内文字后重出 |
| 索引同步 | `docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json`、`图件与PPT页码索引.md` | 页码不变则仅复核 |

### 3.6 需同步的文档/元数据（非正文，避免口径二次漂移）

`README.md`（中英）、`docs/ARTIFACT_INDEX.md`、`docs/figures_reference_matching_20260914/FIGURE_BINDING.md`、`docs/HANDOVER_20260919.md`、`docs/CURRENT_DYNAMIC_FUSION_STATUS.md`、`docs/EXPERIMENT_GAP_ANALYSIS_20260922.md`（A02/A05 图注与协议表注）、`docs/BASELINE_EXPANSION_PLAN_20260921.md`（表 12 协议列命名）。**`docs/论文与图件问题汇总_仅复核_20260921.md` 不在本轮改动范围（另一任务在写）。**

---

## 4 分步执行顺序（建议，未执行）

| 步 | 动作 | 验收 |
| --- | --- | --- |
| S0 | **冻结基线**：对 5 个源文件 + `build.py` + 4 个图源脚本 + 全部 PNG + 3 个 PPTX 计算 SHA-256 并落盘 `.bak_<日期>` | 基线哈希齐备，可一键回退 |
| S1 | **作者拍板命名**（方案 A 还是 B；J/L 是否进公式） | 决策落盘（本文件 §2 勾选） |
| S2 | 改 `tables.json` 标签（行名/表头/表注），**只替换标签 token** | `git diff` 中仅出现标签差异，**无任何数字变化**；`json.loads` 通过 |
| S3 | 改 `manuscript.md` / `results.md` 正文（首现保留"全称（字母）"结构，或按方案改字母本身） | 抽查首现处；**不出现孤立字母**；无未定义符号 |
| S4 | 改 `figures.json` 图注 | 图注与正文命名一致 |
| S5 | 改 `build.py`（`:47` 正则、`:57` 白名单、`:78-102` 各式、`:238` LaTeX 字典） | 12 式可渲染；`native_math_objects` = **142**；退出码 0 |
| S6 | 改图源脚本（`build_methods.mjs`、`plot_primary.py`、`plot_extra.py`、`plot_supplementary_figures.py`），**绕开 `C.*` 颜色命名空间** | 重渲染脚本退出码 0；字号门 ≥ 11.294 pt |
| S7 | 重渲染 12 张图 + 重出 58 页 deck + 重出主图母本 | PNG 哈希刷新；deck 包完整性/版式/字体策略 0 finding |
| S8 | 重建 docx（`build.py`）并复测 | **47 页 / 20 表 / 22 内嵌图 / 12 编号公式 / 142 数学对象 / 34 文献**；如页数变化须记录原因 |
| S9 | 同步 §3.6 文档与索引 | 交叉引用无孤儿 |

### 回退方案

1. **单步回退**：每步前先 `Copy-Item <file> <file>.bak_<日期>`；回退即还原该文件。
2. **整链回退**：还原 5 个源 + `build.py` + 图源脚本 → 重跑 `build.py`（docx 可重建）；图 PNG 从备份还原；PPTX 直接还原旧 deck（`All_Figures_Finalized_20260920.pptx` 为字节级同源副本，可作为旧版锚点）。
3. **数值安全**：改名**不触碰任何实验数值**；`baseline_common_region.csv` 必须全程保持 `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB`（即 `git diff` 只应出现在文档/脚本，不应出现在 `experiments/**`）。
4. **中止条件**：若 S6 后字号门不通过且无法在 1 轮内调好 → 停止整批改名，保留 2a 温和版（加列 + 首现强调）作为交付。

---

## 5 风险评估

| # | 风险 | 等级 | 说明与缓解 |
| --- | --- | --- | --- |
| R1 | **J/L 改名牵连公式与排版字典** | 高 | `J(p)`/`L(p)`/`G(p)` 出现在式(3)(4)(5)、`build.py:87-89,238`、6 张图；`joint`/`indep` 作为函数名更长，可能破坏公式行宽与"每式占一行"的版式。缓解：方案 A 下 J/L **只改文字标签**，公式内保留 `J`/`L` 并在首现处括注 |
| R2 | **`C` 与颜色命名空间 `C.*` 冲突** | 高 | `build_methods.mjs` 中 `C` 有 143 处 `C.xxx`；批量替换会直接破坏图源。缓解：只改 `addText(...)` 的字面量，改后 `node build_methods.mjs` 试跑 + grep `C\.` 计数不变 |
| R3 | **下标长度导致图/表溢出** | 中 | `EqualWReplace`/`BalancedReplace` 作为下标比 `TRI`/`BAL` 长 3–4 倍；`I_equal_t` 等会挤占表列与图内公式。缓解：表内用短名 + Full name 列（2a 已就位）；图内保留短名图例 + 图注全称 |
| R4 | **页数与版面漂移** | 中 | 更长标签会改变折行；当前 47 页为验收基准。缓解：S8 复测页数，若增加需记录并核对表/图未跨页断裂 |
| R5 | **改名不彻底 → 新旧混用** | 中 | 20 张表中 19 张含符号、`results.md` 183 处引用，漏改会造成"同一对象两个名字"。缓解：以本文件 §3.1 计数为对账基线，改后重跑同一计数脚本，目标为"旧名 = 0" |
| R6 | **图内标签与图注不一致** | 中 | 图内由脚本生成、图注在 `figures.json`，两处独立编辑。缓解：S6 后逐图对照（图内 ↔ 图注）抽查 13 个 figure key |
| R7 | **连带文档口径漂移** | 低 | 本仓库历史上多次出现"源改了、索引/README 未同步"。缓解：§3.6 清单逐项打勾 |
| R8 | **数值被误改** | 低 | 风险来自误替换（如把 `D` 当数字/把 `S` 当单位）。缓解：S2 的 `git diff` 必须只含标签 token；冻结 CSV 哈希前后一致 |
| R9 | **是否值得改** | 决策项 | 外部评审的核心诉求是"可读性"；2a 已覆盖"首现强调 + 全称列 + 图注全称"。若时间紧张，可只做方案 A 且**J/L 与公式不动**（改动面最小），把"整批改名"留到 major revision |
| R10 | **PPT 重出成本** | 低 | 重出链已跑通（58 页、0 finding）；纯标签改动不涉及数据 |

---

## 6 本文件明确"未做"

1. 未执行任何改名（`manuscript.md` / `results.md` / `tables.json` / `figures.json` / `build.py` / 图源脚本 / PNG / PPTX 均未因本方案改动）。
2. 未重新渲染任何图、未重出 PPT、未重跑实验、未用 GPU、未改任何数值。
3. 未改动 `docs/论文与图件问题汇总_仅复核_20260921.md`（另一任务在写）。
4. §3.1 的计数含少量非标签 token（代码标识符、`ABL-C`、marker `"D"`），已在表内标注，仅作量级参考。
# 执行状态更新

2026-09-25 修订已按老师最新要求执行描述性命名，覆盖正文、表格、公式描述性下标、图例和 PPT。真实数学变量保留；实验文件和内部 ID 保留以便追溯。当前验收见 [修订与验收](paper_complete_review_20260920/修订说明与验收_20260925.md)。以下是原始方案，不再表示仍待授权。
