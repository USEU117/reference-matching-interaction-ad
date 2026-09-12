"""Audit MPDD support-row provenance for the reference-coupling pilot.

This is deliberately a light-weight input audit.  It reads only
``ref_patch_features`` and ``sample_ids`` from the raw NPZ files; it never
loads query feature tensors, masks, labels, FAISS, Torch, or a model.

The raw caches do not contain ``ref_ids``.  A unit can therefore be verified
only when the exporter source, the frozen MPDD manifest, the export report,
support-file hashes, query IDs, and the K2/K4 angular correspondence agree.
The legacy raw K2/K4 prefix result is reported separately from the canonical
policy, which constructs K2 as ``K4[:2]`` in memory.  The absence of an
embedded ``ref_ids`` field is retained in the output and is not silently
promoted to direct cache identity.

Usage (from the repository root)::

    python scripts/reference_coupling_pilot_v1/audit_inputs.py \
        --output experiments/dynamic_fusion/reference_coupling_pilot_20260912/audit

The command writes ``identity_audit.json`` below ``--output``.  It does not
modify any existing cache or experiment artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT_FALLBACK = ROOT / "data" / "mpdd_raw" / "MPDD"
MANIFEST_PATH = ROOT / "data" / "splits" / "mpdd" / "manifest.json"
MANIFEST_SHA_PATH = ROOT / "data" / "splits" / "mpdd" / "manifest.sha256"
PRIOR_ALIGNMENT_PATH = (
    ROOT
    / "experiments"
    / "dynamic_fusion"
    / "validation_handoff_20260911"
    / "E0"
    / "reference_alignment.json"
)

SEED = 0
SHOTS = (2, 4)
CATEGORIES = (
    "bracket_black",
    "bracket_brown",
    "bracket_white",
    "connector",
    "metal_plate",
    "tubes",
)
BRANCHES = ("B", "S", "C")

# A strict audit tolerance.  Values from K2/K4 are expected to be the same
# support extraction when the same support prefix is reused.  The output also
# reports exact equality and the observed max absolute difference, so a
# future deterministic re-export can change this policy deliberately.
PREFIX_ATOL = 1e-6
PREFIX_RTOL = 1e-6
ANGULAR_DIAG_MIN = 0.99999
ANGULAR_MARGIN_MIN = 1e-5

BRANCH_INFO: dict[str, dict[str, Any]] = {
    "B": {
        "name": "dinov2_vitb14",
        "npz_dir": lambda shot: ROOT
        / "outputs"
        / "dynamic_fusion"
        / "v3_direction_a"
        / f"features_vitb14_s{SEED}_k{shot}"
        / "anomalydino_visual",
        "report_dir": lambda shot: ROOT
        / "outputs"
        / "dynamic_fusion"
        / "v3_direction_a"
        / f"features_vitb14_s{SEED}_k{shot}"
        / "anomalydino_visual",
        "exporter": ROOT / "scripts" / "export_a1_mpdd_ref_only.py",
        "exporter_lines": [
            "scripts/export_a1_mpdd_ref_only.py:171-180",
            "scripts/export_a1_mpdd_ref_only.py:182-206",
        ],
        "support_order_evidence": (
            "references = manifest[categories][seed][shot], then direct "
            "for relative in references; ref_blocks.append(patches)"
        ),
        "query_order_evidence": (
            "ref-only export copies sample_ids from the K1 base cache; "
            "load_base_cache and np.savez lines 51-63 and 192-206"
        ),
        "shuffle_evidence": (
            "reference path uses a direct manifest loop; no DataLoader or "
            "shuffle operation occurs in the exporter"
        ),
    },
    "S": {
        "name": "dinov2_vits14",
        "npz_dir": lambda shot: ROOT
        / "outputs"
        / "validation_handoff_20260911"
        / "DINO_S"
        / f"s{SEED}_k{shot}",
        "report_dir": lambda shot: ROOT
        / "outputs"
        / "validation_handoff_20260911"
        / "DINO_S"
        / f"s{SEED}_k{shot}",
        "exporter": ROOT / "scripts" / "export_anomalydino_mpdd_features.py",
        "exporter_lines": [
            "scripts/export_anomalydino_mpdd_features.py:69-79",
            "scripts/export_anomalydino_mpdd_features.py:81-101",
        ],
        "support_order_evidence": (
            "references = manifest[categories][seed][shot], then direct "
            "for relative in references; ref_blocks.append(patches)"
        ),
        "query_order_evidence": (
            "index_dataset returns the sorted MPDD test traversal and the "
            "exporter appends sample.sample_id in that order"
        ),
        "shuffle_evidence": (
            "reference path uses a direct manifest loop; no DataLoader or "
            "shuffle operation occurs in the exporter"
        ),
    },
    "C": {
        "name": "AnomalyCLIP_ViT-L/14@336px",
        "npz_dir": lambda shot: ROOT
        / "outputs"
        / "dynamic_fusion"
        / "v3_direction_a"
        / f"features_s{SEED}_k{shot}"
        / "anomalyclip_text",
        "report_dir": lambda shot: ROOT
        / "outputs"
        / "dynamic_fusion"
        / "v3_direction_a"
        / f"features_s{SEED}_k{shot}"
        / "anomalyclip_text",
        "exporter": ROOT / "scripts" / "export_a1_mpdd_ref_only.py",
        "exporter_lines": [
            "scripts/export_a1_mpdd_ref_only.py:171-180",
            "scripts/export_a1_mpdd_ref_only.py:192-206",
        ],
        "support_order_evidence": (
            "references = manifest[categories][seed][shot], then direct "
            "for relative in references; ref_blocks.append(patches)"
        ),
        "query_order_evidence": (
            "ref-only export copies sample_ids from the K1 base cache; "
            "load_base_cache and np.savez lines 51-63 and 192-206"
        ),
        "shuffle_evidence": (
            "reference path uses a direct manifest loop; no DataLoader or "
            "shuffle operation occurs in the exporter"
        ),
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_ids(values: np.ndarray | list[Any]) -> list[str]:
    return [str(value) for value in np.asarray(values).reshape(-1).tolist()]


def hash_ids(values: list[str]) -> str:
    return sha256_bytes(("\n".join(values)).encode("utf-8"))


def hash_array(array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    return sha256_bytes(contiguous.view(np.uint8).tobytes())


def resolve_data_root(manifest: dict[str, Any]) -> Path:
    recorded = Path(str(manifest.get("root", "")))
    if recorded.is_dir():
        return recorded
    return DATA_ROOT_FALLBACK


def manifest_support_ids(manifest: dict[str, Any], category: str, shot: int) -> list[str]:
    return list(manifest["categories"][category][str(SEED)][str(shot)])


def manifest_support_hash(manifest: dict[str, Any], support_id: str) -> str | None:
    selected = manifest.get("selected_file_sha256", {})
    value = selected.get(support_id)
    return str(value) if value is not None else None


def load_light_npz(path: Path) -> dict[str, Any]:
    """Load only reference features, query IDs, and small metadata arrays."""

    with np.load(path, allow_pickle=False) as archive:
        keys = list(archive.files)
        required = {"ref_patch_features", "sample_ids", "grid_size"}
        missing = sorted(required.difference(keys))
        if missing:
            raise ValueError(f"missing NPZ keys: {missing}")
        # Deliberately do not touch patch_features, imgs_masks, or gt_sp.
        refs = np.asarray(archive["ref_patch_features"])
        sample_ids = canonical_ids(archive["sample_ids"])
        grid = tuple(int(value) for value in np.asarray(archive["grid_size"]).reshape(-1))
        return {
            "keys": keys,
            "refs": refs,
            "sample_ids": sample_ids,
            "grid": list(grid),
        }


def report_entry(report: dict[str, Any], category: str) -> dict[str, Any] | None:
    for row in report.get("categories", []):
        if str(row.get("category")) == category:
            return row
    return None


def normalise_report_path(value: Any) -> Path | None:
    if value is None:
        return None
    try:
        return Path(str(value)).resolve()
    except (OSError, ValueError):
        return None


def support_file_evidence(
    manifest: dict[str, Any],
    data_root: Path,
    support_ids: list[str],
    file_hash_cache: dict[Path, str | None],
) -> tuple[dict[str, Any], bool]:
    rows: dict[str, Any] = {}
    all_match = True
    for support_id in support_ids:
        path = data_root / Path(support_id)
        if path not in file_hash_cache:
            file_hash_cache[path] = sha256_file(path) if path.is_file() else None
        current = file_hash_cache[path]
        recorded = manifest_support_hash(manifest, support_id)
        match = bool(current is not None and recorded is not None and current == recorded)
        all_match = all_match and match
        rows[support_id] = {
            "path": str(path.resolve()),
            "exists": path.is_file(),
            "manifest_sha256": recorded,
            "current_sha256": current,
            "match": match,
        }
    return rows, all_match


def prefix_evidence(k2: np.ndarray, k4: np.ndarray) -> dict[str, Any]:
    result: dict[str, Any] = {
        "k2_shape": list(k2.shape),
        "k4_shape": list(k4.shape),
        "k4_prefix_shape": list(k4[:2].shape) if k4.ndim >= 1 else None,
        "shape_compatible": bool(k2.ndim == k4.ndim and k4.shape[0] >= 2 and k2.shape == k4[:2].shape),
        "exact_equal": False,
        "allclose_atol": PREFIX_ATOL,
        "allclose_rtol": PREFIX_RTOL,
        "allclose": False,
        "max_abs_diff": None,
        "k2_reference_array_sha256": hash_array(k2),
        "k4_prefix_array_sha256": hash_array(k4[:2]) if k4.ndim >= 1 else None,
    }
    if not result["shape_compatible"]:
        return result
    delta = np.asarray(k2, dtype=np.float64) - np.asarray(k4[:2], dtype=np.float64)
    result["max_abs_diff"] = float(np.max(np.abs(delta), initial=0.0))
    result["exact_equal"] = bool(np.array_equal(k2, k4[:2]))
    result["allclose"] = bool(np.allclose(k2, k4[:2], atol=PREFIX_ATOL, rtol=PREFIX_RTOL))
    return result


def angular_correspondence_evidence(k2: np.ndarray, k4: np.ndarray) -> dict[str, Any]:
    """Check row identity without treating small raw numeric drift as a mismatch.

    Each reference image is flattened as one vector, normalized in float64, and
    compared against every K4 reference.  The expected row for K2 row ``i`` is
    K4 row ``i``.  Thresholds are module constants fixed before inspecting the
    current angular results.
    """

    result: dict[str, Any] = {
        "method": "per_reference_image_flatten_then_float64_L2_normalize",
        "diag_threshold": ANGULAR_DIAG_MIN,
        "margin_threshold": ANGULAR_MARGIN_MIN,
        "k2_shape": list(k2.shape),
        "k4_shape": list(k4.shape),
        "shape_compatible": False,
        "cosine_matrix": None,
        "rows": [],
        "all_rows_pass": False,
        "diag_cos_min": None,
        "diag_cos_max": None,
        "margin_min": None,
        "margin_max": None,
    }
    if k2.ndim != 4 or k4.ndim != 4 or k2.shape[0] < 1:
        return result
    if k4.shape[0] < k2.shape[0] or k2.shape[1:] != k4.shape[1:]:
        return result

    result["shape_compatible"] = True
    k2_flat = np.asarray(k2, dtype=np.float64).reshape(k2.shape[0], -1)
    k4_flat = np.asarray(k4, dtype=np.float64).reshape(k4.shape[0], -1)
    k2_norms = np.linalg.norm(k2_flat, axis=1)
    k4_norms = np.linalg.norm(k4_flat, axis=1)
    if np.any(k2_norms == 0.0) or np.any(k4_norms == 0.0):
        result["zero_norm"] = True
        return result
    result["zero_norm"] = False
    k2_unit = k2_flat / k2_norms[:, None]
    k4_unit = k4_flat / k4_norms[:, None]
    cosine = k2_unit @ k4_unit.T
    result["cosine_matrix"] = cosine.tolist()

    rows: list[dict[str, Any]] = []
    for expected_index in range(k2.shape[0]):
        row = cosine[expected_index]
        order = np.argsort(row)[::-1]
        best_index = int(order[0])
        best_value = float(row[best_index])
        second_value = float(row[order[1]]) if len(order) > 1 else None
        offdiag = np.delete(row, expected_index)
        offdiag_max = float(np.max(offdiag)) if offdiag.size else None
        diag_cos = float(row[expected_index])
        margin = diag_cos - offdiag_max if offdiag_max is not None else None
        unique_argmax = bool(np.count_nonzero(row == best_value) == 1)
        row_pass = bool(
            best_index == expected_index
            and unique_argmax
            and diag_cos >= ANGULAR_DIAG_MIN
            and margin is not None
            and margin >= ANGULAR_MARGIN_MIN
        )
        rows.append(
            {
                "expected_k4_index": expected_index,
                "argmax_k4_index": best_index,
                "unique_argmax": unique_argmax,
                "diag_cos": diag_cos,
                "offdiag_max_cos": offdiag_max,
                "margin": margin,
                "second_best_cos": second_value,
                "pass": row_pass,
            }
        )
    result["rows"] = rows
    diag_values = [row["diag_cos"] for row in rows]
    margin_values = [row["margin"] for row in rows if row["margin"] is not None]
    result["diag_cos_min"] = min(diag_values)
    result["diag_cos_max"] = max(diag_values)
    result["margin_min"] = min(margin_values) if margin_values else None
    result["margin_max"] = max(margin_values) if margin_values else None
    result["all_rows_pass"] = bool(rows) and all(row["pass"] for row in rows)
    return result


def canonical_k4_prefix_evidence(k4: np.ndarray) -> dict[str, Any]:
    """Describe the new nested policy, constructed from one K4 array."""

    valid = bool(k4.ndim == 4 and k4.shape[0] >= 2)
    prefix = k4[:2] if valid else None
    prefix_hash = hash_array(prefix) if prefix is not None else None
    return {
        "source": "current K4 reference array",
        "construction": "canonical K2 is constructed in memory as K4[:2]",
        "valid_shape": valid,
        "strict_numeric_nesting_by_construction": valid,
        "constructed_k2_shape": list(prefix.shape) if prefix is not None else None,
        "constructed_k2_reference_array_sha256": prefix_hash,
        "constructed_k4_prefix_array_sha256": prefix_hash,
        "constructed_array_equal": valid,
        "old_k2_file_is_not_rewritten": True,
    }


def canonical_grid_evidence(native_grid: list[int]) -> dict[str, Any]:
    is_native = native_grid == [32, 32]
    return {
        "target_grid": [32, 32],
        "native_grid": native_grid,
        "native_is_canonical": is_native,
        "operation": (
            "identity"
            if is_native
            else "bilinear resize to 32x32, align_corners=False"
        ),
        "row_order": "support image row first, then row-major native patch cells",
        "support_image_row_identity_preserved": True,
        "code_evidence": "scripts/validation_handoff_20260911/common.py:111-118",
        "fusion_evidence": "scripts/validation_handoff_20260911/common.py:141-165",
    }


def category_npz_path(branch: str, shot: int, category: str) -> Path:
    return BRANCH_INFO[branch]["npz_dir"](shot) / f"{category}.npz"


def report_path(branch: str, shot: int) -> Path:
    return BRANCH_INFO[branch]["report_dir"](shot) / "export_report.json"


def unit_provenance(
    branch: str,
    shot: int,
    category: str,
    npz_path: Path,
    report_path_: Path,
    manifest_hash: str,
) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    info = BRANCH_INFO[branch]
    report: dict[str, Any] = {}
    if not report_path_.is_file():
        failures.append("missing_export_report")
    else:
        try:
            report = json.loads(report_path_.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"invalid_export_report:{type(exc).__name__}")

    row = report_entry(report, category)
    if row is None:
        failures.append("missing_category_in_export_report")
    if not npz_path.is_file():
        failures.append("missing_npz")

    report_manifest_hash = report.get("manifest_sha256") if report else None
    if report_manifest_hash != manifest_hash:
        failures.append("export_report_manifest_hash_mismatch")

    recorded_output = normalise_report_path(row.get("output")) if row else None
    if recorded_output is None or recorded_output != npz_path.resolve():
        failures.append("export_report_output_path_mismatch")

    report_ref_count = None
    if row is not None:
        report_ref_count = row.get("references")
        if report_ref_count is None:
            failures.append("export_report_missing_reference_count")
        elif int(report_ref_count) < 1:
            failures.append("export_report_invalid_reference_count")

    exporter = Path(info["exporter"])
    if not exporter.is_file():
        failures.append("missing_generation_script")

    source_paths: dict[str, Any] = {
        "npz": str(npz_path.resolve()),
        "export_report": str(report_path_.resolve()),
        "manifest": str(MANIFEST_PATH.resolve()),
        "manifest_sha256_sidecar": str(MANIFEST_SHA_PATH.resolve()),
        "generation_script": str(exporter.resolve()),
    }
    source_hashes: dict[str, Any] = {
        "export_report_sha256": sha256_file(report_path_) if report_path_.is_file() else None,
        "manifest_sha256_current": manifest_hash,
        "manifest_sha256_sidecar_file": sha256_file(MANIFEST_SHA_PATH)
        if MANIFEST_SHA_PATH.is_file()
        else None,
        "generation_script_sha256": sha256_file(exporter) if exporter.is_file() else None,
        "npz_full_sha256_recorded_by_export_report": row.get("sha256") if row else None,
        "npz_full_sha256_rehashed_now": False,
        "npz_hash_scope_note": (
            "The large NPZ full hash is recorded from export_report only; this audit "
            "re-hashes the loaded reference array and query ID bytes instead."
        ),
    }
    query_source = report.get("test_features_source") if report else None
    if query_source:
        query_source_path = Path(str(query_source))
        source_paths["query_feature_source"] = str(query_source_path)
        query_report = query_source_path / "export_report.json"
        source_paths["query_feature_source_report"] = str(query_report)
        source_hashes["query_feature_source_report_sha256"] = (
            sha256_file(query_report) if query_report.is_file() else None
        )
    provenance = {
        "report_status": report.get("status") if report else None,
        "report_kind": report.get("kind") if report else None,
        "report_branch": report.get("branch") if report else None,
        "report_recorded_reference_count": report_ref_count,
        "report_recorded_grid": row.get("grid") if row else None,
        "report_recorded_output": row.get("output") if row else None,
        "support_order_evidence": info["support_order_evidence"],
        "query_order_evidence": info["query_order_evidence"],
        "shuffle_evidence": info["shuffle_evidence"],
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "generation_script_lines": info["exporter_lines"],
        "manifest_order_is_the_identity_source": True,
        "direct_ref_ids_in_npz": False,
    }
    return provenance, failures


def inspect_log_evidence() -> dict[str, Any]:
    # The current v3 exports are represented by export_report.json.  The
    # repository also contains older v2/submission logs; do not attach those
    # logs to the current v3 NPZs merely because their names look similar.
    current_candidates = [
        ROOT / "experiments" / "dynamic_fusion" / "validation_handoff_20260911" / "logs",
        ROOT / "outputs" / "validation_handoff_20260911" / "DINO_S",
    ]
    return {
        "current_export_log_candidates": [str(path) for path in current_candidates],
        "current_export_log_found": [],
        "older_log_trees_excluded": [
            "experiments/dynamic_fusion/v2/branch_cache_queue/runtime/logs",
            "submission_repro_20260827/logs",
        ],
        "note": (
            "No current v3 export stdout log is bound to these NPZs. The audit uses "
            "the exporter source plus per-shot export_report and manifest hash; "
            "older logs are not treated as current-cache provenance."
        ),
    }


def inspect_exporter_numeric_controls() -> dict[str, Any]:
    """Record source-level controls relevant to the observed raw drift."""

    patterns = (
        r"autocast",
        r"allow_tf32",
        r"tf32",
        r"float16",
        r"GradScaler",
        r"set_float32_matmul_precision",
    )
    rows: dict[str, Any] = {}
    seen: set[Path] = set()
    for info in BRANCH_INFO.values():
        exporter = Path(info["exporter"]).resolve()
        if exporter in seen:
            continue
        seen.add(exporter)
        text = exporter.read_text(encoding="utf-8") if exporter.is_file() else ""
        matches = {
            pattern: re.findall(pattern, text, flags=re.IGNORECASE)
            for pattern in patterns
        }
        rows[str(exporter)] = {
            "exists": exporter.is_file(),
            "inference_mode_present": "torch.inference_mode" in text,
            "reference_loop_is_direct": "for relative in references" in text,
            "numeric_control_matches": matches,
            "source_lines": {
                "dino_ref_extract": "export_a1_mpdd_ref_only.py:119-126",
                "clip_ref_extract": "export_a1_mpdd_ref_only.py:156-167",
                "dino_s_ref_loop": "export_anomalydino_mpdd_features.py:69-79",
            },
        }
    return {
        "exporters": rows,
        "explicit_autocast_or_tf32_in_exporters": any(
            rows_for_file["numeric_control_matches"][pattern]
            for rows_for_file in rows.values()
            for pattern in (r"autocast", r"allow_tf32", r"tf32")
        ),
        "interpretation": (
            "The inspected exporter sources show inference_mode/direct reference loops, "
            "but no explicit autocast or TF32 control. This is source evidence only and "
            "does not establish the cause of the observed raw float drift."
        ),
    }


def build_audit() -> dict[str, Any]:
    started = time.perf_counter()
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(MANIFEST_PATH)
    manifest_bytes = MANIFEST_PATH.read_bytes()
    manifest_hash = sha256_bytes(manifest_bytes)
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    data_root = resolve_data_root(manifest)
    file_hash_cache: dict[Path, str | None] = {}
    units: list[dict[str, Any]] = []
    prefix_pairs: dict[tuple[str, str], dict[str, Any]] = {}
    angular_pairs: dict[tuple[str, str], dict[str, Any]] = {}
    canonical_pairs: dict[tuple[str, str], dict[str, Any]] = {}
    raw_meta: dict[tuple[str, int, str], dict[str, Any]] = {}

    # Read all three branch caches per shot/category.  Only the small query ID
    # vector and the reference tensor are touched.
    for category in CATEGORIES:
        support_by_shot = {
            shot: manifest_support_ids(manifest, category, shot) for shot in SHOTS
        }
        for branch in BRANCHES:
            for shot in SHOTS:
                path = category_npz_path(branch, shot, category)
                report = report_path(branch, shot)
                provenance, failures = unit_provenance(
                    branch, shot, category, path, report, manifest_hash
                )
                meta: dict[str, Any] = {
                    "branch": branch,
                    "encoder": BRANCH_INFO[branch]["name"],
                    "seed": SEED,
                    "shot": shot,
                    "category": category,
                    "npz_path": str(path.resolve()),
                    "provenance": provenance,
                    "hard_failures": list(failures),
                    "ref_ids_present_in_npz": False,
                    "refs": None,
                    "sample_ids": [],
                    "grid": None,
                    "keys": [],
                }
                if not path.is_file():
                    raw_meta[(branch, shot, category)] = meta
                    continue
                try:
                    loaded = load_light_npz(path)
                    meta.update(
                        {
                            "keys": loaded["keys"],
                            "refs": loaded["refs"],
                            "sample_ids": loaded["sample_ids"],
                            "grid": loaded["grid"],
                        }
                    )
                    if "ref_ids" in loaded["keys"]:
                        meta["ref_ids_present_in_npz"] = True
                    # Embedded IDs are not expected for this audit.  If a
                    # future export includes them, retain the fact but do not
                    # make their presence or absence change the provenance
                    # decision: the manifest/exporter evidence remains the
                    # identity source used here.
                    meta["provenance"]["direct_ref_ids_in_npz"] = bool(
                        meta["ref_ids_present_in_npz"]
                    )
                except Exception as exc:  # keep a per-unit failure record
                    meta["hard_failures"].append(f"npz_read_error:{type(exc).__name__}:{exc}")
                raw_meta[(branch, shot, category)] = meta

            k2_meta = raw_meta[(branch, 2, category)]
            k4_meta = raw_meta[(branch, 4, category)]
            if k2_meta["refs"] is not None and k4_meta["refs"] is not None:
                prefix = prefix_evidence(k2_meta["refs"], k4_meta["refs"])
            else:
                prefix = {
                    "k2_shape": list(k2_meta["refs"].shape) if k2_meta["refs"] is not None else None,
                    "k4_shape": list(k4_meta["refs"].shape) if k4_meta["refs"] is not None else None,
                    "shape_compatible": False,
                    "exact_equal": False,
                    "allclose_atol": PREFIX_ATOL,
                    "allclose_rtol": PREFIX_RTOL,
                    "allclose": False,
                    "max_abs_diff": None,
                    "k2_reference_array_sha256": None,
                    "k4_prefix_array_sha256": None,
                }
            prefix_pairs[(branch, category)] = prefix
            angular_pairs[(branch, category)] = angular_correspondence_evidence(
                k2_meta["refs"], k4_meta["refs"]
            ) if k2_meta["refs"] is not None and k4_meta["refs"] is not None else {
                "method": "per_reference_image_flatten_then_float64_L2_normalize",
                "diag_threshold": ANGULAR_DIAG_MIN,
                "margin_threshold": ANGULAR_MARGIN_MIN,
                "k2_shape": list(k2_meta["refs"].shape) if k2_meta["refs"] is not None else None,
                "k4_shape": list(k4_meta["refs"].shape) if k4_meta["refs"] is not None else None,
                "shape_compatible": False,
                "cosine_matrix": None,
                "rows": [],
                "all_rows_pass": False,
                "diag_cos_min": None,
                "diag_cos_max": None,
                "margin_min": None,
                "margin_max": None,
            }
            canonical_pairs[(branch, category)] = canonical_k4_prefix_evidence(
                k4_meta["refs"]
            ) if k4_meta["refs"] is not None else {
                "source": "current K4 reference array",
                "construction": "canonical K2 is constructed in memory as K4[:2]",
                "valid_shape": False,
                "strict_numeric_nesting_by_construction": False,
                "constructed_k2_shape": None,
                "constructed_k2_reference_array_sha256": None,
                "constructed_k4_prefix_array_sha256": None,
                "constructed_array_equal": False,
                "old_k2_file_is_not_rewritten": True,
            }

        # Cross-branch query order is a separate invariant and is assessed per
        # shot/category, then copied into each of the three unit records.
        for shot in SHOTS:
            branch_ids = {
                branch: raw_meta[(branch, shot, category)]["sample_ids"]
                for branch in BRANCHES
            }
            first = branch_ids[BRANCHES[0]]
            aligned = all(branch_ids[branch] == first for branch in BRANCHES[1:])
            query_alignment = {
                "all_three_branches_order_equal": aligned,
                "ids_sha256_by_branch": {
                    branch: hash_ids(ids) for branch, ids in branch_ids.items()
                },
                "n_test_by_branch": {branch: len(ids) for branch, ids in branch_ids.items()},
                "query_ids_loaded_only": True,
            }
            for branch in BRANCHES:
                raw_meta[(branch, shot, category)]["query_alignment"] = query_alignment

        # Support IDs are manifest-derived; support-file bytes are checked once
        # and then reused for all branches and both shots.
        for shot in SHOTS:
            support_ids = support_by_shot[shot]
            support_files, support_files_match = support_file_evidence(
                manifest, data_root, support_ids, file_hash_cache
            )
            for branch in BRANCHES:
                meta = raw_meta[(branch, shot, category)]
                refs = meta["refs"]
                prefix = prefix_pairs[(branch, category)]
                angular = angular_pairs[(branch, category)]
                canonical = canonical_pairs[(branch, category)]
                failures = list(meta["hard_failures"])
                legacy_raw_prefix_failures: list[str] = []
                query_alignment = meta.get("query_alignment", {})
                if refs is None:
                    failures.append("reference_tensor_unavailable")
                else:
                    if refs.ndim != 4:
                        failures.append("reference_tensor_not_NHWD")
                    if refs.shape[0] != len(support_ids):
                        failures.append("reference_row_count_mismatch_manifest")
                if not support_files_match:
                    failures.append("support_file_hash_mismatch_or_missing")
                if not query_alignment.get("all_three_branches_order_equal", False):
                    failures.append("query_ids_not_aligned_across_B_S_C")
                if not prefix.get("shape_compatible", False):
                    failures.append("k2_k4_prefix_shape_mismatch")
                elif not prefix.get("allclose", False):
                    # Keep this diagnostic separate: it describes the old
                    # independently written K2 file and is not a blocker for
                    # the canonical K4-derived nested policy.
                    legacy_raw_prefix_failures.append("k2_k4_prefix_numeric_mismatch")
                if not angular.get("all_rows_pass", False):
                    failures.append("angular_reference_correspondence_failed")

                native_grid = meta["grid"]
                patch_rows_per_support = None
                row_ranges: list[list[int]] = []
                if refs is not None and refs.ndim == 4:
                    patch_rows_per_support = int(refs.shape[1] * refs.shape[2])
                    row_ranges = [
                        [i * patch_rows_per_support, (i + 1) * patch_rows_per_support]
                        for i in range(int(refs.shape[0]))
                    ]

                provenance_failure_names = {
                    "missing_export_report",
                    "missing_category_in_export_report",
                    "missing_npz",
                    "export_report_manifest_hash_mismatch",
                    "export_report_output_path_mismatch",
                    "export_report_missing_reference_count",
                    "export_report_invalid_reference_count",
                    "missing_generation_script",
                    "reference_tensor_unavailable",
                    "reference_tensor_not_NHWD",
                    "reference_row_count_mismatch_manifest",
                    "support_file_hash_mismatch_or_missing",
                }
                provenance_verified = not any(
                    failure in provenance_failure_names
                    or failure.startswith("invalid_export_report:")
                    or failure.startswith("npz_read_error:")
                    for failure in failures
                )
                source_identity_verified = bool(
                    provenance_verified
                    and query_alignment.get("all_three_branches_order_equal", False)
                    and angular.get("all_rows_pass", False)
                )
                strict_numeric_nesting = bool(prefix.get("allclose", False))
                canonical_policy_valid = bool(
                    source_identity_verified
                    and canonical.get("strict_numeric_nesting_by_construction", False)
                    and not failures
                )
                if canonical_policy_valid:
                    status = "verified_by_provenance_and_canonical_prefix_policy"
                elif failures:
                    status = "failed"
                else:
                    status = "unverified"

                unit = {
                    "seed": SEED,
                    "shot": shot,
                    "category": category,
                    "branch": branch,
                    "encoder": BRANCH_INFO[branch]["name"],
                    "status": status,
                    "source_identity_verified": source_identity_verified,
                    "strict_numeric_nesting": strict_numeric_nesting,
                    "canonical_k4_prefix_policy_valid": canonical_policy_valid,
                    "provenance": meta["provenance"],
                    "support_ids": support_ids,
                    "support_id_count": len(support_ids),
                    "support_order_source": "data/splits/mpdd/manifest.json",
                    "support_order_verified_by_provenance": provenance_verified,
                    "support_file_evidence": support_files,
                    "reference_array": {
                        "shape": list(refs.shape) if refs is not None else None,
                        "row_count": int(refs.shape[0]) if refs is not None else None,
                        "native_grid": native_grid,
                        "patch_dimension": int(refs.shape[-1]) if refs is not None else None,
                        "dtype": str(refs.dtype) if refs is not None else None,
                        "current_reference_array_sha256": hash_array(refs)
                        if refs is not None
                        else None,
                        "patch_rows_per_support_image": patch_rows_per_support,
                        "flattened_row_ranges": row_ranges,
                    },
                    "query": {
                        "n_test": len(meta["sample_ids"]),
                        "sample_ids_sha256": hash_ids(meta["sample_ids"]),
                        "query_ids": meta["sample_ids"],
                        "alignment": query_alignment,
                    },
                    "normal_feature_prefix_k2_k4": prefix,
                    "angular_reference_correspondence": angular,
                    "canonical_k4_prefix": canonical,
                    "canonical32grid_alignment": canonical_grid_evidence(native_grid or []),
                    "ref_ids_present_in_npz": bool(meta["ref_ids_present_in_npz"]),
                    "identity_basis": (
                        "manifest support IDs + exporter direct-loop order + support-file hashes + "
                        "query IDs + K2/K4 angular correspondence; no embedded ref_ids"
                    ),
                    "hard_failures": failures,
                    "legacy_raw_prefix_failures": legacy_raw_prefix_failures,
                    "limitations": [
                        "NPZ has no ref_ids; this is provenance-based identity, not direct embedded-ID verification.",
                        "The NPZ full SHA256 is taken from export_report and not rehashed in this light audit.",
                        "Only ref_patch_features and sample_ids were loaded; query feature tensors were not loaded.",
                    ],
                }
                units.append(unit)

    status_counts: dict[str, int] = {}
    for unit in units:
        status_counts[unit["status"]] = status_counts.get(unit["status"], 0) + 1

    reexport_pairs = []
    for branch in BRANCHES:
        for category in CATEGORIES:
            prefix = prefix_pairs[(branch, category)]
            if not prefix.get("allclose", False):
                reexport_pairs.append(
                    {
                        "seed": SEED,
                        "category": category,
                        "branch": branch,
                        "shots": [2, 4],
                        "reason": "K2 reference array is not within strict prefix tolerance of K4[:2]",
                        "max_abs_diff": prefix.get("max_abs_diff"),
                    }
                )

    verified = len(units) == 36 and all(
        unit["canonical_k4_prefix_policy_valid"] and not unit["hard_failures"] for unit in units
    )
    return {
        "schema_version": 2,
        "audit_id": "reference_coupling_pilot_v1_identity_audit",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "repository_root": str(ROOT),
        "scope": {
            "dataset": "mpdd",
            "seed": SEED,
            "shots": list(SHOTS),
            "categories": list(CATEGORIES),
            "branches": list(BRANCHES),
            "unit_count": len(units),
        },
        "all_pass": verified,
        "canonical_k4_prefix_policy_valid": verified,
        "source_identity_verified": bool(units) and all(u["source_identity_verified"] for u in units),
        "legacy_strict_numeric_nesting": bool(units) and all(u["strict_numeric_nesting"] for u in units),
        "status_counts": status_counts,
        "prefix_policy": {
            "atol": PREFIX_ATOL,
            "rtol": PREFIX_RTOL,
            "strict_status_requires_allclose": False,
            "decision_basis": "canonical K4-derived policy; historical raw equality remains separately reported",
            "angular_diagonal_min": ANGULAR_DIAG_MIN,
            "angular_margin_min": ANGULAR_MARGIN_MIN,
            "exact_equality_is_reported_separately": True,
        },
        "manifest": {
            "path": str(MANIFEST_PATH.resolve()),
            "current_sha256": manifest_hash,
            "sha256_sidecar_path": str(MANIFEST_SHA_PATH.resolve()),
            "sha256_sidecar_file_sha256": sha256_file(MANIFEST_SHA_PATH)
            if MANIFEST_SHA_PATH.is_file()
            else None,
            "recorded_root": manifest.get("root"),
            "data_root_used": str(data_root.resolve()),
            "nested_field": manifest.get("nested"),
            "manifest_is_identity_source": True,
        },
        "prior_alignment_record": {
            "path": str(PRIOR_ALIGNMENT_PATH.resolve()),
            "sha256": sha256_file(PRIOR_ALIGNMENT_PATH)
            if PRIOR_ALIGNMENT_PATH.is_file()
            else None,
            "used_as_current_decision": False,
            "note": "Prior E0 record is retained as corroborating provenance; this script recomputes the light checks.",
        },
        "log_evidence": inspect_log_evidence(),
        "units": units,
        "legacy_raw_prefix_mismatches": reexport_pairs,
        "minimum_reexport_required": {
            "needed": not verified,
            "recommended_minimal_action": "Inspect failed identity checks before any experiment." if not verified else
                "No re-encoding required for canonical protocol: use the existing K4 query/reference cache and derive K2 by slicing the first two references; do not modify old files.",
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "faiss_or_torch_loaded": False,
            "query_feature_arrays_loaded": False,
            "large_npz_full_hashes_rehashed": False,
            "duration_seconds": round(time.perf_counter() - started, 3),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory; identity_audit.json is written below it.",
    )
    args = parser.parse_args()
    initial = args.output / "identity_audit_initial.json"
    existing = args.output / "identity_audit.json"
    if existing.exists() and not initial.exists():
        import shutil
        args.output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(existing, initial)
    result = build_audit()
    args.output.mkdir(parents=True, exist_ok=True)
    output_path = args.output / "identity_audit.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output_path.resolve()),
                "all_pass": result["all_pass"],
                "status_counts": result["status_counts"],
                "unit_count": result["scope"]["unit_count"],
                "duration_seconds": result["runtime"]["duration_seconds"],
            },
            ensure_ascii=False,
        )
    )
    # Scientific audit failures are represented in the JSON (`all_pass` and
    # per-unit `status`); report generation itself remains a successful CLI
    # operation so callers can consume the artifact and decide next steps.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
