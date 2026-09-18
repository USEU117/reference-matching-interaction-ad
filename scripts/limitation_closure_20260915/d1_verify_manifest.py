"""D1 gate: independently verify the seed 3..7 support manifest.

`build_support_manifest.py` writes its own `prefix_checks`, but for seeds 3..7 there is no
historical entry to check against, so its self-report is the only evidence - which is exactly what
a gate must not rely on.  This script therefore re-derives the manifest from the raw dataset
directories with its own directory walk and its own shuffle, and separately checks that the
manifest still agrees with the frozen study manifest for seeds 0..2.

Checks
  VD.1a  independent re-derivation: for every (dataset, category, seed) the manifest's K=1/2/4/8
         lists equal `sorted(train normal images)[random.Random(seed).shuffle()][:K]`
  VD.1b  prefix nesting inside the manifest: K1 == K8[:1], K2 == K8[:2], K4 == K8[:4]
  VD.1c  no duplicate reference inside a K=8 list, and K8 is a subset of the candidate pool
  VD.1d  seeds 0..2 agree with the frozen study manifest (`p0_support/support_manifest_*.json`)
  VD.1e  the manifest records exactly the seeds that have no history

Outputs `seeds_extension_20260917/VD1_MANIFEST.json`.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
FROZEN = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913/p0_support"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
SHOTS = [1, 2, 4, 8]
SEEDS = [0, 1, 2, 3, 4, 5, 6, 7]
HISTORICAL_SEEDS = [0, 1, 2]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def independent_candidates(root: Path, category: str) -> list[str]:
    """Its own walk of the category's normal training images (no shared helper with the builder)."""
    for name in ("good", "ok"):
        base = root / category / "train" / name
        if not base.is_dir():
            continue
        found = [p for p in base.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
        return [p.relative_to(root).as_posix() for p in sorted(found)]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=EXT / "VD1_MANIFEST.json")
    parser.add_argument("--datasets", nargs="+", default=["mpdd", "btad"])
    args = parser.parse_args()

    checks, failures, per_dataset = [], [], {}
    for dataset in args.datasets:
        path = EXT / "p0_support" / f"support_manifest_{dataset}.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        split = json.loads((ROOT / "data/splits" / dataset / "manifest.json").read_text(
            encoding="utf-8"))
        root = Path(manifest["root"])
        frozen_path = FROZEN / f"support_manifest_{dataset}.json"
        frozen = (json.loads(frozen_path.read_text(encoding="utf-8"))
                  if frozen_path.exists() else None)

        rederived_ok, nesting_ok, unique_ok, frozen_ok = 0, 0, 0, 0
        n_units = 0
        for category in sorted(manifest["categories"]):
            pool = independent_candidates(root, category)
            if not pool:
                failures.append(f"{dataset}/{category}: independent walk found no normal images")
            for seed in SEEDS:
                n_units += 1
                listed = manifest["categories"][category][str(seed)]
                shuffled = pool[:]
                random.Random(seed).shuffle(shuffled)
                expected = {str(k): shuffled[:k] for k in SHOTS}
                if all(list(listed[str(k)]) == expected[str(k)] for k in SHOTS):
                    rederived_ok += 1
                else:
                    failures.append(f"{dataset}/{category}/s{seed}: re-derivation mismatch")

                k8 = list(listed["8"])
                if all(k8[:k] == list(listed[str(k)]) for k in SHOTS):
                    nesting_ok += 1
                else:
                    failures.append(f"{dataset}/{category}/s{seed}: K nesting broken")

                if len(set(k8)) == len(k8) and set(k8) <= set(pool):
                    unique_ok += 1
                else:
                    failures.append(f"{dataset}/{category}/s{seed}: K8 has duplicates or "
                                    f"out-of-pool entries")

                if seed in HISTORICAL_SEEDS and frozen is not None:
                    reference = frozen["categories"][category].get(str(seed))
                    if reference is None or all(list(listed[str(k)]) == list(reference[str(k)])
                                                for k in SHOTS):
                        frozen_ok += 1
                    else:
                        failures.append(f"{dataset}/{category}/s{seed}: drifted from the frozen "
                                        f"study manifest")

        per_dataset[dataset] = {
            "manifest": str(path),
            "manifest_sha256": manifest.get("sha256") or None,
            "units_checked": n_units,
            "independent_rederivation_ok": rederived_ok,
            "prefix_nesting_ok": nesting_ok,
            "unique_and_in_pool_ok": unique_ok,
            "historical_seeds_match_frozen": frozen_ok,
            "historical_seeds_checked": sum(1 for _ in HISTORICAL_SEEDS
                                            for _ in manifest["categories"]),
            "build_prefix_invariance_all_match": manifest.get("prefix_invariance_all_match"),
            "build_n_prefix_checks": manifest.get("n_prefix_checks"),
            "seeds_without_history_recorded": manifest.get("n_seeds_without_history"),
            "seeds_without_history_expected": (len(manifest["categories"])
                                               * len([s for s in SEEDS
                                                      if s not in HISTORICAL_SEEDS])),
            "candidate_file_sha256_entries": len(manifest.get("selected_file_sha256", {})),
            "dataset_splits_root": split.get("root"),
        }
        expected_units = len(manifest["categories"]) * len(SEEDS)
        if n_units != expected_units:
            failures.append(f"{dataset}: checked {n_units} units, expected {expected_units}")
        if manifest.get("n_seeds_without_history") != per_dataset[dataset][
                "seeds_without_history_expected"]:
            failures.append(f"{dataset}: seeds_without_history count mismatch")

    report = {
        "created_utc": utcnow(),
        "gate": "VD.1 prefix nesting and independent re-derivation of the seed 3..7 manifest",
        "datasets": per_dataset,
        "failures": failures,
        "pass": not failures,
        "note": ("the builder's own prefix_checks cover seeds 0..2 only; this gate re-derives every "
                 "list from the raw directories so that seeds 3..7 are not verified solely by the "
                 "script that produced them"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("pass", "failures")}, ensure_ascii=False, indent=2))
    for dataset, block in per_dataset.items():
        print(f"[D1] {dataset}: units={block['units_checked']} "
              f"rederived={block['independent_rederivation_ok']} "
              f"nesting={block['prefix_nesting_ok']} "
              f"unique={block['unique_and_in_pool_ok']} "
              f"frozen_match={block['historical_seeds_match_frozen']} "
              f"no_history={block['seeds_without_history_recorded']}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
