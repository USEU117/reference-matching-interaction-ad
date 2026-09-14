"""R1: seed-1 three-branch (B/S/C) fair replication, plus the missing seed-0 ``DUP_L``.

Two stages, each writing into its own sub-directory and never touching the
frozen run directories:

``--stage units``
    Score and evaluate the 12 seed-1 three-branch units with the frozen loader,
    scorer and post-processing.  The pre-declared matrix holds the family weight
    fixed so that "new representation" can be separated from "new weight":

    ====================  ================  ================  ==========
    weights               no new info       S replaces Bcopy  L endpoint
    ====================  ================  ================  ==========
    B/Bcopy/C = 1/3       DUP_J             TRI_J             DUP_L/TRI_L
    B/Bcopy=1/4, C=1/2    DUP_BAL_J≡A1_J    BAL_J             DUP_BAL_L≡A1_L/BAL_L
    ====================  ================  ================  ==========

``--stage seed0``
    Rebuild the missing ``DUP_L`` endpoint for seed 0 from the stored 32x32
    branch distances and re-evaluate it with the same post-processing, then
    assemble a same-caliber unit set for both seeds.

``--stage analyze``
    Bootstrap both seeds with the frozen random stream and report the frozen
    fair contrasts, the matching (L-J) contrasts and the AP-level interaction
    difference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import complete_statistics as cs  # noqa: E402
import diagnostics  # noqa: E402
import engine  # noqa: E402
import replicate_seed1_bc as rs  # noqa: E402

ROOT = HERE.parents[1]
PILOT = ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912"
MAIN0 = PILOT / "main_v2"
B_ROOT = ROOT / "outputs/dynamic_fusion/v3_direction_a"
NEXT = PILOT / "controlled_fusion_next_stage_20260913"
GATE = NEXT / "R0_diagnostics/AUDIT_IDENTITY_GATE.json"
CATEGORIES = list(cs.CATEGORIES)
SHOTS = (2, 4)
SEED1 = 1
TOL = 1e-6
BOOTSTRAP_SEED = 20260912
EFFECT_SCALE = 0.005

# Detector methods written by the seed-1 three-branch run (G and the DUP-only
# diagnostics are excluded; the *_G arrays are diagnostics by the frozen rule).
TRIPLE_DETECTORS = [
    "B", "C", "S",
    "A1_J", "TRI_J", "BAL_J", "DUP_J", "DUP_BAL_J", "DUP_EXPECTED_J",
    "A1_L", "DUP_L", "DUP_BAL_L", "TRI_L", "BAL_L",
    "A1_lambda_0.25", "A1_lambda_0.50", "A1_lambda_0.75",
    "TRI_lambda_0.25", "TRI_lambda_0.50", "TRI_lambda_0.75",
    "BAL_lambda_0.25", "BAL_lambda_0.50", "BAL_lambda_0.75",
]
SINGLE_BRANCH = ("B", "C", "S")

# Pre-declared contrasts.  "representation" holds the family weight fixed and
# swaps the copied B for the real S; "matching" is the L-J effect of each
# construction; "interaction" is a controlled difference of AP differences.
FAIR_CONTRASTS = (
    ("TRI_J", "DUP_J", "representation"),
    ("TRI_L", "DUP_L", "representation"),
    ("BAL_J", "A1_J", "representation"),
    ("BAL_L", "A1_L", "representation"),
    ("A1_L", "A1_J", "matching"),
    ("DUP_L", "DUP_J", "matching"),
    ("TRI_L", "TRI_J", "matching"),
    ("BAL_L", "BAL_J", "matching"),
)
INTERACTION_CONTRASTS = (
    ("(TRI_J-DUP_J)-(TRI_L-DUP_L)", ("TRI_J", "DUP_J"), ("TRI_L", "DUP_L")),
    ("(BAL_J-A1_J)-(BAL_L-A1_L)", ("BAL_J", "A1_J"), ("BAL_L", "A1_L")),
)
# Same-caliber seed-0 plane set that the frozen cache already holds; ``DUP_L`` is
# rebuilt separately because the frozen run never stored that endpoint.
SEED0_FAIR_METHODS = ["A1_J", "A1_L", "DUP_J", "TRI_J", "TRI_L", "BAL_J", "BAL_L"]


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                          encoding="utf-8")


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def dump(path: Path, payload) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for part in iter(lambda: fh.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


# --------------------------------------------------------------------------- seed-1 units


def build_configs(shot: int) -> tuple[list[dict], dict]:
    rows = shot * 1024
    common = np.random.default_rng(BOOTSTRAP_SEED).permutation(rows)
    base = {
        "B": {"B": 1.0}, "C": {"C": 1.0}, "S": {"S": 1.0},
        "A1_J": {"B": .5, "C": .5},
        "TRI_J": {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3},
        "BAL_J": {"B": .25, "S": .25, "C": .5},
        "DUP_J": {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3},
        "DUP_BAL_J": {"B": .25, "Bcopy": .25, "C": .5},
        "DUP_EXPECTED_J": {"B": 2 / 3, "C": 1 / 3},
    }
    configs = [{"name": name, "weights": w, "permutations": {}} for name, w in base.items()]
    for name in ("A1_J", "TRI_J", "BAL_J"):
        configs.append({"name": f"INV_COMMON_{name}", "weights": base[name],
                        "permutations": {b: common for b in base[name]}})
    return configs, {"common": common}


def derive_endpoints(scored: dict) -> None:
    b, c, s = scored["B"], scored["C"], scored["S"]
    scored["A1_L"] = (.5 * b + .5 * c).astype(np.float32)
    scored["DUP_L"] = (np.float32(2.0 / 3.0) * b + np.float32(1.0 / 3.0) * c).astype(np.float32)
    scored["DUP_BAL_L"] = (.25 * b + .25 * b + .5 * c).astype(np.float32)
    scored["TRI_L"] = ((b + s + c) / np.float32(3.0)).astype(np.float32)
    scored["BAL_L"] = (.25 * b + .25 * s + .5 * c).astype(np.float32)
    for prefix in ("A1", "TRI", "BAL"):
        g = (scored[f"{prefix}_J"] - scored[f"{prefix}_L"]).astype(np.float32)
        scored[f"{prefix}_G"] = g
        for lam in (.25, .5, .75):
            scored[f"{prefix}_lambda_{lam:.2f}"] = (scored[f"{prefix}_L"] + np.float32(lam) * g).astype(np.float32)


def run_seed1_unit(out_root: Path, cat: str, shot: int, device: str, chunk: int) -> dict:
    import torch
    sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
    import common as C

    torch.set_num_threads(4)
    C.faiss.omp_set_num_threads(4)
    out = out_root / "units" / f"s1_k{shot}" / cat
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    dump(out / "progress.json", {"state": "loading", "updated_utc": now()})

    inp = engine.load_inputs(SEED1, 4, cat, branches=SINGLE_BRANCH)
    inp["r"] = {b: np.ascontiguousarray(r[: shot * 1024]) for b, r in inp["r"].items()}
    inp["q"]["Bcopy"] = inp["q"]["B"]
    inp["r"]["Bcopy"] = inp["r"]["B"]
    load_s = time.monotonic() - start

    configs, perm_arrays = build_configs(shot)
    np.savez_compressed(out / "reference_permutations.npz", **perm_arrays)
    dump(out / "configurations.json", [
        {"name": cfg["name"], "distance_weights": cfg["weights"],
         "permutation_hashes": {b: hashlib.sha256(v.tobytes()).hexdigest()
                                for b, v in cfg["permutations"].items()}}
        for cfg in configs])
    dump(out / "progress.json", {"state": "scoring", "updated_utc": now(), "n": inp["n"],
                                 "configurations": len(configs), "load_s": load_s})
    score_start = time.monotonic()
    scored, engine_info = engine.score(inp, configs, device=device, chunk=chunk)
    score_s = time.monotonic() - score_start

    checks: dict = {}

    def check(name: str, error: float, tol: float = TOL) -> None:
        checks[name] = {"max_abs_error": float(error), "tolerance": tol,
                        "pass": bool(float(error) <= tol)}

    check("duplicate_matches_weighted_pair", float(np.max(np.abs(scored["DUP_J"] - scored["DUP_EXPECTED_J"]))))
    check("balanced_duplicate_matches_A1", float(np.max(np.abs(scored["DUP_BAL_J"] - scored["A1_J"]))))
    for name in ("A1_J", "TRI_J", "BAL_J"):
        check(f"common_permutation_{name}", float(np.max(np.abs(scored[name] - scored[f"INV_COMMON_{name}"]))))

    count = min(2048, len(inp["q"]["B"]))
    parity_index = np.linspace(0, len(inp["q"]["B"]) - 1, count, dtype=np.int64)
    for branch_set, name in ((("B", "C"), "A1_J"), (("B", "S", "C"), "TRI_J")):
        scale = np.sqrt(1.0 / len(branch_set))
        q_cat = C.unit_rows(np.concatenate([inp["q"][b][parity_index] * scale for b in branch_set], axis=1))
        r_cat = C.unit_rows(np.concatenate([inp["r"][b] * scale for b in branch_set], axis=1))
        legacy = C.knn_dist(q_cat, r_cat)[:, 0]
        check(f"legacy_{name}_faiss_real_patch_parity",
              float(np.max(np.abs(legacy - scored[name].reshape(-1)[parity_index]))))
        del q_cat, r_cat, legacy

    derive_endpoints(scored)
    check("balanced_duplicate_L_matches_A1_L", float(np.max(np.abs(scored["DUP_BAL_L"] - scored["A1_L"]))))
    for prefix in ("A1", "TRI", "BAL"):
        check(f"{prefix}_nonnegative_G", max(0.0, -float(scored[f"{prefix}_G"].min())))
    for prefix in ("TRI", "BAL"):
        dj = scored[f"{prefix}_J"] - scored["A1_J"]
        dl = scored[f"{prefix}_L"] - scored["A1_L"]
        dg = scored[f"{prefix}_G"] - scored["A1_G"]
        check(f"{prefix}_score_decomposition", float(np.max(np.abs(dj - dl - dg))))

    masks, labels = inp["masks"], inp["labels"]
    ids = [str(x) for x in inp["sample_ids"]]
    paths = {k: str(v) for k, v in inp.get("paths", {}).items()}
    del inp
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    saved = {k: v for k, v in scored.items() if not k.startswith("INV_")}
    np.savez_compressed(out / "patch_scores.npz", **saved, sample_ids=np.asarray(ids))
    dump(out / "progress.json", {"state": "metrics", "updated_utc": now(), "score_s": score_s,
                                 "n_scores": len(saved)})
    metric_start = time.monotonic()
    result = rs.evaluate_methods({k: saved[k] for k in TRIPLE_DETECTORS}, masks, labels, ids, out,
                                 include_aupro=True)
    timing = {"load_s": load_s, "score_s": score_s,
              "metric_s": time.monotonic() - metric_start, "total_s": time.monotonic() - start}
    inv = {"all_pass": all(v["pass"] for v in checks.values()), "checks": checks,
           "historical_baseline": {"status": "no_seed1_historical_baseline",
                                   "note": "the validation-handoff metrics only contain reference seed 0"}}
    dump(out / "invariants.json", inv)
    if not inv["all_pass"]:
        failed = [k for k, v in checks.items() if not v["pass"]]
        raise RuntimeError(f"seed1 triple invariant failure in {cat} K{shot}: {failed}")
    dump(out / "DONE.json", {
        "status": "completed", "scientific_status": "exploratory_only", "finished_utc": now(),
        "category": cat, "shot": shot, "seed": SEED1, "n_images": len(ids),
        "configurations": len(configs), "canonical_source_shot": 4,
        "selected_reference_images": shot, "branches": list(SINGLE_BRANCH),
        "timing": timing, "inputs": paths, "engine": engine_info,
        "diagnostics": result, "invariants_pass": True})
    dump(out / "progress.json", {"state": "completed", "updated_utc": now(), "timing": timing})
    print(f"[triple] DONE {cat} K{shot}: {timing}", flush=True)
    return {"category": cat, "shot": shot, "timing": timing, "invariants_pass": True}


# --------------------------------------------------------------------------- seed-0 DUP_L


def build_seed0_same_caliber(out_root: Path) -> dict:
    """Rebuild DUP_L for seed 0 and assemble the same-caliber 9-method unit set.

    ``DUP_L = (2/3) d_B^min + (1/3) d_C^min`` is linear in the stored single-branch
    distances, so it is reconstructed from ``patch_scores.npz`` and pushed through
    the frozen 448 post-processing rather than guessed from another method.
    """
    import csv as csv_module

    methods = SEED0_FAIR_METHODS + ["DUP_L"]
    summary = {}
    for shot in SHOTS:
        for cat in CATEGORIES:
            src = MAIN0 / "units" / f"s0_k{shot}" / cat
            dst = out_root / "seed0_same_caliber/units" / f"s0_k{shot}" / cat
            dst.mkdir(parents=True, exist_ok=True)
            with np.load(src / "patch_scores.npz", allow_pickle=False) as z:
                b = np.asarray(z["B"], dtype=np.float32)
                c = np.asarray(z["C"], dtype=np.float32)
                ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            dup_l_patch = (np.float32(2.0 / 3.0) * b + np.float32(1.0 / 3.0) * c).astype(np.float32)
            done0 = read_json(src / "DONE.json")
            n_images = int(done0["n_images"])
            masks, labels, canonical_ids = engine._load_canonical_metadata(
                B_ROOT / f"features_vitb14_s0_k4/anomalydino_visual/{cat}.npz")
            if [str(x) for x in canonical_ids] != ids:
                raise RuntimeError(f"{cat} K{shot}: sample_ids disagree between patch scores and masks")
            dup_metrics = rs.evaluate_methods({"DUP_L": dup_l_patch}, masks, labels, ids, dst,
                                              include_aupro=True)["metrics"]["DUP_L"]

            with np.load(src / "evaluation_scores.npz", allow_pickle=False) as z:
                names = [str(x) for x in z["method_names"]]
                index = {name: i for i, name in enumerate(names)}
                missing = [m for m in SEED0_FAIR_METHODS if m not in index]
                if missing:
                    raise RuntimeError(f"{src}: missing methods {missing}")
                keep = [index[m] for m in SEED0_FAIR_METHODS]
                planes = np.array(z["pixel_scores"][keep], dtype=np.float32)
                images = np.array(z["image_scores"][keep], dtype=np.float32)
                pixel_masks = np.asarray(z["pixel_masks"])
                labels_arr = np.asarray(z["labels"])
                sample_ids = np.asarray(z["sample_ids"])
            with np.load(dst / "evaluation_scores.npz", allow_pickle=False) as z:
                dup_l_plane = np.asarray(z["pixel_scores"][0], dtype=np.float32)
                dup_l_image = np.asarray(z["image_scores"][0], dtype=np.float32)

            np.savez_compressed(dst / "evaluation_scores.npz",
                                method_names=np.asarray(methods, dtype=np.str_),
                                pixel_scores=np.concatenate([planes, dup_l_plane[None]], axis=0),
                                pixel_masks=pixel_masks,
                                image_scores=np.concatenate([images, dup_l_image[None]], axis=0),
                                labels=labels_arr, sample_ids=sample_ids)
            with (src / "metrics.csv").open(encoding="utf-8-sig") as fh:
                final_rows = [row for row in csv_module.DictReader(fh)
                              if row["method"] in SEED0_FAIR_METHODS]
            final_rows.append({"method": "DUP_L",
                               **{k: dup_metrics.get(k) for k in
                                  ("pixel_auroc", "pixel_ap", "pixel_aupro", "image_auroc",
                                   "image_ap", "image_f1_max")}})
            diagnostics._write_csv(dst / "metrics.csv",
                                   ["method", "pixel_auroc", "pixel_ap", "pixel_aupro",
                                    "image_auroc", "image_ap", "image_f1_max"], final_rows)
            dump(dst / "DONE.json", {"status": "completed", "category": cat, "shot": shot, "seed": 0,
                                     "n_images": n_images, "invariants_pass": True,
                                     "canonical_source_shot": 4, "selected_reference_images": shot,
                                     "derived_from": str(src / "patch_scores.npz")})
            summary[f"k{shot}/{cat}"] = {"DUP_L_pixel_ap": dup_metrics.get("pixel_ap"),
                                         "DUP_L_image_ap": dup_metrics.get("image_ap")}
            print(f"[seed0] DUP_L rebuilt for {cat} K{shot}", flush=True)
    return summary


# --------------------------------------------------------------------------- analysis


def contrast_rows(bootstrap_result: dict, point: dict, seed: int) -> list[dict]:
    arrays = bootstrap_result["arrays"]
    shot = bootstrap_result["shot"]
    rows: list[dict] = []
    for metric in cs.METRIC_KEYS:
        for method, other, group in FAIR_CONTRASTS:
            if method not in arrays or other not in arrays:
                continue
            stats = cs._ci(arrays[method][metric] - arrays[other][metric])
            stats.update({"reference_seed": seed, "shot": shot, "contrast": f"{method} - {other}",
                          "contrast_group": group, "metric": metric, "method": method,
                          "reference": other,
                          "point_delta": point[method][metric] - point[other][metric],
                          "multiple_comparison_adjusted": False})
            rows.append(stats)
        for label, first, second in INTERACTION_CONTRASTS:
            if any(m not in arrays for pair in (first, second) for m in pair):
                continue
            delta = ((arrays[first[0]][metric] - arrays[first[1]][metric])
                     - (arrays[second[0]][metric] - arrays[second[1]][metric]))
            stats = cs._ci(delta)
            stats.update({"reference_seed": seed, "shot": shot, "contrast": label,
                          "contrast_group": "interaction", "metric": metric,
                          "method": "", "reference": "",
                          "point_delta": None, "multiple_comparison_adjusted": False})
            rows.append(stats)
    return rows


def run_bootstrap(out_root: Path, structures_by_shot: dict, methods: list[str], tag: str,
                  replicates: int, resume: bool) -> dict[int, dict]:
    results: dict[int, dict] = {}
    for shot in sorted(structures_by_shot):
        identity = cs.sequence_identity(out_root, structures_by_shot[shot], methods,
                                        BOOTSTRAP_SEED, shot)
        checkpoint = out_root / f"{tag}_bootstrap_k{shot}.npz"
        print(f"[{tag}] bootstrapping K{shot}: {len(methods)} methods x {replicates}", flush=True)
        results[shot] = cs.bootstrap(structures_by_shot[shot], methods, replicates, BOOTSTRAP_SEED,
                                     checkpoint, 25, resume, identity, 0.0)
        print(f"[{tag}] K{shot}: {results[shot]['replicates_used']} replicates in "
              f"{results[shot]['seconds']}s", flush=True)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("units", "seed0", "analyze"), required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-seed0", action="store_true")
    args = parser.parse_args()
    triple_root = NEXT / "R1_seed1_triple"
    triple_root.mkdir(parents=True, exist_ok=True)

    gate = read_json(GATE) if GATE.exists() else None
    if not gate or not gate.get("all_pass"):
        raise SystemExit("R0 identity gate is missing or failed; refusing to run R1")

    if args.stage == "units":
        write_json(triple_root / "PROTOCOL.json", {
            "stage": "R1_seed1_triple", "seed": SEED1, "branches": list(SINGLE_BRANCH),
            "dataset": "mpdd", "dataset_role": "development",
            "categories": CATEGORIES, "shots": list(SHOTS),
            "detectors": TRIPLE_DETECTORS,
            "weights": {"A1_J": {"B": .5, "C": .5},
                        "TRI_J": {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3},
                        "BAL_J": {"B": .25, "S": .25, "C": .5},
                        "DUP_J": {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3},
                        "DUP_BAL_J": {"B": .25, "Bcopy": .25, "C": .5},
                        "DUP_EXPECTED_J": {"B": 2 / 3, "C": 1 / 3},
                        "DUP_L": {"B": 2 / 3, "C": 1 / 3},
                        "TRI_L": {"B": 1 / 3, "S": 1 / 3, "C": 1 / 3},
                        "BAL_L": {"B": .25, "S": .25, "C": .5}},
            "cache_policy": "canonical K4 query and reference; K2 uses the first two K4 references",
            "postprocess": "448 bilinear then gaussian sigma4; image max; stride-8 evaluation",
            "sources": {"B": str(engine.branch_dir("B", SEED1, 4)),
                        "C": str(engine.branch_dir("C", SEED1, 4)),
                        "S": str(engine.branch_dir("S", SEED1, 4)),
                        "gate": str(GATE), "gate_sha256": sha(GATE)},
            "code_hashes": {name: sha(HERE / name) for name in
                            ("engine.py", "diagnostics.py", "complete_statistics.py",
                             "replicate_seed1_bc.py", "run_seed1_triple.py")},
            "created_utc": now()})
        failures = []
        for shot in SHOTS:
            for cat in CATEGORIES:
                unit = triple_root / "units" / f"s1_k{shot}" / cat
                if args.resume and (unit / "DONE.json").exists():
                    print(f"[triple] skip existing {cat} K{shot}", flush=True)
                    continue
                try:
                    run_seed1_unit(triple_root, cat, shot, args.device, args.chunk)
                except Exception as exc:  # noqa: BLE001 - recorded, never hidden
                    failures.append({"category": cat, "shot": shot,
                                     "error": f"{type(exc).__name__}: {exc}"})
                    write_json(triple_root / "FAILURES.json", failures)
                    raise
        write_json(triple_root / "FAILURES.json", failures)
        return 0

    if args.stage == "seed0":
        summary = build_seed0_same_caliber(triple_root)
        write_json(triple_root / "SEED0_DUP_L.json", summary)
        return 0

    # ---- analyze
    structures1 = {}
    for shot in SHOTS:
        rows = []
        for cat in CATEGORIES:
            rows.append(cs.build_category(triple_root / "units" / f"s1_k{shot}" / cat, shot,
                                          TRIPLE_DETECTORS))
        structures1[shot] = rows
    results1 = run_bootstrap(triple_root, structures1, TRIPLE_DETECTORS, "TRIPLE", args.replicates,
                             args.resume)
    point1 = {shot: cs.macro_point(structures1[shot], TRIPLE_DETECTORS) for shot in SHOTS}
    rows1 = [row for shot in sorted(results1) for row in contrast_rows(results1[shot], point1[shot], SEED1)]

    results0 = {}
    point0 = {}
    rows0 = []
    if not args.skip_seed0:
        root0 = triple_root / "seed0_same_caliber"
        if not (root0 / "units").exists():
            raise SystemExit("seed-0 same-caliber units are missing; run --stage seed0 first")
        methods0 = SEED0_FAIR_METHODS + ["DUP_L"]
        structures0 = {}
        for shot in SHOTS:
            structures0[shot] = [cs.build_category(root0 / "units" / f"s0_k{shot}" / cat, shot, methods0)
                                 for cat in CATEGORIES]
        results0 = run_bootstrap(root0, structures0, methods0, "SEED0_FAIR", args.replicates,
                                 args.resume)
        point0 = {shot: cs.macro_point(structures0[shot], methods0) for shot in SHOTS}
        rows0 = [row for shot in sorted(results0) for row in contrast_rows(results0[shot], point0[shot], 0)]

    all_rows = rows0 + rows1
    cs.write_csv(triple_root / "fair_contrasts.csv",
                 ["reference_seed", "shot", "contrast", "contrast_group", "metric", "method",
                  "reference", "point_delta", "mean_delta", "ci_low", "ci_high",
                  "fraction_below_zero", "n_replicates", "multiple_comparison_adjusted"], all_rows)

    same_caliber = []
    for row in all_rows:
        if row["metric"] != "pixel_ap":
            continue
        same_caliber.append({"reference_seed": row["reference_seed"], "shot": row["shot"],
                             "contrast": row["contrast"], "contrast_group": row["contrast_group"],
                             "point_delta": row["point_delta"], "ci_low": row["ci_low"],
                             "ci_high": row["ci_high"],
                             "exceeds_scale": (None if row["point_delta"] is None
                                               else bool(abs(row["point_delta"]) >= EFFECT_SCALE)),
                             "ci_excludes_zero": (None if row["ci_low"] is None
                                                  else bool(row["ci_low"] > 0 or row["ci_high"] < 0)),
                             "n_replicates": row["n_replicates"]})
    cs.write_csv(triple_root / "same_caliber_fair_table.csv",
                 ["reference_seed", "shot", "contrast", "contrast_group", "point_delta", "ci_low",
                  "ci_high", "exceeds_scale", "ci_excludes_zero", "n_replicates"], same_caliber)

    point_rows = []
    for seed, table, methods in ((1, point1, TRIPLE_DETECTORS),
                                 (0, point0, SEED0_FAIR_METHODS + ["DUP_L"])):
        if not table:
            continue
        for shot in SHOTS:
            for method in methods:
                if method not in table.get(shot, {}):
                    continue
                point_rows.append({"reference_seed": seed, "shot": shot, "method": method,
                                   **table[shot][method]})
    cs.write_csv(triple_root / "point_by_condition.csv",
                 ["reference_seed", "shot", "method", "pixel_auroc", "pixel_ap", "image_auroc",
                  "image_ap"], point_rows)

    samples = {}
    for seed, results in ((0, results0), (1, results1)):
        for shot, result in results.items():
            for method, metrics in result["arrays"].items():
                for key, values in metrics.items():
                    samples[f"s{seed}_k{shot}__{method}__{key}"] = values
    if samples:
        np.savez_compressed(triple_root / "bootstrap_samples.npz", **samples)

    unit_gate = {}
    for shot in SHOTS:
        for cat in CATEGORIES:
            inv = read_json(triple_root / "units" / f"s1_k{shot}" / cat / "invariants.json")
            unit_gate[f"k{shot}/{cat}"] = inv["all_pass"]
    acceptance = {
        "seed1_units": sum(1 for shot in SHOTS for cat in CATEGORIES
                           if (triple_root / "units" / f"s1_k{shot}" / cat / "DONE.json").exists()),
        "expected_units": len(SHOTS) * len(CATEGORIES),
        "unit_invariants_all_pass": all(unit_gate.values()),
        "replicates_used_seed1": {shot: results1[shot]["replicates_used"] for shot in sorted(results1)},
        "replicates_used_seed0": {shot: results0[shot]["replicates_used"] for shot in sorted(results0)},
        "identity_gate_all_pass": True,
    }
    acceptance["pass"] = bool(acceptance["seed1_units"] == acceptance["expected_units"]
                              and acceptance["unit_invariants_all_pass"]
                              and all(v == args.replicates
                                      for v in acceptance["replicates_used_seed1"].values())
                              and (not results0 or all(v == args.replicates
                                                       for v in acceptance["replicates_used_seed0"].values())))
    verification = {"acceptance": acceptance, "unit_invariants": unit_gate,
                    "identity_gate": str(GATE)}
    write_json(triple_root / "verification.json", verification)
    write_json(triple_root / "RUN_SUMMARY.json", {
        "stage": "R1_seed1_triple", "state": "completed" if acceptance["pass"] else "completed_with_findings",
        "finished_utc": now(), "acceptance": acceptance,
        "detectors": TRIPLE_DETECTORS, "fair_contrasts": [c[0] + " - " + c[1] for c in FAIR_CONTRASTS],
        "effect_scale": EFFECT_SCALE,
        "note": ("representation = family weight held fixed, copied B replaced by real S; "
                 "matching = L minus J within one construction; interaction = AP-level controlled "
                 "difference of differences, not the patch-level J=L+G decomposition")})
    write_json(triple_root / "STATUS.json", {"state": "completed", "finished_utc": now(),
                                             "acceptance_pass": acceptance["pass"]})
    write_json(triple_root / "ARTIFACT_MANIFEST.json", cs.artifact_manifest(triple_root))
    print(json.dumps({"acceptance_pass": acceptance["pass"]}, ensure_ascii=False), flush=True)
    return 0 if acceptance["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
