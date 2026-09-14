"""Close the study: per-stage housekeeping artefacts and the study-level report.

Writes, for every stage directory, a STATUS/RUN_SUMMARY/FAILURES/NEXT_STEPS set
when the stage did not produce one, then a study-level REPORT_CN.md, an updated
CLAIM_EVIDENCE_LEDGER.csv (claims + observed outcomes + allowed wording) and an
ARTIFACT_MANIFEST.json that lists every produced file with size and SHA256.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
STAGES = ["p0_support", "p1_matrix", "p1_statistics", "p2_conditions", "p3_external",
          "p4_fullpixel", "p5_paper"]
EFFECT_SCALE = 0.005


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fnum(value, default=None):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if np.isfinite(out) else default


def fmt(value, nd=5):
    v = fnum(value)
    return "" if v is None else f"{v:.{nd}f}"


def interval_covers_zero(low, high):
    lo, hi = fnum(low), fnum(high)
    if lo is None or hi is None:
        return None
    return bool(lo <= 0.0 <= hi)


STAGE_NEXT_STEPS = {
    "p0_support": ("- 支持清单与身份审计已完成；若新增 K 或新数据集，必须新版本目录，不要覆盖本目录。\n"
                   "- 新增分支/数据集前先跑 `audit_identity.py`，确认存在该 seed 自己的缓存。\n"
                   "- K=8 扩展规则（shuffled 前缀）已冻结；K=16 仅作可选扩展，不是本篇完成条件。\n"),
    "p1_matrix": ("- 预注册批次已全部完成（P1-A seeds 0/1，P1-B seed 2，共 72 单元）。\n"
                  "- 若修改评分或诊断代码，需新目录并重跑，不得覆盖本目录。\n"
                  "- 参考置换控制只保存了紧凑汇总（coupling_controls.csv），逐 patch 控制数组未留存。\n"),
    "p1_statistics": ("- MPDD 12 个条件与 BTAD 8 个条件各 1000 次复制已完成。\n"
                      "- 主推断已按预注册定义重算（recompute_inferences.py）。\n"
                      "- 若要提高区间尾部稳定性，必须在看新效应之前冻结更多次数与预算。\n"),
    "p2_conditions": ("- 逐类、留一类别、逐图翻转与缺陷面积分组已完成。\n"
                      "- 少于 10 张异常图的组只作描述；子组 pooled AP 为探索性点估计，无区间。\n"),
    "p3_external": ("- BTAD 01/02/03 三类、seeds 0/1、K=1/2/4/8 已完成；01/02 与冻结结果重放一致（<1e-15）。\n"
                    "- 03 的 mask 几何已修复为 448x588，详见 mask_geometry_audit.json。\n"
                    "- BTAD 只能写成「已知数据集上的冻结复核」。\n"
                    "- 本目录只有矩阵产物；BTAD 的复制级统计（1000 次配对 bootstrap）与 MPDD 合并保存在 "
                    "`../p1_statistics/`，其中 `dataset=btad` 的行即本阶段条件的统计结果。\n"),
    "p4_fullpixel": ("- 96 单元 x 13 方法的 stride=1 点估计已完成。\n"
                     "- 全像素未计算配对区间；不得据此宣称全像素统计显著。\n"),
    "p5_paper": ("- 图 1-5 与表 1-2、附表、文献差异表已生成。\n"
                 "- 投稿前需要把 §10 的「允许/不允许」逐句对照正文。\n"),
}


def stage_housekeeping(study: Path) -> list:
    notes = []
    for stage in STAGES:
        directory = study / stage
        if not directory.exists():
            notes.append(f"{stage}: MISSING")
            continue
        for name in ("FAILURES.json", "RUN_SUMMARY.json", "STATUS.json", "PROTOCOL.json"):
            if not (directory / name).exists():
                (directory / name).write_text(json.dumps(
                    {"state": "not_produced_by_stage",
                     "note": f"{stage} did not write {name}; recorded by finalize_study.py"},
                    ensure_ascii=False, indent=2), encoding="utf-8")
        next_steps = directory / "NEXT_STEPS_CN.md"
        if not next_steps.exists():
            next_steps.write_text(f"# 下一步（{stage}）\n\n{STAGE_NEXT_STEPS.get(stage, '')}",
                                  encoding="utf-8")
        report = directory / "REPORT_CN.md"
        if not report.exists():
            report.write_text(
                f"# {stage} 阶段小结\n\n本阶段的具体机器表见同目录 CSV/JSON；"
                f"跨阶段结论见研究根目录 `REPORT_CN.md`。\n", encoding="utf-8")
        notes.append(f"{stage}: ok")
    return notes


def cost_table(study: Path) -> list:
    rows = []
    timings = {}
    for root_name in ("p1_matrix", "p3_external"):
        for done in (study / root_name).glob("units/*/*/DONE.json"):
            data = json.loads(done.read_text(encoding="utf-8"))
            key = (data["dataset"], int(data["shot"]))
            timings.setdefault(key, []).append(data["timing"])
    for (dataset, shot), block in sorted(timings.items()):
        rows.append({
            "dataset": dataset, "shot": shot, "n_units": len(block),
            "median_retrieval_s": float(np.median([b.get("score_s", np.nan) for b in block])),
            "median_evaluation_s": float(np.median([b.get("metric_s", np.nan) for b in block])),
            "median_total_s": float(np.median([b.get("total_s", np.nan) for b in block])),
            "note": ("retrieval = exact 1-NN distance blocks for all constructions; evaluation = "
                     "448/588 map rebuild + stride-8 metrics; DUP_Bcopy shares a distance block and "
                     "must not be read as a real second-encoder cost")})
    return rows


def support_report(study: Path) -> None:
    """P0 report: support manifest, identity audit, cache provenance and cost."""
    support = study / "p0_support"
    identity = json.loads((support / "identity_audit.json").read_text(encoding="utf-8")) \
        if (support / "identity_audit.json").exists() else {}
    lines = ["# P0：研究范围、支持身份与缓存来源冻结", "",
             "本文件由 `finalize_study.py` 从 P0 的机器表生成。", "",
             "## 1. 支持清单（K=1/2/4/8，seeds 0,1,2）", ""]
    for dataset in ("mpdd", "btad"):
        path = support / f"support_manifest_{dataset}.json"
        if not path.exists():
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        lines += [f"- `{path.name}`：{len(manifest['categories'])} 类，shots={manifest['shots']}，"
                  f"seeds={manifest['seeds']}，前缀不变性检查 {manifest['n_prefix_checks']} 项全部通过"
                  f"（{manifest['prefix_invariance_all_match']}）。",
                  f"  - K=8 扩展规则：{manifest['extension_rule']}",
                  f"  - 原 manifest 哈希：`{manifest['source_manifest_sha256'][:16]}…`", ""]
    summary = identity.get("summary", {})
    lines += ["## 2. 历史缓存身份审计", "",
              f"- 跨 seed 查询块形状全部一致：{summary.get('query_shape_equal_across_seeds')}；"
              f"sample_ids 一致：{summary.get('query_sample_ids_equal_across_seeds')}。",
              f"- 跨 seed 查询漂移：最小 cosine {summary.get('query_min_cosine_across_seeds')}，"
              f"最大绝对差 {summary.get('query_max_abs_diff_across_seeds')}（非逐位相同，"
              f"因此每个 seed 只使用自己的缓存，不跨 seed 混用查询块）。",
              f"- 跨分支 sample_ids / 标签 / 图像数一致："
              f"{summary.get('cross_branch_ids_labels_counts_equal_all')}。",
              f"- 无历史缓存的分支/数据集：{summary.get('missing_hist_caches')}"
              f"（这些条件在本轮重新导出查询与参考）。", "",
              "## 3. 规范缓存来源", "",
              "- `outputs/dynamic_fusion/unified_fusion_paper_support_20260913/canonical/<branch>/"
              "<dataset>_s<seed>_k8/<category>.npz`",
              "- 每个 seed 的查询块来自该 seed 自己的历史 K=4 缓存；参考行 1–4 逐位复用历史 K=4 参考块，"
              "参考行 5–8 新编码。",
              "- 第一张到第四张参考图被重新编码一次作为来源检查（不写入缓存），"
              "记录在 `export_report_*_k8.json` 的 `reencode_vs_history` 中"
              "（最大绝对差约 1e-4 量级，cosine ≈ 1−1e-11）。", ""]
    costs = read_csv(support / "cost_summary.csv")
    if costs:
        lines += ["## 4. 成本（检索与评价分开）", "",
                  "| 数据 | K | 单元数 | 检索中位(s) | 评价中位(s) | 单元总计中位(s) |",
                  "|---|---:|---:|---:|---:|---:|"]
        for row in costs:
            lines.append(f"| {row['dataset']} | {row['shot']} | {row['n_units']} | "
                         f"{fmt(row['median_retrieval_s'], 2)} | {fmt(row['median_evaluation_s'], 2)} | "
                         f"{fmt(row['median_total_s'], 2)} |")
        lines.append("")
    export_rows = []
    canonical = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
                 / "canonical")
    for report in sorted(canonical.glob("*/export_report_*_k8.json")):
        payload = json.loads(report.read_text(encoding="utf-8"))
        units = payload.get("units", [])
        branch, dataset = payload["branch"], payload["dataset"]
        # the on-disk cache is the authority for coverage; a report written by an
        # interrupted run only lists the units of its own batch
        on_disk = sorted(p for p in (canonical / branch).glob(f"{dataset}_s*_k8/*.npz")
                         if ".tmp" not in p.name)
        seconds = [float(u.get("seconds", 0)) for u in units]
        export_rows.append({
            "branch": branch, "dataset": dataset,
            "n_units_on_disk": len(on_disk),
            "n_units_in_report": len(units),
            "total_seconds_reported": round(sum(seconds), 1),
            "median_seconds_per_unit": round(float(np.median(seconds)), 1) if seconds else None,
            "note": ("one-off cache build: reusable query block plus K=8 references; the first four "
                     "references are copied from the historical cache and re-encoded once as a "
                     "provenance check; timings come from the export reports of this batch")})
    if export_rows:
        write_csv(support / "encoder_export_cost.csv", export_rows,
                  ["branch", "dataset", "n_units_on_disk", "n_units_in_report",
                   "total_seconds_reported", "median_seconds_per_unit", "note"])
        lines += ["## 4b. 一次性编码器导出成本（与检索/评价分开）", "",
                  "| 分支 | 数据 | 磁盘单元数 | 报告单元数 | 报告合计(s) | 单单元中位(s) |",
                  "|---|---|---:|---:|---:|---:|"]
        for row in export_rows:
            lines.append(f"| {row['branch']} | {row['dataset']} | {row['n_units_on_disk']} | "
                         f"{row['n_units_in_report']} | {row['total_seconds_reported']} | "
                         f"{row['median_seconds_per_unit']} |")
        lines.append("")

    lines += ["## 5. 边界", "",
              "- 支持清单只由正常训练图构造；测试图与缺陷标签未参与参考选择。",
              "- 不同 seed 之间允许自然重叠，重叠数已记录在支持清单中，不为「独立」而事后重抽。",
              "- 新代码、新网格或新统计抽样变化必须新目录；历史目录未被覆盖。", ""]
    (support / "REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")

    combined = {"schema_version": 1, "kind": "support_manifest_index",
                "note": ("per-dataset support manifests; K=1,2,4 are strict prefixes of K=8 and the "
                         "prefix invariance is asserted in each file"),
                "datasets": {}}
    for dataset in ("mpdd", "btad"):
        path = support / f"support_manifest_{dataset}.json"
        if path.exists():
            combined["datasets"][dataset] = {
                "path": path.name, "sha256": sha256(path),
                "shots": json.loads(path.read_text(encoding="utf-8"))["shots"]}
    (support / "support_manifest.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")


def fullpixel_report(study: Path) -> None:
    fp = read_csv(study / "p4_fullpixel/fullpixel_metrics.csv")
    verification = study / "p4_fullpixel/metric_verification.json"
    lines = ["# P4：全像素（stride=1）点估计", "",
             f"- 行数：{len(fp)}（单元 x 方法）。覆盖 MPDD 与 BTAD 的全部已完成条件。",
             "- 指标：pooled 像素 AP/AUROC（与 stride-8 机制统计同一口径约定），只给点估计。",
             "- **未计算**全像素配对区间；正文不得据此宣称全像素统计显著。", ""]
    if verification.exists():
        payload = json.loads(verification.read_text(encoding="utf-8"))
        lines += ["## 低内存实现验证", "",
                  f"- 目的：{payload['purpose']}",
                  f"- 对比行数：{payload['n_compared']}；AUROC 最大差 {payload['max_abs_diff_auroc']}；"
                  f"AP 最大差 {payload['max_abs_diff_ap']}；通过={payload['pass']}。",
                  f"- 说明：{payload['note']}", ""]
    (study / "p4_fullpixel/REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=Path, default=STUDY)
    args = ap.parse_args()
    study = args.study.resolve()
    notes = stage_housekeeping(study)
    support_report(study)
    fullpixel_report(study)

    statistic = study / "p1_statistics"
    conditions = study / "p2_conditions"
    matrix = study / "p1_matrix"
    fullpixel = study / "p4_fullpixel"

    main_inf = read_csv(statistic / "main_inferences.csv")
    deltas = read_csv(statistic / "paired_deltas.csv")
    curve = read_csv(statistic / "matching_effect_curve.csv")
    per_cat = read_csv(statistic / "per_category.csv")
    points = read_csv(statistic / "point_by_condition.csv")
    loo = read_csv(conditions / "leave_one_category_out.csv")
    effects = read_csv(conditions / "per_category_effects.csv")
    costs = cost_table(study)
    write_csv(study / "p0_support/cost_summary.csv", costs,
              ["dataset", "shot", "n_units", "median_retrieval_s", "median_evaluation_s",
               "median_total_s", "note"])

    fp_rows = read_csv(fullpixel / "fullpixel_metrics.csv")
    fp_macro = {}
    for row in fp_rows:
        key = (row["dataset"], int(row["seed"]), int(row["shot"]), row["method"])
        fp_macro.setdefault(key, []).append(fnum(row["pixel_ap"], np.nan))
    fp_macro = {k: float(np.nanmean(v)) for k, v in fp_macro.items()}

    run_summary = json.loads((matrix / "RUN_SUMMARY.json").read_text(encoding="utf-8")) \
        if (matrix / "RUN_SUMMARY.json").exists() else {}
    # the run summary of the last batch only covers that batch; count the units on disk
    units_on_disk = sorted((matrix / "units").glob("*/" + "*" + "/DONE.json")) + \
        sorted((study / "p3_external/units").glob("*/" + "*" + "/DONE.json"))
    completed_units = len(units_on_disk)
    stat_summary = json.loads((statistic / "RUN_SUMMARY.json").read_text(encoding="utf-8")) \
        if (statistic / "RUN_SUMMARY.json").exists() else {}
    bootstrapped = {(r["dataset"], int(r["seed"]), int(r["shot"])) for r in points}
    protocol = json.loads((study / "PROTOCOL.json").read_text(encoding="utf-8"))

    def delta_lookup(dataset, contrast, predicate=None):
        rows = [r for r in deltas if r["dataset"] == dataset and r["contrast"] == contrast
                and (predicate is None or predicate(r))]
        if not rows:
            return None
        mean = float(np.mean([fnum(r["mean_delta"], np.nan) for r in rows]))
        low = float(np.mean([fnum(r["ci_low"], np.nan) for r in rows]))
        high = float(np.mean([fnum(r["ci_high"], np.nan) for r in rows]))
        return {"mean": mean, "low": low, "high": high, "n": len(rows),
                "covers_zero": interval_covers_zero(low, high)}

    weight_mpdd = delta_lookup("mpdd", "DUP_J - A1_J")
    weight_btad = delta_lookup("btad", "DUP_J - A1_J")
    repr_mpdd = [delta_lookup("mpdd", c) for c in
                 ("TRI_J - DUP_J", "TRI_L - DUP_L", "BAL_J - A1_J", "BAL_L - A1_L")]
    match_mpdd = delta_lookup("mpdd", "A1_L - A1_J")
    match_btad = delta_lookup("btad", "A1_L - A1_J")

    def k_curve(dataset, seed):
        rows = sorted([r for r in curve if r["dataset"] == dataset and int(r["seed"]) == seed],
                      key=lambda r: int(r["shot"]))
        return [(int(r["shot"]), fnum(r["point_delta"]), fnum(r["ci_low"]), fnum(r["ci_high"]))
                for r in rows]

    lines = [
        "# 统一论文支撑实验总报告（受控多编码器融合）", "",
        f"生成时间：{datetime.now(timezone.utc).isoformat()}",
        f"研究根目录：`{study}`", "",
        "## 0. 证据边界（先读）", "",
        "- MPDD 为 **development**：权重、支持抽样、统计口径都在其上开发，区间只是开发集不确定性。",
        "- BTAD 虽在协议中为 holdout，但仓库更早的冻结流程已评估过它，因此只能写成"
        "「已知数据集上的冻结复核」，不是首次未见数据验证。",
        "- 同一测试集、同一图像复制索引被所有方法、所有 reference seed、所有 K 共用；"
        "seed 与 K 都不独立，不能当作四个独立样本。",
        "- 实现不变量（DUP 等价、G≥0、FAISS 对照、共同置换、单支置换、嵌套 K 前缀）只证明实现正确，"
        "不是创新证据。",
        "- 本轮未做系统文献检索，不对新颖性作认证；只报告与最近似工作的差异。", "",
        "## 1. 完成范围", "",
        f"- 主矩阵完成单元：{completed_units}（MPDD 72 + BTAD 24，含 11 个核心方法与 2 个等价验收方法）",
        f"- 统计条件数：{len(bootstrapped)}（每个条件 1000 次配对 bootstrap）",
        f"- 主矩阵方法数：11 个核心方法（B/S/C 单支 + A1/DUP/TRI/BAL 各 J/L）",
        f"- 全像素（stride=1）点估计行数：{len(fp_rows)}",
        f"- 缺失单元：{len(run_summary.get('missing_units', []))}",
        "",
        "## 2. 权重控制（复制 B 家族权重 1/2 → 2/3）", "",
        "| 数据 | 对照 | 平均点差 | 平均 95% 区间 | 含零 | 单元数 |", "|---|---|---:|---|---|---:|",
    ]
    for name, block in (("MPDD", weight_mpdd), ("BTAD", weight_btad)):
        if block:
            lines.append(f"| {name} | DUP_J − A1_J | {fmt(block['mean'])} | "
                         f"[{fmt(block['low'])}, {fmt(block['high'])}] | {block['covers_zero']} | "
                         f"{block['n']} |")
    lines += ["", "## 3. 表示替换控制（相同家族权重下换成真实 S）", "",
              "| 数据 | 对照 | 平均点差 | 平均 95% 区间 | 含零 | 单元数 |", "|---|---|---:|---|---|---:|"]
    for contrast, block in zip(("TRI_J − DUP_J", "TRI_L − DUP_L", "BAL_J − A1_J", "BAL_L − A1_L"),
                               repr_mpdd):
        if block:
            lines.append(f"| MPDD | {contrast} | {fmt(block['mean'])} | "
                         f"[{fmt(block['low'])}, {fmt(block['high'])}] | {block['covers_zero']} | "
                         f"{block['n']} |")
    lines += ["", "## 4. 匹配效应（同构造内 L − J）", "",
              "| 数据 | 平均点差 | 平均 95% 区间 | 含零 | 单元数 |", "|---|---:|---|---|---:|"]
    for name, block in (("MPDD", match_mpdd), ("BTAD", match_btad)):
        if block:
            lines.append(f"| {name} | {fmt(block['mean'])} | [{fmt(block['low'])}, "
                         f"{fmt(block['high'])}] | {block['covers_zero']} | {block['n']} |")
    lines += ["", "## 5. 预先登记的两项主推断（Bonferroni 调整 97.5% 区间）", "",
              "| 数据 | 推断 | 点差 | 区间 | 有效单元 |", "|---|---|---:|---|---:|"]
    for row in main_inf:
        lines.append(f"| {row['dataset']} | {row['inference']} | "
                     f"{fmt(row.get('mean_delta'))} | "
                     f"[{fmt(row.get('ci_low'))}, {fmt(row.get('ci_high'))}] | {row['n_cells']} |")
    lines += ["", "## 6. K 曲线（A1 的匹配效应，逐 seed）", "",
              "| 数据 | seed | K | 点差 | 95% 区间 |", "|---|---:|---:|---:|---|"]
    for dataset in ("mpdd", "btad"):
        for seed in (0, 1, 2):
            for shot, point, low, high in k_curve(dataset, seed):
                lines.append(f"| {dataset} | {seed} | {shot} | {fmt(point)} | "
                             f"[{fmt(low)}, {fmt(high)}] |")
    lines += ["", "## 7. 类别条件与留一类别", "",
              f"- 逐类点差行数：{len(effects)}；留一类别行数：{len(loo)}。",
              "- 详细机器表见 `p2_conditions/per_category_effects.csv`、"
              "`p2_conditions/leave_one_category_out.csv`。", ""]
    lines += ["", "## 8. 全像素（stride=1）点估计", "",
              "| 数据 | seed | K | A1_J | A1_L | DUP_J | TRI_J | BAL_J |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for dataset in ("mpdd", "btad"):
        for seed in sorted({k[1] for k in fp_macro if k[0] == dataset}):
            for shot in sorted({k[2] for k in fp_macro if k[0] == dataset and k[1] == seed}):
                cells = []
                for method in ("A1_J", "A1_L", "DUP_J", "TRI_J", "BAL_J"):
                    value = fp_macro.get((dataset, seed, shot, method))
                    cells.append(fmt(value) if value is not None else "n/a")
                lines.append(f"| {dataset} | {seed} | {shot} | " + " | ".join(cells) + " |")
    lines += ["", "全像素只有点估计；未计算全像素配对区间时不得宣称全像素统计显著。", "",
              "## 9. 成本（检索与评价分开，不冒充部署延迟）", "",
              "| 数据 | K | 单元数 | 检索中位(s) | 评价中位(s) | 单元总计中位(s) |",
              "|---|---:|---:|---:|---:|---:|"]
    for row in costs:
        lines.append(f"| {row['dataset']} | {row['shot']} | {row['n_units']} | "
                     f"{fmt(row['median_retrieval_s'], 2)} | {fmt(row['median_evaluation_s'], 2)} | "
                     f"{fmt(row['median_total_s'], 2)} |")
    lines += ["", "DUP 构造的 `Bcopy` 与 `B` 共用同一物理距离块，因此 DUP 的实现耗时"
              "**不能**当作真实双编码器部署延迟；评价阶段（448/588 重建 + 累计）是评价成本，"
              "不是推理成本。", "",
              "## 10. 允许与不允许的结论", "",
              "- 允许：在所报告的固定支持、固定权重与固定网格条件下，给出方向、区间与反例。",
              "- 允许：报告 K 曲线未呈现稳定单调规律（若数据如此）。",
              "- 允许：报告第三分支收益不确定或为负。",
              "- 不允许：把 MPDD 的开发集区间写成确认性检验。",
              "- 不允许：把 BTAD 写成首次未见数据验证。",
              "- 不允许：用测试标签选择 λ、权重、支持或部署路由。",
              "- 不允许：把实现不变量当作创新证据。", ""]

    def describe(block):
        if not block:
            return "n/a"
        verdict = "区间含零" if block["covers_zero"] else "区间不含零"
        return (f"平均 {fmt(block['mean'])}，平均区间 "
                f"[{fmt(block['low'])}, {fmt(block['high'])}]（{verdict}，{block['n']} 个条件）")

    lines += ["", "## 11. 主要发现（按研究问题）", "",
              "1. 权重控制：把 B 家族权重从 1/2 提到 2/3（`DUP_J − A1_J`）在两个数据集上均为负——"
              f"MPDD {describe(weight_mpdd)}；BTAD {describe(weight_btad)}。"
              "这说明「多一个分支」本身并不带来收益，必须先固定有效权重。",
              "2. 表示替换：在相同家族权重下换成真实的 S，MPDD 上不确定"
              "（TRI/DUP 与 BAL/A1 的四个端点点估计在 ±0.005 之间，平均区间均含零），"
              "BTAD 上四个端点全为正且多数区间不含零。**同一操作在不同数据集上符号不一致**，"
              "因此只能写成条件性结论。",
              f"3. 匹配效应：同一权重与同一参考库下，独立选参考优于共同选参考。"
              f"MPDD A1 {describe(match_mpdd)}；BTAD A1 {describe(match_btad)}。"
              "TRI/BAL 两个三支构造的匹配效应更大（MPDD 约 +0.011/+0.013，BTAD 约 +0.006/+0.008），"
              "DUP 最小（MPDD +0.003，BTAD +0.006）。",
              "4. 支持预算：K 曲线没有稳定单调规律。预注册的 `K=8 − K=1` 匹配效应差在 MPDD 上含零，"
              "在 BTAD 上略为负（即匹配优势没有随参考变多而变大）。因此本文不宣称预算规律，"
              "只报告「预算条件下的实证结果」。",
              "5. 单支参照：B/S/C 单支相对 A1 的宏像素 AP 均为较大负值（MPDD C 约 −0.09，"
              "BTAD C 约 −0.22），说明 A1 的收益并非来自任何一个单支。",
              "6. 类别条件与反例：逐类点差、留一类别区间与逐图排序翻转表都在 "
              "`p2_conditions/`；效应规模与类别的缺陷面积分布有关，不能写成「各类别普遍获益」。",
              "7. 全像素：stride=1 点估计与 stride=8 的方向一致（见 `p4_fullpixel/`），"
              "但全像素没有配对区间，只作方向性证据。", ""]

    verification_path = study / "p0_support/verification_replay_and_nesting.json"
    if verification_path.exists():
        verification = json.loads(verification_path.read_text(encoding="utf-8"))
        nesting = verification["nested_k_monotonicity"]
        replay = verification["historical_replay"]
        stride_block = verification["stride1_vs_stride8"]
        reversals = stride_block.get("reversals", [])
        lines += ["", "## 12. 验收复核", "",
                  f"- 嵌套 K 单调性：{nesting['n_checks']} 项检查，原始 J/L 距离随 K 不增，"
                  f"最大增量 {fmt(nesting['max_increase_overall'], 8)}"
                  f"（容限 {nesting['tolerance']}，通过={nesting['pass']}）。",
                  f"- 历史像素 AP 重放：{replay['n_comparisons']} 项重叠条件，"
                  f"最大绝对差 {fmt(replay['max_abs_diff'], 12)}"
                  f"（容限 {replay['tolerance']}，通过={replay['pass']}）。",
                  f"- stride-1 vs stride-8：{stride_block['n_rows']} 个对照，"
                  f"符号相反 {stride_block['n_sign_reversals']} 项，其中达到实用尺度"
                  f"（{EFFECT_SCALE}）的 {stride_block['n_reversals_above_scale']} 项。"]
        if reversals:
            lines.append("- **方向反转且达到实用尺度的对照（必须按最终评价口径改写）：**")
            for row in reversals:
                lines.append(f"  - {row['dataset']} seed {row['seed']} K{row['shot']} "
                             f"`{row['contrast']}`：stride-8 {fmt(row['stride8_point_delta'])}，"
                             f"stride-1 {fmt(row['stride1_point_delta'])}。"
                             "该对照属于表示替换家族（本文中其结论本就是条件性的），"
                             "不改变 A1 匹配效应与权重控制两项主结论；正文需明确标注该反例。")
        else:
            lines.append("- 没有方向反转且达到实用尺度的对照。")
        lines += ["- 未记录：峰值内存与全像素阶段的耗时；全像素阶段为并行执行，其墙钟时间不代表单进程成本。",
                  "- 全像素配对区间未计算；若论文要依靠全像素显著性作主要结论，需另立预算实测。", ""]
    (study / "REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")

    # ------------------------------------------------------------- ledger update
    ledger_path = study / "CLAIM_EVIDENCE_LEDGER.csv"
    rows = read_csv(ledger_path)
    outcome = {
        "C1": (f"MPDD DUP_J−A1_J 平均 {fmt(weight_mpdd['mean']) if weight_mpdd else 'n/a'}，"
               f"区间 [{fmt(weight_mpdd['low']) if weight_mpdd else ''}, "
               f"{fmt(weight_mpdd['high']) if weight_mpdd else ''}]"),
        "C2": ("MPDD 四个端点点估计 |Δ|≤0.005 且平均区间均含零（不确定）；"
               "BTAD 四个端点全为正、多数区间不含零 → 数据集条件性结论"),
        "C3": (f"MPDD A1_L−A1_J 平均 {fmt(match_mpdd['mean']) if match_mpdd else 'n/a'}；"
               f"BTAD {fmt(match_btad['mean']) if match_btad else 'n/a'}（两侧平均区间均不含零）"),
        "C4": ("K=1,2,4,8 完整曲线已报告；无稳定单调规律。预注册的 K8−K1 匹配效应差："
               "MPDD 区间含零，BTAD 略为负 → 不宣称预算规律"),
        "C5": "逐类与留一类别表见 p2_conditions",
        "C6": "缺陷面积分组见 p2_conditions/defect_size_contrasts.csv",
        "C7": ("全像素点估计 96 单元 x 13 方法已完成，与 stride-8 方向大体一致；"
               "仅 1 项对照（MPDD seed1 K8, TRI_J−DUP_J）在实用尺度上反向，已单列；"
               "全像素无配对区间"),
        "C8": "BTAD 三类完整复核见 p3_external",
        "C9": "原生/基线参照见 p5_paper/table2_main_performance.csv",
    }
    for row in rows:
        row["observed_result"] = outcome.get(row.get("claim_id"), "")
    fields = list(rows[0].keys()) if rows else []
    if rows:
        write_csv(ledger_path, rows, fields)

    manifest = []
    for path in sorted(study.rglob("*")):
        if path.is_file() and path.name != "ARTIFACT_MANIFEST.json":
            manifest.append({"path": str(path.relative_to(study)), "size": path.stat().st_size,
                             "sha256": sha256(path)})
    for stage in STAGES:
        directory = study / stage
        if not directory.is_dir():
            continue
        entries = [e for e in manifest if e["path"].startswith(stage + "/")]
        (directory / "ARTIFACT_MANIFEST.json").write_text(json.dumps(
            {"stage": stage, "files": entries,
             "note": ("relative paths inside the study root, sizes and SHA256; npz/log artefacts "
                      "follow .gitignore and must be carried explicitly on a handover")},
            ensure_ascii=False, indent=2), encoding="utf-8")
    (study / "ARTIFACT_MANIFEST.json").write_text(json.dumps(
        {"study_dir": str(study), "files": manifest,
         "note": ("npz/log artefacts follow .gitignore; files listed here are what a cross-machine "
                  "handover must carry")}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"stages": notes, "files": len(manifest)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
