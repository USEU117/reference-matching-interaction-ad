"""P1: run the controlled K x weighting x representation x matching matrix.

One unit = (dataset, reference seed, K, category).  Every unit scores the 11 core
methods plus the implementation controls, writes the raw patch scores and the
stride-8 diagnostics, and records the acceptance invariants.

The 11 core methods are

    B, S, C,                       single branches
    A1_J/L, DUP_J/L, TRI_J/L, BAL_J/L    four constructions x two matching modes

with

    J = min_r sum_b w_b d_b(q, r)      L = sum_b w_b min_r d_b(q, r)

`L` is assembled from the three single-branch independent-minimum maps, so the
only extra scoring work is the four joint constructions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

DEFAULT_OUT = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p1_matrix"
CATS = {
    "mpdd": ["bracket_black", "bracket_brown", "bracket_white", "connector",
             "metal_plate", "tubes"],
    "btad": ["01", "02", "03"],
}
CORE_METHODS = ["B", "S", "C", "A1_J", "A1_L", "DUP_J", "DUP_L", "TRI_J", "TRI_L",
                "BAL_J", "BAL_L"]
TOL = 1e-6
MAP_STRIDE = 14
LAMBDA_END = {"A1": ("A1_L", "A1_J"), "TRI": ("TRI_L", "TRI_J"), "BAL": ("BAL_L", "BAL_J")}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for part in iter(lambda: fh.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


J_WEIGHTS = {
    "B": {"B": 1.0}, "S": {"S": 1.0}, "C": {"C": 1.0},
    "A1_J": {"B": .5, "C": .5},
    "TRI_J": {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3},
    "BAL_J": {"B": .25, "S": .25, "C": .5},
    "DUP_J": {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3},
    "DUP_BAL_J": {"B": .25, "Bcopy": .25, "C": .5},
    "DUP_EXPECTED_J": {"B": 2 / 3, "C": 1 / 3},
}


def build_configs(seed: int, shot: int, grid: tuple[int, int], perm_controls: int):
    import numpy as np

    patch = grid[0] * grid[1]
    rows = shot * patch
    configs = [{"name": name, "weights": weights, "permutations": {}}
               for name, weights in J_WEIGHTS.items()]

    # (a) a permutation applied identically to every branch must not change J
    common = np.random.default_rng(20260913).permutation(rows)
    arrays = {"common": common}
    for name in ("A1_J", "TRI_J", "BAL_J"):
        branches = [b for b in J_WEIGHTS[name] if b != "Bcopy"]
        configs.append({"name": f"INV_COMMON_{name}", "weights": J_WEIGHTS[name],
                        "permutations": {b: common for b in branches}})

    # (b) a single branch's independent minima are invariant to its own row order
    for branch in ("B", "C", "S"):
        rng = np.random.default_rng(20260914 + {"B": 2, "C": 0, "S": 1}[branch])
        perm = rng.permutation(rows)
        arrays[f"single_{branch}"] = perm
        configs.append({"name": f"INV_SINGLE_{branch}", "weights": {branch: 1.0},
                        "permutations": {branch: perm}})

    # (c) coupling controls: permute one branch's reference rows only
    _add_coupling(configs, arrays, seed, shot, patch, rows, perm_controls,
                  kind="cross", np=np)
    _add_coupling(configs, arrays, seed, shot, patch, rows, perm_controls,
                  kind="within", np=np)
    return configs, arrays


def _add_coupling(configs, arrays, seed, shot, patch, rows, perm_controls, kind, np):
    if perm_controls <= 0:
        return
    if kind == "cross":
        orders = [p for p in itertools.permutations(range(shot)) if p != tuple(range(shot))]
        np.random.default_rng(20260915).shuffle(orders)
        orders = orders[:perm_controls]
        perms = [(f"cross_p{i:02d}", (np.asarray(o)[:, None] * patch
                                      + np.arange(patch)).reshape(-1))
                 for i, o in enumerate(orders)]
    else:
        perms = []
        for i in range(perm_controls):
            rng = np.random.default_rng(20260916 + i)
            perms.append((f"within_p{i:02d}",
                          np.concatenate([rng.permutation(patch) + j * patch
                                          for j in range(shot)])))
    for key, perm in perms:
        if not np.array_equal(np.sort(perm), np.arange(rows)):
            raise ValueError("permutation must be a bijection")
        arrays[key] = perm
        for base, branch in (("A1_J", "C"), ("TRI_J", "C"), ("TRI_J", "S"),
                             ("BAL_J", "C"), ("BAL_J", "S")):
            configs.append({"name": f"{base}__perm_{branch}_{key}",
                            "weights": J_WEIGHTS[base], "permutations": {branch: perm}})


def summarise_coupling(scored, masks, labels, grid) -> list:
    """Compact summary of the single-branch reference-permutation controls.

    A coupling control permutes the reference rows of exactly one branch while the
    other branches keep theirs, so `J` changes as soon as the joint reference row
    matters.  Storing mean/max changes per region keeps the evidence without
    keeping 30 extra full patch-score planes per unit.
    """
    import numpy as np

    names = [k for k in scored if "__perm_" in k]
    if not names:
        return []
    h, w = grid
    fraction = ((masks.astype(np.float32) > 0)
                .reshape(masks.shape[0], h, MAP_STRIDE, w, MAP_STRIDE)
                .mean(axis=(2, 4), dtype=np.float32))
    defect = fraction > 0
    normal = fraction == 0
    rows = []
    for name in sorted(names):
        base, _, tail = name.partition("__perm_")
        delta = scored[base] - scored[name]
        abs_delta = np.abs(delta)
        row = {"config": name, "base": base,
               "permuted_branch": tail.rsplit("_p", 1)[0],
               "permutation_index": tail.rsplit("_p", 1)[-1],
               "mean_delta": float(delta.mean()), "mean_abs_delta": float(abs_delta.mean()),
               "max_abs_delta": float(abs_delta.max()),
               "frac_changed_gt_1e-6": float((abs_delta > 1e-6).mean())}
        for region, selection in (("defect", defect), ("normal", normal)):
            if selection.any():
                row[f"{region}_mean_abs_delta"] = float(abs_delta[selection].mean())
                row[f"{region}_mean_delta"] = float(delta[selection].mean())
                row[f"{region}_n_patches"] = int(selection.sum())
            else:
                row[f"{region}_mean_abs_delta"] = None
                row[f"{region}_mean_delta"] = None
                row[f"{region}_n_patches"] = 0
        rows.append(row)
    return rows


def write_coupling_csv(path: Path, rows: list) -> None:
    import csv

    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_unit(args) -> int:
    import numpy as np
    import torch

    import diagnostics_v2
    import engine_v2
    sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
    import common as C

    torch.set_num_threads(4)
    C.faiss.omp_set_num_threads(4)
    dataset, seed, shot, cat = args.unit_dataset, args.unit_seed, args.unit_shot, args.unit_category
    out = args.output / "units" / f"{dataset}_s{seed}_k{shot}" / cat
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    dump(out / "progress.json", {"state": "loading", "updated_utc": now()})
    branches = tuple(args.branches)
    inputs = engine_v2.load_inputs(dataset, seed, shot, cat, branches=branches)
    inputs["q"]["Bcopy"] = inputs["q"]["B"]
    inputs["r"]["Bcopy"] = inputs["r"]["B"]
    grid = inputs["grid"]
    load_s = time.monotonic() - start
    configs, perm_arrays = build_configs(seed, shot, grid, args.permutations)
    np.savez_compressed(out / "reference_permutations.npz", **perm_arrays)
    dump(out / "configurations.json",
         [{"name": c["name"], "distance_weights": c["weights"],
           "permutation_hashes": {b: hashlib.sha256(v.tobytes()).hexdigest()
                                  for b, v in c["permutations"].items()}}
          for c in configs])
    print(f"START {dataset} s{seed} K{shot} {cat}: {inputs['n']} images, grid {grid}, "
          f"{len(configs)} configurations", flush=True)
    dump(out / "progress.json", {"state": "scoring", "updated_utc": now(), "n": inputs["n"],
                                 "configurations": len(configs), "load_s": load_s})
    score_start = time.monotonic()
    scored, engine_info = engine_v2.score(inputs, configs, device=args.device, chunk=args.chunk)
    score_s = time.monotonic() - score_start

    checks = {}

    def check(name, error, tol=TOL):
        checks[name] = {"max_abs_error": float(error), "tolerance": float(tol),
                        "pass": bool(error <= tol)}

    check("duplicate_matches_weighted_pair",
          np.max(np.abs(scored["DUP_J"] - scored["DUP_EXPECTED_J"])))
    check("balanced_duplicate_matches_A1", np.max(np.abs(scored["DUP_BAL_J"] - scored["A1_J"])))
    for base in ("A1_J", "TRI_J", "BAL_J"):
        check("common_permutation_" + base,
              np.max(np.abs(scored[base] - scored["INV_COMMON_" + base])))

    # independent FAISS scorer on the actual patches for the A1 construction
    count = min(2048, len(inputs["q"]["B"]))
    parity_indices = np.linspace(0, len(inputs["q"]["B"]) - 1, count, dtype=np.int64)
    parts_q = []
    parts_r = []
    for branch, weight in (("B", .5), ("C", .5)):
        parts_q.append(inputs["q"][branch][parity_indices] / np.sqrt(2))
        parts_r.append(inputs["r"][branch] / np.sqrt(2))
    qcat = C.unit_rows(np.concatenate(parts_q, axis=1))
    rcat = C.unit_rows(np.concatenate(parts_r, axis=1))
    legacy = C.knn_dist(qcat, rcat)[:, 0]
    check("legacy_A1_faiss_real_patch_parity",
          np.max(np.abs(legacy - scored["A1_J"].reshape(-1)[parity_indices])))
    del qcat, rcat, legacy, parts_q, parts_r

    # L endpoints from the three single-branch independent minima
    scored["A1_L"] = (.5 * scored["B"] + .5 * scored["C"]).astype(np.float32)
    scored["DUP_L"] = ((2 / 3) * scored["B"] + (1 / 3) * scored["C"]).astype(np.float32)
    scored["TRI_L"] = ((scored["B"] + scored["S"] + scored["C"]) / 3).astype(np.float32)
    scored["BAL_L"] = (.25 * scored["B"] + .25 * scored["S"] + .5 * scored["C"]).astype(np.float32)
    for base in ("B", "C", "S"):
        if f"INV_SINGLE_{base}" in scored:
            check(f"single_permutation_{base}",
                  np.max(np.abs(scored[f"INV_SINGLE_{base}"] - scored[base])))
    for prefix in ("A1", "DUP", "TRI", "BAL"):
        g = scored[prefix + "_J"] - scored[prefix + "_L"]
        scored[prefix + "_G"] = g.astype(np.float32)
        check(prefix + "_nonnegative_G", max(0.0, -float(g.min())))
    for prefix, (l_key, j_key) in LAMBDA_END.items():
        scored[f"DELTA_{prefix}_L"] = (scored[l_key] - scored["A1_L"]).astype(np.float32)
        scored[f"DELTA_{prefix}_J"] = (scored[j_key] - scored["A1_J"]).astype(np.float32)

    inv = {"all_pass": all(v["pass"] for v in checks.values()), "checks": checks,
           "grid": list(grid), "n_images": int(inputs["n"]), "shot": int(shot),
           "seed": int(seed), "dataset": dataset, "category": cat,
           "branches": list(branches)}
    dump(out / "invariants.json", inv)
    if not inv["all_pass"]:
        raise RuntimeError(f"Invariant failure in {out}; no mechanism interpretation permitted")

    masks, labels = inputs["masks"], inputs["labels"]
    ids = [str(x) for x in inputs["sample_ids"]]
    paths = {k: str(v) for k, v in inputs.get("paths", {}).items()}
    # Compact summary of the reference-coupling controls, then drop the (large)
    # per-patch control arrays from the saved artefact.
    coupling_rows = summarise_coupling(scored, masks, labels, grid)
    write_coupling_csv(out / "coupling_controls.csv", coupling_rows)
    del inputs
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    saved = {k: v for k, v in scored.items()
             if not k.startswith("INV_") and "__perm_" not in k}
    np.savez_compressed(out / "patch_scores.npz", **saved, sample_ids=np.asarray(ids))
    dump(out / "progress.json", {"state": "metrics", "updated_utc": now(), "score_s": score_s})
    metrics_start = time.monotonic()
    result = diagnostics_v2.evaluate_case(saved, masks, labels, ids, out, grid,
                                         stride=args.stride, include_aupro=False,
                                         write_pair_diagnostics=(args.stride == 8))
    timing = {"load_s": load_s, "score_s": score_s,
              "metric_s": time.monotonic() - metrics_start,
              "total_s": time.monotonic() - start}
    dump(out / "DONE.json", {"status": "completed", "scientific_status": "exploratory_only",
                             "finished_utc": now(), "dataset": dataset, "seed": seed,
                             "shot": shot, "category": cat, "grid": list(grid),
                             "n_images": len(ids), "configurations": len(configs),
                             "reference_images": shot, "timing": timing, "inputs": paths,
                             "engine": engine_info, "invariants_pass": True,
                             "diagnostics": result, "stride": args.stride,
                             "protocol_hash": (sha(args.output / "PROTOCOL.json")
                                               if (args.output / "PROTOCOL.json").exists()
                                               else None)})
    dump(out / "progress.json", {"state": "completed", "updated_utc": now(), "timing": timing})
    print(f"DONE {dataset} s{seed} K{shot} {cat}: {timing}", flush=True)
    return 0


def collect(output: Path, expected: list[tuple], state: str) -> dict:
    import csv

    rows, done_units = [], []
    for p in sorted(output.glob("units/*/*/DONE.json")):
        done = json.loads(p.read_text(encoding="utf-8"))
        done_units.append(done)
        metric_path = p.parent / "metrics.csv"
        if metric_path.exists():
            with metric_path.open(encoding="utf-8-sig") as fh:
                for r in csv.DictReader(fh):
                    rows.append({"dataset": done["dataset"], "seed": done["seed"],
                                 "shot": done["shot"], "category": done["category"], **r})
    if rows:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with (output / "metrics_all_units.csv").open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
    completed = {(d["dataset"], d["seed"], d["shot"], d["category"]) for d in done_units}
    missing = [dict(zip(("dataset", "seed", "shot", "category"), key))
               for key in expected if key not in completed]
    report = {"state": state, "updated_utc": now(), "expected_units": len(expected),
              "completed_units": len(done_units), "missing_units": missing,
              "scientific_status": "exploratory_not_confirmatory", "completed": done_units}
    dump(output / "RUN_SUMMARY.json", report)
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--datasets", nargs="+", default=["mpdd"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--categories", nargs="+", default=None)
    ap.add_argument("--branches", nargs="+", default=["B", "S", "C"])
    ap.add_argument("--permutations", type=int, default=3)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--stride", type=int, default=8)
    ap.add_argument("--unit-timeout-minutes", type=float, default=180.0)
    ap.add_argument("--max-hours", type=float, default=24.0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--code-amendment-reason", default=None,
                    help="recorded when the source hashes change between batches")
    ap.add_argument("--unit-dataset")
    ap.add_argument("--unit-seed", type=int)
    ap.add_argument("--unit-shot", type=int)
    ap.add_argument("--unit-category")
    args = ap.parse_args()
    args.output = args.output.resolve()
    if args.unit_category:
        return run_unit(args)

    import importlib.metadata

    args.output.mkdir(parents=True, exist_ok=True)
    expected = [(d, s, k, c) for d in args.datasets for s in args.seeds for k in args.shots
                for c in (args.categories or CATS[d])]
    versions = {}
    for package in ("numpy", "scipy", "torch", "scikit-learn", "scikit-image", "faiss-cpu"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    protocol = {
        "protocol": "unified_fusion_paper_support_v1_matrix",
        "datasets": args.datasets, "seeds": args.seeds, "shots": args.shots,
        "categories": {d: (args.categories or CATS[d]) for d in args.datasets},
        "branches": args.branches, "core_methods": CORE_METHODS,
        "distance_weights": J_WEIGHTS,
        "L_definition": {"A1_L": "0.5*B+0.5*C", "DUP_L": "(2/3)*B+(1/3)*C",
                         "TRI_L": "(B+S+C)/3", "BAL_L": ".25*B+.25*S+.5*C"},
        "cache": "canonical K=8 cache; every K is a prefix of the same reference block",
        "pixel_stride": args.stride, "tolerances": {"invariants": TOL},
        "permutation_controls": args.permutations,
        "device": args.device, "chunk": args.chunk,
        "dependency_versions": versions, "created_utc": now(),
        "source_hashes": {name: sha(HERE / name)
                          for name in ("engine_v2.py", "diagnostics_v2.py", "run_matrix.py")},
        "invocation": sys.argv, "python": sys.executable,
    }
    pp = args.output / "PROTOCOL.json"
    if pp.exists():
        if not args.resume:
            raise RuntimeError("PROTOCOL.json exists; use --resume or a new --output")
        old = json.loads(pp.read_text(encoding="utf-8"))
        for key in ("datasets", "branches"):
            if old.get(key) != protocol.get(key):
                raise RuntimeError(f"Resume identity mismatch: {key}")
        # A code edit between batches is recorded explicitly instead of being
        # hidden: the previous hashes are kept, the reason is attached, and every
        # unit still carries the protocol hash it was produced under.
        if old.get("source_hashes") != protocol.get("source_hashes"):
            amendments = old.get("code_amendments", [])
            amendments.append({
                "recorded_utc": now(),
                "previous_source_hashes": old.get("source_hashes"),
                "current_source_hashes": protocol.get("source_hashes"),
                "reason": args.code_amendment_reason or "unspecified",
                "scope": ("resume bookkeeping only; units already completed keep their own "
                          "protocol_hash and are not recomputed"),
            })
            old["code_amendments"] = amendments
            old["source_hashes"] = protocol["source_hashes"]
            print(f"[matrix] recording code amendment: {amendments[-1]['reason']}", flush=True)
        # The matrix is filled in pre-registered batches (P1-A seeds 0/1, P1-B seed 2).
        # The frozen design (datasets, branches, source hashes) must not change, but the
        # per-invocation scope may grow; the union is recorded.
        history = old.get("scope_history", [])
        history.append({"seeds": list(args.seeds), "shots": list(args.shots),
                        "categories": {d: (args.categories or CATS[d]) for d in args.datasets}})
        old["scope_history"] = history
        old["seeds_observed"] = sorted({s for item in history for s in item["seeds"]})
        old["shots_observed"] = sorted({s for item in history for s in item["shots"]})
        pp.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        protocol["scope_history"] = [{"seeds": list(args.seeds), "shots": list(args.shots),
                                      "categories": {d: (args.categories or CATS[d])
                                                     for d in args.datasets}}]
        dump(pp, protocol)

    logs = args.output / "logs"
    logs.mkdir(exist_ok=True)
    start = time.time()
    deadline = start + args.max_hours * 3600
    timings, failures = [], []
    state = "running"
    for dataset, seed, shot, cat in expected:
        unit = args.output / "units" / f"{dataset}_s{seed}_k{shot}" / cat
        if (unit / "DONE.json").exists():
            continue
        remaining = deadline - time.time() - 60
        estimated = max(timings[-3:], default=120.0) * 1.5
        if remaining < estimated:
            state = "paused_time_budget"
            break
        dump(args.output / "STATUS.json", {"state": "running", "unit": f"{dataset}/s{seed}/K{shot}/{cat}",
                                           "updated_utc": now(),
                                           "completed": len([p for p in args.output.glob("units/*/*/DONE.json")]),
                                           "expected": len(expected),
                                           "remaining_seconds": remaining})
        command = [sys.executable, "-u", str(Path(__file__).resolve()),
                   "--unit-dataset", dataset, "--unit-seed", str(seed), "--unit-shot", str(shot),
                   "--unit-category", cat, "--output", str(args.output),
                   "--branches", *args.branches, "--permutations", str(args.permutations),
                   "--device", args.device, "--chunk", str(args.chunk), "--stride", str(args.stride)]
        t0 = time.time()
        with (logs / f"{dataset}_s{seed}_k{shot}_{cat}.log").open("a", encoding="utf-8") as log:
            proc = subprocess.Popen(command, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            try:
                code = proc.wait(timeout=min(remaining, args.unit_timeout_minutes * 60))
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                code = -9
                failures.append({"dataset": dataset, "seed": seed, "shot": shot,
                                 "category": cat, "reason": "unit_time_limit"})
        timings.append(time.time() - t0)
        if code != 0:
            if code != -9:
                failures.append({"dataset": dataset, "seed": seed, "shot": shot,
                                 "category": cat, "exit_code": code})
            state = "needs_attention"
            break
        collect(args.output, expected, "running")
    else:
        state = "completed"
    dump(args.output / "FAILURES.json", failures)
    summary = collect(args.output, expected, state)
    dump(args.output / "STATUS.json", {"state": state, "updated_utc": now(),
                                       "completed_units": summary["completed_units"],
                                       "expected_units": len(expected),
                                       "total_seconds": time.time() - start})
    print(json.dumps({"state": state, "completed": summary["completed_units"],
                      "expected": len(expected), "elapsed_s": round(time.time() - start, 1)}),
          flush=True)
    return 0 if state in ("completed", "paused_time_budget") else 1


if __name__ == "__main__":
    raise SystemExit(main())
