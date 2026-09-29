"""Step 1: build the five-seed (0..4) splits + K-extended support manifests.

Everything is written into the new work area
`experiments/dynamic_fusion/five_seed_support_variance_20260928/`
(`splits/`, `support_manifests/`); no frozen manifest under `data/splits` or any
existing experiment directory is modified.

Producers (both standard-library only, invoked as subprocesses):

* `scripts/prepare_splits.py` -- deterministic nested K-shot manifests
  (`sorted normal candidates -> random.Random(seed).shuffle -> prefix`), so the
  seeds 0..2 selections are byte-identical to the frozen `data/splits` manifests;
  seeds 3..4 extend the same rule.
* `scripts/unified_fusion_paper_support_v1/build_support_manifest.py` -- K=8
  extension with an explicit prefix-invariance check against the frozen source
  manifest (seeds without history are recorded, not silently accepted).

Usage:
    python scripts/five_seed_support_variance_20260928/step1_manifests.py
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WS = ROOT / "experiments/dynamic_fusion/five_seed_support_variance_20260928"
SPLITS_OUT = WS / "splits"
SUPPORT_OUT = WS / "support_manifests"
FROZEN_SPLITS = ROOT / "data/splits"
EXTSEED_SUPPORT = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917/p0_support"

DATASETS = {
    "mpdd": ROOT / "data/mpdd_raw/MPDD",
    "btad": ROOT / "data/btad_raw/BTech_Dataset_transformed",
    "mvtec": ROOT / "data/mvtec",
    "visa": ROOT / "data/visa_raw",
}
SEEDS = [0, 1, 2, 3, 4]
SPLIT_SHOTS = [1, 2, 4]
SUPPORT_SHOTS = [1, 2, 4, 8]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args: list[str]) -> None:
    proc = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(args)}\n"
                         f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    tail = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout.strip() else ""
    print(f"  ok: {tail}")


def check_seed_prefix(new: dict, frozen: dict) -> list[dict]:
    """Seeds 0..2 of the regenerated splits must equal the frozen manifest."""
    rows = []
    for seed in (0, 1, 2):
        for cat in sorted(frozen["categories"]):
            for shot in SPLIT_SHOTS:
                expected = frozen["categories"][cat][str(seed)][str(shot)]
                got = new["categories"][cat][str(seed)][str(shot)]
                rows.append({"category": cat, "seed": seed, "shot": shot,
                             "match": expected == got, "n": len(expected)})
    return rows


def main() -> int:
    WS.mkdir(parents=True, exist_ok=True)
    report: dict = {"kind": "five_seed_manifests_step1", "seeds": SEEDS,
                    "split_shots": SPLIT_SHOTS, "support_shots": SUPPORT_SHOTS,
                    "datasets": {}, "checks": []}

    print("[1/3] prepare_splits (seeds 0..4)")
    for ds, root in DATASETS.items():
        run(["scripts/prepare_splits.py", "--dataset", ds, "--root", str(root),
             "--output", str(SPLITS_OUT),
             "--shots", *[str(s) for s in SPLIT_SHOTS],
             "--seeds", *[str(s) for s in SEEDS]])
        new_path = SPLITS_OUT / ds / "manifest.json"
        frozen_path = FROZEN_SPLITS / ds / "manifest.json"
        new = json.loads(new_path.read_text(encoding="utf-8"))
        frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
        prefix = check_seed_prefix(new, frozen)
        if not all(r["match"] for r in prefix):
            bad = [r for r in prefix if not r["match"]]
            raise SystemExit(f"{ds}: regenerated seeds 0..2 disagree with frozen "
                             f"data/splits: {bad[:3]}")
        report["datasets"][ds] = {
            "splits_manifest": str(new_path),
            "splits_manifest_sha256": sha256(new_path),
            "frozen_splits_manifest_sha256": sha256(frozen_path),
            "frozen_prefix_checks": len(prefix),
            "frozen_prefix_all_match": True,
        }
        report["checks"].append({"check": f"{ds}/splits/seeds0-2==frozen",
                                 "pass": True, "n": len(prefix)})
        print(f"  {ds}: seeds 0..2 identical to frozen ({len(prefix)} checks)")

    print("[2/3] build_support_manifest (K=8, seeds 0..4)")
    run(["scripts/unified_fusion_paper_support_v1/build_support_manifest.py",
         "--dataset", *DATASETS, "--shots", *[str(s) for s in SUPPORT_SHOTS],
         "--seeds", *[str(s) for s in SEEDS], "--output", str(SUPPORT_OUT),
         "--out-name", "support_manifest.json"])

    print("[3/3] verify support manifests")
    for ds in DATASETS:
        path = SUPPORT_OUT / f"support_manifest_{ds}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not payload["prefix_invariance_all_match"]:
            raise SystemExit(f"{ds}: support manifest prefix invariance FAILED")
        if payload["seeds"] != SEEDS:
            raise SystemExit(f"{ds}: seeds {payload['seeds']} != {SEEDS}")
        if payload["shots"] != SUPPORT_SHOTS:
            raise SystemExit(f"{ds}: shots {payload['shots']} != {SUPPORT_SHOTS}")
        seeds_without = sorted({r["seed"] for r in payload["seeds_without_history"]})

        extseed_path = EXTSEED_SUPPORT / f"support_manifest_{ds}.json"
        cross = None
        if extseed_path.is_file():
            other = json.loads(extseed_path.read_text(encoding="utf-8"))
            mismatches = []
            for cat in sorted(payload["categories"]):
                for seed in SEEDS:
                    for shot in SUPPORT_SHOTS:
                        a = payload["categories"][cat][str(seed)][str(shot)]
                        b = other["categories"][cat][str(seed)][str(shot)]
                        if a != b:
                            mismatches.append({"category": cat, "seed": seed,
                                               "shot": shot})
            cross = {"path": str(extseed_path),
                     "sha256": sha256(extseed_path),
                     "checked": len(payload["categories"]) * len(SEEDS)
                                * len(SUPPORT_SHOTS),
                     "all_match": not mismatches,
                     "mismatches": mismatches[:5]}
            if mismatches:
                raise SystemExit(f"{ds}: support manifest disagrees with the "
                                 f"seeds_extension archive: {mismatches[:3]}")

        overlap = {}
        for cat in sorted(payload["categories"]):
            for s1, s2 in combinations(SEEDS, 2):
                for shot in (4, 8):
                    key = f"{cat}/s{s1}-vs-s{s2}_k{shot}"
                    overlap[key] = len(
                        set(payload["categories"][cat][str(s1)][str(shot)])
                        & set(payload["categories"][cat][str(s2)][str(shot)]))

        report["datasets"][ds].update({
            "support_manifest": str(path),
            "support_manifest_sha256": sha256(path),
            "prefix_checks": payload["n_prefix_checks"],
            "prefix_all_match": True,
            "seeds_without_history": seeds_without,
            "cross_check_vs_seeds_extension": cross,
            "overlap_k4_k8": overlap,
        })
        report["checks"].append({"check": f"{ds}/support/prefix_invariance",
                                 "pass": True,
                                 "n": payload["n_prefix_checks"]})
        if cross is not None:
            report["checks"].append(
                {"check": f"{ds}/support/cross_vs_seeds_extension", "pass": True,
                 "n": cross["checked"]})
        print(f"  {ds}: {payload['n_prefix_checks']} prefix checks pass; "
              f"seeds without history {seeds_without}; "
              f"cross-check {'ok' if (cross is None or cross['all_match']) else 'FAIL'}")

    report["all_pass"] = all(c["pass"] for c in report["checks"])
    out = WS / "step1_manifest_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"report: {out}  (all_pass={report['all_pass']})")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
