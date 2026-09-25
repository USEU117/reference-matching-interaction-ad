"""Read-only: summarise the A04 products."""
from __future__ import annotations

import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
D = ROOT / "experiments/prereg_20260924/out/A04"


def fnum(v):
    return None if v in (None, "") else float(v)


def r6(v):
    return None if v is None else round(v, 6)


for path in sorted(D.iterdir()):
    if path.is_file():
        print(path.name, path.stat().st_size)

points = list(csv.DictReader((D / "A04_point_values.csv").open(encoding="utf-8-sig")))
stability = list(csv.DictReader((D / "A04_stability.csv").open(encoding="utf-8-sig")))
cross = list(csv.DictReader((D / "A04_cross_config.csv").open(encoding="utf-8-sig")))
print()
print("point rows", len(points), "fields", list(points[0].keys()))
print("stability rows", len(stability), "fields", list(stability[0].keys()))
print("cross rows", len(cross), "fields", list(cross[0].keys()))
print()
print("== geometry perturbation ==")
for r in stability:
    if not r["perturbation"].startswith("input_geometry"):
        continue
    print(f"{r['dataset']:<5} s{r['seed']}k{r['shot']} {r['config']:<30} "
          f"point={r6(fnum(r['point_delta']))} boot={r6(fnum(r['bootstrap_mean']))} "
          f"ci95=[{r6(fnum(r['ci95_low']))},{r6(fnum(r['ci95_high']))}] "
          f"excl={r['ci95_excludes_zero']} fam={r6(fnum(r['ci_family_low']))},"
          f"{r6(fnum(r['ci_family_high']))} fam_excl={r['ci_family_excludes_zero']} "
          f"n={r['n_category_units']}")
print()
print("== reference augmentation ==")
for r in stability:
    if r["perturbation"].startswith("input_geometry"):
        continue
    print(f"{r['perturbation']:<62} {r['dataset']} s{r['seed']}k{r['shot']} "
          f"boot={r6(fnum(r['bootstrap_mean']))} "
          f"ci95=[{r6(fnum(r['ci95_low']))},{r6(fnum(r['ci95_high']))}] "
          f"excl={r['ci95_excludes_zero']}")
print()
print("== cross-config ==")
for r in cross:
    print(f"{r['dataset']} s{r['seed']}k{r['shot']} n={r['n_configs']} "
          f"defined={r['n_configs_with_defined_interval']} "
          f"same_dir={r['all_configs_same_direction']} "
          f"pos={r['n_configs_point_positive']} excl95={r['n_configs_interval_excludes_zero_95']} "
          f"mean={r6(fnum(r['mean_of_config_bootstrap_deltas']))}")
    print("     ", r["config_deltas"])
    if r["undecided_configs"] not in ("[]", ""):
        print("      undecided:", r["undecided_configs"])
print()
checks = json.load((D / "A04_checks.json").open(encoding="utf-8"))
print("parity:", r6(checks["parity_common_region_vs_frozen_table"]["max_abs_delta"]),
      "rows", checks["parity_common_region_vs_frozen_table"]["rows_compared"],
      "pass", checks["parity_common_region_vs_frozen_table"]["pass_1e_6"])
nat = checks["native_frame_vs_registered_artifact"]
print("native diagnostic rows", len(nat["rows"]), "max", r6(nat["max_abs_delta"]))
for row in nat["rows"]:
    print("   ", row["config"], row["dataset"], "s"+str(row["seed"]), "k"+str(row["shot"]),
          "mine", r6(row["mine_macro_pixel_ap"]), "artifact",
          r6(row["artifact_macro_pixel_ap"]), "abs", r6(row["abs_delta"]))
print("missing:", checks["missing"][:10])
