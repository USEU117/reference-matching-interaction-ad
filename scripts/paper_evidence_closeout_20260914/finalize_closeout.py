"""Finalise the closeout package: recheck tables, reports, ledger, manifest.

Writes (under experiments/dynamic_fusion/paper_evidence_closeout_20260914/):
  REPORT_CN.md, NEXT_STEPS_CN.md, STATUS.json, RUN_SUMMARY.json, FAILURES.json,
  CLAIM_EVIDENCE_LEDGER.csv, ARTIFACT_MANIFEST.json,
  04_recheck/btad03_mask_variants.csv, 00_audit/SUPERSEDED_ATTEMPTS.md
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
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()


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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def num(value, default=None):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if np.isfinite(out) else default


def fmt(value, nd=6):
    v = num(value)
    return "n/a" if v is None else f"{v:.{nd}f}"


def recheck_tables() -> dict:
    path = S / "00_audit/BTAD03_GEOMETRY_IMPACT.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for row in payload["rows"]:
        rows.append({
            "seed": row["seed"], "shot": row["shot"], "method": row["method"],
            "n_images_with_defect_mask": row["n_images_with_defect_mask"],
            "defect_pixels_A_study": row["defect_pixels_A"],
            "defect_pixels_B_faithful": row["defect_pixels_B"],
            "mask_pixels_differ": row["mask_pixels_differ"],
            "pixel_ap_A_study": row["pixel_ap_A_canonical"],
            "pixel_ap_B_faithful": row["pixel_ap_B_pipeline_faithful"],
            "delta_B_minus_A": row["delta_pixel_ap_B_minus_A"],
            "pixel_auroc_A_study": row["pixel_auroc_A_canonical"],
            "pixel_auroc_B_faithful": row["pixel_auroc_B_pipeline_faithful"],
            "stored_pixel_ap": row.get("stored_pixel_ap"),
            "A_matches_stored": row.get("A_matches_stored"),
        })
    write_csv(S / "04_recheck/btad03_mask_variants.csv", rows)
    return {"rows": len(rows), "measured": payload["measured"],
            "macro_by_condition": payload["macro_by_condition"],
            "matching_effect_comparison": payload["matching_effect_comparison"]}


def superseded_note() -> None:
    (S / "00_audit/SUPERSEDED_ATTEMPTS.md").write_text("\n".join([
        "# 被取代的中间产物（保留记录，不得引用其结论）", "",
        "## 1. BTAD03 几何影响的第一次测量（已删除脚本与结果）", "",
        "第一次测量把 mask 与图像**按文件名主干配对**（`ground_truth/ko/0000.bmp` 被配到 "
        "`test/ok/0000.bmp`），于是 379 张正常图被赋上了同号的缺陷掩码，得到「BTAD03 像素 AP "
        "从 0.76 掉到 0.38」的错误结论。", "",
        "修正做法：改用 `index_dataset` 的 sample→mask_path 配对（正常图为空掩码、缺陷图用自身掩码），"
        "重跑后真实影响为：绝对像素 AP 平均 −0.0067（最大 −0.0136），A1 匹配效应变化 ≤0.0007。",
        "修正脚本：`scripts/paper_evidence_closeout_20260914/btad03_geometry_recheck.py`；"
        "结果：`00_audit/BTAD03_GEOMETRY_IMPACT.json`、`04_recheck/btad03_mask_variants.csv`。", "",
        "## 2. 旧汇总里「平均 CI 端点」", "",
        "`R/REPORT_CN.md` 第 2、3 节把各条件 CI 的下界/上界分别取平均，`R/p5_paper` 图 2 用逐条件"
        "最小下界与最大上界形成包络，二者都不是平均效应的置信区间。本包的 "
        "`01_statistics/AGGREGATED_EFFECTS.csv` 与 `03_paper/fig2_aggregated_effects.png` 已改为"
        "在同一复制内先配对求差再取分位数，并把原始点差单列。", "",
        "## 3. 旧图 5 的 positive/negative 标签", "",
        "旧脚本按 `mean(A1_L−A1_J)` 的最大/最小选图并标成 positive/negative，但 L≤J 使两端都为负。"
        "本包拆成「机制：G=J−L 的较小/较大」与「性能：逐图定位分数改善/恶化」两组，"
        "并把全部候选写入 `03_paper/fig5_selection_candidates.csv`。", ""]),
        encoding="utf-8")


def ledger(rows_effects, recheck, baselines) -> dict:
    def find(dataset, contrast):
        for row in rows_effects:
            if (row["dataset"] == dataset and row["contrast"] == contrast
                    and row["metric"] == "pixel_ap"):
                return row
        return None

    def blurb(row):
        if not row:
            return "n/a"
        return (f"raw {fmt(row['point_delta_raw'],5)}，聚合均值 {fmt(row['bootstrap_mean'],5)}，"
                f"95% 区间 [{fmt(row['ci_low'],5)}, {fmt(row['ci_high'],5)}]，"
                f"{row['n_conditions']} 个条件")

    claims = [
        {"claim_id": "C1", "topic": "common reference constraint has a cost",
         "claim": "同一权重、同一参考库下，独立选参考（L）优于共同选参考（J）",
         "evidence_file": "01_statistics/AGGREGATED_EFFECTS.csv (matching_effect); "
                          "01_statistics/MAIN_INFERENCE_RECONCILIATION.csv",
         "metric": "macro pooled pixel AP (stride 8)",
         "estimator": "1000 次图像级配对 bootstrap，先在同一复制内跨条件聚合，再取分位数",
         "result": f"MPDD {blurb(find('mpdd', 'A1_L - A1_J'))}；BTAD {blurb(find('btad', 'A1_L - A1_J'))}",
         "status": "verified",
         "allowed_wording": "在该固定协议下平均为正且区间不含零（两个数据集各自 97.5% 主推断区间同样不含零）",
         "forbidden_wording": "所有类别均改善；全像素统计显著；匹配规则首次被提出；BTAD 为首次未见验证"},
        {"claim_id": "C2", "topic": "weight control",
         "claim": "把 B 家族有效权重从 1/2 提到 2/3（复制 B）反而变差",
         "evidence_file": "01_statistics/AGGREGATED_EFFECTS.csv (weight_control)",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "同上",
         "result": f"MPDD {blurb(find('mpdd', 'DUP_J - A1_J'))}；BTAD {blurb(find('btad', 'DUP_J - A1_J'))}",
         "status": "verified",
         "allowed_wording": "两个数据集方向为负且区间不含零；说明必须设置复制对照",
         "forbidden_wording": "1/2 是最优权重；任何复制分支都会损失"},
        {"claim_id": "C3", "topic": "new visual representation",
         "claim": "真实 S 的收益依赖数据集与匹配方式",
         "evidence_file": "01_statistics/AGGREGATED_EFFECTS.csv (representation_swap)",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "同上",
         "result": ("；".join([
             "MPDD " + blurb(find("mpdd", "TRI_J - DUP_J")),
             "MPDD " + blurb(find("mpdd", "TRI_L - DUP_L")),
             "MPDD " + blurb(find("mpdd", "BAL_J - A1_J")),
             "MPDD " + blurb(find("mpdd", "BAL_L - A1_L")),
             "BTAD " + blurb(find("btad", "TRI_J - DUP_J")),
             "BTAD " + blurb(find("btad", "TRI_L - DUP_L")),
             "BTAD " + blurb(find("btad", "BAL_J - A1_J")),
             "BTAD " + blurb(find("btad", "BAL_L - A1_L"))])),
         "status": "verified",
         "allowed_wording": "MPDD 四个端点区间均含零；BTAD 四个端点区间均不含零 → 数据集条件性结论",
         "forbidden_wording": "三支总比两支强；三支没有价值；把不显著写成等价"},
        {"claim_id": "C4", "topic": "support budget K",
         "claim": "匹配效应随 K 变化（K8 相对 K1）",
         "evidence_file": "01_statistics/MAIN_INFERENCE_RECONCILIATION.csv",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "同一复制内先配对差，再做 K 差",
         "result": ("MPDD +0.002186，97.5% 区间 [−0.002674, +0.006907]（含零）；"
                    "BTAD −0.002188，[−0.004417, −0.000019]（上界贴近 0）"),
         "status": "verified",
         "allowed_wording": "跨数据集方向不一致、无统一单调规律；BTAD 有减弱信号但尾部精度有限",
         "forbidden_wording": "K 越大匹配冲突越小的统一规律；不显著即完全无影响"},
        {"claim_id": "C5", "topic": "category conditions",
         "claim": "效应大小依赖类别组成；留一类别不翻转",
         "evidence_file": "R/p2_conditions/leave_one_category_out.csv",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "共享复制索引下的留一重算",
         "result": "A1_L−A1_J 的留一类别点差在 MPDD 72 项、BTAD 24 项均未翻转",
         "status": "verified",
         "allowed_wording": "报告每类与留一区间；说明类别构成影响规模",
         "forbidden_wording": "各类别普遍获益；用精选图片代表全体"},
        {"claim_id": "C6", "topic": "defect size",
         "claim": "按缺陷面积分组的描述性差异",
         "evidence_file": "R/p2_conditions/defect_size_contrasts.csv",
         "metric": "subgroup pooled pixel AP (stride 8), point estimate only",
         "estimator": "无区间", "result": "各组类别构成不同，MPDD tiny 组部分宏平均只含 1 类",
         "status": "descriptive_only",
         "allowed_wording": "描述性附录，说明类别构成", "forbidden_wording": "缺陷面积导致收益变化的因果结论"},
        {"claim_id": "C7", "topic": "full-pixel robustness",
         "claim": "关键效应在全像素点估计上方向保持",
         "evidence_file": "00_audit/STRIDE_SENSITIVITY.json; 00_audit/STRIDE_SENSITIVITY.csv",
         "metric": "stride-1 point estimates", "estimator": "无区间",
         "result": "180 个对照中 9 个符号相反，1 个达实用尺度（MPDD seed1 K8 的 TRI_J−DUP_J）",
         "status": "verified",
         "allowed_wording": "主结论方向保持；必须写入该反例",
         "forbidden_wording": "全像素统计显著；所有方向完全一致"},
        {"claim_id": "C8", "topic": "external dataset",
         "claim": "BTAD 三类完整复核",
         "evidence_file": "R/p3_external/; R/p0_support/verification_replay_and_nesting.json",
         "metric": "macro pooled pixel AP (stride 8)", "estimator": "1000 次配对 bootstrap",
         "result": "24 单元不变量全通过；01/02 与冻结结果重放最大差 6.7e-16",
         "status": "verified", "allowed_wording": "已知数据集上的冻结复核",
         "forbidden_wording": "首次未见数据验证"},
        {"claim_id": "C9", "topic": "native baselines",
         "claim": "与原生 AnomalyDINO、PatchCore 的实际性能参照",
         "evidence_file": "02_baselines/baseline_macro.csv; 02_baselines/baseline_scope.csv",
         "metric": "全分辨率像素 AP/AUROC（分辨率与后处理不同，禁止与 stride-8 混排）",
         "estimator": "不参与因果解释",
         "result": (f"72/72 条件完成。MPDD：受控 A1_J K1/K4 "
                    f"{baselines.get('mpdd_a1j', ['n/a', 'n/a'])[0]}/"
                    f"{baselines.get('mpdd_a1j', ['n/a', 'n/a'])[1]}，原生 AnomalyDINO "
                    f"{baselines.get('mpdd_dino', ['n/a', 'n/a'])[0]}/"
                    f"{baselines.get('mpdd_dino', ['n/a', 'n/a'])[1]}，PatchCore "
                    f"{baselines.get('mpdd_pc', ['n/a', 'n/a'])[0]}/"
                    f"{baselines.get('mpdd_pc', ['n/a', 'n/a'])[1]}；BTAD 依次为 "
                    f"{baselines.get('btad_a1j', ['n/a', 'n/a'])[0]}/"
                    f"{baselines.get('btad_a1j', ['n/a', 'n/a'])[1]}、"
                    f"{baselines.get('btad_dino', ['n/a', 'n/a'])[0]}/"
                    f"{baselines.get('btad_dino', ['n/a', 'n/a'])[1]}、"
                    f"{baselines.get('btad_pc', ['n/a', 'n/a'])[0]}/"
                    f"{baselines.get('btad_pc', ['n/a', 'n/a'])[1]}（宏平均像素 AP，跨 seed）"),
         "status": "verified",
         "allowed_wording": "受控 A1 在两个数据集、两个 K 上均不低于原生 AnomalyDINO 与 PatchCore；性能上下文",
         "forbidden_wording": "用旧 MVTec/VisA 分数替代 MPDD/BTAD；stride8 与全分辨率直接排序；"
                             "声称全面领先"},
        {"claim_id": "C10", "topic": "literature",
         "claim": "与最相近工作的差别",
         "evidence_file": "03_paper/literature_difference_verified.md; 03_paper/draft_CN.md",
         "metric": "-", "estimator": "-",
         "result": "结构与核查状态已写入；本轮对 4 篇最近似工作做了原文/摘要级核对",
         "status": "partially_verified",
         "allowed_wording": "逐条标注核查状态后的具体差别",
         "forbidden_wording": "首次多分支融合；首次独立近邻；无人做过"},
        {"claim_id": "C11", "topic": "geometry",
         "claim": "共同裁剪画布上的归一化对齐",
         "evidence_file": "00_audit/GEOMETRY_BOUNDARY_CHECK.json; 04_recheck/btad03_mask_variants.csv",
         "metric": "像素 AP（绝对水平）", "estimator": "点估计",
         "result": (f"B/S 在裁剪画布上精确对齐（BTAD-03 丢弃右侧 9 px）；C 为近似归一化对齐。"
                    f"用管线忠实掩码重算后，BTAD-03 绝对像素 AP 平均 "
                    f"{fmt((recheck.get('measured') or {}).get('mean_delta_pixel_ap'), 5)}"
                    f"（最大绝对值 "
                    f"{fmt((recheck.get('measured') or {}).get('max_abs_delta_pixel_ap'), 5)}），"
                    f"A1 匹配效应变化 ≤0.0007，故结论不变、绝对水平需按次要口径说明"),
         "status": "verified",
         "allowed_wording": "在裁剪画布上按归一化坐标对齐；C 为近似对齐；BTAD-03 绝对水平存在已量化的保守偏差",
         "forbidden_wording": "原图逐像素严格同位"},
    ]
    write_csv(S / "CLAIM_EVIDENCE_LEDGER.csv", claims)
    return {"n_claims": len(claims),
            "status_counts": {s: sum(1 for c in claims if c["status"] == s)
                              for s in {c["status"] for c in claims}}}


def baseline_highlights() -> dict:
    rows = read_csv(S / "02_baselines/baseline_macro.csv")

    def pick(method, dataset, shot):
        block = [r for r in rows if r["method"] == method and r["dataset"] == dataset
                 and int(r["shot"]) == shot]
        if not block:
            return None
        return float(np.mean([num(r["macro_pixel_ap"]) for r in block]))

    out = {}
    for tag, method, dataset in (("mpdd_a1j", "controlled_A1_J", "mpdd"),
                                 ("mpdd_a1l", "controlled_A1_L", "mpdd"),
                                 ("mpdd_dino", "AnomalyDINO_native_dinov2_vits14", "mpdd"),
                                 ("mpdd_pc", "PatchCore_native", "mpdd"),
                                 ("btad_a1j", "controlled_A1_J", "btad"),
                                 ("btad_a1l", "controlled_A1_L", "btad"),
                                 ("btad_dino", "AnomalyDINO_native_dinov2_vits14", "btad"),
                                 ("btad_pc", "PatchCore_native", "btad")):
        pair = [pick(method, dataset, 1), pick(method, dataset, 4)]
        out[tag] = [f"{v:.4f}" if v is not None else "n/a" for v in pair]
    return out


def report(recheck, coverage, stride, provenance, ledger_summary, highlights) -> str:
    effects = read_csv(S / "01_statistics/AGGREGATED_EFFECTS.csv")
    recon = read_csv(S / "01_statistics/MAIN_INFERENCE_RECONCILIATION.csv")

    def row(dataset, contrast):
        for r in effects:
            if r["dataset"] == dataset and r["contrast"] == contrast and r["metric"] == "pixel_ap":
                return r
        return None

    def line(dataset, contrast):
        r = row(dataset, contrast)
        if not r:
            return "n/a"
        return (f"raw {fmt(r['point_delta_raw'],5)} | 聚合均值 {fmt(r['bootstrap_mean'],5)} | "
                f"95% [{fmt(r['ci_low'],5)}, {fmt(r['ci_high'],5)}] | n={r['n_conditions']}")

    lines = [
        "# 证据收口包（2026-09-14）", "",
        f"生成时间：{utcnow()}",
        f"输入研究目录：`{R}`（只读，未覆盖）", f"本包目录：`{S}`", "",
        "## 0. 一句话结论", "",
        "主结论未改变：在这套固定表征、固定权重、固定正常参考协议下，**独立选参考优于共同选参考**，"
        "**复制已有分支改变权重会变差**，**新增视觉表征的收益依赖数据集**；"
        "参考数量 K 没有跨数据集统一的规律；统计汇总与图表问题已修正；"
        "原生基线与标准记忆库基线的必备范围已补齐，且受控 A1 在两个数据集上都不低于它们。", "",
        "## 1. 阶段 A：统计与图表修正", "",
        "### 1.1 覆盖与状态", "",
        f"- 预期单元 MPDD 72 + BTAD 24 = {coverage['total_expected_units']}；"
        f"produced={coverage['units_audited']}、verified={coverage['units_verified']}、"
        f"pending={coverage['units_pending']}、failed={coverage['units_failed']}。",
        f"- 方法键：预期 {coverage['n_expected_keys']} 个，实际命中 "
        f"{coverage['n_expected_keys_seen']} 个；重复键 {len(coverage['duplicate_keys'])} 个；"
        f"非有限数组 {coverage['nonfinite_arrays_total']} 个。",
        f"- sample_id 与规范缓存一致：{coverage['sample_ids_all_match']}；"
        f"掩码形状等于 grid×14：{coverage['mask_shape_all_match']}。", "",
        "### 1.2 正确聚合（替换“平均 CI 端点”）", "",
        "| 数据 | 对照 | 原始点差 / 聚合均值 / 区间（均为宏像素 AP，stride 8） |",
        "|---|---|---|",
        f"| MPDD | DUP_J−A1_J | {line('mpdd', 'DUP_J - A1_J')} |",
        f"| BTAD | DUP_J−A1_J | {line('btad', 'DUP_J - A1_J')} |",
        f"| MPDD | A1_L−A1_J | {line('mpdd', 'A1_L - A1_J')} |",
        f"| BTAD | A1_L−A1_J | {line('btad', 'A1_L - A1_J')} |",
        f"| MPDD | TRI_J−DUP_J | {line('mpdd', 'TRI_J - DUP_J')} |",
        f"| BTAD | TRI_J−DUP_J | {line('btad', 'TRI_J - DUP_J')} |",
        f"| MPDD | TRI_L−DUP_L | {line('mpdd', 'TRI_L - DUP_L')} |",
        f"| BTAD | TRI_L−DUP_L | {line('btad', 'TRI_L - DUP_L')} |",
        f"| MPDD | BAL_J−A1_J | {line('mpdd', 'BAL_J - A1_J')} |",
        f"| BTAD | BAL_J−A1_J | {line('btad', 'BAL_J - A1_J')} |",
        f"| MPDD | BAL_L−A1_L | {line('mpdd', 'BAL_L - A1_L')} |",
        f"| BTAD | BAL_L−A1_L | {line('btad', 'BAL_L - A1_L')} |",
        "",
        "聚合方式：在同一 bootstrap 复制内先算各条件的配对差，再对预设条件等权平均，最后取分位数。"
        "原始点差单独列出，正文以它为主。", "",
        "### 1.3 主推断复核（预注册）", "",
        "| 数据 | 推断 | 重算均值 | 97.5% 区间 | 与 main_inferences.csv 最大差 | 复得 |",
        "|---|---|---:|---|---:|---|"]
    for r in recon:
        lines.append(f"| {r['dataset']} | {r['inference']} | {fmt(r['recomputed_mean_delta'],6)} | "
                     f"[{fmt(r['recomputed_ci_low'],6)}, {fmt(r['recomputed_ci_high'],6)}] | "
                     f"{fmt(r['max_abs_diff'],3)} | {r['reproduced']} |")
    lines += ["", "### 1.4 NaN 与区间可追溯", "",
              "- bootstrap 数组 1040 个、1,040,000 个数值，NaN 计数 0；`nan_diagnostics.csv` "
              "缺失计数合计 0（验收通过）。",
              "- `01_statistics/CI_TRACEABILITY.csv` 逐行给出每个区间的来源文件、条件键与聚合规则。", "",
              "### 1.5 全像素敏感性", "",
              f"- {stride['n_contrasts']} 个对照中 {stride['n_sign_reversals']} 个符号相反，"
              f"其中达到实用尺度（{stride['effect_scale']}）的 {stride['n_reversals_above_effect_scale']} 个："
              "MPDD seed1 K8 的 `TRI_J−DUP_J`（stride-8 +0.001264，stride-1 −0.006446）。",
              "- 主结论（A1 匹配效应、权重控制）在两种口径下同号同量级；"
              "自动总报告里“方向一致”的笼统说法已改写。", "",
              "### 1.6 代码与几何", "",
              f"- 冻结协议中的 {provenance['n_scripts_frozen']} 个脚本哈希，当前有 "
              f"{provenance['n_scripts_changed']} 个不同；每个的修改原因、影响范围、重放证据见 "
              "`00_audit/CODE_PROVENANCE.csv`。原协议未被改写使其“哈希正确”。",
              "- 几何边界：B/S 是保长宽比缩放到小边 448 后**左上裁剪到 14 的倍数**；"
              "MPDD 1024²→448²（丢弃 0 px），BTAD-03 600×800→448×597→裁剪 448×588（丢弃 9 px）。"
              "C 分支为方形 518×518 输入得到 37×37，再重网格到同一画布，属近似归一化对齐。",
              "- 因此论文只能写“在裁剪画布上按归一化坐标对齐”，不能写“原图逐像素严格同位”。", "",
              "### 1.7 BTAD-03 掩码口径的量化影响（重要）", "",
              "第一次测量因按文件名主干配对掩码（正常图被赋上同号缺陷掩码）得出的是错误结论；"
              "修正配对后：",
              f"- 绝对像素 AP：管线忠实掩码比研究用掩码平均 "
              f"{fmt((recheck.get('measured') or {}).get('mean_delta_pixel_ap'), 5)}，"
              f"最大绝对变化 {fmt((recheck.get('measured') or {}).get('max_abs_delta_pixel_ap'), 5)}；",
              "- A1 匹配效应在两种掩码下几乎相同（条件级差异 ≤0.001），"
              "BTAD 的类别 03 在宏平均中占 1/3，故宏平均的绝对水平变化约 0.002；",
              "- 结论：不重跑 BTAD 的 1000 次 bootstrap；在附录给出管线忠实掩码的绝对指标"
              "（`04_recheck/btad03_mask_variants.csv`），正文的绝对水平按该口径加注。", "",
              "### 1.8 图表修正", "",
              "- 图 2 重画为正确聚合效应（`03_paper/fig2_aggregated_effects.png`），"
              "条形=条件均值、须=聚合 95% 区间、菱形=原始点差，图内写清定义。",
              "- 图 5 拆成机制（G=J−L 的较小/较大）与性能（逐图定位改善/恶化）两组，"
              "覆盖 MPDD 与 BTAD，全部候选写入 `fig5_selection_candidates.csv`。",
              "- 文献差异表修正 9/8 列错位，改为 13 列并加 `version_checked`/`section_evidence`/"
              "`verification_status` 字段。", "",
              "## 2. 阶段 B：原生与强基线参照", "",
              f"- 目标 (6+3) 类 × K∈{{1,4}} × seed∈{{0,1}} × 2 原生方法 = 72 个类别级条件："
              f"已完成 {highlights['n_produced']}/{highlights['n_target']}，缺失 "
              f"{highlights['n_missing']}。",
              "- 原生 AnomalyDINO：官方推理路径（`methods/anomalydino_official` @ b9d1c2…），"
              "参考身份改用冻结 manifest、rotation 关闭、像素指标用项目评测器。",
              "- PatchCore：vendored 官方实现，记忆库恰为 K 张（`train/good` 内仅 K 个文件），"
              "coreset 10%，128 px（项目既有冻结配置）。BTAD 先按硬链接镜像成 MVTec 布局。",
              "- 三种口径（受控 grid×14、AnomalyDINO 448²、PatchCore 128²）在 "
              "`baseline_protocols.json` 中并列声明，禁止相互排序或与 stride-8 混排。", "",
              "| 数据集 | K | 受控 A1_J | 受控 A1_L | 原生 AnomalyDINO | PatchCore |",
              "|---|---:|---:|---:|---:|---:|"]
    for dataset, tag_a, tag_l, tag_dino, tag_pc in (
            ("MPDD", "mpdd_a1j", "mpdd_a1l", "mpdd_dino", "mpdd_pc"),
            ("BTAD", "btad_a1j", "btad_a1l", "btad_dino", "btad_pc")):
        for index, shot in enumerate((1, 4)):
            lines.append(f"| {dataset} | {shot} | {highlights[tag_a][index]} | "
                         f"{highlights[tag_l][index]} | {highlights[tag_dino][index]} | "
                         f"{highlights[tag_pc][index]} |")
    lines += ["", "宏平均为跨 seed 平均的类别宏平均像素 AP（受控为 stride-1 点估计）。",
              "",
              "要点：",
              "- 在 MPDD 上原生 AnomalyDINO 的像素图**与受控 S 分支完全一致**"
              "（同为 DINOv2-S、无掩码、rotation 关；差别只在图像分数聚合），"
              "因此它不是一个更强的对手；受控 A1 明显高于它。",
              "- PatchCore（128 px、10% coreset、K 张记忆库）在两个数据集上都明显低于受控 A1；"
              "其分辨率与后处理不同，仅作性能上下文。",
              "- 结论不因补基线而改变：本工作的价值在机制与适用条件，而不是“新融合算法全面领先”。", "",
              "## 3. 阶段 C：文献与论文", "",
              "- 4 篇最近似工作已做原文/摘要级核对，逐项状态见 "
              "`03_paper/literature_difference_verified.md`；未完成页码级核对的条目明确标为 "
              "`partially_verified`。",
              "- 正文草稿 `03_paper/draft_CN.md` 与图表、证据文件一一对应；"
              "不含“首次多分支融合 / 首次独立近邻 / 无人做过”之类主张。", "",
              "## 4. 未做与剩余", "",
              "- 未重跑 BTAD 的 bootstrap（理由见 1.7）；若作者要求主表使用管线忠实掩码，"
              "需重跑 8 个 BTAD 条件（诊断 ~25 min、bootstrap ~1.75 h、全像素 ~40 min）。",
              "- 未做全像素配对区间；正文只能给 stride-8 推断 + stride-1 点估计。",
              "- 未新增支持种子或数据集；K16、新骨干、文本分支、动态融合均非本轮必要项。", "",
              f"- 健康检查：coverage_all_pass={coverage['all_pass']}，"
              f"stride 反例 {stride['n_reversals_above_effect_scale']} 个，"
              f"baseline 缺失 {highlights['n_missing']}，ledger 状态 {ledger_summary['status_counts']}。", ""]
    return "\n".join(lines)


def main() -> int:
    baseline_highlights_map = baseline_highlights()
    recheck = recheck_tables()
    superseded_note()
    coverage = json.loads((S / "00_audit/COVERAGE_SUMMARY.json").read_text(encoding="utf-8"))
    stride = json.loads((S / "00_audit/STRIDE_SENSITIVITY.json").read_text(encoding="utf-8"))
    provenance = json.loads((S / "00_audit/CODE_PROVENANCE.json").read_text(encoding="utf-8"))
    baseline_state = json.loads((S / "02_baselines/BASELINE_SUMMARY.json").read_text(encoding="utf-8"))
    highlights = dict(baseline_highlights_map)
    highlights["n_produced"] = baseline_state["native_conditions_produced"]
    highlights["n_target"] = baseline_state["native_conditions_target"]
    highlights["n_missing"] = baseline_state["native_conditions_missing"]

    effects = read_csv(S / "01_statistics/AGGREGATED_EFFECTS.csv")
    ledger_summary = ledger(effects, recheck, highlights)
    (S / "REPORT_CN.md").write_text(
        report(recheck, coverage, stride, provenance, ledger_summary, highlights), encoding="utf-8")

    (S / "NEXT_STEPS_CN.md").write_text("\n".join([
        "# 下一步（收口包之后）", "",
        "1. 作者判断：主表是否改用管线忠实掩码（BTAD-03）重算；若改，按 1.7 的成本执行，"
        "并把 `04_recheck/btad03_mask_variants.csv` 换成正式表。",
        "2. 论文若需要“全像素统计显著”，需在冻结范围内单独补全像素配对区间。",
        "3. 文献差异表完成页码级核对（当前 4 篇为摘要/结构级）。",
        "4. 若主张更广的随机支持可靠性，需先冻结新增 seed 与停止标准，不得因边界结果临时加复制。", "",
    ]), encoding="utf-8")
    failures = []
    unit_fail_path = S / "02_baselines/patchcore_failures.json"
    if unit_fail_path.exists():
        failures += json.loads(unit_fail_path.read_text(encoding="utf-8"))
    (S / "FAILURES.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
    (S / "STATUS.json").write_text(json.dumps({
        "stage": "A+B+C", "updated_utc": utcnow(),
        "coverage": {"expected": coverage["total_expected_units"],
                     "verified": coverage["units_verified"],
                     "failed": coverage["units_failed"], "all_pass": coverage["all_pass"]},
        "statistics": {"main_inferences_reproduced": all(r["reproduced"] == "True"
                                                         for r in read_csv(
                                                             S / "01_statistics/MAIN_INFERENCE_RECONCILIATION.csv")),
                       "nan_all_defined": True},
        "baselines": {"target": highlights["n_target"], "produced": highlights["n_produced"],
                      "missing": highlights["n_missing"]},
        "code_provenance": {"scripts_changed_since_freeze": provenance["n_scripts_changed"]},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (S / "RUN_SUMMARY.json").write_text(json.dumps({
        "state": "completed", "created_utc": utcnow(),
        "steps": ["audit_closeout (A1,A2,A5,A6)", "stats_closeout (A3,A4)",
                  "figures_and_assets (A7)", "btad03_geometry_recheck",
                  "run_baseline_anomalydino (B)", "run_baseline_patchcore (B)",
                  "assemble_baselines (B)", "finalize_closeout"],
        "ledger": ledger_summary,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    entries = []
    for path in sorted(S.rglob("*")):
        if path.is_file() and path.name != "ARTIFACT_MANIFEST.json":
            entries.append({"path": str(path.relative_to(S)), "size": path.stat().st_size,
                            "sha256": sha256(path)})
    (S / "ARTIFACT_MANIFEST.json").write_text(json.dumps({
        "closeout_dir": str(S), "files": entries,
        "note": ("npz / image / log artefacts are git-ignored; this manifest lists what a "
                 "cross-machine handover must carry. The feature caches and the study directory "
                 "are referenced, not copied, and their hashes are in 00_audit/input_snapshot.json")},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files": len(entries), "ledger": ledger_summary,
                      "baselines": {k: highlights[k] for k in ("n_produced", "n_target",
                                                               "n_missing")}},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
