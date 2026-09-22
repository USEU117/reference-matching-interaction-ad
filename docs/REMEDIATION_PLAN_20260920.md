# 投稿前解决计划（Remediation Plan）

- 日期：2026-09-20（Asia/Shanghai）
- 配套：问题编号一律引用 `docs/ISSUE_REGISTER_20260920.md`（R-01…R-21）。
- 前提：本计划**只写动作**，执行前请确认允许改动既有文件与创建提交；未获授权时仅执行只读校验类动作。
- **执行状态（2026-09-20 刷新）**：P0 已全部执行完毕（见文末检查清单）；P1/P2/P3 未动。逐条处置凭据见 `docs/ISSUE_REGISTER_20260920.md` §〇bis。
- 全程环境：`.venv-anomalyclip\Scripts\python.exe`（冻结结果即由此环境产出）。

## 执行状态（2026-09-22 刷新，只记状态变化，不上改原文）

- **P0**：已完成状态不变。其中"改后重新出一次 docx"这条验收 2026-09-22 再次通过：`scripts/paper_complete_review_20260920/build.py` 退出码 0，实测 **20 表 / 22 内嵌图 / 12 公式 / 34 文献 / 47 页 / 16,969 词**（docx SHA-256 `F3CAE3B491A99F8649E8900756D60C75163DDAA43B715F73D271308038DC44ED`）。⚠️ P0 文中出现的 `scripts\manuscript_build_20260914` 是**已冻结的旧链**，权威交付稿走 `scripts\paper_complete_review_20260920/`（详见 `docs/论文与图件问题汇总_仅复核_20260921.md` §八"跨文档口径矛盾" A / B 两条）。
- **P1 的"扩展基线"分支已完成**（不在本计划 R 编号内）：SubspaceAD 144/144、WinCLIP+ 144/144、AnomalyCLIP 零样本 36/36，零失败；`…/05_baselines_ext_20260921/baseline_common_region_ext.csv` 1188 行（SHA-256 `1C770129…`）已入正文 **Table 12**。**R-20 的"两个方法家族"提法随之过时**（现 5 个家族：PatchCore、AnomalyDINO、SubspaceAD、WinCLIP+、AnomalyCLIP 零样本）；末节针对 R-20 的措辞约束（禁 `SOTA` / `全面领先` / 排名）**继续有效**，冻结主表（Table 11）六列数值与表注一字未改。
- **P2-5 推送（原"需作者点头"）已完成**：`git rev-list --count origin/main..HEAD` = **0**，`main` 跟踪 `origin/main` 且已同步（HEAD `85d3207`，2026-09-22 复测；`de25a22` 为该条首次记录时的 HEAD）。
- **新增阻断项（建议编号 R-22）**：`build.py` 的版式母本 `docs/manuscript_polished_20260919/Reference_Matching_English_Polished_20260919.docx` 与交付 docx 本轮开始时**不在盘上**（`a08dc46` 把 `*.docx` 加入 `.gitignore` 后消失），`build.py` 首次执行即 `FileNotFoundError`；已按 SHA-256 逐字节恢复（`9DB99E60…` / `18694B90…`）后重建成功。**母本是不可由源重建的二进制输入**，建议移出忽略范围或保留受控副本并登记进 `ARTIFACT_INDEX.md`（详见 `docs/论文与图件问题汇总_仅复核_20260921.md` §八 F17）。
- **图件侧收口（不在本计划编号内）**：F01（图2(b) 紫框与填色对齐）、F02（图3(b) 权重措辞，含图内／图注／正文）、P04（图 S4 的 ±5% 参考带与 6.8% 实测值分开表述，5% 判据下实测首个 N = 700）已改并重渲染；F14 的 58 页 PPT 已重出（SHA-256 `48DD9180…`，第 20/21 页＝收敛／稳定性）。数据未改：`baseline_common_region.csv` `3C83AB004420A4F8…` 前后一致。
- **仍未动**：P1-1…P1-7、P2-1、P2-3、P2-4、P2-6、P3（需作者）。
- **2026-09-22 晚｜外部评审新要求已并入待办**：`docs/论文与图件问题汇总_仅复核_20260921.md` §八新增 **T09（命名规范，只出方案）、T10（long paper 定位）、T11（摘要末句给 GitHub 主页，**已执行并复测 47 页/20 表/22 内嵌图**）、T12（"为何对比方法无需目标域训练"中英段落）、T13（检测/定性图进正文）、T14（仓库改名，已完成）**；实验欠缺的逐条盘点与成本锚点见新增 `docs/EXPERIMENT_GAP_ANALYSIS_20260922.md`（A01–A17）。本批**未跑实验、未用 GPU**，`baseline_common_region.csv` 仍 `3C83AB00…`。

## 阶段总览

| 阶段 | 目标 | 关掉的问题 | 前置 | 主归属 |
|---|---|---|---|---|
| P0 一致性与措辞 | 让所有在册文档对同一口径说话 | R-06 R-07(措辞) R-08 R-09 R-10 | 无 | 自动 |
| P1 复现包可执行化与哈希 | 包在干净机器上能装、能跑、能校验 | R-01 R-02 R-03 R-04 R-13 R-14 R-15 | P0 的措辞定稿（避免二次打包） | 自动（R-03 许可项需作者） |
| P2 版本发布点与归档 | 包 ↔ 提交 ↔ 远端三者对齐 | R-11 R-12 R-05(测试状态) | P1 打包完成 | 自动整理 + 作者决定 push |
| P3 投稿元数据 | 补齐期刊强制字段 | R-16 R-17 | 无（可与 P1 并行） | 作者 |

---

## P0 一致性与措辞

**目标**：消除"同一时点两份记录结论不同"与"区间跨零被写成零效应"两类可被审稿人直接指出的问题。

**具体动作**
1. 统一 BTAD 口径（R-07）。以正文 `English_Manuscript_Source.md:205` 的自设纪律为准，全文改成一句话模板：
   > "点估计接近零、区间跨零，当前数据不足以确定交互方向"（英文：`the point estimate is close to zero and the interval spans zero, so the data do not determine the direction of the interaction`）
   - 替换范围：正文第 5 / 339 / 400 行的 `true null`、`essentially zero`；`docs/manuscript_updated_20260919/English_Manuscript_Source.md:253` 的 `true zero effect`；`CLAIM_EVIDENCE_LEDGER.csv` C17 行及 `scripts/manuscript_build_20260914/results.md`（及包内副本）的 `true null`。
   - 禁止保留 `true null` / `true zero effect` / `essentially zero` 三种写法中的任何一种。
2. 更新验收报告（R-08 R-10）：在 `scripts/limitation_closure_20260915/_night2_20260918/ACCEPTANCE_20260920.md` 第 12 行把 `69/71` 改为与 `SELFCHECK.json` 一致的实测值，并把第 28 行 C16 描述改为"台账已更新为主口径（MPDD 14/14 排除零）"。
3. 更新索引（R-09）：`docs/ARTIFACT_INDEX.md:18` 的 B 行状态改为"完成（主口径 14/14 排除零；最弱格 OT ε=0.05 的 I_BAL 下界 +0.006 个百分点）"，并保留"BTAD ε 网格未落逐单元诊断"这一真实瑕疵。
4. 加测试限定语（R-06）：`docs/CURRENT_DYNAMIC_FUSION_STATUS.md:159`、`docs/project_review_20260910/repro_audit.md`、`docs/paper_writing_preparation_20260830/README.md`、`…/11_RCEC_…md` 中的 `141/141` 改为带提交与日期的写法，例如"于 `<commit>`（`<date>`）在 `<scope>` 上实测 `<N>` passed"；未实跑前先标注"该数字对应历史提交，不适用于当前 HEAD"。

**验收标准（可验证）**
- `git grep -n "true null" -- docs experiments scripts` 命中 **0**；`true zero effect` 命中 **0**；在**论文正文**范围内 `essentially zero on BTAD` 命中 **0**。
- `ACCEPTANCE_20260920.md` 中的自检数字与 `SELFCHECK.json` 的 `passed/checks` 字段逐字一致（人工 diff 即可）。
- `docs/ARTIFACT_INDEX.md` 不再出现"跨零"作为工作流 B 的**结论**（作为"BTAD 判定不变"的说明性文字可以保留）。
- 改后重新出一次 docx：`python scripts\manuscript_build_20260914\build.py`，`build_validation.json` 仍为 tables 18 / figures 8 / equations 12 / refs 34。

**前置依赖**：无。**归属**：自动；R-07 的"BTAD 是否可称零效应"这一科研判断请作者在动手前一次性确认。

---

## P1 复现包可执行化与哈希

**目标**：`dist/replication_package_20260920/` 在干净机器上可安装、可 import、可校验，并自带 claim→evidence 链。

**具体动作**
1. 补源码与配置（R-01）。把 `src/`（含 `industrial_ad/` 全树）、`configs/` 复制进包；`methods/` 因体积与许可，二选一：
   - (a) 全量复制（注意 `methods/winclip/WinClip-master.zip`、`outputs/` 缓存应先剔除）；
   - (b) 只放 vendored 源码 + `VENDORED_*.md` 打补丁说明 + 上游 URL/commit（推荐，需作者选）。
   并在包内 `README.md` 增补"环境变量与路径"节：`set PYTHONPATH=<pkg>\src`（或 `pip install -e src`）、`FUSION_CANONICAL_ROOT`。
2. 修依赖安装（R-02）。在 `requirements_repro.txt` 顶部加 CUDA 段：
   ```
   --extra-index-url https://download.pytorch.org/whl/cu118
   torch==2.0.0+cu118
   torchvision==0.15.1+cu118
   ```
   并追加"非 lock 文件"的醒目提示；是否产出 `requirements-lock.txt`（`pip freeze` 于 `.venv-anomalyclip`）由作者决定（建议产出）。
3. 补权重清单（R-03）。新建包内 `docs/MODEL_WEIGHTS.md`：逐权重给 `名称 / 上游 URL / 固定 revision 或 commit / SHA256 / 许可`；至少覆盖 DINOv2-S/B、AnomalyCLIP、AdaptCLIP、PatchCore 权重、`open_clip` 预训练权重。
4. 补哈希与提交指针（R-04）。在包根生成：
   - `SOURCE_COMMIT.txt`：`git rev-parse HEAD` + `git describe --tags --dirty`；
   - `SHA256SUMS`：对包内全部文件求 SHA-256（排除 `SHA256SUMS` 自身）。
5. 补台账（R-13）。把 `experiments/dynamic_fusion/paper_evidence_closeout_20260914/`（至少 `CLAIM_EVIDENCE_LEDGER.csv`、`FAILURES.json`、各 `*_SUMMARY.json`）复制进包，并在包 `README.md` §6 删除"已知缺口第 1 条"。
6. 补 `p0_support`（R-15）。把 `experiments/dynamic_fusion/seeds_extension_20260917/p0_support/support_manifest_{mpdd,btad}.json` 复制进包对应目录。
7. 落 `manifest_sha256`（R-14）。先在 `d1_verify_manifest.py` 之外**独立计算**清单 SHA-256（不改既有脚本、不改既有 manifest）：`Get-FileHash support_manifest_mpdd.json -Algorithm SHA256`，将值写入包内与仓库内的 `VD1_MANIFEST.json` 对应字段；是否同步回改仓库文件需作者同意。

**验收标准（可验证）**
- 干净 venv 内 `python -c "import industrial_ad; print(industrial_ad.__file__)"` **成功**（包内路径）。
- `python -m pip install -r requirements_repro.txt` 在离线 wheel 缓存下成功；`python -c "import torch; print(torch.__version__)"` 输出含 `+cu118`。
- `Get-FileHash` 校验：包内随机抽 20 个文件重算与 `SHA256SUMS` 一致，0 处不符。
- `SOURCE_COMMIT.txt` 内容等于打包时的 `git rev-parse HEAD`。
- 包内 grep：`CLAIM_EVIDENCE_LEDGER.csv` 存在且行数 ≥17；`support_manifest_mpdd.json`、`support_manifest_btad.json` 存在。
- `VD1_MANIFEST.json` 两处 `manifest_sha256` 均为 64 位十六进制（非 `null`）。
- 包体量在补入后重新实测记录到 `README.md`（预期显著上升；`methods/` 采用 (b) 方案时增幅可控）。

**前置依赖**：P0 措辞定稿（避免同一包内正文与台账口径冲突）。**归属**：自动；`methods/` 方案 (a)/(b) 与权重再分发许可需作者确认。

---

## P2 版本发布点与归档

**目标**：得到一个不可变发布点，并使工作区、tag、远端、包四者对齐。

**具体动作**
1. 处置工作区 3 个修改（R-11）。先看内容再决定：`git diff -- README.md experiments/dynamic_fusion/representation_matching_interaction_20260914/READONLY_PROOF.json experiments/dynamic_fusion/representation_matching_interaction_20260914/SELFCHECK.json`（共 `651 insertions / 175 deletions`）。这些属于 P0 的成果时应随 P0 一并提交，否则回退。
2. 修测试 collection（R-05）。在 `scripts/innovation_v6_dgsafe/run_wave2a_build_reliability.py:64` 修 import（`src.subspacead` → 现包结构）或让 `tests/innovation_v6_dgsafe/test_wave2a_probes.py` 跳过该模块；随后实跑正式范围并记录。
3. `.gitignore` 补 `dist/`（R-12）——或反过来把包纳入正式发布流程。二选一，必须明确。
4. 打新 tag（建议 `final-20260920` 保持不变，另打 `submission-20260920`）：tag 必须指向"P0+P1 全部完成"的提交；并用 `git describe --tags --dirty` 确认 `--dirty` 为空。
5. 推送（**需作者点头**）：`git push origin main --tags`（当前超前 15 个提交）。本次不执行。
6. 归档 DOI：把最终包上传 Zenodo（或等效）取得 DOI，回填稿件可得性章节（R-16 的 3 个占位之一）。

**验收标准（可验证）**
- `.venv-anomalyclip\Scripts\python.exe -m pytest tests -q` 不再出现 collection error，输出实测 `N passed`（N 写入 `ACCEPTANCE_*.md`）。
- `git status --porcelain` 的 modified 行数为 **0**（未跟踪项必须全部属于刻意排除清单）。
- `git rev-parse HEAD` 与 `git rev-parse <新tag>^{commit}` 相同；`git describe --tags --dirty` 无 `-dirty`。
- `dist/` 要么有明确忽略规则、要么其内容与 tag 内清单一致（用 `SHA256SUMS` 抽查 ≥20 项）。
- 包内 `SOURCE_COMMIT.txt` 与新 tag 的 commit 一致。

**前置依赖**：P1 打包完成。**归属**：自动整理与本地 tag；推送与 DOI 归档需作者决定。

---

## P3 投稿元数据

| # | 动作 | 归属 | 验收 |
|---|---|---|---|
| 1 | 补齐作者、单位、通讯作者与邮箱、ORCID | 作者 | 投稿系统必填项无空缺 |
| 2 | 资助信息（基金号/项目名，或不适用声明） | 作者 | 稿件致谢段与投稿表单一致 |
| 3 | 利益冲突声明（或无 COI 声明） | 作者 | 独立章节存在 |
| 4 | 伦理审查声明（本类研究通常写"不涉及人类/动物受试者"） | 作者 | 独立章节存在 |
| 5 | 数据可得性：数据集 URL + 许可；代码可得性：仓库地址 + 归档 DOI + 许可 | 作者 | `ACCEPTANCE_20260920.md:34` 的 3 个占位全部填实 |
| 6 | 是否审稿阶段公开代码（按目标期刊政策） | 作者 | 明确"是/否"并在稿件中给出对应表述 |

**前置依赖**：无。**归属**：全部需作者。

---

## 需要作者提供的信息（清单一览）

1. 作者列表与署名顺序、单位、通讯作者联系方式、ORCID。
2. 资助来源（基金号/项目名）或不适用声明。
3. 利益冲突声明。
4. 伦理审查声明（或不适用声明）。
5. 代码仓库公开地址；归档 DOI 平台（Zenodo？校内？）与 DOI 号。
6. 发布包许可（沿用根 `LICENSE` 的 MIT，还是另定）。
7. `methods/` 在包内的处置方案：(a) 全量复制 / (b) 仅源码 + 上游指针。
8. 各预训练权重的再分发是否许可；若不许可，只给 URL + SHA256。
9. 是否在审稿阶段公开代码（按期刊政策）。
10. BTAD 口径确认：是否接受统一为"点估计接近零、区间跨零，不足以确定方向"。
11. 是否同意为落 `manifest_sha256` 而回改仓库内 `VD1_MANIFEST.json`（会改动既有文件）。
12. ~~是否同意推送本地 `main`（超前远端 15 个提交）并推送 tags~~ —— **已办结**（2026-09-22 实测 `origin/main..HEAD` = 0，tags 已在远端）。

---

## 只作为论文限制保留（不得宣称已完成）

以下四条 **不阻断主结论**，但必须在论文 Limitations 中如实陈述，且不得出现"已完成/已解决"类表述。措辞约束如下：

| 限制 | 允许的措辞 | 禁止的措辞 |
|---|---|---|
| stride-1 / full-pixel 只有点估计（R-18） | "full-pixel 结果目前只有点估计，用于方向一致性检查" | "full-pixel 统计显著"、"full-pixel 区间排除零"、"full-pixel 已补齐区间" |
| 效率数据为部分阶段计时（R-19） | "效率数据为部分阶段的计时，非同步端到端测量" | "端到端耗时"、"同步计时"、"整体加速比" |
| 外部对比为两个方法家族、四数据集六配置（R-20） | "外部对比覆盖四数据集六配置，限于两个方法家族" | "SOTA"、"广泛优于现有方法"、"全面领先" |
| correspondence 只证明零排除判定保持（R-21） | "在各对应变体下零排除判定保持" | "各变体等效"、"变体间无差异"、"对应方式不影响结果"（若需等效结论，须另算 `OT − identity` 配对差区间） |

---

## 建议执行顺序与检查清单

- [x] P0-1 统一 BTAD 口径（已按用户直接指示执行全文替换；**作者对科研判断的追认仍待**，见「需要作者提供的信息」第 10 项）
- [x] P0-2 验收报告 `69/71` → 实测 `71/71`；C16 描述改为"已完成"（2026-09-20）
- [x] P0-3 `ARTIFACT_INDEX.md` B 行旧结论替换为"主口径 14/14 排除零、最弱格 +0.000063；BTAD 14/14 跨零、判定不变；表 18 已加"
- [x] P0-4 `141/141` 已就地标注为 2026-09-02 历史快照并给出当前实测（260 passed）；过程记录类文档只加"后续状态"指针
- [x] P0 验收：结论性文本中 `true null` = 0、`true zero effect` = 0、`essentially zero on BTAD` = 0；重出 docx 后 18/8/12/34 不变（2026-09-20 实测）。**残留**：本计划与 `ISSUE_REGISTER_20260920.md` 中以引号引用这些字符串用于指认（刻意保留，见登记 §〇bis 说明）
- [x] P2-2（部分，替代方案）测试 collection 失败已按"让该模块跳过"处置：新增 `pytest.ini` 显式排除 `tests/innovation_v6_dgsafe/test_wave2a_probes.py`，实跑 **260 passed**；`run_wave2a_build_reliability.py` 的 import **未改**（冻结探针脚本，需单独授权）
- [ ] P1-1 补 `src/` + `configs/` + `methods/`（方案由作者定）
- [ ] P1-2 `requirements_repro.txt` 补 CUDA index；视需要产出 lock
- [ ] P1-3 新增 `docs/MODEL_WEIGHTS.md`（URL + revision + SHA256 + 许可）
- [ ] P1-4 生成 `SOURCE_COMMIT.txt` 与 `SHA256SUMS`
- [ ] P1-5 补 `paper_evidence_closeout_20260914/` 台账
- [ ] P1-6 补 `seeds_extension_20260917/p0_support/`
- [ ] P1-7 回填 `VD1_MANIFEST.json` 的 `manifest_sha256`
- [ ] P1 验收：包内 `import industrial_ad` 成功；抽查 20 项 SHA-256 全对；`+cu118` 安装成功
- [ ] P2-1 处置 3 个 tracked 修改（并入 P0 提交或回退）
- [x] P2-2（部分）测试 collection 失败已处置（采用"让该模块跳过"的替代方案）：新增仓库根 `pytest.ini` 显式排除 `tests/innovation_v6_dgsafe/test_wave2a_probes.py`，实跑 `pytest tests -q` 记录 **260 passed / 0 failed**；**未改** `run_wave2a_build_reliability.py` 的 import（冻结探针脚本，需单独授权）
- [ ] P2-3 `.gitignore` 处理 `dist/`
- [ ] P2-4 打新 tag（`--dirty` 为空）并核对 `SOURCE_COMMIT.txt`
- [ ] P2-5 作者点头后 `git push origin main --tags`
- [ ] P2-6 归档取得 DOI
- [ ] P3 作者提供 12 项信息（见上节），回填投稿表单与稿件章节
- [ ] 终检：Limitations 四条限制按上表措辞写入，全稿无"已完成/等效/SOTA/端到端"越界表述
