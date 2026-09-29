"""Step 4: redraw Figure S8 for five seeds and emit the numbers the text needs.

Inputs are the assembled five-seed table (step 3).  Outputs are new files only:

    docs/five_seed_support_variance_20260928/figures/figS8_five_seed_part{1,2}.{png,pdf}
    docs/five_seed_support_variance_20260928/stability_audit_five_seed.json
    docs/five_seed_support_variance_20260928/stability_per_seed_five_seed.csv
    docs/five_seed_support_variance_20260928/manuscript_numbers_five_seed.json

The archived two-seed figure, its audit JSON and the frozen manuscript are not touched;
the manuscript revision that consumes these files is built by step 5.

Usage:
    python scripts/five_seed_support_variance_20260928/step4_paper_assets.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import fsv_common as P  # noqa: E402

FIVE_SEED_TABLE = P.WS / "five_seed/baseline_common_region_five_seed.csv"
MACRO = P.WS / "five_seed/per_seed_macro.csv"
OUT = P.ROOT / "docs/five_seed_support_variance_20260928"
FIGS = OUT / "figures"
METHOD_LABELS = {
    "controlled_A1_J": "Dual-encoder baseline · Joint matching",
    "controlled_A1_L": "Dual-encoder baseline · Independent matching",
    "anomalydino_canvas": "AnomalyDINO canvas",
    "anomalydino_canvas_rotation": "AnomalyDINO canvas + rotation",
    "PatchCore_native_local128": "PatchCore native 128",
    "PatchCore_native_official224": "PatchCore official 224",
    "SubspaceAD_native_fp16": "SubspaceAD native 256",
    "WinCLIP_native_240": "WinCLIP+ native 240",
}
SEED_STYLE = {0: ("o", "#28618A", "Seed 0"), 1: ("s", "#A5453B", "Seed 1"),
              2: ("^", "#4D7C3F", "Seed 2"), 3: ("D", "#8B6C1F", "Seed 3"),
              4: ("v", "#6A4C93", "Seed 4")}
DATASET_TITLE = {"mvtec": "MVTec AD", "visa": "VisA"}


def macro_index(rows: list[dict]) -> dict:
    return {(r["dataset"], r["method"], int(r["seed"])): float(r["macro_pixel_ap"])
            for r in rows}


def spread(values: list[float]) -> float:
    return 100 * (max(values) - min(values))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-audit", type=Path,
                    default=P.ROOT / "docs/paper_evidence_completion_20260927/stability_audit.json")
    args = ap.parse_args()
    FIGS.mkdir(parents=True, exist_ok=True)

    rows = P.read_csv(MACRO)
    if not rows:
        raise SystemExit(f"missing {MACRO}: run step3_assemble.py first")
    macro = macro_index(rows)
    datasets = P.DATASETS
    methods = list(METHOD_LABELS)

    # ---------------------------------------------------------------- audit numbers
    gaps = []
    for dataset in datasets:
        for method in methods:
            values = {seed: macro[(dataset, method, seed)] for seed in P.SEEDS}
            one_two = [values[0], values[1]]
            gaps.append({
                "dataset": dataset, "method": method,
                "macro_pixel_ap": {f"seed_{s}": v for s, v in values.items()},
                "range_pp_five_seed": spread(list(values.values())),
                "range_pp_seeds_0_1": spread(one_two),
                "signed_change_pp_seeds_0_1": 100 * (values[1] - values[0]),
                "seed_min": min(values, key=values.get), "seed_max": max(values, key=values.get),
                "mean_macro_pixel_ap": sum(values.values()) / len(values),
            })
    five = [g["range_pp_five_seed"] for g in gaps]
    two = [g["range_pp_seeds_0_1"] for g in gaps]
    old = P.read_json(args.old_audit) if args.old_audit.exists() else None
    old_max = old["maximum_observed_difference"]["absolute_change_pp"] if old else None
    old_min = old["minimum_observed_difference_pp"] if old else None
    consistency = None
    if old is not None:
        consistency = {"old_min_pp": old_min, "new_two_seed_min_pp": min(two),
                       "old_max_pp": old_max, "new_two_seed_max_pp": max(two),
                       "matches": bool(abs(old_min - min(two)) < 1e-9
                                       and abs(old_max - max(two)) < 1e-9)}
    sorted_five = sorted(five)
    audit = {
        "created_utc": P.utcnow(),
        "kind": "five_seed_support_variance_audit",
        "source": str(FIVE_SEED_TABLE.relative_to(P.ROOT)),
        "source_sha256": P.sha256_file(FIVE_SEED_TABLE),
        "metric_rows_used": len(P.read_csv(FIVE_SEED_TABLE)),
        "macro_points": len(gaps),
        "seeds": P.SEEDS, "support_budget": P.SHOT,
        "datasets": datasets, "methods": methods,
        "metric": ("equal-category macro pixel AP under the archived common-valid-region "
                   "convention"),
        "excluded_method": P.EXCLUDED_METHOD,
        "exclusion": "AnomalyCLIP zero-shot has no support set; support-seed variation is not "
                     "applicable to it",
        "range_pp_five_seed": {
            "minimum": sorted_five[0], "maximum": sorted_five[-1],
            "median": sorted_five[len(sorted_five) // 2],
            "maximum_at": max(gaps, key=lambda g: g["range_pp_five_seed"]),
            "minimum_at": min(gaps, key=lambda g: g["range_pp_five_seed"]),
        },
        "range_pp_seeds_0_1": {
            "minimum": min(two), "maximum": max(two),
            "maximum_at": max(gaps, key=lambda g: g["range_pp_seeds_0_1"]),
        },
        "two_seed_reference_consistency": consistency,
        "estimand": ("observed seed-associated configuration difference; support selection and "
                     "any seed-dependent implementation randomness are not separately "
                     "identified"),
        "seed_dependent_randomness": (
            "PatchCore coreset subsampling is seeded by the support seed (vendored "
            "fix_seeds(seed)); other seed-dependent implementation randomness is recorded by "
            "each runner but not separately identified from support selection"),
        "not_claimed": ["population variance",
                        "confidence interval over support sets",
                        "method stability ranking",
                        "optimal or recommended configuration"],
        "per_dataset_method": gaps,
        "frozen_sources_written": False,
    }
    P.write_json(OUT / "stability_audit_five_seed.json", audit)
    P.write_csv(OUT / "stability_per_seed_five_seed.csv", rows)

    numbers = {
        "created_utc": P.utcnow(),
        "n_dataset_configuration_pairs": len(gaps),
        "n_seeds": len(P.SEEDS),
        "metric_rows_used": audit["metric_rows_used"],
        "five_seed_range_pp_min": sorted_five[0],
        "five_seed_range_pp_max": sorted_five[-1],
        "five_seed_range_pp_median": sorted_five[len(sorted_five) // 2],
        "five_seed_range_pp_max_at": {"dataset": audit["range_pp_five_seed"]["maximum_at"]["dataset"],
                                      "method": audit["range_pp_five_seed"]["maximum_at"]["method"],
                                      "range_pp": audit["range_pp_five_seed"]["maximum_at"]["range_pp_five_seed"]},
        "five_seed_range_pp_min_at": {"dataset": audit["range_pp_five_seed"]["minimum_at"]["dataset"],
                                      "method": audit["range_pp_five_seed"]["minimum_at"]["method"],
                                      "range_pp": audit["range_pp_five_seed"]["minimum_at"]["range_pp_five_seed"]},
        "seeds_0_1_range_pp_min": min(two),
        "seeds_0_1_range_pp_max": max(two),
        "seeds_0_1_max_at": {"dataset": audit["range_pp_seeds_0_1"]["maximum_at"]["dataset"],
                             "method": audit["range_pp_seeds_0_1"]["maximum_at"]["method"]},
        "two_seed_reference": {"min_pp": old_min, "max_pp": old_max,
                               "consistency": consistency},
        "mean_range_pp_by_dataset": {
            ds: sum(g["range_pp_five_seed"] for g in gaps if g["dataset"] == ds)
                / sum(1 for g in gaps if g["dataset"] == ds) for ds in datasets},
        "max_range_pp_by_dataset": {
            ds: max(g["range_pp_five_seed"] for g in gaps if g["dataset"] == ds)
            for ds in datasets},
    }
    P.write_json(OUT / "manuscript_numbers_five_seed.json", numbers)

    # ------------------------------------------------------------------- figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11.5,
                         "axes.spines.top": False, "axes.spines.right": False})
    pages = {1: ["mpdd", "btad"], 2: ["mvtec", "visa"]}
    for page, page_datasets in pages.items():
        fig, axs = plt.subplots(2, 1, figsize=(17 / 2.54, 18 / 2.54))
        fig.subplots_adjust(left=.49, right=.965, top=.92, bottom=.085, hspace=.5)
        for ax, dataset in zip(axs, page_datasets):
            for i, method in enumerate(methods):
                values = [macro[(dataset, method, seed)] for seed in P.SEEDS]
                y = 7 - i
                ax.plot([min(values), max(values)], [y, y], color="#969696", lw=1.2, zorder=1)
                for seed in P.SEEDS:
                    marker, colour, label = SEED_STYLE[seed]
                    ax.plot(macro[(dataset, method, seed)], y, marker, color=colour,
                            ms=4.5 if seed < 2 else 4.0,
                            label=label if i == 0 else None)
            ax.set_yticks(range(8), list(METHOD_LABELS.values())[::-1], fontsize=11.5)
            ax.set_ylim(-.5, 7.5)
            ax.set_xlim(0, .85)
            ax.set_xticks([0, .2, .4, .6, .8])
            ax.set_xlabel("Macro pixel AP")
            ax.set_title(DATASET_TITLE.get(dataset, dataset.upper()), loc="left",
                         fontweight="bold")
            ax.grid(axis="x", alpha=.2)
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper center", ncol=5, frameon=False)
        for ext in ("png", "pdf"):
            fig.savefig(FIGS / f"figS8_five_seed_part{page}.{ext}", dpi=350)
        plt.close(fig)

    print(f"figure: {FIGS / 'figS8_five_seed_part1.png'} (+part2, png+pdf)")
    print(f"audit : {OUT / 'stability_audit_five_seed.json'}")
    print(f"five-seed range over {len(gaps)} dataset-configuration pairs: "
          f"{sorted_five[0]:.3f} to {sorted_five[-1]:.3f} pp (median "
          f"{sorted_five[len(sorted_five) // 2]:.3f})")
    if consistency is not None:
        print(f"two-seed subset reproduces the archived audit: {consistency['matches']} "
              f"({min(two):.6f}..{max(two):.6f} pp vs {old_min:.6f}..{old_max:.6f} pp)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
