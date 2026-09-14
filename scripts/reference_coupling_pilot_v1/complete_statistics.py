"""Stage A: complete the seed-0 L/lambda paired statistics and verify the implementation.

Why this module exists
----------------------
The frozen P4 entry point ``analyze.py`` computed the paired bootstrap for the
nine *primary* methods only, so the L endpoints and the fixed-lambda
intermediates have point estimates but no paired intervals.  Re-running the
original command cannot fill that gap.  This module is an **independent**
entry point: it never writes into ``run.py``/``engine.py``/``diagnostics.py``
or into the frozen run directory, and it only reads the artifacts those
writers produced.

What it does
------------
* Loads the 21 methods that the frozen engine wrote into ``evaluation_scores.npz``
  (nine primary + ``A1``/``TRI``/``BAL`` x ``{L, lambda=.25/.50/.75}``).
* Runs an image-level paired bootstrap with the *same* random stream as the
  frozen analysis (``default_rng([20260912, shot, replicate])`` and the
  document's category order), K2 and K4 separately, 1000 replicates each.
* Reports the original nine methods, the twelve within-family contrasts
  (``L-J`` and three ``S_lambda-J``), and every additional method against
  ``A1_J`` while flagging the rows that are listed twice.
* Verifies: the weighted metric primitive against sklearn and against the
  explicit-resampling path, the 21 point estimates against ``metrics.csv``,
  and the nine primary replicate series against the frozen checkpoint.

The weighted metric is an exact reformulation, not an approximation: drawing
an image with multiplicity ``k`` is the same as giving every one of that
image's stride-8 pixels the integer weight ``k``, so grouping equal scores and
summing weights reproduces the explicit resample bit for bit.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import analyze as base  # noqa: E402  (metric primitives + parity helpers)

ROOT = HERE.parents[1]
CATEGORIES = ["bracket_black", "bracket_brown", "bracket_white", "connector",
              "metal_plate", "tubes"]
SHOTS = (2, 4)
PRIMARY_METHODS = ["B", "S", "C", "A1_J", "TRI_J", "BAL_J",
                   "DUP_J", "DUP_BAL_J", "DUP_EXPECTED_J"]
LAMBDA_BASES = {
    "A1": ("A1_L", "A1_lambda_0.25", "A1_lambda_0.50", "A1_lambda_0.75", "A1_J"),
    "TRI": ("TRI_L", "TRI_lambda_0.25", "TRI_lambda_0.50", "TRI_lambda_0.75", "TRI_J"),
    "BAL": ("BAL_L", "BAL_lambda_0.25", "BAL_lambda_0.50", "BAL_lambda_0.75", "BAL_J"),
}
LAMBDA_OFFSETS = (0.0, 0.25, 0.50, 0.75, 1.0)
ADDITIONAL_METHODS = [name for names in LAMBDA_BASES.values() for name in names[:4]]
ALL_METHODS = PRIMARY_METHODS + ADDITIONAL_METHODS  # 21
REFERENCE = "A1_J"
METRIC_KEYS = base.METRIC_KEYS
EFFECT_SCALE = 0.005
OLD_CHECKPOINT_TOLERANCE = 1e-10
POINT_TOLERANCE = 5e-6
SKLEARN_TOLERANCE = 1e-12
GRID = 56  # 448 / stride 8

MANIFEST_EXCLUDE = {"ARTIFACT_MANIFEST.json", "STATUS.json"}


# --------------------------------------------------------------------------- metric primitive


def weighted_auroc_ap(group_total: np.ndarray, group_pos: np.ndarray) -> tuple[float, float]:
    """Tie-correct AUROC/AP from weighted score groups (exact for integer weights).

    ``group_total``/``group_pos`` are the summed weights of all pixels and of
    the positive pixels inside each group of equal scores, groups ordered by
    ascending score.  This is algebraically identical to
    ``analyze.pooled_auroc_ap`` on the explicitly expanded resample; the tests
    assert that equality.
    """
    total = float(np.asarray(group_total, dtype=np.float64).sum())
    pos = float(np.asarray(group_pos, dtype=np.float64).sum())
    neg = total - pos
    if pos <= 0.0 or neg <= 0.0:
        return float("nan"), float("nan")
    gt = np.asarray(group_total, dtype=np.float64)
    gp = np.asarray(group_pos, dtype=np.float64)
    # An image that was not drawn keeps zero weight, so its score groups exist in
    # the pre-computed sort but are absent from the explicit resample.  Dropping
    # them is exact and keeps the AP precision from dividing by an empty group.
    keep = gt > 0.0
    gt = gt[keep]
    gp = gp[keep]
    neg_in = gt - gp
    negative_before = np.cumsum(neg_in) - neg_in
    concordant = float((gp * negative_before).sum() + 0.5 * (gp * neg_in).sum())
    auroc = concordant / (pos * neg)

    tp = np.cumsum(gp[::-1])
    counts = np.cumsum(gt[::-1])
    precision = tp / counts
    recall = tp / pos
    ap = float((np.diff(np.concatenate(([0.0], recall))) * precision).sum())
    return auroc, ap


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, payload) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
                          encoding="utf-8")


# --------------------------------------------------------------------------- per-category structure


class CategoryStructure:
    """One category at one K, reduced to a fixed sort order per method.

    Storing the sort order once turns every replicate into a gather plus a
    grouped sum instead of a fresh ``argsort`` per method, which is what made
    the frozen run spend minutes per thousand replicates.
    """

    def __init__(self, category: str, shot: int, n_images: int, labels: np.ndarray,
                 pixel_y: np.ndarray, starts: dict, sorted_image: dict,
                 is_pos_sorted: dict, image_scores: dict, pixel_block: dict, point: dict,
                 metrics_rows: list[dict], source_path: Path):
        self.category = category
        self.shot = shot
        self.n_images = n_images
        self.labels = labels
        self.pixel_y = pixel_y
        self.starts = starts
        self.sorted_image = sorted_image
        self.is_pos_sorted = is_pos_sorted
        self.image_scores = image_scores
        self.pixel_block = pixel_block
        self.point = point
        self.metrics_rows = metrics_rows
        self.source_path = source_path

    def n_defect_pixels(self) -> int:
        return int(self.pixel_y.sum())


def build_category(directory: Path, shot: int, methods: list[str]) -> CategoryStructure:
    done = _read_json(directory / "DONE.json")
    if not done.get("invariants_pass", False):
        raise RuntimeError(f"{directory}/DONE.json: invariants_pass is not true")
    n_images = int(done["n_images"])
    sources = directory / "evaluation_scores.npz"
    with np.load(sources, allow_pickle=False) as z:
        names = [str(x) for x in z["method_names"]]
        index = {name: i for i, name in enumerate(names)}
        missing = [m for m in methods if m not in index]
        if missing:
            raise RuntimeError(f"{sources}: missing methods {missing}")
        masks = z["pixel_masks"].astype(np.uint8)
        labels = z["labels"].astype(np.int32)
        if labels.size != n_images:
            raise RuntimeError(f"{sources}: labels disagree with DONE.json n_images")
        pixel_all = z["pixel_scores"]
        image_all = z["image_scores"]

        pixel_y = (masks.reshape(-1) > 0)
        per_image = pixel_y.size // n_images
        image_of_pixel = np.repeat(np.arange(n_images, dtype=np.int32), per_image)

        starts: dict[str, np.ndarray] = {}
        sorted_image: dict[str, np.ndarray] = {}
        is_pos_sorted: dict[str, np.ndarray] = {}
        image_scores: dict[str, np.ndarray] = {}
        pixel_block: dict[str, np.ndarray] = {}
        point: dict[str, dict] = {}
        for name in methods:
            i = int(index[name])
            block = np.array(pixel_all[i], dtype=np.float32).reshape(n_images, per_image)
            pixel_block[name] = block
            scores = block.astype(np.float64).reshape(-1)
            order = np.argsort(scores, kind="stable")
            ordered = scores[order]
            change = np.nonzero(np.diff(ordered))[0] + 1
            starts[name] = np.concatenate(([0], change)).astype(np.int64)
            sorted_image[name] = image_of_pixel[order].astype(np.int16)
            is_pos_sorted[name] = pixel_y[order]
            image_scores[name] = np.array(image_all[i], dtype=np.float32)
            p_auroc, p_ap = base.pooled_auroc_ap(scores, pixel_y)
            i_auroc, i_ap = base.pooled_auroc_ap(image_scores[name], labels)
            point[name] = {"pixel_auroc": p_auroc, "pixel_ap": p_ap,
                           "image_auroc": i_auroc, "image_ap": i_ap}
            del scores, ordered, order, block
        del pixel_all, image_all, masks
    gc.collect()
    rows = list(csv.DictReader((directory / "metrics.csv").open(encoding="utf-8-sig")))
    return CategoryStructure(directory.name, shot, n_images, labels, pixel_y, starts,
                             sorted_image, is_pos_sorted, image_scores, pixel_block, point,
                             rows, sources)


def assert_comparable(first: CategoryStructure, second: CategoryStructure) -> None:
    """Refuse to pair resamples whose category image count or order changed."""
    if first.n_images != second.n_images or first.category != second.category:
        raise RuntimeError(f"category {first.category}: incompatible structures across K")


# --------------------------------------------------------------------------- bootstrap


def replicate_metrics(structures: list[CategoryStructure], methods: list[str],
                      seed: int, shot: int, index: int) -> tuple[dict, dict]:
    """One paired replicate: every method sees the same drawn images per class.

    Returns ``(per_method_metrics, diagnostics)``.  Metrics are the four
    document metrics; diagnostics counts how many categories were undefined
    for a method/metric so the macro-mean policy stays explicit instead of
    silently dropping a class.
    """
    rng = np.random.default_rng([int(seed), int(shot), int(index)])
    n_cat = len(structures)
    values = {m: {key: np.full(n_cat, np.nan) for key in METRIC_KEYS} for m in methods}
    for ci, st in enumerate(structures):
        n = st.n_images
        idx = rng.integers(0, n, size=n)
        weights = np.bincount(idx, minlength=n).astype(np.float64)
        i_labels = st.labels[idx]
        for m in methods:
            w = weights[st.sorted_image[m]]
            group_total = np.add.reduceat(w, st.starts[m])
            group_pos = np.add.reduceat(w * st.is_pos_sorted[m], st.starts[m])
            p_auroc, p_ap = weighted_auroc_ap(group_total, group_pos)
            i_auroc, i_ap = base.pooled_auroc_ap(st.image_scores[m][idx], i_labels)
            values[m]["pixel_auroc"][ci] = p_auroc
            values[m]["pixel_ap"][ci] = p_ap
            values[m]["image_auroc"][ci] = i_auroc
            values[m]["image_ap"][ci] = i_ap
    out: dict[str, dict[str, float]] = {}
    nan_categories: dict[str, dict[str, int]] = {}
    for m in methods:
        out[m] = {}
        nan_categories[m] = {}
        for key in METRIC_KEYS:
            column = values[m][key]
            finite = np.isfinite(column)
            out[m][key] = float(column[finite].mean()) if finite.any() else float("nan")
            nan_categories[m][key] = int((~finite).sum())
    return out, nan_categories


def macro_point(structures: list[CategoryStructure], methods: list[str]) -> dict:
    point: dict[str, dict[str, float]] = {}
    for m in methods:
        point[m] = {}
        for key in METRIC_KEYS:
            column = [st.point[m][key] for st in structures]
            finite = [v for v in column if v is not None and np.isfinite(v)]
            point[m][key] = float(np.mean(finite)) if finite else float("nan")
    return point


def sequence_identity(run_root: Path, structures: list[CategoryStructure], methods: list[str],
                      seed: int, shot: int) -> dict:
    """Everything a resuming process must match before it may reuse a checkpoint."""
    source_hashes = {}
    for st in structures:
        source_hashes[str(st.source_path.relative_to(run_root))] = _sha256(st.source_path)
    return {
        "run_root": str(run_root),
        "categories": [st.category for st in structures],
        "n_images": {st.category: st.n_images for st in structures},
        "methods": list(methods),
        "bootstrap_seed": int(seed),
        "shot": int(shot),
        "metric_keys": list(METRIC_KEYS),
        "grid": GRID,
        "pixel_stride": base.STRIDE,
        "source_hashes": source_hashes,
    }


def _identity_hash(identity: dict) -> str:
    blob = json.dumps(identity, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _save_checkpoint(path: Path, method_arrays: dict, methods: list[str], identity: dict,
                     categories: list[str], done: int, requested: int,
                     elapsed_seconds: float) -> None:
    payload = {f"{m}__{key}": method_arrays[m][key][:done]
               for m in methods for key in METRIC_KEYS}
    payload.update(done=np.int64(done), requested=np.int64(requested),
                   methods=np.asarray(methods, dtype=np.str_),
                   categories=np.asarray(categories, dtype=np.str_),
                   identity_hash=np.str_(_identity_hash(identity)),
                   identity_json=np.str_(json.dumps(identity, ensure_ascii=True, sort_keys=True)),
                   elapsed_s=np.float64(elapsed_seconds))
    np.savez_compressed(path, **payload)


def _load_checkpoint(path: Path, methods: list[str], identity: dict,
                     requested: int) -> tuple[int, float, dict] | None:
    with np.load(path, allow_pickle=False) as z:
        stored_methods = [str(x) for x in z["methods"]]
        if stored_methods != list(methods):
            print(f"[stats] ignoring {path.name}: method axis differs", flush=True)
            return None
        if str(z["identity_hash"]) != _identity_hash(identity):
            print(f"[stats] ignoring {path.name}: source identity differs", flush=True)
            return None
        if int(z["requested"]) > int(requested):
            print(f"[stats] ignoring {path.name}: it holds more replicates than requested", flush=True)
            return None
        done = int(z["done"])
        elapsed = float(z["elapsed_s"]) if "elapsed_s" in z.files else 0.0
        stored = {m: {key: z[f"{m}__{key}"].copy() for key in METRIC_KEYS} for m in methods}
    return done, elapsed, stored


def bootstrap(structures: list[CategoryStructure], methods: list[str], requested: int,
              seed: int, checkpoint: Path | None, checkpoint_every: int,
              resume: bool, identity: dict, budget_seconds: float) -> dict:
    shot = structures[0].shot
    categories = [st.category for st in structures]
    t_start = time.perf_counter()

    def run_one(index: int):
        return replicate_metrics(structures, methods, seed, shot, index)

    actual = requested
    if budget_seconds and budget_seconds > 0:
        probe = min(5, requested)
        t0 = time.perf_counter()
        for i in range(probe):
            run_one(i)
        per = (time.perf_counter() - t0) / max(probe, 1)
        allowed = int(budget_seconds / per) if per > 0 else requested
        actual = max(min(requested, 64), min(requested, allowed))
        print(f"[stats] K{shot}: warm-up {per:.2f}s/replicate -> budget caps at {actual}", flush=True)

    arrays = {m: {key: np.full(requested, np.nan) for key in METRIC_KEYS} for m in methods}
    nan_counts = {m: {key: np.zeros(requested, dtype=np.int32) for key in METRIC_KEYS} for m in methods}
    done = 0
    elapsed_before = 0.0
    if checkpoint is not None and checkpoint.exists() and resume:
        saved = _load_checkpoint(checkpoint, methods, identity, requested)
        if saved is not None:
            done, elapsed_before, stored = saved
            for m in methods:
                for key in METRIC_KEYS:
                    arrays[m][key][:done] = stored[m][key]
            print(f"[stats] K{shot}: resuming after {done} stored replicates "
                  f"({elapsed_before:.0f}s already spent)", flush=True)
            del stored
            gc.collect()
    actual = max(actual, done)

    def elapsed() -> float:
        return elapsed_before + (time.perf_counter() - t_start)

    for index in range(done, actual):
        attempt = 0
        while True:
            try:
                values, per_cat_nan = run_one(index)
                break
            except MemoryError:
                attempt += 1
                if attempt >= 6:
                    raise
                gc.collect()
                print(f"[stats] K{shot}: MemoryError at replicate {index}; "
                      f"retry {attempt}", flush=True)
                time.sleep(2.0 * attempt)
        for m in methods:
            for key in METRIC_KEYS:
                arrays[m][key][index] = values[m][key]
                nan_counts[m][key][index] = per_cat_nan[m][key]
        if checkpoint is not None and checkpoint_every and (index + 1) % checkpoint_every == 0:
            _save_checkpoint(checkpoint, arrays, methods, identity, categories, index + 1,
                             requested, elapsed())
            print(f"[stats] K{shot}: {index + 1}/{actual} replicates "
                  f"({elapsed():.0f}s)", flush=True)
    if checkpoint is not None:
        _save_checkpoint(checkpoint, arrays, methods, identity, categories, actual,
                         requested, elapsed())

    return {"shot": shot, "categories": categories, "requested": int(requested),
            "replicates_used": int(actual), "seed": int(seed),
            "seconds": round(elapsed(), 1), "arrays": arrays, "nan_counts": nan_counts,
            "identity": identity, "checkpoint": str(checkpoint) if checkpoint else None}


# --------------------------------------------------------------------------- contrasts


def _ci(delta: np.ndarray) -> dict:
    values = np.asarray(delta, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"point_delta": None, "mean_delta": None, "ci_low": None, "ci_high": None,
                "fraction_below_zero": None, "n_replicates": 0}
    return {"mean_delta": float(values.mean()),
            "ci_low": float(np.percentile(values, 2.5)),
            "ci_high": float(np.percentile(values, 97.5)),
            "fraction_below_zero": float((values < 0).mean()),
            "n_replicates": int(values.size)}


def contrast_table(bootstrap_result: dict, point: dict) -> list[dict]:
    arrays = bootstrap_result["arrays"]
    shot = bootstrap_result["shot"]
    families = [(base_name, name, offset)
                for base_name, names in LAMBDA_BASES.items()
                for name, offset in zip(names, LAMBDA_OFFSETS)]
    rows: list[dict] = []
    for metric in METRIC_KEYS:
        reference_series = arrays[REFERENCE][metric]

        def emit(contrast: str, method: str, other: str, group: str, also: str) -> None:
            delta = arrays[method][metric] - arrays[other][metric]
            stats = _ci(delta)
            stats.update({
                "shot": shot, "contrast": contrast, "contrast_group": group, "metric": metric,
                "method": method, "reference": other,
                "point_delta": (point[method][metric] - point[other][metric]),
                "also_listed_as": also,
            })
            rows.append(stats)

        for method in PRIMARY_METHODS:
            if method == REFERENCE:
                continue
            emit(f"{method} - {REFERENCE}", method, REFERENCE, "primary_vs_A1_J", "")
        for base_name, method, offset in families:
            other = f"{base_name}_J"
            if method == other:
                continue
            also = "additional_vs_A1_J" if base_name == "A1" else ""
            emit(f"{method} - {other}", method, other, "family_lambda", also)
        for method in ADDITIONAL_METHODS:
            also = "family_lambda" if method.startswith("A1_") else ""
            emit(f"{method} - {REFERENCE}", method, REFERENCE, "additional_vs_A1_J", also)
        del reference_series
    return rows


# --------------------------------------------------------------------------- verification


def verify_metric_primitive() -> dict:
    """Weighted grouping vs explicit resampling vs sklearn on adversarial cases."""
    from sklearn.metrics import average_precision_score, roc_auc_score

    cases = []
    rng = np.random.default_rng(20260913)
    # random scores, no ties
    n, m = 40, 25
    scores = rng.normal(size=(n, m)).astype(np.float32)
    labels = (rng.random((n, m)) < 0.3)
    cases.append(("random", scores, labels, rng.integers(1, 4, size=n)))
    # heavy ties
    tied = np.repeat(rng.normal(size=(n, m // 5)).astype(np.float32), 5, axis=1)
    cases.append(("ties", tied, labels, rng.integers(1, 4, size=n)))
    # zero-weight images
    weights = rng.integers(1, 4, size=n)
    weights[: n // 4] = 0
    if weights.sum() == 0:
        weights[0] = 1
    cases.append(("zero_weight_images", scores, labels, weights))
    # duplicate draws of one image only
    dup = np.zeros(n, dtype=np.int64)
    dup[3] = n
    cases.append(("duplicate_draws", scores, labels, dup))
    # extreme imbalance
    imbalanced = np.zeros((n, m), dtype=bool)
    imbalanced.reshape(-1)[0] = True
    cases.append(("extreme_imbalance", scores, imbalanced, np.ones(n, dtype=np.int64)))
    # undefined: a single class after resampling
    single = np.zeros((n, m), dtype=bool)
    cases.append(("undefined_single_class", scores, single, np.ones(n, dtype=np.int64)))

    max_explicit = 0.0
    max_sklearn = 0.0
    undefined_ok = 0
    for name, block, lab, counts in cases:
        expanded_scores = np.repeat(block.astype(np.float64), counts, axis=0).reshape(-1)
        expanded_labels = np.repeat(lab.astype(np.int64), counts, axis=0).reshape(-1)
        explicit = base.pooled_auroc_ap(expanded_scores, expanded_labels)

        order = np.argsort(block.astype(np.float64).reshape(-1), kind="stable")
        flat_scores = block.astype(np.float64).reshape(-1)[order]
        flat_labels = lab.reshape(-1)[order]
        image_of_pixel = np.repeat(np.arange(n), m)[order]
        w = counts[image_of_pixel].astype(np.float64)
        starts = np.concatenate(([0], np.nonzero(np.diff(flat_scores))[0] + 1)).astype(np.int64)
        group_total = np.add.reduceat(w, starts)
        group_pos = np.add.reduceat(w * flat_labels, starts)
        weighted = weighted_auroc_ap(group_total, group_pos)

        for got, want in zip(weighted, explicit):
            if np.isnan(want):
                assert np.isnan(got), (name, got, want)
                undefined_ok += 1
            else:
                max_explicit = max(max_explicit, abs(got - want))
        if not np.isnan(explicit[0]):
            max_sklearn = max(max_sklearn,
                              abs(explicit[0] - roc_auc_score(expanded_labels, expanded_scores)),
                              abs(explicit[1] - average_precision_score(expanded_labels, expanded_scores)))
    return {"cases": [c[0] for c in cases], "undefined_cases_matched": undefined_ok,
            "max_abs_diff_vs_explicit_resample": max_explicit,
            "max_abs_diff_vs_sklearn": max_sklearn,
            "tolerance": SKLEARN_TOLERANCE,
            "pass": bool(max_explicit <= SKLEARN_TOLERANCE and max_sklearn <= SKLEARN_TOLERANCE)}


def verify_against_explicit_path(structures: list[CategoryStructure], methods: list[str],
                                 seed: int, shot: int, indices: tuple[int, ...]) -> dict:
    """Fixed replicate indices: weighted path vs the frozen explicit path."""
    worst = 0.0
    checked = 0
    for index in indices:
        fast, _ = replicate_metrics(structures, methods, seed, shot, index)
        rng = np.random.default_rng([int(seed), int(shot), int(index)])
        slow = {m: {key: [] for key in METRIC_KEYS} for m in methods}
        for st in structures:
            n = st.n_images
            idx = rng.integers(0, n, size=n)
            p_y = st.pixel_y.reshape(n, -1)[idx].reshape(-1)
            i_labels = st.labels[idx]
            for m in methods:
                pixel = st.pixel_block[m][idx].reshape(-1)
                p_auroc, p_ap = base.pooled_auroc_ap(pixel, p_y)
                i_auroc, i_ap = base.pooled_auroc_ap(st.image_scores[m][idx], i_labels)
                slow[m]["pixel_auroc"].append(p_auroc)
                slow[m]["pixel_ap"].append(p_ap)
                slow[m]["image_auroc"].append(i_auroc)
                slow[m]["image_ap"].append(i_ap)
        for m in methods:
            for key in METRIC_KEYS:
                want = base.nanmean(slow[m][key])
                got = fast[m][key]
                if np.isnan(want):
                    continue
                worst = max(worst, abs(got - want))
                checked += 1
    return {"indices": list(indices), "n_comparisons": checked,
            "max_abs_diff": worst, "tolerance": SKLEARN_TOLERANCE,
            "pass": bool(worst <= SKLEARN_TOLERANCE)}


def verify_point_estimates(structures_by_shot: dict[int, list[CategoryStructure]],
                           methods: list[str]) -> dict:
    rows = []
    for shot, structures in structures_by_shot.items():
        for st in structures:
            for m in methods:
                for row in st.metrics_rows:
                    if row.get("method") != m:
                        continue
                    for key in METRIC_KEYS:
                        stored = base.as_float(row.get(key))
                        if stored is None:
                            continue
                        rows.append({"shot": shot, "category": st.category, "method": m,
                                     "metric": key, "abs_diff": abs(stored - st.point[m][key])})
    return {"n_comparisons": len(rows),
            "max_abs_diff": max((r["abs_diff"] for r in rows), default=None),
            "tolerance": POINT_TOLERANCE,
            "pass": bool(all(r["abs_diff"] <= POINT_TOLERANCE for r in rows))}


def verify_old_checkpoint(run_root: Path, results: dict[int, dict]) -> dict:
    out = {}
    for shot, result in results.items():
        path = run_root / f"ANALYSIS_bootstrap_k{shot}.npz"
        if not path.exists():
            out[f"k{shot}"] = {"status": "missing", "path": str(path)}
            continue
        worst = 0.0
        worst_where = ""
        compared = 0
        compared_replicates = None
        with np.load(path, allow_pickle=False) as z:
            stored_methods = [str(x) for x in z["methods"]]
            done = int(z["done"])
            requested = int(z["requested"])
            for m in stored_methods:
                if m not in result["arrays"]:
                    continue
                for key in METRIC_KEYS:
                    key_name = f"{m}__{key}"
                    if key_name not in z.files:
                        continue
                    want = z[key_name][:done]
                    got = result["arrays"][m][key]
                    # A short (smoke-sized) run may hold fewer replicates than the
                    # frozen file; compare the overlap and record it as partial.
                    n = int(min(want.size, got.size))
                    want = want[:n]
                    got = got[:n]
                    both_finite = np.isfinite(want) & np.isfinite(got)
                    if not both_finite.any():
                        continue
                    diff = np.abs(got[both_finite] - want[both_finite])
                    value = float(diff.max())
                    compared += int(both_finite.sum())
                    compared_replicates = n if compared_replicates is None else min(compared_replicates, n)
                    if value > worst:
                        worst, worst_where = value, f"{m}/{key}"
        out[f"k{shot}"] = {"status": "compared" if compared else "no_overlap", "path": str(path),
                           "stored_methods": stored_methods, "stored_done": done,
                           "stored_requested": requested, "n_comparisons": compared,
                           "compared_replicates": compared_replicates,
                           "max_abs_diff": worst, "worst_at": worst_where,
                           "tolerance": OLD_CHECKPOINT_TOLERANCE,
                           "pass": bool(compared > 0 and worst <= OLD_CHECKPOINT_TOLERANCE)}
    return out


# --------------------------------------------------------------------------- writing


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def artifact_manifest(output: Path) -> dict:
    entries = []
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(output))
        if rel in MANIFEST_EXCLUDE:
            continue
        entries.append({"path": rel, "size": path.stat().st_size, "sha256": _sha256(path)})
    return {"output_dir": str(output), "files": entries,
            "note": ("npz/log artifacts follow the repository .gitignore; this manifest records "
                     "what stays on this machine so a handover can verify it")}


def render_report(payload: dict, contrast_rows: list[dict]) -> str:
    lines = ["# 阶段 A：seed0 统计补齐与独立复核", "",
             f"输出目录：`{payload['output_dir']}`", "",
             f"- 源运行目录：`{payload['run_root']}`",
             f"- 方法数：{len(ALL_METHODS)}（九个主要方法 + A1/TRI/BAL 各 L 与 λ=.25/.50/.75）",
             f"- 参照方法：`{REFERENCE}`；实用效应参考尺度：宏像素 AP {EFFECT_SCALE}",
             f"- 抽样口径：图像级配对 bootstrap，`default_rng([{payload['bootstrap_seed']}, shot, replicate])`，"
             f"类别顺序 {CATEGORIES}", "",
             "## 每 K 完成情况", "",
             "| K | 请求复制数 | 实际复制数 | 耗时(s) |", "|---|---:|---:|---:|"]
    for shot in sorted(payload["bootstrap"]):
        block = payload["bootstrap"][shot]
        lines.append(f"| {shot} | {block['requested']} | {block['replicates_used']} | {block['seconds']} |")
    lines += ["", "## 宏点估计（21 方法）", "",
              "| K | 方法 | 宏 P-AP | 宏 P-AUROC | 宏 I-AUROC | 宏 I-AP |", "|---|---|---:|---:|---:|---:|"]
    for shot in sorted(payload["point"]):
        for method in ALL_METHODS:
            values = payload["point"][shot].get(method)
            if values is None:
                continue
            lines.append(f"| {shot} | {method} | {_fmt(values['pixel_ap'])} | "
                         f"{_fmt(values['pixel_auroc'])} | {_fmt(values['image_auroc'])} | "
                         f"{_fmt(values['image_ap'])} |")
    lines += ["", "## 家族内对比（L−J 与 Sλ−J，与 A1_J 对照分开列出）", "",
              "| K | 对比 | 指标 | 点差 | 95% 区间 | 差值<0 比例 | 有效复制数 |",
              "|---|---|---|---:|---|---:|---:|"]
    for row in contrast_rows:
        if row["contrast_group"] != "family_lambda" or row["metric"] != "pixel_ap":
            continue
        lines.append(f"| {row['shot']} | {row['contrast']} | {row['metric']} | {_fmt(row['point_delta'])} | "
                     f"[{_fmt(row['ci_low'])}, {_fmt(row['ci_high'])}] | "
                     f"{_fmt(row['fraction_below_zero'])} | {row['n_replicates']} |")
    lines += ["", "## 附加方法相对 A1_J（与家族内行重复者已标注 also_listed_as）", "",
              "| K | 对比 | 指标 | 点差 | 95% 区间 | 差值<0 比例 | 有效复制数 | 重复于 |",
              "|---|---|---|---:|---|---:|---:|---|"]
    for row in contrast_rows:
        if row["contrast_group"] != "additional_vs_A1_J" or row["metric"] != "pixel_ap":
            continue
        lines.append(f"| {row['shot']} | {row['contrast']} | {row['metric']} | {_fmt(row['point_delta'])} | "
                     f"[{_fmt(row['ci_low'])}, {_fmt(row['ci_high'])}] | "
                     f"{_fmt(row['fraction_below_zero'])} | {row['n_replicates']} | "
                     f"{row['also_listed_as']} |")
    verification = payload["verification"]
    explicit = {k: v.get("max_abs_diff") for k, v in verification.get("explicit_path", {}).items()}
    lines += ["", "## 复核", "",
              f"- 加权指标 vs 显式重采样：最大绝对差 {verification['metric_primitive']['max_abs_diff_vs_explicit_resample']}"
              f"（容限 {SKLEARN_TOLERANCE}，通过={verification['metric_primitive']['pass']}）",
              f"- 加权指标 vs sklearn：最大绝对差 {verification['metric_primitive']['max_abs_diff_vs_sklearn']}",
              f"- 固定复制编号对照冻结显式路径：{explicit}",
              f"- 21 方法点估计 vs `metrics.csv`：最大绝对差 "
              f"{verification['point_estimates']['max_abs_diff']}"
              f"（容限 {POINT_TOLERANCE}，通过={verification['point_estimates']['pass']}）",
              f"- 九个主要方法 1000 复制 vs 旧 checkpoint："
              f"{ {k: v.get('max_abs_diff') for k, v in verification['old_checkpoint'].items()} }"
              f"（容限 {OLD_CHECKPOINT_TOLERANCE}）", "",
              "## 允许与不允许的结论", "",
              "- 允许：说固定 seed0 下 L/J、固定 λ 的效应量与配对区间已补齐。",
              "- 允许：说原九个方法的结果已被独立重算复核。",
              "- 不允许：说已跨 seed 验证（本阶段只做 seed0）。",
              "- 不允许：把 K2/K4 当作独立 seed 或独立数据集。",
              "- 不允许：选取测试集上最优 λ 并包装成新方法。", ""]
    return "\n".join(lines)


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and np.isnan(value):
        return "nan"
    return f"{value:.5f}"


# --------------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path,
                        default=ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912/main_v2")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--categories", nargs="+", default=CATEGORIES)
    parser.add_argument("--shots", nargs="+", type=int, default=list(SHOTS))
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260912)
    parser.add_argument("--checkpoint-every", type=int, default=25)
    parser.add_argument("--budget-seconds", type=float, default=0.0,
                        help="0 keeps the requested replicate count (the default)")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--tag", default="COMPLETE_STATISTICS")
    parser.add_argument("--explicit-check-indices", default="0,1,2",
                        help="fixed replicate indices compared against the frozen explicit path")
    args = parser.parse_args()

    run_root: Path = args.run.resolve()
    output: Path = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    shots = tuple(args.shots)
    started = time.time()
    _write_json(output / "STATUS.json", {
        "state": "running", "started_utc": _utc(started), "pid": None,
        "replicates_requested": args.replicates, "shots": list(shots),
        "categories": list(args.categories), "methods": ALL_METHODS,
    })
    failures: list[dict] = []

    protocol = {
        "stage": "A",
        "purpose": "complete seed-0 L/lambda paired statistics and independently verify the implementation",
        "run_root": str(run_root),
        "output_dir": str(output),
        "methods": ALL_METHODS,
        "primary_methods": PRIMARY_METHODS,
        "additional_methods": ADDITIONAL_METHODS,
        "reference_method": REFERENCE,
        "uncertainty": ("paired image-level bootstrap, reference seed 0 only; K2/K4 reported "
                        "separately and never pooled as independent seeds"),
        "bootstrap_seed": args.bootstrap_seed,
        "replicates": args.replicates,
        "categories": list(args.categories),
        "shots": list(shots),
        "category_order_for_sampling": list(args.categories),
        "rng": "numpy.random.default_rng([bootstrap_seed, shot, replicate_index])",
        "resampling_unit": "image; a drawn image carries all of its stride-8 pixels, mask and label",
        "metric": "pooled pixel AP/AUROC and image AP/AUROC per category, macro mean over the six categories",
        "undefined_policy": ("a category replicate with a single class yields NaN and is excluded from that "
                             "metric's macro mean; the effective count is recorded, never zero-filled"),
        "effect_scale_macro_pixel_ap": EFFECT_SCALE,
        "tolerances": {"sklearn_and_explicit": SKLEARN_TOLERANCE, "point_estimate": POINT_TOLERANCE,
                       "old_checkpoint": OLD_CHECKPOINT_TOLERANCE},
        "implementation_hashes": {name: _sha256(HERE / name)
                                  for name in ("analyze.py", "complete_statistics.py")
                                  if (HERE / name).exists()},
        "frozen_writers_untouched": ["run.py", "engine.py", "diagnostics.py"],
        "stop_conditions": ["missing DONE.json or invariants_pass=false in any unit",
                            "checkpoint identity mismatch (refused, not merged)",
                            "replicate crash that is not a transient MemoryError"],
        "source_files": {str(p.relative_to(run_root)): _sha256(p) for p in sorted(run_root.rglob("DONE.json"))},
    }
    protocol_path = output / "PROTOCOL.json"
    if protocol_path.exists():
        existing = _read_json(protocol_path)
        if existing.get("shots") != protocol["shots"] or existing.get("methods") != protocol["methods"]:
            raise RuntimeError(f"{protocol_path} exists with a different protocol; refusing to overwrite")
    _write_json(protocol_path, protocol)

    structures_by_shot: dict[int, list[CategoryStructure]] = {}
    for shot in shots:
        structures = []
        for cat in args.categories:
            directory = run_root / "units" / f"s0_k{shot}" / cat
            if not (directory / "DONE.json").exists():
                failures.append({"shot": shot, "category": cat, "reason": "missing DONE.json"})
                continue
            st = build_category(directory, shot, ALL_METHODS)
            print(f"[stats] loaded K{shot}/{cat}: n_images={st.n_images} "
                  f"defect_pixels={st.n_defect_pixels()}", flush=True)
            structures.append(st)
        if len(structures) != len(args.categories):
            raise RuntimeError(f"K{shot}: only {len(structures)}/{len(args.categories)} categories loaded")
        structures_by_shot[shot] = structures

    # K2 and K4 share the same test images, so the per-category image count must agree;
    # otherwise the two K would not be comparable at all.
    for first_shot, other_shot in zip(shots, shots[1:]):
        for first, other in zip(structures_by_shot[first_shot], structures_by_shot[other_shot]):
            assert_comparable(first, other)

    point = {shot: macro_point(structures_by_shot[shot], ALL_METHODS) for shot in shots}

    verification = {
        "metric_primitive": verify_metric_primitive(),
        "point_estimates": verify_point_estimates(structures_by_shot, ALL_METHODS),
    }
    indices = tuple(int(x) for x in str(args.explicit_check_indices).split(",") if x.strip())
    if indices:
        verification["explicit_path"] = {
            f"k{shot}": verify_against_explicit_path(structures_by_shot[shot], ALL_METHODS,
                                                     args.bootstrap_seed, shot, indices)
            for shot in shots}

    results: dict[int, dict] = {}
    if not args.verify_only:
        for shot in shots:
            identity = sequence_identity(run_root, structures_by_shot[shot], ALL_METHODS,
                                         args.bootstrap_seed, shot)
            checkpoint = output / f"{args.tag}_bootstrap_k{shot}.npz"
            print(f"[stats] K{shot}: bootstrapping {len(ALL_METHODS)} methods "
                  f"x {args.replicates} replicates", flush=True)
            results[shot] = bootstrap(structures_by_shot[shot], ALL_METHODS, args.replicates,
                                      args.bootstrap_seed, checkpoint, args.checkpoint_every,
                                      args.resume, identity, args.budget_seconds)
            print(f"[stats] K{shot}: {results[shot]['replicates_used']} replicates in "
                  f"{results[shot]['seconds']}s", flush=True)

    verification["old_checkpoint"] = verify_old_checkpoint(run_root, results) if results else {}

    contrast_rows = [row for shot in sorted(results) for row in contrast_table(results[shot], point[shot])]

    nan_rows = []
    for shot, result in results.items():
        for method in ALL_METHODS:
            for key in METRIC_KEYS:
                counts = result["nan_counts"][method][key]
                array = result["arrays"][method][key]
                nan_rows.append({"shot": shot, "method": method, "metric": key,
                                 "n_replicates": int(array.size),
                                 "n_nan_metric": int((~np.isfinite(array)).sum()),
                                 "n_replicates_with_nan_category": int((counts > 0).sum()),
                                 "max_nan_categories_in_a_replicate": int(counts.max())})

    point_rows = []
    per_category_rows = []
    for shot in shots:
        for method in ALL_METHODS:
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

    write_csv(output / "point_by_k.csv",
              ["shot", "method", "n_categories", "macro_pixel_ap", "macro_pixel_auroc",
               "macro_image_auroc", "macro_image_ap"], point_rows)
    write_csv(output / "per_category.csv",
              ["shot", "method", "category", "pixel_auroc", "pixel_ap", "image_auroc", "image_ap"],
              per_category_rows)
    write_csv(output / "paired_deltas.csv",
              ["shot", "contrast", "contrast_group", "metric", "method", "reference",
               "point_delta", "mean_delta", "ci_low", "ci_high", "fraction_below_zero",
               "n_replicates", "also_listed_as"], contrast_rows)
    write_csv(output / "nan_diagnostics.csv",
              ["shot", "method", "metric", "n_replicates", "n_nan_metric",
               "n_replicates_with_nan_category", "max_nan_categories_in_a_replicate"], nan_rows)

    samples = {}
    for shot, result in results.items():
        for method in ALL_METHODS:
            for key in METRIC_KEYS:
                samples[f"k{shot}__{method}__{key}"] = result["arrays"][method][key]
    if samples:
        np.savez_compressed(output / "bootstrap_samples.npz", **samples)

    acceptance = {
        "units_covered": {shot: [st.category for st in structures_by_shot[shot]] for shot in shots},
        "n_units": sum(len(v) for v in structures_by_shot.values()),
        "expected_units": len(shots) * len(args.categories),
        "methods_complete": sorted(ALL_METHODS) == sorted(set(ALL_METHODS)),
        "replicates_used": {shot: results[shot]["replicates_used"] for shot in sorted(results)},
        "replicates_requested": {shot: results[shot]["requested"] for shot in sorted(results)},
    }
    units_ok = bool(acceptance["n_units"] == acceptance["expected_units"]
                    and len(results) == len(shots)
                    and all(acceptance["replicates_used"][s] == acceptance["replicates_requested"][s]
                            for s in acceptance["replicates_requested"]))
    implementation_ok = bool(verification["metric_primitive"]["pass"]
                             and verification["point_estimates"]["pass"]
                             and all(v.get("pass", False)
                                     for v in verification.get("explicit_path", {}).values()))
    replacement_ok = bool(verification["old_checkpoint"]) and all(
        v.get("status") == "compared" and v.get("pass", False)
        and v.get("compared_replicates") == v.get("stored_done")
        for v in verification["old_checkpoint"].values())
    acceptance.update({"units_and_replicates_ok": units_ok,
                       "implementation_verification_ok": implementation_ok,
                       "old_checkpoint_replayed": replacement_ok,
                       "pass": bool(units_ok and implementation_ok and replacement_ok)})
    verification["acceptance"] = acceptance

    _write_json(output / "verification.json", verification)
    _write_json(output / "FAILURES.json", failures)

    summary = {
        "output_dir": str(output), "run_root": str(run_root),
        "state": "completed" if acceptance["pass"] else "completed_with_findings",
        "started_utc": _utc(started), "finished_utc": _utc(time.time()),
        "categories": list(args.categories), "shots": list(shots),
        "methods": ALL_METHODS, "reference_method": REFERENCE, "effect_scale": EFFECT_SCALE,
        "bootstrap_seed": args.bootstrap_seed,
        "point": {f"k{shot}": point[shot] for shot in shots},
        "bootstrap": {f"k{shot}": {"requested": results[shot]["requested"],
                                  "replicates_used": results[shot]["replicates_used"],
                                  "seconds": results[shot]["seconds"],
                                  "checkpoint": results[shot]["checkpoint"]}
                      for shot in sorted(results)},
        "verification": {"metric_primitive": verification["metric_primitive"],
                         "point_estimates": verification["point_estimates"],
                         "explicit_path": verification.get("explicit_path", {}),
                         "old_checkpoint": verification["old_checkpoint"],
                         "acceptance": acceptance},
        "failures": failures,
        "files": sorted(str(p.relative_to(output)) for p in output.rglob("*") if p.is_file()),
    }
    _write_json(output / f"{args.tag}.json", summary)
    (output / "REPORT_CN.md").write_text(render_report(summary, contrast_rows), encoding="utf-8")
    (output / "NEXT_STEPS_CN.md").write_text(render_next_steps(summary), encoding="utf-8")
    _write_json(output / "STATUS.json", {
        "state": summary["state"], "started_utc": summary["started_utc"],
        "finished_utc": summary["finished_utc"],
        "replicates_requested": args.replicates,
        "replicates_used": {f"k{s}": results[s]["replicates_used"] for s in sorted(results)},
        "acceptance_pass": acceptance["pass"],
    })
    _write_json(output / "ARTIFACT_MANIFEST.json", artifact_manifest(output))
    print(f"[stats] wrote {output}", flush=True)
    return 0


def render_next_steps(summary: dict) -> str:
    acceptance = summary["verification"]["acceptance"]
    return "\n".join([
        "# 下一步（阶段 A 之后）", "",
        f"- 阶段 A 验收通过：{acceptance['pass']}",
        "- 阶段 B0：审计 seed1 B/C 缓存与支持身份（`features_vitb14_s1_k4`、`features_s1_k4`）。",
        "- 阶段 B1：仅在 B0 通过、且获得执行授权时启动 seed1 的 B/C 固定矩阵。",
        "- 阶段 C：需要先补齐并审计 seed1 的 DINO-S 缓存，才能升级为真实三分支复核。",
        "- 阶段 D：第二数据集与全像素复核，需先核实数据角色协议与成本，不得自动扩展。", "",
        "**本阶段不做的事**：跨 seed 结论、跨域迁移结论、用测试标签选 λ、全像素复核。", "",
    ])


def _utc(timestamp: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
