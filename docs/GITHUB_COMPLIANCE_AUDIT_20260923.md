# GitHub 合规审查与收尾记录 —— 2026-09-23

> 目的：把**上一轮审查结论**与**本轮（收尾轮）改动**合并成一份可交接文档，并列出**待作者决定项**。
> 纪律：不 `git add`、不 commit、不推送；不改实验数值、不改论文源、不动上一轮已归档结果。
> 基线：`HEAD = fc08b4e`（`main [origin/main]`）。

---

## 1. 上一轮审查结论（复述 + 本轮实测复核）

| # | 结论 | 本轮实测（命令 / 值） |
|---|---|---|
| 1 | **体积：tracked 3.31 GB** | `git ls-files` 计数 **16,105** 个文件；合计 **3,308,895,330 B ≈ 3.31 GB（3.08 GiB）**（PowerShell 逐文件 `Length` 求和；少量 CJK 文件名的条目因 PowerShell `Test-Path` 限制未计入，量级可忽略） |
| 2 | **`>50 MB` 的 tracked 文件共 3 个**（全为 pptx，无 `>100 MB`） | ① `docs/paper_complete_review_20260920/All_Figures_Complete_20260923.pptx` 69.1 MiB（72,415,664 B）② `…/All_Figures_Complete_20260920.pptx` 68.8 MiB ③ `…/All_Figures_Finalized_20260920.pptx` 68.3 MiB。**无 >100 MB 文件** |
| 3 | **`.git` ≈ 7.1 GB** | `Get-ChildItem .git -Recurse` 求和 = **6.62 GiB = 7.11 GB** |
| 4 | **密钥：0** | 上一轮扫描未发现密钥/凭据；本轮未新增任何含凭据的文件 |
| 5 | **数据集与预训练权重均未入库** | 数据集在 `data/**`（`.gitignore` 排除）、权重由 `.gitignore` 的 `*.pt` 与 `methods/` 排除；`docs/MODEL_WEIGHTS.md` 记录"本包不携带任何大权重" |
| 6 | **本机绝对路径分布** | `git grep -l "My_github"` 命中 **1,503** 个 tracked 文件（多为历史记录、脚本注释与红线区状态记录；见第 4 节待决定项） |
| 7 | **禁忌词逐处判定** | 除**唯一一处非表格表述**（`docs/REMAINING_REVIEW_AFTER_AI_20260923.md:32` 的"导师"）外，其余命中均为**历史登记 / 蒸馏术语**（如 `student-teacher` 蒸馏范式、`supervisor`＝进程编排 supervisor、被哈希清单登记的历史文件名），上一轮判定**保留不动**。本轮已改写该 1 处（见 2.2） |
| 8 | **tag：10 个，最新早于 09-23 扩版** | `git tag` = **10** 个；最新为 `reference-figures-20260920`（提交日 **2026-09-20**，早于 09-23 扩版/收口） |

---

## 2. 本轮改动（收尾轮）

### 2.1 删除第 2 个空目录（0 删除 tracked 文件）

| 项 | 证据 |
|---|---|
| 目标 | `docs/manuscript_reference_matching_20260914/figures/superseded/` |
| 删除前文件数 | `Get-ChildItem -Force -Recurse \| Measure-Object` = **0** |
| tracked 引用 | `git ls-files docs/manuscript_reference_matching_20260914/figures/superseded` = **空**（空目录不可被 git 跟踪）；无任何脚本/配置按该路径读取 |
| 删除后 | `Test-Path` = **False** |
| 备注 | 该路径仅在历史文档中被**过去时**提及（如 `SUPERSEDED_20260921.md:23`"此前已收纳更早版图"、`PROJECT_CLEANUP_AUDIT_20260922.md` §#2 记"9 个同哈希副本**已删**"），属历史记录，不构成 live 引用 |

> 第 1 个空目录现状确认：`docs/` 顶层现**无空目录**（逐目录 items 均 >0）。`FOLDER_CONSOLIDATION_20260923.md` §6 曾记其 `docs/` 顶层"1 个 0 文件、名称含非中性词的遗留空目录"，该目录在本轮之前**已不在盘**，本轮确认无误。

### 2.2 改写唯一一处非表格禁忌表述

| 文件:行 | 改前 | 改后 |
|---|---|---|
| `docs/REMAINING_REVIEW_AFTER_AI_20260923.md:32` | 当前版本可继续供**导师**审阅 | 当前版本可继续供**外部评审**审阅 |

改后该文件禁忌词自查 = **0**（`REMAINING_REVIEW_AFTER_AI_20260923.md` 未出现在第 3 节的禁忌词命中里）。

### 2.3 `.gitignore` 收口

| 改动 | 位置 | 目的 |
|---|---|---|
| 新增 `/.trae/`（写作 `.trae/`） | IDE/OS 段（`.gitignore:66`） | 防止本机 IDE 目录被误提交 |
| 新增 `!docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx` | `*.docx` 规则之后（`.gitignore:83`） | **只放行这一个**现役权威 docx；旧版 `…20260920.docx` 与全部 `.bak_*` 仍被忽略 |

三方验证（`git check-ignore -v`）：

```text
新 docx    → .gitignore:83:!docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx
旧 docx    → .gitignore:80:*.docx            （仍被忽略）
.bak 文件  → .gitignore:77:*.bak*            （仍被忽略）
.trae/     → .gitignore:66:.trae/            （被忽略）
git status -- <新 docx>  →  ?? docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx
```

### 2.4 新增三个标准文件

| 文件 | 要点 |
|---|---|
| `CITATION.cff` | CFF **1.2.0**；英文标准 `message`；`title` = 少样本工业异常检测的"参考匹配 × 表征交互"；`authors` = `Li` / `Yuening`；`type: software`；`license: MIT`；`repository-code` = 仓库 URL。**`affiliation` / `orcid` / `version` / `date-released` / `doi` 一律以注释占位**，注明"待作者补充"，未代填 |
| `.gitattributes` | `* text=auto eol=lf`；`*.png *.pdf *.docx *.pptx *.npz *.npy *.pt *.pth *.zip` 标为 `binary`，避免 diff/CRLF 噪声 |
| `THIRD_PARTY_NOTICES.md` | ① 数据集许可与**不再分发原始数据**声明（MVTec CC BY-NC-SA 4.0 / VisA CC BY 4.0 / BTAD CC BY-SA 4.0 / MPDD CC BY-NC-SA 4.0 / KSDD2 CC BY-NC-SA 4.0），逐条给"若被引用需如何署名"；② 声明 `experiments/dynamic_fusion/v2/branch_cache_queue/reference_views/` 下 **945 张 PNG 为 BTAD/MPDD 正常参考图的亮度/对比度派生视图**（`scripts/prepare_normal_reference_views.py` 的 `VIEW_SPECS`：identity + brightness 0.90/1.10 + contrast 0.90/1.10），受原数据集许可约束，**本项目 MIT 不覆盖这些图像**；③ `methods/`（本地镜像，gitignored）+ `patches/`（7 个 diff）派生自 AnomalyCLIP / AnomalyDINO / PatchCore / PromptAD / WinCLIP 等上游仓，**仅存来源与 diff，不再分发源码**；④ 预训练权重（DINOv2、CLIP、WideResNet50-2、BERT、GroundingDINO、SAM-HQ 等）不再分发。信息不足处（MPDD 镜像来源、UniVAD/SubspaceAD 上游许可、未登记权重许可）标 **to be verified**，未编造条款 |

### 2.5 README 收口

- 现役 docx 链接的 **href 由目录改为文件本身**（中英两处）：`…20260923.docx`（可点、指向文件）。
- 文档获取一节写明：**权威稿 docx 已随仓库提供（纳入 git 跟踪）；复现包（`dist/`，2488 文件 / 470.7 MB ≈ 449 MiB）走 Release / Zenodo，未入库**。
- 新增一行指向 `CITATION.cff` 与 `THIRD_PARTY_NOTICES.md`（中英两处）。
- **口径未改**：152 原生数学对象 / 19,434 词 / deck 63 页（及其余页/表/图/公式/文献数）保持上一轮已修正值。

### 2.6 记录文档

- 本文件（`docs/GITHUB_COMPLIANCE_AUDIT_20260923.md`）。
- `docs/MASTER_TODO_PAPER_PPT_FIGURES_20260923.md` §五 E 组新增 **E-20…E-24**（编号接续）。
- `docs/GITHUB_METADATA.md` 追加本轮上传变更一行（§6）。

---

## 3. 复验输出

### 3.1 `git status --porcelain` 概览

```text
 M README.md
 M experiments/dynamic_fusion/innovation_breadth_20260908/round12/RESULTS_s0_k2.json
?? .gitattributes
?? CITATION.cff
?? THIRD_PARTY_NOTICES.md
?? docs/GITHUB_COMPLIANCE_AUDIT_20260923.md
?? docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx
?? .trae/            （新增后被 .gitignore 的 .trae/ 忽略，不再出现）
?? docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md   （并行产物，非本轮）
?? experiments/dynamic_fusion/innovation_breadth_20260908/round13/   （并行产物，非本轮）
?? scripts/innovation_breadth_20260908/probe_breadth12.py            （并行产物，非本轮）
```

> 说明：`.trae/` 原先为 `??`，加入 `.gitignore` 后应消失；`docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md`、`experiments/…/round13/`、`scripts/…/probe_breadth12.py` 是**并行流程**产物，本轮**未触碰**。
> **无 `D`/`R` 行**（删除的空目录不可被 git 跟踪，故不产生删除条目）。

### 3.2 三方 `check-ignore`

见 §2.3 代码块（新 docx 命中 `!` 放行行；旧 docx 命中 `*.docx`；`.bak_*` 命中 `*.bak*`；`.trae/` 命中 `.trae/`）。

### 3.3 docx 体积与 SHA-256

```text
docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx
  19,220,478 B
  9B3E15F56155FA4ABED5B5BF01A55FE22FF70DF7E063AD6B8C2180E844149245
```

> 与 `MASTER_TODO` §现状 #1 一致。

### 3.4 未触碰证明

| 区域 | 本轮动作 | 证明 |
|---|---|---|
| `experiments/**`（含 round12/round13 第三方改动） | 未改 | `git diff -- experiments` 为空（round12 的 `M`、round13 的 `??` 均为**并行流程**产生，非本轮） |
| `scripts/innovation_breadth_20260908/probe_breadth12.py` | 未改 | 未出现在 `git diff`；文件仍为并行产物 |
| `dist/` | 未改 | 连续 `*`/`binary` 规则不影响被忽略状态；未读写 |
| `methods/` | 未改 | gitignored；未读写 |
| `data/` | 未改 | `git diff -- data` 为空 |
| 论文源（`scripts/paper_complete_review_20260920/{manuscript.md,results.md,tables.json,figures.json,references.json}`）与图件数值 | 未改 | 未出现在 `git diff`；docx 未重建，SHA 不变 |

### 3.5 新增文本禁忌词自查

新增/修改文本（`CITATION.cff`、`.gitattributes`、`THIRD_PARTY_NOTICES.md`、本文件、README 新增行、`MASTER_TODO` 新增行、`GITHUB_METADATA` 新增行）= **0** 命中"老师/导师/教师/课堂/辅导/teacher/advisor/supervisor"。

> **例外报告（未改，非本轮范围）**：未跟踪的并行产物 `docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md` 含 **2 处"导师"**（第 21 行表格单元格 `需导师拍板`、第 120 行**非表格标题** `### T3 — 训练 / 新机制（需导师拍板；…）`）。该文件不在上一轮判定清单内、非本轮新增，按"其余处不动"**未改**；若该文件将入库，建议一并中性化（见第 4 节）。

---

## 4. 待作者决定项

| # | 事项 | 事实 / 选项 | 关联 |
|---|---|---|---|
| 1 | **现役 docx 是否留在 git，还是改走 Release** | 本轮已入库（`.gitignore:83` 白名单；`git status` 显示 `??`，体积 19.2 MB）。留 git＝克隆即得权威稿；移出＝需改白名单并改走 Release | E-20 |
| 2 | **是否启用 Git LFS** | tracked 3.31 GB、`.git` 6.62 GiB、3 个 `>50 MB` pptx。启用会改写历史对象、成本较高 | E-21 |
| 3 | **是否出 PDF** | 现役只有 docx；投稿/归档常需 PDF | E-22 |
| 4 | **是否打 `v1.0.0`** | 现 **10** 个 tag，最新 `reference-figures-20260920` 早于 09-23 扩版；扩版后无新 tag | E-23 |
| 5 | **`experiments/**` 与 `submission_repro_20260827/logs` 内本机绝对路径是否脱敏** | 二者属**红线/哈希登记**区：改动会使 `SHA256SUMS` / `VERSIONED_EVIDENCE.sha256` 失效（`git grep "My_github"` 现命中 1,503 个 tracked 文件） | E-24 / E-16 |
| 6 | **并行产物 `docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md` 的 2 处"导师"是否中性化** | 该文件**未跟踪**、非本轮新增；入库前若不处理，将成为公开仓库中的非中性表述 | 第 3.5 节 |

---

## 5. 未做 / 不确定

- **未提交 / 未推送**（按要求）：所有改动留在工作区。
- **未重建 docx / deck**：本轮只改元数据与文档，不触碰论文源与图件，故无必要重建。
- **体积为近似**：`git ls-files` 逐文件求和时，少量含 CJK 文件名的条目因 PowerShell `Test-Path` 限制被跳过（量级可忽略，四舍五入后与"3.31 GB"一致）。
- **禁忌词例外**：未跟踪并行产物 `docs/INNOVATION_DIRECTION_LIBRARY_20260922_CN.md` 的 2 处"导师"未改（见第 3.5 / 第 4 节）。
- **空目录历史提及**：被删路径在若干**历史文档**中按过去时被提及，未改写（历史记录不改）。
