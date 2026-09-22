# 公开仓库 `sci` 字符串审计与中性化 — 2026-09-22

> 目标：公开仓库（GitHub `USEU117/reference-matching-interaction-ad`）的内容与提交信息层面，**不再出现泄露项目身份或中文期刊层级的 `sci`**；合法技术词（`science` / `scientific` / `SciPy` / `scikit` / `ASCII` / 第三方库名、论文名、URL）**一律保留**。
> 范围：全仓（工作目录 `D:\STUDY\My_github\sci_project`；该物理目录同时以 junction 名 `D:\STUDY\My_github\reference-matching-interaction-ad` 可达），Windows / PowerShell。
> 基线：`HEAD = 36bd243`，`main [origin/main]`，`origin/main..HEAD = 0`、`HEAD..origin/main = 0`，历史共 180 个提交。所有路径与计数均为本轮盘上 / git 实读。
> **本轮未做**：git 提交、推送、GPU、实验、任何红线条目（`experiments/**` 证据字段、`data/**`、`LICENSE`、`requirements_repro.txt`、权威稿、版式母本、`figure_sources/**`）的修改。

---

## 0. 结论摘要

| 层 | 项 | 扫描（本轮起点） | 处置后 | 说明 |
|---|---|---|---|---|
| 路径层 | `git ls-files` 中含 `sci` 的路径 | **13 项**（3 项为身份泄露，10 项为 `scientific` 技术词） | 身份泄露项 **0**；`scientific` 10 项保留 | 3 项已 `git mv` 重命名 |
| 内容层 A（身份泄露） | `sci_project` / 旧绝对路径 | **1542 文件 / 82 179 处** | **1497 文件 / 81 942 处**（人工可读面已清零） | 残留全在红线区/冻结证据/生成物，逐条见 §6 |
| 内容层 B（中文期刊层级） | 独立词 `SCI` | **34 文件 / 67 处** | **3 文件 / 8 处** | 残留 3 文件均为**哈希登记**文档，按规则不改，见 §6.3 |
| 内容层 C（合法技术词） | `science*` 等 | 约 2000 文件量级（含 `scientific` 路径 10 项） | **全部保留** | 见 §5 |
| 提交信息层 | 含 `sci` 的提交 | **4 条**（其中 2 条含 `sci_project`） | 未动（历史层） | 见 §4；其中 1 条为**本地悬空提交、未公开** |
| 归档区 | `docs/archive_pre202609/**` | 4 文件 / 326 处 `sci_project` | **4 文件 / 326 处**（保留） | 全部是生成的图件溯源 JSON，见 §6.2 |
| lesson_notes | `docs/lesson_notes_*` | 路径 1 项 + 内容 `SCI` 14 处 + `sci_project` 6 处 | **路径 0 / `SCI` 0 / `sci_project` 0** | 已全部中性化 |

**核心判断**：`sci_project` 的暴露面实质上由**冻结证据与生成物**构成（`experiments/**` 79 134 处、`scripts/**` 1 137 处、`docs/**` 生成 JSON 1 375 处、`submission_repro_20260827/**` 等）。这些是**逐字节冻结的复现证据**（多数被 SHA-256 清单登记），按硬约束与"判定不确定即保留"原则**未改**；能安全改的**人工撰写面（.md / 顶层 .py）已全部清零**。

---

## 1. 方法与红线

### 1.1 扫描口径

| 项 | 命令（可直接复跑） |
|---|---|
| 路径 | `git ls-files` + 过滤 `(?i)sci` |
| 内容（宽） | `git grep -n -i -I "sci"`（**注意**：裸 `-i sci` 会把 `science`/`scientific`/`descriptive`/`discipline`/`ASCII` 等一并命中，不可直接当暴露面） |
| 内容（A） | `git grep -n -i -I "sci_project"`、`git grep -n -i -I "sci-project"` |
| 内容（B） | `git grep -n -I -w "SCI"`（独立词，大小写敏感） |
| 提交 | `git log --all --grep="sci" -i --format="%H|%h|%s"` |
| 哈希登记 | `git ls-files | Select-String "sha256|SHA256SUMS|VERSIONED_EVIDENCE"` |

### 1.2 本轮红线（全部未触碰）

`experiments/**` 已发布产物的 csv/json/npz 汇总与逐图证据、`data/**`（含 `data/splits/*/manifest.json`）、`LICENSE`、`requirements_repro.txt`、权威稿 `docs/paper_complete_teacher_review_20260920/Reference_Matching_Complete_English_20260920.docx`、版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx`、`scripts/paper_complete_teacher_review_20260920/figure_sources/**`。

**且**：任何**被哈希清单登记且当前哈希仍然匹配**的文件，不改（见 §6.3）。

### 1.3 验证（硬约束）

| 校验项 | 要求 | 实测 |
|---|---|---|
| `baseline_common_region.csv` | 保持 `3C83AB00…` | `3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB` ✅ 未变 |
| 实验数值 | 不改 | `experiments/**` 本轮**零改动**（见 §8 说明） |
| git 提交/推送 | 不做 | `git status` 仅工作区改动，未 commit / 未 push ✅ |

---

## 2. 路径层：`git ls-files` 中含 `sci` 的项

**复核结果：13 项**（任务提示"已知 3 个"，另发现 10 项为合法技术词 `scientific`，且分别在 `docs/` 与 `experiments/summaries/` 两处）。

| # | 路径 | 类别 | 处置 |
|---|---|---|---|
| 1 | `docs/lesson_notes_20260905/20260905_SCI论文辅导详细整理与修改清单.md` | **A（身份/中文层级）** | **已改名** → `20260905_论文辅导详细整理与修改清单.md` |
| 2 | `scripts/audit_english_sci_manuscript.py` | **A（身份）** | **已改名** → `scripts/audit_english_manuscript.py` |
| 3 | `scripts/build_english_sci_manuscript_docx.py` | **A（身份）** | **已改名** → `scripts/build_english_manuscript_docx.py` |
| 4 | `docs/archive_pre202609/dynamic_fusion_scientific_analysis_20260809.md` | C（`scientific`） | 保留 |
| 5 | `experiments/summaries/dynamic_fusion_scientific_analysis_20260809/README.md` | C | 保留 |
| 6–12 | `experiments/summaries/dynamic_fusion_scientific_analysis_20260809/{ablation_summary,category_diagnostics,input_provenance_sha256,provenance,route_statistics,run_comparison}.csv`、`summary.json`（共 7 项） | C | 保留 |

> 大小写 / 变体复核：`SCI`（大写）命中即上表 #1；`sci_project`、`sci-project` 在路径中**无残留**；`sci_project` 仅作为目录名出现在**内容**与**旧本地路径**里（§3）。中文文件名只此 1 项。

### 2.1 重命名清单（`git mv`，历史保留）

| 旧路径 | 新路径 |
|---|---|
| `docs/lesson_notes_20260905/20260905_SCI论文辅导详细整理与修改清单.md` | `docs/lesson_notes_20260905/20260905_论文辅导详细整理与修改清单.md` |
| `scripts/audit_english_sci_manuscript.py` | `scripts/audit_english_manuscript.py` |
| `scripts/build_english_sci_manuscript_docx.py` | `scripts/build_english_manuscript_docx.py` |

### 2.2 重命名后的引用修复

| 检查 | 结果 |
|---|---|
| `git grep "audit_english_sci_manuscript"` | **0 处**（该脚本无任何引用，脚本内也无自引用） |
| `git grep "build_english_sci_manuscript_docx"` | **0 处**（同上；脚本内引用的是产物名，不是自身文件名） |
| `git grep "20260905_SCI"` | **0 处**（原 4 处引用已全部随批量替换改为 `20260905_论文辅导详细整理与修改清单.md`） |

**被修复的 4 处引用**（文件:行）：

| 文件:行 | 改前 | 改后 |
|---|---|---|
| `docs/figures_revision_20260905/图件内容整理_放置方案与英文图注.md:205` | `` `docs/lesson_notes_20260905/20260905_SCI论文辅导详细整理与修改清单.md` `` | `` `docs/lesson_notes_20260905/20260905_论文辅导详细整理与修改清单.md` `` |
| `docs/manuscript_review_20260906/01_按老师要求逐项审核与修改说明.md:12` | `(D:/STUDY/My_github/sci_project/docs/lesson_notes_20260905/20260905_SCI论文辅导…md)` | `(<repo-root>/docs/lesson_notes_20260905/20260905_论文辅导…md)` |
| `docs/manuscript_review_20260906/02_第二轮核查与遗留问题清单.md:12` | `docs/lesson_notes_20260905/20260905_SCI论文辅导…md` | `docs/lesson_notes_20260905/20260905_论文辅导…md` |
| `docs/manuscript_revision_20260905/00_两次课程要求汇总与论文生成计划.md:25` | `(D:/STUDY/My_github/sci_project/docs/lesson_notes_20260905/20260905_SCI论文辅导…md)` | `(<repo-root>/docs/lesson_notes_20260905/20260905_论文辅导…md)` |

> 无任何被改名的路径出现在哈希清单中；`ARTIFACT_INDEX.md` / `FIGURE_BINDING.md` / `VALIDATION_*` 三处**均未登记这 3 个路径**，故重命名不触发"哈希登记则不改"规则。

---

## 3. 内容层：`sci` 出现的逐处分类

### 3.1 A 类（身份泄露）——扫描起点

| 形态 | 文件数 | 处数 |
|---|---:|---:|
| `sci_project`（含 `D:\STUDY\My_github\sci_project` 等绝对路径、`USEU117/sci_project` 等 URL 片段、`<...>/sci_project/` 目录名） | **1542** | **82 179** |
| `sci-project` | 0 | 0 |
| `SCI 项目` / `SCI Project` | 1（`scripts/build_concise_project_overview_docx.py:210` 的 docx 作者字段） | 1 |

按顶层目录分布（起点）：

| 顶层 | 文件数 | 处数 | 性质 |
|---|---:|---:|---|
| `experiments/` | 1381 | 79 134 | 冻结实验证据（provenance/manifest/汇总 JSON、逐图 JSON） |
| `scripts/` | 69 | 1 137 | 夜跑日志 `.err`、`VALIDATION_*.json`、硬编码绝对路径的 `.py`/`.ps1` |
| `docs/` | 63 | 1 610 | 人工撰写 `.md` + 生成图件 JSON |
| `submission_repro_20260827/` | 20 | 281 | 复现日志 + `pip freeze`（哈希登记） |
| `data/` | 4 | 4 | `data/splits/*/manifest.json` 的 `root` 字段（**红线 + 哈希登记**） |
| `methods/` | 2 | 2 | vendored 上游 `SOURCE.json` 的 `destination` 字段 |
| 根 / `tools/` | 2 | 10 | `README.md`、`build_progress_report.py`、`tools/rename_folder_*.ps1` |

### 3.2 B 类（中文期刊层级 / 投稿描述）——扫描起点

**34 文件 / 67 处**（`git grep -I -w "SCI"`）。典型形态：

`SCI 四区`、`中科院 SCI 四区`、`中科院升级版 SCI 四区`、`SCI 三区`、`SCI 期刊`、`SCI 四区期刊`、`SCI 论文`、`SCI 投稿`、`SCI 初稿`、`SCI 风格`、`SCI 论文辅导`、`SCI-I`、`English SCI-style`、`For an applied SCI journal`、`不含 "SCI"`、`不得写 SCI`、`去 "SCI" 命名`、`SCI Project`、`D:\保研\SCI\…docx`。

### 3.3 C 类（必须保留）——统计

| 形态 | 说明 | 处置 |
|---|---|---|
| `scientific` / `science` | 如 `dynamic_fusion_scientific_analysis_20260809`（路径 10 项 + 内容多处）、"英文 SCI 风格稿"语义外的普通用法 | 保留 |
| `SciPy` / `scipy` / `scikit-learn` | 依赖与第三方库名 | 保留（未出现在被改文件中） |
| `ASCII` | 编码说明（如 `.ps1` 纯 ASCII 约定） | 保留 |
| 第三方库名 / 论文名 / URL（AnomalyDINO、WinCLIP、PatchCore、`github.com/dammsi/…` 等） | 上游标识 | 保留 |
| **误命中示范（非 C 类词，但同样不改）** | `discipline` 含 `s c i`；`desc`/`descriptor` 并不含 `sci`（任务举例中的澄清） | 保留 |

> 判定不确定的一律**保留并在此登记**：本轮**未对** `science`/`scientific`/`SciPy`/`ASCII` 做任何替换。

---

## 4. 提交信息层（**本轮不动**）

### 4.1 清单（`git log --all --grep="sci" -i`，共 4 条）

| # | SHA | 日期 | 主题 | `sci` 命中位置 | 类别 | 是否公开 |
|---|---|---|---|---|---|---|
| 1 | `1b360bf808e982d9dfc434231590963ee1689fba` | 2026-09-21 | `rename to reference-matching-interaction: public README, GitHub metadata, and the folder swap` | **正文首段**：`The name sci_project says nothing about the work, so the repository becomes …` | **A（含 `sci_project`）** | **是**（`origin/main` 祖先） |
| 2 | `cfcaca10a92069aab274a045c9578f2c49aac0ae` | 2026-09-21 | 同上（主题**逐字相同**） | 同 #1 | **A（含 `sci_project`）** | **否** — 见 4.3 |
| 3 | `93c7292ec6075beda71cbe311b3cdc5e4d15cf0b` | 2026-09-05 | `docs: SCI paper coaching notes 2026-09-05 (detailed revision list)` | **主题**含 `SCI`；**正文**含 `20260905_SCI论文辅导详细整理与修改清单` | B | 是（`origin/main` 祖先） |
| 4 | `76ed697f9e1379dcfb9cafe82b465067b3ca2d18` | 2026-09-02 | `docs: add CASF category-conditional algorithm & experiment plan (task book 15)` | **误命中**：仅 `discipline` 一词含 `sci`，无真实暴露 | C（误命中，无需处理） | 是 |

复核结论与任务提示一致：**4 条含 `sci`、其中 2 条含 `sci_project`**（#1 公开、#2 本地）。

### 4.2 若要在提交信息层清除：需要重写历史 + 强制推送（**属需作者明确授权的操作**）

- **影响**：`git filter-repo` / `filter-branch` 会**改写 `1b360bf` 及其之后所有提交的 SHA**（即 `main` 上约数十个提交全部换 SHA），所有人的既有克隆都会分叉；必须 `git push --force`（对 `main` 属危险操作），并通知任何已克隆者重新 clone。若该仓库曾被打过 tag / 被引用（如论文中的 commit 号、Zenodo 归档），都要同步更新。
- **本轮不执行、不推送。**

### 4.3 推荐做法（仅方案，未执行）

≥ 3 步操作，**只在作者书面授权后**进行；建议先 `git clone --mirror` 备份。

```bash
# 方案 A：git-filter-repo（推荐，需另装）
git clone --mirror https://github.com/USEU117/reference-matching-interaction-ad.git repo.git
cd repo.git
# 仅改提交信息：把正文里的旧目录名替换为中性说法
git filter-repo --message-callback '
    return message.replace(b"sci_project", b"the old repository name")
                  .replace(b"SCI paper coaching notes", b"paper coaching notes")
'

# 方案 B：git filter-branch（无 filter-repo 时）
git filter-branch --force --msg-filter '
    sed -e "s/sci_project/the old repository name/g" \
        -e "s/SCI paper coaching/presubmission coaching/g"
' -- --all

# 之后（作者确认后才做）
git push --force origin main --tags     # ⚠ 改写已公开历史
```

> 补充：提交 #2（`cfcaca1`）**不是任何分支/标签的祖先**，只存在于本地 reflog（`refs/heads/main@{14}`），即改写前被 amend/重建过一次的旧对象。它**当前不在远端**，最终会被 `git gc` 回收；**无需**为它做历史重写。（若想立即确认：`git merge-base --is-ancestor cfcaca1 HEAD` 返回 1。）

---

## 5. 归档区与 `lesson_notes` 单独统计

| 区域 | 起点 `sci_project` | 处置后 | `-w SCI` 起点 → 后 | 说明 |
|---|---|---|---|---|
| `docs/archive_pre202609/**` | 4 文件 / 326 处 | **4 文件 / 326 处（保留）** | 4 处 → **0** | 4 文件全是生成的 `fig7_multimethod_*.json`（图件溯源记录），见 §6.2；`.md` 类归档文档中的 `SCI` 与旧绝对路径**已中性化** |
| `docs/lesson_notes_20260905/**` | 1 文件 / 1 处 | **0** | 2 处 → **0** | 含 1 项路径重命名 |
| `docs/lesson_notes_20260912/**` | 4 文件 / 6 处 | **0** | 14 处 → **0** | 逐字稿/课堂清单中的 `SCI 论文辅导`、`不得写 SCI`、`去 "SCI"` 等已中性化 |

---

## 6. 已执行修改与复扫残留

### 6.1 A 类：已改内容

**合计：72 个文件内容被改动**（脚本批量 70 文件 / 290 处 + 手工 2 文件 / 9 处）；另有 **3 项 `git mv` 重命名**（其中 2 项同时改了内容：`20260905_论文辅导….md`、`scripts/build_english_manuscript_docx.py`，第 3 项 `scripts/audit_english_manuscript.py` 仅改名）。替换后落盘占位符：`<repo-root>` **205 处**、`<旧仓库名>` **16 处**、`<旧物理目录名>` / `<local-docs>` 各 1 处。

**替换映射（可直接复用的口径）**

| 改前 | 改后 | 适用面 |
|---|---|---|
| `D:\STUDY\My_github\sci_project`、`D:/…`、`d:\…`、`d:/…` | `<repo-root>` | 全部人工可读文档 |
| `<...>/sci_project/`（目录名） | `<repo-root>/` | 目录树示例 |
| `USEU117/sci_project`、`github.com/USEU117/sci_project`（**历史语境**：旧地址/旧仓库名） | `USEU117/<旧仓库名>`、`github.com/USEU117/<旧仓库名>` | 课堂记录、审计记录 |
| `github.com/USEU117/sci_project`（**正文语境**：代码可用性地址） | `github.com/USEU117/reference-matching-interaction-ad` | 各轮 `English_content.md` / `中文对照内容.md` 的 "Code is available at …" |
| `sci_project`（散见叙述） | `<旧仓库名>` / `<旧物理目录名>` | 其余 |

**代表性「文件:行 → 改前 → 改后」（每类 3 例；全量可用 §9 命令导出）**

| 文件:行 | 改前 | 改后 |
|---|---|---|
| `README.md:3` | `…; the previous sci_project URL redirects to it.` | `…; the previous repository address redirects to it.` |
| `docs/AI_HANDOFF_VALIDATION_AND_INNOVATION_20260911_CN.md:3` | ``版本：1.0｜编写日期：2026-09-11｜项目：`D:\STUDY\My_github\sci_project` `` | ``…｜项目：`<repo-root>` `` |
| `docs/AI_HANDOFF_VALIDATION_AND_INNOVATION_20260911_CN.md:395` | `Set-Location -LiteralPath 'D:\STUDY\My_github\sci_project'` | `Set-Location -LiteralPath '<repo-root>'` |
| `docs/figures_reference_matching_20260914/FIGURE_BINDING.md:47` | `[…docx](docs/manuscript_reference_matching_20260914/…)` | `[…docx](docs/manuscript_reference_matching_20260914/…)`（**占位符化，链接不再可点**，见 §8.4） |
| `docs/lesson_notes_20260912/DCFnet_课堂修改要求与执行清单_20260912_审核定稿版.md:35` | ``…但地址仍是 `github.com/USEU117/sci_project`；`` | ``…但地址仍是 `github.com/USEU117/<旧仓库名>`；`` |
| `docs/论文与图件问题汇总_仅复核_20260921.md:126` | `…但当前物理目录和origin仍使用sci_project；` | `…但当前物理目录和origin仍使用<旧仓库名>；` |
| `docs/manuscript_review_20260906/English_content.md:5` | `Code is available at https://github.com/USEU117/sci_project.` | `Code is available at https://github.com/USEU117/reference-matching-interaction-ad.` |
| `scripts/build_concise_project_overview_docx.py:210` | `doc.core_properties.author = "SCI Project"` | `doc.core_properties.author = "Reference Matching Interaction"` |
| `build_progress_report.py:239` | `("项目目录", r"D:\STUDY\My_github\sci_project")` | `("项目目录", r"<repo-root>")` |
| `docs/GITHUB_METADATA.md:5` | ``…远端仓库 `USEU117/sci_project` → **`USEU117/reference-matching-interaction-ad`**（…`` | ``…远端仓库已改名为 **`USEU117/reference-matching-interaction-ad`**（…`` |
| `docs/PROJECT_CLEANUP_AUDIT_20260922.md:3` | ``> 范围：全仓（`D:\STUDY\My_github\sci_project`）…`` | ``> 范围：全仓（`<repo-root>`）…`` |

### 6.2 复扫残留（A 类）：**非 0，全部在红线区 / 冻结证据 / 生成物**

`git grep -l -i -I "sci_project"` = **1497 文件 / 81 942 处**。逐类如下（每类给文件数与处数）：

| 区 | 文件数 | 处数 | 保留理由 | 是否可改（需授权） |
|---|---:|---:|---|---|
| `experiments/**` | 1381 | 79 134 | **红线**：已发布产物的证据字段（`provenance.csv`、`input_manifest.json`、`*_audit*.json`、逐图 JSON 的 `source` 绝对路径）。改一处即与冻结断言/哈希不符；项目自身在提交 `1b360bf` 里已明确采用"junction 保路径"而非改文件 | 否（除非重跑并接受证据漂移） |
| `scripts/**`（34 `.err` / 15 `.py` / 7 `.json` / 6 `.ps1` / 3 `.txt` / 2 `.md` / 1 `.mjs` / 1 `.pregatefix`） | 69 | 1 137 | ① `.err`/`.txt`/`.pregatefix` = 夜跑日志；② `VALIDATION_20260918.json`、`FAST_ESTIMATOR_PARITY.json` 等为**验收证据**；③ `.py`/`.ps1` 中的绝对路径是**可执行依赖**（改成占位符即脚本不可运行；且物理目录当前就叫该名）；④ `.mjs` 属 `figure_sources/**` 免改区 | 部分可（需作者决定是否改脚本为自定位路径） |
| `docs/**`（生成物） | 20 | 1 375 | ① `fig7_multimethod_{btad,mpdd,mvtec,visa}_s0_k4.json` ×4 处副本 = 16 文件（由 `build_fig7_multimethod_samples.py` 生成的**来源溯源记录**，含路径/mtime/字节数）；② `FIGURE_SLIDE_INDEX.json`、`figures/primary_sources.json`（`build_deck.mjs` 生成）；③ `English_Manuscript_Source.md`（`build.py:265` 生成的**正文产物**，官方明示"不要直接编辑，会被下次构建覆盖"） | 否（手改会与生成器失配） |
| `submission_repro_20260827/**` | 20 | 281 | `SHA256SUMS` **逐条登记**了 `environment/*pip_freeze.txt` 与 `logs/*.log` 的 SHA-256（如 `logs/clip_s0_k1_full.log` = `f9f2f92f…`）。改动即让已发布的复现包校验失败 | 否 |
| `data/splits/*/manifest.json` | 4 | 4 | **红线**（`data/**`）**且**被 `manifest.sha256` / `archive.sha256` 登记哈希 | 否 |
| `methods/{anomalydino,univad}_official/SOURCE.json` | 2 | 2 | vendored 上游来源记录（`destination` 指向本地目录）；属**第三方来源溯源**，且 `methods/` 整体被 `.gitignore` 排除、此二文件为 `-f` 强制加入 | 否（建议保留） |
| `tools/rename_folder_to_reference_matching_interaction.ps1` | 1 | 9 | **功能依赖**：该脚本的唯一作用就是把物理目录从旧名改到新名，参数默认值 `-OldName 'sci_project'`、回滚说明等都**必须**写出旧名，否则脚本失效。删除该脚本同样是"移除功能"而非"移除文字" | 需作者决定（可整脚本删除，若确认本地改名已完成） |

> **结论**：A 类残留 = 0 **仅**在"人工撰写面（`.md` / 顶层 `.py` / 仓库根说明文档）"成立；`experiments/**`+`data/**`+哈希登记+生成物构成的 1477 文件属**结构性冻结面**，已逐条给出不可改理由。

### 6.3 B 类：已改内容与保留项

**已改：31 个文件 / 59 处**（67 → 8）。映射表：

| 改前 | 改后 | 改前 | 改后 |
|---|---|---|---|
| `中科院升级版 SCI 四区` | `中科院目标分区（应用/实证型）` | `SCI 论文辅导` | `论文辅导` |
| `中科院 SCI 四区` | `中科院目标分区（应用/实证型）` | `SCI 论文` | `论文` |
| `SCI 中科院四区` | `应用/实证型分区` | `SCI 初稿` | `英文初稿` |
| `SCI 四区期刊` | `应用/实证型期刊` | `SCI 稿` | `英文稿` |
| `SCI 四区论文` | `应用/实证型论文` | `SCI 风格` | `学术风格` |
| `SCI 四区投稿` | `应用/实证型投稿` | `English SCI-style` | `English academic-style` |
| `SCI 四区选刊` | `应用/实证型选刊` | `English SCI Draft` | `English Draft` |
| `SCI 四区候选期刊` | `应用/实证型候选期刊` | `applied SCI journal` | `applied journal` |
| `SCI 四区` / `SCI 三区` | `应用/实证型分区` | `SCI-I` | `目标期刊` |
| `SCI 期刊` | `目标期刊` | `不含 "SCI"` / `不得写 SCI` | 不含/不得写**期刊层级字样** |
| `SCI 投稿` | `投稿` | `去 "SCI" 命名` / `SCI 命名` | 去/…**期刊层级字样**命名 |
| `SCI Paper Writing Preparation Hub` | `Paper Writing Preparation Hub` | `SCI Project` | `Reference Matching Interaction` |
| `D:\保研\SCI\…docx`（输出路径） | `<local-docs>\…docx` | | |

**保留项（8 处 / 3 文件）——理由逐条**

| 文件 | 处数 | 保留理由 |
|---|---:|---|
| `docs/PAPER_SUBMISSION_HANDOFF_AND_REPRODUCIBILITY_PLAN_20260826.md` | 6 | 被 `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256` **登记且哈希当前匹配**（实测 `1a05569f…` 一致）⇒ 按"哈希登记不改"规则保留，改为上报 |
| `docs/PROJECT_PROGRESS_AND_MANUSCRIPT_PLAN_FOR_SUPERVISOR_EN_20260827.md` | 1 | 同上，哈希匹配（`e239d3de…`） |
| `docs/submission_reproducibility_20260826/README.md` | 1 | 同上，哈希匹配（`bb1786f3…`） |

（同批另 1 处 `docs/AI_HANDOFF_REPRESENTATION_MATCHING_INTERACTION_AND_ACCEPTANCE_20260914_CN.md` 的 `SCI录用保证` 已改为"录用保证"，不在残留内。）

**附带发现**（同批更新的 3 个文档，其登记哈希**早已过期**，故可安全改写）：`README.md`（登记 `52b3206d…` ≠ 实读 `af10be…`）、`docs/CURRENT_DYNAMIC_FUSION_STATUS.md`、`docs/PAPER_DETAILED_CHINESE_DRAFT_20260827.md`。

---

## 7. 未做 / 不确定

| # | 项 | 原因 |
|---|---|---|
| 1 | `tools/rename_folder_to_reference_matching_interaction.ps1` 的 9 处旧目录名 | **功能依赖**——去掉旧名脚本即失效。若作者确认本地物理改名已完成、该脚本可废弃，**删除整个脚本**比改写它更干净（建议单独一轮处理） |
| 2 | `scripts/**` 15 个 `.py` + 6 个 `.ps1` 中硬编码的绝对路径 | 改成占位符会让脚本不可执行；改为 `Path(__file__).resolve().parents[n]` 属**代码行为变更**，超出"字符串中性化"范围 ⇒ 保留 + 上报 |
| 3 | `experiments/**`（79 134 处）、`data/splits/**`（4 处）、`submission_repro_20260827/**`（281 处） | 红线 + 冻结哈希 + 复现证据；项目既有决定（junction 方案）即"不改文件" |
| 4 | `docs/**` 20 个生成 JSON/MD 与 `FIGURE_SLIDE_INDEX.json` | 生成物，手改会与生成器失配。**副作用提示**：本轮把 `FIGURE_BINDING.md` 的 `file:///d:/…` 绝对链接改成了占位符 `…`，**链接不再可点**（读者需自行替换）；如不希望如此，建议把该文件的这类链接整体改为**仓库相对路径**（如 `docs/…`），属独立小改动，本轮未做 |
| 5 | 课堂逐字稿中的**原话引用** `"那个项目名字不能写 S ci project……"` | 是老师原话的逐字记录（含空格，非 `sci_project` 形态）且为本次清理的**依据本身**；按"历史记录不改"保留，并在同段落保留"去期刊层级字样命名"的处置说明 |
| 6 | 提交信息层（4.2 / 4.3） | **需作者明确授权**才能重写历史 + 强制推送；本轮只出清单与方案 |
| 7 | 未跟踪文件 `docs/manuscript_reference_matching_20260914/论文总览_基础理解_20260917.md`、`.trae/**` | 未被 git 跟踪 ⇒ 当前不会随仓库公开；实测前者**不含** `sci`。（`.trae/` 内容未逐字核） |
| 8 | `sci` 的**全文宽松扫描**（`git grep -i sci`，80 982 行 / 2005 文件） | 绝大多数是 `science`/`scientific`/`descriptive`/`discipline` 等技术词，无法作为暴露面判据；本轮改用 `sci_project` + 独立词 `SCI` 两个可判定口径，**未**逐一审阅宽松命中 |

---

## 8. 交付状态

| 项 | 状态 |
|---|---|
| 本报告 | `docs/SCI_STRING_AUDIT_20260922.md`（新增） |
| 工作区改动 | `git status` = **75 条**：`M` 70、`RM` 2（改名+改写）、`R` 1（纯改名）；另有 2 条**既有**未跟踪项（`.trae/`、`docs/manuscript_reference_matching_20260914/论文总览_基础理解_20260917.md`） |
| 提交 / 推送 | **未做**（按任务要求） |
| 临时脚本 | 已写入 `/.tmp_sci_neutralize/` 并在用后**全部删除**（该目录被 `.gitignore` 的 `/.tmp_*/` 覆盖） |
| 建议提交信息 | `neutralise the project-identity and journal-tier sci strings outside the frozen evidence` |

### 附：本章所有扫描 / 复扫的可复现命令

```powershell
# 路径层
git ls-files | Where-Object { $_ -match '(?i)sci' }

# A 类残留（按顶层聚合）
git grep -l -i -I "sci_project" -- . | ForEach-Object { ($_ -split '/')[0] } | Group-Object | Sort-Object Count -Descending

# A 类明细（逐处，可导出为本报告的明细附录）
git grep -n -i -I "sci_project" -- . | Where-Object { $_ -notmatch 'My_github' } | Where-Object { $_ -notmatch '^experiments/' }

# B 类残留
git grep -n -I -w "SCI" -- .

# 重命名引用是否清干净（三条都应为空）
git grep -n -I "audit_english_sci_manuscript"   -- .
git grep -n -I "build_english_sci_manuscript_docx" -- .
git grep -n -I "20260905_SCI" -- .

# C 类（举例：合法技术词）
git grep -l -I -w "SciPy" -- .

# 提交信息层
git log --all --grep="sci" -i --format="%H|%h|%s"
git merge-base --is-ancestor cfcaca1 HEAD   # 返回 1 ⇒ 该提交未公开（仅本地 reflog）

# 硬约束校验
(Get-FileHash "experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv" -Algorithm SHA256).Hash
# 期望 3C83AB004420A4F836102CABC5F8248DEBFEBC742D8E9602FED0881823A0B8BB
```
