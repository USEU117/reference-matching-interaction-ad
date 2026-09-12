"""P4 aggregation, paired uncertainty and interpretation for the reference-coupling pilot.

This module only reads artifacts written by ``run.py``.  It never recomputes
features and never writes into a unit directory.

Design decisions that follow the handover document:

* K2 and K4 are reported separately and are never treated as independent seeds
  or pooled into a larger sample.
* The resampling unit is the image.  Pixel observations move with their image,
  so a resample pools exactly the pixels of the drawn images.  Resampling is
  paired: the same drawn image indices are used for every method, which is what
  makes the reported deltas paired differences.
* Permutation-seed variation is reported as its own distribution and is never
  merged into the bootstrap (that would fake extra independent samples).
* Only reference seed 0 exists here, so no interval includes reference-seed
  uncertainty.  This is stated in the outputs.
* Effect size uses the pre-declared macro P-AP scale of 0.005.  Small or
  zero-crossing intervals are reported as uncertain, never as "equivalent".
"""
from __future__ import annotations

import argparse
import csv
import gc
import json
import re
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STRIDE = 8
PATCH_MAP_SIZE = (448 // STRIDE, 448 // STRIDE)

PRIMARY_METHODS = [
    "B", "S", "C", "A1_J", "TRI_J", "BAL_J",
    "DUP_J", "DUP_BAL_J", "DUP_EXPECTED_J",
]
REFERENCE = "A1_J"
EFFECT_SCALE = 0.005
LAMBDA_BASES = {
    "A1": ("A1_L", "A1_lambda_0.25", "A1_lambda_0.50", "A1_lambda_0.75", "A1_J"),
    "TRI": ("TRI_L", "TRI_lambda_0.25", "TRI_lambda_0.50", "TRI_lambda_0.75", "TRI_J"),
    "BAL": ("BAL_L", "BAL_lambda_0.25", "BAL_lambda_0.50", "BAL_lambda_0.75", "BAL_J"),
}
LAMBDA_VALUES = (0.0, 0.25, 0.50, 0.75, 1.0)
G_METHODS = ("A1_G", "TRI_G", "BAL_G")
PERM_BASES = (("A1_J", "C"), ("TRI_J", "C"), ("TRI_J", "S"), ("BAL_J", "C"), ("BAL_J", "S"))
CATEGORIES = ["bracket_black", "bracket_brown", "bracket_white", "connector", "metal_plate", "tubes"]
SHOTS = (2, 4)
PERM_RE = re.compile(r"^(?P<base>.+?)__perm_(?P<branch>[CS])_(?P<kind>within|cross)_p(?P<seed>\d+)$")

# ``evaluation_scores.npz`` stores one full pixel plane per configuration (up to
# 152 for K4).  Only these planes have to stay resident; the permutation planes
# are read while the file is open and dropped again immediately.
KEEP_METHODS = set(PRIMARY_METHODS)
for _lambda_names in LAMBDA_BASES.values():
    KEEP_METHODS.update(_lambda_names)
del _lambda_names


# --------------------------------------------------------------------------- metrics


def pooled_auroc_ap(scores: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    """Tie-correct AUROC and average precision from one sort.

    Sklearn's ``average_precision_score`` is the mean of precision at each
    jump of recall, so grouping equal scores reproduces it exactly; ties are
    also handled by the rank-sum AUROC below.
    """
    scores = np.asarray(scores, dtype=np.float64).reshape(-1)
    y = np.asarray(labels).reshape(-1).astype(np.int64, copy=False)
    if y.size != scores.size:
        raise ValueError("scores and labels must have the same length")
    n_pos = int(y.sum())
    n_neg = int(y.size - n_pos)
    if n_pos == 0 or n_neg == 0:
        return float("nan"), float("nan")

    order = np.argsort(scores, kind="stable")
    s = scores[order]
    yy = y[order]
    change = np.nonzero(np.diff(s))[0] + 1
    starts = np.concatenate(([0], change))
    ends = np.concatenate((change, [s.size]))
    n_in = (ends - starts).astype(np.float64)
    pos_in = np.add.reduceat(yy, starts).astype(np.float64)

    negative_before = np.cumsum(n_in - pos_in) - (n_in - pos_in)
    # Ties inside a group split half a win: pos_g * neg_g counted with 0.5.
    concordant = float((pos_in * negative_before).sum()
                       + 0.5 * (pos_in * (n_in - pos_in)).sum())
    auroc = concordant / (n_pos * n_neg)

    tp = np.cumsum(pos_in[::-1])
    total = np.cumsum(n_in[::-1])
    precision = tp / total
    recall = tp / n_pos
    ap = float((np.diff(np.concatenate(([0.0], recall))) * precision).sum())
    return float(auroc), ap


def image_auroc_ap(scores: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    """Image-level AUROC and AP (max-score per image, tie-correct)."""
    return pooled_auroc_ap(scores, labels)


# --------------------------------------------------------------------------- io helpers


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def as_float(value):
    if value in ("", None):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if np.isfinite(out) else None


# --------------------------------------------------------------------------- unit loading


class Unit:
    """One category x K unit, reduced to what P4 needs.

    The pixel plane of every non-kept configuration is consumed here (the
    permutation rows) and then released, so a loaded run stays well below the
    memory a full npz dump would need.
    """

    def __init__(self, directory: Path, payload: dict, scores_path: Path, metrics_rows: list[dict]):
        self.dir = directory
        self.category = payload["category"]
        self.shot = int(payload["shot"])
        self.n_images = int(payload["n_images"])
        self.invariants_pass = bool(payload.get("invariants_pass"))
        self.timing = payload.get("timing", {})
        self.paths = scores_path
        self.metrics_rows = metrics_rows
        with np.load(scores_path, allow_pickle=False) as z:
            methods = [str(x) for x in z["method_names"]]
            pixel = z["pixel_scores"].astype(np.float32)
            image = z["image_scores"].astype(np.float32)
            masks = z["pixel_masks"].astype(np.uint8)
            self.labels = z["labels"].astype(np.int32)
            self.sample_ids = [str(x) for x in z["sample_ids"]]
        if pixel.shape[1] != self.n_images or image.shape[1] != self.n_images:
            raise ValueError(f"{scores_path}: image count disagrees with DONE.json")
        self.methods = methods
        self.method_set = set(methods)
        self.pixel_mask = masks
        self.pixel_y = (masks.reshape(-1) > 0).astype(np.int64)
        self.defect_pixels = int(self.pixel_y.sum())
        self.normal_pixels = int(self.pixel_y.size - self.defect_pixels)
        keep = [i for i, name in enumerate(methods) if name in KEEP_METHODS]
        # Copy out of the stacked planes: a plain view would keep the whole
        # stack alive for as long as the unit exists.
        self.pixel = {methods[i]: np.array(pixel[i], dtype=np.float32) for i in keep}
        self.image = {methods[i]: np.array(image[i], dtype=np.float32) for i in keep}
        self.perm_rows = self._build_perm_rows(methods, pixel)

    def _build_perm_rows(self, methods: list[str], pixel: np.ndarray) -> list[dict]:
        """Permitted interventions for this unit, computed before the planes go away."""
        bases = {base for base, _ in PERM_BASES}
        wanted = []
        for i, name in enumerate(methods):
            match = PERM_RE.match(name)
            if match is not None and match.group("base") in bases:
                wanted.append((i, name, match))
        if not wanted:
            return []
        base_ap = {base: self.point_metrics(base)["pixel_ap"]
                   for base in sorted(bases) if base in self.pixel}
        rows: list[dict] = []
        for i, name, match in wanted:
            ap = pooled_auroc_ap(pixel[i].reshape(-1), self.pixel_y)[1]
            base = match.group("base")
            rows.append({
                "category": self.category, "shot": self.shot,
                "kind": match.group("kind"), "branch": match.group("branch"),
                "base": base, "seed": int(match.group("seed")), "method": name,
                "macro_pixel_ap": ap, "delta_vs_base": ap - base_ap[base],
            })
        return rows

    def has(self, name: str) -> bool:
        return name in self.method_set

    def point_metrics(self, name: str) -> dict:
        pixel_scores = self.pixel[name].reshape(-1)
        p_auroc, p_ap = pooled_auroc_ap(pixel_scores, self.pixel_y)
        i_auroc, i_ap = image_auroc_ap(self.image[name], self.labels)
        return {"pixel_auroc": p_auroc, "pixel_ap": p_ap,
                "image_auroc": i_auroc, "image_ap": i_ap}


def load_units(run_root: Path, categories: list[str], shots: tuple[int, ...]) -> dict[int, dict[str, Unit]]:
    units: dict[int, dict[str, Unit]] = {k: {} for k in shots}
    for shot in shots:
        for cat in categories:
            directory = run_root / "units" / f"s0_k{shot}" / cat
            done = directory / "DONE.json"
            if not done.exists():
                print(f"[analyze] skip (no DONE): K{shot}/{cat}", flush=True)
                continue
            payload = read_json(done)
            if not payload.get("invariants_pass"):
                raise RuntimeError(f"{done} has invariants_pass=false; it must not be interpreted")
            scores = directory / "evaluation_scores.npz"
            metrics_rows = read_csv_rows(directory / "metrics.csv")
            units[shot][cat] = Unit(directory, payload, scores, metrics_rows)
    return units


# --------------------------------------------------------------------------- bootstrap

METRIC_KEYS = ("pixel_auroc", "pixel_ap", "image_auroc", "image_ap")


def _warmup_budget(fn, requested: int, budget_seconds: float) -> int:
    """Cap the replicate count so the bootstrap cannot overrun its budget."""
    if budget_seconds <= 0 or requested <= 0:
        return requested
    t0 = time.perf_counter()
    warm = min(20, requested)
    for _ in range(warm):
        fn()
    elapsed = time.perf_counter() - t0
    if elapsed <= 0:
        return requested
    allowed = int(warm * budget_seconds / elapsed)
    # Never raise the requested count, never drop below a usable minimum.
    return max(min(requested, 64), min(requested, allowed))


def nanmean(values) -> float:
    """Mean of the finite entries; NaN when nothing finite is left."""
    arr = np.asarray(values, dtype=np.float64)
    arr = arr[np.isfinite(arr)]
    return float(arr.mean()) if arr.size else float("nan")


def _guarded(fn, attempts: int = 6, pause_seconds: float = 2.0):
    """Run ``fn``, retrying a transient MemoryError after releasing memory.

    This host is shared with desktop applications that make the system commit
    charge fluctuate by several GiB; a single failed allocation must not
    destroy an hour of completed replicates.
    """
    delay = pause_seconds
    for attempt in range(attempts):
        try:
            return fn()
        except MemoryError:
            if attempt == attempts - 1:
                raise
            gc.collect()
            print(f"[analyze] MemoryError; retry {attempt + 1}/{attempts - 1} "
                  f"after {delay:.0f}s", flush=True)
            time.sleep(delay)
            delay *= 2
    raise AssertionError("unreachable")


def _equivalent_methods(units: dict[str, "Unit"], categories: list[str],
                        methods: list[str]) -> dict[str, str]:
    """Map a method onto an earlier one whose score planes are bitwise identical.

    The weight controls deliberately include distance-equivalent settings, so
    two configurations can produce exactly the same scores.  Recomputing their
    bootstrap would burn memory and time without adding any information; the
    equality is verified on the actual data rather than assumed.
    """
    aliases: dict[str, str] = {}
    for i, method in enumerate(methods):
        for other in methods[:i]:
            same = all(np.array_equal(units[c].pixel[method], units[c].pixel[other])
                       and np.array_equal(units[c].image[method], units[c].image[other])
                       for c in categories)
            if same:
                aliases[method] = other
                break
    return aliases


def _read_checkpoint(path: Path, methods: list[str], seed: int, shot: int,
                     requested: int) -> tuple[int, float, dict[str, dict[str, np.ndarray]]] | None:
    """Load a compatible bootstrap checkpoint, or None when it must be restarted.

    A shorter checkpoint may be extended (that is exactly the crash-resume
    case); a longer one, or one written for other methods/seed/shot, is refused
    so a stale file can never be reinterpreted.  The accumulated compute time
    travels with the checkpoint so the reported duration stays honest.
    """
    with np.load(path, allow_pickle=False) as z:
        stored_methods = [str(x) for x in z["methods"]]
        if (stored_methods != list(methods) or int(z["seed"]) != int(seed)
                or int(z["shot"]) != int(shot) or int(z["requested"]) > int(requested)):
            print(f"[analyze] ignoring {path.name}: it was written for another request", flush=True)
            return None
        done = int(z["done"])
        elapsed = float(z["elapsed_s"]) if "elapsed_s" in z.files else 0.0
        stored = {m: {key: z[f"{m}__{key}"] for key in METRIC_KEYS} for m in methods}
    return done, elapsed, stored


def _save_checkpoint(path: Path, samples: dict, methods: list[str], seed: int, shot: int,
                     requested: int, done: int, elapsed_seconds: float) -> None:
    payload = {f"{m}__{key}": samples[m][key][:done] for m in methods for key in METRIC_KEYS}
    payload.update(done=np.int64(done), seed=np.int64(seed), shot=np.int64(shot),
                   requested=np.int64(requested), methods=np.asarray(methods, dtype=np.str_),
                   elapsed_s=np.float64(elapsed_seconds))
    np.savez_compressed(path, **payload)


def bootstrap_macro(
    units: dict[str, Unit],
    methods: list[str],
    n_replicates: int,
    seed: int,
    budget_seconds: float,
    checkpoint: Path | None = None,
    checkpoint_every: int = 25,
) -> dict:
    """Paired image-level bootstrap of macro (category-mean) metrics.

    Returns point estimates plus, for every method other than the reference,
    the paired delta distribution against the reference.  Each replicate draws
    its own generator from ``[seed, shot, replicate]``, so replicates are
    individually reproducible and an interrupted run can resume.
    """
    categories = [c for c in units if all(units[c].has(m) for m in methods)]
    if not categories:
        raise ValueError("no category has every requested method")
    t_start = time.perf_counter()
    shot = units[categories[0]].shot
    aliases = _equivalent_methods(units, categories, methods)
    unique_methods = [m for m in methods if m not in aliases]

    def one_replicate(index: int) -> dict[str, dict[str, float]]:
        rng = np.random.default_rng([int(seed), int(shot), int(index)])
        per_method = {m: {key: [] for key in METRIC_KEYS} for m in unique_methods}
        for cat in categories:
            unit = units[cat]
            n = unit.n_images
            idx = rng.integers(0, n, size=n)
            p_y = unit.pixel_y.reshape(n, -1)[idx].reshape(-1)
            i_labels = unit.labels[idx]
            for m in unique_methods:
                p_auroc, p_ap = pooled_auroc_ap(unit.pixel[m][idx].reshape(-1), p_y)
                i_auroc, i_ap = image_auroc_ap(unit.image[m][idx], i_labels)
                per_method[m]["pixel_auroc"].append(p_auroc)
                per_method[m]["pixel_ap"].append(p_ap)
                per_method[m]["image_auroc"].append(i_auroc)
                per_method[m]["image_ap"].append(i_ap)
        out: dict[str, dict[str, float]] = {}
        for m in methods:
            source = per_method[aliases.get(m, m)]
            out[m] = {key: nanmean(source[key]) for key in METRIC_KEYS}
        return out

    point = {m: {key: nanmean([units[c].point_metrics(m)[key] for c in categories])
                 for key in METRIC_KEYS} for m in methods}

    actual = _warmup_budget(lambda: one_replicate(0), n_replicates, budget_seconds)
    saved = None
    if checkpoint is not None and checkpoint.exists():
        saved = _read_checkpoint(checkpoint, methods, seed, shot, n_replicates)
    done = 0
    elapsed_before = 0.0
    stored = None
    if saved is not None:
        done, elapsed_before, stored = saved
    actual = max(actual, done)
    samples = {m: {key: np.full(actual, np.nan) for key in METRIC_KEYS} for m in methods}
    if stored is not None:
        for m in methods:
            for key in METRIC_KEYS:
                samples[m][key][:done] = stored[m][key]
        print(f"[analyze] resuming after {done} stored replicates "
              f"({elapsed_before:.0f}s already spent)", flush=True)

    def elapsed() -> float:
        return elapsed_before + (time.perf_counter() - t_start)

    def store(index: int, out: dict[str, dict[str, float]]) -> None:
        for m in methods:
            for key in METRIC_KEYS:
                samples[m][key][index] = out[m][key]

    for index in range(done, actual):
        store(index, _guarded(lambda i=index: one_replicate(i)))
        if checkpoint is not None and checkpoint_every and (index + 1) % checkpoint_every == 0:
            _save_checkpoint(checkpoint, samples, methods, seed, shot, n_replicates,
                             index + 1, elapsed())

    if stored is not None:
        del saved, stored
        gc.collect()
    if checkpoint is not None and done < actual:
        _save_checkpoint(checkpoint, samples, methods, seed, shot, n_replicates,
                         actual, elapsed())

    summary = {}
    for m in methods:
        summary[m] = {"point": point[m], "ci": {}, "n_valid": {}}
        for key in METRIC_KEYS:
            values = samples[m][key]
            values = values[np.isfinite(values)]
            summary[m]["ci"][key] = _ci(values)
            summary[m]["n_valid"][key] = int(values.size)
    contrasts = {}
    for m in methods:
        if m == REFERENCE:
            continue
        contrasts[m] = {}
        for key in METRIC_KEYS:
            delta = samples[m][key] - samples[REFERENCE][key]
            delta = delta[np.isfinite(delta)]
            contrasts[m][key] = {
                "point_delta": point[m][key] - point[REFERENCE][key],
                "mean_delta": float(delta.mean()) if delta.size else None,
                "ci_low": float(np.percentile(delta, 2.5)) if delta.size else None,
                "ci_high": float(np.percentile(delta, 97.5)) if delta.size else None,
                "fraction_below_zero": float((delta < 0).mean()) if delta.size else None,
                "n_replicates": int(delta.size),
            }
    return {"categories": categories, "requested_replicates": int(n_replicates),
            "replicates_used": int(actual), "seed": int(seed), "shot": int(shot),
            "equivalence_verified_on_bitwise_equal_planes": True,
            "equivalent_methods": aliases,
            "checkpoint": str(checkpoint) if checkpoint is not None else None,
            "seconds": round(elapsed(), 1),
            "methods": summary, "contrasts_vs_reference": contrasts}


def _ci(values: np.ndarray) -> dict:
    if values.size == 0:
        return {"mean": None, "ci_low": None, "ci_high": None}
    return {"mean": float(values.mean()),
            "ci_low": float(np.percentile(values, 2.5)),
            "ci_high": float(np.percentile(values, 97.5))}


# --------------------------------------------------------------------------- permutation variation


def permutation_variation(units: dict[str, Unit]) -> list[dict]:
    """Permutation-intervention rows already derived by each unit at load time."""
    rows: list[dict] = []
    for _, unit in units.items():
        rows.extend(unit.perm_rows)
    return rows


def summarise_permutation(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["shot"], row["kind"], row["branch"], row["base"], row["category"])
        groups.setdefault(key, []).append(row)
    out: list[dict] = []
    for (shot, kind, branch, base, cat), items in sorted(groups.items()):
        deltas = np.asarray([r["delta_vs_base"] for r in items], dtype=np.float64)
        aps = np.asarray([r["macro_pixel_ap"] for r in items], dtype=np.float64)
        out.append({
            "shot": shot, "kind": kind, "branch": branch, "base": base, "category": cat,
            "n_seeds": int(deltas.size),
            "mean_pixel_ap": float(aps.mean()), "min_pixel_ap": float(aps.min()),
            "max_pixel_ap": float(aps.max()),
            "mean_delta": float(deltas.mean()), "min_delta": float(deltas.min()),
            "max_delta": float(deltas.max()), "std_delta": float(deltas.std(ddof=1)) if deltas.size > 1 else None,
            "frac_delta_below_zero": float((deltas < 0).mean()),
        })
    return out


def macro_over_categories(rows: list[dict], keys: tuple[str, ...]) -> dict:
    out = {}
    for key in keys:
        values = [r[key] for r in rows if r.get(key) is not None]
        out[key] = float(np.mean(values)) if values else None
    return out


# --------------------------------------------------------------------------- g tails / regions / flips


def g_tails(run_root: Path, units: dict[int, dict[str, Unit]], shots: tuple[int, ...]) -> list[dict]:
    rows: list[dict] = []
    for shot in shots:
        for cat, unit in sorted(units[shot].items()):
            directory = unit.dir
            with np.load(directory / "patch_scores.npz", allow_pickle=False) as z:
                keys = [k for k in G_METHODS if k in z.files]
                if not keys:
                    continue
                arrays = {k: z[k].reshape(unit.n_images, -1).astype(np.float64) for k in keys}
            for name, values in arrays.items():
                per_image = values
                image_mean = per_image.mean(axis=1)
                image_p95 = np.percentile(per_image, 95, axis=1)
                image_max = per_image.max(axis=1)
                for label, selection in (("normal", unit.labels == 0),
                                         ("abnormal", unit.labels > 0),
                                         ("all", np.ones_like(unit.labels, dtype=bool))):
                    if not np.any(selection):
                        continue
                    selected = image_mean[selection]
                    rows.append({
                        "shot": shot, "category": cat, "method": name, "image_class": label,
                        "n_images": int(selected.size),
                        "mean_of_image_means": float(selected.mean()),
                        "p05_of_image_means": float(np.percentile(selected, 5)),
                        "p25_of_image_means": float(np.percentile(selected, 25)),
                        "median_of_image_means": float(np.percentile(selected, 50)),
                        "p75_of_image_means": float(np.percentile(selected, 75)),
                        "p95_of_image_means": float(np.percentile(selected, 95)),
                        "max_of_image_means": float(selected.max()),
                        "mean_of_image_p95": float(image_p95[selection].mean()),
                        "mean_of_image_max": float(image_max[selection].mean()),
                    })
    return rows


def region_macro(units: dict[int, dict[str, Unit]], shots: tuple[int, ...]) -> list[dict]:
    rows: list[dict] = []
    for shot in shots:
        for cat, unit in sorted(units[shot].items()):
            path = unit.dir / "region_stats.csv"
            if not path.exists():
                continue
            for row in read_csv_rows(path):
                rows.append({"shot": shot, "category": cat, **row})
    return rows


def flip_macro(units: dict[int, dict[str, Unit]], shots: tuple[int, ...]) -> list[dict]:
    rows: list[dict] = []
    for shot in shots:
        for cat, unit in sorted(units[shot].items()):
            path = unit.dir / "flip_stats.csv"
            if not path.exists():
                continue
            for row in read_csv_rows(path):
                rows.append({"shot": shot, "category": cat, **row})
    return rows


# --------------------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path,
                        default=ROOT / "experiments/dynamic_fusion/reference_coupling_pilot_20260912/main_v2")
    parser.add_argument("--categories", nargs="+", default=CATEGORIES)
    parser.add_argument("--shots", nargs="+", type=int, default=list(SHOTS))
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260912)
    parser.add_argument("--bootstrap-budget-seconds", type=float, default=2700.0)
    parser.add_argument("--bootstrap-checkpoint-every", type=int, default=25,
                        help="write a resumable checkpoint every N replicates (0 disables)")
    parser.add_argument("--tag", default="ANALYSIS")
    args = parser.parse_args()
    run_root: Path = args.run.resolve()
    shots = tuple(args.shots)

    units = load_units(run_root, args.categories, shots)
    coverage = {shot: sorted(units[shot]) for shot in shots}
    print(f"[analyze] coverage {coverage}", flush=True)

    out_json: dict = {
        "run_root": str(run_root),
        "shots": list(shots),
        "categories_requested": list(args.categories),
        "coverage": coverage,
        "reference_method": REFERENCE,
        "effect_scale_macro_pixel_ap": EFFECT_SCALE,
        "uncertainty_scope": ("paired image-level bootstrap; reference seed 0 only, so no "
                              "reference-seed uncertainty is included; K2 and K4 are reported "
                              "separately and never pooled"),
        "bootstrap": {"replicates_requested": args.bootstrap_replicates,
                      "seed": args.bootstrap_seed,
                      "budget_seconds": args.bootstrap_budget_seconds},
    }

    # ---- point estimates per K, primary methods
    point_rows: list[dict] = []
    per_category_rows: list[dict] = []
    for shot in shots:
        for method in PRIMARY_METHODS:
            if not all(units[shot][c].has(method) for c in units[shot]):
                continue
            per_cat = {c: units[shot][c].point_metrics(method) for c in units[shot]}
            aupro_values = []
            for c, unit in units[shot].items():
                for row in unit.metrics_rows:
                    if row["method"] == method:
                        value = as_float(row.get("pixel_aupro"))
                        if value is not None:
                            aupro_values.append(value)
            macro = macro_over_categories(list(per_cat.values()),
                                         ("pixel_ap", "pixel_auroc", "image_auroc", "image_ap"))
            point_rows.append({
                "shot": shot, "method_group": "primary", "method": method,
                "n_categories": len(per_cat),
                "macro_pixel_ap": macro["pixel_ap"], "macro_pixel_auroc": macro["pixel_auroc"],
                "macro_image_auroc": macro["image_auroc"], "macro_image_ap": macro["image_ap"],
                "macro_pixel_aupro": float(np.mean(aupro_values)) if aupro_values else None,
            })
            for c, values in sorted(per_cat.items()):
                per_category_rows.append({
                    "shot": shot, "method": method, "category": c,
                    "pixel_ap": values["pixel_ap"], "pixel_auroc": values["pixel_auroc"],
                    "image_auroc": values["image_auroc"], "image_ap": values["image_ap"],
                })
        # lambda sweep rows (fixed relaxation diagnostic only)
        for base, names in LAMBDA_BASES.items():
            for lam, name in zip(LAMBDA_VALUES, names):
                if not all(units[shot][c].has(name) for c in units[shot]):
                    continue
                per_cat = [units[shot][c].point_metrics(name) for c in units[shot]]
                macro = macro_over_categories(per_cat, ("pixel_ap", "pixel_auroc", "image_auroc", "image_ap"))
                point_rows.append({
                    "shot": shot, "method_group": "lambda_sweep", "method": f"{base}_lambda_{lam:.2f}",
                    "n_categories": len(per_cat),
                    "macro_pixel_ap": macro["pixel_ap"], "macro_pixel_auroc": macro["pixel_auroc"],
                    "macro_image_auroc": macro["image_auroc"], "macro_image_ap": macro["image_ap"],
                    "macro_pixel_aupro": None,
                })

    # ---- parity self-check of the recomputed point estimates against unit metrics.csv
    parity = []
    for shot in shots:
        for cat, unit in units[shot].items():
            for method in PRIMARY_METHODS + ["A1_L", "TRI_L", "BAL_L"]:
                if not unit.has(method):
                    continue
                for row in unit.metrics_rows:
                    if row["method"] != method:
                        continue
                    recomputed = unit.point_metrics(method)
                    for key in ("pixel_ap", "pixel_auroc", "image_auroc", "image_ap"):
                        stored = as_float(row.get(key))
                        if stored is None:
                            continue
                        parity.append({"shot": shot, "category": cat, "method": method, "metric": key,
                                       "abs_diff": abs(stored - recomputed[key])})
    out_json["point_estimate_parity"] = {
        "n_comparisons": len(parity),
        "max_abs_diff": max((p["abs_diff"] for p in parity), default=None),
        "tolerance": 5e-6,
        "pass": bool(all(p["abs_diff"] <= 5e-6 for p in parity)),
    }

    # ---- permutation seed variation (separate from the bootstrap)
    perm_rows: list[dict] = []
    perm_summary: list[dict] = []
    for shot in shots:
        for _, unit in sorted(units[shot].items()):
            perm_rows.extend(unit.perm_rows)
    perm_summary = summarise_permutation(perm_rows)

    # ---- bootstrap per K
    boot: dict[str, dict] = {}
    for shot in shots:
        available = [m for m in PRIMARY_METHODS
                     if all(units[shot][c].has(m) for c in units[shot])]
        if REFERENCE not in available or len(available) < 2:
            print(f"[analyze] K{shot}: not enough methods for a paired bootstrap", flush=True)
            continue
        print(f"[analyze] bootstrapping K{shot} with {len(available)} methods", flush=True)
        checkpoint = None
        if args.bootstrap_checkpoint_every:
            checkpoint = run_root / f"{args.tag}_bootstrap_k{shot}.npz"
        boot[f"k{shot}"] = bootstrap_macro(units[shot], available,
                                          args.bootstrap_replicates, args.bootstrap_seed,
                                          args.bootstrap_budget_seconds,
                                          checkpoint=checkpoint,
                                          checkpoint_every=args.bootstrap_checkpoint_every)
        print(f"[analyze] K{shot} bootstrap done in {boot[f'k{shot}']['seconds']}s "
              f"({boot[f'k{shot}']['replicates_used']} replicates, "
              f"equivalent={boot[f'k{shot}']['equivalent_methods']})", flush=True)
    out_json["bootstrap"]["per_k"] = boot

    # ---- G tails, regions, flips
    tails = g_tails(run_root, units, shots)
    regions = region_macro(units, shots)
    flips = flip_macro(units, shots)

    # ---- decision evidence
    decision = build_decision(boot, perm_summary, point_rows)
    out_json["decision"] = decision

    # ---- write everything
    write_csv(run_root / "analysis_point_by_k.csv",
              ["shot", "method_group", "method", "n_categories", "macro_pixel_ap", "macro_pixel_auroc",
               "macro_image_auroc", "macro_image_ap", "macro_pixel_aupro"], point_rows)
    write_csv(run_root / "analysis_per_category.csv",
              ["shot", "method", "category", "pixel_ap", "pixel_auroc", "image_auroc", "image_ap"],
              per_category_rows)
    write_csv(run_root / "analysis_perm_seed_variation.csv",
              ["shot", "kind", "branch", "base", "category", "seed", "method",
               "macro_pixel_ap", "delta_vs_base"], perm_rows)
    write_csv(run_root / "analysis_perm_seed_summary.csv",
              ["shot", "kind", "branch", "base", "category", "n_seeds", "mean_pixel_ap", "min_pixel_ap",
               "max_pixel_ap", "mean_delta", "min_delta", "max_delta", "std_delta",
               "frac_delta_below_zero"], perm_summary)
    write_csv(run_root / "analysis_g_tails.csv",
              ["shot", "category", "method", "image_class", "n_images", "mean_of_image_means",
               "p05_of_image_means", "p25_of_image_means", "median_of_image_means",
               "p75_of_image_means", "p95_of_image_means", "max_of_image_means",
               "mean_of_image_p95", "mean_of_image_max"], tails)
    write_csv(run_root / "analysis_region_macro.csv",
              ["shot", "category", "method", "image_index", "sample_id", "image_label", "region",
               "boundary_count", "patch_count", "mean", "p05", "p25", "median", "p75", "p95",
               "min", "max"], regions)
    write_csv(run_root / "analysis_flip_macro.csv",
              ["shot", "category", "method", "scope", "image_index", "sample_id", "n_pairs",
               "l_correct", "j_correct", "l_correct_j_wrong", "l_wrong_j_correct", "both_correct",
               "both_wrong", "l_tie", "j_tie", "any_tie", "both_tie", "l_correct_rate",
               "j_correct_rate", "l_correct_j_wrong_rate", "l_wrong_j_correct_rate"], flips)

    contrast_rows: list[dict] = []
    for shot in shots:
        payload = boot.get(f"k{shot}")
        if not payload:
            continue
        for method, metrics in payload["contrasts_vs_reference"].items():
            for metric, values in metrics.items():
                contrast_rows.append({"shot": shot, "contrast": f"{method} - {REFERENCE}", "metric": metric,
                                      **{k: v for k, v in values.items()}})
    write_csv(run_root / "analysis_paired_deltas.csv",
              ["shot", "contrast", "metric", "point_delta", "mean_delta", "ci_low", "ci_high",
               "fraction_below_zero", "n_replicates"], contrast_rows)

    out_json["point_estimates"] = point_rows
    out_json["permutation_seed_summary"] = perm_summary
    out_json["g_tail_rows"] = len(tails)
    out_json["region_rows"] = len(regions)
    out_json["flip_rows"] = len(flips)
    out_json["files"] = {name: str(run_root / name) for name in (
        "analysis_point_by_k.csv", "analysis_per_category.csv", "analysis_perm_seed_variation.csv",
        "analysis_perm_seed_summary.csv", "analysis_g_tails.csv", "analysis_region_macro.csv",
        "analysis_flip_macro.csv", "analysis_paired_deltas.csv")}
    (run_root / f"{args.tag}.json").write_text(
        json.dumps(out_json, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    (run_root / f"{args.tag}_CN.md").write_text(
        render_markdown(out_json, point_rows, perm_summary), encoding="utf-8")
    print(f"[analyze] wrote {run_root / (args.tag + '.json')} and {run_root / (args.tag + '_CN.md')}",
          flush=True)
    return 0


def build_decision(boot: dict, perm_summary: list[dict], point_rows: list[dict]) -> dict:
    """Apply the handover document's evidence routing without over-claiming."""
    evidence: dict = {"weight_control": {}, "pairing_intervention": {}, "relaxation": {}}
    for key, payload in boot.items():
        shot = int(key.lstrip("k"))
        contrasts = payload["contrasts_vs_reference"]
        block: dict = {}
        for method in ("DUP_J", "TRI_J", "BAL_J", "DUP_BAL_J", "DUP_EXPECTED_J", "S", "C", "B"):
            values = contrasts.get(method, {}).get("pixel_ap")
            if values is None:
                continue
            block[method] = {
                "point_delta_macro_pixel_ap": values["point_delta"],
                "ci_low": values["ci_low"], "ci_high": values["ci_high"],
                "fraction_below_zero": values["fraction_below_zero"],
                "exceeds_effect_scale": bool(abs(values["point_delta"]) >= EFFECT_SCALE),
                "ci_excludes_zero": bool(values["ci_low"] is not None and
                                         (values["ci_low"] > 0 or values["ci_high"] < 0)),
            }
        evidence["weight_control"][f"k{shot}"] = block
    grouped: dict = {}
    for row in perm_summary:
        key = f"k{row['shot']}_{row['kind']}"
        grouped.setdefault(key, []).append(row)
    for key, rows in sorted(grouped.items()):
        deltas = [r["mean_delta"] for r in rows if r["mean_delta"] is not None]
        evidence["pairing_intervention"][key] = {
            "n_category_seed_groups": len(rows),
            "mean_of_mean_delta": float(np.mean(deltas)) if deltas else None,
            "min_mean_delta": float(np.min(deltas)) if deltas else None,
            "max_mean_delta": float(np.max(deltas)) if deltas else None,
            "note": ("within = full spatial permutation inside each reference image; "
                     "cross = image-identity permutation at fixed patch position; "
                     "these are reference-row interventions, not new data"),
        }
    relaxation: dict = {}
    for row in point_rows:
        if row["method_group"] != "lambda_sweep":
            continue
        base = row["method"].split("_lambda_")[0]
        relaxation.setdefault(f"k{row['shot']}", {}).setdefault(base, {})[
            row["method"].split("_lambda_")[1]] = row["macro_pixel_ap"]
    evidence["relaxation"] = relaxation
    return evidence


def render_markdown(payload: dict, point_rows: list[dict], perm_summary: list[dict]) -> str:
    lines = ["# 参考耦合机制试探：P4 汇总分析", "",
             f"运行根目录：`{payload['run_root']}`", "",
             f"- 类别覆盖：{payload['coverage']}",
             f"- 参照方法：`{payload['reference_method']}`；实用效应参考尺度：宏 P-AP {payload['effect_scale_macro_pixel_ap']}",
             f"- 不确定性口径：{payload['uncertainty_scope']}", ""]
    parity = payload.get("point_estimate_parity", {})
    lines += ["## 实现自检", "",
              f"- 重算点估计与各单元 `metrics.csv` 的最大绝对差：{parity.get('max_abs_diff')}"
              f"（容限 {parity.get('tolerance')}，通过={parity.get('pass')}）", ""]
    lines += ["## 每 K 的宏指标（点估计）", "",
              "| K | 方法 | 组 | 宏 P-AP | 宏 P-AUROC | 宏 P-AUPRO | 宏 I-AUROC | 宏 I-AP |",
              "|---|---|---|---:|---:|---:|---:|---:|"]
    for row in point_rows:
        lines.append(f"| {row['shot']} | {row['method']} | {row['method_group']} | "
                     f"{_fmt(row['macro_pixel_ap'])} | {_fmt(row['macro_pixel_auroc'])} | "
                     f"{_fmt(row.get('macro_pixel_aupro'))} | {_fmt(row['macro_image_auroc'])} | "
                     f"{_fmt(row['macro_image_ap'])} |")
    boot = payload.get("bootstrap", {}).get("per_k", {})
    lines += ["", "## 配对 bootstrap（图像为重采样单位，与 A1_J 对照）", "",
              "| K | 对照 | 指标 | 点差 | 95% 区间 | 差值<0 的复制比例 | 复制数 |",
              "|---|---|---|---:|---|---:|---:|"]
    for key, block in sorted(boot.items()):
        for method, metrics in block["contrasts_vs_reference"].items():
            for metric in ("pixel_ap", "image_auroc"):
                values = metrics.get(metric)
                if values is None:
                    continue
                lines.append(f"| {key} | {method} − A1_J | {metric} | "
                             f"{_fmt(values['point_delta'])} | "
                             f"[{_fmt(values['ci_low'])}, {_fmt(values['ci_high'])}] | "
                             f"{_fmt(values['fraction_below_zero'])} | {values['n_replicates']} |")
    lines += ["", f"复制数实际使用：{ {k: v.get('replicates_used') for k, v in boot.items()} }", ""]
    aliases = {k: v.get("equivalent_methods", {}) for k, v in boot.items()}
    lines += [f"位精确等价的重复方法（其 bootstrap 复用同一对照，不重复计算）：{aliases}", "",
              "每个复制由 `[seed, shot, 复制序号]` 独立播种，可按复制复现；中断后从检查点续跑，",
              "不改变重采样单位、配对方式或样本数。", ""]
    lines += ["## 置换种子变异（与 bootstrap 分开汇报，不并入重采样）", "",
              "| K | 类别 | 类型 | 置换支 | 基线 | 种子数 | 均值 ΔP-AP | 最小 ΔP-AP | 最大 ΔP-AP | Δ<0 比例 |",
              "|---|---|---|---|---|---:|---:|---:|---:|---:|"]
    for row in perm_summary:
        lines.append(f"| {row['shot']} | {row['category']} | {row['kind']} | {row['branch']} | "
                     f"{row['base']} | {row['n_seeds']} | {_fmt(row['mean_delta'])} | "
                     f"{_fmt(row['min_delta'])} | {_fmt(row['max_delta'])} | "
                     f"{_fmt(row['frac_delta_below_zero'])} |")
    lines += ["## 证据分流（交接文档 §9）", "", "```json",
              json.dumps(payload.get("decision", {}), ensure_ascii=False, indent=2), "```", ""]
    lines += ["## 本轮允许与不允许的结论", "",
              "- 允许：报告上述宏指标、逐类方向、K2/K4 各自结果与配对差值区间。",
              "- 允许：把参考行置换后的变化解释为“评分依赖经验对应关系”的证据。",
              "- 不允许：把置换敏感性直接写成原始系统已经失败。",
              "- 不允许：把 K2/K4 当作独立 seed 或独立数据集，或声称跨 seed/跨域确认。",
              "- 不允许：把 λ 插值的最优值改称为新方法（本轮不使用测试标签调参）。",
              "- 不允许：用本轮结果宣称普适失效机制、准确率上限或可预测边界。", ""]
    return "\n".join(lines)


def _fmt(value) -> str:
    if value is None:
        return ""
    return f"{value:.5f}"


if __name__ == "__main__":
    raise SystemExit(main())
