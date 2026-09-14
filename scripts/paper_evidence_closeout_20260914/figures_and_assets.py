"""Stage A: corrected figure 2 / figure 5, literature table structure, claim ledger.

Figure 2 (old) drew per-condition CI bounds averaged or enveloped, and called it a
confidence interval.  The corrected version uses the aggregated interval from
`01_statistics/AGGREGATED_EFFECTS.csv` and shows the raw test-set point delta as a
separate marker.

Figure 5 (old) selected abnormal images by the extreme of ``mean(A1_L - A1_J)`` and
labelled them positive/negative, although ``L <= J`` makes both extremes negative.
The corrected version separates two questions:

* mechanism panels - smallest / largest mean constraint difference ``G = J - L``;
* performance panels - largest improvement / degradation of the per-image
  localisation score of L relative to J.

Every selection is written to CSV with all candidates, so the figure caption can
state the rule, the seed/K and the sample ids.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
CANONICAL = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
             / "canonical").resolve()
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
SEED, SHOT = 0, 4
MAP_STRIDE = 14


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
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def unit_path(dataset: str, seed: int, shot: int, category: str) -> Path:
    root = R / ("p1_matrix" if dataset == "mpdd" else "p3_external")
    return root / "units" / f"{dataset}_s{seed}_k{shot}" / category


# --------------------------------------------------------------------------- fig 2


def figure2(output: Path) -> dict:
    rows = [r for r in read_csv(S / "01_statistics/AGGREGATED_EFFECTS.csv")
            if r["metric"] == "pixel_ap"]
    panels = [("weight_control", "Weight control: DUP - A1 (B-family weight 1/2 -> 2/3)"),
              ("representation_swap", "Representation swap at fixed family weight")]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6))
    plotted = []
    for ax, (family, title) in zip(axes, panels):
        selected = [r for r in rows if r["family"] == family]
        labels, raw, mean, lo, hi = [], [], [], [], []
        for dataset in ("mpdd", "btad"):
            for row in selected:
                if row["dataset"] != dataset:
                    continue
                labels.append(f"{row['contrast']}\n{dataset}")
                raw.append(float(row["point_delta_raw"]))
                mean.append(float(row["bootstrap_mean"]))
                lo.append(float(row["ci_low"]))
                hi.append(float(row["ci_high"]))
                plotted.append({"figure": "fig2", "family": family,
                                "label": f"{row['contrast']} {dataset}",
                                "point_delta_raw": raw[-1], "bootstrap_mean": mean[-1],
                                "ci_low": lo[-1], "ci_high": hi[-1], "ci_level": 0.95,
                                "aggregation": row["aggregation"]})
        xs = np.arange(len(labels))
        mean = np.asarray(mean)
        lo = np.asarray(lo)
        hi = np.asarray(hi)
        ax.bar(xs, mean, width=0.5, color=["#3b6ea5" if m >= 0 else "#a5453b" for m in mean],
               zorder=2)
        ax.errorbar(xs, mean, yerr=[mean - lo, hi - mean], fmt="none", ecolor="black",
                    capsize=4, zorder=3)
        ax.scatter(xs, raw, marker="D", s=22, color="white", edgecolor="black", zorder=4,
                   label="raw test-set point delta")
        ax.axhline(0.0, color="black", linewidth=0.8)
        ax.axhspan(-0.005, 0.005, color="grey", alpha=0.15, zorder=0)
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=7.5)
        ax.set_ylabel("macro pixel AP (delta)", fontsize=9)
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=7.5, loc="lower left")
        ax.grid(axis="y", alpha=0.25)
    axes[0].text(0.02, 0.02,
                 "bars = mean over the pre-specified seeds/K of the paired replicates;\n"
                 "whiskers = 95% interval of that aggregated effect;\n"
                 "diamonds = raw test-set point delta (not a bootstrap quantity)",
                 transform=axes[0].transAxes, fontsize=6.2, va="bottom")
    fig.tight_layout()
    fig.savefig(output / "fig2_aggregated_effects.png", dpi=200)
    plt.close(fig)
    write_csv(S / "03_paper/fig2_values.csv", plotted)
    return {"figure": "fig2_aggregated_effects.png",
            "definition": ("bars are the mean over conditions of the paired per-replicate "
                           "difference; whiskers are the 95% percentile interval of that "
                           "aggregated effect; diamonds are raw test-set point deltas"),
            "n_bars": len(plotted)}


# --------------------------------------------------------------------------- fig 5


def _per_image_scores(directory: Path) -> dict:
    out = {}
    for row in read_csv(directory / "per_image.csv"):
        key = (row["method"], int(row["image_index"]))
        out[key] = {"pixel_ap": (None if row["pixel_ap"] == "" else float(row["pixel_ap"])),
                    "sample_id": row["sample_id"], "label": int(row["label"])}
    return out


def _select(directory: Path, category: str, dataset: str):
    """Return the mechanism and performance selections plus every candidate."""
    with np.load(directory / "patch_scores.npz", allow_pickle=False) as z:
        ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
        a1_j = np.asarray(z["A1_J"], dtype=np.float32)
        a1_l = np.asarray(z["A1_L"], dtype=np.float32)
        a1_g = np.asarray(z["A1_G"], dtype=np.float32)
    cache = CANONICAL / "B" / f"{dataset}_s{SEED}_k8" / f"{category}.npz"
    with np.load(cache, allow_pickle=False) as z:
        labels = np.asarray(z["gt_sp"], dtype=np.int32).reshape(-1)
        masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
        grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
    per_image = _per_image_scores(directory)
    abnormal = np.flatnonzero(labels == 1)
    candidates = []
    for index in abnormal:
        g_mean = float(a1_g[index].mean())
        ap_l = per_image.get(("A1_L", int(index)), {}).get("pixel_ap")
        ap_j = per_image.get(("A1_J", int(index)), {}).get("pixel_ap")
        candidates.append({
            "dataset": dataset, "category": category, "seed": SEED, "shot": SHOT,
            "image_index": int(index), "sample_id": ids[index],
            "mean_G_J_minus_L": g_mean,
            "per_image_pixel_ap_A1_L": ap_l, "per_image_pixel_ap_A1_J": ap_j,
            "per_image_pixel_ap_delta_L_minus_J": (None if ap_l is None or ap_j is None
                                                   else ap_l - ap_j)})
    if not candidates:
        return None, None, []
    by_g = sorted(candidates, key=lambda r: r["mean_G_J_minus_L"])
    mechanism = {"smaller": by_g[0], "larger": by_g[-1]}
    perf = [c for c in candidates if c["per_image_pixel_ap_delta_L_minus_J"] is not None]
    performance = None
    if perf:
        by_delta = sorted(perf, key=lambda r: r["per_image_pixel_ap_delta_L_minus_J"])
        performance = {"worse": by_delta[0], "better": by_delta[-1]}
    return mechanism, performance, candidates


def _panel(ax_row, dataset, category, sample_id, index, masks, grid, scores_path):
    import cv2

    with np.load(scores_path, allow_pickle=False) as z:
        l_map = np.asarray(z["A1_L"], dtype=np.float32)[index]
        j_map = np.asarray(z["A1_J"], dtype=np.float32)[index]
        g_map = np.asarray(z["A1_G"], dtype=np.float32)[index]
    root = (ROOT / "data/mpdd_raw/MPDD") if dataset == "mpdd" else (
        ROOT / "data/btad_raw/BTech_Dataset_transformed")
    image = cv2.imread(str(root / sample_id), cv2.IMREAD_COLOR)
    if image is None:
        return False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    canvas = (grid[0] * MAP_STRIDE, grid[1] * MAP_STRIDE)
    mask = cv2.resize(masks[index], (canvas[1], canvas[0]), interpolation=cv2.INTER_NEAREST)
    l_up = cv2.resize(l_map, (canvas[1], canvas[0]), interpolation=cv2.INTER_LINEAR)
    j_up = cv2.resize(j_map, (canvas[1], canvas[0]), interpolation=cv2.INTER_LINEAR)
    g_up = cv2.resize(g_map, (canvas[1], canvas[0]), interpolation=cv2.INTER_LINEAR)
    ax_row[0].imshow(image)
    ax_row[0].set_title(f"{dataset}/{category}\n{sample_id}", fontsize=6.5)
    ax_row[1].imshow(image)
    ax_row[1].imshow(mask, alpha=0.45, cmap="Reds")
    ax_row[1].set_title("ground truth (canvas coords)", fontsize=6.5)
    ax_row[2].imshow(l_up, cmap="inferno")
    ax_row[2].set_title("A1 L (independent rows)", fontsize=6.5)
    ax_row[3].imshow(j_up, cmap="inferno")
    ax_row[3].set_title("A1 J (shared row)", fontsize=6.5)
    ax_row[4].imshow(g_up, cmap="viridis")
    ax_row[4].set_title("G = J - L (constraint gap)", fontsize=6.5)
    for column in range(5):
        ax_row[column].axis("off")
    return True


def figure5(output: Path) -> dict:
    selections, candidates_all = [], []
    for dataset in ("mpdd", "btad"):
        categories = CATS[dataset][:3]
        for category in categories:
            directory = unit_path(dataset, SEED, SHOT, category)
            if not (directory / "patch_scores.npz").exists():
                continue
            mechanism, performance, candidates = _select(directory, category, dataset)
            candidates_all += candidates
            for kind, row in (("mechanism", mechanism or {}), ("performance", performance or {})):
                for extreme, entry in row.items():
                    if not entry:
                        continue
                    selections.append({"question": kind, "extreme": extreme, **entry})
    write_csv(S / "03_paper/fig5_selection_candidates.csv", candidates_all)
    write_csv(S / "03_paper/fig5_selection.csv", selections)

    made = []
    for question, filename, headline in (
            ("mechanism", "fig5a_constraint_gap.png",
             "Mechanism: smallest / largest mean constraint gap G = J - L"),
            ("performance", "fig5b_localisation_change.png",
             "Performance: largest localisation change of L relative to J")):
        chosen = [r for r in selections if r["question"] == question]
        if not chosen:
            continue
        fig, axes = plt.subplots(len(chosen), 5, figsize=(13.5, 2.4 * len(chosen)), squeeze=False)
        drawn = 0
        for row in chosen:
            directory = unit_path(row["dataset"], SEED, SHOT, row["category"])
            cache = CANONICAL / "B" / f"{row['dataset']}_s{SEED}_k8" / f"{row['category']}.npz"
            with np.load(cache, allow_pickle=False) as z:
                masks = np.asarray(z["imgs_masks"], dtype=np.uint8)
                grid = tuple(int(v) for v in np.asarray(z["grid_size"]).reshape(-1))
            ok = _panel(axes[drawn], row["dataset"], row["category"], row["sample_id"],
                        row["image_index"], masks, grid, directory / "patch_scores.npz")
            if ok:
                drawn += 1
        for spare in range(drawn, len(chosen)):
            for column in range(5):
                axes[spare][column].axis("off")
        fig.suptitle(headline + f"  (seed {SEED}, K={SHOT}, all candidates in fig5_selection_candidates.csv)",
                     fontsize=9)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        fig.savefig(output / filename, dpi=180)
        plt.close(fig)
        made.append(filename)
    return {"figures": made, "n_selected": len(selections),
            "rule": ("mechanism panels use the extreme mean G = J - L over abnormal images; "
                     "performance panels use the extreme per-image pixel AP difference "
                     "(A1_L - A1_J). The labels state the selection metric, not "
                     "success/failure, except in the performance panels where the metric is a "
                     "localisation score."),
            "note": ("per-image pixel AP is an illustration selector, not a pooled statistic; "
                     "the pooled metric remains the category-level pooled AP")}


# --------------------------------------------------------------------------- paper assets


def literature_table(output: Path) -> dict:
    """Fix the column mismatch and add the columns Stage C must fill."""
    works = [
        {"work": "M3DM", "link": "https://arxiv.org/abs/2303.00601",
         "same_rgb_multi_encoder": "yes", "normal_k_shot": "yes", "fixed_weights": "partly",
         "shared_support_row": "unclear", "copy_control": "no", "JL_intervention": "no",
         "budget_condition_analysis": "no",
         "difference": "multi-modal fusion with per-modality memory banks; no controlled "
                       "shared-vs-independent reference-row intervention"},
        {"work": "Fusion-architecture controlled study",
         "link": "https://arxiv.org/abs/2412.17297",
         "same_rgb_multi_encoder": "unclear", "normal_k_shot": "yes", "fixed_weights": "yes",
         "shared_support_row": "unclear", "copy_control": "no", "JL_intervention": "no",
         "budget_condition_analysis": "no",
         "difference": "studies fusion architecture rather than the reference-matching axis"},
        {"work": "Sea-CLIP (WACV 2026)",
         "link": ("https://openaccess.thecvf.com/content/WACV2026/papers/Guo_Sea-CLIP_Mining_"
                  "Semantic-Aware_Representations_for_Few-Shot_Anomaly_Detection_with_CLIP_"
                  "WACV_2026_paper.pdf"),
         "same_rgb_multi_encoder": "unclear", "normal_k_shot": "yes", "fixed_weights": "yes",
         "shared_support_row": "unclear", "copy_control": "no", "JL_intervention": "no",
         "budget_condition_analysis": "no",
         "difference": "semantic-aware CLIP representation; no fixed-weight shared/independent "
                       "reference control"},
        {"work": "CIF", "link": "https://arxiv.org/abs/2511.05966",
         "same_rgb_multi_encoder": "unclear", "normal_k_shot": "yes", "fixed_weights": "partly",
         "shared_support_row": "unclear", "copy_control": "no", "JL_intervention": "no",
         "budget_condition_analysis": "no",
         "difference": "CLIP-based injection; does not vary the support budget under a fixed "
                       "reference coupling"},
    ]
    for row in works:
        row.update({"version_checked": "", "section_evidence": "",
                    "verification_status": "not_verified_in_stage_a",
                    "note": "Stage C must open the paper and fill version/section evidence"})
    write_csv(output / "literature_difference_verified.csv", works)
    lines = ["# 最相近文献差异表（结构已修正；内容待阶段 C 逐篇原文核对）", "",
             "说明：本表在阶段 A 只修正了结构与列数（旧文件表头 9 列、正文 8 列导致错列）。"
             "`yes/partly/no/unclear` 均为**待核查的候选判断**，必须由阶段 C 打开原文核对后填写 "
             "`version_checked`、`section_evidence` 与 `verification_status`。", "",
             "| 工作 | 链接 | 同一 RGB 多编码器 | 正常 K-shot | 固定权重 | 共同支持行 | 复制对照 | "
             "J/L 干预 | 预算与条件分析 | 版本 | 章节证据 | 核查状态 | 与本研究的差别 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in works:
        lines.append("| " + " | ".join([
            row["work"], f"[link]({row['link']})", row["same_rgb_multi_encoder"],
            row["normal_k_shot"], row["fixed_weights"], row["shared_support_row"],
            row["copy_control"], row["JL_intervention"], row["budget_condition_analysis"],
            row["version_checked"] or "待填", row["section_evidence"] or "待填",
            row["verification_status"], row["difference"]]) + " |")
    lines += ["", "本表不能用来证明「无人做过」；只用于说明本研究的具体问题与既有工作的差别。", ""]
    (output / "literature_difference_verified.md").write_text("\n".join(lines), encoding="utf-8")
    return {"n_works": len(works), "status": "structure_fixed_content_pending_stage_c"}


def claim_ledger(output: Path) -> dict:
    rows = [
        {"claim_id": "C1", "topic": "common reference constraint has a measurable cost",
         "claim": "在同一权重与同一参考库下，独立选参考（L）优于共同选参考（J）",
         "evidence_file": "01_statistics/AGGREGATED_EFFECTS.csv (matching_effect) + "
                          "01_statistics/MAIN_INFERENCE_RECONCILIATION.csv",
         "metric": "macro pooled pixel AP (stride 8)",
         "estimator": "paired image-level bootstrap, 1000 replicates, aggregated per replicate",
         "status": "verified", "wording_allowed": "在该固定协议下平均为正且区间不含零；"
                                                  "不可写所有类别普遍改善、不可写全像素显著",
         "wording_forbidden": "所有类别均改善；匹配规则首次被提出；BTAD 为首次未见验证",
         "stage": "A"},
        {"claim_id": "C2", "topic": "weight control",
         "claim": "复制一个已有分支（B->Bcopy）把 B 家族有效权重从 1/2 提到 2/3，反而变差",
         "evidence_file": "01_statistics/AGGREGATED_EFFECTS.csv (weight_control)",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "同上",
         "status": "verified", "wording_allowed": "方向为负且区间不含零；支持设置复制对照",
         "wording_forbidden": "1/2 是最优权重；任何复制分支都会损失", "stage": "A"},
        {"claim_id": "C3", "topic": "new visual representation",
         "claim": "真实 S 的表征收益依赖数据集与匹配方式",
         "evidence_file": "01_statistics/AGGREGATED_EFFECTS.csv (representation_swap)",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "同上",
         "status": "verified",
         "wording_allowed": "MPDD 不确定、BTAD 四个端点正向且区间不含零；条件性结论",
         "wording_forbidden": "三支总比两支强；三支没有价值；把不显著写成等价",
         "stage": "A"},
        {"claim_id": "C4", "topic": "support budget K",
         "claim": "匹配效应随 K 变化（K8 相对 K1）",
         "evidence_file": "01_statistics/MAIN_INFERENCE_RECONCILIATION.csv",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "同一条 K 内配对差再做 K 差",
         "status": "verified",
         "wording_allowed": "MPDD 区间含零、BTAD 略负且上界贴近 0；不宣称统一预算规律",
         "wording_forbidden": "K 越大匹配冲突越小的统一规律；不显著即无影响",
         "stage": "A"},
        {"claim_id": "C5", "topic": "category conditions",
         "claim": "效应大小依赖类别组成，留一类别不翻转符号",
         "evidence_file": "R/p2_conditions/leave_one_category_out.csv",
         "metric": "macro pooled pixel AP (stride 8)",
         "estimator": "共享复制索引下逐条件重算",
         "status": "verified",
         "wording_allowed": "报告每类与留一类别区间；说明类别构成影响规模",
         "wording_forbidden": "各类别普遍获益；用精选图片代表全体", "stage": "A"},
        {"claim_id": "C6", "topic": "defect size",
         "claim": "按缺陷面积分组的描述性差异",
         "evidence_file": "R/p2_conditions/defect_size_contrasts.csv",
         "metric": "subgroup pooled pixel AP (stride 8), point estimate only",
         "estimator": "无区间",
         "status": "descriptive_only",
         "wording_allowed": "描述性附录；说明各组类别构成不同",
         "wording_forbidden": "缺陷面积导致收益变化（因果）", "stage": "A"},
        {"claim_id": "C7", "topic": "full-pixel robustness",
         "claim": "关键效应在全像素点估计上方向保持",
         "evidence_file": "00_audit/STRIDE_SENSITIVITY.json",
         "metric": "stride-1 point estimates", "estimator": "无区间",
         "status": "verified",
         "wording_allowed": "主结论方向保持；表示替换家族存在 1 处达实用尺度的反转，须写明",
         "wording_forbidden": "全像素统计显著；所有方向完全一致", "stage": "A"},
        {"claim_id": "C8", "topic": "external dataset",
         "claim": "BTAD 三类完整复核",
         "evidence_file": "R/p3_external/ + R/p0_support/verification_replay_and_nesting.json",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "1000 次配对 bootstrap",
         "status": "verified",
         "wording_allowed": "已知数据集上的冻结复核",
         "wording_forbidden": "首次未见数据验证", "stage": "A"},
        {"claim_id": "C9", "topic": "native baselines",
         "claim": "与原生 AnomalyDINO 及标准记忆库基线的实际性能参照",
         "evidence_file": "02_baselines/",
         "metric": "full-pixel AP/AUROC（协议差异必须并列说明）",
         "estimator": "不参与因果解释", "status": "pending_stage_b",
         "wording_allowed": "性能上下文；说明协议差异",
         "wording_forbidden": "用旧 MVTec/VisA 分数替代 MPDD/BTAD；stride8 与 stride1 直接比胜负",
         "stage": "B"},
        {"claim_id": "C10", "topic": "literature",
         "claim": "与最相近工作的差别",
         "evidence_file": "03_paper/literature_difference_verified.md",
         "metric": "-", "estimator": "-", "status": "pending_stage_c",
         "wording_allowed": "逐篇核对后的具体差别",
         "wording_forbidden": "首次多分支融合；首次独立近邻；无人做过", "stage": "C"},
        {"claim_id": "C11", "topic": "geometry",
         "claim": "共同画布上的归一化对齐",
         "evidence_file": "00_audit/GEOMETRY_BOUNDARY_CHECK.json",
         "metric": "-", "estimator": "-", "status": "verified",
         "wording_allowed": "B/S 在裁剪画布上精确对齐；C 为近似归一化对齐",
         "wording_forbidden": "原图逐像素严格同位", "stage": "A"},
    ]
    fields = ["claim_id", "topic", "claim", "evidence_file", "metric", "estimator", "status",
              "wording_allowed", "wording_forbidden", "stage"]
    write_csv(output / "CLAIM_EVIDENCE_LEDGER.csv", rows, fields)
    return {"n_claims": len(rows),
            "status_counts": {s: sum(1 for r in rows if r["status"] == s)
                              for s in {r["status"] for r in rows}}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=S / "03_paper")
    args = ap.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    summary = {"created_utc": utcnow()}
    summary["fig2"] = figure2(out)
    print("[A7] fig2 written", flush=True)
    summary["fig5"] = figure5(out)
    print("[A7] fig5 written", flush=True)
    summary["literature"] = literature_table(out)
    print("[A7] literature table written", flush=True)
    summary["ledger"] = claim_ledger(S)
    print("[A7] claim ledger written", flush=True)
    (out / "ASSET_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
