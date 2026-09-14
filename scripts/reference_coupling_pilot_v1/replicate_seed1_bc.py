"""Stage B0/B1: audit the seed-1 B/C caches and replicate the frozen checks on them.

B0 (``--audit-only``) reads only metadata: the two seed-1 export reports, the
MPDD split manifest, and the NPZ headers.  It answers whether the caches may be
used at all, records the seed-0/seed-1 support overlap, and keeps the
provenance limitation that the raw NPZ files carry no per-row ``ref_ids``.

B1 scores the pre-declared fixed matrix on reference seed 1 with the *frozen*
loader/scorer and the frozen post-processing, then repeats the image-level
paired bootstrap from ``complete_statistics``:

    B, C, A1_J, DUP_J, DUP_BAL_J, DUP_EXPECTED_J, A1_L, and the three
    intermediate ``S_lambda`` points of A1.

Only branches B and C exist for seed 1 (there is no seed-1 DINO-S cache), so
this stage can never be reported as a three-branch replication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import complete_statistics as cs  # noqa: E402
import diagnostics  # noqa: E402
import engine  # noqa: E402

ROOT = HERE.parents[1]
CATEGORIES = list(cs.CATEGORIES)
SHOTS = (2, 4)
SEED = 1
TOL = 1e-6

B1_METHODS = ["B", "C", "A1_J", "DUP_J", "DUP_BAL_J", "DUP_EXPECTED_J", "A1_L",
              "A1_lambda_0.25", "A1_lambda_0.50", "A1_lambda_0.75"]
REFERENCE = "A1_J"

CACHE_ROOT = ROOT / "outputs" / "dynamic_fusion" / "v3_direction_a"
MANIFEST = ROOT / "data" / "splits" / "mpdd" / "manifest.json"
HISTORICAL = ROOT / "experiments/dynamic_fusion/validation_handoff_20260911/E2/metrics_per_category.csv"

B1_CONTRASTS = [
    ("B", REFERENCE, "single_branch_vs_A1_J"),
    ("C", REFERENCE, "single_branch_vs_A1_J"),
    ("DUP_J", REFERENCE, "weight_control"),
    ("DUP_BAL_J", REFERENCE, "weight_control_equivalence"),
    ("DUP_EXPECTED_J", REFERENCE, "weight_control_equivalence"),
    ("A1_L", REFERENCE, "relaxation"),
    ("A1_lambda_0.25", REFERENCE, "relaxation_ladder"),
    ("A1_lambda_0.50", REFERENCE, "relaxation_ladder"),
    ("A1_lambda_0.75", REFERENCE, "relaxation_ladder"),
    ("A1_lambda_0.25", "A1_L", "relaxation_vs_L"),
    ("A1_lambda_0.50", "A1_L", "relaxation_vs_L"),
    ("A1_lambda_0.75", "A1_L", "relaxation_vs_L"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                          encoding="utf-8")


def dump(path: Path, payload) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def branch_file(branch: str, shot: int, cat: str) -> Path:
    if branch == "B":
        return CACHE_ROOT / f"features_vitb14_s{SEED}_k{shot}" / "anomalydino_visual" / f"{cat}.npz"
    if branch == "C":
        return CACHE_ROOT / f"features_s{SEED}_k{shot}" / "anomalyclip_text" / f"{cat}.npz"
    raise ValueError(branch)


def report_path(branch: str) -> Path:
    if branch == "B":
        return CACHE_ROOT / f"features_vitb14_s{SEED}_k4" / "anomalydino_visual" / "export_report.json"
    if branch == "C":
        return CACHE_ROOT / f"features_s{SEED}_k4" / "anomalyclip_text" / "export_report.json"
    raise ValueError(branch)


# --------------------------------------------------------------------------- B0 audit


def npz_header(path: Path, member: str) -> tuple[tuple, object]:
    """Read one member's shape/dtype from the zip header without decompressing."""
    import zipfile
    from numpy.lib import format as npformat

    with zipfile.ZipFile(path) as zf:
        with zf.open(f"{member}.npy") as fh:
            version = npformat.read_magic(fh)
            if version == (1, 0):
                shape, _fortran, dtype = npformat.read_array_header_1_0(fh)
            elif version == (2, 0):
                shape, _fortran, dtype = npformat.read_array_header_2_0(fh)
            elif version == (3, 0):
                shape, _fortran, dtype = npformat.read_array_header_3_0(fh)
            else:  # pragma: no cover - numpy does not emit other versions
                raise ValueError(f"unsupported npy version {version}")
    return tuple(int(v) for v in shape), dtype


def audit_seed1(manifest_path: Path = MANIFEST) -> dict:
    """Metadata-only audit of the seed-1 B/C caches. Never loads full features."""
    report = {"stage": "B0", "seed": SEED, "created_utc": now(), "checks": {}, "limitations": []}
    manifest = read_json(manifest_path)
    report["manifest_path"] = str(manifest_path)
    report["manifest_sha256"] = sha256(manifest_path)

    checks = report["checks"]
    report_hashes = {}
    for branch in ("B", "C"):
        rp = report_path(branch)
        payload = read_json(rp)
        report_hashes[branch] = payload
        checks[f"report_{branch}_status"] = {"value": payload.get("status"),
                                            "pass": payload.get("status") == "passed"}
        checks[f"report_{branch}_seed_shot"] = {
            "value": [payload.get("seed"), payload.get("shot")],
            "pass": int(payload.get("seed")) == SEED and int(payload.get("shot")) == 4}
        checks[f"report_{branch}_manifest_hash"] = {
            "value": payload.get("manifest_sha256"),
            "pass": payload.get("manifest_sha256") == report["manifest_sha256"]}
        cats = [c["category"] for c in payload.get("categories", [])]
        checks[f"report_{branch}_categories"] = {
            "value": cats, "pass": sorted(cats) == sorted(CATEGORIES)}
        checks[f"report_{branch}_no_test_fit"] = {
            "pass": not any(payload.get(k) for k in
                            ("test_predictions_used_for_parameter_fit",
                             "test_labels_used_for_parameter_fit",
                             "test_set_statistics_used_for_calibration"))}

    # Manifest: seed-0 vs seed-1 support identity and overlap.
    per_category = {}
    for cat in CATEGORIES:
        node = manifest["categories"][cat]
        s0 = list(node["0"]["4"])
        s1 = list(node["1"]["4"])
        s0_k2 = list(node["0"]["2"])
        s1_k2 = list(node["1"]["2"])
        overlap = sorted(set(s0) & set(s1))
        per_category[cat] = {
            "seed0_k4": s0, "seed1_k4": s1,
            "seed0_k2": s0_k2, "seed1_k2": s1_k2,
            "overlap_k4": overlap,
            "seed1_k2_is_prefix_of_seed1_k4": s1_k2 == s1[:2],
            "identical_support": s0 == s1,
        }
    report["support_identity"] = per_category
    checks["seed1_k2_is_prefix_of_seed1_k4"] = {
        "value": {c: v["seed1_k2_is_prefix_of_seed1_k4"] for c, v in per_category.items()},
        "pass": all(v["seed1_k2_is_prefix_of_seed1_k4"] for v in per_category.values())}
    report["support_overlap_total"] = int(sum(len(v["overlap_k4"]) for v in per_category.values()))
    report["categories_with_identical_support"] = [
        c for c, v in per_category.items() if v["identical_support"]]

    # NPZ headers and file hashes.
    file_meta = {}
    for branch in ("B", "C"):
        declared = {c["category"]: c for c in report_hashes[branch]["categories"]}
        for cat in CATEGORIES:
            path = branch_file(branch, 4, cat)
            entry = {"path": str(path), "exists": path.exists()}
            if path.exists():
                entry["size"] = path.stat().st_size
                entry["sha256"] = sha256(path)
                entry["sha256_matches_report"] = entry["sha256"] == declared[cat]["sha256"]
                with zipfile.ZipFile(path) as zf:
                    members = sorted(name[:-4] for name in zf.namelist() if name.endswith(".npy"))
                entry["keys"] = members
                with np.load(path, allow_pickle=False) as z:
                    entry["grid_size"] = [int(v) for v in np.asarray(z["grid_size"]).reshape(-1)]
                    ids = [str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)]
                ref_shape, _ = npz_header(path, "ref_patch_features")
                query_shape, _ = npz_header(path, "patch_features")
                entry["ref_shape"] = list(ref_shape)
                entry["query_shape"] = list(query_shape)
                entry["n_references"] = ref_shape[0]
                entry["n_query_images"] = query_shape[0]
                if branch == "B":
                    entry["masks_shape"] = list(npz_header(path, "imgs_masks")[0])
                    entry["labels_shape"] = list(npz_header(path, "gt_sp")[0])
                entry["n_query_ids"] = len(ids)
                entry["sample_ids_sha256"] = hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
            file_meta[f"{branch}/{cat}"] = entry
    report["files"] = file_meta

    checks["npz_sha256_matches_report"] = {
        "value": {k: v.get("sha256_matches_report") for k, v in file_meta.items()},
        "pass": all(v.get("sha256_matches_report") for v in file_meta.values())}
    expected_grid = {k: ([32, 32] if k.startswith("B/") else [37, 37]) for k in file_meta}
    checks["grid_sizes_expected"] = {
        "value": {k: v.get("grid_size") for k, v in file_meta.items()},
        "pass": all(v.get("grid_size") == expected_grid[k] for k, v in file_meta.items())}
    checks["patch_grid_matches_declared"] = {
        "value": {k: [v.get("ref_shape", [None])[1:3], v.get("query_shape", [None])[1:3]]
                  for k, v in file_meta.items()},
        "pass": all(v.get("ref_shape", [0, None, None])[1:3] == expected_grid[k]
                    and v.get("query_shape", [0, None, None])[1:3] == expected_grid[k]
                    for k, v in file_meta.items())}
    checks["k4_reference_images"] = {
        "value": {k: v.get("n_references") for k, v in file_meta.items()},
        "pass": all(v.get("n_references") == 4 for v in file_meta.values())}
    checks["query_ids_match_query_rows"] = {
        "value": {k: v.get("n_query_ids") == v.get("n_query_images") for k, v in file_meta.items()},
        "pass": all(v.get("n_query_ids") == v.get("n_query_images") for v in file_meta.values())}
    checks["B_masks_448"] = {
        "value": {k: v.get("masks_shape") for k, v in file_meta.items() if k.startswith("B/")},
        "pass": all(v.get("masks_shape") == [v.get("n_query_images"), 448, 448]
                    for k, v in file_meta.items() if k.startswith("B/"))}
    checks["B_labels_length"] = {
        "value": {k: v.get("labels_shape") for k, v in file_meta.items() if k.startswith("B/")},
        "pass": all(int(np.prod(v.get("labels_shape") or [0])) == v.get("n_query_images")
                    for k, v in file_meta.items() if k.startswith("B/"))}
    checks["B_has_masks_and_labels"] = {
        "pass": all(("imgs_masks" in v.get("keys", []) and "gt_sp" in v.get("keys", []))
                    for k, v in file_meta.items() if k.startswith("B/"))}

    # Query identity must agree between the two branches and with seed 0.
    seed0_ids = {}
    for cat in CATEGORIES:
        path = CACHE_ROOT / "features_vitb14_s0_k4" / "anomalydino_visual" / f"{cat}.npz"
        with np.load(path, allow_pickle=False) as z:
            seed0_ids[cat] = hashlib.sha256(
                "\n".join(str(x) for x in np.asarray(z["sample_ids"]).reshape(-1)).encode("utf-8")
            ).hexdigest()
    checks["query_ids_match_seed0"] = {
        "value": {c: file_meta[f"B/{c}"].get("sample_ids_sha256") == seed0_ids[c] for c in CATEGORIES},
        "pass": all(file_meta[f"B/{c}"].get("sample_ids_sha256") == seed0_ids[c] for c in CATEGORIES)}
    checks["query_ids_match_between_branches"] = {
        "value": {c: file_meta[f"B/{c}"].get("sample_ids_sha256") == file_meta[f"C/{c}"].get("sample_ids_sha256")
                  for c in CATEGORIES},
        "pass": all(file_meta[f"B/{c}"].get("sample_ids_sha256")
                    == file_meta[f"C/{c}"].get("sample_ids_sha256") for c in CATEGORIES)}

    report["limitations"] = [
        "the raw NPZ files do not embed per-row ref_ids: support identity is provenance-based "
        "(export report + manifest) and numerically unverified at the row level",
        "seed-1 references differ from seed-0 references, so this is a new support draw, not a "
        "re-measurement of the same references",
        "there is no seed-1 DINO-S cache, so no three-branch (TRI/BAL) replication is possible here",
        "no historical seed-1 A1 baseline exists in the validation-handoff metrics, so the frozen "
        "historical-AP replay check cannot be applied to seed 1",
    ]
    report["all_pass"] = all(v.get("pass", False) for v in checks.values())
    return report


# --------------------------------------------------------------------------- scoring


def build_configs(shot: int) -> tuple[list[dict], dict]:
    rows = shot * 1024
    common = np.random.default_rng(20260912).permutation(rows)
    original = {
        "B": {"B": 1.0},
        "C": {"C": 1.0},
        "A1_J": {"B": .5, "C": .5},
        "DUP_J": {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3},
        "DUP_BAL_J": {"B": .25, "Bcopy": .25, "C": .5},
        "DUP_EXPECTED_J": {"B": 2 / 3, "C": 1 / 3},
    }
    configs = [{"name": k, "weights": v, "permutations": {}} for k, v in original.items()]
    configs.append({"name": "INV_COMMON_A1_J", "weights": original["A1_J"],
                    "permutations": {"B": common, "C": common}})
    return configs, {"common": common}


def evaluate_methods(scores: dict, masks: np.ndarray, labels: np.ndarray, ids: list[str],
                     out_dir: Path, include_aupro: bool = True) -> dict:
    """Same frozen post-processing as diagnostics.evaluate_case, without the
    TRI/BAL-only region and flip products that need a third branch."""
    common = diagnostics._load_common()
    detector_names = [name for name in scores if not diagnostics._is_diagnostic_name(name)]
    if not detector_names:
        raise ValueError("no detector arrays after diagnostic filtering")
    n = len(ids)
    stride = diagnostics.STRIDE
    patch_map = diagnostics.PATCH_MAP_SIZE
    mask_s = np.ascontiguousarray(masks[:, ::stride, ::stride], dtype=np.uint8)
    pixel_scores = np.empty((len(detector_names), n, *patch_map), dtype=np.float32)
    image_scores = np.empty((len(detector_names), n), dtype=np.float32)
    metric_rows: list[dict] = []
    per_image_rows: list[dict] = []
    for index, method in enumerate(detector_names):
        print(f"[seed1] scoring metrics {index + 1}/{len(detector_names)}: {method}", flush=True)
        tmp_path = out_dir / f".seed1_{index:03d}.maps448.f32"
        maps448 = np.memmap(tmp_path, dtype=np.float32, mode="w+", shape=(n, *diagnostics.MAP_SIZE))
        per_image_pap: list = []
        try:
            for image_index in range(n):
                one_map = common.dists_to_maps(scores[method][image_index].reshape(1, -1), 1,
                                               diagnostics.GRID, diagnostics.MAP_SIZE)[0]
                maps448[image_index] = one_map
                compact = np.asarray(one_map[::stride, ::stride], dtype=np.float32)
                pixel_scores[index, image_index] = compact
                image_scores[index, image_index] = float(np.max(one_map))
                per_image_pap.append(diagnostics._per_image_pixel_ap(compact, mask_s[image_index]))
            maps448.flush()
            metrics = diagnostics._safe_pixel_metrics(common, maps448, masks, include_aupro)
        finally:
            del maps448
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass
        metrics.update(diagnostics._safe_image_metrics(common, image_scores[index], labels))
        metric_rows.append({"method": method, **metrics})
        for image_index, sample_id in enumerate(ids):
            per_image_rows.append({
                "method": method, "image_index": image_index, "sample_id": sample_id,
                "label": int(labels[image_index]),
                "image_max": float(image_scores[index, image_index]),
                "pixel_ap": per_image_pap[image_index],
            })
    np.savez_compressed(out_dir / "evaluation_scores.npz",
                        method_names=np.asarray(detector_names, dtype=np.str_),
                        pixel_scores=pixel_scores, pixel_masks=mask_s,
                        image_scores=image_scores, labels=labels,
                        sample_ids=np.asarray(ids, dtype=np.str_))
    fields = ["method", "pixel_auroc", "pixel_ap"] + (["pixel_aupro"] if include_aupro else []) \
        + ["image_auroc", "image_ap", "image_f1_max"]
    diagnostics._write_csv(out_dir / "metrics.csv", fields, metric_rows)
    diagnostics._write_csv(out_dir / "per_image.csv",
                           ["method", "image_index", "sample_id", "label", "image_max", "pixel_ap"],
                           per_image_rows)
    return {"detector_methods": detector_names,
            "metrics": {row["method"]: {k: row.get(k) for k in fields if k != "method"}
                        for row in metric_rows}}


def run_unit(output: Path, cat: str, shot: int, device: str, chunk: int) -> dict:
    import torch
    sys.path.insert(0, str(ROOT / "scripts/validation_handoff_20260911"))
    import common as C

    torch.set_num_threads(4)
    C.faiss.omp_set_num_threads(4)
    out = output / "units" / f"s1_k{shot}" / cat
    out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    dump(out / "progress.json", {"state": "loading", "updated_utc": now()})

    inp = engine.load_inputs(SEED, 4, cat, branches=("B", "C"))
    inp["r"] = {b: np.ascontiguousarray(r[: shot * 1024]) for b, r in inp["r"].items()}
    inp["q"]["Bcopy"] = inp["q"]["B"]
    inp["r"]["Bcopy"] = inp["r"]["B"]
    load_s = time.monotonic() - start

    configs, perm_arrays = build_configs(shot)
    np.savez_compressed(out / "reference_permutations.npz", **perm_arrays)
    record = [{"name": c["name"], "distance_weights": c["weights"],
               "permutation_hashes": {b: hashlib.sha256(v.tobytes()).hexdigest()
                                      for b, v in c["permutations"].items()}}
              for c in configs]
    dump(out / "configurations.json", record)
    dump(out / "progress.json", {"state": "scoring", "updated_utc": now(), "n": inp["n"],
                                 "configurations": len(configs), "load_s": load_s})
    score_start = time.monotonic()
    scored, engine_info = engine.score(inp, configs, device=device, chunk=chunk)
    score_s = time.monotonic() - score_start

    checks: dict = {}

    def check(name: str, error: float, tol: float = TOL) -> None:
        checks[name] = {"max_abs_error": float(error), "tolerance": tol,
                        "pass": bool(float(error) <= tol)}

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
    g = (scored["A1_J"] - scored["A1_L"]).astype(np.float32)
    scored["A1_G"] = g
    check("A1_nonnegative_G", max(0.0, -float(g.min())))
    for lam in (.25, .5, .75):
        scored[f"A1_lambda_{lam:.2f}"] = (scored["A1_L"] + np.float32(lam) * g).astype(np.float32)

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
    result = evaluate_methods(saved, masks, labels, ids, out, include_aupro=True)
    timing = {"load_s": load_s, "score_s": score_s,
              "metric_s": time.monotonic() - metric_start, "total_s": time.monotonic() - start}
    inv = {
        "all_pass": all(v["pass"] for v in checks.values()),
        "checks": checks,
        "historical_baseline": {
            "status": "no_seed1_historical_baseline",
            "searched": str(HISTORICAL),
            "note": ("the validation-handoff metrics only contain reference seed 0, so the frozen "
                     "historical-AP replay is unavailable for seed 1; the independent legacy FAISS "
                     "parity check above is used instead"),
        },
    }
    dump(out / "invariants.json", inv)
    if not inv["all_pass"]:
        raise RuntimeError(f"seed1 invariant failure in {cat} K{shot}; no interpretation permitted")
    dump(out / "DONE.json", {
        "status": "completed", "scientific_status": "exploratory_only", "finished_utc": now(),
        "category": cat, "shot": shot, "seed": SEED, "n_images": len(ids),
        "configurations": len(configs), "canonical_source_shot": 4,
        "selected_reference_images": shot, "timing": timing, "inputs": paths,
        "engine": engine_info, "diagnostics": result, "invariants_pass": True,
    })
    dump(out / "progress.json", {"state": "completed", "updated_utc": now(), "timing": timing})
    print(f"[seed1] DONE {cat} K{shot}: {timing}", flush=True)
    return {"category": cat, "shot": shot, "timing": timing, "invariants": checks}


# --------------------------------------------------------------------------- analysis


def b1_contrasts(result: dict, point: dict) -> list[dict]:
    arrays = result["arrays"]
    shot = result["shot"]
    rows = []
    for metric in cs.METRIC_KEYS:
        for method, other, group in B1_CONTRASTS:
            delta = arrays[method][metric] - arrays[other][metric]
            stats = cs._ci(delta)
            stats.update({"shot": shot, "contrast": f"{method} - {other}",
                          "contrast_group": group, "metric": metric,
                          "method": method, "reference": other,
                          "point_delta": point[method][metric] - point[other][metric]})
            rows.append(stats)
    return rows


def render_report(payload: dict, contrast_rows: list[dict]) -> str:
    lines = ["# 阶段 B1：参考 seed1 的 B/C 复核", "",
             f"输出目录：`{payload['output_dir']}`", "",
             f"- 审计结论（B0）：`all_pass={payload['audit_all_pass']}`；"
             f"seed0/seed1 K4 支持重叠合计 {payload['support_overlap_total']} 张",
             f"- 分支：仅 B、C（**没有** seed1 的 DINO-S，故不是三分支复核）",
             f"- 方法：{B1_METHODS}", "",
             "## 每 K 完成情况", "",
             "| K | 请求复制数 | 实际复制数 | 耗时(s) |", "|---|---:|---:|---:|"]
    for key in sorted(payload["bootstrap"]):
        block = payload["bootstrap"][key]
        lines.append(f"| {key} | {block['requested']} | {block['replicates_used']} | {block['seconds']} |")
    lines += ["", "## 宏点估计", "",
              "| K | 方法 | 宏 P-AP | 宏 P-AUROC | 宏 I-AUROC | 宏 I-AP |", "|---|---|---:|---:|---:|---:|"]
    for key in sorted(payload["point"]):
        for method in B1_METHODS:
            values = payload["point"][key].get(method)
            if values is None:
                continue
            lines.append(f"| {key} | {method} | {_fmt(values['pixel_ap'])} | {_fmt(values['pixel_auroc'])} | "
                         f"{_fmt(values['image_auroc'])} | {_fmt(values['image_ap'])} |")
    lines += ["", "## 配对差值（宏像素 AP；图像级配对 bootstrap）", "",
              "| K | 对比 | 组 | 点差 | 95% 区间 | 差值<0 比例 | 有效复制数 |",
              "|---|---|---|---:|---|---:|---:|"]
    for row in contrast_rows:
        if row["metric"] != "pixel_ap":
            continue
        lines.append(f"| {row['shot']} | {row['contrast']} | {row['contrast_group']} | "
                     f"{_fmt(row['point_delta'])} | [{_fmt(row['ci_low'])}, {_fmt(row['ci_high'])}] | "
                     f"{_fmt(row['fraction_below_zero'])} | {row['n_replicates']} |")
    verification = payload["verification"]
    lines += ["", "## 复核", "",
              f"- 加权指标 vs sklearn/显式重采样：通过={verification['metric_primitive']['pass']}",
              f"- 点估计 vs 各单元 metrics.csv：最大绝对差 {verification['point_estimates']['max_abs_diff']}"
              f"（容限 5e-6，通过={verification['point_estimates']['pass']}）",
              f"- 单元实现不变量：{verification['unit_invariants']}", "",
              "## 允许与不允许的结论", "",
              "- 允许：说 B/C 的权重与共同匹配约束在第二个预定支持抽样上复现或未复现。",
              "- 不允许：说真实三支（TRI/BAL）已在 seed1 复核（无 seed1 DINO-S）。",
              "- 不允许：把 seed0 与 seed1 当作独立数据集，或合并 K2/K4 成四个独立 seed。",
              "- 不允许：因方向不符而改换 seed。", ""]
    return "\n".join(lines)


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and np.isnan(value):
        return "nan"
    return f"{value:.5f}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--categories", nargs="+", default=CATEGORIES)
    parser.add_argument("--shots", nargs="+", type=int, default=list(SHOTS))
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--checkpoint-every", type=int, default=25)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    output: Path = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()

    audit = audit_seed1()
    write_json(output / "AUDIT_SEED1_BC.json", audit)
    print(f"[seed1] audit all_pass={audit['all_pass']}", flush=True)
    if not audit["all_pass"]:
        write_json(output / "STATUS.json", {"state": "audit_failed", "created_utc": now()})
        return 1
    if args.audit_only:
        write_json(output / "STATUS.json", {"state": "audit_only", "created_utc": now(),
                                            "audit_all_pass": True})
        print(f"[seed1] audit written to {output / 'AUDIT_SEED1_BC.json'}", flush=True)
        return 0

    shots = tuple(args.shots)
    protocol = {
        "stage": "B1", "seed": SEED, "branches": ["B", "C"],
        "dataset": "mpdd", "categories": list(args.categories), "shots": list(shots),
        "methods": B1_METHODS, "reference_method": REFERENCE,
        "weights": {
            "B": {"B": 1.0}, "C": {"C": 1.0}, "A1_J": {"B": .5, "C": .5},
            "DUP_J": {"B": 1 / 3, "Bcopy": 1 / 3, "C": 1 / 3},
            "DUP_BAL_J": {"B": .25, "Bcopy": .25, "C": .5},
            "DUP_EXPECTED_J": {"B": 2 / 3, "C": 1 / 3},
        },
        "lambda": [0.0, 0.25, 0.5, 0.75, 1.0],
        "cache_policy": "canonical K4 query and reference; K2 uses the first two K4 references",
        "postprocess": "448 bilinear then gaussian sigma4; image max; stride-8 evaluation",
        "bootstrap_seed": 20260912, "replicates": args.replicates,
        "uncertainty": ("paired image-level bootstrap under reference seed 1 only; K2 and K4 are "
                        "reported separately and are not independent seeds"),
        "no_three_branch_claim": "no seed-1 DINO-S cache exists, so TRI/BAL cannot be replicated",
        "audit_hash": hashlib.sha256(json.dumps(audit, sort_keys=True).encode("utf-8")).hexdigest(),
        "source_hashes": {name: sha256(HERE / name)
                          for name in ("engine.py", "diagnostics.py", "complete_statistics.py",
                                       "replicate_seed1_bc.py")},
        "created_utc": now(),
    }
    protocol_path = output / "PROTOCOL.json"
    if protocol_path.exists():
        existing = read_json(protocol_path)
        if existing.get("shots") != protocol["shots"] or existing.get("seed") != SEED:
            raise RuntimeError(f"{protocol_path} exists with a different protocol; refusing to overwrite")
    else:
        write_json(protocol_path, protocol)

    write_json(output / "STATUS.json", {"state": "running", "started_utc": now(),
                                        "replicates_requested": args.replicates})
    failures: list[dict] = []
    unit_summaries = []
    for shot in shots:
        for cat in args.categories:
            unit_dir = output / "units" / f"s1_k{shot}" / cat
            if (unit_dir / "DONE.json").exists() and args.resume:
                print(f"[seed1] skip existing {cat} K{shot}", flush=True)
                continue
            try:
                unit_summaries.append(run_unit(output, cat, shot, args.device, args.chunk))
            except Exception as exc:  # noqa: BLE001 - recorded, never hidden
                failures.append({"category": cat, "shot": shot, "error": f"{type(exc).__name__}: {exc}"})
                write_json(output / "FAILURES.json", failures)
                raise
    write_json(output / "FAILURES.json", failures)

    structures_by_shot: dict[int, list] = {}
    for shot in shots:
        structures = []
        for cat in args.categories:
            directory = output / "units" / f"s1_k{shot}" / cat
            if not (directory / "DONE.json").exists():
                failures.append({"category": cat, "shot": shot, "reason": "missing DONE.json"})
                continue
            structures.append(cs.build_category(directory, shot, B1_METHODS))
        if len(structures) != len(args.categories):
            raise RuntimeError(f"K{shot}: only {len(structures)}/{len(args.categories)} categories")
        structures_by_shot[shot] = structures

    point = {shot: cs.macro_point(structures_by_shot[shot], B1_METHODS) for shot in shots}
    verification = {
        "metric_primitive": cs.verify_metric_primitive(),
        "point_estimates": cs.verify_point_estimates(structures_by_shot, B1_METHODS),
        "unit_invariants": {
            f"k{shot}": {
                "all_pass": all(all(v["pass"] for v in read_json(
                    output / "units" / f"s1_k{shot}" / cat / "invariants.json")["checks"].values())
                    for cat in args.categories),
                "checks": {cat: read_json(output / "units" / f"s1_k{shot}" / cat / "invariants.json")["checks"]
                           for cat in args.categories},
            } for shot in shots},
    }
    results: dict[int, dict] = {}
    for shot in shots:
        identity = cs.sequence_identity(output, structures_by_shot[shot], B1_METHODS,
                                        20260912, shot)
        checkpoint = output / f"BOOTSTRAP_SEED1_k{shot}.npz"
        print(f"[seed1] bootstrapping K{shot}: {len(B1_METHODS)} methods x {args.replicates}", flush=True)
        results[shot] = cs.bootstrap(structures_by_shot[shot], B1_METHODS, args.replicates,
                                     20260912, checkpoint, args.checkpoint_every, args.resume,
                                     identity, 0.0)
        print(f"[seed1] K{shot}: {results[shot]['replicates_used']} replicates in "
              f"{results[shot]['seconds']}s", flush=True)

    contrast_rows = [row for shot in sorted(results) for row in b1_contrasts(results[shot], point[shot])]
    point_rows = []
    per_category_rows = []
    for shot in shots:
        for method in B1_METHODS:
            values = point[shot][method]
            point_rows.append({"shot": shot, "method": method,
                               "n_categories": len(structures_by_shot[shot]),
                               "macro_pixel_ap": values["pixel_ap"],
                               "macro_pixel_auroc": values["pixel_auroc"],
                               "macro_image_auroc": values["image_auroc"],
                               "macro_image_ap": values["image_ap"]})
            for st in structures_by_shot[shot]:
                per_category_rows.append({"shot": shot, "method": method, "category": st.category,
                                          **st.point[method]})
    cs.write_csv(output / "point_by_k.csv",
                 ["shot", "method", "n_categories", "macro_pixel_ap", "macro_pixel_auroc",
                  "macro_image_auroc", "macro_image_ap"], point_rows)
    cs.write_csv(output / "per_category.csv",
                 ["shot", "method", "category", "pixel_auroc", "pixel_ap", "image_auroc", "image_ap"],
                 per_category_rows)
    cs.write_csv(output / "paired_deltas.csv",
                 ["shot", "contrast", "contrast_group", "metric", "method", "reference",
                  "point_delta", "mean_delta", "ci_low", "ci_high", "fraction_below_zero",
                  "n_replicates"], contrast_rows)

    samples = {}
    for shot, result in results.items():
        for method in B1_METHODS:
            for key in cs.METRIC_KEYS:
                samples[f"k{shot}__{method}__{key}"] = result["arrays"][method][key]
    np.savez_compressed(output / "bootstrap_samples.npz", **samples)

    acceptance = {
        "units": sum(len(v) for v in structures_by_shot.values()),
        "expected_units": len(shots) * len(args.categories),
        "replicates_used": {shot: results[shot]["replicates_used"] for shot in sorted(results)},
        "audit_all_pass": audit["all_pass"],
    }
    acceptance["pass"] = bool(acceptance["units"] == acceptance["expected_units"]
                              and all(v == args.replicates for v in acceptance["replicates_used"].values())
                              and audit["all_pass"]
                              and verification["metric_primitive"]["pass"]
                              and verification["point_estimates"]["pass"]
                              and all(v["all_pass"] for v in verification["unit_invariants"].values()))
    verification["acceptance"] = acceptance

    write_json(output / "verification.json", verification)
    summary = {
        "output_dir": str(output), "stage": "B1", "seed": SEED,
        "state": "completed" if acceptance["pass"] else "completed_with_findings",
        "started_utc": str(started), "finished_utc": now(),
        "audit_all_pass": audit["all_pass"],
        "support_overlap_total": audit["support_overlap_total"],
        "categories_with_identical_support": audit["categories_with_identical_support"],
        "methods": B1_METHODS, "reference_method": REFERENCE,
        "point": {f"k{shot}": point[shot] for shot in shots},
        "bootstrap": {f"k{shot}": {"requested": results[shot]["requested"],
                                  "replicates_used": results[shot]["replicates_used"],
                                  "seconds": results[shot]["seconds"]}
                      for shot in sorted(results)},
        "verification": verification,
        "failures": failures,
    }
    write_json(output / "RUN_SUMMARY.json", summary)
    (output / "REPORT_CN.md").write_text(render_report(summary, contrast_rows), encoding="utf-8")
    (output / "NEXT_STEPS_CN.md").write_text(
        "\n".join(["# 下一步（阶段 B1 之后）", "",
                   "- 阶段 C：补齐并审计 seed1 的 DINO-S 缓存后，才能做真实三分支（TRI/BAL）复核。",
                   "- 阶段 D：第二数据集与全像素复核，需先核实数据角色与成本。",
                   "- 不得因 seed1 方向不符而改换 seed；不得把 K2/K4 当作独立 seed。", ""]),
        encoding="utf-8")
    write_json(output / "STATUS.json", {"state": summary["state"], "finished_utc": now(),
                                        "acceptance_pass": acceptance["pass"],
                                        "replicates_used": acceptance["replicates_used"]})
    write_json(output / "ARTIFACT_MANIFEST.json", cs.artifact_manifest(output))
    print(f"[seed1] wrote {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
