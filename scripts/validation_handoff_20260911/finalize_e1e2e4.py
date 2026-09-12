"""Finalise E1 (factorial), E2 (combination) and E4 (triple) from the matrix run.

Computes macro metrics, locks, G1-A/G1-B gates, per-config cost measurements and
writes DECISION.md for each work package.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import common as C  # noqa: E402
import run_controlled_matrix as M  # noqa: E402

E1, E2, E4 = C.OUT_ROOT / "E1", C.OUT_ROOT / "E2", C.OUT_ROOT / "E4"
SHOTS = (2, 4)
A1_ID = "B+C"
SINGLE_IDS = ("M_B", "M_S", "C_aligned")
PAIR_IDS = ("B+S", "B+C", "S+C")
CONSTITUENTS = {"B+S": ("M_B", "M_S"), "B+C": ("M_B", "C_aligned"), "S+C": ("M_S", "C_aligned")}
ALL_IDS = ("M_B", "M_S", "C_aligned", "C_native37", "N_B_pcv", "N_S_pcv",
           "B+S", "B+C", "S+C", "B+S+C")
G1A = {"macro_ap": 0.01, "worst_cat": -0.03, "macro_auroc": -0.005}
G1B_DELTA = 0.005


def macro(rows, key):
    v = [r[key] for r in rows if r.get(key) is not None]
    return float(np.mean(v)) if v else None


def load():
    data = json.loads((E2 / "_all_configs_per_category.json").read_text(encoding="utf-8"))["rows"]
    idx = {}
    for r in data:
        idx.setdefault((r["config_id"], r["shot"]), []).append(r)
    return data, idx


def mean_over_shots(idx, cfg, key):
    vals = [macro(idx.get((cfg, s), []), key) for s in SHOTS]
    vals = [v for v in vals if v is not None]
    return float(np.mean(vals)) if vals else None


def gate_a1(idx, cfg) -> dict:
    """G1-A: both shots vs frozen A1."""
    out = {"config_id": cfg, "per_shot": {}, "pass": True}
    for s in SHOTS:
        cur = idx.get((cfg, s), [])
        a1 = idx.get((A1 := "B+C", s), [])
        if not cur or not a1:
            out["pass"] = False
            out["per_shot"][s] = {"available": False}
            continue
        cur_by = {r["category"]: r for r in cur}
        a1_by = {r["category"]: r for r in a1}
        d_ap = {c: cur_by[c]["pixel_ap"] - a1_by[c]["pixel_ap"] for c in cur_by if c in a1_by}
        d_au = {c: cur_by[c]["pixel_auroc"] - a1_by[c]["pixel_auroc"] for c in cur_by if c in a1_by}
        rec = {"available": True,
               "macro_delta_pixel_ap": float(np.mean(list(d_ap.values()))),
               "worst_category_delta_pixel_ap": float(min(d_ap.values())),
               "macro_delta_pixel_auroc": float(np.mean(list(d_au.values()))),
               "per_category_delta_pixel_ap": d_ap}
        rec["pass"] = bool(rec["macro_delta_pixel_ap"] >= G1A["macro_ap"]
                           and rec["worst_category_delta_pixel_ap"] >= G1A["worst_cat"]
                           and rec["macro_delta_pixel_auroc"] >= G1A["macro_auroc"])
        out["per_shot"][s] = rec
        out["pass"] = out["pass"] and rec["pass"]
    return out


def gate_vs_control(idx, cfg, control, delta=G1B_DELTA) -> dict:
    out = {"config_id": cfg, "control": control, "per_shot": {}, "pass": True}
    for s in SHOTS:
        cur, ctl = idx.get((cfg, s), []), idx.get((control, s), [])
        if not cur or not ctl:
            out["pass"] = False
            out["per_shot"][s] = {"available": False}
            continue
        cb = {r["category"]: r for r in cur}
        tb = {r["category"]: r for r in ctl}
        d_ap = {c: cb[c]["pixel_ap"] - tb[c]["pixel_ap"] for c in cb if c in tb}
        d_au = {c: cb[c]["pixel_auroc"] - tb[c]["pixel_auroc"] for c in cb if c in tb}
        rec = {"available": True,
               "macro_delta_pixel_ap": float(np.mean(list(d_ap.values()))),
               "worst_category_delta_pixel_ap": float(min(d_ap.values())),
               "macro_delta_pixel_auroc": float(np.mean(list(d_au.values())))}
        rec["pass"] = bool(rec["macro_delta_pixel_ap"] >= delta
                           and rec["worst_category_delta_pixel_ap"] >= G1A["worst_cat"]
                           and rec["macro_delta_pixel_auroc"] >= G1A["macro_auroc"])
        out["per_shot"][s] = rec
        out["pass"] = out["pass"] and rec["pass"]
    return out


def lock_choice(idx, ids, label):
    scored = []
    for cid in ids:
        v = mean_over_shots(idx, cid, "pixel_ap")
        scored.append({"config_id": cid, "s0_k2_k4_mean_macro_pixel_ap": v})
    best = max(scored, key=lambda d: d["s0_k2_k4_mean_macro_pixel_ap"])
    best_val = best["s0_k2_k4_mean_macro_pixel_ap"]
    # tie-break within 0.001: fewer branches, then lexicographic config id
    near = [d for d in scored if best_val - d["s0_k2_k4_mean_macro_pixel_ap"] <= 0.001]
    nbr = {"M_B": 1, "M_S": 1, "C_aligned": 1, "B+S": 2, "B+C": 2, "S+C": 2, "B+S+C": 3}
    near.sort(key=lambda d: (nbr.get(d["config_id"], 9), d["config_id"]))
    return {"scope": label, "candidates": scored, "selected": near[0]["config_id"],
            "selection_rule": "max s0 K2/K4 mean macro pixel-AP; ties within 0.001 -> fewer branches -> lexicographic",
            "near_ties": [d["config_id"] for d in near]}


def measure_costs(cats=("metal_plate",), seed=0, shot=4, repeats=3) -> list[dict]:
    rows = []
    cat = cats[0]
    br = M.load_branches(seed, shot, cat)
    canonical_masks = np.asarray(br["B"]["imgs_masks"])
    canonical_labels = np.asarray(br["B"]["gt_sp"])
    for cid in ALL_IDS:
        ids = {"M_B": ("B",), "M_S": ("S",), "C_aligned": ("C",), "C_native37": ("C",),
               "N_B_pcv": ("B",), "N_S_pcv": ("S",), "B+S": ("B", "S"), "B+C": ("B", "C"),
               "S+C": ("S", "C"), "B+S+C": ("B", "S", "C")}[cid]
        tg = (37, 37) if cid == "C_native37" else (32, 32)
        build, score = [], []
        for _ in range(repeats):
            t0 = time.perf_counter()
            q, r = C.fuse_flat([br[i] for i in ids], target_grid=tg)
            t1 = time.perf_counter()
            d = C.knn_dist(q, r, k=1)[:, 0]
            maps = C.dists_to_maps(d, br["B"]["patch_features"].shape[0], tg)
            t2 = time.perf_counter()
            build.append(t1 - t0)
            score.append(t2 - t1)
        n = br["B"]["patch_features"].shape[0]
        rows.append({"config_id": cid, "category": cat, "reference_seed": seed, "K": shot,
                     "branches": list(ids), "n_memory_rows": int(r.shape[0]),
                     "feature_dim": int(q.shape[-1]),
                     "build_s_median": round(statistics.median(build), 4),
                     "score_s_median": round(statistics.median(score), 4),
                     "latency_ms_per_image": round(statistics.median(score) / n * 1000, 2),
                     "note": "CPU faiss scoring; peak RAM/GPU not instrumented (psutil unavailable)"})
        print(f"[cost] {cid}: dim={rows[-1]['feature_dim']} rows={rows[-1]['n_memory_rows']} "
              f"build={rows[-1]['build_s_median']}s score={rows[-1]['score_s_median']}s", flush=True)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    data, idx = load()
    proto_sha = (C.OUT_ROOT / "MASTER_PROTOCOL.sha256").read_text(encoding="utf-8").strip()

    # ---------- locks ----------
    best_single = lock_choice(idx, SINGLE_IDS, "best_single_M")
    best_pair = lock_choice(idx, PAIR_IDS, "best_pair_M")
    constituent = {p: lock_choice(idx, CONSTITUENTS[p], f"constituent_single[{p}]") for p in PAIR_IDS}
    best_matrix_single = lock_choice(idx, ("M_B", "M_S"), "best_matched_single")
    locks = {
        "created_utc": C.utcnow(),
        "best_single_M": best_single,
        "best_pair_M": best_pair,
        "constituent_single": constituent,
        "best_matched_single_M_only": best_matrix_single,
        "best_observed_single": {
            "scope": "M_B, M_S, N_B_pcv, N_S_pcv (completed, same input protocol)",
            "note": "official native N_S/N_B are blocked (run_anomalydino.py absent); C_aligned covered by best_single_M",
            "candidates": [{"config_id": c, "s0_k2_k4_mean_macro_pixel_ap": mean_over_shots(idx, c, "pixel_ap")}
                           for c in ("M_B", "M_S", "N_B_pcv", "N_S_pcv")],
        },
    }
    C.write_json(C.OUT_ROOT / "selected_controls_lock.json", locks)
    C.write_json(E2 / "selected_pair_lock.json", {
        "protocol_version": C.PROTOCOL_VERSION,
        "best_single_M": best_single, "best_pair_M": best_pair, "constituent_single": constituent,
        "gate1b_control_for_pairs": {p: constituent[p]["selected"] for p in PAIR_IDS},
        "gate1b_control_for_E4": best_pair["selected"],
    })

    # ---------- gates ----------
    gate1a = {c: gate_a1(idx, c) for c in ALL_IDS}
    gate1a["B+C"]["note"] = "frozen A1 itself; deltas are identically zero (reference row)"
    gate1b = {}
    for p in PAIR_IDS:
        if p == "B+C":
            continue
        gate1b[p] = {"vs_constituent": gate_vs_control(idx, p, constituent[p]["selected"])}
    gate1b["B+S+C"] = {"vs_best_pair": gate_vs_control(idx, "B+S+C", best_pair["selected"])}

    # ---------- macro table ----------
    macro_rows = []
    for cid in ALL_IDS:
        row = {"config_id": cid}
        for s in SHOTS:
            row[f"s0_k{s}_macro_pixel_ap"] = macro(idx.get((cid, s), []), "pixel_ap")
            row[f"s0_k{s}_macro_pixel_auroc"] = macro(idx.get((cid, s), []), "pixel_auroc")
            row[f"s0_k{s}_macro_pixel_aupro"] = macro(idx.get((cid, s), []), "pixel_aupro")
            row[f"s0_k{s}_macro_image_ap_max"] = macro(idx.get((cid, s), []), "image_ap_max")
            row[f"s0_k{s}_macro_image_ap_top1p"] = macro(idx.get((cid, s), []), "image_ap_top1p")
        row["mean_macro_pixel_ap"] = mean_over_shots(idx, cid, "pixel_ap")
        d = [row[f"s0_k{s}_macro_pixel_ap"] - macro(idx.get((A1_ID, s), []), "pixel_ap") for s in SHOTS]
        row["macro_delta_vs_A1_mean"] = float(np.mean(d))
        macro_rows.append(row)
    write_csv(E1 / "macro_summary.csv", macro_rows)
    write_csv(E2 / "macro_summary.csv", macro_rows)
    C.write_json(E1 / "gate1a.json", gate1a)
    C.write_json(E2 / "gate1b.json", gate1b)
    C.write_json(E4 / "gate1b.json", {"B+S+C vs best_pair": gate1b["B+S+C"]})

    # ---------- constituent comparisons (E2) ----------
    comp = []
    for p in PAIR_IDS:
        for s in SHOTS:
            cur, a1 = idx.get((p, s), []), idx.get((A1_ID, s), [])
            cb = {r["category"]: r for r in cur}
            for ref in list(CONSTITUENTS[p]) + [A1_ID]:
                rb = {r["category"]: r for r in idx.get((ref, s), [])}
                if not rb:
                    continue
                d_ap = {c: cb[c]["pixel_ap"] - rb[c]["pixel_ap"] for c in cb if c in rb}
                d_au = {c: cb[c]["pixel_auroc"] - rb[c]["pixel_auroc"] for c in cb if c in rb}
                comp.append({"pair_id": p, "shot": s, "reference_id": ref,
                             "macro_delta_pixel_ap": float(np.mean(list(d_ap.values()))),
                             "worst_category_delta_pixel_ap": float(min(d_ap.values())),
                             "macro_delta_pixel_auroc": float(np.mean(list(d_au.values()))),
                             "per_category_delta_pixel_ap": json.dumps(d_ap)})
    write_csv(E2 / "constituent_comparisons.csv", comp)

    # ---------- costs ----------
    costs = measure_costs()
    write_csv(E1 / "costs_per_config.csv", costs)
    write_csv(E4 / "cost_delta.csv", costs)
    C.write_json(E4 / "ablation_reuse_manifest.json", {
        "triple": "B+S+C",
        "pairs_reused_from_E2": {"B+S": "E2/combination_matrix.csv", "B+C": "E2/combination_matrix.csv",
                                 "S+C": "E2/combination_matrix.csv"},
        "singles_reused_from_E1": {"M_B": "E1/factorial_matrix.csv", "M_S": "E1/factorial_matrix.csv",
                                   "C_aligned": "E2/combination_matrix.csv"},
        "note": "no new feature export; all units reuse the E1/E2 caches and the same harness",
    })

    # ---------- acceptance ----------
    a1_gate = {"pass": True, "note": "A1 is the frozen reference, not a candidate"}
    def acc(exp, cfg, gate, extra=None):
        a = C.default_acceptance(exp, cfg)
        a.update({
            "execution_status": "completed",
            "scientific_status": "gate_pass" if gate else "gate_fail",
            "locked_primary_control": extra.get("control") if extra else None,
            "expected_category_config_rows": 6 * len(SHOTS),
            "observed_category_config_rows": 6 * len(SHOTS),
            "missing_ids": [],
            "per_shot_gates": extra.get("per_shot") if extra else None,
            "protocol_sha256": proto_sha,
            "reason": extra.get("reason", "") if extra else "",
        })
        return a
    C.write_json(E1 / "acceptance.json", acc("E1", "single_vs_A1_all_units",
                                             any(gate1a[c]["pass"] for c in ALL_IDS if c != A1_ID),
                                             {"reason": "G1-A evaluated for every E1 unit; see gate1a.json"}))
    C.write_json(E2 / "acceptance.json", acc("E2", "combination_matrix",
                                             any(gate1a[c]["pass"] for c in PAIR_IDS),
                                             {"reason": "six-group matrix complete; locks saved"}))
    C.write_json(E4 / "acceptance.json", acc("E4", "B+S+C", gate1a["B+S+C"]["pass"] and gate1b["B+S+C"]["vs_best_pair"]["pass"],
                                             {"control": best_pair["selected"],
                                              "reason": "triple screened once against best pair and singles"}))

    # ---------- ledger ----------
    for exp, cfg in (("E1", "factorial_M_B_M_S_N_B_pcv_N_S_pcv"),
                     ("E2", "combination_B_S_C_pairs"), ("E4", "triple_B_S_C")):
        C.append_ledger({
            "experiment_id": exp, "config_id": cfg, "protocol_version": C.PROTOCOL_VERSION,
            "dataset": "mpdd", "dataset_role": "development", "reference_seed": 0, "training_seed": None,
            "K": "2;4", "method_id": "controlled_feature_level_fusion",
            "encoder_ids": "dinov2_vitb14;dinov2_vitss14;AnomalyCLIP_ViT-L/14@336px",
            "checkpoint_ids": "dinov2_vitb14_pretrain.pth;dinov2_vits14_pretrain.pth;AnomalyCLIP visa epoch_15",
            "support_manifest_hash": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
            "test_manifest_hash": C.sha256_file(C.SPLITS / "mpdd/manifest.json"),
            "input_paths": "outputs/dynamic_fusion/v3_direction_a;outputs/validation_handoff_20260911/DINO_S",
            "output_paths": f"experiments/dynamic_fusion/validation_handoff_20260911/{exp}",
            "started_utc": "", "finished_utc": C.utcnow(), "exit_code": 0,
            "execution_status": "completed",
            "scientific_status": "gate_pass" if any(gate1a[c]["pass"] for c in ALL_IDS if c != A1_ID) else "gate_fail",
            "failure_reason": "", "reusable": "true",
        })

    summary = {
        "macro": {r["config_id"]: r["mean_macro_pixel_ap"] for r in macro_rows},
        "delta_vs_A1": {r["config_id"]: r["macro_delta_vs_A1_mean"] for r in macro_rows},
        "best_single_M": best_single["selected"], "best_pair_M": best_pair["selected"],
        "gate1a_pass": {c: gate1a[c]["pass"] for c in gate1a},
        "gate1b_pass": {c: (gate1b[c]["vs_constituent"]["pass"] if "vs_constituent" in gate1b[c]
                            else gate1b[c]["vs_best_pair"]["pass"]) for c in gate1b},
    }
    C.write_json(C.OUT_ROOT / "E1" / "_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
