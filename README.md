# Few-shot Industrial Anomaly Detection — Dual-Encoder Patch Fusion

> **接手先读（2026-09-19）**：[docs/HANDOVER_20260919.md](docs/HANDOVER_20260919.md)（交接正文：结论/证据链/踩坑/边界）；
> **产物总索引**：[docs/ARTIFACT_INDEX.md](docs/ARTIFACT_INDEX.md)（工作流 A–I → 目录 → 产物 → 复现命令 → 状态）。

> **最新入口（2026-09-14）**：`docs/` 的阅读索引与当前状态请看 [docs/README.md](docs/README.md)。
> 当前论文主线已更新为**固定融合下「正常参考匹配方式 × 新增视觉表征分支」的交互研究**，
> 最新结果与六问回答见 [experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md](experiments/dynamic_fusion/representation_matching_interaction_20260914/REPORT_CN.md)。
> 本文件下方"当前状态 (2026-08-27)"与 HANDOFF.md 记录的是 **2026-08 的旧主线**（A1 双编码器固定融合 +
> 四数据集 9/9 全正），保留作历史参考，**不代表当前结论**。

> 投稿收尾入口（2026-08-26）：[SCI 四区投稿与复现总交接](docs/PAPER_SUBMISSION_HANDOFF_AND_REPRODUCIBILITY_PLAN_20260826.md)；[投稿复现包审计入口](docs/submission_reproducibility_20260826/README.md)。论文详细中文初稿：[PAPER_DETAILED_CHINESE_DRAFT_20260827.md](docs/PAPER_DETAILED_CHINESE_DRAFT_20260827.md)。

本仓库当前论文主线是**双编码器视觉 patch 固定融合 + 正常记忆库**，用于少样本工业异常检测。早期视觉—语言动态路由是已关闭的探索路线，仅作为负结果与研究边界保留。

## 当前状态 (2026-08-27)

- **A1 主结果（双视觉固定融合）**: DINO `dinov2_vitb14` + AnomalyCLIP `ViT-L/14@336` image-tower patch 特征 concat + KNN(k=1) normal memory bank（冻结 w=0.5，非动态路由、非显式文本融合）。相对 matched feature-DINO-only KNN 的纯融合 mean ΔPixel-AP 在 MPDD/BTAD/VisA/MVTec 分别为 +0.0258 / +0.0249 / +0.0524 / +0.0320，均为 9/9 配置正。
- **论文前准备 Gate 已全部关闭（R1–R4）**: P1-A 统计 / P1-B 失败边界 / P1-C 效率（含稳态 benchmark + 峰值 RAM）/ P1-D 公平性 / P1-E 完整指标全部完成；`p1_acceptance.py` 21/21 通过、包审计 `submission_repro_package_complete=true`、pytest 123 passed；定性图 source manifest 与跨方法 baseline 对照表已入包。R5 剩余仅作者人工事项：MPDD/BTAD 数据使用条款确认与 BibTeX 复核。
- **论文初稿**: `docs/PAPER_DETAILED_CHINESE_DRAFT_20260827.md`（中文详细母稿，15 章，含摘要/Intro/Related Work/Method/Experiments/Results/Discussion/Limitation/Conclusion 与表述边界），已登记进 `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256`。
- **V4 视觉—文本动态融合扩展**: 已按决策 D 关闭（官方 SubspaceAD G2 审计 FAILED，`paper_eligible=false`，G4–G11 永久阻断）。
- 唯一权威状态: [docs/CURRENT_DYNAMIC_FUSION_STATUS.md](docs/CURRENT_DYNAMIC_FUSION_STATUS.md)；权威计划: [docs/DYNAMIC_FUSION_NEXT_STEPS.md](docs/DYNAMIC_FUSION_NEXT_STEPS.md)；写作前验收: [docs/PRE_MANUSCRIPT_READINESS_AUDIT_20260827.md](docs/PRE_MANUSCRIPT_READINESS_AUDIT_20260827.md)。

详细实验记录、交接文档: [HANDOFF.md](HANDOFF.md)  
项目状态: [PROJECT_STATUS.md](PROJECT_STATUS.md)  
初始计划: [PLAN.md](PLAN.md)

## 核心目标

- 数据集: MPDD (6类), BTAD (3类), VisA (12类), MVTec AD (15类)
- Shot: 1 / 2 / 4 张正常参考图
- 基础方法: AnomalyCLIP, WinCLIP+, PatchCore, PromptAD, AnomalyDINO, ReMP-AD, AdaptCLIP
- 输出: 图像级检测、像素级定位、效率统计与可复现实验记录

## 环境

> 下表于 2026-09-19 在盘上逐环境实读（`<venv>\Scripts\python.exe`），不是转抄上游 requirements。

| 虚拟环境 | 用途（实读） |
|---|---|
| `.venv-anomalyclip` | **论文主线工作流的默认解释器**（torch 2.0.0+cu118, CUDA 11.8）：B/S/C 编码、D 支、E1–E3、泛化与 KSDD2 矩阵、AnomalyDINO 基线、统计与图件脚本 —— `scripts/**` 的绝大多数调用都用它 |
| `.venv-patchcore` | PatchCore 基线推理 + 部分 CPU 评估 / 早期 DINOv2 特征导出（torch 2.0.0+cu118, faiss-cpu 1.7.4） |
| `.venv-winclip` | WinCLIP+ 推理 |
| `.venv-promptad` | PromptAD 训练/推理 |
| `.venv-adaptclip` | AdaptCLIP 推理 + 部分 CPU 评估（torch 2.7.1+cu118） |
| `.venv-remp_ad` | ReMP-AD 推理（torch 2.6.0+cu124） |
| **（无）** | **`.venv-anomalydino` 不存在**；AnomalyDINO 基线在 `.venv-anomalyclip` 下运行（见 `scripts/limitation_closure_20260915/anomalydino_guarded_retry.ps1` L21） |
| `.venv-rempad` | 同名残留：盘上另存一份（torch 2.0.0+cu118，**未装 matplotlib**）；不要假定它是被使用的那一份 |
| 默认 `python`（PATH） | torch 2.12.1+**cpu**，`cuda_available=False` ⇒ **只能跑统计/CPU 阶段，不能编码** |

GPU: NVIDIA RTX 3060 Laptop, 6 GB VRAM；内存 15.8 GB，20 逻辑核。

## 快速复现

A1 冻结配置的完整复现步骤见 [experiments/dynamic_fusion/freeze/a1_mpdd_w05/REPRODUCE.md](experiments/dynamic_fusion/freeze/a1_mpdd_w05/REPRODUCE.md) 与 [METHOD_CARD.md](experiments/dynamic_fusion/freeze/a1_mpdd_w05/METHOD_CARD.md)。
