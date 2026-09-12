"""E3: run the full SubspaceAD matrix (MVTec 15 + VisA 12 classes x K1/2/4 x seeds 0/1/2).

Goal: give E3 a *second complete method* (243 method-category units) alongside
PatchCore's 243, which together reach the task book's 486-unit minimum scope.

Protocol notes (recorded, not silently changed):
- Every category of a dataset is processed in ONE process per (seed, K). The
  upstream K-shot sampling is `random.shuffle(train_paths)[:k]` with a single
  seed set at process start, so the RNG state depends on the category order.
  Running categories in separate processes would therefore select different
  support images; per-category results are only comparable inside one run.
  Consequently the 12-unit small matrix (which ran 2 categories per process)
  is NOT merged into this matrix - the whole 243-unit matrix is recomputed here.
- `--smoke_half` (fp16) is kept from the small matrix for VRAM reasons; it is an
  accuracy adaptation and must be quoted wherever these numbers are used.
- The native evaluator is used as-is; its own P-AUROC/P-AP stride-8 subsample
  and full-resolution AU-PRO are properties of the upstream code path.

Resumable: a (dataset, seed, K) combination whose benchmark_results.csv already
has the expected number of category rows is skipped.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

METHOD_ROOT = C.ROOT / "methods" / "SubspaceAD"
PYTHON = C.ROOT / ".venv-anomalyclip" / "Scripts" / "python.exe"
OUT_ROOT = C.HANDOFF_OUT / "subspacead_official_full"
CKPT = "checkpoints/dinov2-with-registers-giant"

MVTEC_CATS = ["bottle", "cable", "capsule", "carpet", "grid", "hazelnut", "leather",
              "metal_nut", "pill", "screw", "tile", "toothbrush", "transistor", "wood", "zipper"]
VISA_CATS = ["candle", "capsules", "cashew", "chewinggum", "fryum", "macaroni1",
             "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe_fryum"]

DATASETS = {
    "mvtec": {"name": "mvtec_ad", "path": "../../data/mvtec", "cats": MVTEC_CATS},
    "visa": {"name": "visa", "path": "../../data/visa_pytorch/1cls", "cats": VISA_CATS},
}


def run_dir(dataset: str, seed: int, k: int) -> Path | None:
    """Locate the per-run output directory created by main.py for (seed, K)."""
    base = OUT_ROOT / dataset
    hits = sorted(p for p in base.glob(f"*_k{k}_seed{seed}") if p.is_dir())
    return hits[0] if hits else None


def done_rows(dataset: str, seed: int, k: int) -> int:
    d = run_dir(dataset, seed, k)
    if d is None:
        return 0
    f = d / "benchmark_results.csv"
    if not f.exists():
        return 0
    rows = list(csv.DictReader(f.open(encoding="utf-8")))
    return sum(1 for r in rows if r.get("Category") not in (None, "", "Average"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="mvtec,visa")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--shots", default="1,2,4")
    args = ap.parse_args()

    log_dir = C.OUT_ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    status_rows, matrix_rows = [], []

    plan = [(ds, int(s), int(k))
            for ds in args.datasets.split(",")
            for s in args.seeds.split(",")
            for k in args.shots.split(",")]

    for ds, seed, k in plan:
        info = DATASETS[ds]
        expect = len(info["cats"])
        got = done_rows(ds, seed, k)
        (OUT_ROOT / ds).mkdir(parents=True, exist_ok=True)
        if got == expect:
            print(f"[skip] {ds} seed={seed} k={k}: already {got}/{expect}")
            status_rows.append({"dataset": ds, "seed": seed, "K": k, "expected_rows": expect,
                                "observed_rows": got, "status": "skipped_complete",
                                "seconds": 0.0, "exit_code": 0})
        else:
            cmd = [str(PYTHON), "-X", "utf8", "main.py",
                   "--dataset_name", info["name"], "--dataset_path", info["path"],
                   "--model_ckpt", CKPT, "--seed", str(seed), "--k_shot", str(k),
                   "--categories", *info["cats"], "--smoke_half", "--no_log_file",
                   "--outdir", str(OUT_ROOT / ds)]
            log = log_dir / f"{ds}_s{seed}_k{k}.log"
            print(f"[run ] {ds} seed={seed} k={k} -> {log}")
            t0 = time.perf_counter()
            with log.open("w", encoding="utf-8", errors="replace") as fh:
                proc = subprocess.run(cmd, cwd=str(METHOD_ROOT), stdout=fh,
                                      stderr=subprocess.STDOUT, text=True)
            secs = time.perf_counter() - t0
            got = done_rows(ds, seed, k)
            status_rows.append({"dataset": ds, "seed": seed, "K": k, "expected_rows": expect,
                                "observed_rows": got,
                                "status": "completed" if (proc.returncode == 0 and got == expect)
                                          else "failed",
                                "seconds": round(secs, 2), "exit_code": proc.returncode})
            print(f"[done] {ds} seed={seed} k={k}: rows {got}/{expect}, "
                  f"exit {proc.returncode}, {secs:.1f}s")

        d = run_dir(ds, seed, k)
        if d and (d / "benchmark_results.csv").exists():
            for r in csv.DictReader((d / "benchmark_results.csv").open(encoding="utf-8")):
                if r.get("Category") in (None, "", "Average"):
                    continue
                matrix_rows.append({
                    "dataset": ds, "category": r["Category"], "seed": seed, "K": k,
                    "image_auroc": r["Image AUROC"], "image_aupr": r["Image AUPR"],
                    "pixel_auroc": r["Pixel AUROC"], "pixel_ap": r["Pixel AP"],
                    "aupro": r["AU-PRO"],
                    "source": str((d / "benchmark_results.csv").relative_to(C.ROOT)),
                })

    e3 = C.OUT_ROOT / "E3"
    _write_csv(e3 / "subspacead_full_runs.csv", status_rows)
    _write_csv(e3 / "subspacead_full_matrix.csv", matrix_rows)
    n_ok = sum(1 for r in status_rows if r["status"] in ("completed", "skipped_complete"))
    summary = {
        "created_utc": C.utcnow(),
        "protocol": "SubspaceAD official main.py, fp16 (--smoke_half), native evaluator",
        "model_ckpt": CKPT,
        "datasets": {ds: {"n_categories": len(v["cats"]), "categories": v["cats"]}
                     for ds, v in DATASETS.items()},
        "planned_runs": len(plan), "runs_ok": n_ok,
        "matrix_rows": len(matrix_rows),
        "expected_matrix_rows": sum(len(DATASETS[ds]["cats"]) for ds, _, _ in plan),
        "total_seconds": round(sum(r["seconds"] for r in status_rows), 1),
        "status_counts": {s: sum(1 for r in status_rows if r["status"] == s)
                          for s in sorted({r["status"] for r in status_rows})},
        "note": ("All categories of a dataset run in one process per (seed, K) so the upstream "
                 "K-shot shuffle sees a fixed category order; the earlier 12-unit small matrix "
                 "(2 categories per process) is not merged. fp16 via --smoke_half is an accuracy "
                 "adaptation. The native evaluator computes P-AUROC/P-AP on its own stride-8 "
                 "subsample of the 672x672 map and AU-PRO at full resolution."),
    }
    C.write_json(e3 / "subspacead_full_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if n_ok == len(plan) else 1


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
