"""R0 gate: explicit identity audit of the seed-0 and seed-1 feature caches.

The stage-B1 acceptance only proved that the files existed, hashed as declared
and carried the right grid.  It did not put the *internal* metadata, the
cross-branch correspondence, the cross-seed mask/label/query identity and the
downstream DONE/FAILURES state into one explicit gate.  This module does that,
and it also covers the newly exported seed-1 DINO-S cache, so a later runner
can refuse to start on any identity conflict instead of trusting a single
``acceptance_pass`` flag.

Nothing here writes into a run directory; the report goes to the next-stage
directory.
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

import engine  # noqa: E402

ROOT = HERE.parents[1]
CATEGORIES = ["bracket_black", "bracket_brown", "bracket_white", "connector",
              "metal_plate", "tubes"]
BRANCHES = ("B", "C", "S")
SEEDS = (0, 1)
EXPECTED_META = {
    "dataset": "mpdd",
    "dataset_role": "development",
    "score_direction": "higher_is_more_anomalous",
}
EXPECTED_BRANCH_LABEL = {"B": "anomalydino_visual", "C": "anomalyclip_text", "S": "anomalydino_visual"}
EXPECTED_GRID = {"B": [32, 32], "C": [37, 37], "S": [32, 32]}
# The query features of the two seeds come from two separate export runs, so they
# are never bitwise identical.  The pilot's own identity audit already treats a
# cosine of 0.99999 as "same feature"; the same tolerance is reused here.
QUERY_COSINE_MIN = 0.99999
MANIFEST = ROOT / "data" / "splits" / "mpdd" / "manifest.json"
DATA_ROOT = ROOT / "data" / "mpdd_raw" / "MPDD"
RUN_DIRS = {
    0: ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912/main_v2",
    1: ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912/replication_seed1_bc_20260913",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                          encoding="utf-8")


def cache_path(branch: str, seed: int, shot: int, cat: str) -> Path:
    return engine.branch_dir(branch, seed, shot) / f"{cat}.npz"


def read_meta(path: Path) -> dict:
    """Read only the small metadata members; feature arrays stay compressed."""
    with np.load(path, allow_pickle=False) as z:
        out = {}
        for key in ("dataset", "dataset_role", "branch", "seed", "shot", "grid_size", "score_direction"):
            if key in z.files:
                value = np.asarray(z[key]).reshape(-1)
                out[key] = [int(v) for v in value] if np.issubdtype(value.dtype, np.integer) else [
                    str(v) for v in value]
        return out


def member_digest(path: Path, name: str) -> str | None:
    with np.load(path, allow_pickle=False) as z:
        if name not in z.files:
            return None
        arr = z[name]
        digest = hashlib.sha256()
        digest.update(f"{arr.dtype}{arr.shape}".encode("ascii"))
        digest.update(np.ascontiguousarray(arr).data)
        return digest.hexdigest()


def query_feature_agreement(path_a: Path, path_b: Path) -> dict:
    """Compare two query-feature planes numerically (they are separate export runs)."""
    with np.load(path_a, allow_pickle=False) as z:
        a = np.asarray(z["patch_features"], dtype=np.float32)
    with np.load(path_b, allow_pickle=False) as z:
        b = np.asarray(z["patch_features"], dtype=np.float32)
    if a.shape != b.shape:
        return {"shape_a": list(a.shape), "shape_b": list(b.shape), "comparable": False}
    flat_a = a.reshape(-1, a.shape[-1])
    flat_b = b.reshape(-1, b.shape[-1])
    diff = np.abs(flat_a.astype(np.float64) - flat_b.astype(np.float64))
    norm_a = flat_a / np.linalg.norm(flat_a, axis=1, keepdims=True)
    norm_b = flat_b / np.linalg.norm(flat_b, axis=1, keepdims=True)
    cosine = np.einsum("ij,ij->i", norm_a, norm_b, dtype=np.float64)
    return {"comparable": True, "bitexact": bool(np.array_equal(a, b)),
            "max_abs_diff": float(diff.max()), "mean_abs_diff": float(diff.mean()),
            "cosine_min": float(cosine.min()), "cosine_mean": float(cosine.mean())}


def check_metadata(branch: str, seed: int, cat: str, path: Path) -> dict:
    meta = read_meta(path)
    values = {}
    if "dataset" in meta:
        values["dataset"] = meta["dataset"][0]
    if "dataset_role" in meta:
        values["dataset_role"] = meta["dataset_role"][0]
    if "branch" in meta:
        values["branch"] = meta["branch"][0]
    if "score_direction" in meta:
        values["score_direction"] = meta["score_direction"][0]
    values["seed"] = meta.get("seed", [None])[0]
    values["shot"] = meta.get("shot", [None])[0]
    values["grid_size"] = meta.get("grid_size")
    passed = (values.get("dataset") == EXPECTED_META["dataset"]
              and values.get("dataset_role") == EXPECTED_META["dataset_role"]
              and values.get("branch") == EXPECTED_BRANCH_LABEL[branch]
              and values.get("score_direction") == EXPECTED_META["score_direction"]
              and values["seed"] == seed
              and values["shot"] == 4
              and values.get("grid_size") == EXPECTED_GRID[branch])
    return {"values": values, "pass": bool(passed)}


def audit(base: Path) -> dict:
    started = time.time()
    report = {
        "stage": "R0-identity-gate",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "categories": CATEGORIES,
        "branches": list(BRANCHES),
        "seeds": list(SEEDS),
        "checks": {},
        "limitations": [
            "the raw NPZ files do not embed per-row ref_ids; the reference *order* remains "
            "provenance-based (export report + manifest) and is not verified at row level",
            "reference features are only shown to differ from the other seed, which rules out an "
            "identical support draw but does not identify which image each row came from",
            "the query features of the two seeds are separate export runs; they agree to "
            f"cosine >= {QUERY_COSINE_MIN} but are not bitwise identical, so a tiny run-to-run "
            "component is present in any cross-seed difference",
            "the CLIP branch stores its masks at 518x518 by design; masks are therefore only "
            "compared between branches that declare the same grid (B and S)",
        ],
    }
    checks = report["checks"]

    # ---- 1. internal metadata, per branch/seed/category
    meta_rows = {}
    for seed in SEEDS:
        for branch in BRANCHES:
            for cat in CATEGORIES:
                path = cache_path(branch, seed, 4, cat)
                key = f"s{seed}/{branch}/{cat}"
                if not path.exists():
                    meta_rows[key] = {"pass": False, "error": "missing file", "path": str(path)}
                    continue
                meta_rows[key] = {**check_metadata(branch, seed, cat, path), "path": str(path)}
    report["branch_metadata"] = meta_rows
    checks["npz_internal_metadata"] = {
        "value": {k: v.get("values") for k, v in meta_rows.items()},
        "pass": all(v.get("pass") for v in meta_rows.values()),
    }

    # ---- 1b. the newly exported seed-1 DINO-S report must match its own files
    s_report_path = engine.branch_dir("S", 1, 4) / "export_report.json"
    s_report = read_json(s_report_path) if s_report_path.exists() else None
    s_rows = {}
    if s_report:
        declared = {row["category"]: row for row in s_report.get("categories", [])}
        for cat in CATEGORIES:
            path = cache_path("S", 1, 4, cat)
            row = {"declared": cat in declared}
            if path.exists() and cat in declared:
                row["sha256_matches"] = sha256_file(path) == declared[cat]["sha256"]
                row["references"] = declared[cat].get("references")
                row["test_samples"] = declared[cat].get("samples")
            s_rows[cat] = row
    report["seed1_S_export_report"] = {
        "path": str(s_report_path), "exists": s_report_path.exists(),
        "status": (s_report or {}).get("status"), "model": (s_report or {}).get("model"),
        "seed": (s_report or {}).get("seed"), "shot": (s_report or {}).get("shot"),
        "categories": s_rows,
    }
    checks["seed1_S_export_report"] = {
        "pass": bool(s_report and s_report.get("status") == "passed"
                     and s_report.get("model") == "dinov2_vits14"
                     and int(s_report.get("seed", -1)) == 1 and int(s_report.get("shot", -1)) == 4
                     and all(v.get("declared") and v.get("sha256_matches") for v in s_rows.values()))}

    # ---- 2. cross-branch correspondence within a seed
    # Masks are only comparable between branches that declare the same grid: B and S
    # store 448x448, while the CLIP branch stores its masks at 518x518 on purpose and
    # the frozen engine never reads them (canonical masks always come from B).
    mask_branches = [b for b in BRANCHES if EXPECTED_GRID[b] == [32, 32]]
    cross_branch = {}
    for seed in SEEDS:
        for cat in CATEGORIES:
            row = {"mask_grids": {b: EXPECTED_GRID[b] for b in BRANCHES},
                   "mask_branches_compared": mask_branches}
            digests = {}
            for name in ("sample_ids", "gt_sp", "imgs_masks"):
                digests[name] = {
                    branch: member_digest(cache_path(branch, seed, 4, cat), name) for branch in BRANCHES}
            row["sample_ids_equal"] = len({v for v in digests["sample_ids"].values() if v}) == 1
            row["gt_sp_equal"] = len({v for v in digests["gt_sp"].values() if v}) == 1
            row["imgs_masks_equal_within_same_grid"] = len(
                {digests["imgs_masks"][b] for b in mask_branches if digests["imgs_masks"][b]}) == 1
            row["digests"] = digests
            row["pass"] = bool(row["sample_ids_equal"] and row["gt_sp_equal"]
                               and row["imgs_masks_equal_within_same_grid"])
            cross_branch[f"s{seed}/{cat}"] = row
    report["cross_branch"] = cross_branch
    checks["cross_branch_ids_masks_labels"] = {
        "pass": all(v["pass"] for v in cross_branch.values())}

    # ---- 3. cross-seed identity of the query-side content
    cross_seed = {}
    for branch in BRANCHES:
        for cat in CATEGORIES:
            s0 = cache_path(branch, 0, 4, cat)
            s1 = cache_path(branch, 1, 4, cat)
            row = {"masks_equal": None, "labels_equal": None, "sample_ids_equal": None,
                   "ref_features_differ": None}
            if s0.exists() and s1.exists():
                row["query_features"] = query_feature_agreement(s0, s1)
                row["ref_features_differ"] = member_digest(s0, "ref_patch_features") != member_digest(
                    s1, "ref_patch_features")
                row["sample_ids_equal"] = member_digest(s0, "sample_ids") == member_digest(s1, "sample_ids")
                if "imgs_masks" in np.load(s0, allow_pickle=False).files:
                    row["masks_equal"] = member_digest(s0, "imgs_masks") == member_digest(s1, "imgs_masks")
                    row["labels_equal"] = member_digest(s0, "gt_sp") == member_digest(s1, "gt_sp")
            row["pass"] = bool(row.get("query_features", {}).get("cosine_min", 0.0) >= QUERY_COSINE_MIN
                               and row["ref_features_differ"] and row["sample_ids_equal"]
                               and row["masks_equal"] and row["labels_equal"])
            cross_seed[f"{branch}/{cat}"] = row
    report["cross_seed"] = cross_seed
    checks["cross_seed_query_and_test_content"] = {
        "query_cosine_min_required": QUERY_COSINE_MIN,
        "pass": all(v["pass"] for v in cross_seed.values())}

    # ---- 4. support-image hashes on disk (both seeds)
    manifest = read_json(MANIFEST)
    support = {}
    missing = []
    for seed in SEEDS:
        for cat in CATEGORIES:
            entries = []
            for relative in manifest["categories"][cat][str(seed)]["4"]:
                path = DATA_ROOT / relative
                entry = {"path": relative, "exists": path.exists()}
                if path.exists():
                    entry["size"] = path.stat().st_size
                    entry["sha256"] = sha256_file(path)
                else:
                    missing.append(f"s{seed}/{relative}")
                entries.append(entry)
            support[f"s{seed}/{cat}"] = entries
    report["support_image_hashes"] = support
    report["support_overlap"] = {
        cat: sorted(set(manifest["categories"][cat]["0"]["4"]) & set(manifest["categories"][cat]["1"]["4"]))
        for cat in CATEGORIES}
    checks["support_images_present_and_hashed"] = {"missing": missing, "pass": not missing}
    checks["seed_support_disjoint"] = {
        "value": report["support_overlap"],
        "pass": all(not v for v in report["support_overlap"].values())}

    # ---- 5. downstream run gate: DONE + FAILURES for both seeds
    run_gate = {}
    for seed, run_dir in RUN_DIRS.items():
        prefix = f"s{seed}_k"
        failures_path = run_dir / "FAILURES.json"
        failures = read_json(failures_path) if failures_path.exists() else None
        done_rows = {}
        for shot in (2, 4):
            for cat in CATEGORIES:
                done = run_dir / "units" / f"{prefix}{shot}" / cat / "DONE.json"
                if not done.exists():
                    done_rows[f"k{shot}/{cat}"] = {"pass": False, "error": "missing DONE.json"}
                    continue
                payload = read_json(done)
                done_rows[f"k{shot}/{cat}"] = {
                    "status": payload.get("status"),
                    "seed": payload.get("seed"),
                    "shot": payload.get("shot"),
                    "invariants_pass": payload.get("invariants_pass"),
                    "canonical_source_shot": payload.get("canonical_source_shot"),
                    "selected_reference_images": payload.get("selected_reference_images"),
                    "pass": bool(payload.get("status") == "completed"
                                 and int(payload.get("seed", -1)) == seed
                                 and int(payload.get("shot", -1)) == shot
                                 and payload.get("invariants_pass") is True
                                 and int(payload.get("canonical_source_shot", -1)) == 4
                                 and int(payload.get("selected_reference_images", -1)) == shot),
                }
        run_gate[f"s{seed}"] = {"run_dir": str(run_dir), "failures": failures,
                                "failures_empty": failures == [],
                                "units": done_rows}
    report["run_gate"] = run_gate
    checks["downstream_runs_complete"] = {
        "pass": all(v["failures_empty"] and all(u.get("pass") for u in v["units"].values())
                    for v in run_gate.values())}

    report["all_pass"] = all(v.get("pass", False) for v in checks.values())
    report["seconds"] = round(time.time() - started, 1)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.output)
    write_json(args.output / "AUDIT_IDENTITY_GATE.json", report)
    failed = [k for k, v in report["checks"].items() if not v.get("pass")]
    print(json.dumps({"all_pass": report["all_pass"], "failed_checks": failed,
                      "seconds": report["seconds"]}, ensure_ascii=False), flush=True)
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
