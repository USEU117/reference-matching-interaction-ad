"""R3: frozen B/C reference-coupling re-check on the protocol holdout dataset (BTAD).

The project protocol assigns MPDD as the development dataset and BTAD as the
one-time holdout (``configs/dynamic_fusion_v2_data_protocol.yaml``); MVTec and
VisA are retrospective checks.  BTAD already carries B/C caches for reference
seeds 0..2 and K in {1,2,4}, so no model has to run for this stage, and no
parameter may be chosen from its results.

Two honest labels are enforced by this file:

* BTAD has already been evaluated by an earlier frozen pipeline
  (``experiments/dynamic_fusion/v3_3/btad_holdout/report.json``).  This stage is
  therefore a *known-dataset frozen re-check*, not a first-time unseen-data
  validation, and the report says so.
* No DINO-S cache exists for BTAD, so the three-branch mechanism cannot be
  replicated here.  Only the pre-declared B/C matrix runs; the representation
  contrasts are recorded as ``not_run`` with the reason.

Stages: ``--stage audit`` (read-only identity/completeness gate),
``--stage units`` (frozen scoring + evaluation of the B/C matrix),
``--stage analyze`` (paired image bootstrap and the pre-declared contrasts).
"""
from __future__ import annotations

import argparse
import csv
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
NEXT = PILOT / "controlled_fusion_next_stage_20260913"
OUT = NEXT / "R3_external"
B_ROOT = ROOT / "outputs/dynamic_fusion/v3_direction_a"
MANIFEST = ROOT / "data/splits/btad/manifest.json"
PROTOCOL_YAML = ROOT / "configs/dynamic_fusion_v2_data_protocol.yaml"
DEVELOPMENT_GUARD = ROOT / "src/industrial_ad/innovation_v2/common.py"
PRIOR_ACCESS = ROOT / "experiments/dynamic_fusion/v3_3/btad_holdout/report.json"

DATASET = "btad"
SEEDS = (0, 1)
SHOTS = (2, 4)
CATEGORIES = ["01", "02"]
# Decided by the read-only audit *before* any scoring: BTAD category 03 stores a
# 32x42 DINOv2-B patch grid, which is outside the frozen 32x32 branch contract of
# the reference-coupling engine.  Resampling it would change the frozen pipeline,
# so the category is declared out of scope instead of being silently adapted.
EXCLUDED_CATEGORIES = {"03": "BTAD 03 stores a 32x42 DINOv2-B patch grid; the frozen engine only "
                             "accepts the 32x32 canonical grid, and adapting it would change the "
                             "frozen protocol"}
CANONICAL_SHOT = 4
BOOTSTRAP_SEED = 20260912
REPLICATES_DEFAULT = 1000
EFFECT_SCALE = cs.EFFECT_SCALE
TOL = 1e-6
QUERY_COSINE_MIN = 0.99999
# The stored K2/K4 reference files come from separate export runs, so their rows
# are not bit-identical; this bound only catches a wrong reference image.
STORED_K2_COSINE_MIN = 0.999
GRID_EXPECTED = {"B": (32, 32), "C": (37, 37)}

# The pre-declared B/C minimum matrix.  DUP_L is linear in the stored single
# branch distances; the DUP_* controls are implementation invariants and are
# reported as controls, never as evidence for the mechanism.
DETECTORS = ["B", "C", "A1_J", "A1_L", "DUP_J", "DUP_L", "DUP_BAL_J", "DUP_BAL_L",
             "DUP_EXPECTED_J", "A1_lambda_0.25", "A1_lambda_0.50", "A1_lambda_0.75"]
CONTRASTS = (
    ("DUP_J - A1_J", "DUP_J", "A1_J", "weight"),
    ("A1_L - DUP_L", "A1_L", "DUP_L", "weight"),
    ("A1_L - A1_J", "A1_L", "A1_J", "matching"),
    ("DUP_L - DUP_J", "DUP_L", "DUP_J", "matching"),
    ("DUP_BAL_J - A1_J", "DUP_BAL_J", "A1_J", "equivalence_control"),
    ("DUP_BAL_L - A1_L", "DUP_BAL_L", "A1_L", "equivalence_control"),
    ("DUP_EXPECTED_J - DUP_J", "DUP_EXPECTED_J", "DUP_J", "equivalence_control"),
)
NOT_RUN = (
    {"contrast": "TRI_J - DUP_J", "group": "representation",
     "reason": "no DINO-S cache exists for BTAD, so the third branch cannot be scored"},
    {"contrast": "BAL_J - A1_J", "group": "representation",
     "reason": "no DINO-S cache exists for BTAD, so the third branch cannot be scored"},
)


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def dump(path: Path, payload) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def branch_file(branch: str, seed: int, shot: int, category: str) -> Path:
    if branch == "B":
        return B_ROOT / f"features_vitb14_btad_s{seed}_k{shot}" / "anomalydino_visual" / f"{category}.npz"
    if branch == "C":
        return B_ROOT / f"features_btad_s{seed}_k{shot}" / "anomalyclip_text" / f"{category}.npz"
    raise ValueError(f"BTAD only carries the B/C matrix here, got {branch!r}")


# --------------------------------------------------------------------------- audit


def audit_unit(seed: int, shot: int, category: str) -> dict:
    """Read-only metadata audit of one stored BTAD unit; no features are scored."""

    record: dict = {"seed": seed, "shot": shot, "category": category, "checks": {}}

    def check(name: str, ok: bool, detail) -> None:
        record["checks"][name] = {"pass": bool(ok), "detail": detail}

    headers = {}
    for branch in ("B", "C"):
        path = branch_file(branch, seed, shot, category)
        if not path.exists():
            check(f"{branch}_file_exists", False, str(path))
            continue
        # Shapes come from the zip header; only small metadata arrays are decompressed.
        n_query = int(rs.npz_header(path, "patch_features")[0][0])
        n_ref = int(rs.npz_header(path, "ref_patch_features")[0][0])
        masks_shape = list(rs.npz_header(path, "imgs_masks")[0])
        with np.load(path, allow_pickle=False) as z:
            files = set(z.files)
            scalar = lambda key: (str(np.asarray(z[key]).reshape(-1)[0]) if key in files else None)  # noqa: E731
            header = {
                "dataset": scalar("dataset"), "dataset_role": scalar("dataset_role"),
                "branch": scalar("branch"),
                "seed": int(np.asarray(z["seed"]).reshape(-1)[0]) if "seed" in files else None,
                "shot": int(np.asarray(z["shot"]).reshape(-1)[0]) if "shot" in files else None,
                "grid_size": [int(v) for v in np.asarray(z["grid_size"]).reshape(-1)],
                "score_direction": scalar("score_direction"),
                "n_query": n_query, "n_ref": n_ref,
                "sample_ids": [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)],
                "gt": np.asarray(z["gt_sp"]).reshape(-1).astype(np.int32) if "gt_sp" in files else None,
                "masks_shape": masks_shape,
            }
        header["masks_unique"] = None
        if shot == CANONICAL_SHOT:
            with np.load(path, allow_pickle=False) as z:
                header["masks_unique"] = sorted(int(v) for v in np.unique(np.asarray(z["imgs_masks"])))
        headers[branch] = header
        check(f"{branch}_internal_metadata",
              header["dataset"] == DATASET and header["seed"] == seed and header["shot"] == shot
              and tuple(header["grid_size"]) == GRID_EXPECTED[branch],
              {k: header[k] for k in ("dataset", "dataset_role", "branch", "seed", "shot", "grid_size",
                                      "score_direction", "n_query", "n_ref")})
        check(f"{branch}_branch_field_present", bool(header["branch"]), header["branch"])

    if "B" in headers and "C" in headers:
        b, c = headers["B"], headers["C"]
        check("cross_branch_sample_ids", b["sample_ids"] == c["sample_ids"],
              {"n": len(b["sample_ids"]), "n_c": len(c["sample_ids"])})
        check("cross_branch_labels", np.array_equal(b["gt"], c["gt"]), {"label_set": sorted(set(b["gt"].tolist()))})
        masks_ok = b["masks_shape"] == [b["n_query"], 448, 448]
        if b["masks_unique"] is not None:
            masks_ok = masks_ok and b["masks_unique"] == [0, 1]
        check("canonical_masks", masks_ok, {"shape": b["masks_shape"], "values": b["masks_unique"]})
        record["n_images"] = b["n_query"]
        record["n_references_canonical"] = b["n_ref"]
    return record


def audit_stage(out: Path) -> dict:
    """Identity, nesting, manifest-hash and prior-access audit; writes the gate."""

    manifest = read_json(MANIFEST)
    support = manifest["categories"]
    units = [audit_unit(seed, shot, category)
             for seed in SEEDS for shot in SHOTS for category in CATEGORIES]

    nesting = {}
    for seed in SEEDS:
        for category in CATEGORIES:
            with np.load(branch_file("B", seed, CANONICAL_SHOT, category), allow_pickle=False) as z:
                ref4 = np.asarray(z["ref_patch_features"], dtype=np.float32)
                ids4 = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
            row = {"manifest_nested": True}
            for shot in SHOTS:
                with np.load(branch_file("B", seed, shot, category), allow_pickle=False) as z:
                    refk = np.asarray(z["ref_patch_features"], dtype=np.float32)
                    idsk = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                entry = {"n_ref": int(refk.shape[0]), "expected_n_ref": shot}
                if shot != CANONICAL_SHOT:
                    entry["ref_prefix_max_abs_diff"] = float(np.max(np.abs(refk - ref4[:shot])))
                    a = refk.reshape(shot, -1)
                    b = ref4[:shot].reshape(shot, -1)
                    entry["ref_prefix_cosine_min"] = float(np.min(
                        np.einsum("ij,ij->i", a, b)
                        / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-12)))
                entry["sample_ids_match_canonical"] = bool(idsk == ids4)
                row[f"k{shot}"] = entry
            listed = {int(k): v for k, v in support[category][str(seed)].items()}
            row["manifest_support_counts"] = {f"k{k}": len(v) for k, v in sorted(listed.items())}
            row["manifest_k2_is_prefix_of_k4"] = bool(listed[2] == listed[4][:2])
            row["manifest_selected_is_subset_of_k4"] = bool(set(listed[2]) <= set(listed[4]))
            nesting[f"s{seed}/{category}"] = row

    # Hash evidence for every support image actually named by the manifest.
    hashes = {}
    for rel, digest in manifest["selected_file_sha256"].items():
        path = Path(manifest["root"]) / rel
        ag = {"path": rel, "manifest_sha256": digest, "exists": path.exists()}
        if path.exists():
            ag["disk_sha256"] = sha(path)
            ag["matches"] = bool(ag["disk_sha256"] == digest)
        hashes[rel] = ag
    hash_failures = [k for k, v in hashes.items() if not v.get("matches", False)]

    prior = read_json(PRIOR_ACCESS) if PRIOR_ACCESS.exists() else None
    prior_access = {
        "path": str(PRIOR_ACCESS) if PRIOR_ACCESS.exists() else None,
        "exists": PRIOR_ACCESS.exists(),
        "role": None if prior is None else prior.get("role"),
        "note": None if prior is None else prior.get("note"),
        "seeds": None if prior is None else prior.get("seeds"),
        "categories": None if prior is None else prior.get("categories"),
        "interpretation": ("BTAD was already evaluated by an earlier frozen pipeline (v3_3 weighted "
                           "ensemble with per-category z-score calibration). This stage is therefore a "
                           "known-dataset frozen re-check, not a first-time unseen-data validation."),
    }

    checks = {
        "all_units_present": all(all(v["pass"] for v in u["checks"].values()) for u in units),
        "units_audited": len(units),
        "expected_units": len(SEEDS) * len(SHOTS) * len(CATEGORIES),
        "support_image_hashes_match": not hash_failures,
        "support_images_hashed": len(hashes),
        "manifest_k2_prefix_of_k4": all(v["manifest_k2_is_prefix_of_k4"] for v in nesting.values()),
        "stored_k2_reference_matches_k4_prefix": all(
            v.get(f"k{shot}", {}).get("ref_prefix_cosine_min", 1.0) >= STORED_K2_COSINE_MIN
            for v in nesting.values() for shot in SHOTS),
        "stored_k2_reference_cosine_min": min(
            (v.get(f"k{shot}", {}).get("ref_prefix_cosine_min", 1.0)
             for v in nesting.values() for shot in SHOTS), default=1.0),
    }
    audit = {
        "dataset": DATASET,
        "dataset_role_from_protocol": "holdout",
        "protocol_evidence": {
            "yaml": str(PROTOCOL_YAML.relative_to(ROOT)).replace("\\", "/"),
            "declaration": "holdout: dataset btad, purpose one_time_validation_after_freeze, "
                           "labels_visible_before_freeze: false",
            "development_guard": str(DEVELOPMENT_GUARD.relative_to(ROOT)).replace("\\", "/") + (
                " registers MPDD as development and exposes btad through the frozen-validation guard; "
                "parameter development on BTAD is refused by that guard"),
        },
        "units": units, "nesting": nesting,
        "excluded_categories": EXCLUDED_CATEGORIES,
        "support_image_hashes": hashes,
        "support_hash_failures": hash_failures,
        "prior_access": prior_access,
        "limitations": [
            "the audit proves count/manifest/hash consistency; it cannot re-prove the per-row image "
            "identity inside ref_patch_features from stored features alone",
            "the npz files do not store the reference relative paths or per-image hashes, so reference "
            "identity is provenance-level (manifest + export_report + counts), matching the level the "
            "MPDD audit reached",
            "no DINO-S cache exists for BTAD; the three-branch mechanism is out of scope here",
            f"BTAD category 03 is excluded before any scoring: {EXCLUDED_CATEGORIES['03']}",
            "the stored K2 reference rows are not bit-identical to the K4 prefix (separate export runs, "
            f"cosine min {checks['stored_k2_reference_cosine_min']:.8f}); the run itself uses the "
            "canonical K4 prefix, exactly like the frozen MPDD protocol",
        ],
        "checks": checks,
    }
    audit["all_pass"] = bool(checks["all_units_present"]
                             and checks["units_audited"] == checks["expected_units"]
                             and checks["support_image_hashes_match"]
                             and checks["manifest_k2_prefix_of_k4"]
                             and checks["stored_k2_reference_matches_k4_prefix"])
    dump(out / "audit/BTAD_CACHE_AUDIT.json", audit)
    dump(out / "audit/R3_IDENTITY_GATE.json",
         {"all_pass": audit["all_pass"], "checks": checks, "finished_utc": now(),
          "source": "audit/BTAD_CACHE_AUDIT.json"})
    print(json.dumps({"audit_all_pass": audit["all_pass"], **checks}, ensure_ascii=False), flush=True)
    return audit


# --------------------------------------------------------------------------- units


def load_btad_inputs(seed: int, shot: int, category: str) -> dict:
    """Canonical K4 sources truncated to ``shot`` references, as in the pilot."""

    q, r, paths = {}, {}, {}
    masks = labels = ids = None
    for branch in ("B", "C"):
        path = branch_file(branch, seed, CANONICAL_SHOT, category)
        q_b, r_b, masks_b, labels_b, ids_b = engine._load_branch(path, branch)
        q[branch] = q_b
        r[branch] = np.ascontiguousarray(r_b[: shot * 1024])
        paths[branch] = str(path)
        if branch == "B":
            masks, labels, ids = masks_b, labels_b, ids_b
        elif list(ids_b) != list(ids):
            raise RuntimeError(f"{path}: C sample_ids are not aligned with B")
    n = ids.size
    for branch, rows in q.items():
        if rows.shape[0] != n * 1024:
            raise RuntimeError(f"{branch}: query rows {rows.shape[0]} do not match n={n}")
    if masks.shape != (n, 448, 448):
        raise RuntimeError(f"canonical masks {masks.shape} do not match n={n}")
    return {"q": q, "r": r, "masks": np.ascontiguousarray(masks, dtype=np.uint8),
            "labels": np.ascontiguousarray(labels, dtype=np.int32),
            "sample_ids": np.asarray(ids, dtype=str), "grid": (32, 32), "n": int(n),
            "paths": paths, "dataset": DATASET, "seed": seed, "shot": shot,
            "branches": ("B", "C")}


def run_unit(out_root: Path, seed: int, shot: int, category: str, device: str, chunk: int) -> dict:
    import torch

    sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
    import common as C

    torch.set_num_threads(4)
    C.faiss.omp_set_num_threads(4)
    out = out_root / "units" / f"s{seed}_k{shot}" / category
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    dump(out / "progress.json", {"state": "loading", "updated_utc": now()})

    inp = load_btad_inputs(seed, shot, category)
    inp["q"]["Bcopy"] = inp["q"]["B"]
    inp["r"]["Bcopy"] = inp["r"]["B"]
    load_s = time.monotonic() - start

    configs, perm_arrays = rs.build_configs(shot)
    np.savez_compressed(out / "reference_permutations.npz", **perm_arrays)
    dump(out / "configurations.json",
         [{"name": c["name"], "distance_weights": c["weights"],
           "permutation_hashes": {b: hashlib.sha256(v.tobytes()).hexdigest()
                                  for b, v in c["permutations"].items()}} for c in configs])
    score_start = time.monotonic()
    scored, engine_info = engine.score(inp, configs, device=device, chunk=chunk)
    score_s = time.monotonic() - score_start

    checks: dict = {}

    def check(name: str, error: float, tol: float = TOL) -> None:
        checks[name] = {"max_abs_error": float(error), "tolerance": tol, "pass": bool(float(error) <= tol)}

    check("duplicate_matches_weighted_pair",
          float(np.max(np.abs(scored["DUP_J"] - scored["DUP_EXPECTED_J"]))))
    check("balanced_duplicate_matches_A1",
          float(np.max(np.abs(scored["DUP_BAL_J"] - scored["A1_J"]))))
    check("common_permutation_A1_J",
          float(np.max(np.abs(scored["A1_J"] - scored["INV_COMMON_A1_J"]))))

    count = min(2048, len(inp["q"]["B"]))
    parity_index = np.linspace(0, len(inp["q"]["B"]) - 1, count, dtype=np.int64)
    q_cat = C.unit_rows(np.concatenate([inp["q"]["B"][parity_index] / np.sqrt(2),
                                        inp["q"]["C"][parity_index] / np.sqrt(2)], axis=1))
    r_cat = C.unit_rows(np.concatenate([inp["r"]["B"] / np.sqrt(2),
                                        inp["r"]["C"] / np.sqrt(2)], axis=1))
    legacy = C.knn_dist(q_cat, r_cat)[:, 0]
    check("legacy_A1_faiss_real_patch_parity",
          float(np.max(np.abs(legacy - scored["A1_J"].reshape(-1)[parity_index]))))
    del q_cat, r_cat, legacy

    scored["A1_L"] = (.5 * scored["B"] + .5 * scored["C"]).astype(np.float32)
    scored["DUP_L"] = (np.float32(2.0 / 3.0) * scored["B"] + np.float32(1.0 / 3.0) * scored["C"]).astype(np.float32)
    scored["DUP_BAL_L"] = (.25 * scored["B"] + .25 * scored["B"] + .5 * scored["C"]).astype(np.float32)
    g = (scored["A1_J"] - scored["A1_L"]).astype(np.float32)
    scored["A1_G"] = g
    check("A1_nonnegative_G", max(0.0, -float(g.min())))
    check("balanced_duplicate_L_matches_A1_L",
          float(np.max(np.abs(scored["DUP_BAL_L"] - scored["A1_L"]))))
    for lam in (.25, .5, .75):
        scored[f"A1_lambda_{lam:.2f}"] = (scored["A1_L"] + np.float32(lam) * g).astype(np.float32)

    masks, labels = inp["masks"], inp["labels"]
    ids = [str(x) for x in inp["sample_ids"]]
    paths = {k: str(v) for k, v in inp["paths"].items()}
    del inp
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    saved = {k: v for k, v in scored.items() if not k.startswith("INV_")}
    np.savez_compressed(out / "patch_scores.npz", **saved, sample_ids=np.asarray(ids))
    dump(out / "progress.json", {"state": "metrics", "updated_utc": now(), "score_s": score_s})

    metric_start = time.monotonic()
    result = rs.evaluate_methods(saved, masks, labels, ids, out, include_aupro=True)
    timing = {"load_s": load_s, "score_s": score_s, "metric_s": time.monotonic() - metric_start,
              "total_s": time.monotonic() - start}
    inv = {"all_pass": all(v["pass"] for v in checks.values()), "checks": checks,
           "engine": engine_info, "cut": "no stride-8 historical AP baseline exists for BTAD in this "
                                         "repository; the independent legacy FAISS parity is used instead"}
    dump(out / "invariants.json", inv)
    if not inv["all_pass"]:
        raise RuntimeError(f"BTAD invariant failure in {category} K{shot} seed{seed}; no interpretation permitted")
    dump(out / "DONE.json", {"status": "completed", "scientific_status": "exploratory_only",
                             "finished_utc": now(), "category": category, "shot": shot, "seed": seed,
                             "dataset": DATASET, "dataset_role": "holdout_frozen_recheck",
                             "n_images": len(ids), "configurations": len(configs),
                             "canonical_source_shot": CANONICAL_SHOT, "selected_reference_images": shot,
                             "timing": timing, "inputs": paths, "engine": engine_info,
                             "invariants_pass": True, "detector_methods": result["detector_methods"]})
    dump(out / "progress.json", {"state": "completed", "updated_utc": now(), "timing": timing})
    print(f"[R3] DONE {DATASET} s{seed} {category} K{shot}: {timing}", flush=True)
    return {"status": "completed", "n_images": len(ids), "timing": timing, "checks": checks}


# --------------------------------------------------------------------------- analyze


def contrast_rows(results: dict, point: dict, seed: int) -> list[dict]:
    rows: list[dict] = []
    for shot, bootstrap in results.items():
        arrays = bootstrap["arrays"]
        for metric in cs.METRIC_KEYS:
            for label, left, right, group in CONTRASTS:
                if left not in arrays or right not in arrays:
                    continue
                stats = cs._ci(arrays[left][metric] - arrays[right][metric])
                stats.update({"reference_seed": seed, "shot": shot, "dataset": DATASET,
                              "contrast": label, "contrast_group": group, "metric": metric,
                              "method": left, "reference": right,
                              "point_delta": point[shot][left][metric] - point[shot][right][metric],
                              "multiple_comparison_adjusted": False})
                rows.append(stats)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("audit", "units", "analyze"), required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--replicates", type=int, default=REPLICATES_DEFAULT)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    parser.add_argument("--shots", nargs="+", type=int, default=list(SHOTS))
    parser.add_argument("--categories", nargs="+", default=CATEGORIES)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    if args.stage == "audit":
        audit = audit_stage(out)
        return 0 if audit["all_pass"] else 1

    gate_path = out / "audit/R3_IDENTITY_GATE.json"
    gate = read_json(gate_path) if gate_path.exists() else None
    if not gate or not gate.get("all_pass"):
        raise SystemExit("R3 identity gate is missing or failed; refusing to score or analyze BTAD")

    if args.stage == "units":
        dump(out / "PROTOCOL.json", {
            "stage": "R3_external", "dataset": DATASET, "dataset_role": "holdout",
            "label": ("known-dataset frozen re-check: BTAD has already been evaluated by the earlier "
                      "frozen v3_3 holdout pipeline, so this is not a first-time unseen-data validation"),
            "seeds": args.seeds, "shots": args.shots, "categories": args.categories,
            "excluded_categories": EXCLUDED_CATEGORIES,
            "methods": DETECTORS,
            "weights": {"A1_J": {"B": .5, "C": .5}, "DUP_J": {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3},
                        "DUP_L": {"B": 2 / 3, "C": 1 / 3}, "A1_L": {"B": .5, "C": .5}},
            "cache_policy": "canonical K4 query and reference; K2 uses the first two K4 references",
            "postprocess": "448 bilinear then gaussian sigma4; image max; stride-8 evaluation",
            "metric_keys": list(cs.METRIC_KEYS), "primary_metric": "macro pixel_ap",
            "comparisons": [{"contrast": c[0], "group": c[3]} for c in CONTRASTS],
            "not_run": list(NOT_RUN),
            "resampling_unit": "image; paired across methods; 1000 replicates per K and reference seed",
            "bootstrap_seed": BOOTSTRAP_SEED, "effect_scale": EFFECT_SCALE, "replay_tolerance": rs.TOL,
            "parameter_selection_forbidden": True,
            "stop_rules": ["stop a unit when an implementation invariant fails",
                           "stop when the identity gate fails"],
            "gate": str(gate_path), "gate_sha256": sha(gate_path),
            "code_hashes": {name: sha(HERE / name) for name in
                            ("engine.py", "diagnostics.py", "complete_statistics.py",
                             "replicate_seed1_bc.py", "run_external_btad_bc.py")},
            "created_utc": now()})
        failures = []
        for seed in args.seeds:
            for shot in args.shots:
                for category in args.categories:
                    unit = out / "units" / f"s{seed}_k{shot}" / category
                    if args.resume and (unit / "DONE.json").exists():
                        print(f"[R3] skip existing s{seed} K{shot} {category}", flush=True)
                        continue
                    try:
                        run_unit(out, seed, shot, category, args.device, args.chunk)
                    except Exception as exc:  # noqa: BLE001 - recorded, never hidden
                        failures.append({"seed": seed, "shot": shot, "category": category,
                                         "error": f"{type(exc).__name__}: {exc}"})
                        dump(out / "FAILURES.json", failures)
                        raise
        dump(out / "FAILURES.json", failures)
        return 0

    # ---- analyze
    methods = DETECTORS
    results, point = {}, {}
    per_category_rows: list[dict] = []
    for seed in args.seeds:
        for shot in args.shots:
            structures = [cs.build_category(out / "units" / f"s{seed}_k{shot}" / cat, shot, methods)
                          for cat in args.categories]
            for structure in structures:
                for method in methods:
                    per_category_rows.append({"dataset": DATASET, "reference_seed": seed, "shot": shot,
                                              "category": structure.category, "method": method,
                                              "pixel_stride": diagnostics.STRIDE,
                                              **structure.point[method]})
            identity = cs.sequence_identity(out, structures, methods, BOOTSTRAP_SEED, shot)
            checkpoint = out / f"BTAD_bootstrap_s{seed}_k{shot}.npz"
            print(f"[R3] bootstrapping seed{seed} K{shot}: {len(methods)} methods x {args.replicates}",
                  flush=True)
            results[(seed, shot)] = cs.bootstrap(structures, methods, args.replicates, BOOTSTRAP_SEED,
                                                checkpoint, 25, args.resume, identity, 0.0)
            point[(seed, shot)] = cs.macro_point(structures, methods)
            print(f"[R3] seed{seed} K{shot}: {results[(seed, shot)]['replicates_used']} replicates in "
                  f"{results[(seed, shot)]['seconds']}s", flush=True)

    rows: list[dict] = []
    for (seed, shot), bootstrap in results.items():
        rows += contrast_rows({shot: bootstrap}, {shot: point[(seed, shot)]}, seed)
    cs.write_csv(out / "paired_deltas.csv",
                 ["dataset", "reference_seed", "shot", "contrast", "contrast_group", "metric", "method",
                  "reference", "point_delta", "mean_delta", "ci_low", "ci_high", "fraction_below_zero",
                  "n_replicates", "multiple_comparison_adjusted"], rows)
    cs.write_csv(out / "per_category.csv",
                 ["dataset", "reference_seed", "shot", "category", "method", "pixel_stride",
                  "pixel_auroc", "pixel_ap", "image_auroc", "image_ap"], per_category_rows)

    point_rows = []
    for (seed, shot), table in point.items():
        for method in methods:
            point_rows.append({"dataset": DATASET, "reference_seed": seed, "shot": shot, "method": method,
                               **table[method]})
    cs.write_csv(out / "point_by_condition.csv",
                 ["dataset", "reference_seed", "shot", "method", "pixel_auroc", "pixel_ap",
                  "image_auroc", "image_ap"], point_rows)

    samples = {}
    for (seed, shot), bootstrap in results.items():
        for method, metrics in bootstrap["arrays"].items():
            for key, values in metrics.items():
                samples[f"s{seed}_k{shot}__{method}__{key}"] = values
    if samples:
        np.savez_compressed(out / "bootstrap_samples.npz", **samples)

    unit_gate = {}
    for seed in args.seeds:
        for shot in args.shots:
            for category in args.categories:
                inv = read_json(out / "units" / f"s{seed}_k{shot}" / category / "invariants.json")
                unit_gate[f"s{seed}/k{shot}/{category}"] = inv["all_pass"]
    acceptance = {
        "units_completed": len(unit_gate),
        "expected_units": len(args.seeds) * len(args.shots) * len(args.categories),
        "unit_invariants_all_pass": all(unit_gate.values()),
        "replicates_used": {f"s{s}_k{k}": results[(s, k)]["replicates_used"] for s, k in sorted(results)},
        "identity_gate_all_pass": True,
        "effect_scale": EFFECT_SCALE,
    }
    acceptance["pass"] = bool(acceptance["units_completed"] == acceptance["expected_units"]
                              and acceptance["unit_invariants_all_pass"]
                              and all(v == args.replicates for v in acceptance["replicates_used"].values()))
    audit = read_json(out / "audit/BTAD_CACHE_AUDIT.json")
    verification = {"acceptance": acceptance, "unit_invariants": unit_gate,
                    "audit_all_pass": audit["all_pass"], "audit_checks": audit["checks"],
                    "excluded_categories": EXCLUDED_CATEGORIES,
                    "prior_access": audit["prior_access"], "not_run": list(NOT_RUN),
                    "limitations": audit["limitations"] + [
                        "BTAD has already been evaluated before, so these intervals describe a known "
                        "dataset; they cannot be presented as a first-time held-out result"]}
    dump(out / "verification.json", verification)
    dump(out / "RUN_SUMMARY.json", {"stage": "R3_external", "state": "completed",
                                    "finished_utc": now(), "dataset": DATASET,
                                    "dataset_role": "holdout_frozen_recheck", "acceptance": acceptance,
                                    "contrasts": [c[0] for c in CONTRASTS], "not_run": [c["contrast"] for c in NOT_RUN],
                                    "effect_scale": EFFECT_SCALE})
    dump(out / "STATUS.json", {"state": "completed", "finished_utc": now(),
                               "acceptance_pass": acceptance["pass"]})
    dump(out / "FAILURES.json", [])
    dump(out / "ARTIFACT_MANIFEST.json", cs.artifact_manifest(out))

    write_report(out, rows, point_rows, per_category_rows, verification)
    print(json.dumps({"acceptance_pass": acceptance["pass"]}, ensure_ascii=False), flush=True)
    return 0 if acceptance["pass"] else 1


def write_report(out: Path, rows: list[dict], point_rows: list[dict], per_category: list[dict],
                 verification: dict) -> None:
    def cell(value, digits=6):
        return "n/a" if value is None else f"{value:.{digits}f}"

    lines = ["# R3：BTAD 冻结复核（B/C 最小矩阵）", "",
             f"输出目录：`{out}`", f"完成时间：{now()}", "",
             "## 0. 必须先说清的两件事", "",
             "1. **这不是首次未见数据的外部验证。** 本仓库更早的冻结流程已经评估过 BTAD"
             "（`experiments/dynamic_fusion/v3_3/btad_holdout/report.json`，v3_3 加权集成 + 逐类 z-score 校准）。"
             "本阶段只能表述为「已知数据集上的冻结复核」。",
             "2. **没有 BTAD 的 DINO-S 缓存**，因此三支机制无法在此复现；只跑事前登记的 B/C 最小矩阵，"
             "表示对照记为 `not_run` 并写明原因。",
             "",
             "## 0b. 事前排除的类别", "",
             f"- BTAD `{', '.join(EXCLUDED_CATEGORIES)}`：{EXCLUDED_CATEGORIES['03']}。"
             "该排除在打分之前由只读审计定下，理由与网格证据见 `audit/BTAD_CACHE_AUDIT.json` 的 "
             "`nesting`/`units` 字段；因此本阶段的外部覆盖是 3 类中的 2 类，报告不得写成全类迁移。",
             "",
             "## 1. 身份与完整性审计", "",
             f"- 审计单元：{verification['acceptance']['units_completed']}/"
             f"{verification['acceptance']['expected_units']}；支持图像哈希核对全部匹配："
             f"{verification['audit_checks']['support_image_hashes_match']}"
             f"（{verification['audit_checks']['support_images_hashed']} 张）。",
             f"- K2 参考 = K4 参考前两张（支持集按 manifest 嵌套，存储行余弦 ≥ {verification['audit_checks']['stored_k2_reference_cosine_min']:.6f}）："
             f"{verification['audit_checks']['stored_k2_reference_matches_k4_prefix']}。",
             f"- 数据角色（协议）：BTAD = holdout；本阶段禁止任何参数选择。", "",
             "## 2. 宏点估计（已纳入类别平均）", "",
             "| reference seed | K | 方法 | 宏 P-AP | 宏 P-AUROC | 宏 I-AP |", "|---|---:|---|---:|---:|---:|"]
    for row in point_rows:
        lines.append(f"| {row['reference_seed']} | {row['shot']} | {row['method']} | "
                     f"{cell(row['pixel_ap'])} | {cell(row['pixel_auroc'])} | {cell(row['image_ap'])} |")

    lines += ["", "## 3. 事前登记的对照（宏像素 AP，图像配对 bootstrap）", "",
              "| reference seed | K | 对照 | 组 | 点差 | 95% 区间 | 区间不含零 |", "|---|---:|---|---|---:|---|---|"]
    for row in rows:
        if row["metric"] != "pixel_ap":
            continue
        excludes = bool(row["ci_low"] > 0 or row["ci_high"] < 0)
        lines.append(f"| {row['reference_seed']} | {row['shot']} | {row['contrast']} | "
                     f"{row['contrast_group']} | {cell(row['point_delta'])} | "
                     f"[{cell(row['ci_low'])}, {cell(row['ci_high'])}] | {excludes} |")

    lines += ["", "## 4. 未运行的对照", ""]
    lines += [f"- `{item['contrast']}`（{item['group']}）：{item['reason']}" for item in NOT_RUN]
    lines += ["", "## 5. 限制", ""]
    lines += [f"- {item}" for item in verification["limitations"]]
    lines += ["", "机器表：`per_category.csv`、`point_by_condition.csv`、`paired_deltas.csv`、"
                  "`bootstrap_samples.npz`；审计证据：`audit/BTAD_CACHE_AUDIT.json`。", ""]
    (out / "REPORT_CN.md").write_text("\n".join(lines), encoding="utf-8")

    steps = ["# R3 后续动作", "",
             "1. 对外部结论必须写成「冻结复核」；若要用未触碰数据集做一次性验证，需要平台上尚无缓存的新数据集。",
             "2. 若要主张三支机制迁移，需要先为候选数据集导出 DINO-S 参考缓存并重新登记协议。",
             "3. MVTec / VisA 属 retrospective 角色，同样已被先前的冻结流程评估过，不得当作未见数据。", ""]
    (out / "NEXT_STEPS_CN.md").write_text("\n".join(steps), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
