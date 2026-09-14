"""Render the R1 hand-over documents from the artifacts the analyze stage wrote.

This file is deliberately *separate* from ``run_seed1_triple.py``: the analyze
stage recorded the SHA256 of that script inside ``PROTOCOL.json``, so editing it
after the run would break the recorded code identity.  The renderer only reads
the frozen CSVs and unit records and writes:

* ``per_category.csv`` and ``per_category_contrasts.csv`` (the per-class tables
  the hand-over requires but the analyze stage aggregates away),
* ``REPORT_CN.md`` / ``NEXT_STEPS_CN.md``,
* ``POST_RUN_NOTES.json`` (what was added after the run and when),
* a refreshed ``ARTIFACT_MANIFEST.json`` that includes those files.

No frozen number is recomputed or rewritten.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import complete_statistics as cs  # noqa: E402
import run_seed1_triple as rst  # noqa: E402

R1 = rst.NEXT / "R1_seed1_triple"
SEED0_ROOT = R1 / "seed0_same_caliber"
METRIC_KEYS = ("pixel_auroc", "pixel_ap", "image_auroc", "image_ap")


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                          encoding="utf-8")


def read_metrics(path: Path) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with path.open(encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            values = {}
            for key in METRIC_KEYS + ("pixel_aupro", "image_f1_max"):
                raw = row.get(key)
                values[key] = None if raw in (None, "", "None") else float(raw)
            rows[row["method"]] = values
    return rows


def collect(seed: int) -> list[dict]:
    root = R1 if seed == 1 else SEED0_ROOT
    methods = rst.TRIPLE_DETECTORS if seed == 1 else rst.SEED0_FAIR_METHODS + ["DUP_L"]
    units = []
    for shot in rst.SHOTS:
        for cat in rst.CATEGORIES:
            unit = root / "units" / f"s{seed}_k{shot}" / cat
            done = read_json(unit / "DONE.json")
            metrics = read_metrics(unit / "metrics.csv")
            missing = [m for m in methods if m not in metrics]
            if missing:
                raise SystemExit(f"{unit}/metrics.csv is missing {missing}")
            units.append({"seed": seed, "shot": shot, "category": cat, "done": done,
                          "metrics": {m: metrics[m] for m in methods}})
    return units


def main() -> int:
    units = collect(1) + collect(0)
    methods_by_seed = {1: rst.TRIPLE_DETECTORS, 0: rst.SEED0_FAIR_METHODS + ["DUP_L"]}

    rows = []
    for unit in units:
        for method, values in unit["metrics"].items():
            rows.append({"reference_seed": unit["seed"], "shot": unit["shot"],
                         "category": unit["category"], "method": method,
                         "pixel_stride": 8, **values})
    cs.write_csv(R1 / "per_category.csv",
                 ["reference_seed", "shot", "category", "method", "pixel_stride", "pixel_auroc",
                  "pixel_ap", "pixel_aupro", "image_auroc", "image_ap", "image_f1_max"], rows)

    index = {(u["seed"], u["shot"], u["category"]): u for u in units}
    contrast_rows = []
    for seed, methods in methods_by_seed.items():
        for shot in rst.SHOTS:
            for left, right, group in rst.FAIR_CONTRASTS:
                if left not in methods or right not in methods:
                    continue
                label = f"{left} - {right}"
                for cat in rst.CATEGORIES:
                    unit = index[(seed, shot, cat)]
                    contrast_rows.append({
                        "reference_seed": seed, "shot": shot, "category": cat, "contrast": label,
                        "contrast_group": group, "metric": "pixel_ap",
                        "delta": unit["metrics"][left]["pixel_ap"] - unit["metrics"][right]["pixel_ap"]})
    cs.write_csv(R1 / "per_category_contrasts.csv",
                 ["reference_seed", "shot", "category", "contrast", "contrast_group", "metric", "delta"],
                 contrast_rows)

    verification = read_json(R1 / "verification.json")
    summary = read_json(R1 / "RUN_SUMMARY.json")
    # The analyze stage named this table ``fair_contrasts.csv``.  The hand-over
    # convention asks for ``paired_deltas.csv``, so the identical rows are also
    # written under that name (a byte copy, recorded in POST_RUN_NOTES.json).
    fair_table = R1 / "fair_contrasts.csv"
    paired_table = R1 / "paired_deltas.csv"
    if not paired_table.exists() or paired_table.read_bytes() != fair_table.read_bytes():
        paired_table.write_bytes(fair_table.read_bytes())
    paired = list(csv.DictReader(fair_table.open(encoding="utf-8-sig")))
    gate = read_json(rst.GATE)

    def cell(value, digits=6):
        return "n/a" if value in (None, "") else f"{float(value):.{digits}f}"

    lines = ["# R1：seed-1 真实三支复核与表示×匹配的公平对照", "",
             f"输出目录：`{R1}`", f"报告生成时间：{now()}（分析运行完成后单独渲染）", "",
             "## 1. 范围与冻结口径", "",
             "- 数据：MPDD（development），seed 1 真实三支 B/S/C；同时用同口径重建 seed 0 缺失端点 `DUP_L`。",
             "- 网格：32×32；各支单位化；精确 1-NN；448 双线性 + Gaussian σ=4；图像分数取最大值；stride-8 评价。",
             "- K2 由该 seed 的 K4 前两张参考构造（`canonical_source_shot=4`）。",
             "- 图像级配对 bootstrap，`default_rng([20260912, shot, replicate])`，两个 K 各 1000 次；"
             "主要指标为宏像素 AP，实用尺度 0.005；**未做多重比较校正**。",
             "- 两个 seed 共用同一测试集与同一复制索引，因此 **不独立**：分别报告，不合并为独立样本。", "",
             "## 2. 输入身份与不变量", "",
             f"- R0 身份门控：`all_pass={gate.get('all_pass')}`（`{rst.GATE}`）。",
             f"- seed-1 三支单元：{verification['acceptance']['seed1_units']}/"
             f"{verification['acceptance']['expected_units']}，单元不变量全通过："
             f"{verification['acceptance']['unit_invariants_all_pass']}。",
             f"- 复制数：seed1 {verification['acceptance']['replicates_used_seed1']}，"
             f"seed0 {verification['acceptance']['replicates_used_seed0']}。",
             "- 每个单元的 DUP 等价、共同置换、FAISS 真实 patch 对照、G≥0、分数分解都在 "
             "`units/s1_k*/类别/invariants.json` 中逐项记录。", "",
             "## 3. 公平对照（宏像素 AP，图像配对 bootstrap）", "",
             "| seed | K | 对照 | 组 | 点差 | 95% 区间 | 不含零 |", "|---|---:|---|---|---:|---|---|"]

    for row in paired:
        if row["metric"] != "pixel_ap":
            continue
        lo, hi = float(row["ci_low"]), float(row["ci_high"])
        lines.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['contrast_group']} | {cell(row['point_delta'])} | "
                     f"[{cell(lo)}, {cell(hi)}] | {bool(lo > 0 or hi < 0)} |")

    lines += ["", "## 4. 逐类点差（stride-8，未做区间）", "",
              "| seed | K | 对照 | 正向类别 | 负向类别 | 正向类数/负向类数 |", "|---|---:|---|---|---|---|"]
    grouped: dict[tuple, list[dict]] = {}
    for row in contrast_rows:
        grouped.setdefault((row["reference_seed"], row["shot"], row["contrast"]), []).append(row)
    for key in sorted(grouped):
        block = grouped[key]
        positive = [r["category"] for r in block if r["delta"] > 0]
        negative = [r["category"] for r in block if r["delta"] < 0]
        lines.append(f"| {key[0]} | {key[1]} | {key[2]} | {';'.join(positive) or '（无）'} | "
                     f"{';'.join(negative) or '（无）'} | {len(positive)}/{len(negative)} |")

    lines += ["", "## 5. 结论边界", "",
              "- 主要对比在运行前冻结：表示效应 `TRI_J−DUP_J`、`TRI_L−DUP_L`、`BAL_J−A1_J`、`BAL_L−A1_L`；"
              "匹配效应为每个构造的 `L−J`；交互为 AP 层面的受控差值之差。",
              "- AP 层面的差值之差 **不等于** patch 分数上的 `J=L+G` 分解，不能据此宣称完整因果归因。",
              "- 负结果同样是结论：若 S 的额外贡献不明确，应据实报告，不能继续更换 backbone 直到变好。",
              "- 事后探索性分析（R0 的公平对照、留一类别点估计）不得与本次事前登记的对照混写。", "",
              "机器表：`fair_contrasts.csv`、`same_caliber_fair_table.csv`、`point_by_condition.csv`、"
              "`per_category.csv`、`per_category_contrasts.csv`、`bootstrap_samples.npz`。", ""]
    (R1 / "REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")

    steps = ["# R1 后续动作", "",
             "1. 若表示对照区间跨零，论文只能写「未观察到独立于权重的 S 收益」，不能写等价或无效。",
             "2. 若要补区间，应在运行前登记范围与校正方式，不能对已看过的结果事后加检验。",
             "3. 全像素稳健性见 `../R2_fullpixel/REPORT_CN.md`；外部冻结复核见 `../R3_external/REPORT_CN.md`。", ""]
    (R1 / "NEXT_STEPS_CN.md").write_text("\n".join(steps), encoding="utf-8")

    write_json(R1 / "POST_RUN_NOTES.json", {
        "post_run_files": ["per_category.csv", "per_category_contrasts.csv", "paired_deltas.csv",
                           "REPORT_CN.md", "NEXT_STEPS_CN.md", "POST_RUN_NOTES.json",
                           "ARTIFACT_MANIFEST.json"],
        "renderer": str(Path(__file__).relative_to(rst.ROOT)).replace("\\", "/"),
        "rendered_utc": now(),
        "note": ("REPORT/NEXT_STEPS/per-class tables were rendered from the frozen CSVs and unit "
                 "records after the analyze stage finished; ARTIFACT_MANIFEST.json was refreshed once "
                 "to include them. ``paired_deltas.csv`` is a byte copy of the analyze stage's "
                 "``fair_contrasts.csv`` under the hand-over naming convention, not a recomputation. "
                 "No frozen number, interval or hash was recomputed."),
        "analyze_summary": summary.get("acceptance")})
    write_json(R1 / "ARTIFACT_MANIFEST.json", cs.artifact_manifest(R1))
    print(json.dumps({"rendered": True, "rows_per_category": len(rows),
                      "rows_contrasts": len(contrast_rows)}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
