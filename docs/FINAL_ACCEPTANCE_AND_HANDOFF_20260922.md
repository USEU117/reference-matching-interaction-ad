# 最终验收与交接（论文补充部分与图表生成说明）— 2026-09-22/23

> **给下游 AI 助手 / 作者**：本文件是**最终收口**件。前六节是验收与冲突记录（每条都能指向文件或实测输出）；**第七节起是"怎么写、拿哪张表/哪张图、哪些不能写、哪些不能改"的操作说明**。
> 方案与论证见 `docs/METHOD_COMPARISON_PRESENTATION_PLAN_20260922.md`；B 线的详细写作说明见 `docs/METHOD_COMPARISON_HANDOFF_20260922.md`（本文件不重复其论证，只做索引与纪律汇总）。
> 本轮**未做 git 提交、未推送、未用 GPU、未跑新实验**；`baseline_common_region.csv` 与 `data/**` 全程未触碰。
> 环境：Windows / PowerShell，解释器 `.venv-anomalyclip\Scripts\python.exe`。

---

## 0 一句话状态

| 层 | 状态 |
|---|---|
| 权威稿 | `docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260920.docx`，**47 页 / 20 表 / 22 内嵌图 / 12 编号公式（142 原生数学对象）/ 34 文献 / 17,200 词**，SHA-256 `194681CFCFEEF9F64D6D368C0F3FB70F7D19049F35A496063E99BBE3C9E5E625` |
| 稿件侧 | 摘要与 Data and Code Availability 的 URL 已一致；命名温和版（`Full name` 列 + 首现加粗）已在盘并复测；Table 12 表注已按最保守表述 |
| 实验侧 | 同口径 448 子集表 A/表 B + 协议杠杆实算 + 图 S6 全部落盘、过门禁；冻结表/扩展表/`data/**` 逐字节未变 |
| 门禁 | `pytest` 260 passed；`qa_layout.py` 0 problem；`figure_font_gate --self-test` 4/4；`build.py` 退出 0；**`selfcheck.py` 67/69（2 项失败，见 §4）** |
| git | `main...origin/main [ahead 2]`（HEAD `4d7f640`）；**未提交、未推送** |

---

## 1 禁忌词与身份泄露：复扫结果（2026-09-23）

### 1.1 已修正（逐条"文件:行 → 改前 → 改后"）

> 占位符：`〈教学称谓〉` = 本轮清单里的中文教学性称谓（两个词，原句直接写出）；`<旧物理目录名>` = 仓库改名前的物理目录名（同 `docs/SCI_STRING_AUDIT_20260922.md` 的写法）。

| 文件:行 | 改前 | 改后 |
|---|---|---|
| `docs/论文与图件问题汇总_仅复核_20260921.md:279` | `> 口径：把"〈教学称谓〉"按现有中性化口径写为…`（直接写出两个中文教学称谓） | `> 口径：原话中的教学性称谓统一按现有中性化口径写为 **AI 辅助评审 / 外部评审**。` |
| 同上 `:345` | `与〈教学称谓〉⑥"检测图放正文"同向` | `与外部评审⑥"检测图放正文"同向` |
| 同上 `:413` | `**这是〈教学称谓〉⑥所指的"检测结果图"主体…**` | `**这是外部评审⑥所指的"检测结果图"主体…**` |
| 同上 `:430` | ``旧名 `<旧物理目录名>` 现为指向新名的 **junction**``（改前直接写出旧物理目录名） | ``旧名（`<旧物理目录名>`）现为指向新名的 **junction**`` |
| `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md:45` | `C1/C17；T02；〈教学称谓〉要求⑤` + `**补**（〈教学称谓〉本轮明确要求…）` | `C1/C17；T02；外部评审要求⑤` + `**补**（外部评审本轮明确要求…）` |
| 同上 `:47` | `C7/C8；〈教学称谓〉要求⑥` + `**补**（〈教学称谓〉⑥明确"…"）` | `C7/C8；外部评审要求⑥` + `**补**（外部评审⑥明确"…"）` |
| 同上 `:110` | `（建议补，〈教学称谓〉⑥同向）` | `（建议补，外部评审⑥同向）` |
| `.trae/documents/night_run_handover_20260917.md:340-341` | `docs/PAPER_OUTLINE_TEACHER_REVIEW_20260914_CN.md` / `docs/paper_outline_teacher_review_20260914/新主题论文详细提纲_〈教学称谓〉审阅版_20260914_更新版.docx` | `docs/PAPER_OUTLINE_REVIEW_20260914_CN.md` / `docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx` |
| `scripts/paper_complete_review_20260920/figures.json`（14 处 `path`/`parts`） | `D:\STUDY\My_github\<旧物理目录名>\docs\paper_complete_review_20260920\figures\…` | `docs/paper_complete_review_20260920/figures/…` |
| `docs/paper_complete_review_20260920/English_Manuscript_Source.md`（11 处图链） | `D:/STUDY/My_github/<旧物理目录名>/docs/…` | `docs/…` |
| `docs/main_figure_revision_20260920/English_Manuscript_Source.md`（1 处图链） | 同上 | `docs/main_figure_revision_20260920/Main_Figure_20260920.png` |

### 1.2 命中统计

| 口径 | 改前 | 改后 |
|---|---|---|
| `docs/**` + `README.md` 中的六个中文教学性称谓词（人工可读面） | **9 处 / 2 文件**（`EXPERIMENT_GAP_ANALYSIS` 3 行 5 处 + `论文与图件问题汇总` 3 行 4 处；另 `.trae/**` 未跟踪文档 1 处） | **0** |
| 6 个重点文件（`EXPERIMENT_GAP_ANALYSIS`、`NAMING_MIGRATION_PLAN`、`METHOD_COMPARISON_{HANDOFF,PRESENTATION_PLAN}`、`论文与图件问题汇总`、`REMEDIATION_PLAN`、`README.md`） | 各有命中 | **全部 0** |
| 旧绝对路径（`D:\STUDY\My_github\<旧物理目录名>`，人工可读源 + 其生成物） | `figures.json` 14 处 + 2 个生成 md 共 12 处 | **0**（重建后生成物实测残留 0） |
| 旧物理目录名 / 旧仓库名（tracked，非 `experiments/**`、非 `data/**`） | 见 §1.3 | 仅保留 §1.3 所列记录类文件 |

### 1.3 保留项与理由（"判定不确定 → 保留并登记"）

| 文件 | 命中 | 保留理由 |
|---|---|---|
| `docs/RENAME_LOG_20260922.txt` | 旧物理目录名 5 处 | **改名作业的唯一作业记录**（`state BEFORE/AFTER`、9/9 PASS 清单、新旧路径对照）；删改即摧毁该操作的证据。所指目录是 gitignored 的 junction，未公开 |
| `docs/SCI_STRING_AUDIT_20260922.md` | 旧物理目录名 37 处、旧 `lesson_notes` 目录名 1 处、`supervisor` 1 处 | 该文档是**上一轮的字符串审计报告**，这些串是它审计的**对象本身**（改前/改后映射表）；改写会使其失据。其 §7 已自述"逐字稿原话按历史记录不改" |
| `docs/PROJECT_CLEANUP_AUDIT_20260922.md` | `.tmp_teacherfig_20260910`、`.tmp_lesson_20260912/*_docx_extract.json`、`teacherfig` | 记录的是 **gitignored 临时目录的真实文件名**；`experiments/dynamic_fusion/validation_handoff_20260911/E8/figure_version_binding.md` 与 `figure_render_qa.json`（**红线区，不可改**）用的是同一串名字，只改文档一侧会造成跨文档不一致 |
| `docs/PROJECT_PROGRESS_AND_MANUSCRIPT_PLAN_FOR_SUPERVISOR_EN_20260827.md`（文件名本身） | 5 处引用 + `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256:11` | **被哈希清单登记且哈希当前匹配**（`e239d3de…`）⇒ 按"哈希登记不改"规则保留 |
| `docs/archive_pre202609/PROJECT_STATUS.md:177,185,198` | `supervisor` | 指**进程 supervisor**（串行编排进程），非"〈教学称谓〉"语义 |
| `BASELINE_EXPANSION_PLAN_20260921.md:87`、`docs/paper_writing_preparation_20260830/{26,27}_*.md`、`scripts/.../build_dc_fnet_draft.py:149` | `teacher` / `student-teacher`（含对应中文词） | 全部是**蒸馏术语**（EfficientAD 等文献的 student-teacher 范式），非外部指导痕迹 |
| `docs/figures_reference_matching_20260914/fig7_multimethod_*.json`（4）、`docs/manuscript_reference_matching_20260914/figures/fig7_multimethod_*.json`（4）、`docs/paper_complete_review_20260920/figures/multimethod/fig7_multimethod_*.json`（4）、`docs/archive_pre202609/figures_package_20260917/04_multimethod_cases/fig7_multimethod_*.json`（4）、`docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json`、`figures/primary_sources.json` | 各若干处旧绝对路径 | **生成器的溯源产物**（每个方法/样本的 `source` 绝对路径 + mtime + 字节数）；手改会与生成器失配、并使"这些图取自哪个冻结文件"失去可核性。若要清，需改 `build_fig7_multimethod_samples.py` / `build_deck.mjs` 并把整批图重出——**本轮未做，交作者决定** |
| `experiments/**`（79k+ 处）、`submission_repro_20260827/**`（281 处）、`data/splits/*/manifest.json`（4 处）、`methods/**/SOURCE.json` | 大量 | **红线**：冻结证据字段 / 数据集清单 / vendored 上游来源；改一处即与冻结断言和哈希不符 |
| `scripts/**` 的 `.err`/`.log`/`.txt` 夜跑日志与硬编码绝对路径的 `.py`/`.ps1` | 1 137 处 | 日志是运行证据；脚本里的绝对路径是**可执行依赖**（改占位符即脚本失效），当前物理目录确实仍以旧名作为 junction 可达 |
| 提交信息层（4 条含身份串的提交，其中 2 条含旧仓库名） | 4 条 | 改写需 `filter-repo` + 强推，**属需作者书面授权**的操作；本轮只出方案（见 `SCI_STRING_AUDIT_20260922.md` §4） |

---

## 2 冲突与时效性：清单与已修正处

### 2.1 冲突清单（一处 vs 另一处 vs 建议口径）

| # | 一处说法 | 另一处说法 | 建议口径 / 处置 |
|---|---|---|---|
| 1 | `README.md`（中英）"47 页 / 20 表 / … / **16,969 词**"、`REMEDIATION_PLAN` 与 `论文与图件问题汇总` §八同 | 2026-09-23 Word COM 实测 **17,200 词**（字符 100,569） | **已改**：README 中英两处改为 "2026-09-23 实测 … 17,200 词"；`ISSUE_REGISTER` §〇ter 加刷新行；`ARTIFACT_INDEX.md` §2.1 与 `HANDOVER_20260919.md:17` 行内注明当前值。旧值 16,969（09-22）与 16,977（T10）作为历史值保留 |
| 2 | `docs/ARTIFACT_INDEX.md:51` 把 `docs/manuscript_reference_matching_20260914/build_validation.json` 的 **18 表 / 8 图**列在"有效（可直接作为口径依据）" | 权威稿为 **20 表 / 22 内嵌图** | **已加注**：该行标注"该 2026-09-14 链已 superseded；权威链为 20260920（20 表 / 22 内嵌图 / 12 公式 / 34 文献 / 47 页 / 17,200 词）；18/8 **不得当作当前值**" |
| 3 | `docs/HANDOVER_20260919.md:17`"**当前**论文标题方向见 `manuscript_reference_matching_20260914/…`（正文 8 图 / 18 表）" | 该链已 superseded | **已加注**：行内补"2026-09-23 校：该链已 superseded，当前权威稿为 …docx（47 页 / 20 表 / 22 内嵌图 …）" |
| 4 | `docs/ISSUE_REGISTER_20260920.md` §〇ter R-11"**已解决**（`origin/main..HEAD` = 0，HEAD `85d3207`）" | 2026-09-23 实测 `git status -sb` = `main...origin/main **[ahead 2]**` | **已加刷新行**：09-22 的 0 在当时成立；其后 `e61d039`、`4d7f640` 两次提交**未推送**。如实口径："远端已同步到 `a887633`；本地另有 2 个未推送提交（截至 2026-09-23）" |
| 5 | `docs/ISSUE_REGISTER_20260920.md:60/:69/:184` R-11"超前远端 15 提交"、R-20"只两个方法家族 / 方法家族仅两类" | 现为 **5 个外部家族**（PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AnomalyCLIP 零样本）；家族数刷新已在 §〇ter 有行 | **保留原登记 + 依既有体例在刷新行说明**；`REMEDIATION_PLAN` 末节 R-20 行的"限于两个方法家族"加注"现状 5 家族"，**禁止表述（SOTA / 全面领先）不变** |
| 6 | `docs/REMEDIATION_PLAN_20260920.md` P0 验收"`python scripts\manuscript_build_20260914\build.py`，`build_validation.json` 仍为 tables 18 / figures 8 / equations 12 / refs 34" | 权威交付稿走 `scripts/paper_complete_review_20260920/` 链（20 表 / 22 内嵌图） | **两处并存、不互斥**：前者是**已冻结旧链**的验收行，后者是权威链；本轮在 `REMEDIATION_PLAN` 头部指针中再次指明（沿用 `论文与图件问题汇总` §八"跨文档口径矛盾" A/B 两条的处置） |
| 7 | 表 11（冻结 6 列）/ 表 12（扩展，9 方法列）/ 同口径 448 子集表（5 列 × 36 单元）三者关系 | — | **无"子集误写成全量"、无"漏掉不构成排名"**（实读复核）：`METHOD_COMPARISON_HANDOFF_20260922.md` §3.1"36 个类别单元 … 是表 11/12 的 144 单元的 **1/4**；不得写成'全量'或'四数据集完整协议'"；§3.3 与表注模板均明写"**不构成排名**"；`HARMONISED_SUMMARY.json` 的 `note` 亦写 "NOT a ranking"。**唯一一处可再收紧**的是 §1.3"可以写"块里"都是该子集中的最高水平"——已加括注"（该子集内的描述性读数，**不构成排名**）" |
| 8 | 统计口径：区间是否只对 `pixel_ap` | — | **已核对无冲突**：`harmonised_macro.csv` 只有 `interval_pixel_ap_lo/hi`；handoff §6.2 明写"区间只算了 `pixel_ap`"；**全仓未见"AUROC 区间"表述**。入稿时表注须写明"区间仅针对 `pixel_ap`" |
| 9 | figS6 编号是否与 S1–S5 冲突；`FIGURE_BINDING.md` 是否登记 | — | **无冲突**（既有图集止于 S5，S4 为两页合并图）；**已登记**为 `FIGURE_BINDING.md` **§十**（含脚本、来源、门禁、未入正文说明） |
| 10 | 权威源路径是否仍引用改名前的旧目录（`paper_complete_teacher_review_*`、`figures_teacher_revision_*`、`main_figure_teacher_revision_*`、`lesson_notes_*`、`PAPER_OUTLINE_TEACHER_REVIEW_*`） | — | **已修 `.trae/documents/night_run_handover_20260917.md`**；**其余命中仅两类**：(a) 改名/审计**记录件本身**（`RENAME_LOG_20260922.txt`、`SCI_STRING_AUDIT_20260922.md`、`PROJECT_CLEANUP_AUDIT_20260922.md`）——按 §1.3 保留；(b) **`experiments/dynamic_fusion/representation_matching_interaction_20260914/RUN_SUMMARY.json:50`** 与 `validation_handoff_20260911/E8/*`（红线区），仍写 `docs/paper_outline_teacher_review_20260914/…` 与 `docs/figures_teacher_revision_20260910/…` —— **该文件已不在盘**，属**过期指针**，登记不改（见 §6 第 3 条） |

### 2.2 已修正处清单（本轮动过的文件）

| 文件 | 改动性质 |
|---|---|
| `docs/论文与图件问题汇总_仅复核_20260921.md` | §八 追加"八·续 最终轮"；`:279/:345/:413/:430` 中性化 |
| `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` | `:45/:47/:110` 中性化；新增 §七（A01–A17 状态 + A18–A23 新欠缺） |
| `docs/REMEDIATION_PLAN_20260920.md` | 头部执行状态追加"2026-09-23 最终轮指针" |
| `docs/ISSUE_REGISTER_20260920.md` | §〇ter 追加 3 条刷新行（R-11 二次变化 / 词数口径 / 自检门禁） |
| `docs/ARTIFACT_INDEX.md` | §2.1 旧链 18/8 加注 superseded + 当前值 |
| `docs/HANDOVER_20260919.md` | `:17` 加"2026-09-23 校" |
| `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` | 新增 §十（图 S6 登记） |
| `scripts/paper_complete_review_20260920/figures.json` | 14 处绝对路径 → 仓库相对路径（图注/数值未动） |
| `docs/paper_complete_review_20260920/English_Manuscript_Source.md`、`docs/main_figure_revision_20260920/English_Manuscript_Source.md` | 生成物中的绝对图链 → 相对路径（并由 `build.py` 重建刷新前者） |
| `scripts/paper_complete_review_20260920/build_validation.json` | 由 `build.py` 重建刷新（内容度量不变） |
| `README.md` | 中英两处词数 16,969 → 17,200（日期 09-23） |
| `.trae/documents/night_run_handover_20260917.md` | 旧目录名 → 新目录名 |
| **未动** | `manuscript.md`、`results.md`、`tables.json` 的**科学内容**；`experiments/**` 证据字段；`data/**`；`LICENSE`；`requirements_repro.txt`；版式母本；`figure_sources/**`；图 1–8 与 S1–S5 |

---

## 3 实验欠缺终检（索引）

逐条状态见 **`docs/EXPERIMENT_GAP_ANALYSIS_20260922.md` §七**。摘要：

- **A01–A17 无一项因 B 线失效**；A01/A02（正文部分）/A03/A05/A06/A07/A10/A13 共 **8 项仍缺**，全部是**写作/图件/打包**类、**零 GPU**；A04/A08/A09/A11 维持"不补"；A12/A15/A16/A17 维持"已满足/已限定"；A14 仍待作者。
- **B 线新增欠缺 A18–A23**：A18 子集只覆盖 36/144 单元（不补，成本锚点 PatchCore@448 实测 52.4 min/36 单元 ⇒ 144 单元约 3.5 h GPU）；A19 区间只算 `pixel_ap`（不补，低成本可补项）；A20 WinCLIP+/AnomalyCLIP 的 448 属**代码级**排除（不补）；A21 SubspaceAD@448 仅 2 图冒烟（不补，排除依据是输入规则）；A22 子集内 PatchCore 塌缩为一列（不补，协议敏感度由 S6 承担）；A23 图 S6 未入正文（登记待作者）。

---

## 4 最终验收表（真实门禁，2026-09-23 实测）

| 项目 | 命令（仓库根执行） | 结果 | 判定 |
|---|---|---|---|
| 一致性：冻结表 | `Get-FileHash experiments/…/05_baselines_multi_dataset/baseline_common_region.csv` | `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` | **通过**（与运行前逐字节一致） |
| 一致性：扩展表 | `Get-FileHash experiments/…/05_baselines_ext_20260921/baseline_common_region_ext.csv` | `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B` | **通过** |
| 一致性：数据集清单 | 逐库比对 `data/splits/*/manifest.json` 与同目录 `manifest.sha256` | btad / mpdd / mvtec / visa **4/4 MATCH**；`git status --porcelain -- data/splits` 为空 | **通过** |
| 一致性：版式母本 | `Get-FileHash docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` | `9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837` | **通过**（与 F17 记录一致，未改） |
| 单元测试 | `.venv-anomalyclip\Scripts\python.exe -m pytest tests -q` | **260 passed**, 1 warning（SciPy/NumPy 版本提示），35.15 s，退出 0 | **通过** |
| 版面门禁 | `…\python.exe scripts\figures_reference_matching_20260914\qa_layout.py` | `TOTAL PROBLEMS: 0`（7 张幻灯片母版图；最小字号 11.29 pt，地板 11.0 pt），退出 0 | **通过** |
| 字号门禁自检 | `…\python.exe scripts\figures_reference_matching_20260914\figure_font_gate.py --self-test` | `self-test passed: 4 controls behaved as required`，退出 0 | **通过** |
| 图 S6 四道门禁 | `…\python.exe scripts\harmonised_20260922\build_figS6_protocol_sensitivity.py --out-dir <.tmp 临时目录>` | 102 个 text artist **全部 11.50 pt**、0 文本互压、0 文本压图、0 出页；退出 0；重渲染 PNG 与在盘 PNG **逐字节相同**（`0C6F801C…`） | **通过** |
| 图 S6 图注一致性 | python 读 `figS6_protocol_sensitivity.json` 比对 handoff §2.1 | `caption_en` / `caption_zh` **逐字一致** | **通过** |
| 权威稿构建 | `…\python.exe scripts\paper_complete_review_20260920\build.py` | 退出 0；`build_validation.json` = tables 20 / figures 8 / equations 12 / math 142 / refs 34；生成 md 绝对路径残留 **0** | **通过（但见下条）** |
| 权威稿字节可复现性 | 同一条命令连跑 3 次并比对 docx SHA-256 | `194681CF…`（运行前）→ `C6EE3A63…` → `81193BFA…`，**三次不同**；内容度量三次一致 | **不通过（新发现，需作者）**；已把 docx 还原为 `194681CF…` |
| 权威稿内容复测（python-docx） | `.tmp_finalcheck_20260923\check_docx.py` | `tables 20` / `inline_shapes 22` / `native_math_objects 142` / `Full name` 表头行 **2** / 加粗首现 token `[C,J,L,B,B,S,C,D,A1,DUP,TRI,BAL,E1,E2,E3]` / `Figure S6` **0** / `Figure S4` 3 | **通过** |
| 权威稿页数/词数（Word COM） | `.tmp_finalcheck_20260923\word_stats.ps1` | **47 页 / 17,200 词 / 100,569 字符** | **通过（词数口径已更正）** |
| 仓库自检 | `…\python.exe scripts\representation_matching_interaction_20260914\selfcheck.py` | `checks=69 / passed=67 / failed=2`，退出 **1**；失败项 `manuscript: the updated outline exists`、`read-only inputs were not written during this delivery` | **不通过（需作者）**；脚本就地改写的 `experiments/**` 两个 JSON 已 `git checkout --` 逐字节还原 |
| B 线口径一致性（只读） | python 读 `HARMONISED_SUMMARY.json` | `rows=180`；`region_vs_frozen` **36/36** `identical_region=true`；复用 4 列 `max_abs_delta = 0.0`；`frozen_table.rows=864`、`sha256` 前 8 位 `3C83AB00` | **通过** |
| git 状态 | `git status -sb` | `## main...origin/main [ahead 2]`；14 个 tracked 修改、10 条未跟踪 | **如实记录：本地 2 个提交未推送**（按要求不提交、不推送） |

**判定汇总**：**通过 12 项**；**不通过 2 项**（均为本轮**新发现**的既有状态：`build.py` 字节不可复现、`selfcheck.py` 2 项失败）；**需作者 1 项**（词数口径已自行更正，无遗留）。

---

## 5 本轮的边界（做了什么、没做什么）

- **没做**：git 提交 / 推送；任何 GPU 或新实验；`experiments/**` 证据字段与 `data/**` 的改动；`LICENSE`、`requirements_repro.txt`、版式母本、`figure_sources/**` 科学内容的改动；图 1–8 与 S1–S5 的改动；正文科学内容的改动。
- **做了**：文档中性化与时效性修正；`figures.json` 的路径写法；`build.py` 重建并复测；`selfcheck.py` 运行（并还原其副作用）；图 S6 的门禁复跑；冻结哈希与清单校验；本文件与 `§八·续` 的登记。
- **临时产物**：全部落在 `.tmp_finalcheck_20260923/`（无 `.tmp_*` 覆盖；运行后**已删除**），未进 git。

---

## 6 未做 / 不确定 / 需作者决定

| # | 项 | 现状与建议 |
|---|---|---|
| 1 | **`build.py` 非字节可复现**（F21） | 连跑三次 docx SHA 三个值；若要"可复现校验值"，需固定 docProps/时间戳或改为**内容**校验。本轮已把 docx 还原为 `194681CF…` |
| 2 | **`selfcheck.py` 2 项失败**（F22） | ① 大纲 docx `docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx` **不在盘**（从未入库，git 对象也没有；重建源 `.tmp_outline_20260914/{build.py,artifact.md,render_native.py}` 在盘）——是否重建/放回，或把该检查点改为"缺失即跳过并记 caveat"；② 冻结快照 3 处漂移（`_smoke` 下 2 个 `.npz` 缺失 + `REPORT_CN.md` 仅 mtime 变化）——是否把 `_smoke` 从冻结清单豁免 |
| 3 | **`experiments/**` 内的过期指针** | `representation_matching_interaction_20260914/RUN_SUMMARY.json:50` 仍指向已不存在的 `docs/paper_outline_teacher_review_20260914/…docx`；`validation_handoff_20260911/E8/figure_version_binding.md` 等仍用旧目录名 `figures_teacher_revision_20260910`（该目录已改名为 `figures_expanded_20260910`）。红线区，**未改**；属"历史记录里的旧值" |
| 4 | **A14 AnomalyCLIP 检查点来源** | 仍待作者；Table 12 表注已按最保守写法（`auxiliary-domain-trained prompt learner`） |
| 5 | **A23 图 S6 是否入稿** | 若入稿需在 `figures.json` 增设 S6 条目并重建 docx（页数/表数需复测） |
| 6 | **整批改名（T09 方案 A/B）** | 未执行；方案见 `docs/NAMING_MIGRATION_PLAN_20260922.md`。执行会连带 6 张图重渲染 + PPT/docx 重出 |
| 7 | **提交信息层的旧仓库名（4 条提交，2 条含旧名）** | 需 `filter-repo` + 强推，**须作者书面授权**；方案见 `SCI_STRING_AUDIT_20260922.md` §4 |
| 8 | **生成物中的绝对路径（fig7_multimethod JSON × 16、`FIGURE_SLIDE_INDEX.json`、`primary_sources.json`）** | 需改生成器后重出，本轮未做 |
| 9 | **`19 表` / `46 页` / `未推送` 等历史值** | 按"历史记录不改写 + 加注"处理，已在前几轮加注；本轮只新增词数一条 |

---

## 7 可用表格（列名 / 含义 / 来源 / 入稿纪律）

目录别名：`HARM = experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/`，`EXTB = …/05_baselines_ext_20260921/`，`MULTI = …/05_baselines_multi_dataset/`。

### 7.1 表 A（B 线新增，**尚未入正文**）：`HARM/harmonised_common_region.csv`

**180 行 = 5 个方法列 × 36 个类别单元**（4 数据集 × 全部类别 × **seed 0 × K = 1**）。列结构与既有共同区域表**逐列对齐**：

| 列名 | 含义 | 来源/备注 |
|---|---|---|
| `method` | 5 个固定值：`controlled_A1_J`、`controlled_A1_L`、`anomalydino_canvas`、`anomalydino_canvas_rotation`、`PatchCore_harmonised448` | 前 4 列**复用**既有逐图产物（未重跑）；PatchCore 那列本轮在 6 GiB 卡上**重跑** |
| `dataset` / `seed` / `shot` / `category` | 单元键 | 与表 11/12 的同名单元一一对应 |
| `revision` | 评估修订号（mpdd = `study`，其余 = `corrected`） | 与冻结表同义 |
| `region_grid` | 该单元共同区域栅格 | 本表 **36/36 与冻结表完全相同（392×392）**（`region_mode = frozen`） |
| `region_fraction_of_canvas` | 区域占画布比例 | 与冻结表逐行相同 |
| `pixel_ap` / `pixel_auroc` | 该单元该方法的**合并 rank-based** AP/AUROC（像素池化，非逐图平均） | 复用 `s8_common_region.pooled_ap_auroc` |
| `n_pixels` | 该单元参与统计的正像素总数 | — |
| `seconds` | 本表重采样耗时（**不是性能结果**） | 不得当作效率证据 |
| `source` | 产出该分数图的 npz 绝对路径 | 溯源字段 |
| `source_table` | 常量 `05_baselines_harmonised_20260922` | — |
| `note` | 常量说明：`harmonised subset: single input geometry (short side 448)` | — |

### 7.2 表 B（B 线新增，**尚未入正文**）：`HARM/harmonised_macro.csv`

| 列名 | 含义 |
|---|---|
| `method, dataset, seed, shot` | 单元键 |
| `n_categories` | 该数据集的类别数（btad 3 / mpdd 6 / mvtec 15 / visa 12） |
| `macro_pixel_ap` / `macro_pixel_auroc` | 逐类先在类内池化、再跨类取宏平均（**点估计**） |
| `interval_pixel_ap_lo` / `interval_pixel_ap_hi` | **图像级配对自助区间**（B = 1000；`np.random.default_rng([seed, shot, replicate])`；同一类内每次抽同一批图给所有方法；2.5/97.5 百分位）。**只有 `pixel_ap` 有区间**；点估计在完整栅格上算，区间在 **stride-8 子样本**上复算（沿用本仓 `p1_stats_bootstrap.py` 的 `STRIDE = 8`），两者不必逐位相等 |

**表 B 主读数（宏 pixel AP [95% 图像级配对自助区间]）**

| 方法列 | BTAD (3 类) | MPDD (6 类) | MVTec (15 类) | VisA (12 类) |
|---|---|---|---|---|
| `controlled_A1_L` | 0.6278 [0.5701, 0.6735] | 0.3167 [0.2980, 0.3409] | 0.5612 [0.5446, 0.5817] | 0.3493 [0.3215, 0.3721] |
| `controlled_A1_J` | 0.6174 [0.5594, 0.6642] | 0.3123 [0.2935, 0.3366] | 0.5582 [0.5413, 0.5783] | 0.3439 [0.3166, 0.3671] |
| `anomalydino_canvas_rotation` | 0.5881 [0.5354, 0.6315] | 0.2929 [0.2763, 0.3195] | 0.5582 [0.5394, 0.5811] | 0.3256 [0.2978, 0.3502] |
| `anomalydino_canvas` | 0.5576 [0.4992, 0.6058] | 0.2846 [0.2676, 0.3115] | 0.5611 [0.5400, 0.5827] | 0.3032 [0.2754, 0.3278] |
| `PatchCore_harmonised448` | 0.3725 [0.3315, 0.4290] | 0.2110 [0.1978, 0.2272] | 0.5050 [0.4860, 0.5246] | 0.3228 [0.2960, 0.3468] |

### 7.3 表 11（冻结）/ 表 12（扩展）/ 表 A 三者关系（**入稿必须写清**）

| 表 | 源 | 规模与协议 | 纪律 |
|---|---|---|---|
| **Table 11**（正文，冻结） | `MULTI/baseline_common_region.csv`（SHA `3C83AB00…`，864 行） | 4 数据集 × 6 方法列，**各方法原生协议** | **继续冻结未改**；六列数值与表注**一个字都没动** |
| **Table 12**（正文，扩展） | `EXTB/baseline_common_region_ext.csv`（SHA `1C770129…`，1188 行 = 864 逐行照抄 + 324 新） | 追加 3 个外部家族（SubspaceAD 256 fp16 / WinCLIP+ 240 / AnomalyCLIP zero-shot 518），**各自原生协议** | **不构成排名**（表注已写）；AnomalyCLIP 列只有 36 单元、无 seed/K 循环，**不可与 K 循环方法配对**；SubspaceAD 256↔官方 672 的偏离须写进协议列；表注须写"若某方法覆盖范围为子区域，则重算会改变表 11 数值；本批不属此情形" |
| **表 A / 表 B**（B 线新增，**未入正文**） | `HARM/*` | **子集**：5 个方法列 × **36 个类别单元**（表 11/12 的 **1/4**），**统一输入几何（短边 448）** | **不构成排名**（未做跨方法配对差异检验、未做 SOTA 主张）；**不得写成"全量"或"四数据集完整协议"**；区间只针对 `pixel_ap`；与表 11/12 **同单元、同区域、同指标**，故可**逐格对照**（唯一系统变化量是输入几何）；接触拉伸族（SubspaceAD / WinCLIP+ / AnomalyCLIP）**不在子集内**，原因见 `HARM/PREFLIGHT.json` |

---

## 8 可用图（路径 / 图注 / 建议插入位置）

### 8.1 图 S6（B 线新增，**未入正文**）

| 项 | 值 |
|---|---|
| 路径 | `docs/figures_reference_matching_20260914/figS6_protocol_sensitivity.{png,pdf,json}`（PNG `0C6F801C…`，645,557 B；PDF `A541E824D31CB7EE8F2826CD942809701F4896670786FD36D1791DCBC1CAECDA`） |
| 图注（**英文，可直接入稿**） | 见 `figS6_protocol_sensitivity.json → caption_en`，与 `METHOD_COMPARISON_HANDOFF_20260922.md` §2.1 **逐字一致**：`Protocol sensitivity of the external-method comparison. Each row is one method under its own published native configuration, and the two dots joined by a line are the same method under two configurations, so the connector length is that method's protocol lever. Measured from the frozen per-unit pixel AP already on disk, PatchCore's own two configurations differ by 0.100 macro pixel AP on average (144 units), i.e. 3.8x more than the 0.026 separating SubspaceAD 256 fp16 from AnomalyDINO canvas, and switching only PatchCore's configuration reverses which of the two is ahead on 33.3% of units. The values are therefore context, not a ranking: no ordering, interval, significance test or state-of-the-art claim is made here.` |
| 图注（中文对照） | 同 JSON `caption_zh`（见 handoff §2.1） |
| 建议插入位置 | **补充材料**，排在 S5 之后（本图集既有编号止于 S5）；若作者要求进正文，建议放 §4.2.7（外部方法上下文）末，并同步更新 `FIGURE_BINDING.md`、`ARTIFACT_INDEX.md` 与 `figures.json`（重建 docx 后页数/表数需复测） |
| 门禁 | `figure_font_gate` 四道（11.50 pt / 0 互压 / 0 压图 / 0 出页）全部通过；PNG 可复现（重渲染逐字节相同）；**不生成** `qa_layout.py` 版面（刻意） |
| 绑定 | `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` **§十** |

### 8.2 正文既有图（**已在 docx 内，22 内嵌图**；不要重出）

| 图号 | 键（`figures.json`） | 正文位置 | 类型 |
|---|---|---|---|
| Fig 1 | `framework` | §3.2 | 框架 |
| Fig 2 | `matching` | §3.3 | 方法机制 |
| Fig 3 | `constructions` | §3.4 | 方法构造 |
| Fig 4 | `effects`（a/b 两页） | §4.2.3–4.2.4 | 结果曲线 |
| Fig 5 | `budget_category`（a/b/c） | §4.2.5 | 结果曲线 |
| Fig 6 | `cases_good`（a/b） | §4.2.6 | **定性检测（正文）** |
| Fig 7 | `cases_bad` | §4.2.6 | **定性检测（正文）** |
| Fig 8 | `resources` | §4.2.7 | 资源 |
| Fig S1 | `encoders_geo` | 补充方法图 | 方法几何 |
| Fig S2 | `shared_op_ablation` | 补充结果图 | 探索性消融 |
| Fig S3 | `extra_cases`（6 页） | 补充结果图 | 几何诊断 + 8 例逐图交互 |
| Fig S4 | `stability`（2 页：收敛 v2 + 稳定性） | 补充结果图 | bootstrap 稳定性 |
| Fig S5 | `speed_vram` | 补充结果图 | 计时/显存 |
| **Fig S6** | **无键（未入表）** | — | **协议敏感度（新增，未入正文）** |

### 8.3 未进正文的图（**缺口 F05 / A05**）

- **36 张逐类别多方法对比图**：`docs/figures_reference_matching_20260914/fig7_multimethod_<dataset>_s0_k4_<category>.{png,pdf}`（mpdd 6 + btad 3 + mvtec 15 + visa 12），在已交付 PPT 第 23–58 页；正文仅在 `manuscript.md:247` 以一句文字提及。
- **建议**：从 36 张中选 **2–3 张代表图**（跨数据集 + 跨缺陷类型，含 query、GT、各方法热图；本文列与 GT 相邻）放进 §4.2.6 末或 §4.2.7，其余留补充材料并注明选择规则与色标规则。

---

## 9 必须写明的限制（硬要求，缺一条就会被审稿人抓）

1. **表 A/表 B 是子集**：36 个类别单元（seed 0 × K = 1），是表 11/12 的 144 单元的 **1/4**；**不得**写成"全量"或"四数据集完整协议"。
2. **统一协议 X = 短边 448 + 同一共同区域 + 同一 rank-based 池化指标**；拉伸族（SubspaceAD / WinCLIP+ / AnomalyCLIP）**不在子集内**，故本表**不能**读作"全体外部方法在统一协议下的横评"。
3. **不构成排名**：本表刻意抹平了协议差异，剩下的差值仍混有"方法 + 各自实现细节"；**未做**跨方法配对差异检验，**未做** SOTA 主张；区间是**边际**区间（不是配对差区间），重叠/不重叠只能作描述。
4. **表 11 是冻结值**：六列数值与表注一字未改；表 A 复用 A1 两列与 AnomalyDINO 两列，与冻结表**逐格完全相同（最大绝对差 = 0.0）**——这可作为"评估口径未漂移"的证据引用。
5. **区间只针对 `pixel_ap`**；`pixel_auroc` 只有宏平均点值。点估计与区间不必逐位相等（区间在 stride-8 子样本上复算）。
6. **窗口口径**：表 A 的区域不是"子集成员自己覆盖范围的最大交集"，而是额外取**冻结表的共同区域**（`region_mode = frozen`），以便与表 11/12 逐格可比；代价是本子集放弃了成员本可覆盖的边缘区域。
7. **SubspaceAD 分辨率偏离官方设置**（256 vs 官方 few-shot 脚本 672，且关闭官方 `aug_count=30`）必须写进表 12 协议列与补充材料，**不得**作为"官方配置"表述。
8. **AnomalyCLIP 检查点来源未核实**：表 12 已按最保守写法标注 `auxiliary-domain-trained prompt learner`；作者确证前**不得**把它写成"纯零样本"或与零样本方法并列陈述。
9. **效率数据是部分阶段计时**（含参考库工作，排除初始化/指标计算/写盘），**不是**端到端墙钟、也不是 ms/image 或 FPS；显存继续区分进程内 allocated peak 与设备级监测。
10. **full-pixel 只有点估计**：用于方向一致性检查，**不得**写"full-pixel 统计显著/区间排除零"。
11. **S4 只证明"已存 bootstrap 估计的数值稳定性"**，不证明训练收敛，也不能替代跨支持集/跨种子/跨数据集的泛化稳定性。
12. **同机证据范围受限**：MPDD 三类别、seed 0、K = 1/4，每单元 1 次预热 + 3 次重复；共同硬件**不自动**消除输入/实现差异。
13. **对应方式（correspondence）只证明"零排除判定在各变体下保持"**，**不得**写"各变体等效/无差异/对应方式不影响结果"。
14. **BTAD 口径**：点估计接近零、区间跨零 ⇒ **方向未定**，**不是**零效应。

---

## 10 禁止的表述（反例清单）

| 不要写 | 为什么 | 可以改成 |
|---|---|---|
| `SOTA` / `state-of-the-art` / "全面领先" / "所有数据集、所有协议下都优于所有基线" | 本轮**没有**任何 SOTA 主张；表 A 覆盖 4 数据集 × 1 个 (seed, K) 子集、只与 5 列对照，且未做跨方法检验 | "在该子集与统一输入几何下，本文两条匹配规则的宏观 pixel AP 落在表 B 的区间内" |
| "表 A 是表 11/12 的更新版 / 取代表 11/12" | 表 11/12 是原生协议下的**冻结**上下文表；表 A 是另一口径的**子集** | "表 A 是在统一输入几何下的补充子集读数，与表 11/12 并列" |
| "我们的方法比 PatchCore 高 X，因为方法更好" / "PatchCore 差是因为分辨率低" | 差值里含协议/几何因素；反例在盘上：PatchCore 自身两配置平均差 **0.100**，比家族差 **0.026** 大 3.8 倍 | "同一方法的原生配置之间可以相差到与家族间差距同量级或更大，因此表中差值不能归因于方法" |
| "区间不重叠 ⇒ 显著优于" | 表 A 的区间是**边际**区间、且未做配对检验 | "两列区间不重叠（描述性）；本轮未做跨方法配对差异检验" |
| "外部对比覆盖四数据集六配置，限于两个方法家族"（R-20 旧措辞） | 现为 **5 个外部家族** + 本文 A1 两列 | "外部对比覆盖 5 个外部家族（PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AnomalyCLIP 零样本）与本文受控两列；跨组不作排名" |
| "所有对比方法都不需要训练" / "无超参数" / "零计算 / 零准备" | 预训练编码器与继承检查点**仍带训练来源**；参考库/coreset 属**准备计算**；分辨率、保留层、支持预算、高斯 σ、阈值等都是显式配置 | "本文评估的配置在**目标域**不做梯度优化；参考构造、特征编码与打分属**准备计算**"（T12 段落可直接用） |
| "端到端耗时 / 同步计时 / 整体加速比" | 效率数据只覆盖部分阶段 | "效率数据为**部分阶段**的计时，非同步端到端测量" |
| "full-pixel 统计显著 / full-pixel 区间排除零" | full-pixel 只有点估计（已登记限制） | "full-pixel 结果目前只有点估计，用于方向一致性检查" |
| "各对应变体等效 / 变体间无差异 / 对应方式不影响结果" | correspondence 只证明"零排除判定保持" | "在各对应变体下零排除判定保持" |
| "BTAD 无效应 / true null / essentially zero" | 区间跨零 = **方向未定** | "点估计接近零、区间跨零，当前数据不足以确定交互方向" |
| 把图 S4 说成"训练收敛曲线" | 冻结方法无目标域训练、无优化过程 | "已存 bootstrap 估计的数值稳定性诊断" |
| 在正文里把 `L` 叫 `local` | 正文术语是 **independent matching**（F04 已修，勿回退） | `L` = independent matching；`J` = joint matching |

---

## 11 复现命令（仓库根，`.venv-anomalyclip\Scripts\python.exe`）

```powershell
# ---- B 线：协议杠杆实算（只读，CPU 秒级）----
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\analyse_protocol_leverage.py

# ---- B 线：PatchCore 在短边 448 下重跑（GPU，4 个 group，实测 52.4 min；--skip-existing 断点续跑）----
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\run_patchcore_harmonised.py --datasets btad mpdd mvtec visa --seeds 0 --shots 1

# ---- B 线：共同区域评测 + 配对自助区间（CPU；复用 A1/AnomalyDINO 逐图 map）----
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\harmonised_common_region.py --mode eval --bootstrap 1000 --workers 4
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\harmonised_common_region.py --mode assemble --frozen-sha 3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB

# ---- B 线：图 S6（四道门禁内建；加 --out-dir <临时目录> 可只验证不改产物）----
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\build_figS6_protocol_sensitivity.py

# ---- B 线：SubspaceAD@448 冒烟（只为排除依据；GPU 约 1 min）----
.venv-anomalyclip\Scripts\python.exe scripts\harmonised_20260922\smoke_subspacead_448.py --image-res 448 --limit-images 2

# ---- 权威稿：重建 + 内容复测 ----
.venv-anomalyclip\Scripts\python.exe scripts\paper_complete_review_20260920\build.py
# 页数/词数用 Word COM（见 .tmp 里用过的 word_stats.ps1 写法：ComputeStatistics(2)/ComputeStatistics(0)）

# ---- 既有图集门禁 ----
node scripts\figures_reference_matching_20260914\build.mjs
.venv-anomalyclip\Scripts\python.exe scripts\figures_reference_matching_20260914\qa_layout.py
.venv-anomalyclip\Scripts\python.exe scripts\figures_reference_matching_20260914\figure_font_gate.py --self-test

# ---- 仓库自检与测试（注意：selfcheck.py 会就地改写 experiments/** 的两个 JSON）----
.venv-anomalyclip\Scripts\python.exe scripts\representation_matching_interaction_20260914\selfcheck.py
.venv-anomalyclip\Scripts\python.exe -m pytest tests -q
```

---

## 12 冻结值（**不得改动**）

| 对象 | 权威值 | 校验命令 |
|---|---|---|
| 冻结共同区域表 | `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` | `Get-FileHash experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines_multi_dataset\baseline_common_region.csv` |
| 扩展共同区域表 | `1C77012971A4C2EBA52512A8D7850C0DA072B8107FFFE316A74E3C39DF73EC4B` | 同目录名替换为 `05_baselines_ext_20260921\baseline_common_region_ext.csv` |
| 数据集划分清单 | `data/splits/{btad,mpdd,mvtec,visa}/manifest.json`（4/4 与其 `manifest.sha256` 匹配） | 见 `data/splits/*/manifest.sha256` |
| 版式母本（**不可由源重建的二进制输入**） | `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` = `9DB99E60CD3024D1D49429641EDD6E49777BF014A3F4B7FB674C9C20338FB837` | `Get-FileHash` |
| 已发布图 | 图 1–8、S1–S5 的 PNG/PDF 与 PPT 内嵌位图 | 不得重出、不得重渲染（除 F01/F02/P04/F14 那批已获批的改动） |
| `experiments/**` 证据字段 | `provenance.csv`、`input_manifest.json`、`*_audit*.json`、逐图 JSON 的 `source`、各 `*_SUMMARY.json`、`SELFCHECK.json`、`READONLY_PROOF.json` | **不改**（`selfcheck.py` 会改写后两者，运行后须 `git checkout --` 还原） |
| `data/**`、`LICENSE`、`requirements_repro.txt`、`figure_sources/**` 科学内容 | — | **不改** |
| 表 11 六列数值与表注 | `tables.json → baselines` | **一字未改**，不得与表 12/表 A 混排 |
| B 线数值 | `HARM/protocol_leverage.json` 的 0.1000 / 0.0265 / 3.8× / 33.3%（48/144） | 只读聚合，可复算；不得手改 |

