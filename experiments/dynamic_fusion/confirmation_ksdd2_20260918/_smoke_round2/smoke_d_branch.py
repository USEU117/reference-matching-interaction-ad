"""Round-2 KSDD2 smoke test: the D branch (WideResNet50-2) through the interaction pipeline.

Runs the *real* code path - `s3_new_encoder.EncoderD` / `build_features` / `score_branches` /
`assemble_maps` - on three KSDD2 test images and asserts the three conventions frozen in
`../F_SPEC.json`:

  1. `patch_features` is (N, 45, 16, 1536) and the masks are (N, 630, 224);
  2. the two redundant `(copy)` files appear in no list;
  3. train 246/2085 and test 110/894.

The B and C feature blocks are 3-image *fixtures* (random, unit-normalised, marked with
`smoke_fixture=True` inside the npz) written into `_smoke_round2/canonical`: a real canonical
export needs the DINO/CLIP encoders and the full 1004-image pass, which is a long job.  D is
encoded for real, by the code this round added, on the frozen 224 x 630 canvas.

No metric is computed from KSDD2 test labels - only shapes, counts and algebraic invariants
are asserted - so the one-shot rule of F_SPEC is untouched.

Run:  .venv-anomalyclip\\Scripts\\python.exe <this file>
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
F_DIR = HERE.parents[1]                      # .../confirmation_ksdd2_20260918
ROOT = F_DIR.parents[2]                      # .../sci_project
SMOKE = HERE.parent
CANON = SMOKE / "canonical"
OUT = SMOKE / "out"
SUPPORT = SMOKE / "p0_support"

sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))
sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))

import export_k8_cache as E              # noqa: E402
import build_support_manifest as B       # noqa: E402

CANVAS_HW = (630, 224)                   # (rows, cols) = grid * patch
GRID_HW = (45, 16)
PATCH = 14
D_DIM = 1536
N_QUERY = 3
K_REF = 8

gates: dict[str, bool] = {}
facts: dict[str, object] = {}


def gate(name: str, ok: bool, detail) -> None:
    gates[name] = bool(ok)
    facts[name] = detail
    print(f"[gate] {name}: {'PASS' if ok else 'FAIL'} :: {json.dumps(detail, default=str)}",
          flush=True)


def main() -> int:
    for path in (CANON, OUT, SUPPORT):
        if path.exists():
            shutil.rmtree(path)
    for path in (CANON, OUT, SUPPORT):
        path.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- 0. registration
    gate("s3_data_root_ksdd2", E.KSDD2 in E.DATA_ROOT and E.DATA_ROOT[E.KSDD2].is_dir(),
         str(E.DATA_ROOT.get(E.KSDD2)))

    # The canonical root must come from the environment (appended this round).
    os.environ["FUSION_CANONICAL_ROOT"] = str(CANON)
    import s3_new_encoder as S3          # noqa: E402  (import after the env is set)
    gate("canonical_root_from_env", Path(S3.CANONICAL) == CANON, str(S3.CANONICAL))
    gate("s3_geometry_constants",
         (S3.KSDD2_CANVAS_WH == (224, 630) and S3.KSDD2_GRID_HW == (45, 16)
          and S3.KSDD2_PATCH == 14 and S3.SMALL_EDGE == 448),
         {"canvas_wh": S3.KSDD2_CANVAS_WH, "grid_hw": list(S3.KSDD2_GRID_HW),
          "patch": S3.KSDD2_PATCH, "mpdd_btad_smaller_edge": S3.SMALL_EDGE,
          "cats": S3.CATS[S3.KSDD2], "dataset_id": S3.DATASET_ID[S3.KSDD2],
          "default_datasets": list(S3.DEFAULT_DATASETS)})

    # ------------------------------------------------------- 1. counts / (copy) files
    root = E.DATA_ROOT[E.KSDD2]
    manifest = B.build_ksdd2([1, 2, 4, 8], [0, 1, 2])
    (SUPPORT / "support_manifest_ksdd2.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    observed = manifest["observed_counts"]
    gate("counts_train_246_2085", observed["train"] == {"pos": 246, "neg": 2085}, observed["train"])
    gate("counts_test_110_894", observed["test"] == {"pos": 110, "neg": 894}, observed["test"])
    gate("counts_match_official", manifest["counts_match_official"], True)
    n_train = len(E.ksdd2_images(root / "train"))
    n_test = len(E.ksdd2_images(root / "test"))
    gate("index_sizes_2331_1004", (n_train, n_test) == (2331, 1004), [n_train, n_test])

    copy_names = {Path(rel).name for rel in E.KSDD2_EXCLUDED_FILES}
    ref_rels = {rel for seed_map in manifest["categories"]["ksdd2"].values()
                for rels in seed_map.values() for rel in rels}
    query_rels = {q["sample_id"] for q in manifest["queries"]["ksdd2"]} | {
        q["mask"] for q in manifest["queries"]["ksdd2"] if q["mask"]}
    names_seen = {Path(rel).name for rel in (ref_rels | query_rels)}
    leaks = sorted(n for n in copy_names if n in names_seen)
    gate("copy_files_in_no_list", leaks == [],
         {"leaks": leaks, "copy_present_on_disk": sorted(
             n for n in copy_names if (root / "train" / n).is_file()),
          "original_kept_in_index": "10301.png" in {p.name for p in E.ksdd2_images(root / "train")}})

    # ------------------------------------------------------- 2. masks on the canvas
    masks_all, ids_all = E.masks_on_canvas(E.KSDD2, "ksdd2", GRID_HW)
    gate("masks_shape_N_630_224", tuple(masks_all.shape) == (1004, *CANVAS_HW),
         list(masks_all.shape))
    gate("masks_binary_uint8",
         masks_all.dtype == np.uint8 and set(np.unique(masks_all).tolist()) <= {0, 1},
         {"dtype": str(masks_all.dtype), "values": sorted(np.unique(masks_all).tolist()),
          "positive_masks": int(sum(1 for m in masks_all if m.any()))})

    pos_idx = [i for i, m in enumerate(masks_all) if m.any()][:2]
    neg_idx = [i for i, m in enumerate(masks_all) if not m.any()][:1]
    pick = pos_idx + neg_idx
    ids3 = [str(ids_all[i]) for i in pick]
    masks3 = masks_all[pick]
    labels3 = np.asarray([1 if m.any() else 0 for m in masks3], dtype=np.int64)
    gate("smoke_sample_masks_3_630_224", tuple(masks3.shape) == (N_QUERY, *CANVAS_HW),
         {"sample_ids": ids3, "labels": labels3.tolist(), "shape": list(masks3.shape)})

    # --------------------------------------------------- 3. canonical fixture (B, C)
    rng = np.random.default_rng(20260918)
    for branch, dim in (("B", 384), ("C", 768)):
        directory = CANON / branch / "ksdd2_s0_k8"
        directory.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            directory / "ksdd2.npz",
            patch_features=rng.standard_normal((N_QUERY, *GRID_HW, dim)).astype(np.float32),
            ref_patch_features=rng.standard_normal((K_REF, *GRID_HW, dim)).astype(np.float32),
            gt_sp=labels3, imgs_masks=masks3, sample_ids=np.asarray(ids3),
            grid_size=np.asarray(GRID_HW, dtype=np.int64),
            smoke_fixture=np.asarray(True))

    # ------------------------------------------------------ 4. real D encode (WRN50-2)
    encoder = S3.EncoderD("cpu", S3.KSDD2)
    canvas = encoder.canvas(E.read_absolute(root / ids3[0]))
    gate("ksdd2_canvas_630_224", tuple(canvas.shape) == (*CANVAS_HW, 3), list(canvas.shape))

    started = time.perf_counter()
    record = S3.build_features(OUT, encoder, "ksdd2", "ksdd2", 0, support_dir=SUPPORT)
    encode_seconds = round(time.perf_counter() - started, 2)
    query_path = OUT / "features/query/ksdd2_ksdd2.npy"
    ref_path = OUT / "features/ref/ksdd2_s0_ksdd2.npy"
    query = np.load(query_path, mmap_mode="r")
    ref = np.load(ref_path, mmap_mode="r")
    gate("patch_features_N_45_16_1536", tuple(query.shape) == (N_QUERY, *GRID_HW, D_DIM),
         {"query_shape": list(query.shape), "ref_shape": list(ref.shape),
          "dtype": str(query.dtype), "encode_s": encode_seconds})
    gate("ref_patch_features_8_45_16_1536", tuple(ref.shape) == (K_REF, *GRID_HW, D_DIM),
         list(ref.shape))
    gate("query_rows_are_unit_length",
         bool(np.allclose(np.linalg.norm(np.asarray(query[0], dtype=np.float32), axis=-1), 1.0,
                          atol=1e-3)), "L2 per position, max|norm-1|="
         f"{float(np.max(np.abs(np.linalg.norm(np.asarray(query[0], dtype=np.float32), axis=-1) - 1.0))):.3e}")

    # --------------------------------------------------- 5. minimal interaction run
    patch_count = GRID_HW[0] * GRID_HW[1]
    rows = N_QUERY * patch_count
    providers = {
        "B": S3.DenseRows(S3.unit_rows(rng.standard_normal((rows, 384)).astype(np.float32))),
        "C": S3.DenseRows(S3.unit_rows(rng.standard_normal((rows, 768)).astype(np.float32))),
        "D": S3.MemmapRows(query_path, (rows, D_DIM)),
    }
    refs = {
        "B": S3.unit_rows(rng.standard_normal((patch_count, 384)).astype(np.float32)),
        "C": S3.unit_rows(rng.standard_normal((patch_count, 768)).astype(np.float32)),
        "D": S3.unit_rows(np.load(ref_path).astype(np.float32).reshape(-1, D_DIM)[:patch_count]),
    }
    raw, configs = S3.score_branches(providers, refs, GRID_HW, N_QUERY, "cpu")
    maps = S3.assemble_maps(raw, configs)

    shapes = {name: list(np.asarray(map_).shape) for name, map_ in {**raw, **configs, **maps}.items()}
    gate("all_maps_N_45_16", all(s == [N_QUERY, *GRID_HW] for s in shapes.values()),
         {"n_methods": len(shapes), "shapes": sorted({tuple(s) for s in shapes.values()})})

    # J = min_r sum_b w_b d_b  >=  sum_b w_b min_r d_b = L, i.e. the engine's G = J - L >= 0.
    # (The inequality goes this way: the shared reference row may minimise each branch at a
    # different position, so the independent minima sum can only be smaller.)
    g_gap = {j: float(np.min(configs[j] - maps[l]))
             for j, l in (("A1_J", "A1_L"), ("DUP_J", "DUP_L"),
                          ("TRI_D_J", "TRI_D_L"), ("BAL_D_J", "BAL_D_L"))}
    gate("G_J_minus_L_non_negative", all(v >= -1e-6 for v in g_gap.values()),
         {f"min(G)_{k.split('_J')[0]}": round(v, 9) for k, v in g_gap.items()})

    # the L maps are the frozen weighted sums of the per-branch minima
    exact = {
        "A1_L": float(np.max(np.abs(maps["A1_L"] - (.5 * raw["B"] + .5 * raw["C"])))),
        "DUP_L": float(np.max(np.abs(maps["DUP_L"] - ((2 / 3) * raw["B"] + (1 / 3) * raw["C"])))),
        "TRI_D_L": float(np.max(np.abs(maps["TRI_D_L"] - ((raw["B"] + raw["D"] + raw["C"]) / 3)))),
        "BAL_D_L": float(np.max(np.abs(maps["BAL_D_L"] - (.25 * raw["B"] + .25 * raw["D"]
                                                        + .5 * raw["C"])))),
        "D_single": float(np.max(np.abs(maps["D"] - raw["D"]))),
    }
    gate("construction_arithmetic_exact", all(v == 0.0 for v in exact.values()), exact)

    interaction = float(np.mean(maps["TRI_D_L"] - maps["DUP_L"]
                               - configs["TRI_D_J"] + configs["DUP_J"]))
    gate("interaction_expression_finite", bool(np.isfinite(interaction)),
         {"I_TRI_D_placeholder": round(interaction, 6),
          "note": "synthetic B/C, one reference: a wiring value, NOT a KSDD2 result"})

    print("[smoke] gates:", json.dumps(gates), flush=True)
    print("[smoke] facts:", json.dumps(facts, ensure_ascii=False, default=str), flush=True)
    print(f"[smoke] ALL_GATES_PASS {all(gates.values())}", flush=True)
    (SMOKE / "SMOKE_RESULTS.json").write_text(
        json.dumps({"gates": gates, "facts": facts,
                    "all_gates_pass": bool(all(gates.values()))},
                   ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
