"""Stage B assembly: baseline scope, macro table, protocols, commands and acceptance.

Combines three sources into one comparable-but-grouped baseline package:

* native AnomalyDINO (official inference path) for MPDD/BTAD, K in {1,4}, seeds {0,1};
* PatchCore (vendored official, 128 px, coreset 10%) on the same grid;
* the controlled matrix's own A1_J / A1_L (stride-1 point estimates) for the same grid.

The three groups are reported side by side and never merged into one causal
comparison: the pooled pixel metric of the native runs is computed at the method's
own resolution (448x448 map for AnomalyDINO, 128x128 for PatchCore) while the
controlled runs use the grid x 14 canvas (448x448 for MPDD and BTAD-01/02,
448x588 for BTAD-03).
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
R = (ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913").resolve()
S = (ROOT / "experiments/dynamic_fusion/paper_evidence_closeout_20260914").resolve()
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
GRID = [1, 4]
SEEDS = [0, 1]


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


def num(value, default=None):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if np.isfinite(out) else default


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baselines", type=Path, default=S / "02_baselines")
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    base = args.baselines
    out = args.output or S
    baselines_dir = out / "02_baselines"

    # ---------------------------------------------------------------- native DINO
    native_cat = read_csv(base / "anomalydino_native_per_category.csv")
    native_macro = read_csv(base / "anomalydino_native_macro.csv")
    # ---------------------------------------------------------------- PatchCore
    patch_cat, patch_macro = [], []
    for unit_dir in sorted((base / "patchcore").glob("*_s*_k*")):
        if not (unit_dir / "per_category.csv").exists():
            continue
        parts = unit_dir.name.split("_s")
        dataset = parts[0]
        seed = int(parts[1].split("_k")[0])
        shot = int(parts[1].split("_k")[1])
        for row in read_csv(unit_dir / "per_category.csv"):
            if row["category"] == "macro_mean":
                continue
            patch_cat.append({
                "method": "PatchCore_native", "dataset": dataset, "seed": seed, "shot": shot,
                "category": row["category"].replace("mvtec_", ""),
                "n_test": int(row["sample_count"]),
                "pixel_ap": num(row["pixel_ap"]), "pixel_auroc": num(row["pixel_auroc"]),
                "pixel_aupro": num(row["aupro"]),
                "image_auroc": num(row["image_auroc"]), "image_ap": num(row["image_ap"]),
                "map_size": "128x128", "source": str(unit_dir.relative_to(ROOT))})
        for row in read_csv(unit_dir / "summary.csv"):
            if row["category"] != "macro_mean":
                continue
            patch_macro.append({
                "method": "PatchCore_native", "dataset": dataset, "seed": seed, "shot": shot,
                "n_categories": len(CATS[dataset]),
                "macro_pixel_ap": num(row["pixel_ap"]),
                "macro_pixel_auroc": num(row["pixel_auroc"]),
                "macro_image_auroc": num(row["image_auroc"]),
                "macro_image_ap": num(row["image_ap"]),
                "map_size": "128x128",
                "source": str(unit_dir.relative_to(ROOT))})
    # ------------------------------------------------------- controlled anchors
    controlled_cat, controlled_macro = [], []
    full = read_csv(R / "p4_fullpixel/fullpixel_metrics.csv")
    for method in ("A1_J", "A1_L", "B", "S", "C"):
        for dataset in ("mpdd", "btad"):
            for seed in SEEDS:
                for shot in GRID:
                    block = [r for r in full
                             if r["dataset"] == dataset and int(r["seed"]) == seed
                             and int(r["shot"]) == shot and r["method"] == method]
                    if not block:
                        continue
                    for row in block:
                        controlled_cat.append({
                            "method": f"controlled_{method}", "dataset": dataset, "seed": seed,
                            "shot": shot, "category": row["category"],
                            "n_test": None, "pixel_ap": num(row["pixel_ap"]),
                            "pixel_auroc": num(row["pixel_auroc"]), "pixel_aupro": None,
                            "image_auroc": num(row["image_auroc"]),
                            "image_ap": num(row["image_ap"]),
                            "map_size": "grid x 14 (448x448 or 448x588)",
                            "source": "R/p4_fullpixel/fullpixel_metrics.csv"})
                    controlled_macro.append({
                        "method": f"controlled_{method}", "dataset": dataset, "seed": seed,
                        "shot": shot, "n_categories": len(block),
                        "macro_pixel_ap": float(np.mean([num(r["pixel_ap"]) for r in block])),
                        "macro_pixel_auroc": float(np.mean([num(r["pixel_auroc"]) for r in block])),
                        "macro_image_auroc": float(np.mean([num(r["image_auroc"]) for r in block])),
                        "macro_image_ap": float(np.mean([num(r["image_ap"]) for r in block])),
                        "map_size": "grid x 14 (448x448 or 448x588)",
                        "source": "R/p4_fullpixel/fullpixel_metrics.csv"})

    # ------------------------------------------------------------------- scope
    def support_ids(dataset: str, seed: int, shot: int, category: str, method: str) -> str:
        """The exact normal-reference file names used by the baseline run."""
        if method.startswith("AnomalyDINO"):
            for row in native_cat:
                if (row["dataset"] == dataset and int(row["seed"]) == seed
                        and int(row["shot"]) == shot and row["category"] == category):
                    return row.get("reference_ids", "")
            return ""
        if method.startswith("PatchCore"):
            # the few-shot view records one JSON per unit with a per-category block
            selection = (ROOT / "data/patchcore_closeout"
                         / f"{dataset}_s{seed}_k{shot}" / "fewshot_selection.json")
            if selection.exists():
                payload = json.loads(selection.read_text(encoding="utf-8"))
                block = payload.get("categories", {}).get(category, {})
                return ";".join(block.get("reference_files", []))
            return ""
        if method.startswith("controlled"):
            manifest = json.loads((ROOT / f"data/splits/{dataset}/manifest.json")
                                  .read_text(encoding="utf-8"))
            return ";".join(Path(p).name for p in
                            manifest["categories"][category][str(seed)][str(shot)])
        return ""

    _query_hash_cache: dict = {}

    def query_ids_hash(dataset: str, seed: int, category: str) -> str:
        key = (dataset, seed, category)
        if key in _query_hash_cache:
            return _query_hash_cache[key]
        cache = (ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
                 / "canonical/B" / f"{dataset}_s{seed}_k8" / f"{category}.npz")
        digest = ""
        if cache.exists():
            with np.load(cache, allow_pickle=False) as z:
                ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            digest = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()[:16]
        _query_hash_cache[key] = digest
        return digest

    scope = []
    for dataset in ("mpdd", "btad"):
        for category in CATS[dataset]:
            for seed in SEEDS:
                for shot in GRID:
                    for method, cat_rows in (("AnomalyDINO_native", native_cat),
                                             ("PatchCore_native", patch_cat),
                                             ("controlled_A1_J", controlled_cat),
                                             ("controlled_A1_L", controlled_cat)):
                        match = [r for r in cat_rows if r["dataset"] == dataset
                                 and int(r["seed"]) == seed and int(r["shot"]) == shot
                                 and r["category"] == category]
                        scope.append({
                            "dataset": dataset, "category": category, "seed": seed, "shot": shot,
                            "method": method,
                            "status": "produced" if match else "missing",
                            "pixel_ap": match[0]["pixel_ap"] if match else None,
                            "map_size": match[0].get("map_size") if match else None,
                            "n_support": shot,
                            "support_ids": support_ids(dataset, seed, shot, category, method),
                            "query_ids_hash": query_ids_hash(dataset, seed, category),
                            "source": (match[0].get("source") if match else None)
                            or "02_baselines/anomalydino_native_per_category.csv"})
    write_csv(baselines_dir / "baseline_scope.csv", scope)
    native_scope = [r for r in scope if r["method"].endswith("_native")]
    produced = sum(1 for r in native_scope if r["status"] == "produced")
    missing = [r for r in native_scope if r["status"] == "missing"]

    macro = native_macro + patch_macro + controlled_macro
    write_csv(baselines_dir / "baseline_macro.csv", macro)

    # ---------------------------------------------------------------- protocols
    protocols = {
        "created_utc": utcnow(),
        "groups": {
            "AnomalyDINO_native": {
                "code": "methods/anomalydino_official @ b9d1c2648e3a5247437d4d953d907a8f3d994457",
                "inference": "official DINOv2Wrapper preprocessing (smaller edge 448), official "
                             "dists2map post-processing, official mean_top1p image score",
                "backbone": "dinov2_vits14 (AnomalyDINO default)", "target_training": "none",
                "source_training": "none", "text_used": False,
                "map_resolution": "448x448 (square, official)",
                "deviations": ["reference IDs from the frozen project manifest",
                              "rotation augmentation off",
                              "pixel metrics computed by the project evaluator because the "
                              "official evaluator hardcodes the MVTec mask extension"],
                "support_budget": "exactly the K manifest images"},
            "PatchCore_native": {
                "code": "methods/patchcore/patchcore-inspection-main (vendored official)",
                "backbone": "wide_resnet50_2 (ImageNet), layer2+layer3",
                "target_training": "none", "source_training": "none", "text_used": False,
                "map_resolution": "128x128 (resize 144 + centercrop 128)",
                "coreset": "approx_greedy_coreset, percentage 0.1",
                "deviations": ["128 px input instead of the official 224 px",
                              "target_embed_dimension 256 instead of 1024",
                              "CPU FAISS (no --faiss_on_gpu)",
                              "BTAD mirrored into the MVTec layout by hard links"],
                "support_budget": "exactly the K manifest images (the memory-bank directory "
                                  "contains only those K files) "},
            "controlled": {
                "code": "scripts/unified_fusion_paper_support_v1",
                "inference": "frozen encoders, exact 1-NN on the shared canvas",
                "map_resolution": "grid x 14 (448x448 for MPDD/BTAD-01/02, 448x588 for BTAD-03)",
                "protocol_note": "the reference for causal statements; the native rows are "
                                 "performance context only"},
        },
        "comparability_warning": ("the three groups differ in map resolution, post-processing and "
                                  "backbone; their metrics may be listed side by side but must not "
                                  "be merged into one causal comparison, and stride-8 numbers must "
                                  "never be ranked against these full-resolution numbers"),
    }
    (baselines_dir / "baseline_protocols.json").write_text(
        json.dumps(protocols, ensure_ascii=False, indent=2), encoding="utf-8")

    # ----------------------------------------------------------------- commands
    commands = ["# 阶段 B 基线运行命令（自动生成，逐条可复现）", "",
                "# 1) 原生 AnomalyDINO（MPDD + BTAD, K=1/4, seeds 0/1）",
                "& .venv-anomalyclip\\Scripts\\python.exe scripts\\paper_evidence_closeout_20260914\\"
                "run_baseline_anomalydino.py",
                "",
                "# 2) PatchCore（同一网格；BTAD 先镜像成 MVTec 布局）",
                "& .venv-anomalyclip\\Scripts\\python.exe scripts\\paper_evidence_closeout_20260914\\"
                "run_baseline_patchcore.py --skip-existing",
                "",
                "# 3) PatchCore 单单元等价命令（driver 内部按此调用，cwd=methods/patchcore/"
                "patchcore-inspection-main，PYTHONPATH=src）"]
    state_path = base / "patchcore_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        seen = set()
        for unit, entry in sorted(state["units"].items()):
            command = entry.get("run", {}).get("command")
            if command and command not in seen:
                seen.add(command)
                commands.append(f"# {unit}")
                commands.append(command.replace(str(ROOT), "."))
    (baselines_dir / "commands.ps1").write_text("\n".join(commands) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ costs
    cost_rows = []
    for row in native_macro:
        cost_rows.append({"method": row["method"], "dataset": row["dataset"],
                          "seed": row["seed"], "shot": row["shot"],
                          "memory_bank_s": num(row.get("mean_memory_bank_s")),
                          "per_image_s": num(row.get("mean_s_per_image")),
                          "peak_gpu_mb": num(row.get("peak_gpu_mb")),
                          "wall_clock_s": None,
                          "note": "official inference path; per-image scoring only"})
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for unit, entry in sorted(state["units"].items()):
            if unit == "btad_layout":
                continue
            cost_rows.append({"method": "PatchCore_native", "dataset": entry["dataset"],
                              "seed": entry["seed"], "shot": entry["shot"],
                              "memory_bank_s": None, "per_image_s": None, "peak_gpu_mb": None,
                              "wall_clock_s": entry.get("run", {}).get("seconds"),
                              "note": "whole-run wall clock (memory bank + scoring + results); "
                                      "PatchCore peak GPU memory is not instrumented"})
    write_csv(baselines_dir / "resource_cost.csv", cost_rows)

    acceptance = [
        "# 阶段 B 基线验收", "",
        f"- 目标范围：2 数据集 x (6+3) 类 x K∈{{1,4}} x seed∈{{0,1}} x 2 原生方法 = 72 个类别级条件；"
        f"已产出 {produced}/{len(native_scope)}。",
        f"- 缺失：{len(missing)} 条" + ("（见 baseline_scope.csv）" if missing else "（无）"),
        "- PatchCore 记忆库只含规定的 K 张正常图（`train/good` 目录内仅 K 个文件，"
        "`fewshot_selection.json` 记录文件名）。",
        "- 没有用 MVTec/VisA 的历史分数替代 MPDD/BTAD；旧参照仍留在旧目录，未并入本表。",
        "- 三组的分辨率与后处理不同，已在 `baseline_protocols.json` 中声明；"
        "禁止把 stride-8 数值与这些全分辨率数值排序比较。",
        "- 未用测试集调参；coreset 比例、层选择、输入尺寸沿用项目既有冻结配置。",
        "- A1 是否胜出不作为验收条件。", "",
    ]
    (baselines_dir / "BASELINE_ACCEPTANCE_CN.md").write_text("\n".join(acceptance),
                                                             encoding="utf-8")
    summary = {"created_utc": utcnow(), "scope_rows": len(scope),
               "native_conditions_target": len(native_scope),
               "native_conditions_produced": produced, "native_conditions_missing": len(missing),
               "macro_rows": len(macro), "native_categories": len(native_cat),
               "patchcore_categories": len(patch_cat), "controlled_rows": len(controlled_cat)}
    (baselines_dir / "BASELINE_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
