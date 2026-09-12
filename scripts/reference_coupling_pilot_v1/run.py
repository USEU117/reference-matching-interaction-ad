"""Bounded, resumable mechanism pilot. Never writes historical experiment files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912"
CATS = ["bracket_black", "bracket_brown", "bracket_white", "connector", "metal_plate", "tubes"]
TOL = 1e-6


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def build_configs(shot, permutations):
    import numpy as np
    original = {
        "B": {"B": 1.0}, "S": {"S": 1.0}, "C": {"C": 1.0},
        "A1_J": {"B": .5, "C": .5},
        "TRI_J": {"B": 1/3, "S": 1/3, "C": 1/3},
        "BAL_J": {"B": .25, "S": .25, "C": .5},
        "DUP_J": {"B": 1/3, "Bcopy": 1/3, "C": 1/3},
        "DUP_BAL_J": {"B": .25, "Bcopy": .25, "C": .5},
        "DUP_EXPECTED_J": {"B": 2/3, "C": 1/3},
    }
    configs = [{"name": k, "weights": v, "permutations": {}} for k, v in original.items()]
    rows = shot * 1024
    arrays = {}
    common = np.random.default_rng(20260912).permutation(rows)
    arrays["common"] = common
    for name in ("A1_J", "TRI_J", "BAL_J"):
        configs.append({"name": "INV_COMMON_" + name, "weights": original[name],
                        "permutations": {b: common for b in original[name]}})
    support_orders = [p for p in itertools.permutations(range(shot)) if p != tuple(range(shot))]
    np.random.default_rng(20260913).shuffle(support_orders)
    for seed in range(permutations):
        for kind in ("within", "cross"):
            rng = np.random.default_rng(20260912 + seed * 100 + (0 if kind == "within" else 1))
            if kind == "within":
                # Full within-image position permutation, no deletion or repeated rows.
                perm = np.concatenate([rng.permutation(1024) + i * 1024 for i in range(shot)])
            else:
                if seed >= len(support_orders):
                    continue
                # Distinct non-identity image permutations, preserving patch position.
                order = np.asarray(support_orders[seed])
                perm = (order[:, None] * 1024 + np.arange(1024)).reshape(-1)
            key = f"{kind}_p{seed:02d}"
            arrays[key] = perm
            if not np.array_equal(np.sort(perm), np.arange(rows)):
                raise ValueError("Permutation must be a bijection")
            for branch in ("C", "S"):
                configs.append({"name": f"INV_SINGLE_{branch}_{key}", "weights": {branch: 1.},
                                "permutations": {branch: perm}})
            for base, branch in (("A1_J", "C"), ("TRI_J", "C"), ("TRI_J", "S"),
                                 ("BAL_J", "C"), ("BAL_J", "S")):
                configs.append({"name": f"{base}__perm_{branch}_{key}", "weights": original[base],
                                "permutations": {branch: perm}})
    return configs, arrays


def reference_ap(shot, cat):
    p = ROOT / "experiments/dynamic_fusion/validation_handoff_20260911/E2/metrics_per_category.csv"
    with p.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if int(r["seed"]) == 0 and int(r["shot"]) == shot and r["category"] == cat and r["config_id"] == "B+C":
                return float(r["pixel_ap"])
    raise ValueError("Missing historical A1 reference")


def run_unit(args):
    import numpy as np
    import torch
    import engine
    import diagnostics
    sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
    import common as C

    torch.set_num_threads(4)
    C.faiss.omp_set_num_threads(4)
    cat, shot = args.unit_category, args.unit_shot
    out = args.output / "units" / f"s0_k{shot}" / cat
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    dump(out / "progress.json", {"state": "loading", "updated_utc": now()})
    # Canonical source: one K4 query/reference extraction for both K conditions.
    # Historical K2/K4 files have tiny extraction drift; do not confuse it with K.
    inp = engine.load_inputs(0, 4, cat)
    inp["r"] = {b: np.ascontiguousarray(r[:shot * 1024]) for b, r in inp["r"].items()}
    inp["q"]["Bcopy"] = inp["q"]["B"]
    inp["r"]["Bcopy"] = inp["r"]["B"]
    load_s = time.monotonic() - start
    configs, perm_arrays = build_configs(shot, args.permutations)
    np.savez_compressed(out / "reference_permutations.npz", **perm_arrays)
    config_record = [{"name": c["name"], "distance_weights": c["weights"],
                      "permutation_hashes": {b: hashlib.sha256(v.tobytes()).hexdigest()
                                               for b, v in c["permutations"].items()}}
                     for c in configs]
    dump(out / "configurations.json", config_record)
    print(f"START {cat} K{shot}; {inp['n']} images; {len(configs)} score configurations", flush=True)
    dump(out / "progress.json", {"state": "scoring", "updated_utc": now(), "n": inp["n"],
                                  "configurations": len(configs), "load_s": load_s})
    score_start = time.monotonic()
    scored, engine_info = engine.score(inp, configs, device=args.device, chunk=args.chunk)
    score_s = time.monotonic() - score_start
    checks = {}
    def check(name, error, tol=TOL):
        checks[name] = {"max_abs_error": float(error), "tolerance": tol, "pass": bool(error <= tol)}

    check("duplicate_matches_weighted_pair", np.max(np.abs(scored["DUP_J"] - scored["DUP_EXPECTED_J"])))
    check("balanced_duplicate_matches_A1", np.max(np.abs(scored["DUP_BAL_J"] - scored["A1_J"])))
    for base in ("A1_J", "TRI_J", "BAL_J"):
        check("common_permutation_" + base, np.max(np.abs(scored[base] - scored["INV_COMMON_" + base])))
    for name, values in scored.items():
        if name.startswith("INV_SINGLE_"):
            branch = name.split("_")[2]
            check(name, np.max(np.abs(values - scored[branch])))
    # Independent legacy scorer on actual patches, including normalisation and exact FAISS.
    count = min(2048, len(inp["q"]["B"]))
    parity_indices = np.linspace(0, len(inp["q"]["B"]) - 1, count, dtype=np.int64)
    qcat = C.unit_rows(np.concatenate([inp["q"]["B"][parity_indices] / np.sqrt(2),
                                       inp["q"]["C"][parity_indices] / np.sqrt(2)], axis=1))
    rcat = C.unit_rows(np.concatenate([inp["r"]["B"] / np.sqrt(2),
                                       inp["r"]["C"] / np.sqrt(2)], axis=1))
    legacy = C.knn_dist(qcat, rcat)[:, 0]
    check("legacy_A1_faiss_real_patch_parity", np.max(np.abs(legacy - scored["A1_J"].reshape(-1)[parity_indices])))
    del qcat, rcat, legacy
    scored["A1_L"] = (.5 * scored["B"] + .5 * scored["C"]).astype(np.float32)
    scored["TRI_L"] = ((scored["B"] + scored["S"] + scored["C"]) / 3).astype(np.float32)
    scored["BAL_L"] = (.25 * scored["B"] + .25 * scored["S"] + .5 * scored["C"]).astype(np.float32)
    for prefix in ("A1", "TRI", "BAL"):
        g = scored[prefix + "_J"] - scored[prefix + "_L"]
        scored[prefix + "_G"] = g
        check(prefix + "_nonnegative_G", max(0., -float(g.min())))
        for lam in (.25, .5, .75):
            scored[f"{prefix}_lambda_{lam:.2f}"] = scored[prefix + "_L"] + np.float32(lam) * g
    for prefix in ("TRI", "BAL"):
        dj = scored[prefix + "_J"] - scored["A1_J"]
        dl = scored[prefix + "_L"] - scored["A1_L"]
        dg = scored[prefix + "_G"] - scored["A1_G"]
        scored[f"DELTA_{prefix}_J"] = dj
        scored[f"DELTA_{prefix}_L"] = dl
        scored[f"DELTA_{prefix}_G"] = dg
        check(prefix + "_score_decomposition", np.max(np.abs(dj - dl - dg)))
    # Historical full-category P-AP parity uses the original stride-8 evaluator.
    amap = C.dists_to_maps(scored["A1_J"].reshape(-1), inp["n"], (32, 32))
    actual_ap = C.pixel_metrics(amap, inp["masks"])["pixel_ap"]
    expected_ap = reference_ap(shot, cat)
    check("historical_A1_pixel_AP", abs(actual_ap - expected_ap), 5e-4)
    del amap
    inv = {"all_pass": all(v["pass"] for v in checks.values()), "checks": checks,
           "A1_pixel_ap": actual_ap, "historical_A1_pixel_ap": expected_ap}
    dump(out / "invariants.json", inv)
    if not inv["all_pass"]:
        raise RuntimeError("Invariant failure; no mechanism interpretation permitted")
    # Free raw unit features before metric processing to keep RAM low.
    masks, labels, ids = inp["masks"], inp["labels"], [str(x) for x in inp["sample_ids"]]
    paths = {k: str(v) for k, v in inp.get("paths", {}).items()}
    del inp
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    saved = {k: v for k, v in scored.items() if not k.startswith("INV_")}
    np.savez_compressed(out / "patch_scores.npz", **saved, sample_ids=np.asarray(ids))
    dump(out / "progress.json", {"state": "metrics", "updated_utc": now(), "score_s": score_s,
                                  "n_scores": len(saved)})
    metrics_start = time.monotonic()
    result = diagnostics.evaluate_case(saved, masks, labels, ids, out, include_aupro=True)
    timing = {"load_s": load_s, "score_s": score_s, "metric_s": time.monotonic() - metrics_start,
              "total_s": time.monotonic() - start}
    dump(out / "DONE.json", {"status": "completed", "scientific_status": "exploratory_only",
                             "finished_utc": now(), "category": cat, "shot": shot, "seed": 0,
                             "n_images": len(ids), "configurations": len(configs),
                             "canonical_source_shot": 4, "selected_reference_images": shot,
                             "timing": timing, "inputs": paths, "engine": engine_info,
                             "diagnostics": result, "invariants_pass": True,
                             "protocol_hash": sha(args.output / "PROTOCOL.json")})
    dump(out / "progress.json", {"state": "completed", "updated_utc": now(), "timing": timing})
    print(f"DONE {cat} K{shot}: {timing}", flush=True)


def collect_report(output, expected, state):
    """Always leave an honest partial/completed handoff even if a unit fails."""
    rows, done_units = [], []
    for p in sorted((output / "units").glob("s0_k*/*/DONE.json")):
        done = json.loads(p.read_text(encoding="utf-8"))
        done_units.append(done)
        metric_path = p.parent / "metrics.csv"
        if metric_path.exists():
            with metric_path.open(encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    rows.append({"seed": 0, "shot": done["shot"], "category": done["category"], **r})
    if rows:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with (output / "metrics_all_units.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(rows)
    completed_ids = {(r["category"], r["shot"]) for r in done_units}
    missing = [{"category": c, "shot": k} for c, k in expected if (c, k) not in completed_ids]
    report = {"state": state, "updated_utc": now(), "expected_units": len(expected),
              "completed_units": len(done_units), "missing_units": missing,
              "scientific_status": "exploratory_not_confirmatory", "completed": done_units}
    dump(output / "RUN_SUMMARY.json", report)
    lines = ["# 参考耦合机制试探运行报告", "", f"更新：{now()}。运行状态：{state}。",
             f"完成 {len(done_units)}/{len(expected)} 个类别×K 单元。全部属于探索性试探。", "",
             "本轮范围：MPDD s0/K2/K4，权重/复制控制、原始 J/L/G 与分数分解、参考配对置换、固定 lambda 松弛。",
             "尚不支持跨 seed、跨数据域、K8/16 或可预测失效边界结论。", "",
             "## 文件与验收", "", "- PROTOCOL.json：预注册范围、时间预算及代码身份。",
             "- audit/identity_audit.json：参考行身份来源与限制。",
             "- units/s0_k*/类别/invariants.json：恒等与重放验收，失败单元不能用于机制归因。",
             "- units/s0_k*/类别/patch_scores.npz：可重建全部图的 patch 原始分数。",
             "- units/s0_k*/类别/reference_permutations.npz：实际置换行数组。",
             "- 各单元 metrics.csv、region_stats.csv、flip_stats.csv 与评价分数缓存：后续统计入口。",
             "- metrics_all_units.csv：已完成单元汇总；RUN_SUMMARY.json：完成/缺失清单。", "",
             "## 未完成项", ""]
    lines += [f"- {m['category']} K{m['shot']}" for m in missing] or ["计划内单元全部完成。"]
    lines += ["", "## 科学结论状态", "", "本自动报告只验收执行状态。最终效应量、配对区间与继续方向由后续分析报告给出；不得把已执行等同于已发现机制。", ""]
    (output / "RUN_REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--categories", nargs="+", default=CATS)
    ap.add_argument("--shots", nargs="+", type=int, choices=[2, 4], default=[2, 4])
    ap.add_argument("--permutations", type=int, default=10)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--max-hours", type=float, default=10.)
    ap.add_argument("--deadline", default="2026-09-13T07:00:00+08:00")
    ap.add_argument("--unit-timeout-minutes", type=float, default=90.)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--audit-file", type=Path)
    ap.add_argument("--unit-category")
    ap.add_argument("--unit-shot", type=int)
    args = ap.parse_args()
    if args.permutations < 0 or args.permutations > 23:
        raise ValueError("Pilot supports 0..23 permutation seeds")
    args.output = args.output.resolve()
    if args.unit_category:
        run_unit(args)
        return 0
    args.output.mkdir(parents=True, exist_ok=True)
    audit_path = args.audit_file or args.output / "audit/identity_audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if not audit.get("all_pass", False):
        raise RuntimeError("Support identity audit failed or incomplete")
    coverage = {(u.get("category"), u.get("shot"), u.get("branch")) for u in audit.get("units", [])}
    needed = {(c, 4, b) for c in args.categories for b in ("B", "S", "C")}
    if not needed.issubset(coverage):
        raise RuntimeError(f"Audit does not cover canonical inputs: {sorted(needed - coverage)}")
    start = time.time()
    deadline = min(start + args.max_hours * 3600, datetime.fromisoformat(args.deadline).timestamp())
    if deadline - start < 120:
        raise RuntimeError("Insufficient time before hard deadline")
    expected = [(c, k) for k in args.shots for c in args.categories]
    config_list, _ = build_configs(args.shots[0], args.permutations)
    versions = {}
    for package in ("numpy", "scipy", "torch", "scikit-learn", "scikit-image", "faiss-cpu"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    protocol = {"protocol": "reference_coupling_pilot_v1", "dataset": "mpdd", "seed": 0,
                "categories": args.categories, "shots": args.shots, "permutation_seeds": list(range(args.permutations)),
                "config_names_example": [x["name"] for x in config_list],
                "distance_tolerance": TOL, "historical_AP_tolerance": 5e-4,
                "within_permutation": "independent full spatial permutation within each support image",
                "cross_permutation": "distinct non-identity image permutations, same spatial position; up to min(requested,K!-1)",
                "permutation_replicates_note": "K2 has only one non-identity image permutation; evaluated once, not treated as repeated evidence",
                "lambda": [0., .25, .5, .75, 1.], "pixel_stride": 8, "raw_grid": [32, 32],
                "cache_policy": "canonical K4 query and reference features for both shots; K2 uses first two manifest references",
                "postprocess": "448 bilinear then gaussian sigma4; image max",
                "acceptance": "implementation invariants then exploratory effects; no winner-only filtering",
                "created_utc": now(), "deadline_utc": datetime.fromtimestamp(deadline, timezone.utc).isoformat(),
                "audit_path": str(audit_path), "audit_hash": sha(audit_path),
                "source_hashes": {name: sha(HERE / name) for name in ("run.py", "engine.py", "diagnostics.py")},
                "legacy_common_sha256": sha(ROOT / "scripts/validation_handoff_20260911/common.py"),
                "dependency_versions": versions, "invocation": sys.argv,
                "python": sys.executable, "device": args.device, "chunk": args.chunk}
    pp = args.output / "PROTOCOL.json"
    if pp.exists():
        if not args.resume:
            raise RuntimeError("Protocol exists; use --resume with unchanged settings or a new output path")
        old = json.loads(pp.read_text(encoding="utf-8"))
        for key in ("categories", "shots", "permutation_seeds", "distance_tolerance", "source_hashes", "audit_hash"):
            if old.get(key) != protocol.get(key):
                raise RuntimeError(f"Resume identity mismatch: {key}")
    else:
        dump(pp, protocol)
    logs = args.output / "logs"; logs.mkdir(exist_ok=True)
    state = "running"
    timings = []
    failures = []
    for cat, shot in expected:
        unit = args.output / "units" / f"s0_k{shot}" / cat
        if (unit / "DONE.json").exists():
            continue
        remaining = deadline - time.time() - 90
        estimated = max(timings[-3:], default=60.) * 1.5
        if remaining < estimated:
            state = "paused_time_budget"; break
        dump(args.output / "STATUS.json", {"state": "running", "pid": os.getpid(),
                                             "unit": f"{cat}/s0/K{shot}", "updated_utc": now(),
                                             "remaining_seconds": remaining})
        command = [sys.executable, "-u", str(Path(__file__).resolve()), "--unit-category", cat,
                   "--unit-shot", str(shot), "--output", str(args.output), "--permutations", str(args.permutations),
                   "--device", args.device, "--chunk", str(args.chunk)]
        t0 = time.time()
        with (logs / f"s0_k{shot}_{cat}.log").open("a", encoding="utf-8") as log:
            proc = subprocess.Popen(command, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            try:
                code = proc.wait(timeout=min(remaining, args.unit_timeout_minutes * 60))
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(); code = -9
                failures.append({"category": cat, "shot": shot, "reason": "unit_time_limit"})
        timings.append(time.time() - t0)
        if code != 0:
            if code != -9:
                failures.append({"category": cat, "shot": shot, "exit_code": code})
            state = "needs_attention"
            # Do not repeatedly run a broken mechanism protocol overnight.
            break
        collect_report(args.output, expected, "running")
    else:
        state = "completed"
    dump(args.output / "FAILURES.json", failures)
    summary = collect_report(args.output, expected, state)
    dump(args.output / "STATUS.json", {"state": state, "pid": os.getpid(), "updated_utc": now(),
                                        "completed_units": summary["completed_units"],
                                        "expected_units": len(expected), "total_seconds": time.time() - start})
    print(json.dumps({"state": state, "completed_units": summary["completed_units"],
                      "elapsed_seconds": time.time() - start}, ensure_ascii=False), flush=True)
    return 0 if state in ("completed", "paused_time_budget") else 1


if __name__ == "__main__":
    raise SystemExit(main())
