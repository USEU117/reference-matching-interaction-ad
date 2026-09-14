"""S5: refresh the claims ledger, the literature table and the two paper figures.

Reads only the artefacts this delivery produced (S1/S2/S3/S4 and the corrected literature
verification) and writes to NEW/06_paper/.  Nothing in R or CLOSE is modified: the figures
here are the updated versions, and the paper draft delta says so explicitly.

Two things are kept separate everywhere:

* `experiment_status`  - did the experiment run and pass its own checks?
* `hypothesis_support` - does the result support the claim?

A completed experiment with an unsupported hypothesis is recorded as completed/unsupported,
never as a failure.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
NEW = (ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
       ).resolve()
CLOSE = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
OUT = NEW / "06_paper"
PRIMARY = "pixel_ap"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or (list(dict.fromkeys(k for row in rows for k in row)) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def interaction_rows():
    rows = read_csv(NEW / "02_interaction/interaction_aggregate.csv")
    return [r for r in rows if r.get("kind") == "interaction" and r.get("metric") == PRIMARY]


def primary_revision(dataset: str) -> str:
    return "study" if dataset == "mpdd" else "corrected"


def claim_ledger() -> list:
    s1 = read_json(NEW / "02_interaction/S1_SUMMARY.json") or {}
    s2 = read_json(NEW / "03_robustness/S2_SUMMARY.json")
    s3 = read_json(NEW / "04_new_encoder/S3_SUMMARY.json")
    s4 = read_json(NEW / "05_baselines/S4_SUMMARY.json")
    s6 = read_json(NEW / "04_new_encoder/S6_SUMMARY.json")
    s7 = read_json(NEW / "04_new_encoder/S7_SUMMARY.json")
    s8 = read_json(NEW / "05_baselines/S8_SUMMARY.json")
    encoder_diff = read_csv(NEW / "04_new_encoder/encoder_difference.csv")
    diff_excludes = [r for r in encoder_diff
                     if str(r.get("difference_ci95_excludes_zero")).lower() == "true"]
    fp_new = read_csv(NEW / "04_new_encoder/interaction_fullpixel_new_encoder.csv")
    fullpixel_common = read_csv(NEW / "05_baselines/baseline_common_region_summary.csv")
    rows = interaction_rows()
    primary = {(r["dataset"], r["contrast"].split(":")[0]): r for r in rows
               if r["evaluation_revision"] == primary_revision(r["dataset"])}
    stride = read_csv(NEW / "03_robustness/interaction_stride_sensitivity.csv")
    loo = read_csv(NEW / "03_robustness/interaction_leave_one_category_out.csv")
    per_cat = read_csv(NEW / "03_robustness/interaction_per_category.csv")
    verdict = {}
    for key, row in primary.items():
        verdict[key] = {
            "point": row["point_delta"], "mean": row["bootstrap_mean"],
            "ci95": f"[{row['ci95_low']}, {row['ci95_high']}]",
            "ci9875": f"[{row['ci9875_low']}, {row['ci9875_high']}]",
            "excludes_zero_95": row["ci95_excludes_zero"],
            "reaches_scale": row["reaches_effect_scale"]}
    family = {f"{k[0]}|{k[1]}": v for k, v in verdict.items()}
    sign_diffs = [r for r in stride if str(r.get("same_sign")).lower() == "false"
                  and r["evaluation_revision"] == primary_revision(r["dataset"])]
    loo_flips = [r for r in loo if str(r.get("sign_flip")).lower() == "true"
                 and r["evaluation_revision"] == primary_revision(r["dataset"])]
    loo_flip_datasets = sorted({r["dataset"] for r in loo_flips})
    loo_datasets = sorted({r["dataset"] for r in loo
                           if r["evaluation_revision"] == primary_revision(r["dataset"])})
    loo_label = ("supported" if not loo_flips
                 else ("unsupported" if len(loo_flip_datasets) == len(loo_datasets)
                       else "partial"))
    claims = [
        {"claim_id": "I1",
         "claim": ("新增视觉表征（S 或第二 DINOv2 副本）的收益，在独立匹配下与共同匹配下"
                   "不同（I_TRI/I_BAL ≠ 0）"),
         "experiment_status": "completed" if s1 and row_present(primary) else "not_run",
         "hypothesis_support": support_label(primary),
         "evidence_artifact": "NEW/02_interaction/interaction_aggregate.csv",
         "statistic": json.dumps(family, ensure_ascii=False),
         "note": ("I>0 只表示独立匹配让表征替换的损失更小；E 本身另列，不能合并成一个成功标签")},
        {"claim_id": "I2",
         "claim": "交互效应在 MPDD 与 BTAD 上同号",
         "experiment_status": "completed" if s1 else "not_run",
         "hypothesis_support": same_sign_label(primary),
         "evidence_artifact": "NEW/02_interaction/interaction_aggregate.csv",
         "statistic": json.dumps({f"{k[0]}|{k[1]}": family[f"{k[0]}|{k[1]}"]["mean"]
                                  for k in primary}, ensure_ascii=False),
         "note": "两数据集单独报告，不合并成一个总体"},
        {"claim_id": "I3",
         "claim": "交互效应达到 0.005 宏 pixel AP 的实用尺度",
         "experiment_status": "completed" if s1 else "not_run",
         "hypothesis_support": ("partial" if any(
             str(r.get("reaches_effect_scale")).lower() == "true" for r in primary.values())
             and any(str(r.get("reaches_effect_scale")).lower() == "false"
                     for r in primary.values()) else
             ("supported" if all(str(r.get("reaches_effect_scale")).lower() == "true"
                                 for r in primary.values()) else "unsupported")),
         "evidence_artifact": "NEW/02_interaction/interaction_aggregate.csv",
         "statistic": json.dumps({f"{k[0]}|{k[1]}": family[f"{k[0]}|{k[1]}"]["reaches_scale"]
                                  for k in primary}, ensure_ascii=False),
         "note": "达到尺度与统计显著分开评价"},
        {"claim_id": "I8",
         "claim": ("换用 WideResNet50-2 分支后交互变大：直接检验 S 与 D 两项交互的差值"),
         "experiment_status": "completed" if s7 else "not_run",
         "hypothesis_support": ("partial" if 0 < len(diff_excludes) < len(encoder_diff)
                                else ("supported" if diff_excludes and encoder_diff
                                      else "unsupported")),
         "evidence_artifact": "NEW/04_new_encoder/encoder_difference.csv",
         "statistic": json.dumps({f"{r['dataset']}|{r['comparison']}":
                                  {"difference": r.get("difference_mean"),
                                   "ci95": [r.get("difference_ci95_low"),
                                            r.get("difference_ci95_high")],
                                   "excludes_zero": r.get("difference_ci95_excludes_zero"),
                                   "stride1_point_difference": r.get("stride1_difference_point")}
                                  for r in encoder_diff}, ensure_ascii=False),
         "note": ("同条件配对（seed 0/1 x K 1/4），差值在复制内相减后再取分位数；四种组合构成"
                  "一个家族，同时报 95% 与 98.75% 区间。只有显著的那些才允许说'更大'")},
        {"claim_id": "I4",
         "claim": "交互效应在全像素（stride-1）口径下保持方向",
         "experiment_status": "completed" if s2 else "not_run",
         "hypothesis_support": "unsupported" if sign_diffs else ("supported" if s2 else "undetermined"),
         "evidence_artifact": "NEW/03_robustness/interaction_stride_sensitivity.csv",
         "statistic": f"sign_differences={len(sign_diffs)}",
         "note": "全像素只给点估计；若要声称显著必须另算区间"},
        {"claim_id": "I5",
         "claim": "交互效应不由单一类别驱动（留一类不变号）",
         "experiment_status": "completed" if s2 else "not_run",
         "hypothesis_support": loo_label,
         "evidence_artifact": "NEW/03_robustness/interaction_leave_one_category_out.csv",
         "statistic": f"sign_flips={len(loo_flips)}; datasets={loo_flip_datasets}",
         "note": ("不复用旧 A1 的留一类结果替代新交互的检查；某一数据集变号即降低该主张的强度")},
        {"claim_id": "I6",
         "claim": "交互效应在每一类、每个 K 上都被报告，而不是挑端点",
         "experiment_status": "completed" if s2 else "not_run",
         "hypothesis_support": "descriptive",
         "evidence_artifact": "NEW/03_robustness/interaction_per_category.csv; "
                              "NEW/03_robustness/interaction_K_curve.csv",
         "statistic": f"per_category_rows={len(per_cat)}",
         "note": "跨 K 交互差为次要探索，不升级为主假说"},
        {"claim_id": "I7",
         "claim": "换一个非 DINOv2 的视觉编码器（WideResNet50-2）后交互仍然复现",
         "experiment_status": "completed" if s3 else "not_run",
         "hypothesis_support": new_encoder_label(s3),
         "evidence_artifact": "NEW/04_new_encoder/interaction_new_encoder.csv",
         "statistic": (json.dumps(s3.get("interaction_lookup", {}), ensure_ascii=False)
                       if s3 else None),
         "note": ("预先固定的编码器迁移检查；测试数据已被使用过，不能称为未见数据集确认。"
                  "范围仅 seed0/1、K1/4。四个主要数据集×对照组合的区间都不含零")},
        {"claim_id": "I9",
         "claim": "新分支的交互与新增表征收益在全像素（stride-1）口径下同样成立",
         "experiment_status": "completed" if s6 else "not_run",
         "hypothesis_support": ("supported" if s6 and len(fp_new) >= 4
                                and all(float(r["point_delta"]) > 0 for r in fp_new)
                                else ("unsupported" if s6 else "undetermined")),
         "evidence_artifact": "NEW/04_new_encoder/interaction_fullpixel_new_encoder.csv",
         "statistic": json.dumps({f"{r['dataset']}|{r['evaluation_revision']}|"
                                  f"{r['contrast'].split(':')[0]}":
                                  {"stride1_point": r.get("point_delta"),
                                   "stride8_point": r.get("stride8_point_delta"),
                                   "stride8_replicate_mean": r.get("stride8_replicate_mean")}
                                  for r in fp_new}, ensure_ascii=False),
         "note": ("新分支此前只有抽样像素评价；此处用 study 同款 resize+σ=4 补齐全像素点估计，"
                  "并以 A1 对照对旧全像素表做复现校验（见 S6_SUMMARY.json 的 replication_check）")},
        {"claim_id": "B1",
         "claim": "经合理配置与统一评价后，受控融合的竞争力可以与成熟基线比较",
         "experiment_status": "completed" if s4 else "not_run",
         "hypothesis_support": "descriptive",
         "evidence_artifact": "NEW/05_baselines/baseline_common_region.csv",
         "statistic": (f"common_region_rows={len(fullpixel_common)}" if s8 else None),
         "note": ("PatchCore 的中心裁剪预测不再被拉伸到整张画布；共同有效区域取各方法真实覆盖"
                  "矩形的交集，所有方法重采样到同一像素集后比较。仍不据此宣称击败强基线")},
        {"claim_id": "B2",
         "claim": "开启参考旋转的 AnomalyDINO 已纳入同一共同评价坐标",
         "experiment_status": "completed" if s8 else "not_run",
         "hypothesis_support": "descriptive",
         "evidence_artifact": "NEW/05_baselines/baseline_common_region_summary.csv",
         "statistic": (json.dumps(s8.get("region_fraction_of_canvas", {}), ensure_ascii=False)
                       if s8 else None),
         "note": "共同区域小于画布，丢弃比例按类别记录，避免把未预测区域当成可评价区域"},
        {"claim_id": "L1",
         "claim": "J/L 匹配模式本身是本文首创的操作",
         "experiment_status": "completed",
         "hypothesis_support": "refuted",
         "evidence_artifact": ("NEW/06_paper/literature_verification_20260914.csv; "
                              "NEW/06_paper/multi_view_neighborhood_prior_art.csv"),
         "statistic": ("Sea-CLIP Eq.5-7 同文并存 J 型与 L 型；多视图异常检测方向已把"
                       "「各视图独立邻域后对齐」与「直接表示跨视图一致邻域」作为核心问题"
                       "（SCoNE AAAI-26；MUVAD AAAI-19；NC-Nets AAAI-21）"),
         "note": "已被全文/摘要核实推翻：不得声称共同参考或独立参考这一操作是本文首创"},
        {"claim_id": "L4",
         "claim": ("在多视图异常检测中，「跨视图一致的邻域」与「各视图独立邻域」的取舍"
                   "已经是被研究过的问题，本文不能把它当成新发现"),
         "experiment_status": "completed",
         "hypothesis_support": "supported",
         "evidence_artifact": "NEW/06_paper/multi_view_neighborhood_prior_art.csv",
         "statistic": ("SCoNE 明确把该取舍写成多视图异常检测的核心问题；MUVAD 区分"
                       "dissension 与 unanimous；NC-Nets 与 ECMOD 统一各视图邻域结构"),
         "note": ("本文的增量限定在：冻结编码器 + 少样本工业定位、把有效权重与新增表征分离、"
                  "并对「匹配方式 × 新增分支」给出带重复种子与区间的直接交互估计；"
                  "多视图文献的输入是无标注多视图数据且多用于离群检测，不能直接等同")},
        {"claim_id": "L2",
         "claim": "把匹配模式与新增表征分支作为两个因子的交互，在最近似文献中未被报告",
         "experiment_status": "completed",
         "hypothesis_support": "supported",
         "evidence_artifact": "NEW/06_paper/literature_verification_20260914.csv",
         "statistic": "5 篇中 0 篇给出带重复种子/区间估计的交互项",
         "note": "Sea-CLIP 与 3D-ADNAS 是在不同融合配置下分别度量分支收益，不是因子化交互"},
        {"claim_id": "L3",
         "claim": "首次融合多个视觉编码器用于少样本异常检测",
         "experiment_status": "completed",
         "hypothesis_support": "refuted",
         "evidence_artifact": "NEW/06_paper/literature_verification_20260914.csv",
         "statistic": "Sea-CLIP / M3DM / CIF 均已融合多编码器特征",
         "note": "不得使用"},
    ]
    return claims


def row_present(primary) -> bool:
    return bool(primary)


def support_label(primary) -> str:
    if not primary:
        return "undetermined"
    excludes = [str(r.get("ci95_excludes_zero")).lower() == "true" for r in primary.values()]
    signs = {np.sign(float(r["bootstrap_mean"])) for r in primary.values()}
    if all(excludes) and len(signs) == 1:
        return "supported"
    if any(excludes):
        return "partial"
    return "unsupported"


def same_sign_label(primary) -> str:
    if not primary:
        return "undetermined"
    by_contrast = {}
    for (dataset, contrast), row in primary.items():
        by_contrast.setdefault(contrast, []).append(float(row["bootstrap_mean"]))
    consistent = all(np.sign(v[0]) == np.sign(v[1]) for v in by_contrast.values()
                     if len(v) == 2)
    return "supported" if consistent else "unsupported"


def new_encoder_label(s3) -> str:
    if not s3:
        return "undetermined"
    lookup = s3.get("interaction_lookup") or {}
    values = dict(lookup)
    if not values:
        return "undetermined"
    means = [v["mean"] for v in values.values()]
    return "supported" if all(np.sign(m) == np.sign(means[0]) for m in means) else "unsupported"


def literature_table() -> list:
    verified = {r["source"]: r for r in read_csv(OUT / "literature_verification_20260914.csv")}
    alias = {"M3DM": "M3DM", "Sea-CLIP": "Sea-CLIP",
             "Revisiting Multimodal Fusion for 3D-AD": "3D-ADNAS (Revisiting Multimodal Fusion)",
             "CIF (Commonality In Few)": "CIF"}
    rows = []
    for row in read_csv(CLOSE / "03_paper/literature_difference_verified.csv"):
        work = row["work"]
        source = verified.get(alias.get(work, ""))
        out = dict(row)
        if source:
            out["same_rgb_multi_encoder"] = source["uses_multiple_visual_encoders"]
            out["shared_support_row"] = source["shares_reference_bank_across_branches"]
            out["JL_intervention"] = source["joint_or_independent_nearest_neighbour"]
            out["normal_k_shot"] = source["normal_sample_budget"]
            out["fixed_weights"] = source["weight_search_or_learned_weights"]
            out["budget_condition_analysis"] = source["interaction_experiment_reported"]
            out["evidence"] = f"{source['evidence_level']}: {source['evidence_location']}"
            out["difference"] = source["closest_to_current_work"]
            out["verification_status"] = source["evidence_level"]
            if work.startswith("Sea-CLIP"):
                out["difference"] = (source["closest_to_current_work"]
                                     + "。早前 no multi-RGB-encoder fusion 的说法已被全文核实"
                                       "推翻：" + source["uses_multiple_visual_encoders_evidence"][:220])
            elif work.startswith("M3DM"):
                out["same_rgb_multi_encoder"] = "no (two modalities, one encoder each)"
        rows.append(out)
    if "AnomalyDINO (official implementation)" in verified:
        source = verified["AnomalyDINO (official implementation)"]
        rows.append({
            "work": "AnomalyDINO", "venue": source["venue_year"],
            "version_checked": "official repository + arXiv:2405.14529",
            "link": source["url_used"], "modality": "RGB only",
            "same_rgb_multi_encoder": source["uses_multiple_visual_encoders"],
            "normal_k_shot": source["normal_sample_budget"],
            "fixed_weights": source["weight_search_or_learned_weights"],
            "shared_support_row": source["shares_reference_bank_across_branches"],
            "copy_control": "no",
            "JL_intervention": source["joint_or_independent_nearest_neighbour"],
            "budget_condition_analysis": source["interaction_experiment_reported"],
            "evidence": f"{source['evidence_level']}: {source['evidence_location']}",
            "difference": source["closest_to_current_work"],
            "verification_status": source["evidence_level"]})
    return rows


def figure_effects_and_interaction(out: Path) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    effects = read_csv(NEW / "02_interaction/representation_effects.csv")
    effects = [r for r in effects if r["metric"] == PRIMARY]
    rows = interaction_rows()
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
    colors = {"mpdd": "#1f77b4", "btad": "#d62728"}
    order = ["E_TRI_L", "E_TRI_J", "E_BAL_L", "E_BAL_J"]
    position = 0
    labels = []
    for dataset in ("mpdd", "btad"):
        for name in order:
            row = next((r for r in effects if r["dataset"] == dataset
                        and r["contrast"].split(":")[0] == name
                        and r["evaluation_revision"] == primary_revision(dataset)), None)
            if row is None:
                continue
            mean = float(row["bootstrap_mean"])
            low, high = float(row["ci95_low"]), float(row["ci95_high"])
            axes[0].errorbar(position, mean, yerr=[[mean - low], [high - mean]], fmt="o",
                             color=colors[dataset], capsize=3)
            labels.append(f"{dataset}\n{name.replace('E_', '')}")
            position += 1
        position += 0.6
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].axhspan(-0.005, 0.005, color="grey", alpha=0.15)
    axes[0].set_xticks(range(len(labels)))
    axes[0].set_xticklabels(labels, fontsize=7)
    axes[0].set_ylabel("macro pixel AP difference")
    axes[0].set_title("Representation swap effect (E), 95% exploratory CI", fontsize=9)

    position, tick_labels = 0, []
    for dataset in ("mpdd", "btad"):
        for name in ("I_TRI", "I_BAL"):
            row = next((r for r in rows if r["dataset"] == dataset
                        and r["contrast"].split(":")[0] == name
                        and r["evaluation_revision"] == primary_revision(dataset)), None)
            if row is None:
                continue
            mean = float(row["bootstrap_mean"])
            low, high = float(row["ci9875_low"]), float(row["ci9875_high"])
            axes[1].errorbar(position, mean, yerr=[[mean - low], [high - mean]], fmt="s",
                             color=colors[dataset], capsize=4)
            axes[1].annotate(f"{mean:+.5f}", (position, mean), fontsize=7,
                             xytext=(4, 6), textcoords="offset points")
            tick_labels.append(f"{dataset}\n{name}")
            position += 1
        position += 0.6
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].axhspan(-0.005, 0.005, color="grey", alpha=0.15,
                    label="practical reference scale 0.005")
    axes[1].set_xticks(range(len(tick_labels)))
    axes[1].set_xticklabels(tick_labels, fontsize=8)
    axes[1].set_title("Interaction I = E_L - E_J, 98.75% family CI", fontsize=9)
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    path = out / "fig2_effects_and_interaction.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return str(path)


def figure_interaction_conditioned(out: Path) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    curve = read_csv(NEW / "03_robustness/interaction_K_curve.csv")
    per_cat = read_csv(NEW / "03_robustness/interaction_per_category.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))
    colors = {"I_TRI": "#2ca02c", "I_BAL": "#ff7f0e"}
    markers = {"mpdd": "o", "btad": "^"}
    for dataset in ("mpdd", "btad"):
        revision = primary_revision(dataset)
        for name in ("I_TRI", "I_BAL"):
            block = [r for r in curve if r["dataset"] == dataset
                     and r["evaluation_revision"] == revision and r["interaction"] == name
                     and int(r["seed"]) == -1]
            if not block:
                continue
            xs = [int(r["shot"]) for r in block]
            mean = [float(r["mean_delta"]) for r in block]
            low = [float(r["ci95_low"]) for r in block]
            high = [float(r["ci95_high"]) for r in block]
            axes[0].errorbar(xs, mean, yerr=[np.array(mean) - np.array(low),
                                            np.array(high) - np.array(mean)],
                             fmt=markers[dataset], color=colors[name], capsize=3,
                             label=f"{dataset} {name}")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].axhspan(-0.005, 0.005, color="grey", alpha=0.15)
    axes[0].set_xscale("log", base=2)
    axes[0].set_xticks([1, 2, 4, 8])
    axes[0].set_xticklabels(["1", "2", "4", "8"])
    axes[0].set_xlabel("K (few-shot references)")
    axes[0].set_ylabel("macro pixel AP interaction")
    axes[0].set_title("Interaction by K (seed-averaged, 95% CI)", fontsize=9)
    axes[0].legend(fontsize=7)

    position, tick_labels = 0, []
    for dataset in ("mpdd", "btad"):
        revision = primary_revision(dataset)
        block = [r for r in per_cat if r["dataset"] == dataset
                 and r["evaluation_revision"] == revision and r["interaction"] == "I_TRI"]
        for row in block:
            mean = float(row["mean_delta"])
            low, high = float(row["ci95_low"]), float(row["ci95_high"])
            axes[1].errorbar(position, mean, yerr=[[mean - low], [high - mean]], fmt="o",
                             color="#1f77b4", capsize=3)
            tick_labels.append(f"{dataset}\n{row['category']}")
            position += 1
        position += 0.5
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].axhspan(-0.005, 0.005, color="grey", alpha=0.15)
    axes[1].set_xticks(range(len(tick_labels)))
    axes[1].set_xticklabels(tick_labels, fontsize=6.5, rotation=45, ha="right")
    axes[1].set_title("I_TRI per category (95% CI)", fontsize=9)
    fig.tight_layout()
    path = out / "fig3_interaction_conditioned.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return str(path)


ABSTRACT = """# 摘要与贡献草稿（依据本轮结果修订）

## 摘要（草稿）

在只有少量正常样本、视觉编码器全程冻结、分支权重预先固定的受控设定下，我们区分两件
常被混在一起的事：(i) 融合权重与新增视觉表征带来的收益，(ii) 多分支是否必须共用同一
个正常参考 patch 行。我们把后者的两种做法显式命名为 J（跨分支共同参考行）与 L（各分支
独立参考行），并在同一批预测上构造直接交互量

    I = E_L - E_J,   E = 新增表征相对其对照的类别宏平均像素 AP 变化

两个数据集、两种公平对照共 4 项汇总交互构成一个推断家族，配以 4 项 Bonferroni 98.75%
近似区间；类别、参考数量 K、留一类别与全像素方向另有稳健性检查。
**I>0 只说明独立匹配使表征替换的损失更小，不等于新增分支本身有正收益**，因此表征效应
E 本身一并报告。

结果是有条件的，而不是一条普遍规律：

- **MPDD**：允许各分支独立选择参考，确实使新增分支（DINOv2-S）的收益相对更有利——两种
  公平对照的差别约为 0.60 与 0.77 个 AP 百分点，调整后的区间都不含零。这里说的是
  **匹配方式对新增分支收益的影响**，不是整体准确率提升这么多。S 分支在独立匹配下
  相对改善明确（E_L 的点估计为正、区间含零），但**绝对正收益尚不明确**。
- **BTAD**：S 分支本身有新增表征收益（E 的区间不含零），但**没有明确证据表明该收益依赖
  共同或独立匹配**（交互区间含零，且方向与类别 02 和 K4/K8 相关）。"新分支有用"与
  "新分支必须配合独立匹配才有用"是两个不同问题。
- **换成分支 D（ImageNet WideResNet50-2）后**，两个数据集都出现了正向交互：四项交互的
  点估计约 0.50-0.97 个 AP 百分点，区间均不含零；新增分支本身也有正收益。直接检验
  S 与 D 两项交互的差值发现：**BTAD 上 D 的交互显著更大，MPDD 上两者不可区分**。
  因此"匹配方式的影响并非只在原来的 DINOv2-S 组合中出现，但影响大小依赖编码器与数据
  条件"，而不能写成新编码器整体优于旧编码器。

（范围：MPDD 六类 × seed 0/1/2 × K 1/2/4/8；BTAD 三类 × seed 0/1 × K 1/2/4/8；
新分支仅 seed 0/1 × K 1/4。全像素口径只有点估计，未计算其区间。）

## 贡献（草稿，已按文献全文核实收窄）

1. **因子化的实验设计**：把"参考匹配模式"（J/L）作为显式因子，与"新增/替换视觉表征分支"
   交叉，在重复种子与类别宏平均下给出带区间估计的交互效应。最近似的 5 篇工作中没有一篇
   给出该交叉：Sea-CLIP 在同一切片内并存 J 型（DINOv2 选行、CLIP 打分）与 L 型（CLIP
   独立最近邻），但只在两种融合机制下分别度量分支收益；3D-ADNAS 做了模块级 early/middle/
   late 融合的组合消融并给出条件性命题，但不涉及参考匹配；M3DM、CIF 只做逐项累加消融。
   **必须同时引用多视图异常检测这条线**（SCoNE AAAI-26；MUVAD AAAI-19；NC-Nets AAAI-21；
   ECMOD DASFAA-23）：那里已经把"各视图独立邻域后对齐"与"直接表示跨视图一致邻域"当作
   核心问题，因此共同/独立参考这一**操作本身不是本文首创**，本文的增量只能限定在设定
   （冻结编码器、少样本工业定位、像素级评价）、分离方式（有效权重 vs 新增表征）与
   估计形式（带重复种子与区间的直接交互）上。
2. **把两条既有线统一到同一受控设定**：多视图异常检测中的"跨视图一致邻域 vs 各视图独立
   最近邻"与多模态融合中的 early/late fusion。
3. **可复核的条件性结论**：交互与表征收益都被拆成"统计证据 / 实际尺度 / E_L 是否为正"
   三件事分别报告；在 BTAD 上给出反例条件（区间含零、依赖类别与 K），并用第二个编码器
   检验结论是否只属于原来的 DINOv2-S 组合。

## 明确不能使用的表述

- 不能称"首次将多个视觉编码器特征融合用于少样本异常检测"（Sea-CLIP、M3DM、CIF 均已如此）。
- 不能称"首次系统比较早/中/晚期融合"（3D-ADNAS 已有系统实验与理论）。
- 不能称"首次指出新增表征分支收益并非无条件"（3D-ADNAS Proposition 1/2 已有条件性结论）。
- 不能把 J 型操作本身（用 A 分支选参考行、B 分支在该行打分）当作全新操作（Sea-CLIP Eq.5–6）。
- 不能把"共同参考限制了新增信息收益"写成根本机制或普遍规律：BTAD 不支持，且 S 与 D 的
  交互差值只在 BTAD 上可区分。
- 不能把"独立匹配让新增分支更强"写成整体模型准确率提升 0.6-0.8 个百分点。
- 不能把本次结果称为未见数据集上的确认：测试图像在本项目此前的分析中已被使用。

## 图表更新说明

- 本文交付的 `fig2_effects_and_interaction.png` 与 `fig3_interaction_conditioned.png`
  是更新版，**取代** CLOSE/03_paper 下同名的旧图（旧图只画成对差值，没有交互量）。
- CLOSE/03_paper/fig2_aggregated_effects.png 与 fig5a/5b 保持不变，作为历史版本保留。
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    claims = claim_ledger()
    write_csv(out / "claim_to_evidence.csv", claims)

    literature = literature_table()
    write_csv(out / "literature_difference_verified_updated.csv", literature)

    figures = []
    try:
        figures.append(figure_effects_and_interaction(out))
        figures.append(figure_interaction_conditioned(out))
    except Exception as exc:  # noqa: BLE001 - recorded, not hidden
        (out / "FIGURE_ERROR.txt").write_text(repr(exc), encoding="utf-8")
    (out / "abstract_and_contributions_CN.md").write_text(ABSTRACT, encoding="utf-8")

    summary = {"created_utc": utcnow(), "claims": len(claims),
               "claims_completed": sum(1 for c in claims
                                       if c["experiment_status"] == "completed"),
               "claims_supported": sum(1 for c in claims
                                       if c["hypothesis_support"] == "supported"),
               "claims_unsupported": sum(1 for c in claims
                                         if c["hypothesis_support"] == "unsupported"),
               "literature_rows": len(literature), "figures": figures,
               "note": ("experiment_status and hypothesis_support are deliberately separate "
                        "columns; an unsupported hypothesis is not a failed experiment")}
    (out / "S5_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
