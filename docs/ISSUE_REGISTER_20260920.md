# 投稿前问题归档（Issue Register）

- 日期：2026-09-20（Asia/Shanghai）
- 范围：外部只读审计结论的逐条归档；证据均为本次在盘上实读所得（命令 / 文件 / 实测值），未验证的显式标注。
- 仓库：`<repo-root>`；证据采集时的 HEAD `841b478`（annotated tag `final-20260920` 的 peeled commit 即此提交）。
- 约定：**本文档只登记问题**；处置动作与验收标准见 `docs/REMEDIATION_PLAN_20260920.md`。

## 〇、审计认定"已真正补齐"的事实（本登记不列为问题，仅作为基线）

| 项 | 实测证据 |
|---|---|
| correspondence 改为正确的配对图像 bootstrap | `experiments/dynamic_fusion/paper_evidence_closeout_20260914/CLAIM_EVIDENCE_LEDGER.csv` C16 行：MPDD 主口径 `14/14 全部排除零`，最弱格 OT ε=0.05 的 I_BAL 下界 `+0.000063`；BTAD `14/14 仍跨零` |
| 夜间总验收重跑仍 36/36 | `scripts/limitation_closure_20260915/_night2_20260918/ACCEPTANCE_20260920.md` 第 11 行：`verdict=pass phases=8 checks=36`（exit 0） |
| 权威稿规模 | 同上第 18 行：tables 18 / figures 8 / equations 12 / refs 34（34 键映射，含 `ksdd2:34`） |
| 本地复现包 | `dist/replication_package_20260920/`：实测 **1316 文件 / 413.5 MiB**（`Get-ChildItem -Recurse -File \| Measure-Object Length -Sum`） |

---

## 〇bis、处置后状态（2026-09-20 刷新；下文各条原文不改写）

| ID | 刷新后状态 | 凭据（实读/实测） |
|---|---|---|
| R-05 | **已处置** | 仓库根新增 `pytest.ini`（`testpaths = tests`；`addopts = --ignore=tests/innovation_v6_dgsafe/test_wave2a_probes.py`），`pytest tests -q` 与裸 `pytest` 均 **260 passed / 0 failed / 0 errors**；原因定位为 **PEP 420 命名空间包遮蔽**（vendored `methods/SubspaceAD/src/subspacead` **存在**），非依赖缺失。详见 `tests/README.md` |
| R-06 | **已处置** | `docs/CURRENT_DYNAMIC_FUSION_STATUS.md`、`docs/paper_writing_preparation_20260830/{README.md, 11_RCEC_…_20260901.md}` 中的 `141/141` 已就地标注为 **2026-09-02 历史快照**并给出当前实测；`docs/project_review_20260910/repro_audit.md` 与 `docs/PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md` 各加一句"后续状态（2026-09-20 追注）"指针，不改写原审计事实 |
| R-07（措辞部分） | **已处置** | 正文与台账的 `true null` / `true zero effect` / `essentially zero on BTAD` 均已清零（`scripts/manuscript_build_20260914/{manuscript.md,results.md}`、`…/paper_evidence_closeout_20260914/CLAIM_EVIDENCE_LEDGER.csv` C13 行、`docs/HANDOVER_20260919.md`、`docs/manuscript_reference_matching_20260914/中文对照内容.md`），统一为"点估计接近零、区间跨零，当前数据不足以确定交互方向"；docx 已重出。**科研判断部分仍归作者**（是否接受该统一口径，见 `REMEDIATION_PLAN_20260920.md` 需作者信息第 10 项） |
| R-08 | **已处置** | `ACCEPTANCE_20260920.md` 第 12 行改为 `checks=71, passed=71, failed=[]`，与 `SELFCHECK.json` 逐字一致；并标注最后刷新时间 |
| R-09 | **已处置** | `docs/ARTIFACT_INDEX.md` 工作流 B 状态行改为"完成（主口径 14/14 排除零、最弱格 +0.000063；BTAD 14/14 跨零、判定不变；表 18 已加）"，旧"OT 软混合下两条区间跨零"结论删除，保留"BTAD ε 网格未落逐单元诊断"这一真实瑕疵 |
| R-10 | **已处置** | 同上报告 §二.5 与 §三.1 改为"已完成"，凭据为 `CLAIM_EVIDENCE_LEDGER.csv` 第 17 行（C16）实读 |

> 说明：本登记与 `REMEDIATION_PLAN_20260920.md` 为**过程记录**，为便于指认，文内以引号/反引号引用 `true null`、`true zero effect`、`essentially zero` 等字符串；这些是**被指认对象**，不是断言。正文与台账（结论性文本）中已无这些写法。

---

## 〇ter、2026-09-22 状态刷新（只记状态变化，上文原文不改写）

| ID | 刷新后状态 | 凭据（实读 / 实测） |
|---|---|---|
| R-11（推送部分） | **已解决** | `git rev-list --count origin/main..HEAD` = **0**（HEAD `85d3207`，2026-09-22 复测；`de25a22` 为本节首次记录时的 HEAD）。R-11 余下仅"工作区有未提交改动"，按要求**不提交、不推送** |
| R-20 | **状态变化：外部方法家族 2 → 5；原限制条款不变** | 三个新增外部家族已按既定协议跑完并落表：`experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_ext_20260921/baseline_common_region_ext.csv`（1188 行 = 冻结 864 + 新 324，SHA-256 `1C770129…`），已入正文 **Table 12**（`scripts/paper_complete_review_20260920/tables.json` 的 `baselines_ext` 键）。现家族＝PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AnomalyCLIP 零样本。仍为**同机自测、不构成排名**，"禁止 `SOTA / 全面领先`"约束不变（见 `REMEDIATION_PLAN_20260920.md` 末节） |
| 权威稿规模（§〇 第 3 行所引数字） | **口径补充（数字并存，不互斥）** | §〇 第 3 行引用的 `ACCEPTANCE_20260920.md` 第 18 行的 **18 表 / 8 图**属**已冻结的旧链** `scripts/manuscript_build_20260914/`（`docs/manuscript_reference_matching_20260914/build_validation.json` 实读一致）；权威交付稿走 `scripts/paper_complete_review_20260920/` 链，2026-09-22 实测 **20 表 / 22 内嵌图 / 12 编号公式 / 34 文献 / 47 页 / 16,969 词**（docx SHA-256 `F3CAE3B491A99F8649E8900756D60C75163DDAA43B715F73D271308038DC44ED`） |
| 新发现（建议编号 R-22） | **已恢复，仍建议处置** | 权威 docx 与其版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` 在本轮开始时**不在盘上**（`a08dc46` 把 `*.docx` 加入 `.gitignore` 后从工作区消失），`build.py` 因此无法执行；已从 git 对象逐字节恢复并 SHA-256 校验一致（`18694B90…` / `9DB99E60…`）。母本是**不可由源重建的二进制输入**，建议移出忽略范围或保留受控副本并登记进 `ARTIFACT_INDEX.md`。详见 `docs/论文与图件问题汇总_仅复核_20260921.md` §八 的 **F17** |
| 图件侧 F01 / F02 / P04 / F14 | **已完成** | 见 `docs/论文与图件问题汇总_仅复核_20260921.md` §八"2026-09-22 轮次"：图 2(b) 紫框与填色对齐、图 3(b) 权重措辞更正（图内＋图注＋正文）、图 S4 的 ±5% 参考带与 6.8% 实测值分开表述（5% 判据下实测首个 N = 700）、58 页 PPT 已重出（SHA-256 `48DD9180…`，第 20/21 页＝收敛／稳定性） |
| R-11（推送部分）**二次状态变化** | **本地又超前 2 个提交** | 2026-09-23 实测 `git status -sb` = `## main...origin/main [ahead 2]`，`git rev-list --count origin/main..HEAD` = **2**、`HEAD..origin/main` = 0；本地 HEAD `4d7f640`（2026-09-23）。上表 09-22 记的 `= 0` 在当时成立（HEAD `85d3207`），其后两次提交（`e61d039`、`4d7f640`）**未推送**。按要求**不提交、不推送** |
| 权威稿词数 | **口径更新（47 页不变）** | 2026-09-23 Word COM 复测 **47 页 / 17,200 词**（字符 100,569）。09-22 记的 `16,969 词` 是命名温和版（Table 1/2 新增 `Full name` 列）**之前**的旧值；页数未变 |
| 自检门禁 | **不通过（2/69 项失败）** | 2026-09-23 复跑 `scripts/representation_matching_interaction_20260914/selfcheck.py`：`checks=69 / passed=67 / failed=["read-only inputs were not written during this delivery", "manuscript: the updated outline exists"]`，退出码 1。**（b）** `docs/paper_outline_review_20260914/新主题论文详细提纲_外部评审版_20260914_更新版.docx` 已不在盘（`0 bytes`；`dist/replication_package_20260920/docs/paper_outline_teacher_review_20260914/` 只剩空目录；git 对象中亦无该文件；重建源 `.tmp_outline_20260914/{build.py,artifact.md,render_native.py}` 在盘）。**（a）** 冻结快照 3 处漂移：`unified_fusion_paper_support_20260913/_smoke/units/mpdd_s0_k2/bracket_black/{evaluation_scores,patch_scores}.npz` **缺失**、`…/unified_fusion_paper_support_20260913/REPORT_CN.md` 仅 mtime 变化（size 10029→10029）；`READONLY_PROOF.json` 的 `verdict` 仍为 `no frozen read-only input was written`。⚠️ **该脚本会就地改写** `experiments/**/{SELFCHECK,READONLY_PROOF}.json`（本次运行后已用 `git checkout --` 逐字节还原为 HEAD 状态） |

---

## 一、问题总表

| ID | 标题 | 类别 | 严重度 | 处置归属 |
|---|---|---|---|---|
| R-01 | 复现包缺 `src/`、`methods/`、`configs/`，不能独立执行 | 复现包 | 阻断投稿 | 本次可自动解决 |
| R-02 | `requirements_repro.txt` 非 lock，且缺 CUDA wheel 安装源 | 复现包 | 影响可复现性 | 本次可自动解决 |
| R-03 | 缺权重获取方式与 SHA-256 | 复现包 / 数据完整性 | 影响可复现性 | 自动（登记）+ 作者（确认分发） |
| R-04 | 缺包级 `SHA256SUMS` 与 `SOURCE_COMMIT.txt` | 复现包 | 影响可复现性 | 本次可自动解决 |
| R-05 | `pytest tests -q` 在 collection 阶段失败（缺 `src.subspacead`） | 测试 | 阻断投稿 | 本次可自动解决 |
| R-06 | 文档中的"141/141 passed"不能作为当前 HEAD 结论 | 测试 / 措辞 | 影响表述准确性 | 本次可自动解决 |
| R-07 | BTAD 统计措辞不统一（`insufficient evidence` / `essentially zero` / `true null` / `true zero effect`） | 措辞 | 影响表述准确性 | 自动（正文）+ 作者（口径确认） |
| R-08 | 验收与自检新旧冲突：`SELFCHECK.json` 71/71 vs `ACCEPTANCE_20260920.md` 69/71 | 文档一致性 | 影响表述准确性 | 本次可自动解决 |
| R-09 | `ARTIFACT_INDEX.md` 工作流 B 行仍保留"OT 软混合跨零"旧结论 | 文档一致性 | 影响表述准确性 | 本次可自动解决 |
| R-10 | 验收报告称 C16 台账未更新，但台账已更新 | 文档一致性 | 仅整洁性 | 本次可自动解决 |
| R-11 | 未形成不可变发布点：本地 `main` 超前远端 15 提交；工作区仍有 3 个 tracked 文件被修改 | 版本与发布 | 阻断投稿 | 自动（可执行）+ 作者（是否推送） |
| R-12 | `dist/` 未跟踪且未被 `.gitignore` 覆盖 | 版本与发布 | 影响可复现性 | 本次可自动解决 |
| R-13 | 复现包缺 claim–evidence 台账与当前提交指针 | 复现包 | 影响可复现性 | 本次可自动解决 |
| R-14 | `VD1_MANIFEST.json` 的 `manifest_sha256` 为 `null` | 数据完整性 | 影响可复现性 | 本次可自动解决 |
| R-15 | 复现包未带 `seeds_extension_20260917/p0_support` 清单 | 复现包 | 影响可复现性 | 本次可自动解决 |
| R-16 | 投稿元数据缺失（作者 / 单位 / 资助 / COI / 伦理或不适用声明） | 投稿元数据 | 阻断投稿 | 需作者决定 |
| R-17 | 是否审稿阶段即公开代码（按期刊定） | 投稿元数据 | 阻断投稿 | 需作者决定 |
| R-18 | stride-1 / full-pixel 只有点估计、无区间 | 论文限制 | 不阻断（限制） | 需作者决定（保留为限制） |
| R-19 | 效率数据是部分阶段计时，非同步端到端 | 论文限制 | 不阻断（限制） | 需作者决定（保留为限制） |
| R-20 | 外部对比覆盖四数据集六配置，但仍只两个方法家族 | 论文限制 | 不阻断（限制） | 需作者决定（保留为限制） |
| R-21 | correspondence 只证明"零排除判定在各变体下保持"，不能证明变体间等效 | 论文限制 | 不阻断（限制） | 需作者决定（保留为限制） |

**类别分布（共 21 条）**：复现包 6（R-01/02/04/13/15，R-03 计入复现包与数据完整性各半按复现包计）→ 复现包 **6**、测试 2（R-05/06）、措辞 1（R-07）、文档一致性 3（R-08/09/10）、版本与发布 2（R-11/12）、数据完整性 1（R-14）、投稿元数据 2（R-16/17）、论文限制 4（R-18/19/20/21）。

---

## 二、逐条证据、影响与归属

### R-01 复现包缺源码与配置，不能独立执行
- **现状证据（实读）**：`dist/replication_package_20260920/` 根层仅 `data/ docs/ experiments/ scripts/ LICENSE README.md requirements_repro.txt`；`Glob dist/replication_package_20260920/{src,methods,configs,tests}/**` → **No file found**。而源码实际存在于 `src/industrial_ad/`（含 `fusion/`、`innovation_v2/`…），`methods/` 下有 vendored 代码（如 `methods/winclip/WinClip-master/…`），仓库根有 `configs/`（`dynamic_fusion.yaml` 等 18 个）。
- **交叉证据**：包内 `README.md` §3 明示 `data/*_raw/`、`outputs/`、`canonical/`、`units/` 因体积/许可排除，但**未列出** `src/`、`methods/`、`configs/`；而 §4 复现步骤要求"跑各工作流"，这些脚本 `import industrial_ad`，实现缺失。
- **影响**：新机器按包内文档走不到任何结果；复现性声明（论文"code availability"）不成立，审稿/读者会直接卡住。
- **归属**：本次可自动解决（打包补入 + 在包内 README 明确 `PYTHONPATH`/`pip install -e` 指引）。

### R-02 `requirements_repro.txt` 非 lock，缺 CUDA wheel 源
- **现状证据（实读）**：该文件第 3 行自述 `This is a reproduction list, NOT a lock file.`；第 29–30 行 `torch==2.0.0+cu118` / `torchvision==0.15.1+cu118`，但全文**无 `--index-url` / `--extra-index-url`**（无 `download.pytorch.org/whl/cu118` 行）；第 16–17 行给出的安装指令是 `pip install -r requirements_repro.txt`。
- **影响**：按文档安装时 `+cu118` 本地版本号在默认 PyPI 上不可解析，安装直接失败；即使装上，无 lock 也意味着无法保证与他人环境一致，冻结结果的可比性下降。
- **归属**：本次可自动解决（补 CUDA index 段 + 锁定可解析版本；是否改为真 lock 由作者决定）。

### R-03 缺权重获取方式与 SHA-256
- **现状证据（实读）**：`dist/replication_package_20260920/docs/sources.md` 第 27 行只写"所有资源下载后都应记录获取日期、URL、commit/checkpoint 名称与 SHA256"，**实际只录到 2 个 Source ZIP 的 SHA256**（第 9、12 行），AdaptCLIP 仅有 URL（第 19 行，`https://huggingface.co/csgaobb/AdaptCLIP`）而**无 SHA256**；`dist/docs/environment_matrix.md` 全文 grep `sha256|SHA-256|checkpoint|weights|权重` → **No matches**。
- **影响**：DINOv2 / AnomalyCLIP / AdaptCLIP / PatchCore 等权重的来源与校验不可核，评审无法确认所用的确切 checkpoint。
- **归属**：自动可补"来源 URL + 固定 revision + SHA256 清单"；权重的再分发许可需作者确认。
- 备注：`docs/REPRODUCIBILITY_PACKAGE.md` 第 111 行提到离线加载需 `HF_HUB_OFFLINE=1` / `HF_ENDPOINT` 及 vendored patch，属运行提示，**不是**权重校验记录。

### R-04 缺包级 `SHA256SUMS` 与 `SOURCE_COMMIT.txt`
- **现状证据（实读）**：在包内递归查找 `SHA256SUMS*` / `SOURCE_COMMIT.txt` → **均为 0 命中**。仓库内唯一相关文件是旧包 `submission_repro_20260827/SHA256SUMS`、`submission_repro_20260827/SOURCE_COMMIT.txt`，与本次 `dist/replication_package_20260920/` 无关。
- **影响**：无法校验包是否被改动，也无法把包绑定到某个提交，"不可变归档"不成立。
- **归属**：本次可自动解决（生成清单 + 写入提交指针）。

### R-05 `pytest tests -q` collection 阶段失败
- **现状证据（实测，仅运行一次）**：`.venv-anomalyclip\Scripts\python.exe -m pytest tests -q`（exit code **2**）：
  ```
  ERROR collecting tests/innovation_v6_dgsafe/test_wave2a_probes.py
  scripts\innovation_v6_dgsafe\run_wave2a_build_reliability.py:64:
      from src.subspacead.core.extractor import FeatureExtractor
  E   ModuleNotFoundError: No module named 'src.subspacead'
  ===== 1 warning, 1 error in 18.82s =====
  ```
  测试模块以 `spec.loader.exec_module` 载入 `scripts/innovation_v6_dgsafe/run_wave2a_build_reliability.py`，其中仍指向已不存在的旧包路径 `src.subspacead`（现为 `src/industrial_ad/`）。
- **影响**：整个 `tests` 目标在 collection 阶段中断，没有任何测试真正运行；审计提出的"测试状态不成立"成立。
- **归属**：本次可自动解决（修 import 或明确排除该模块；正式范围与 N passed 需实跑确认）。

### R-06 "141/141 passed" 表述失效
- **现状证据（实读）**：`docs/CURRENT_DYNAMIC_FUSION_STATUS.md` 第 159 行写"项目自有测试 `pytest tests -q` 为 **141/141 通过**"；同一字符串亦出现在 `docs/project_review_20260910/repro_audit.md`、`docs/paper_writing_preparation_20260830/README.md`、`docs/paper_writing_preparation_20260830/11_RCEC_INNOVATION_IMPLEMENTATION_AND_ACCEPTANCE_HANDOFF_CN_20260901.md`（另有 dist 内副本）。当前 HEAD 实测为 collection error（见 R-05）。
- **影响**：任何以该数字支撑"测试全绿"的表述对当前 HEAD 不成立，属可被审稿人直接复现打假的事实性错误。
- **归属**：本次可自动解决（加限定语 + 重跑并记录当前 HEAD 的真实通过数）。

### R-07 BTAD 统计措辞不统一
- **现状证据（实读，正文）**：`docs/manuscript_reference_matching_20260914/English_Manuscript_Source.md`
  - 第 5 行（摘要）：`BTAD provides insufficient evidence of interaction`，同段又有 `essentially zero on BTAD`；
  - 第 205 行：`An interval spanning zero is treated as insufficient evidence of a direction, not as statistical equivalence`（与本条最一致，可作统一口径）；
  - 第 339 行：`BTAD is a true null.`；
  - 第 400 行：`essentially zero on BTAD`。
- **同类措辞的全仓分布（实读计数）**：`true null` 命中 10 个文件（含正文、`CLAIM_EVIDENCE_LEDGER.csv`、`scripts/manuscript_build_20260914/results.md` 及 dist 副本）；`true zero effect` 命中 2 个文件（`docs/manuscript_updated_20260919/English_Manuscript_Source.md:253` 及 dist 副本）。
- **影响**：区间跨零 **≠** 证明零效应；"true null / true zero effect"是超出口径的强断言，与第 205 行自设纪律直接冲突，也易被读成"四数据集一致复制"。
- **归属**：措辞修订可自动执行；**是否把 BTAD 定位为"真零效应"的科研判断需作者确认**（登记为需作者口径确认）。

### R-08 验收与自检新旧冲突
- **现状证据（实读）**：
  - `experiments/dynamic_fusion/representation_matching_interaction_20260914/SELFCHECK.json`：`"checks": 71, "passed": 71, "failed": []`（该文件当前处于 modified 状态，即工作区版本为 71/71）。
  - `scripts/limitation_closure_20260915/_night2_20260918/ACCEPTANCE_20260920.md` 第 12 行仍写 `69/71 通过`，并称两条失败为"既有"。
- **影响**：同一时点两份权威记录对"自检是否全过"给出不同结论；若照抄进子说明，投稿材料自相矛盾。
- **归属**：本次可自动解决（更新验收报告或标注其为 tag 前快照）。

### R-09 `ARTIFACT_INDEX.md` 保留旧结论
- **现状证据（实读）**：`docs/ARTIFACT_INDEX.md` 第 18 行工作流 B 状态仍为"完成但有已知瑕疵（**OT 软混合下两条区间跨零**；BTAD ε 网格未落逐单元诊断）"。与 `CLAIM_EVIDENCE_LEDGER.csv` C16 行（主口径更新后 MPDD 14/14 排除零、最弱格下界 `+0.000063`）相反。
- **影响**：索引是接手与审稿的第一入口；旧结论会让读者认为主结论对 OT 变体不稳健。
- **归属**：本次可自动解决。

### R-10 验收报告对 C16 的描述已过期
- **现状证据（实读）**：`ACCEPTANCE_20260920.md` 第 28 行称 C16 行"仍写'零排除判定对软混合替换不稳健'及旧区间（该文件是实验产物台账，本轮按要求未改）。**建议下一轮单独修订该行**"；但实读 `CLAIM_EVIDENCE_LEDGER.csv` 第 17 行 C16 已是新口径（`14/14 全部排除零`、ε 网格逐格数值、最差格 `+0.000063`），并把"沿用旧口径（对 4 个条件点值取分位）的区间与'软混合跨零'结论"写进了**禁止用法**列。
- **影响**：仅造成接手者重复劳动与不必要的返工，不改变结论。
- **归属**：本次可自动解决。

### R-11 未形成不可变发布点
- **现状证据（实测）**：
  - `git rev-list --count origin/main..main` = **15**；`git log --oneline origin/main..main` 首行为 `841b478 close the four leftovers: …`（远端未含这 15 个提交）。
  - `git rev-parse HEAD` = `841b478b…`；`final-20260920` 是 annotated tag（`git rev-parse final-20260920` 返回 tag 对象 `c42856d…`，`git log -1 final-20260920` 解引用到 `841b478`，`rev-list --count` 两个方向均为 0）→ **tag 指向 HEAD**，但工作区与之不一致。
  - `git status --porcelain` 的 modified 项共 **3 个**：`README.md`、`experiments/dynamic_fusion/representation_matching_interaction_20260914/READONLY_PROOF.json`、`…/SELFCHECK.json`；`git diff --stat` = `3 files changed, 651 insertions(+), 175 deletions(-)`。
  - `git tag` 现有 8 个：`audit-closure-20260919, b-interval-fix, closure-round-2-20260919, final-20260920, handover-20260919, night-20260918, night-20260918-final, paper-materials-20260919`。
  - 注意：`ACCEPTANCE_20260920.md` 第 19 行记录当时 HEAD 为 `df51d7c`、且"17 项未提交全部是刻意不入库"，该描述已与当前 HEAD 不符。
- **影响**："发布点 = tag" 的声明不成立（工作区 ≠ tag 内容）；远端无这 15 个提交，任何外部读者拿不到对应代码。
- **归属**：整理与提交可自动执行；**是否 push 到远端属作者决定**（本次不提交、不推送）。

### R-12 `dist/` 未跟踪且无忽略规则
- **现状证据（实测）**：`git status --porcelain` 输出 `?? dist/`；`git check-ignore -v dist` 无输出（**未被忽略**）。包体积 1316 文件 / 413.5 MiB。
- **影响**：包体既不在版本控制内、也不在忽略清单里，任何一次 `git add .` 都可能把 413.5 MiB 二进制图件灌进历史；同时"包与提交对应"无从建立。
- **归属**：本次可自动解决（明确二者其一：纳入发布流程或写入 `.gitignore`；本登记不改文件）。

### R-13 复现包缺 claim–evidence 台账与提交指针
- **现状证据（实读）**：`dist/replication_package_20260920/experiments/dynamic_fusion/` 下只有 `confirmation_ksdd2_20260918/`、`generalization_mvtec_visa_20260915/`、`limitation_closure_20260915/`、`representation_matching_interaction_20260914/`、`seeds_extension_20260917/` 五个工作流目录，**不含** `paper_evidence_closeout_20260914/`（`CLAIM_EVIDENCE_LEDGER.csv` 所在）。包内 `README.md` §6 亦自述此缺口。提交指针缺失见 R-04。
- **影响**：正文每个数字到证据的映射链在包内断掉，复现者无法按 claim 逐条验证。
- **归属**：本次可自动解决。

### R-14 `VD1_MANIFEST.json` 的 `manifest_sha256` 为 `null`
- **现状证据（实读）**：`experiments/dynamic_fusion/seeds_extension_20260917/VD1_MANIFEST.json` 中 `datasets.mpdd.manifest_sha256` 与 `datasets.btad.manifest_sha256` 均为 `null`（对应 `manifest` 字段分别指向 `…\p0_support\support_manifest_mpdd.json` / `…_btad.json`）。脚本侧成因已定位：`scripts/limitation_closure_20260915/d1_verify_manifest.py:109` 的 `"manifest_sha256": manifest.get("sha256") or None` —— 清单 JSON 内无顶层 `sha256` 键即落 `null`。
- **补充证据**：`Glob experiments/dynamic_fusion/seeds_extension_20260917/p0_support/*` → 两个 `support_manifest_{mpdd,btad}.json` **存在**（即文件在，只是哈希未落值）。
- **影响**：8-seed 批次的输入清单不可校验，与 `data/splits/*/manifest.sha256` 的既有做法不一致。
- **归属**：本次可自动解决（补写哈希或改脚本回填；后者会改动既有文件，需作者同意）。

### R-15 复现包未带 `p0_support` 清单
- **现状证据（实读）**：`dist/…/seeds_extension_20260917/` 仅含 `CANONICAL_GUARD.json`、`CANONICAL_PRESNAPSHOT.json`、`QUERY_DRIFT.json`、`VD1_MANIFEST.json`、`interaction_by_seed.csv`，**无 `p0_support/`**；而 `confirmation_ksdd2_20260918/p0_support/`（KSDD2）在包内 — 即两套确认/扩展集处理不一致。
- **影响**：D 工作流（种子 3..7 支持集方差）在包内不可复核，且 `VD1_MANIFEST.json` 指向的清单文件在包内不存在（悬空引用）。
- **归属**：本次可自动解决。

### R-16 / R-17 投稿元数据与公开策略
- **现状证据**：`ACCEPTANCE_20260920.md` 第 34 行自述"数据/代码可得性的 **3 个占位**（仓库地址、归档 DOI、发布包许可）与 MPDD/BTAD 许可的补录，需作者决定"。作者署名 / 单位 / 资助 / COI / 伦理声明：**未验证**（本次未逐份检索稿件正文，无法给出确定结论）。
- **影响**：多数期刊在投稿系统即强制这些字段，缺失会直接卡在投稿表单。
- **归属**：需作者决定（信息只能由作者提供）。

### R-18 ~ R-21 论文限制类（不阻断主结论）
- **R-18**：正文自述 `Full-pixel results currently have no bootstrap intervals and cannot support claims of full-pixel statistical significance`（`English_Manuscript_Source.md:205`）。→ 只能报告点估计方向，不得写 full-pixel 显著性/置信。
- **R-19**：效率数据为部分阶段计时（`SELFCHECK.json` 中 `closure/baseline-region: the instrumented canvas run has synchronised stage timings`=36 行，但 `closure/cost: the remaining gaps are written down, not hidden` 记 `gaps=4`；`ARTIFACT_INDEX.md` 工作流 C 记 "VisA 混合设备，计时不可用"）。→ 不得宣称"同步端到端计时"。
- **R-20**：`ARTIFACT_INDEX.md` 工作流 C 覆盖四数据集、共同区域表 864 行、6 个方法列，但方法家族仅两类（如 `SELFCHECK.json` 的 `PatchCore_native_*` 与 `AnomalyDINO_native_canvas*` + 自有 controlled_A1_*）。→ 不得包装为广泛 SOTA 排名。
- **R-21**：C16 证明的是"零排除判定在各对应变体下保持"。要证明变体间**等效**需另算 `OT − identity` 配对差区间——**本次未找到**该区间产物（`CLAIM_EVIDENCE_LEDGER.csv` C16 的证据列只列 `interaction_by_variant*.csv` / `ot_sensitivity*.csv` / `REPORT_CN.md §10`）。→ 不得写"各变体等效"。

---

## 三、未能验证 / 存疑

| 项 | 状态 | 说明 |
|---|---|---|
| 作者 / 单位 / 资助 / COI / 伦理声明现状 | **未验证** | 未逐份检索稿件与投稿材料的对应字段（见 R-16） |
| 权重 SHA-256 的具体期望值 | **未验证** | 盘上未见任何权重哈希记录，无法给出应有值（见 R-03） |
| `141/141` 对应的历史提交 | **未验证** | 未回溯该数字产生时的 HEAD 与测试范围（见 R-06） |
| `pytest` 修好后的真实通过数 | **未知** | 本次按要求只运行一次，且 collection 即中断，未得到 N passed |
| `R-11` 的推送意愿 / 归档 DOI 平台 | **未验证** | 属作者决策，非盘上事实 |
