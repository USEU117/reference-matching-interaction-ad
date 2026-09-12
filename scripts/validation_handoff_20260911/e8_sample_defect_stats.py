"""E8-4: sample-size / image-size / defect-area statistics from the real split and GT.

Reads the frozen MPDD split manifest and the real MPDD test ground truth, and
reports per-category:

* numbers of test / normal / anomalous images,
* native image sizes and ground-truth mask sizes,
* defect-area statistics at native resolution (px, fraction of image,
  connected components), including how many defects are smaller than one
  canonical 448-grid cell and smaller than one stride-8 evaluation cell.

It also cross-checks the counted sample numbers against the prediction coverage
recorded by E2 (metrics_per_category.csv) so the report can state that
"sample counts agree with prediction coverage".

Nothing here is used to select a configuration; it is description of the
evaluation set only. Maps are never touched.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import common as C  # noqa: E402
from v2_mpdd_prediction_common import index_dataset  # noqa: E402

E8 = C.OUT_ROOT / "E8"
DATA_ROOT = C.ROOT / "data" / "mpdd_raw" / "MPDD"
MANIFEST = C.SPLITS / "mpdd" / "manifest.json"

# MPDD images are 1024x1024.  One canonical grid cell of the 32x32 grid covers
# 1024/32 = 32 native px per side (1024 native px^2).  One stride-8 cell of the
# 448x448 map covers 8*1024/448 ~ 18.29 native px per side (~334 native px^2).
NATIVE_PX_PER_GRID_CELL = 1024 / 32
NATIVE_PX_PER_STRIDE_CELL = C.STRIDE * 1024 / 448


def _components(mask: np.ndarray) -> list[int]:
    from skimage import measure
    lab = measure.label(mask.astype(bool))
    if lab.max() == 0:
        return []
    return [int((lab == i).sum()) for i in range(1, int(lab.max()) + 1)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path, default=DATA_ROOT)
    args = ap.parse_args()

    indexed = index_dataset("mpdd", args.data_root)
    rows: list[dict] = []
    all_areas: list[int] = []
    all_comp: list[int] = []

    for category in sorted(indexed):
        samples = indexed[category]
        n_test = len(samples)
        n_anom = sum(s.label for s in samples)
        n_normal = n_test - n_anom

        img_sizes, mask_sizes = set(), set()
        areas: list[int] = []
        fracs: list[float] = []
        comps: list[int] = []
        small_grid = 0
        small_stride = 0
        for s in samples:
            with Image.open(s.image_path) as im:
                img_sizes.add(tuple(im.size))
            if s.mask_path is None:
                continue
            with Image.open(s.mask_path) as im:
                mask_sizes.add(tuple(im.size))
                m = (np.asarray(im) > 0).astype(np.uint8)
            area = int(m.sum())
            frac = area / float(m.size)
            comp_sizes = _components(m)
            areas.append(area)
            fracs.append(frac)
            comps.append(len(comp_sizes))
            all_areas.append(area)
            all_comp.extend(comp_sizes)
            if comp_sizes:
                if min(comp_sizes) < NATIVE_PX_PER_GRID_CELL ** 2:
                    small_grid += 1
                if min(comp_sizes) < NATIVE_PX_PER_STRIDE_CELL ** 2:
                    small_stride += 1

        def _q(v, p):
            return float(np.percentile(v, p)) if v else float("nan")

        rows.append({
            "category": category,
            "n_test": n_test, "n_normal": n_normal, "n_anomalous": n_anom,
            "n_defect_images": len(areas),
            "image_sizes": ";".join(f"{w}x{h}" for w, h in sorted(img_sizes)),
            "mask_sizes": ";".join(f"{w}x{h}" for w, h in sorted(mask_sizes)),
            "defect_area_px_min": int(min(areas)) if areas else 0,
            "defect_area_px_p25": int(_q(areas, 25)),
            "defect_area_px_median": int(_q(areas, 50)),
            "defect_area_px_mean": float(np.mean(areas)) if areas else 0.0,
            "defect_area_px_p75": int(_q(areas, 75)),
            "defect_area_px_max": int(max(areas)) if areas else 0,
            "defect_frac_min": float(min(fracs)) if fracs else 0.0,
            "defect_frac_median": float(np.median(fracs)) if fracs else 0.0,
            "defect_frac_max": float(max(fracs)) if fracs else 0.0,
            "n_components_mean": float(np.mean(comps)) if comps else 0.0,
            "n_components_max": int(max(comps)) if comps else 0,
            "n_defect_images_smaller_than_one_grid_cell": int(small_grid),
            "n_defect_images_smaller_than_one_stride8_cell": int(small_stride),
        })

    # cross-check against E2 prediction coverage
    e2 = C.OUT_ROOT / "E2" / "metrics_per_category.csv"
    coverage = []
    if e2.exists():
        with e2.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                coverage.append(r)
    cov_by_key = {}
    for r in coverage:
        cov_by_key.setdefault((int(r["shot"]), r["category"]), set()).add(int(r["n_test"]))

    cov_rows = []
    mismatches = []
    for shot in (2, 4):
        for row in rows:
            key = (shot, row["category"])
            observed = sorted(cov_by_key.get(key, set()))
            ok = observed == [row["n_test"]]
            if not ok:
                mismatches.append({"shot": shot, "category": row["category"],
                                   "counted": row["n_test"], "predicted": observed})
            cov_rows.append({"shot": shot, "category": row["category"],
                             "counted_n_test": row["n_test"], "predicted_n_test": observed,
                             "match": ok})

    summary = {
        "created_utc": C.utcnow(),
        "dataset": "mpdd",
        "dataset_role": "development",
        "data_root": str(args.data_root),
        "manifest": str(MANIFEST),
        "manifest_sha256": C.sha256_file(MANIFEST) if MANIFEST.exists() else None,
        "n_categories": len(rows),
        "n_test_total": int(sum(r["n_test"] for r in rows)),
        "n_anomalous_total": int(sum(r["n_anomalous"] for r in rows)),
        "n_normal_total": int(sum(r["n_normal"] for r in rows)),
        "defect_area_px_median_all": float(np.median(all_areas)) if all_areas else 0.0,
        "defect_area_px_min_all": int(min(all_areas)) if all_areas else 0,
        "defect_component_px_min_all": int(min(all_comp)) if all_comp else 0,
        "defect_component_px_median_all": float(np.median(all_comp)) if all_comp else 0.0,
        "n_components_total": len(all_comp),
        "n_components_smaller_than_one_grid_cell": int(sum(
            1 for a in all_comp if a < NATIVE_PX_PER_GRID_CELL ** 2)),
        "n_components_smaller_than_one_stride8_cell": int(sum(
            1 for a in all_comp if a < NATIVE_PX_PER_STRIDE_CELL ** 2)),
        "native_px_per_grid_cell": NATIVE_PX_PER_GRID_CELL ** 2,
        "native_px_per_stride8_cell": NATIVE_PX_PER_STRIDE_CELL ** 2,
        "coverage_mismatches": mismatches,
        "coverage_consistent": not mismatches,
        "note": ("Defect areas are computed on the native-resolution ground-truth masks; "
                 "the canonical evaluation grid coarsens them to 32x32 (and stride=8 to 56x56). "
                 "Pixel AP is a ranking metric over the coarsened grid: a high AP shows the "
                 "score ranks labelled defect cells above labelled normal cells on this set, "
                 "it does not prove the score is the uniquely optimal ordering, nor that "
                 "sub-grid-scale defects are resolved. Sample counts here equal the E2 "
                 "prediction coverage, so AP is computed over the whole split."),
    }

    E8.mkdir(parents=True, exist_ok=True)
    with (E8 / "sample_defect_stats_per_category.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with (E8 / "prediction_coverage_check.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["shot", "category", "counted_n_test",
                                           "predicted_n_test", "match"], extrasaction="ignore")
        w.writeheader()
        w.writerows(cov_rows)
    C.write_json(E8 / "sample_defect_stats_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
