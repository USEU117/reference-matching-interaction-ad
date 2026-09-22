> 本文件是 `.trae/documents/` 同名文件的受控副本（2026-09-19 复制），原路径保留。

# 夜间执行交接文档（2026-09-17 20:40 冻结）

> 本文件是给「新开一个对话」的执行者看的。**所有正在运行的进程已在 20:36 全部暂停**，无残留。
> 本轮的权威计划仍在 `.trae/documents/remaining_experiments_full_closure_plan_20260915.md`；
> 本文件只描述**它之外**的进度、待办、坑，以及计划里没有的新增实验内容。

---

## 0. 一句话现状

工作流 **A / B / E 全部完成**；**C 的 MVTec 完成、VisA 75/144**；**D 的矩阵（seeds 0..7）完成、统计未跑**。
论文主线所需证据里，还差 **VisA 剩余单元 → d3 支持集方差 → C 统计与四数据集交互表 → 共同有效区域**，
以及一个计划里没有、但属于最大科学缺口的 **真正未碰过的确认集**。

---

## 0.1 【先读】两套编号完全不同，极易混淆

本文档的**工作流编号**与论文里的**分支编号**是两套独立体系，字母重合纯属巧合：

| 本文档的工作流 | 含义 | 论文里的同名/近名字母 | 含义 |
|---|---|---|---|
| 工作流 **A** | BTAD-03 修正几何细网格 | — | — |
| 工作流 **B** | 画布对应审计 + 学习式替换 | 分支 **B** | DINOv2-B (ViT-B/14) |
| 工作流 **C** | MVTec/VisA 泛化 | 分支 **C** | AnomalyCLIP ViT-L/14@336px |
| 工作流 **D** | **seed 3..7 支持集方差** | 分支 **D** | **WideResNet50-2**（论文的"预指定扩展"） |
| 工作流 **E** | 两个额外编码器 | **E1 / E2** | DINO `deiT-small/8` / ConvNeXt-Tiny |

**最危险的一条**：文档里的「工作流 D」是**种子扩展**，论文里的「D」是**编码器分支**。看到 "D 已完成" 时先确认说的是哪个——
- 「工作流 D 的矩阵已完成」= mpdd/btad 的 seeds 0..7 矩阵（本文档 §2）
- 「论文的 D 扩展已完成」= TRI_D / BAL_D 的 36 单元（见附录 D）
两者是**不同的东西**，都已部分完成，别互相顶替。

---

## 1. 环境事实（不遵守会静默退回 CPU / 直接 OOM）

```
默认 python            : torch 2.12.1+cpu      cuda_available=False  ← 只能跑统计，不能编码
.venv-anomalyclip      : torch 2.0.0+cu118     cuda_available=True   ← 编码与矩阵必须用它
.venv-patchcore        : torch 2.0.0+cu118     cuda_available=True
GPU                    : RTX 3060 Laptop, 6.0 GB, sm_86
RAM                    : 15.8 GB 总量（注意：不是 20+ GB，空闲通常只有 8–10 GB）
CPU                    : 20 逻辑核
D: 剩余空间            : 约 190 GB
```

**新增的实测事实（本轮测得，计划里没有）**

| 事实 | 数值 | 用途 |
|---|---|---|
| 单单元 GPU 显存峰值（小类别 candle） | 2430 MiB | 决定并发上限 |
| 单单元 GPU 显存峰值（大类别 pcb3） | 2600 MiB | **与单元大小几乎无关**：`--chunk 256` 把 matmul 分块，峰值主要是 CUDA 上下文 |
| 3 路并发 K=8 显存峰值 | 3331 MiB | 3 路安全，尚有 ~2.5 GB 余量 |
| GPU / CPU 单单元耗时比 | 1.77×（candle K=1）、2.41×（pcb3 K=1） | score 阶段快 5.3–7.8×，load/metric 不变 |
| 3 路 GPU vs 顺序 CPU（3 个 K=8 大单元） | 159 s vs ~2500 s | **约 8×** |
| CPU 并发上限 | 2（16 GB RAM） | 并发 4 在主机侧 OOM：`Unable to allocate 980 MiB for (334464, 768)` |

---

## 2. 已完成（含验证门结论与产物路径）

| 工作流 | 内容 | 关键结论 | 产物 |
|---|---|---|---|
| **A** | BTAD-03 修正几何细网格 | VA.1–VA.4 全过，复现到 5.55e-16 | `experiments/dynamic_fusion/limitation_closure_20260915/A_btad03_corrected/` |
| **B1** | 画布对应审计 | exact 5.9%(mpdd)/13.3%(btad)，perm 0.06%/0.05% | `.../B_correspondence/B1_SUMMARY.json` |
| **B2** | 学习式对应替换 | identity 与 Procrustes **完全相同**（I_TRI +0.007671）；‖W−I‖_F=39.2 | `.../B_correspondence/B2_SUMMARY.json` |
| **E1** | DINO `deiT-small/8` | 48 单元；AUROC min 0.9163；I_TRI 在 MPDD/BTAD 均排除零 | `.../05_extra_encoders/E1/` |
| **E2** | ConvNeXt-Tiny (`fb_in1k`) | 48 单元；AUROC min 0.8871；MPDD 上 I_TRI≈0、BTAD 上 I_TRI 与 I_BAL 均排除零 | `.../05_extra_encoders/E2/` |
| **VE.3** | 恒等回归 | 新代码路径驱动已发布 D 编码器，20 项比较 **max\|Δ\|=0.0** | `.../05_extra_encoders/E1/E1_SUMMARY.json` 同目录体系 |
| **VE.5** | 四分支交互并列表 | 见 §6 的表 | `.../05_extra_encoders/encoder_comparison_three.csv`、`S10_SUMMARY.json` |
| **论文 D 扩展** | TRI_D / BAL_D（WideResNet50-2 分支，**预指定**） | 36 单元；四个交互全部排除零；D−S 在 BTAD 排除零、MPDD 跨零 | `.../04_new_encoder/`；已进手稿 §4.2.4 的 Table 8/9/10。详见**附录 D.1**（注意：与「工作流 D」不是一回事，见 §0.1） |
| **C** | MVTec 矩阵 | 180/180 | `experiments/.../generalization_mvtec_visa_20260915/p1_matrix/` |
| **C** | VisA 掩码几何修复 | 见 §5 坑 3 | `gen/canonical/B/visa_s*_k8/*.npz`（36 单元全部重建掩码） |
| **D** | 清单 + 守卫 | VD.1 过（72 单元独立复现）；只增不改守卫过 | `experiments/dynamic_fusion/seeds_extension_20260917/VD1_MANIFEST.json`、`CANONICAL_GUARD.json` |
| **D** | seeds 3..7 编码 | 135 个 npz（3 分支×2 数据集×5 种子），共享 query 块 | 原 canonical 根下新增 `*_s3..s7_k8` |
| **D** | mpdd / btad 矩阵 | **192/192、64/64 完成** | `seeds_extension_20260917/p1_matrix_mpdd|_btad/` |
| **D** | VD.2 漂移测量 | 见 §6，比值 ~1.5e-05 | `seeds_extension_20260917/QUERY_DRIFT.json` |

---

## 3. 未完成（按执行顺序，含确切命令）

### 3.1 VisA 矩阵剩余 69 个单元（75/144 已完成）

```powershell
cd <repo-root>
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass',
  '-File','scripts\limitation_closure_20260915\run_visa_parallel.ps1',
  '-Concurrency','3','-Device','cuda','-Python','.venv-anomalyclip\Scripts\python.exe' -WindowStyle Hidden
```

- 队列式**幂等**：自动只排 `DONE.json` 缺失的单元，重复启动不重算。
- 双重节流：空闲 RAM < 3.5 GB 或空闲显存 < 900 MB 时暂停派发。
- 收尾会用标准 `run_matrix.py --resume` 写 `STATUS.json: completed`（分析链等的就是它）。
- 预计 **~45 min**（3 路 GPU，37–40 s/单元有效速度）。

### 3.2 d3 支持集方差（VD.3 + VD.4）

```powershell
.venv-anomalyclip\Scripts\python.exe -u scripts\limitation_closure_20260915\d3_seed_variance.py
```

- 输入：`p1_matrix_mpdd`、`p1_matrix_btad`（seeds 0..7）+ `QUERY_DRIFT.json`
- 输出：`seeds_extension_20260917/interaction_by_seed.csv`、`interaction_seed_variance.json`
- 口径：MPDD 6 类 + BTAD 01/02（**BTAD-03 被排除，理由见 §5 坑 4**）；256 单元 × 1000 次重采样
- 单进程约 **100 min**，是当前最长尾。**若要缩短**：按单元并行化（单元彼此独立），4 路可压到 ~25 min。
  注意 16 GB RAM 上限，建议 4 路并加内存节流。
- **VD.3 有一个陷阱已修但需复核**：发布值是**整数据集宏平均**，缩小类别范围时必须标 `skipped: reduced category scope`，不能当成回归失败。

### 3.3 C 的统计与交互表（VC.5 / VC.6）

三条命令已全部串在一个脚本里：

```powershell
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass',
  '-File','scripts\limitation_closure_20260915\run_analysis.ps1' -WindowStyle Hidden
```

它会依次执行（阶段 0 先等 VisA 完成，然后）：

| 阶段 | 命令 | 产物 | 默认是否执行 |
|---|---|---|---|
| 1 | `d2b_query_drift.py --device cuda` | `QUERY_DRIFT.json`（已存在，重跑约 3 min，幂等） | 是 |
| 2 | `d3_seed_variance.py` | `interaction_by_seed.csv`、`interaction_seed_variance.json` | **否（需 `-IncludeD3`）** |
| 3a | `run_fullpixel.py --run-root gen/p1_matrix --output gen/p4_fullpixel --datasets mvtec visa --seeds 0 1 2 --shots 1 2 4 8 --resume` | stride-1 点估计 | 是 |
| 3b | `stats_v2.py --run-root gen/p1_matrix --output gen/p1_statistics --datasets mvtec visa --seeds 0 1 2 --shots 1 2 4 8` | 自助样本 | 是 |
| 3c | `analyze_conditions.py --matrix gen/p1_matrix --statistics gen/p1_statistics --output gen/p2_conditions` | 条件表 | 是 |
| 4 | `c5_generalization_interactions.py` | `gen/interaction_generalization.csv`、`C5_SUMMARY.json` | 是 |

**关键**：3a/3b/3c 必须带 `FUSION_CANONICAL_ROOT=experiments/dynamic_fusion/generalization_mvtec_visa_20260915/canonical`（脚本已设）。跑完写 `seeds_extension_20260917/ANALYSIS_CHAIN.json` 记录每步退出码。

> **已改为默认跳过，无需手动注释**：`run_analysis.ps1` 现在带 `-IncludeD3` 开关，**默认不跑 d3**（阶段 2 会记录 `skipped by design`）。
> 理由：d3 是单线程 100 min 的 CPU 阶段，串在链里会白占 GPU 空闲窗口并推迟阶段 3–4。
> 两者读的是不同产物，**先后顺序任意**：可以先并行跑 d3，再启动链；也可以先跑链的 3–4，再补 d3。
> 需要一次性串跑时才加 `-IncludeD3`。

默认启动命令（阶段 0/1/3/4）：

```powershell
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass',
  '-File','scripts\limitation_closure_20260915\run_analysis.ps1' -WindowStyle Hidden
```

### 3.4 跨方法共同有效区域（三评价网格的第三项）

计划的「三评价网格」= stride-8 区间（主）、全像素点估计、**跨方法共同有效区域交集**。
前两项有产物，第三项**在 MVTec/VisA 上从未跑过**。原研究用 `scripts/representation_matching_interaction_20260914/s8_common_region.py` 做过 mpdd/btad。**待办**：确认该脚本能否直接吃 `CATS=mvtec/visa`（大概率需要像其它脚本一样追加 `CATS`），然后对 gen 矩阵跑一次。这是 VC.5 之外唯一还缺的评价口径。

### 3.5 论文正文落地（非实验，但阻塞交付）

以下数值都还没进正文，需要在 `docs/manuscript_reference_matching_20260914/` 的英文稿与中文对照稿里补齐：

- 工作流 A/B 的收口结论（`limitation_closure_20260915/VERIFICATION_REPORT_CN.md` 有素材）
- VE.5 四编码器并列表（见 §6）
- C 的四数据集交互表 + 角色措辞（MVTec=`external_frozen_validation`、VisA=`in_domain_frozen_validation`，**不得**写 `holdout`）
- D 的支持集方差结论（"换一批正常参考图结论是否改变"）
- **设备偏离声明**（见 §5 坑 6）与 E1/E2 的**事后探索性**标注（AD-6）

---

## 4. 计划里没有、但属于最大科学缺口的新增实验

### 4.1 工作流 F：真正的未碰过确认集（**推荐优先做，且必须一次性打开**）

计划 §6.1 已承认：**目前不存在未碰过的确认集**。MVTec/VisA 都参与过旧项目，且 VisA 对 C 分支是域内（AnomalyCLIP checkpoint 在 VisA 上训练）。这直接削弱"泛化"主张的说服力。

**做法（严格顺序，不可颠倒）**：

1. 选定数据集并下载。候选（按「工业异常 + 规模可控 + 与本项目无交集」排序）：
   - **KolektorSDD2**（真实工业缺陷、小、二分类）—— 最省算力
   - **MVTec LOCO-AD**（逻辑异常，与像素级缺陷互补）—— 最有新意
   - **Real-IAD**（多视角、规模大）—— 最强但最贵
2. **先写冻结规格**：`F_branch/encoder`、特征层、几何、J/L 定义、评价口径、`DATASET_ID`（**必须新键，绝不动 mpdd=1/btad=2/mvtec=3/visa=4**）、以及**预期方向**（明确写："若 I_TRI 不排除零，则本主张在本数据集上不成立"）。
3. **规格落盘时间戳必须早于任何特征文件**（VE.1 的门就是查这个）。
4. 编码（`export_k8_cache.py` 追加 dataset/branch/ROLE/DATA_ROOT，见坑 3 的掩码守卫）→ 矩阵（`run_matrix.py` 追加 `CATS`）→ 统计（`stats_v2.py` 追加 `CATS` 与 `DATASET_ID`）。
5. 只打开一次，结论无论正负都如实报告。
6. 预估：编码 GPU ~1 h，矩阵 GPU ~1–2 h（新数据集类别通常少于 MVTec），统计 CPU ~1–2 h。

**若时间不够**：至少把"为什么必须有一个冻结的确认集、以及为什么本计划给不出"写清（§6 已有素材），不要用泛化证据冒充确认。

### 4.2 工作流 G（可选）：BTAD-03 纳入 D 的跨种子方差

当前 D 的 BTAD 只用 01/02。原因是 seeds 0..2 的 canonical B 掩码带着**正方形压缩缺陷**（BTAD-03 grid 32×42 但掩码 448×448），而 seeds 3..7 用的是正确几何，两者不可混。

**补齐做法**：
1. 为 seeds 3..7 生成 `01_geometry/gt/btad_s{seed}_03_faithful.npz`（生成器见 `scripts/paper_evidence_closeout_20260914/btad03_geometry_recheck.py:80` 的 `faithful_masks(sample_ids, canvas, resized_hw)`，它对 seed 无依赖）。
2. 在**不改冻结产物**的前提下，把 seeds 0..2 的 BTAD-03 也导出到**独立的 corrected 根**，然后在 corrected 几何上跑 seeds 0..7 的跨种子方差。
3. 收益：BTAD 从 2 类恢复到 3 类，D 的结论覆盖面完整。

### 4.3 工作流 H（可选，成本极低）：第二个真正异构骨干 Swin-T

AD-5 原定主选 ConvNeXt-T、备选 Swin-T。ConvNeXt-T 已跑通，Swin-T 现在**下载已无障碍**（走 `HF_ENDPOINT=https://hf-mirror.com`，实测 200；torchvision 官方源 `download.pytorch.org` 返回 403 不可用）。

- 只需在 `s4_extra_encoders.py` 的 `BRANCHES` 里加一项（`timm.create_model('swin_tiny_patch4_window7_224.ms_in1k', features_only=True, out_indices=(1,2))`，stride 8/16 与 D 的 layer2/layer3 对齐，dim=192+384=576，canvas 需取 16 的倍数）。
- 收益：把"分层窗口注意力"作为**第三个**独立家族，VE.5 表从 4 行扩到 5 行。约 40 min。

### 4.4 工作流 I（可选）：监督式学习对应的"保证边界"

B2 只做了**无监督** Procrustes（结果：交互完全不变）。若要让"学习式对应"的论证更硬，可加一个**有监督**变体：用几何真值对应训练一个线性映射/小 MLP，再检验交互是否仍不变。**注意 AD-9**：这仍然只能证明"结论不依赖对应选择"，**不能**证明"画布位置描述同一物体部位"。这是方法论边界，不是实验缺口——做了也只是加强，不是解决。

---

## 5. 本轮踩过的坑（务必先读，避免重复劳动）

1. **后台作业会被终端杀掉**。把长任务作为后台作业跑在 agent 的终端里，后续任何前台命令复用同一终端都会把它挤掉，退出码 **-1**，看上去像崩溃但没有 traceback。
   → **一律用 `Start-Process ... -WindowStyle Hidden` 分离启动**。
2. **`Start-Process -PassThru` 的 `ExitCode` 在本机 PowerShell 读不到**（恒为空），据此判成败会产生大量**假 FAILED**。
   → **判据改为「单元目录里有没有 `DONE.json`」**（`run_visa_parallel.ps1` 已修）。
3. **VisA 历史缓存的 B 分支掩码是正方形压缩的**（如 candle 存 448×448，而网格 32×35 对应画布 448×490）。MVTec 因图像本身是正方形掩盖了这个 bug。同一缺陷也命中 **BTAD-03**（grid 32×42，掩码 448×448）——正是论文 S0 修正针对的那类几何错误。
   → `export_k8_cache.py` 已加 `masks_on_canvas()` 守卫：掩码形状 ≠ `grid*MAP_STRIDE` 时按同一规则从数据集重建，并记录 `masks_rebuilt_on_canvas`。**VisA B 的 36 个单元已重导**。
4. **BTAD 的 canonical 只有 seeds 0,1**（`btad_s2_k8` 从未导出，尽管冻结清单里有 seed 2），导致 D 的 btad 批次一开始 `FileNotFoundError`。
   → 本轮已用冻结清单补导 `btad_s2_k8`（三分支）。**mpdd 有 0/1/2，btad 原本只有 0/1**，写新脚本时别再假设对称。
5. **`STATUS.json` 会撒谎**：进程被杀后它可能长时间停留在 `state: running`。
   → 可靠的存活信号是**最新 `DONE.json` 的时间戳**（`watch_progress.ps1` 就是按这个判 STALLED）。
6. **设备偏离（本轮引入，必须写进正文）**：剩余 VisA 单元已切到 `--device cuda` + `.venv-anomalyclip`（torch 2.0.0），而已完成的 75 个 VisA 与 180 个 MVTec 是 `cpu` + torch 2.12.1。记录在 `gen/p1_matrix/DEVICE_DEVIATION.json`。
   支持它的是数值等价证据：`probe_device_parity.py` 实测同解释器下 CPU vs GPU，`grid/labels/method_names/pixel_masks/sample_ids/stride` **逐位相同**，`pixel_scores` max\|Δ\|=5.2e-07，**13 个方法 pixel AP 最大差 6.5e-07**（比要报告的效应 ~5e-03 低 4 个数量级）。
   **残余风险**：torch 2.12.1 vs 2.0.0 的差异**未单独测过**。
7. **`run_matrix.py` 遇到第一个失败单元就整批停下**（`state=needs_attention`）。排查顺序：`FAILURES.json` → `logs/<dataset>_s<seed>_k<shot>_<cat>.log`。
8. **`export_k8_cache.py` 的 `hist_dir` 原先不做存在性检查**，对 seeds 3..7 会返回不存在的路径。已修（对所有候选加 `is_dir()`）。
9. **内存**：并发 4 个 VisA 单元会 OOM（单分支归一化行 980 MB）。CPU 并发上限 2，GPU 3 路 显存够但主机 RAM 仍需节流。
10. **PowerShell 多行括号表达式会把 `+` 写在行首导致整脚本无法解析**。`PowerShell` 在括号内遇到"已完整的表达式 + 换行"会当作语句结束，于是下一行的 `+ '...'` 变成非法语句，
    报错是 `Missing closing ')' in expression` / `Unexpected token '+'`。**本轮就让 `run_analysis.ps1` 因此完全无法启动**（阶段 0 都没跑）。
    → 写法必须是 `('第一段 ' +` 换行 `'第二段')`，即 **`+` 留在上一行行尾**。
    → **开工前先做语法自检**（不执行，只解析）：

```powershell
foreach($f in @('run_analysis.ps1','run_visa_parallel.ps1','run_matrices.ps1','run_d_btad.ps1','watch_progress.ps1')){
  $errs=@(); $tokens=@()
  [void][System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path "scripts\limitation_closure_20260915\$f").Path, [ref]$tokens, [ref]$errs)
  "{0,-24} parse errors = {1}" -f $f, $errs.Count
  $errs | ForEach-Object { "    line {0}: {1}" -f $_.Extent.StartLineNumber, $_.Message }
}
```

（2026-09-17 20:50 复核：五个脚本 parse errors 均为 0。）

---

## 6. 本轮产出的关键数值（正文要用）

**VE.5 四分支交互并列表**（stride-8 像素 AP，Bonferroni 98.75%，scope: seed {0,1} × K {1,4}）

| 数据集 | 交互 | S (DINOv2-S) | D (WRN50-2) | E1 (deiT-S/8) | E2 (ConvNeXt-T) |
|---|---|---|---|---|---|
| MPDD | I_TRI | +0.00695 ✓ | +0.01020 ✓ | +0.00811 ✓ | −0.00018 ✗ |
| MPDD | I_BAL | +0.00547 ✓ | +0.00686 ✓ | +0.00488 ✗ | +0.00076 ✗ |
| BTAD | I_TRI | +0.00029 ✗ | +0.00631 ✓ | +0.00583 ✓ | +0.00278 ✓ |
| BTAD | I_BAL | −0.00052 ✗ | +0.00524 ✓ | +0.00224 ✗ | +0.00422 ✓ |

（✓ = 98.75% 区间排除零）

**配对差值 vs S**（同重采样流，逐 replicate 相减）

| 数据集 | 对比 | D−S | E1−S | E2−S |
|---|---|---|---|---|
| MPDD | I_TRI | +0.00326 ✗ | +0.00116 ✗ | **−0.00712 ✓** |
| BTAD | I_TRI | **+0.00603 ✓** | **+0.00555 ✓** | +0.00249 ✗ |
| BTAD | I_BAL | **+0.00576 ✓** | +0.00276 ✗ | **+0.00474 ✓** |

⇒ 可支持的结论：**交互不是 DINOv2-S 配对独有**；三个不同家族的额外分支都在 BTAD 上把 J/L 差距抬到排除零；而**方向随编码器而变**（MPDD 上 E2 显著低于 S）。这正是"新增分支的价值"与"该价值对匹配规则的依赖"是两件事的证据。

**VD.2 漂移 vs 支持集效应**（`QUERY_DRIFT.json`）

| 单元 | 原始特征漂移 max\|Δ\| | 对最近邻距离的影响 | 换支持集的影响 | 比值 |
|---|---|---|---|---|
| mpdd/bracket_black B | 5.0e-04 | 3.93e-07 | 6.83e-02 | 5.8e-06 |
| mpdd/bracket_black C | 2.0e-04 | 1.15e-07 | 1.41e-02 | 8.2e-06 |
| btad/01 B | 1.4e-03 | 2.92e-07 | 1.96e-02 | 1.5e-05 |
| btad/01 C | 8.3e-04 | 1.14e-07 | 7.54e-03 | 1.5e-05 |

⇒ 原始漂移看着不小（BTAD 上 2.7e-3），但**对真正进入交互的那个量（最近邻余弦距离）的影响比换支持集小约 4 个数量级**，因此种子 3..7 共用一份 query 编码是站得住的。
**注意**：计划 VD.2 原文写的是"漂移要小于交互的跨种子标准差"，那是**量纲不匹配**（特征 vs AP）。已改成上面这个同量纲判据，正文引用请用这个版本。

**设备性能对照**（`_gpu_probe/`）

| 单元 | CPU | GPU | 倍数 | 显存峰值 |
|---|---|---|---|---|
| candle（小，32×35） | 107.3 s | 60.5 s | 1.77× | 2430 MiB |
| pcb3（大，32×52） | 154.6 s | 64.2 s | 2.41× | 2600 MiB |
| 3 路并发 K=8（pcb3+pcb4+pipe_fryum） | ~2500 s（推算顺序） | **159 s** | **~8×** | 3331 MiB |

---

## 7. 必须写进正文、不能含糊的边界（计划 §6 原文）

1. **不存在"未碰过的确认集"**（除非做了 §4.1）。MVTec/VisA 给的是**泛化证据**，不是确认；VisA 对 C 分支是域内。
2. **"学习保证"不可得**。工作流 B 能量化"画布对应有多可靠"并证明结论不依赖该选择，但**不能**证明画布位置描述同一物体部位。
3. **事后扩展不是预指定**。E1/E2 只能作探索性；唯一还能保留"预指定"性质的是工作流 D 的支持集方差分析。
4. **BTAD-03 修正几何的复算不是逐位可复现**（CUDA `torch.mm` 非确定性，只能到 float32 舍入级 ~1.8e-05，见 `S0C_SUMMARY.json` 的 `all_replicates_bit_identical: false`）。

---

## 8. 夜间执行建议顺序与时间预算

| 顺序 | 任务 | 预计 | 备注 |
|---|---|---|---|
| 1 | 重启 VisA 派发器（§3.1） | 45 min | 与 2 并行；GPU |
| 2 | `run_analysis.ps1`（§3.3，先注释掉阶段 2） | 60–90 min | 等 VisA 完成后自动接 3a–3c、4；CPU |
| 3 | d3（§3.2） | 100 min（并行化可到 25 min） | **可与 1、2 并行**（CPU，注意 16 GB RAM） |
| 4 | 共同有效区域（§3.4） | 30 min | 需先确认 `s8_common_region.py` 的 `CATS` |
| 5 | Swin-T（§4.3，成本最低的新增项） | 40 min | GPU |
| 6 | 工作流 F 确认集（§4.1） | 3–6 h | **最大科学缺口**，与其它不冲突时优先 |
| 7 | 论文正文落地（§3.5） | — | 依赖 1–4 的数值 |

**监控命令**（一屏看全部）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\watch_progress.ps1
```

显示 D mpdd/btad 与 C VisA 的 done/总数、当前单元、最新 `DONE.json` 年龄、ETA、**STALLED 告警**，VisA 派发器计数，分析链阶段与 6 个产物是否落地。

**注意**：`watch_progress.ps1` 里 C VisA 那一行若显示 `(parallel dispatcher active)`，表示该批次由派发器托管，不看批次自带的 `STATUS.json`。

---

## 9. 相关文件索引

| 用途 | 路径 |
|---|---|
| 权威计划 | `.trae/documents/remaining_experiments_full_closure_plan_20260915.md` |
| 收口脚本 | `scripts/limitation_closure_20260915/`（`run_visa_parallel.ps1`、`run_analysis.ps1`、`run_d_btad.ps1`、`watch_progress.ps1`、`d1_verify_manifest.py`、`d2_canonical_guard.py`、`d2b_query_drift.py`、`d3_seed_variance.py`、`c5_generalization_interactions.py`、`probe_device_parity.py`） |
| 主研究脚本 | `scripts/unified_fusion_paper_support_v1/`（`export_k8_cache.py`、`engine_v2.py`、`run_matrix.py`、`run_fullpixel.py`、`stats_v2.py`、`analyze_conditions.py`） |
| 论文实验目录 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/` |
| 主研究实验目录 | `experiments/dynamic_fusion/unified_fusion_paper_support_20260913/` |
| 泛化实验目录 | `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/` |
| 种子扩展目录 | `experiments/dynamic_fusion/seeds_extension_20260917/` |
| 主 canonical 缓存 | `outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/` |
| 泛化 canonical 缓存 | `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/canonical/` |
| 代码追加改动记录 | `outputs/dynamic_fusion/generalization_mvtec_visa_20260915/CODE_AMENDMENT.md` |
| 设备偏离记录 | `experiments/dynamic_fusion/generalization_mvtec_visa_20260915/p1_matrix/DEVICE_DEVIATION.json` |
| E2 权重溯源修补 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_extra_encoders/E2/E2_BRANCH_SPEC.json`（`weights_sha256` 原为 null，已解析 HF 快照 blob 并加注 `weights_sha256_resolved_utc`） |

---

# 附录 A：论文大纲逐项核对（2026-09-17 追加）

核对对象：`docs/PAPER_OUTLINE_TEACHER_REVIEW_20260914_CN.md` 与
`docs/paper_outline_teacher_review_20260914/新主题论文详细提纲_导师审阅版_20260914_更新版.docx`，
以及已生成的 `docs/manuscript_reference_matching_20260914/English_Manuscript_Source.md`。

## A.1 大纲「图表与补充材料安排」对照

| 编号 | 大纲要求 | 现有产物 | 状态 |
|---|---|---|---|
| 图 1 | 多图支持建库/查询/真实输出（§3.2） | `fig1_framework.png` | 有，但需随新增分支与数据集更新 |
| 图 2 | 同一查询位置的 J/L 候选参考与约束差（§3.3） | `fig2_matching.png` | 有 |
| 图 3 | A1/DUP/TRI/BAL 权重与替换路径（§3.4） | `fig3_constructions.png` | 有，但**槽位需加 E1/E2** |
| 图 4 | 表征效应与直接交互区间（§4.2.3–4.2.4） | `fig4_effects_interaction.png` | 有 4(a)(b)(c)，**必须重绘**：要并入 E1/E2 与四个数据集 |
| 图 5 | K 曲线、类别或留一类稳定性（§4.2.5） | `fig5_budget_category.png` | 有，需并入 MVTec/VisA 与 seeds 3..7 |
| 图 6 | ≥5 例局部放大、热图与轮廓（§4.2.6） | `qualitative_improvements_part1/2.png`、`qualitative_mpdd_matching_degradations.png` | 有（manifest 在 git 中为已修改态） |
| 图 7 | **≥3 样本的正式方法对比与 GT** | **未见对应产物** | **缺** |
| 图 8 | VRAM 与推理速度 | `fig8_resources.png` | 有，**但见 A.3 返工风险 1** |
| 图 S1–S3 | 编码器几何 / 真模块消融 / 额外案例 | 仅 `figS1_encoders.png` | **S2、S3 未见** |
| 表 1 | 模型配置与固定条件（§3.7） | 需核对 | 需更新为 5 编码器 × 4 数据集 |
| 表 2 | 数据角色、K、seed、指标、评价版本 | 需核对 | 需写入 mvtec/visa 的新角色措辞 |
| 表 3 | 核心构造全像素性能 + 区间口径单列 | 部分（S/D） | 需并入 C 的 fullpixel 与四数据集 |
| 表 4 | 成熟基线配置与统一评价结果 | 需核对 | 待确认 |
| 表 S1–S4 | 全条件 / 缺失消融 / 文献差异 / 版本清单 | 需核对 | 待确认 |

## A.2 手稿正文的证据缺口

手稿 §4.2 目前只覆盖 **S 与 D**。以下每一处都是正文里"写死的未完成句"，本轮实验正好补上，但**还没有写进去**：

| 手稿原文位置 | 原文（要点） | 现在有什么 | 待办 |
|---|---|---|---|
| §4.2.4 末 | "It does not establish the same result for **arbitrary convolutional backbones** or for **additional datasets**." | E1/E2 三编码器表（VE.5）；C 的四数据集表（C5） | 新增小节 + 改写这句 |
| §4.2.3 / §4.2.4 | 只有 S 效应与 D 扩展；无 E1/E2 | `encoder_comparison_three.csv`、`encoder_vs_S_difference.csv` | 新增"第三/第四编码器"小节与表 |
| 全文 | 无支持集抽样不确定性 | VD.4（seeds 3..7 方差分解） | 新增小节 |
| §4.1.5 几何与评价一致性 | 只有 BTAD-03 的粗网格说明 | 工作流 A（细网格区间，VA.1–VA.4） | 更新该节 |
| 全文 | 无"画布对应可靠性" | 工作流 B1（审计）+ B2（学习式替换） | 新增小节（注意 AD-9 的措辞边界） |
| 摘要 / §5 结论 | 基于旧证据 | 全部新结果 | 重写 |
| §Data and Code Availability | 明写公开复现包位置**尚未确定** | 无 | 见 D.2 |

大纲自身的「当前证据状态」表也已过期：其中"直接交互 = 检查时尚无完整交互结果表"**已经不成立**（现有 S/D/C/E 四套交互表）；"新颖性 = 完整原文对照待补"**仍成立**（见 D.3）。

---

# 附录 B：全项目剩余工作（含论文以外的部分）

## B.1 实验类（阻塞论文数值）

已在正文 §3、§4 逐项给出命令，此处只列清单：
① VisA 剩余 69 单元；② d3 方差分解；③ C 的统计与 C5；④ 跨方法共同有效区域；⑤ 工作流 F（确认集）；
⑥ 工作流 G（BTAD-03 纳入 D）；⑦ 工作流 H（Swin-T）。

## B.2 论文写作类

1. 按 A.2 补齐 5 个新小节（第三/第四编码器、四数据集、支持集方差、细网格几何、画布对应审计）。
2. 重写摘要与结论，并把"未建立"的措辞按新证据改写（**不能**把泛化证据写成确认）。
3. 中文件（`中文对照内容.md`、`论文精读讲解.md`）与两个 `.docx` 需同步重生成。
4. 更新大纲的「当前证据状态」表后再送导师审阅。

## B.3 图表类

1. 重绘图 3（加 E1/E2 槽位）、图 4（并入 E1/E2 与四数据集）、图 5（并入 MVTec/VisA 与 8 seeds）。
2. **补图 7**（≥3 样本正式方法对比 + GT）。
3. **补图 S2、S3**（真模块消融、额外案例）。
4. 图 8 见返工风险 1。
5. 核对 `docs/figures_reference_matching_20260914/FIGURE_BINDING.md` 与手稿里 `{{figure:...}}` / `{{table:...}}` 占位符的一致性。

## B.4 非论文／工程类

| 项 | 现状 | 待办 |
|---|---|---|
| **git 版本控制** | `git status` 显示 **43 项未提交**：新手稿与图集为 untracked，`.trae/` untracked，7 个冻结脚本为 modified | 提交并打 tag；否则冻结脚本的追加改动无法回溯 |
| **公开复现包位置** | 手稿明写尚未确定 | 选定 Zenodo/GitHub release，生成 `VERSIONED_EVIDENCE.sha256`（模板见 `docs/submission_reproducibility_20260826/`） |
| **文献全文对照** | 大纲「新颖性」栏标记"完整原文对照待补" | 逐条比对关键一手文献全文，明确不使用 "first" |
| **参考文献表** | `docs/introduction_research_20260825/references_latest_20260826.bib` 为旧主题 | 更新到新主题，并补新数据集/编码器引用 |
| **环境快照** | `docs/environment_matrix.md` 未覆盖本轮 | 补 `.venv-anomalyclip`=torch 2.0.0+cu118 与默认 python=2.12.1+cpu 的双环境、`HF_ENDPOINT=https://hf-mirror.com`、E2 的 HF 权重 sha256 |
| **冻结脚本清单与哈希** | `run_matrix.py` 记录了它依赖的三个源文件哈希；`export_k8_cache.py`、`build_support_manifest.py` 不在内 | 补一份冻结脚本 清单+哈希（用本轮改动后的版本），否则"冻结"不可审计 |
| **scratch 清理** | `_gpu_probe/`、`_s4_dreg_smoke/`、`_s4_e1_smoke/`、`_s4_e2_smoke/`、`_maskfix_smoke/`、`_smoke_canonical/` | 决定保留（作证据）还是删除后重生成 |
| **canonical 只增不改复核** | 本轮新增 `*_s3..s7_k8`（30 个目录）与 `btad_s2_k8`，`CANONICAL_GUARD.json` 已证未改动旧文件 | 再跑一次 `d2_canonical_guard.py verify` 覆盖 btad_s2 的补充导出 |

---

# 附录 C：返工风险清单（**这些必须在动笔前定，否则写完还要回头重跑实验**）

按"若不现在处理、后面必须重跑"的严重程度排序。

### C.1 【必须现在决定】E 的 K 范围是否要扩到 K=2/8

`05_extra_encoders/E1|E2` 的 SPEC 明确把 **K2、K8、seed 2 列为 out_of_scope**，只做了 seed {0,1} × K {1,4}。而 C/D 的矩阵包含 K=1/2/4/8、seeds 0..7。

→ **如果正文或审稿要求 E1/E2 也报 K=8 或与 C/D 同 scope，必须重跑 E（GPU ~1 h + 统计）**。
→ 现在就要定：E 是否只作"受限 scope 的探索性对照"（则无需重跑，但正文必须写清 scope 差异），否则立刻扩 scope。

### C.2 【必须现在决定】确认集只能"提前冻结"

工作流 F 的确认集必须在本项目看过其结果**之前**冻结规格并一次性打开。越晚做，越会被质疑为事后解释。**这是唯一无法事后补的项**。若时间不够，正文必须明确写"本文给不出确认集"，不能用泛化证据顶替。

### C.3 【必须现在决定】图 8（速度/显存）与设备混合

VisA 单元现在是**混合设备**：前 75 个 `device=cpu` + torch 2.12.1，其余 `device=cuda` + torch 2.0.0。
→ 若图 8 或"实现与计算环境"节要报推理速度/显存，**VisA 的计时不可用**。
→ 处理方式（二选一，现在定）：
  (a) 在**单一设备**上重测一组代表单元专供图 8（推荐：`.venv-anomalyclip` 下 cpu 与 cuda 各测同组，我本轮已有 `_gpu_probe` 的对照脚本可直接复用）；
  (b) 图 8 明确限定在 MPDD/BTAD/MVTec，VisA 不参与速度/显存结论。

### C.4 【建议现在补】跨方法共同有效区域（三评价网格的第三项）

MVTec/VisA 从未跑过该口径。若正文或表 3 要报"区间口径单列 / 共同有效区域"，**现在补**；否则后面补要重跑整套评价（不必重跑矩阵，但需要时间与一致性声明）。

### C.5 【建议现在补】BTAD-03 纳入 D 的跨种子方差（工作流 G）

当前 D 的 BTAD 只有 01/02。若审稿要求 BTAD 全 3 类，需要 G。成本低（生成 seeds 3..7 的 faithful GT + 在独立 corrected 根上重算 BTAD-03），**现在做比后面做省事**，因为矩阵与统计的脚手架都在。

### C.6 【需要确认，可能不算返工】图像级指标与 AUPRO

- 图像级 AP/AUROC：矩阵的 `evaluation_scores.npz` 里已存 `image_scores`，`stats_v2` 的口径可后补，**大概率不必重跑矩阵**。需确认 MVTec/VisA 是否已随 C 的统计产出。
- AUPRO：矩阵用 `include_aupro=False`。若审稿人要 AUPRO，需**重跑评价阶段**（不必重跑矩阵）。建议现在就定要不要。

### C.7 【现在统一】数据集角色措辞

旧稿沿用 `holdout`；新政策是 `mpdd=development`、`btad=external_frozen_validation`、`mvtec=external_frozen_validation`、`visa=in_domain_frozen_validation`。冻结的 mpdd/btad npz 里仍带 `holdout` 字样（不改动冻结产物），正文必须统一到新措辞并说明历史遗留。

### C.8 一句话总结

**C.1（E 的 K 范围）、C.2（确认集）、C.3（图 8 的设备口径）是三条"现在不定就必然返工"的**；
C.4、C.5 是"现在做成本最低"；C.6、C.7 是"现在确认即可"。

---

# 附录 D：夜间无人值守执行方案（2026-09-18 00:0x 追加）

本附录记录**本文档冻结之后**新增的执行层，以及今天核对时发现、必须写进交接的三处更正与六个坑。

## D.1 新增与改动的文件

| 文件 | 类型 | 作用 |
|---|---|---|
| `scripts/limitation_closure_20260915/night_run_20260917.ps1` | 新增 | 整夜编排：preflight → VisA →（链 ∥ BTAD-03）→ E3+S10 → 限时等链 → d3 → 收尾报告 |
| `scripts/limitation_closure_20260915/night_watch.ps1` | 新增 | 一屏只读监控（阶段状态、单元计数、`DONE.json` 陈旧告警、产物核对） |
| `scripts/limitation_closure_20260915/night_report.py` | 新增 | 由 `NIGHT_RUN_STATUS.json` 生成 `NIGHT_RUN_REPORT_CN.md`（中文报告，Python 按 UTF-8 读源码） |
| `scripts/representation_matching_interaction_20260914/s4_extra_encoders.py` | 追加 | 新增 **E3 = Swin-Tiny**（`BRANCHES['E3']` + `EncoderE3` + `ENCODER_CLASSES`）；规格仍由 `write_spec()` 在任何特征之前写出，VE.1 时序门自动满足 |
| `scripts/representation_matching_interaction_20260914/s10_encoder_comparison.py` | 追加 | 五编码器表：`EXTRA_BRANCHES` 常量 + `CONTRASTS/ENCODER_LABEL/ENCODER_STATUS` 增加 E3 |
| `scripts/limitation_closure_20260915/d3_seed_variance.py` | 修改 | `CATS["btad"]` 由 `["01","02"]` → `["01","02","03"]`；报告里"03 被排除"的说明改为几何口径声明 |
| `scripts/limitation_closure_20260915/_night_20260917/` | 新增产物目录 | `NIGHT_RUN_STATUS.json`、`NIGHT_RUN_REPORT_CN.md`、`logs_night.txt`、`phase_*.log`、`RUNNING.lock` |

## D.2 对本文档的三处更正

### D.2.1 §4.2 工作流 G 的原方案在现有代码下不可实现，且对 D 而言是错的

逐行核对结论（**不是猜测**）：

- `export_k8_cache.py:239-264` 只有一种掩码规则（直接缩放到 `grid*14`），**没有** faithful / 图像等比变换选项；
- `run_matrix`/`engine_v2.py:77-87` 只有近似 C→画布映射，`regrid_correct`（`rescore_btad03.py:96-119`）**从未被引擎引用**；
- faithful GT 由 `freeze_s0.py` 生成，其种子循环写死 `for seed in (0, 1)`（`freeze_s0.py:457`，且 `main()` 无 `--seeds`）；
- `run_matrix` 评价用的掩码**只来自 B 分支的 npz**（`engine_v2.py:110-122`，形状必须恰为 `grid*14`，否则直接抛错），所以"只换 03 的几何"必须换掉整个 B 缓存。

更关键的是：D 里 seeds 0..7 的 **01/02 用的是 canonical（study）几何 + 近似 C 映射**。若按原方案只把 03 换成 rev_correct（faithful GT + 坐标正确重网格），三类宏平均就混用了**两套几何 + 两套 C 映射**，比不补更糟。

**实际做法**：给 D 补 **canonical 几何下的 BTAD-03**（8 seeds × K1/2/4/8 = 32 单元）。已实测确认 seeds 0..7 的 canonical B `03.npz` 掩码**全部为 448×588、grid 32×42**（形状守卫逐个通过），因此可以与 01/02 合并到同一口径。附带收益：d3 的 VD.3 回归会拿新 03 单元比对已发布 study 值，等于自带一致性门。

rev_correct 版本（faithful GT + 坐标正确重网格）需要新代码路径，**不影响 D 的三类结论**，留给白天；现在做的 32 个 03 单元将来是对照的另一半，不浪费。

### D.2.2 §1 / §5 坑 5：`STATUS.json` 的字段不可用于排期

`generalization_mvtec_visa_20260915/p1_matrix/STATUS.json` 当前写 `remaining_seconds: 80951`（≈22 h）与 `completed: 225`。前者是**切 GPU 之前**的旧估算（3 路 GPU 实测约 45 min），后者与真实 `DONE.json` 计数（180 + 75 = 255）不一致。**进度只信 `DONE.json` 计数与最新时间戳。**

### D.2.3 §5 坑 6：设备偏离记录自相矛盾

`p1_matrix/DEVICE_DEVIATION.json` 的 `scope` 写 "the remaining VisA units … (99 of 144 at the time of the switch)"，而同一文件 `consequence_for_the_artefact` 写 "the first **55** units were produced with device=cpu"。两处数字不一致，需确认真实 CPU/GPU 分割后再写进正文的"混合设备"声明。

## D.3 夜跑阶段与依赖（实际编排）

| 阶段 | 内容 | 依赖 | 失败后果 |
|---|---|---|---|
| 0 | 预检：解释器 / GPU / 磁盘 / canonical / Swin 权重 | — | 直接拒绝启动（不产生任何实验） |
| 1 | VisA 剩余 69 单元（GPU 3 路，**监督式**） | — | 记为 `needs_attention`；**链不再启动** |
| 2 | C 统计链（后台） | **阶段 1 必须 pass** | 阶段 5 记录退出码，不影响 3/4/6 |
| 3 | BTAD-03 矩阵 32 单元（GPU） | canonical 缓存 | d3 跳过 |
| 4 | E3 Swin-T + S10 五编码器表（GPU） | 本地 HF 权重 | 表保持 4 行 |
| 5 | 限时等链（默认 240 min 上限） | 阶段 2 已启动 | 记 `needs_attention` 并继续 |
| 6 | d3 支持集方差（CPU） | **仅阶段 3** | 记 FAILED |
| 7 | 收尾：状态 JSON + 中文报告 | — | — |

## D.4 中断硬化规则（今天新增，全部已在脚本内实现）

1. **单实例锁**：`RUNNING.lock` 记录 PID，二次启动直接拒绝（`exit 2`），避免两个派发器跑同一队列。
2. **阶段 1 是"监督"而非"等待"**：判定为停滞的条件是"**无新 `DONE.json` 超过 20 min 且日志最后一行不是 `throttled`**"（被节流是健康状态，绝不被杀），外加 240 min 硬上限。杀掉只损失在飞单元，因为队列按 `DONE.json` 重建，重启即续跑。
3. **链只在整个 VisA 完成后启动**：`run_analysis.ps1` 的设计是在自己的 stall 窗口后**照常继续**，这会在**部分 VisA 数据**上算出"成功"的统计与 C5 表。这些表要进论文，所以门放在编排层：VisA 不是 `pass`/`skipped_already_done` 就根本不启动链。
4. **E3 与 d3 不排在链后面**：链是最长的 CPU 阶段、也最可能停滞；旧版本会让停滞的链把剩余阶段一起卡到 deadline。
5. **每阶段先查自己的产物**：崩溃后重启本脚本会跳过已完成阶段（派发器、`run_matrix --resume`、`s4 --skip-existing` 同样幂等）。
6. **验证模式零副作用**：`-PreflightOnly` 不写状态文件、不取锁。

## D.5 今天新踩的坑（务必先读）

| # | 现象 | 根因与规则 |
|---|---|---|
| K1 | 编排脚本**完全无法解析**（27 个 parse error，报"缺少 )"、"意外的标记"） | **Windows PowerShell 5.1 把无 BOM 的 `.ps1` 按 ANSI/GBK 解码**，脚本里的中文被拆成坏字节 → 引号/反引号失配。**规则：`.ps1` 一律纯 ASCII**；中文交给 `night_report.py`（Python 默认按 UTF-8 读源码）。自查：`[IO.File]::ReadAllBytes($p) \| Where-Object {$_ -gt 127}` 必须为 0 |
| K2 | `night_report.py` 读状态文件报 `Unexpected UTF-8 BOM` | PowerShell 5.1 的 `Set-Content -Encoding utf8` **会写 BOM**；Python 端必须 `encoding="utf-8-sig"` |
| K3 | 监控误判"有运行在进行中"，且验证模式可能挡住真夜跑 | `-PreflightOnly` 曾经经过 `Set-Phase()` 写状态文件、留下 `finished=null`；现已改为完全不写 |
| K4 | 怕"脱离失败"（关掉终端就死） | 已实测：`Start-Process -WindowStyle Hidden` 的子进程在**发起命令返回后继续写入**（心跳 1→2 行，进程仍存活）。但 `SetThreadExecutionState` **无法覆盖"合盖即睡"**，这是唯一需要人工确认的物理条件 |
| K5 | E3 建模型时 `Input height (448) doesn't match model (224)` | 必须 `timm.create_model(..., img_size=None, strict_img_size=False)`；timm 的 Swin `features_only` 返回 **channels-last**，需 permute 回 NCHW 再插值；权重已在本地 HF 缓存，`HF_HUB_OFFLINE=1` 可完全离线（实测峰值显存 139.7 MB，448×588 → `(32,42,576)`） |
| K6 | d3 无法用 `--categories` 把 btad 限制成 03 | `d3_seed_variance.py:174-176` 是**取交集**（传 `03` 会得到空列表）；另外 `FULL_CATS = dict(CATS)` 是浅拷贝，改 `CATS` 后 `FULL_CATS` 同步变化，VD.3 不再判 "reduced scope"，会把 03 与已发布 study 值逐条比对——这正是我们要的门 |

## D.6 启动与监控

```powershell
# 启动（分离进程，启动后可以直接关闭终端）
Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',
  '<repo-root>\scripts\limitation_closure_20260915\night_run_20260917.ps1' -WindowStyle Hidden

# 只做环境预检，不启动任何实验
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\night_run_20260917.ps1 -PreflightOnly

# 监控（一屏）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\night_watch.ps1
```

可选参数：`-SkipG`、`-SkipSwinT`、`-VisAConcurrency`、`-VisAStallMinutes`、`-VisAHardCapMinutes`、`-ChainWaitMaxMinutes`、`-MaxHours`。

## D.7 早上要核对的三件事

1. `analysis_chain` 与 `d3_seed_variance` 两行的 `result`；任何 `needs_attention`/`FAILED` 先看对应的 `phase_*.log` 与 `logs_analysis.txt`。
2. d3 的 VD.3 回归：BTAD 三类下 `max_abs_delta` 应在 1e-9 量级。若远大于该值，说明 03 的口径与矩阵不是同一套，**这批数先别写进论文**。
3. E3 的 `VERIFICATION.json → VE_2_single_branch_auroc.pass` 与 `S10_SUMMARY.json` 是否已从 4 行变 5 行。

## D.8 今晚**不**覆盖的项（仍然开着）

- **C.1 E1/E2/E3 的 K 范围**（仍是 seed {0,1} × K {1,4}，K2/K8 与 seed 2 为 out_of_scope）——需你拍板是"受限 scope 探索性对照"还是补跑；
- **C.2 确认集**（工作流 F）——唯一无法事后补的项，仍未开始；
- **C.4 跨方法共同有效区域 / 图 7**：今天查明 `s8_common_region.py` 还依赖 `05_baselines/region_maps/` 下 AnomalyDINO 与 PatchCore 的**逐样本区域图**，而 MVTec/VisA **没有**这类产物（`s8_common_region.py:182-208`）。所以它不是"加个 `CATS`"，而是要先在统一画布上补一遍原生基线导出；图 7 与它是同一件底层工作；
- **图 6/图 7 字号 < 11 pt**（违反老师 F09/O5 口径）需重排布；
- **BTAD-03 的 rev_correct 八种子版本**（需新代码路径）；
## D.9 夜跑实测对本文档的修正（2026-09-18 上午追加）

夜跑实际执行后，以下**数值与判断被实测推翻或修正**，优先级高于前文：

### D.9.1 【重要】d3 的真实成本是"约 2 天"，不是 100 分钟（推翻 §3.2）

- **实测**：d3 于 04:40 启动，**07:15** 才打印第一行
  `[D3] mpdd s0 I_TRI: conditions=24 (units visited 24/288)` → 24 单元 ≈ 2 h 35 min →
  **单单元约 6.5 min（MPDD）**；BTAD-03（441 图 ×32×42）约为其 7 倍。
- **代码依据**：`scripts/representation_matching_interaction_20260914/s3_new_encoder.py:513-547`
  每个副本要 gather + 两次 `reduceat` + `weighted_ap` 的多次 cumsum，长度等于**池化像素数**
  （MPDD≈78k、BTAD-03≈593k），且对 13 个方法各做一遍 × 1000 副本。
- **推算**：288 单元（MPDD 192 + BTAD 96）≈ **40–55 小时**。§3.2 的"单进程约 100 min"应由小 scope 外推而来，**不可再引用**。
- **d3 无部分产物**：`d3_seed_variance.py:225` 只在全部循环结束后才写 `interaction_by_seed.csv`，
  中途中断 = 全部丢失；需要"连续开机两天"。
- **三个选项**（需人决定）：①就按现实现跑两天；②换 E1 的快速估计器并加"同单元逐副本对齐到 1e-9"的可比性门（预计 1–2 h）；
  ③缩减 scope（改口径，正文需同步改写）。

### D.9.2 stats_v2 的真实成本：单条件 2.5 h+，24 条件共 8–16 h（修正 §3.3 的"3a–3c 60–90 min"）

- **实测**（用 `stats_v2` 自身函数计时）：`build_structure` 33 s + **单副本 9.14 s** × 1000 ≈ **153 min/条件（mvtec，15 类）**。
- 已按 seed 拆成 3 组并行（零科学改动，见 `_night_20260917/MANUAL_INTERVENTIONS.md` 的 I-4），
  预计 9-18 下午到傍晚出 `p1_statistics`；之后**必须重跑** `analyze_conditions.py` 与
  `c5_generalization_interactions.py`（链里那两步因为我中断 stats 而失败）。
- **收尾安全网**：三组结束后校验 `bootstrap_samples.npz` 是否含 24 条件 × 13 方法 × 4 指标的全部键。

### D.9.3 新踩的坑（续 D.5，编号接 K6 之后）

| # | 现象 | 根因与规则 |
|---|---|---|
| K7 | 统计链 `run_fullpixel_mvtec_visa` 报 `FileNotFoundError: canonical/B/mvtec_s0_k8/bottle.npz` | `run_fullpixel.py:34` 的 `CANONICAL` 是硬编码常量，**不读 `FUSION_CANONICAL_ROOT`**（`engine_v2.py:33-36` 读）。已改为同样的环境变量约定并验证"默认路径不变"，不影响已发布结果。**凡是要跨数据集复用的脚本，都要检查这一点。** |
| K8 | 我的改动写入后"消失"，grep 发现旧内容仍在 | **同一文件的两处编辑若在同一批并行提交，后一次会基于陈旧快照覆盖前一次**；工具两次都回"成功"。规则：**同一文件必须串行单条编辑**，改完用 grep 或行为测试确认落地。本案受害文件：`run_fullpixel.py`（另 5 个文件复查后完好）。 |
| K9 | E3 阶段直接失败：`can't open file ...\experiments\...\s4_extra_encoders.py` | 编排脚本用 `$new`（experiments 产物目录）拼了**脚本**路径；脚本实际在 `scripts/representation_matching_interaction_20260914/`。**preflight 只查了数据与权重，没查自己要调用的脚本是否存在** → 应加脚本存在性检查。 |
| K10 | fullpixel 两个进程被 `_ArrayMemoryError` 打死（差 136–196 MiB） | 8 个 stats worker（约 6.4 GB）+ E3 + d3 + **3 个 fullpixel**（各 1–2 GB）在 15.8 GB 机器上超配。规则：**并行度必须按"峰值之和"预算**，fullpixel 单进程最稳；`run_fullpixel.py` 有逐单元 CSV 断点，随时可 `--resume`。 |
| K11 | E3 的特征与打分早已完成，但 `E3_SUMMARY.json` 迟迟不出 | s4 在特征/打分之后还要跑一遍**同一套昂贵估计器**的 replicate 阶段（`[S3] replicates ...`），48 单元也可能要数小时；`VERIFICATION.json` 会**先**落地（可提前看 VE.2 是否通过）。 |

### D.9.4 夜跑的实际结论（与本附录前文对照）

- ✅ VisA 144/144（62 min，3 路 GPU）；✅ BTAD-03 矩阵 32/32（workflow G 的矩阵部分）；
  ✅ E3 特征/打分完成且 **VE.2 通过**（48 单元，min AUROC 0.9062、mean 0.9518）；✅ C 矩阵 324/324。
- ⏳ fullpixel 275/324（单进程续跑）；⏳ stats_v2 两组运行中；⏳ E3 的 summary 与 S10 五编码器表。
- ⛔ d3（D 支持集方差）：按当前实现需 40–55 h，**未完成**。
- 全部人工干预与实测证据：`scripts/limitation_closure_20260915/_night_20260917/MANUAL_INTERVENTIONS.md`
  （I-1 … I-7，含每条的现象、根因、处置、验证方式）。

---

# 附录 D：论文「D 版本」的完成状态、两条概念澄清、C.1/C.3 的可执行方案（2026-09-17 补）

## D.1 论文的 D 扩展（TRI_D / BAL_D）**已完成，且已进手稿**

先划掉一个可能的重复劳动：这一项**不是待办**。

| 项 | 内容 |
|---|---|
| 脚本 | `scripts/representation_matching_interaction_20260914/s3_new_encoder.py` |
| 范围 | MPDD 6 类 + BTAD 3 类 × seed {0,1} × K {1,4} → **36 单元**，180 个新方法条件 |
| 方法 | `D`、`TRI_D_J/L`、`BAL_D_J/L`；`A1`/`DUP` 在同一次运行内重算作对照 |
| 预指定性质 | **是**（`D_BRANCH_SPEC.json` 冻结于任何 D 结果之前；当时 S 已知、D 未知）。与后来 E1/E2 的"事后探索性"不同 |
| 产物 | `experiments/dynamic_fusion/representation_matching_interaction_20260914/04_new_encoder/` |

**四个 D 交互（stride-8，98.75% 校正，全部排除零）**

| 数据集 | 交互 | point | bootstrap mean | 98.75% 区间 | 排除零 |
|---|---|---|---|---|---|
| MPDD | I_TRI_D | +0.00974 | +0.01020 | [+0.00514, +0.01689] | 是 |
| MPDD | I_BAL_D | +0.00628 | +0.00686 | [+0.00162, +0.01394] | 是 |
| BTAD（corrected） | I_TRI_D | +0.00622 | +0.00631 | [+0.00298, +0.01003] | 是 |
| BTAD（corrected） | I_BAL_D | +0.00501 | +0.00524 | [+0.00188, +0.00995] | 是 |

（另有 btad `study` 两行作敏感性检查，同样排除零。）

**配对编码器差值 D − S**（`encoder_difference.csv`，工作流 S7；S 被限制到与 D 相同的 seed/K）

| 数据集 | 对比 | 差值 | 98.75% 区间 | 排除零 |
|---|---|---|---|---|
| BTAD | I_TRI_D − I_TRI | **+0.00603** | [+0.00255, +0.00945] | **是** |
| BTAD | I_BAL_D − I_BAL | **+0.00576** | [+0.00204, +0.01060] | **是** |
| MPDD | I_TRI_D − I_TRI | +0.00326 | [−0.00296, +0.01118] | 否 |
| MPDD | I_BAL_D − I_BAL | +0.00139 | [−0.00372, +0.00806] | 否 |

⇒ 可支持："BTAD 上存在编码器依赖（D 的交互显著大于 S）"；**不支持**"MPDD 上两者等价"（只是分辨不出）。

**全像素敏感性**（S6）：`fullpixel_new_encoder.csv`、`interaction_fullpixel_new_encoder.csv`，方向与 stride-8 一致。

**手稿坐标**：`English_Manuscript_Source.md` §4.2.4 已含 **Table 8**（D 全像素）、**Table 9**（四个 D 交互）、**Table 10**（D−S 差值），并保留了正确的边界句：
> "It does not establish the same result for arbitrary convolutional backbones or for additional datasets."

这句话的前半段已由 E1/E2（3 个家族）与 C（4 个数据集）补上，**但尚未写进正文**（见附录 A.2）。

## D.2 两条容易被弄反的概念——写作/讲解时**不要"改错"**

### D.2.1 「BAL − A1 同时改变了权重和表征」是**错的**

直觉上 `A1 = B(1/2)+C(1/2)` 与 `BAL = B(1/4)+S(1/4)+C(1/2)` 看起来权重变了。但归档的**逐单元不变量**给出了数值恒等（`p1_matrix/units/*/invariants.json`）：

```
"duplicate_matches_weighted_pair": { "max_abs_error": 0.0, "pass": true }   ← DUP ≡ B(2/3)+C(1/3)
"balanced_duplicate_matches_A1":   { "max_abs_error": 0.0, "pass": true }   ← DUP_BAL ≡ A1
```

即 $B(\tfrac14)+B_{copy}(\tfrac14)+C(\tfrac12)\equiv B(\tfrac12)+C(\tfrac12)=A_1$（因为 $B_{copy}$ 就是 $B$，两规则下都合并）。所以把 A1 也写成三槽位后：

| | 槽位 1 | 槽位 2 | 槽位 3 | 第二槽位内容 |
|---|---|---|---|---|
| `A1` ≡ `DUP_BAL` | B 1/4 | **Bcopy** 1/4 | C 1/2 | B 的副本 |
| `BAL` | B 1/4 | **S** 1/4 | C 1/2 | 真的 S |
| `DUP` | B 1/3 | **Bcopy** 1/3 | C 1/3 | B 的副本 |
| `TRI` | B 1/3 | **S** 1/3 | C 1/3 | 真的 S |

**槽位分配逐项相同、C 权重相同，只有第二槽位的内容不同。** TRI−DUP 与 BAL−A1 是同一类对照；BAL 的对照恰好**就是 A1 自己**（不是设计漏了对照，而是那个对照在构造上坍缩成了 A1）。

B 的**有效权重**确实从 1/2 降到 1/4 —— 但这与"新表征占掉一个槽位"是同一件事的两面（总预算守恒，加分支必然从某处挪权重），TRI−DUP 里同样从 2/3 降到 1/3，幅度更大。**不是两个独立变动。**

### D.2.2 待修的文档措辞 bug

`docs/manuscript_reference_matching_20260914/论文精读讲解.md` 第 105–108 行的表里：

> `| **BAL − A1** | 另一种分配方式下的表征效应（互补检验） |`

这里的"另一种分配方式"本意是**"与 TRI 那一组不同的分配"**（TRI 用 1/3-1/3-1/3，BAL 用 1/4-1/4-1/2），但字面能被读成"这次对比里分配方式变了"——**恰好读反**。建议改为：

> `| **BAL − A1** | 在**另一组**槽位分配（C 保 1/2）下做同样的槽位替换 → **换分配后的互补检验** |`

同表 TRI 行也建议点明坍缩关系：

> `| **TRI − DUP** | 槽位和权重都一样，只剩"换了表征" → **纯表征效应**（BAL 的同型对照是 A1，因 B_copy ≡ B 而写成 A1） |`

> 这两处属**讲解文档**，改它不影响任何实验产物与手稿数字。

## D.3 把 C.1 / C.3 从"待决定"变成可执行方案

### D.3.1 C.1：E1/E2 的 scope 扩不扩（**动笔前必须二选一**）

现状：`05_extra_encoders/E1|E2` 的 SPEC 把 **K2、K8、seed 2** 列入 `out_of_scope`，实际只跑了 seed {0,1} × K {1,4}（与论文 D 同 scope）。

**路线 1（推荐先做）：保持受限 scope，不重跑。**
- 成本 **0**。
- 正文必须明写：E1/E2 的 scope 是 seed{0,1}×K{1,4}，与预指定的 D 扩展**同 scope**；"随 K 变化"的结论只归给 S（K 1..8）与 C 的曲线。
- 残余风险：审稿人要求 E 也报 K 曲线。**这是可接受的**，因为 E 本来就定位为事后探索性。
- 现有数值已足够支撑"正交互不是 DINOv2-S 独有"这一条（BTAD 上 D/E1/E2 都对 S 排除零）。

**路线 2：扩到 K {1,2,4,8}。**
- 需要改 `scripts/representation_matching_interaction_20260914/s4_extra_encoders.py` 的 `SHOTS`，再重跑 E1/E2。
- 单元数 36 → 72（seed{0,1}×K{1,2,4,8}）。成本估：GPU 约 1–1.5 h（E1/E2 的 query 编码每类只做一次，K 只增参考数）+ 统计约 20 min。
- **纪律要求**：必须**新写一份 SPEC**、把 `out_of_scope` 里的 K2/K8 移除，并注明这是 scope 扩展（保持"规格先于结果"）。**旧 SPEC 一旦被覆盖，原来的"预指定"性质就没了**——所以这条只能在**动笔前**决定。
- 若要再对齐 C 的 seeds 0..2，再加一轮（成本约 +50%）。
- 命令骨架（与已有用法一致）：

```powershell
# 1) 先改 SHOTS，并新建 SPEC（不要覆盖旧 SPEC）
# 2) 重跑两个分支
foreach($b in @('E1','E2')){
  .venv-anomalyclip\Scripts\python.exe -u scripts\representation_matching_interaction_20260914\s4_extra_encoders.py `
    --branch $b --device cuda --workers 4
}
# 3) 重建并列表
.venv-anomalyclip\Scripts\python.exe -u scripts\representation_matching_interaction_20260914\s10_encoder_comparison.py
```

### D.3.2 C.3：图 8（速度/显存）的设备口径

现状：VisA 前 75 个单元是 `device=cpu` + torch 2.12.1，其余是 `device=cuda` + torch 2.0.0（`p1_matrix/DEVICE_DEVIATION.json`）。**VisA 的计时不能直接用于速度/显存图。**

**路线 (a)（推荐）：单设备重测一组代表单元专供图 8。**
- 复用本轮已有的对照脚本与单元集：`scripts/limitation_closure_20260915/probe_device_parity.py` + `_gpu_probe/`。
- 做法：在 `.venv-anomalyclip` 下对**同一组**代表单元各跑一遍 `--device cpu` 与 `--device cuda`，记录 wall time 与显存峰值。
- 成本 **约 10 min**（本轮实测：candle 108/60 s、pcb3 155/64 s、3 路并发 K=8 共 159 s / 峰值 3331 MiB）。
- 好处：图 8 能覆盖四个数据集，且口径干净、可复核。
- 注意：这样得到的是"同设备内的相对成本"，与旧图 8（MPDD/BTAD 的历史数字）**口径不同**，不能直接拼在一张图里——要么两批用同一方法重测，要么在正文把两批分开说明。

**路线 (b)：图 8 限定 MPDD/BTAD/MVTec，VisA 不参与速度/显存结论。**
- 成本 0；少一个数据集的资源数据。

### D.3.3 决策清单（动笔前打勾）

- [ ] C.1：E1/E2 的 scope —— 保持受限（正文写清）／扩到 K{1,2,4,8}（需重跑）
- [ ] C.2：确认集 —— 启动工作流 F（先冻结规格）／正文明确声明"本文给不出确认集"
- [ ] C.3：图 8 —— 路线 (a) 单设备重测／路线 (b) 排除 VisA
- [ ] C.4：共同有效区域 —— 现在补／正文不报该口径
- [ ] C.5：BTAD-03 纳入跨种子方差 —— 现在补／正文限定 BTAD 01/02 并说明理由
- [ ] C.6：AUPRO 要不要 —— 要（需重跑评价）/不要
- [ ] C.7：角色措辞统一为 `external_frozen_validation` / `in_domain_frozen_validation`
- [ ] D.2.2：修 `论文精读讲解.md` 的两处措辞
