# 投稿复现性只读审计（2026-09-10）

本审计只覆盖 A1 投稿复现链、实验数值证据、方法口径、数据角色、baseline、公平性、测试记录、运行环境和许可证。没有重跑 GPU、特征导出、四数据集重建或全量测试；本文件中的“通过”只表示已有记录或本轮只读检查通过，不能把文件存在、缓存计数或历史 JSON 当成本轮重新复现。

审计基准是 Git `0da9b8fef33afb6a64b218538c0a11a7f6127adf`（2026-09-10 20:30 +08:00）。审计开始时 `git status --short --branch` 为 `## main...origin/main` 且无改动；共享工作区随后出现另一项未跟踪的 `docs/PROJECT_REVIEW_AND_NEXT_STEPS_20260910_CN.md`，本审计没有修改、回退或覆盖它。当前 HEAD、历史验收快照和本轮检查必须分开理解。

## 已有投稿证据

| 结论 | 已有证据 | 审计解释 |
|---|---|---|
| A1 数值重建已有闭环 | `docs/submission_reproducibility_20260826/P0_ACCEPTANCE_REVIEW_20260827.md:15-24` 记录了 `--verify-only` 324/324、MPDD s0/k1 6/6、MVTec s1/k4 15/15、配置聚合最大误差 `1e-5/3e-6`、历史 `122 passed in 5.80s` 和 447 条哈希检查；`submission_repro_20260827/rebuild_manifest_v2.json:5-10,1635-1639` 明确 `numerically_equivalent_to_historical=true`、`byte_identical_to_historical=false`、36 配置/324 payload。 | 这是 2026-08-27 的保存记录，足以支持“历史数值等价”这一限定表述，不支持当前 HEAD 已重新执行。 |
| compact CPU 包可复算论文表 | `submission_repro_20260827/README.md:10-18,40-53`、`submission_repro_20260827/recompute_tables.py:1-26,193-257,260-377`；脚本不导入仓库源码，读取 float16 patch map 和用户合法 mask，`--verify-only` 不需要数据。 | 包内有独立 CPU 实现；仍需用户按许可获取数据/GT mask。完整 GPU 复现、原图和第三方权重均不在包内。 |
| A1 结果边界已记录 | `submission_repro_20260827/README.md:24-36` 给出 matched feature-DINO-only 的四数据集 ΔPixel-AP：MPDD `+0.025829`、BTAD `+0.024895`、VisA `+0.052353`、MVTec `+0.031962`，均 9/9 正；同时明确 3 seed × 3 shot 是同一测试集的参考采样，BTAD Image-AP/F1-max 下降。 | 可支持“Pixel-AP 稳定提升”，不能扩写为所有 image/pixel 指标提升。 |
| P1 统计和完整指标已有记录 | `submission_repro_20260827/evidence/p1/p1_a_bootstrap_ci.md:3-6,49-73`；`scripts/p1_stats_bootstrap.py:17-26,55-71,134-160,221-274`；`scripts/p1_e_complete_metrics_table.py:22-32,73-131,142-175`。 | 36 配置、6 指标和 3 seed × 3 shot 汇总已有来源 hash；脚本说明只聚合既有报告，不重新推理。 |

P0 快照的时间和源码并不等于当前提交：`submission_repro_20260827/evidence/P0_LIVE_AUDIT_REBUILD_20260827.json:3-5` 的 `git_head` 是 `9cb986...`，`docs/submission_reproducibility_20260826/P0_ACCEPTANCE_AUDIT_20260827.json:3-5` 的 `git_head` 是 `313688...`，而本轮 HEAD 是 `0da9b8f...`。`SOURCE_COMMIT.txt:4-12` 指向 `12e1fcf...`；`git diff --name-status 12e1fcf.....HEAD -- submission_repro_20260827` 可见其后加入了 P1 证据并修改了 package README、许可证说明、manifest 和 `SHA256SUMS`。因此应在投稿材料中明确：源码指针是冻结/重建基线，P1 文档和当前审核材料是后续提交；不要把旧 audit 的 `git_head` 写成当前代码的验收结果。

## 方法和入口核对

冻结配置在 `submission_repro_20260827/config/frozen_a1.json:7-30`：DINOv2 ViT-B/14 448 px、32×32×768；AnomalyCLIP ViT-L/14@336 image tower 518 px、37×37×768；两支各自 L2、等权 `0.5/0.5` concat、整体 L2、FAISS `IndexFlatL2`、k=1、distance/2、map 448、stride 8、K={1,2,4}、seed={0,1,2}。`submission_repro_20260827/METHOD_SPEC_V2.md:3-4,10-22,24-42` 是投稿口径，且明确 `anomalyclip_text` 只是历史目录名，最终推理没有文本特征；历史 `METHOD_CARD.md` 的 1152/multimodal 文字只能作为旧证据，不能混入正文。

本轮对关键入口做了存在性检查，以下路径均实际存在：

- CPU 复算：`submission_repro_20260827/recompute_tables.py`；机器审计：`scripts/audit_submission_repro_package.py`。
- GPU smoke/缓存重建：`scripts/smoke_a1_one_class_one_image.py`、`scripts/p0_3_evaluate_a1_rebuild.py`、`scripts/build_compact_predictions.py`。
- 评估和主表：`scripts/evaluate_a1_feature_fusion.py`、`scripts/evaluate_a1_complete_metrics.py`、`scripts/p1_e_complete_metrics_table.py`、`scripts/build_main_results_table.py`。
- 数据根和实验产物：`data/mpdd_raw/MPDD`、`data/btad_raw/BTech_Dataset_transformed`、`data/visa_raw`、`data/mvtec`、`outputs/dynamic_fusion/v3_direction_a`、`experiments/dynamic_fusion/v3_direction_a/p0_rebuild_20260826`、`experiments/dynamic_fusion/v3_direction_a/a1_complete_metrics_20260819`、`experiments/dynamic_fusion/main_results_20260818`、`outputs/unified`。

本轮只读计数为 `outputs/dynamic_fusion/v3_direction_a` 下 648 个 feature NPZ、`submission_repro_20260827/predictions_compact/maps` 下 324 个 compact NPZ。这只是当前文件系统的存在性证据，不是本轮生成或验证证据。

完整 GPU 入口还有一个发布边界：`scripts/evaluate_a1_feature_fusion.py:30-40` 先把 `methods/anomalydino` 放入 `sys.path`，再执行 `from src.utils import dists2map`；因此当前工作树实际优先使用 `methods/anomalydino/src/utils.py:1-17`。该文件虽然存在，但被 `.gitignore:14-15` 的 `methods/` 规则忽略，第三方 `methods/` 源码也不在 compact 投稿包中。仓库跟踪的 `src/utils.py:1-13` 有相同实现；包内 `recompute_tables.py` 是独立实现，所以 CPU 复算入口不依赖这一忽略目录。对外发布时必须把 `methods/` 的来源、固定版本和获取步骤作为 GPU smoke 前置条件，不能仅给出仓库脚本路径。

## Gaussian 顺序歧义（需要澄清，暂不改冻结实现）

`submission_repro_20260827/METHOD_SPEC_V2.md:17-20` 第 7 步写成“`gaussian_filter(sigma=4) + INTER_LINEAR resize 到 448×448`”，包内说明也在 `submission_repro_20260827/recompute_tables.py:14-16` 使用同样的并列写法。这一措辞会被读成先平滑、后 resize。

实际调用链是先 resize、后平滑：

- `methods/anomalydino/src/utils.py:14-17` 和跟踪的 `src/utils.py:10-13` 实际执行 `gaussian_filter(cv2.resize(dists, ..., interpolation=cv2.INTER_LINEAR), sigma=4)`。
- `scripts/evaluate_a1_feature_fusion.py:40,101-103` 导入并调用 `dists2map`；由于上面的 `sys.path` 顺序，完整评估优先走 `methods/anomalydino/src/utils.py`。
- `scripts/build_compact_predictions.py:44,125-128` 的 replay 也调用 `dists2map`。
- `submission_repro_20260827/recompute_tables.py:114-117` 有独立但相同顺序的实现。

这不是当前发现的数值不一致，而是复现协议的文字不充分；sigma=4 是在 448×448 像素网格上应用，若复现者按文档先在 patch 网格平滑再放大，空间尺度会不同。最小修复是把 V2 和包内说明改为：“先对 patch distance grid 使用 `cv2.resize(..., INTER_LINEAR)` 上采样到 448×448，再在 448×448 网格上使用 `scipy.ndimage.gaussian_filter(sigma=4)`”，随后重新生成受影响文档的哈希。此修复不应改动冻结实现或历史结果。

## 数据角色、主指标和 seed 统计

`scripts/p1_e_complete_metrics_table.py:22-32` 固定角色为：MPDD `development`，BTAD `external_frozen_validation`，VisA `in_domain_frozen_validation`，MVTec `external_frozen_validation`；`METHOD_SPEC_V2.md:38-42` 也明确 VisA 与 AnomalyCLIP checkpoint 有训练域关系。论文必须保持这一标签，不得把 VisA 写成独立外部泛化验证。

主指标是 Pixel-AP；`submission_repro_20260827/recompute_tables.py:120-129` 先在 448 图上按 `[::8, ::8]` 取样再算 Pixel-AUROC/AP/AUPRO，AUPRO 上限为 30% FPR（同文件 `:75-111`）。`scripts/p1_e_complete_metrics_table.py:88-99,129-131` 还检查 image score=`max_pool`、stride=8，并将 36 个报告聚合为 72 个 method-config rows。

seed 统计的含义已写对，但正文仍需避免“独立重复实验”的措辞：`p1_a_bootstrap_ci.md:3-6` 明确 3 seed × 3 shot 是同一测试集上的参考采样；`scripts/p1_stats_bootstrap.py:65-71,134-160` 的 B=2000、95% CI、RNG seed=20260827 是类别 bootstrap 和异常图像级 paired bootstrap，`scripts/p1_stats_bootstrap.py:221-237` 的 seed std 只是 3 个参考选择配置的描述性 std，不是跨数据集独立重复的显著性检验。没有看到 test label/mask 用于拟合的证据，代码和包 README 均声明其只用于评估。

## matched baseline 和外部 backbone 公平性

纯融合因果对照应使用同一 DINO 特征、同一 KNN、同一 map/stride 的 feature-DINO-only。`scripts/build_main_results_table.py:90-115,118-138,205-216` 同时保留了旧 score-cache 与 matched feature-level 两种口径：MPDD 的旧口径 A1 ΔAP `+0.0486`，matched 纯融合贡献 `+0.0258`；BTAD 的旧口径 `+0.0766`，matched 纯融合贡献 `+0.0249`；VisA/MVTec 使用 feature-DINO-only。正文若要回答“CLIP 分支带来多少增益”，只能引用 matched 口径，不得把 legacy score-cache 差值当作 fusion gain。

外部方法表是协议对照，不是严格同 backbone 的因果公平实验。`submission_repro_20260827/evidence/p1/p1_d_fairness_table.md:5-17` 列出 A1 为 DINOv2 ViT-B/14 + AnomalyCLIP image tower、无训练；AnomalyDINO 为 ViT-S/14、PatchCore 为 WRN50、WinCLIP+ 使用 OpenCLIP、PromptAD/AdaptCLIP/ReMP-AD 含目标或源域训练/文本。`p1_r3_baseline_comparison.md:7-18` 明确 MVTec/VisA 上 A1 未超过 AnomalyDINO，MPDD/BTAD 没有同协议的完整外部训练 baseline。因而现有证据支持“matched feature-DINO 上的融合增益”和“受协议差异约束的跨方法对照”，不支持“公平外部 backbone 胜出”或全面 SOTA。最小后续工作是收紧论文措辞并在表注列出 backbone、训练、文本、shot/seed 和数据域；若坚持外部胜出论断，才需要新增同协议外部复验。

## 测试记录和当前版本化完整性

已有测试记录互相不完全一致，且本轮未重跑：

- `submission_repro_20260827/evidence/CPU_REGRESSION_20260826.json:3-15`：2026-08-26，`.venv-anomalyclip`，选定 5 个 CPU suite，81 passed、0 failed、6.46 s；`.venv-patchcore` 当时没有 pytest。
- `docs/submission_reproducibility_20260826/P0_ACCEPTANCE_REVIEW_20260827.md:15-24`：2026-08-27 记录 `python -m pytest -q tests` 为 122 passed in 5.80 s。
- `docs/submission_reproducibility_20260826/README.md:9-18` 仍写 123 passed；`docs/CURRENT_DYNAMIC_FUSION_STATUS.md:114-123` 写 122 passed，而该状态后段 `:152-166` 又记录后续项目测试 141/141，并指出根目录无范围 pytest 会误收集 `methods/` 第三方测试。

未来发布前的最小动作是选一个带日期、解释器和明确 `tests` 范围的权威 CPU 记录，修正 81/122/123/141 的语义，不需要为本次审计重跑 GPU。另有版本化证据清单问题：对 `docs/submission_reproducibility_20260826/VERSIONED_EVIDENCE.sha256` 逐项只读核对时，`:9` 的 `docs/CURRENT_DYNAMIC_FUSION_STATUS.md` 期望 SHA256 `8f9d93...`、实际 `fcb2ff...`，`:10` 的 `docs/PAPER_DETAILED_CHINESE_DRAFT_20260827.md` 期望 `bd49e7...`、实际 `269090...`；其余清单项本轮核对相符。应在这些文档定稿后重生成清单，不要把旧 hash index 当作当前 HEAD 的完整性证明。

## 运行环境和许可证

环境快照 `submission_repro_20260827/environment/system.txt:4-14` 是 Windows、Python 3.10.11、RTX 3060 Laptop 6 GiB；DINO 和 CLIP 分别在 `.venv-patchcore` / `.venv-anomalyclip`，K=2/4 复用 K=1 测试特征。两个 freeze 文件记录了关键依赖（例如 `faiss-cpu==1.7.4`、`numpy==1.24.4`、`opencv-python==4.8.1.78`、`scipy==1.9.1`、`scikit-learn==1.2.2`、`torchvision==0.15.1+cu118`）；但 `patchcore_pip_freeze.txt:49` 和 `anomalyclip_pip_freeze.txt:73` 的 torch 依赖是绝对本机 `D:/.../outputs/downloads/...whl` URL，DINO 权重又在 `C:/Users/lynle/.cache/...`。因此这是可追溯的历史机器快照，不是外部机器可直接安装的 lockfile/container。最小后续是补一份带 wheel 来源、第三方 `methods/` 固定 commit、DINO hub commit/权重校验和双环境安装顺序的便携说明；不必重新导出 648 个 cache。

许可证仍是公开发布前的闭环项：

- 冻结包 `submission_repro_20260827/LICENSES_AND_DATA.md:7-16` 当时写 MPDD、BTAD 条款未核验，VisA 为 CC BY 4.0，MVTec 为 CC BY-NC-SA 4.0；`:25-38` 说明包不含原图/第三方权重，自研代码为 MIT。
- 较新的 `docs/CURRENT_DYNAMIC_FUSION_STATUS.md:70-76,114-126,144-147` 已记录后续确认：MPDD 为 CC BY-NC-SA 4.0，BTAD 为 CC BY-SA 4.0，并明确不能把 VT-ADL 代码 MIT 误写成 BTAD 数据许可；同时要求正式 release 刷新许可说明和哈希。
- `submission_repro_20260827/manifest.json:21-38` 明确 raw data、GT mask、third-party weights 和 full feature cache 均不在包内。

因此当前可写“代码 MIT、VisA/MVTec 已列明、MPDD/BTAD 后续证据已确认”，但冻结包本身的 `LICENSES_AND_DATA.md` 仍是旧快照。最小发布动作是保留旧包不变，另生成正式 release 的许可索引、官方 URL/访问日期和新的 SHA256 清单；不要静默改写已验收的冻结包。

## 最小后续工作（按优先级）

1. **P0：澄清方法操作顺序。** 更新 `METHOD_SPEC_V2.md` 和 package README/recompute 说明为“先 `INTER_LINEAR resize` 到 448，再 `gaussian_filter(sigma=4)`”，代码和历史结果保持不变；之后重算文档哈希。
2. **P0：固定当前投稿版本。** 在 P1 文档和 package 定稿后，重新生成 versioned evidence/package hash，并明确 `SOURCE_COMMIT=12e1...` 是冻结基线、当前 HEAD 是后续文档/P1 版本；不能引用 9cb9/3136 的历史 audit 作为当前 HEAD 通过证据。
3. **P1：收敛可复现测试记录。** 选择一个明确环境和 `tests` 范围的 CPU 记录，解释 81、122、123、141 的日期/范围差异；不需要 GPU 重跑。
4. **P1：完成正式 release 许可和环境说明。** 刷新 MPDD/BTAD 条款与 hash，补齐 `methods/` 第三方源码、权重来源和绝对 wheel 路径的获取说明。
5. **P1：论文表述收紧。** 主结果只用 matched feature-DINO-only 解释融合贡献；外部 baseline 写成异构协议对照；seed std/CI 写成同一测试集参考采样统计；VisA 保持 in-domain frozen validation。
