"""Step 2: run the five-seed (0..4) extension at K=4 across the four datasets.

The script is a resumable orchestrator: every phase checks its own outputs first, so it
can be re-run after an interruption without redoing finished work.  Nothing archived is
written to - see `fsv_common.arm` for how each runner's output paths are redirected into
`experiments/dynamic_fusion/five_seed_support_variance_20260928/`.

Phases (run in this order, `--phases` selects a subset):

    merge       hard-link the archived canonical caches (mpdd/btad seeds 0-4, mvtec/visa
                seeds 0-2) into WS/canonical + write the guard record
    export      encode the missing mvtec/visa canonical caches (seeds 3,4, branches B/S/C)
    matrix      run the A1 matrix for mvtec/visa seeds 3,4 (K=4) -> WS/p1_matrix_gen
    gt          faithful BTAD-03 ground truth for seeds 3,4
    rescore     BTAD-03 geometry-corrected re-score for seeds 2,3,4
    anomalydino AnomalyDINO canvas / canvas+rotation region maps, seeds 2,3,4
    patchcore   PatchCore native local128 / official224, seeds 2,3,4
    extmethods  SubspaceAD + WinCLIP+ region maps, seeds 2,3,4
    eval        shared-region evaluation of seeds 2,3,4 (new rows) -> WS/eval
    evalverify  the same evaluation for seeds 0,1 (replay of the archived convention)
                -> WS/eval_verify

Usage:
    python scripts/five_seed_support_variance_20260928/step2_run_five_seed.py
    python scripts/five_seed_support_variance_20260928/step2_run_five_seed.py --phases merge export
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import fsv_common as P  # noqa: E402

PHASES = ["merge", "export", "matrix", "gt", "rescore", "anomalydino", "patchcore",
          "extmethods", "relabel", "eval", "evalverify"]
NEW_METHODS = ["SubspaceAD_native_fp16", "WinCLIP_native_240"]
CANONICAL_SOURCES = [  # (root, datasets, seeds)
    (P.STUDY_CANON, ["mpdd", "btad"], [0, 1, 2, 3, 4]),
    (P.GEN_CANON, ["mvtec", "visa"], [0, 1, 2]),
]


def log(message: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{P.utcnow()}\t{message}\n")


def link_file(src: Path, dst: Path) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return "exists"
    try:
        os.link(src, dst)
        return "hardlink"
    except OSError:
        shutil.copy2(src, dst)
        return "copy"


def missing_unit(root: Path, branch: str, dataset: str, seed: int,
                 categories: list[str]) -> list[str]:
    out_dir = root / branch / f"{dataset}_s{seed}_k8"
    return [c for c in categories if not (out_dir / f"{c}.npz").exists()]


# ------------------------------------------------------------------------------- phases

def phase_merge(state: dict, args) -> dict:
    record = {"phase": "merge", "root": str(P.WS_CANONICAL), "sources": [], "files": {}}
    for root, datasets, seeds in CANONICAL_SOURCES:
        for dataset in datasets:
            for seed in seeds:
                for branch in P.BRANCHES:
                    src_dir = root / branch / f"{dataset}_s{seed}_k8"
                    if not src_dir.is_dir():
                        raise SystemExit(f"canonical source missing: {src_dir}")
                    for src in sorted(src_dir.glob("*.npz")):
                        dst = P.WS_CANONICAL / branch / f"{dataset}_s{seed}_k8" / src.name
                        action = link_file(src, dst)
                        rel = f"{branch}/{dataset}_s{seed}_k8/{src.name}"
                        record["files"][rel] = {"source": str(src), "sha256": P.sha256_file(src),
                                                "size": src.stat().st_size, "action": action}
        record["sources"].append(str(root))
    record["n_files"] = len(record["files"])
    record["created_utc"] = P.utcnow()
    P.write_json(P.WS_GUARD, record)
    log(f"merge\tlinked={record['n_files']}", P.WS_LOGS / "step2.log")
    return {"phase": "merge", "files": record["n_files"],
            "hardlinks": sum(1 for v in record["files"].values() if v["action"] == "hardlink")}


def guard_verify() -> dict:
    """Re-hash every linked source file: proves the archived caches were not modified."""
    guard = P.read_json(P.WS_GUARD)
    changed, missing = [], []
    for rel, info in guard["files"].items():
        src = Path(info["source"])
        if not src.exists():
            missing.append(rel)
            continue
        if P.sha256_file(src) != info["sha256"]:
            changed.append(rel)
    return {"checked": len(guard["files"]), "changed": changed, "missing": missing}


def phase_export(state: dict, args) -> dict:
    results = []
    if args.smoke:
        result = P.run_script(
            "export_k8_cache",
            ["--dataset", "visa", "--branch", "B", "--seeds", args.seeds_output[0],
             "--categories", P.CATS["visa"][0],
             "--output-root", P.WS_CANONICAL,
             "--support-manifest", P.WS_SUPPORT / "support_manifest_visa.json",
             "--reuse-query-from", P.GEN_CANON, "--reuse-query-seed", "0"],
            P.WS_LOGS / "export_smoke_visa_B.log")
        return {"phase": "export", "smoke": True, "seconds": result["seconds"],
                "unit": str(P.WS_CANONICAL / "B" / f"visa_s{args.seeds_output[0]}_k8"
                            / f"{P.CATS['visa'][0]}.npz")}
    for dataset in ("mvtec", "visa"):
        categories = P.CATS[dataset]
        seeds = args.seeds_output
        for branch in P.BRANCHES:
            todo = [s for s in seeds
                    if missing_unit(P.WS_CANONICAL, branch, dataset, s, categories)]
            if not todo:
                results.append({"dataset": dataset, "branch": branch, "status": "complete"})
                continue
            result = P.run_script(
                "export_k8_cache",
                ["--dataset", dataset, "--branch", branch, "--seeds", *todo,
                 "--output-root", P.WS_CANONICAL,
                 "--support-manifest", P.WS_SUPPORT / f"support_manifest_{dataset}.json",
                 "--reuse-query-from", P.GEN_CANON, "--reuse-query-seed", "0"],
                P.WS_LOGS / f"export_{dataset}_{branch}.log")
            still = [s for s in todo
                     if missing_unit(P.WS_CANONICAL, branch, dataset, s, categories)]
            results.append({"dataset": dataset, "branch": branch, "seeds": todo,
                            "seconds": result["seconds"], "still_missing": still})
    bad = [r for r in results if r.get("still_missing")]
    if bad:
        raise SystemExit(f"export incomplete: {bad}")
    return {"phase": "export", "runs": results}


def phase_matrix(state: dict, args) -> dict:
    out = P.WS_P1_GEN
    attempts = []

    def incomplete() -> list[str]:
        missing = []
        for dataset in ("mvtec", "visa"):
            for seed in args.seeds_output:
                unit = out / "units" / f"{dataset}_s{seed}_k4"
                for category in P.CATS[dataset]:
                    if not (unit / category / "patch_scores.npz").exists():
                        missing.append(f"{dataset}_s{seed}_k4/{category}")
        return missing

    for attempt in range(args.matrix_attempts):
        missing = incomplete()
        if not missing:
            break
        print(f"    matrix: {len(missing)} units outstanding", flush=True)
        result = P.run_script(
            "run_matrix",
            ["--datasets", "mvtec", "visa", "--seeds", *args.seeds_output, "--shots", P.SHOT,
             "--output", out, "--resume", "--max-hours", "60",
             "--code-amendment-reason",
             "five-seed support-variance extension 2026-09-28: seeds 3-4 at K=4; the frozen "
             "design (datasets, branches) is unchanged"],
            P.WS_LOGS / f"matrix_gen_{attempt}.log")
        attempts.append({"attempt": attempt, "seconds": result["seconds"],
                         "returncode": result["returncode"]})
    missing = incomplete()
    if missing:
        raise SystemExit(f"matrix incomplete: {len(missing)} units, e.g. {missing[:5]}")
    done = sorted((out / "units").glob("*/*/DONE.json"))
    return {"phase": "matrix", "attempts": attempts, "units_done": len(done)}


def _purge_archive_gt(seeds: list[int]) -> list[dict]:
    """Remove any BTAD faithful-GT file an earlier run wrote into the archive.

    `freeze_s0.faithful_gt` writes to ``NEW/01_geometry/gt``; the first gt run of this
    workstream happened before the module redirection took effect, so two files landed in
    the frozen experiment directory.  They are deleted (their hashes are recorded here) and
    regenerated into the five-seed work area by the correctly redirected runner, which is
    deterministic, so the archive returns to exactly its recorded contents.
    """
    purged = []
    for seed in seeds:
        name = f"btad_s{seed}_03_faithful.npz"
        stray = P.NEW / "01_geometry/gt" / name
        if not stray.exists():
            continue
        purged.append({"path": str(stray), "sha256": P.sha256_file(stray),
                       "action": "deleted; regenerated under the five-seed work area"})
        stray.unlink()
    return purged


def phase_gt(state: dict, args) -> dict:
    purged = _purge_archive_gt([3, 4])
    # Mirror the archived faithful ground truth (seeds 0-2) into the work area: the
    # re-score, the canvas geometry and the region masks then all resolve inside WS, and
    # the archived copies are read-only inputs.  Seeds 3-4 are built below.
    mirrored = []
    for seed in (0, 1, 2):
        for category in P.CATS["btad"]:
            name = f"btad_s{seed}_{category}_faithful.npz"
            source = P.NEW / "01_geometry/gt" / name
            if not source.exists():
                raise SystemExit(f"archived faithful ground truth missing: {source}")
            target = P.WS_GEOM / "gt" / name
            action = link_file(source, target)
            mirrored.append({"file": name, "action": action,
                             "sha256": P.sha256_file(source)})
    records = []
    for seed in (3, 4):
        target = P.WS_GEOM / "gt" / f"btad_s{seed}_03_faithful.npz"
        if target.exists():
            records.append({"seed": seed, "status": "exists", "path": str(target),
                            "exists": True})
            continue
        result = P.run_script(
            "freeze_s0", [], P.WS_LOGS / f"faithful_gt_s{seed}.log",
            env={"FSV_CALL": "freeze_s0:faithful_gt",
                 "FSV_KWARGS": P.json.dumps({"dataset": "btad", "seed": seed,
                                             "category": "03", "write": True})})
        records.append({"seed": seed, "status": "built", "log": result["log"],
                        "path": str(target), "exists": target.exists()})
    if not all(r["exists"] for r in records):
        raise SystemExit(f"faithful_gt incomplete: {records}")
    return {"phase": "gt", "mirrored_from_archive": mirrored,
            "removed_from_archive": purged, "built": records}


def phase_rescore(state: dict, args) -> dict:
    # The re-score replays the archived per-seed patch scores.  Seeds 0-1 replay the
    # 2026-09-13 study store (their corrected unit is already in the archive); seeds 2-4
    # have no unit there, so their replay source is the 2026-09-17 seed extension, which the
    # protocol records as byte-identical for every seed both stores share.
    replay = P.WS_REPLAY / "p3_external/units"
    linked = 0
    for seed in P.RESCORE_SEEDS:
        source = P.EXTSEED / "p1_matrix_btad/units" / f"btad_s{seed}_k4" / "03"
        if not source.is_dir():
            raise SystemExit(f"replay source missing: {source}")
        for src in sorted(source.iterdir()):
            if src.is_file() and src.suffix in (".npz", ".json", ".csv"):
                link_file(src, replay / f"btad_s{seed}_k4" / "03" / src.name)
                linked += 1
    todo = [s for s in P.RESCORE_SEEDS
            if not (P.WS_GEOM / "units" / f"btad_s{s}_k4" / "03__rev_correct"
                    / "patch_scores.npz").exists()]
    if todo:
        P.run_script("rescore_btad03",
                     ["--seeds", *todo, "--shots", P.SHOT],
                     P.WS_LOGS / "rescore_btad03.log")
    units = [
        {"seed": seed,
         "path": ("five_seed work area" if (P.WS_GEOM / "units" / f"btad_s{seed}_k4"
                                            / "03__rev_correct" / "patch_scores.npz").exists()
                  else ("archive rev_correct" if seed < 2 else None))}
        for seed in P.SEEDS]
    absent = [u["seed"] for u in units if u["seed"] in P.RESCORE_SEEDS
              and u["path"] != "five_seed work area"]
    if absent:
        raise SystemExit(f"rescore produced no unit for seeds {absent}")
    summary = P.WS_GEOM / "S0B_SUMMARY.json"
    return {"phase": "rescore", "replayed_files": linked, "units": units,
            "summary": str(summary) if summary.exists() else None,
            "summary_sha256": P.sha256_file(summary) if summary.exists() else None}


def _region_map_done(variant: str, dataset: str, seed: int) -> bool:
    base = P.WS_BASELINES / "region_maps" / variant
    return all((base / f"{dataset}_s{seed}_k4_{c}.npz").exists() for c in P.CATS[dataset])


def phase_anomalydino(state: dict, args) -> dict:
    runs = []
    for variant, extra in (("anomalydino_canvas", []),
                           ("anomalydino_canvas_rotation", ["--rotation"])):
        pending = [(ds, seed) for ds in P.DATASETS for seed in args.seeds_output
                   if not _region_map_done(variant, ds, seed)]
        if not pending:
            runs.append({"variant": variant, "status": "complete"})
            continue
        datasets = sorted({ds for ds, _ in pending})
        seeds = sorted({seed for _, seed in pending})
        result = P.run_script(
            "run_baseline_anomalydino",
            ["--datasets", *datasets, "--seeds", *seeds, "--shots", P.SHOT,
             "--frame", "canvas", *extra,
             "--out", P.WS_BASELINES,
             "--dump-maps", P.WS_BASELINES / "region_maps" / variant,
             "--suffix", f"_five_seed_{variant}"],
            P.WS_LOGS / f"{variant}.log")
        still = [f"{ds}_s{seed}" for ds, seed in pending if not _region_map_done(variant, ds, seed)]
        runs.append({"variant": variant, "seconds": result["seconds"], "still_missing": still})
    bad = [r for r in runs if r.get("still_missing")]
    if bad:
        raise SystemExit(f"anomalydino incomplete: {bad}")
    return {"phase": "anomalydino", "runs": runs}


def _patchcore_done(config: str, dataset: str, seed: int) -> bool:
    name = "patchcore" if config == "local128" else "patchcore_official224"
    return (P.WS_PATCHCORE / name / f"{dataset}_s{seed}_k4" / "summary.csv").exists()


def phase_patchcore(state: dict, args) -> dict:
    runs = []
    for config in ("local128", "official224"):
        pending = [(ds, seed) for ds in P.DATASETS for seed in args.seeds_output
                   if not _patchcore_done(config, ds, seed)]
        if not pending:
            runs.append({"config": config, "status": "complete"})
            continue
        result = P.run_script(
            "run_baseline_patchcore",
            ["--datasets", *sorted({ds for ds, _ in pending}),
             "--seeds", *sorted({s for _, s in pending}), "--shots", P.SHOT,
             "--config", config, "--skip-existing", "--out", P.WS_PATCHCORE],
            P.WS_LOGS / f"patchcore_{config}.log")
        still = [f"{ds}_s{seed}" for ds, seed in pending
                 if not _patchcore_done(config, ds, seed)]
        runs.append({"config": config, "seconds": result["seconds"], "still_missing": still})
    bad = [r for r in runs if r.get("still_missing")]
    if bad:
        raise SystemExit(f"patchcore incomplete: {bad}")
    return {"phase": "patchcore", "runs": runs}


def phase_extmethods(state: dict, args) -> dict:
    runs = []
    # The runners only create their own output directory on the first successful unit, but
    # they write a failure report into it; without this a first-unit failure surfaces as a
    # FileNotFoundError that hides the real error.
    for folder in ("subspacead", "winclip_plus"):
        (P.WS_EXT / folder).mkdir(parents=True, exist_ok=True)
    for method, module, python in (("subspacead", "ext_run_subspacead", P.PY_ANOMALYCLIP),
                                  ("winclip", "ext_run_winclip", P.PY_WINCLIP)):
        result = P.run_script(
            module,
            ["--datasets", *P.DATASETS, "--seeds", *args.seeds_output, "--shots", P.SHOT,
             "--skip-existing"],
            P.WS_LOGS / f"{method}_seeds.log", python=python)
        runs.append({"method": method, "seconds": result["seconds"],
                     "returncode": result["returncode"]})
    return {"phase": "extmethods", "runs": runs}


def _expected_eval_rows(seeds: list[int]) -> int:
    return sum(len(P.CATS[ds]) for ds in P.DATASETS) * len(seeds) * 8


def _part_methods(path: Path) -> set:
    """Methods already recorded in a region part (used to decide what still needs a run)."""
    import numpy as np

    if not path.exists():
        return set()
    with np.load(path, allow_pickle=False) as z:
        rows = P.json.loads(str(z["rows"]))
    return {row["method"] for row in rows}


def _aggregate_parts(parts: Path, out: Path, rows_name: str) -> list[dict]:
    """Rebuild the row CSV from the per-unit part files (same layout ECR writes)."""
    import numpy as np

    rows = []
    for path in sorted(parts.glob("*.npz")):
        with np.load(path, allow_pickle=False) as z:
            rows += P.json.loads(str(z["rows"]))
    P.write_csv(out / rows_name, rows)
    return rows


def _phase_eval(state: dict, args, *, seeds: list[int], out: Path, parts: Path,
                tag: str) -> dict:
    """Evaluate the selected seeds dataset by dataset, so an interrupted run resumes."""
    rows_name = "baseline_common_region_new_methods.csv"
    expected = _expected_eval_rows(seeds)
    if len(P.read_csv(out / rows_name)) == expected and not args.force_eval:
        return {"phase": tag, "status": "complete", "rows": expected,
                "csv": str(out / rows_name)}
    seconds = 0.0
    for dataset in P.DATASETS:
        pending = [(seed, category) for seed in seeds for category in P.CATS[dataset]
                   if not set(P.EVAL_METHODS) <= _part_methods(
                       parts / f"{dataset}_{seed}_{P.SHOT}_{category}.npz")]
        if not pending:
            continue
        categories = sorted({category for _, category in pending})
        print(f"    {tag}: {dataset} {len(pending)} units outstanding", flush=True)
        result = P.run_script(
            "ext_common_region",
            ["--mode", "eval", "--datasets", dataset, "--seeds", *seeds, "--shots", P.SHOT,
             "--categories", *categories, "--methods", *NEW_METHODS,
             "--out", out, "--parts", parts, "--workers", args.eval_workers],
            P.WS_LOGS / f"{tag}_{dataset}.log",
            env={"FSV_POOL": "1" if args.eval_workers > 1 else ""})
        seconds += result["seconds"]
    rows = P.read_csv(out / rows_name)
    if len(rows) != expected:
        rows = _aggregate_parts(parts, out, rows_name)
    if len(rows) != expected:
        raise SystemExit(f"{tag}: expected {expected} rows, found {len(rows)}")
    return {"phase": tag, "status": "ran", "rows": len(rows), "csv": str(out / rows_name),
            "seconds": round(seconds, 1), "parts": str(parts)}


def phase_eval(state: dict, args) -> dict:
    return _phase_eval(state, args, seeds=P.EVAL_SEEDS, out=P.WS_EVAL,
                       parts=P.WS_EVAL / "region_parts", tag="eval")


def phase_evalverify(state: dict, args) -> dict:
    return _phase_eval(state, args, seeds=[0, 1], out=P.WS_EVAL_VERIFY,
                       parts=P.WS_EVAL_VERIFY / "region_parts", tag="evalverify")


def phase_relabel(state: dict, args) -> dict:
    """Put the new region maps on the archived id spelling before they are evaluated."""
    targets = [P.WS_BASELINES / "region_maps" / variant
               for variant in ("anomalydino_canvas", "anomalydino_canvas_rotation")]
    targets += [P.WS_EXT / "subspacead/region_maps/subspacead_native_fp16",
                P.WS_EXT / "winclip_plus/region_maps/winclip_native_240"]
    report = {}
    for directory in targets:
        if not directory.is_dir():
            raise SystemExit(f"region-map directory missing: {directory}")
        report[str(directory.relative_to(P.WS))] = P.relabel_dump_ids(directory)
    return {"phase": "relabel", "directories": report,
            "files_relabelled": sum(len(v["relabelled"]) for v in report.values()),
            "files_checked": sum(v["checked"] for v in report.values())}


RUNNERS = {"merge": phase_merge, "export": phase_export, "matrix": phase_matrix,
           "gt": phase_gt, "rescore": phase_rescore, "anomalydino": phase_anomalydino,
           "patchcore": phase_patchcore, "extmethods": phase_extmethods,
           "relabel": phase_relabel, "eval": phase_eval, "evalverify": phase_evalverify}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phases", nargs="+", default=PHASES, choices=PHASES)
    ap.add_argument("--seeds-output", nargs="+", type=int, default=[3, 4],
                    help="seeds that need new encoding work (mpdd/btad are archived)")
    ap.add_argument("--eval-workers", type=int, default=4)
    ap.add_argument("--matrix-attempts", type=int, default=4)
    ap.add_argument("--force-eval", action="store_true")
    ap.add_argument("--smoke", action="store_true",
                    help="phase 'export' only: encode one single visa/branch-B unit")
    ap.add_argument("--guard-check", action="store_true",
                    help="re-hash every linked canonical source and stop if it changed")
    args = ap.parse_args()

    P.WS.mkdir(parents=True, exist_ok=True)
    report = {"kind": "five_seed_step2", "started_utc": P.utcnow(),
              "seeds_output": args.seeds_output, "phases": {}, "order": [], "failures": {}}
    log(f"step2\tSTART\tphases={','.join(args.phases)}", P.WS_LOGS / "step2.log")

    if args.guard_check and P.WS_GUARD.exists():
        report["canonical_guard_before"] = guard_verify()

    for name in args.phases:
        print(f"\n=== phase {name} ===", flush=True)
        try:
            result = RUNNERS[name](report["phases"], args)
            report["phases"][name] = result
            report["order"].append(name)
            print(f"    {result}", flush=True)
        except BaseException as exc:  # noqa: BLE001 - recorded, re-raised at the end
            report["failures"][name] = repr(exc)
            print(f"!!! phase {name} failed: {exc!r}", flush=True)
            break
        finally:
            P.write_json(P.WS / "step2_state.json", report)

    if args.guard_check and P.WS_GUARD.exists():
        report["canonical_guard_after"] = guard_verify()
    report["finished_utc"] = P.utcnow()
    report["all_pass"] = not report["failures"]
    P.write_json(P.WS / "step2_state.json", report)
    log(f"step2\tDONE\tall_pass={report['all_pass']}", P.WS_LOGS / "step2.log")
    print(f"\nreport: {P.WS / 'step2_state.json'}  all_pass={report['all_pass']}")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
