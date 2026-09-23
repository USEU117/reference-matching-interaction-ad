# 复现打包清单（REPRODUCIBILITY PACKAGE）

> 用途：把"公开/交接时应打包什么、排除什么、为什么"写成一张可执行的清单，并给出外人复现的正确顺序。
> 写作时点：2026-09-19（本地 Asia/Shanghai）。**所有体积均为本机实读**（`Get-ChildItem -Recurse | Measure-Object Length -Sum`，测量命令见 §4），不是估算。
> 配套：结论与数值见 [`HANDOVER_20260919.md`](HANDOVER_20260919.md)，目录 → 产物 → 命令索引见 [`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md)，环境见 [`environment_matrix.md`](environment_matrix.md) 与 [`../requirements_repro.txt`](../requirements_repro.txt)。

---

## 1. 三档处理原则

| 档 | 含义 | 处置 |
|---|---|---|
| **A 进版本控制（必打）** | 文本/脚本/清单/汇总数字：体积小、可审查、无法重建 | 直接随仓库交付 |
| **B 交接包附带（可选打）** | 体积中等、能重建但重建代价高 | 另打 `repro_assets/`，或按 §5 顺序现场重建 |
| **C 不打包（必排）** | 体积巨大或可重建：特征缓存、原始数据、虚拟环境、scratch、备份 | 排除并写明重建方式 |

**红线**：数据一律不再分发（各数据集许可见 `data/README.md`）；`.npz/.npy/.pt` 特征缓存**不在 git 里**，只能按 §5 重建或单独传到归档（体积见 §3）。

---

## 2. 应打包（档 A / B）

| 项 | 路径 | 体积（实读） | 为什么 |
|---|---|---|---|
| 全部脚本 | `scripts/**` | **39.4 MB / 1095 个文件** | 唯一的重建入口（`.py` + `.ps1` + `figures_*.mjs`）；不含 `.ps1` 无法跑编排 |
| 全部文档 | `docs/**` | **858.7 MB / 552 个文件** | 含规格 `docs/specs/`、索引 `ARTIFACT_INDEX.md`、交接 `HANDOVER_20260919.md`、图件绑定 `figures_reference_matching_20260914/FIGURE_BINDING.md`、本清单 |
| ├─ 其中 docx | `docs/**/*.docx`（28 份） | 199.9 MB | **排除**，见 §3（可重建） |
| └─ 其中图件/PDF | `docs/**/*.png|*.pdf|*.jpg`（298 份） | 366.7 MB | 保留：图件是产物的一部分，重建需 GPU 与数据 |
| 依赖清单 | `requirements_repro.txt` | 3,382 B | 环境重建的直接依据 |
| 数据许可与来源 | `data/README.md` | 小 | 逐数据集的来源/许可/校验和说明（**数据本体不打包**） |
| 划分清单 | `data/splits/{mpdd,btad,mvtec,visa}/{manifest.json,manifest.sha256}`、`mvtec/archive.sha256` | 小 | 定义全部报告条件的冻结支持集；已进 git |
| 工作流 A 汇总 | `experiments/dynamic_fusion/limitation_closure_20260915/A_btad03_corrected/{VERIFICATION.json,VERIFICATION_stride4.json,VERIFICATION_stride8.json,interaction_dataset_stride*.csv,interaction_by_condition_stride*.csv,log_stride8.txt}` | 小 | 四门校验 + 区间（数值可审查） |
| 工作流 B 汇总 | `…/B_correspondence/*.csv` + `*.json`（15 个，含 `B1_SUMMARY.json`、`B2_SUMMARY{,_btad}.json`、`variant_metrics{,_btad}.csv`、`interaction_by_variant{,_btad}.csv`、`ot_sensitivity{,_btad}.csv`、`VB_*.json`） | **122.1 KB / 15 个** | 对应审计与替换变体的全部数字 |
| 工作流 C 汇总 | `…/generalization_mvtec_visa_20260915/interaction_generalization.csv`、`C5_SUMMARY.json`、`p1_matrix/{STATUS,PROTOCOL,FAILURES}.json`、`p1_matrix/metrics_all_units.csv`、`p1_matrix/RUN_SUMMARY.json`、`p1_matrix/DEVICE_DEVIATION.json` | **≈ 3.0 MB**（`RUN_SUMMARY.json` 2.54 MB、`metrics_all_units.csv` 0.44 MB、`PROTOCOL.json` 6.6 KB、`DEVICE_DEVIATION.json` 3.2 KB；`FAILURES.json` 2 B = 空、`STATUS.json` 175 B） | 四数据集交互 + 逐单元指标 + 批次状态/失败清单 |
| 工作流 D 汇总 | `…/seeds_extension_20260917/{interaction_seed_variance.json,interaction_by_seed.csv,VD1_MANIFEST.json,CANONICAL_GUARD.json,CANONICAL_PRESNAPSHOT.json,QUERY_DRIFT.json}` | 小 | 8-seed 方差与四道门 |
| 工作流 E/H 汇总 | `…/representation_matching_interaction_20260914/05_extra_encoders/{S10_SUMMARY.json,encoder_comparison_three.csv,encoder_vs_S_difference.csv}` 及 `matched_scope/`、`wide_scope/` 下同名文件 | `S10_SUMMARY.json` **11.8 KB**（3 份共 0.035 MB） | 五编码器表与配对差 |
| 跨目录交互表 | `**/interaction_*.csv`（39 份） | **0.242 MB** | 各数据集/各构造的交互行，是表 14/15/17 的直接来源 |
| 工作流 F 汇总 | `…/confirmation_ksdd2_20260918/{F_SPEC.json,02_interaction/interaction_aggregate.csv,04_new_encoder/interaction_new_encoder.csv,p0_support/support_manifest_ksdd2.json}` | 小 | 唯一预冻结确认集的规格与结果 |
| 基线共同区域表 | `…/05_baselines_multi_dataset/baseline_common_region.csv`（864 行）、`S8_SUMMARY.json`；旧表 `05_baselines/baseline_common_region.csv`（216 行）保留作对照 | 232,684 B 级 | 图 7 与跨方法表的输入；旧表是生成器默认值，必须一并说明 |
| 夜跑/验收证据 | `scripts/limitation_closure_20260915/_night_20260917/`、`_night2_20260918/{VALIDATION_20260918.md,AUDIT_CLOSURE_20260919.md,*.json,*.log}` | 小 | 验收与审计的原始记录 |
| 正文源 | `scripts/manuscript_build_20260914/{manuscript.md,results.md,tables.json,references.json,figures.json,build.py,build_cn_docx.py}` | 小 | 正文与 docx 的唯一源 |

**档 A/B 合计（不含被排除项）≈ 0.70 GB**，其中 `docs/**` 的图件占 366.7 MB、`scripts/**` 占 39.4 MB。

---

## 3. 应排除（档 C）

| 排除项 | 体积（实读） | 为什么排除 | 怎么补回来 |
|---|---|---|---|
| `*.npz` / `*.npy` / `*.pt` | `outputs/` **477,616 MB / 3220 个**；`experiments/` **181,252 MB / 5540 个**（合计 ≈ 659 GB） | 特征/分数缓存，体积压倒一切；且是**确定性重导出**的结果，不是原始证据 | 按 §5 第 3 步用 `export_k8_cache.py` + `run_matrix.py` 重导 |
| `canonical/`（`outputs/**` 与 `experiments/**` 下） | **211,980 MB / 485 个**（≈ 212 GB） | 同上；B 支的 `imgs_masks` 是评价掩码的唯一来源，但可重导 | 同上；KSDD2/泛化的 canonical 分别导到各自 `canonical/` |
| `units/`（逐单元目录） | `experiments/**/units/` **41,584 MB / 13,490 个**（≈ 41.6 GB） | 逐单元 `patch_scores.npz`/`evaluation_scores.npz` 是中间量；**注意**：同目录的 `DONE.json`/`metrics.csv`/`PROTOCOL.json` 没进 git，若要留证据需**单独按白名单打** | 重跑矩阵（§5 第 4 步） |
| `outputs/`（整目录） | **480,404 MB / 6733 个**（≈ 480.4 GB） | 主 canonical 缓存 + PatchCore 缓存 + 日志 | 重导 canonical；基线缓存按 `05_baselines/README.md` 重跑 |
| `data/*_raw/`、`data/downloads/` | 原始目录合计 **10,917 MB / 23,226 个**（整个 `data/` 为 39,143 MB / 77,573 个） | **许可禁止再分发**（CC BY-NC-SA 等）；且体积大 | 由使用者自行按 `data/README.md` 下载并核对校验和 |
| `.venv-*`（7 个虚拟环境） | `.venv-adaptclip` 5,387 MB、`.venv-anomalyclip` 5,521 MB、`.venv-patchcore` 5,292 MB、`.venv-promptad` 5,316 MB、`.venv-rempad` 5,304 MB、`.venv-remp_ad` 5,164 MB、`.venv-winclip` 5,300 MB（合计 **37,285 MB ≈ 37.3 GB**） | 平台相关、体积大、可用 `requirements_repro.txt` 重建 | `python -m venv` + `pip install -r requirements_repro.txt`（见 `environment_matrix.md`） |
| `.tmp_*` / `.qa_render_*` | **847.2 MB / 1433 个** | scratch/渲染中间物 | 重跑对应脚本 |
| `*.bak*` | **241.25 MB / 23 个**（其中 8 份 docx 备份约 199 MB，另有 `中文对照内容.md.bak*` 等） | 修改前备份，非产物 | 不需要 |
| `docs/**/*.docx`（含当前 2 份 + 8 份 `.bak`） | **199.9 MB / 28 个** | 体积大且**完全可由源重建**；交接时若只给源可保证排版一致 | `.venv-anomalyclip\Scripts\python.exe scripts\manuscript_build_20260914\build.py`（中文稿用 `build_cn_docx.py`） |
| `.trae/`（对话/计划草稿） | 0.1 MB / 2 个 | 非交付内容（其中计划副本已在 `docs/specs/`） | 不需要 |

**注意（最容易漏的一点）**：`experiments/dynamic_fusion/generalization_mvtec_visa_20260915/{canonical,p1_matrix}`、`05_extra_encoders/{E1,E2,E3}/units/`、`seeds_extension_20260917/p1_matrix_*/units/` 这些目录**整体是 untracked**，其 `metrics.csv`/`DONE.json`/`PROTOCOL.json` 等**非 npz 文件也没进 git**。打包时必须显式加白名单，否则下一手拿到的就是"盘上有、git 没有"（见 `HANDOVER_20260919.md` §4.3 与 §6 #13）。

---

## 4. 体积是怎么读的（可复核）

```powershell
# 单项体积
Get-ChildItem <path> -Recurse -File -Force -ErrorAction SilentlyContinue |
  Measure-Object Length -Sum

# 排除项（示例：全仓 npz/npy/pt，剔除虚拟环境）
Get-ChildItem . -Recurse -File -Force -Include *.npz,*.npy,*.pt |
  Where-Object { $_.FullName -notmatch '\\.venv-' } | Measure-Object Length -Sum
```

| 汇总项 | 体积（实读） |
|---|---|
| `scripts/` | 39.4 MB / 1095 文件 |
| `docs/` | 858.7 MB / 552 文件 |
| `experiments/` | 182,858 MB / 20,120 文件 |
| `outputs/` | 480,404 MB / 6733 文件 |
| `data/` | 39,143 MB / 77,573 文件 |
| 7 个 `.venv-*` | 37,285 MB 合计 |

---

## 5. 外人复现的正确顺序

> 目标：在一台**空闲**的新机器上，从零走到"能自己算出表 14/15/17 的数字"。顺序不可颠倒——第 3 步之后才能进入任何工作流。

**第 0 步 读文档、确认机器**
先读 `docs/HANDOVER_20260919.md`（结论、坑、边界）、`docs/ARTIFACT_INDEX.md`（工作流 A–I 的目录/产物/命令）、`docs/environment_matrix.md`。
硬件：RTX 3060 Laptop 6 GB（sm_86）/ 16 GB RAM / 20 逻辑核；**并发上限 2**（超配会被 OOM 打死，见交接坑 10）。

**第 1 步 数据下载（按 `data/README.md`，再核对 `data/splits/*/manifest.json` 的 `root`）**

| 数据集 | 本机实际根（manifest `root` / 脚本默认） | 获取方式 |
|---|---|---|
| MVTec AD | `data/mvtec` | 官网表单后下载；校验 15 类与像素掩码 |
| VisA | `data/visa_raw` | `aws s3 cp --no-sign-request s3://amazon-visual-anomaly/VisA_20220922.tar data/downloads/` |
| MPDD | `data/mpdd_raw/MPDD` | HF 镜像（LFS SHA256 见 `data/README.md`） |
| BTAD | `data/btad_raw/BTech_Dataset_transformed` | 公共服务器（数据集 03 类用 BMP 掩码） |
| KolektorSDD2 | `data/kolektorsdd2_raw` | `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/fetch_kolektorsdd2.ps1 -Parts 16` |

下载完**逐一核对** `data/splits/<dataset>/manifest.sha256`（MVTec 另有 `archive.sha256`）。

**第 2 步 环境**
建 Python 3.10.11 的 `.venv-anomalyclip`，`pip install -r requirements_repro.txt`（这是"实际 import 过的包"清单，不是 lock 文件）；按需建其他 venv（PatchCore/WinCLIP/PromptAD/AdaptCLIP/ReMP-AD，见 `environment_matrix.md`）。
离线加载 HF/DINOv2 权重时设 `HF_HUB_OFFLINE=1`、`HF_ENDPOINT=https://hf-mirror.com`；vendored 代码需按 `scripts/limitation_closure_20260915/_night2_20260918/VENDORED_PATCH_anomalydino_backbones.md` 打 `skip_validation=True` 补丁。

**第 3 步 canonical 生成或获取（**先决条件**）**
canonical `k8` 缓存不随包发布，必须重建（或单独从归档下载后放到同一相对路径）：
- 主研究（MPDD/BTAD）：默认根 `outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/{B,S,C}/`
- 泛化（MVTec/VisA）：`experiments/dynamic_fusion/generalization_mvtec_visa_20260915/canonical/{B,S,C}/`
- 确认集（KSDD2）：`experiments/dynamic_fusion/confirmation_ksdd2_20260918/canonical/{B,S,C}/`
- 种子扩展（3..7）：`experiments/dynamic_fusion/seeds_extension_20260917/canonical/`（或复用主根）

工具：`scripts/unified_fusion_paper_support_v1/{build_support_manifest.py,export_k8_cache.py,run_matrix.py}`；跨数据集脚本统一读环境变量 **`FUSION_CANONICAL_ROOT`**（`run_matrices.ps1`、`run_analysis.ps1`、`run_visa_parallel.ps1`、`f_chain_20260918.ps1` 都会设置它）。
**冻结纪律**：`stats_v2.DATASET_ID` 只能追加（mpdd=1/btad=2/mvtec=3/visa=4/ksdd2=5），它是重采样种子的组成部分；不要改动已归档产物。

**第 4 步 各工作流入口命令**（详细路径以 `ARTIFACT_INDEX.md` §一 为准）

| 工作流 | 入口 |
|---|---|
| C 编码 → 矩阵 → 统计 → 交互表 | `scripts\limitation_closure_20260915\c_encode_generalization.ps1` → `run_visa_parallel.ps1` → `run_analysis.ps1` → `.venv-anomalyclip\Scripts\python.exe …\c5_generalization_interactions.py` |
| A（BTAD-03 细网格） | `.venv-anomalyclip\Scripts\python.exe scripts\limitation_closure_20260915\a1_btad03_corrected_grid.py --stride 8 --replicates 1000` |
| B（对应审计 + 替换） | `…\b1_correspondence_audit.py`；`…\b2_learned_correspondence.py --mode variants`；BTAD 四变体 + ε 网格见交接 §4.2（**必须一次跑完**） |
| D（种子方差） | `…\d1_verify_manifest.py`、`d2_canonical_guard.py`、`d2b_query_drift.py`、`d3_seed_variance.py` |
| E/H（额外编码器） | `…\s4_extra_encoders.py --branch E1\|E2\|E3 …` → `…\s10_encoder_comparison.py`；一键重算 `p0_fixes_20260919.ps1` |
| F（KSDD2 确认集） | `scripts\limitation_closure_20260915\night_run_2_20260918.ps1`（阶段 2；`-PreflightOnly` 只预检） |
| 图件 | `node scripts\figures_reference_matching_20260914\build.mjs` → `qa_layout.py` → `figure_font_gate.py --self-test` → 各 `build_*.py` |
| 正文/docx | `.venv-anomalyclip\Scripts\python.exe scripts\manuscript_build_20260914\build.py`（中文 `build_cn_docx.py`） |

**第 5 步 判成败**
**只看单元目录里的 `DONE.json` 计数与最新时间戳**；`STATUS.json` 可能长时间停在 `running`（交接坑 9）。批次失败先看 `FAILURES.json`，再按 `logs/<dataset>_s<seed>_k<shot>_<cat>.log` 排查。长任务一律分离启动。

---

## 6. 打包前检查清单

- [ ] 原始数据**没有**被打进包（`data/*_raw/`、`data/downloads/`）
- [ ] `*.npz/*.npy/*.pt`、`canonical/`、`units/`、`outputs/`、`.venv-*`、`.tmp_*`、`*.bak*`、`*.docx` 均未进包
- [ ] untracked 实验目录里的**非 npz 证据**（`DONE.json`/`metrics.csv`/`PROTOCOL.json`/`*_SUMMARY.json`）已按白名单单独打
- [ ] `docs/specs/`、`ARTIFACT_INDEX.md`、`HANDOVER_20260919.md`、`FIGURE_BINDING.md`、本清单、`environment_matrix.md`、`requirements_repro.txt`、`data/README.md` 均在包内
- [ ] 各工作流的 `*_SUMMARY.json` / `VERIFICATION*.json` / `interaction_*.csv` 均在包内
- [ ] 包内不含任何秘密（token/密钥）；`.env` 类文件已确认不存在
- [ ] 需要一次 docx 重建：`python scripts/manuscript_build_20260914/build.py`（本次**未重建**，见交接说明）

---

## 7. 已生成的复现包与 2026-09-20 的可执行性加固

> 本节记录 `dist/replication_package_20260920/` 的**实际状态**（实读）。前六节是"应打包什么"的清单，
> 本节是"实际打了什么、外人能不能直接跑"。

### 7.1 包的基本指标（实读）

| 项 | 值 |
|---|---|
| 路径 | `dist/replication_package_20260920/` |
| 文件数 / 体积 | **2488 个文件 / 470,734,903 B = 470.73 MB = 448.93 MiB**（不含 `SHA256SUMS` 自身） |
| 首版（v1） | 1316 个文件 / ≈433.55 MB —— 只是**证据与说明包**，缺 `src/`、`configs/`、`methods/`、包级校验和与提交指针，**不能独立执行** |
| 校入口 | `SHA256SUMS`（2488 行，`hash  path`）、`SOURCE_COMMIT.txt`、包内 `README.md` |

### 7.2 各顶层目录（实读）

| 包内路径 | 文件数 | 体积 | 相对 §2 白名单 |
|---|---:|---:|---|
| `docs/` | 462 | 419,147,828 B | 一致 |
| `methods/` | 1085 | 36,546,719 B | **新增**（§2 未列；`src/` 属"重建入口"的隐含依赖） |
| `scripts/` | 756 | 10,156,044 B | 一致 |
| `experiments/` | 88 | 4,379,744 B | 白名单 + **新增** `paper_evidence_closeout_20260914/CLAIM_EVIDENCE_LEDGER.csv` 与 `seeds_extension_20260917/p0_support/support_manifest_{mpdd,btad}.json` |
| `src/` | 57 | 363,339 B | **新增（必需）**：`industrial_ad` 被 106 个脚本 import |
| `data/` | 10 | 60,018 B | 一致 |
| `configs/` | 24 | 23,340 B | **新增（必需）**：协议/路由配置由脚本按相对路径读取 |
| `weights/` | 1 | 17,426 B | **新增**：46 个权重的目标路径 + SHA-256 + 来源（权重本体不入包） |
| `LICENSE` / `SOURCE_COMMIT.txt` / `requirements_lock.txt` / `requirements_repro.txt` | 4 | 20,609 B | **新增 3 个**：提交指针、lock 文件；`requirements_repro.txt` 补注 CUDA 安装源与解释器选择 |
| **合计（不含 `SHA256SUMS`）** | **2488** | **470,734,903 B** | |

### 7.3 加固做了什么

1. **静态依赖审计**：对包内 `scripts/**` 的 418 个 `.py` 做 AST import 扫描，用 `.venv-anomalyclip`
   的 `find_spec` + 仓库导入根逐个判定"第三方 / 仓库本地 / 无解"，得到"包内缺失的本地依赖"清单；
   据此补齐 `src/`、`configs/`、`methods/`（9 个方法目录的**源码与配置**，剔除权重 8.5 GB 与数据集 7.3 GB）。
2. **权重不进包**：改为 `weights/README.md` —— 46 个权重逐个给出目标路径、字节数、**本机实读的 SHA-256**
   （46/46 全部读到，无 `[[SHA256]]` 占位）与来源 URL；其中 **30 个（AnomalyCLIP）随上游源码归档提供**
   （归档 commit `3911738c…`，ZIP SHA-256 `533ED87B…`；见 `docs/reproduction_notes.md:13-23`），
   **2 个（AdaptCLIP / ReMP-AD）才是本项目训练产物**（后者公网不存在）。
3. **环境**：`requirements_repro.txt` 头部明确它是"最小可复现约束集、**不是 lock**"，并给出
   `--index-url https://download.pytorch.org/whl/cu118` + `torch==2.0.0+cu118 / torchvision==0.15.1+cu118`
   的写法（版本与实读一致）与两个解释器的分工；另生成 `requirements_lock.txt`（`.venv-anomalyclip`
   的 `pip freeze` 实读，95 行），并逐条标注 3 行**本机特有**条目（`anyup @ file:///…`、
   `torch @ file:///…outputs/downloads/…whl`、`-e git+…SubspaceAD@ef56d5c8…`）。
4. **包级校验与指针**：`SHA256SUMS`（2488 行）+ `SOURCE_COMMIT.txt`（HEAD `841b478b0658ff0af12d4aa93ad8009a38b1e532`、
   分支 `main`、8 个 tag、**工作树不干净**：19 个已改 + 32 项未跟踪）。
5. **8-seed 清单哈希**：`VD1_MANIFEST.json` 的 `manifest_sha256` 原为 `null`，原因是
   `d1_verify_manifest.py` L109 读的 `manifest.get("sha256")` 这个键**从未被生成脚本写入**
   （`build_support_manifest.py` L299 只把它打印到 stdout）。口径由同一流水线的两处代码确证为
   "**清单文件字节的 SHA-256**"（`export_k8_cache.py` L641 `support_manifest_sha256`；
   并用 `support_manifest_*.json` 里的 `source_manifest_sha256` == `sha256(data/splits/<ds>/manifest.json)`
   交叉验证通过）。填入值：mpdd `e9964504564396ee2c5d0fd6cf9b05a077c792930aa7e2798a203d90f7f77f35`、
   btad `c0304a9666ebdbf2c8aa04dd23912d1aa0b9b81908df9c79ff3e78374b4ef66c`。
6. **可执行性验证**（不新建 venv）：把 `sys.path` 指向包目录，61 个本地模块 import 全部成功
   （唯一例外 `UniVAD`：缺 `groundingdino` 编译扩展，且不在冻结流水线上）；从包内运行 4 个代表性
   入口脚本的 `--help`，退出码均为 0。

### 7.4 校验方式

```powershell
cd dist\replication_package_20260920
$bad = 0
Get-Content .\SHA256SUMS | ForEach-Object {
    $h, $p = $_ -split '  ', 2
    if ((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() -ne $h) { $bad++ }
}
"mismatching files: $bad"      # 期望 0
```

### 7.5 本包仍未覆盖的（详见包内 `README.md` §7）

- 数据本体（许可）、模型权重（体积 + 2 个项目训练权重（AdaptCLIP / ReMP-AD）不可下载；AnomalyCLIP 的 30 个检查点随上游源码归档提供）、canonical/units/outputs 缓存（≈659 GB）、GPU。
- `CLAIM_EVIDENCE_LEDGER.csv` 有 10 条 `evidence_file` 引用指向 `00_audit/`、`01_statistics/`、
  `02_baselines/`、`03_paper/`、`04_recheck/` 下的文件，这些文件**在仓库里存在但不在包内**（原白名单未含）。
- `patches/*.patch`（7 个，记录 vendored 方法相对上游的改动）未随包；包内 `methods/` 已是打过补丁的版本。
- `fetch_assets` / `recompute_tables` / `table_geometry` 三个模块来自仓库之外的第三方文档技能目录，
  受影响脚本 8 个（清单见包内 `README.md` §7 第 4 条）。
- 本包**未重建任何实验产物、未跑任何实验、未做 git 提交**。
