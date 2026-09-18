"""P0: build the K-extended support manifest for the unified fusion study.

The historical manifests (`data/splits/<dataset>/manifest.json`) already hold the
nested K=1/2/4 reference lists for seeds 0..2.  The new study needs K=8, and it
needs to be able to prove that K=1/2/4 did not change.

Rule (verified against `scripts/prepare_splits.py`):

    rel_candidates = sorted normal training images of the category
    shuffled       = copy; random.Random(seed).shuffle(shuffled)
    K n reference  = shuffled[:n]

So K=8 is simply the next four entries of the same shuffled sequence.  This
script rebuilds the whole sequence, asserts the historical K=1/2/4 prefixes are
byte-identical to the existing manifest (and to `selected_file_sha256`), and then
writes a new, independent manifest file.  The historical manifest is never
modified.

Usage:
    python scripts/unified_fusion_paper_support_v1/build_support_manifest.py \
        --dataset mpdd --dataset btad --output <new output dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
DEFAULT_OUT = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
# --- KolektorSDD2 confirmation set (appended 2026-09-18, additive only) --------
# KSDD2 ships as one flat `train/` + `test/` pair (no per-category folders, no
# `data/splits` manifest), so it gets its own builder below.  Nothing in
# `build()` (mpdd/btad/mvtec/visa) changes.
KSDD2 = "ksdd2"
KSDD2_ROOT = ROOT / "data" / "kolektorsdd2_raw"
KSDD2_CATEGORY = "ksdd2"
# The official archive carries one redundant pair of duplicates; the mask member
# does not end in `_GT.png`, so a suffix-based scan would count it as an image.
KSDD2_EXCLUDED_FILES = ("train/10301 (copy).png", "train/10301_GT (copy).png")
KSDD2_OFFICIAL_COUNTS = {"train": {"pos": 246, "neg": 2085}, "test": {"pos": 110, "neg": 894}}
KSDD2_F_SPEC = (ROOT / "experiments/dynamic_fusion/confirmation_ksdd2_20260918"
                / "F_SPEC.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def image_files(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)


def normal_candidates(root: Path, dataset: str, category: str) -> list[str]:
    if dataset == "visa" and (root / "meta.json").is_file():
        meta = json.loads((root / "meta.json").read_text(encoding="utf-8"))
        return sorted(item["img_path"] for item in meta["train"][category]
                      if int(item.get("anomaly", 0)) == 0)
    category_root = root / category
    for candidate in (category_root / "train" / "good", category_root / "train" / "ok"):
        if candidate.is_dir():
            return [p.relative_to(root).as_posix() for p in image_files(candidate)]
    return []


def ksdd2_split_images(split: str) -> list[Path]:
    """Images of one KSDD2 split (ground truth and the two `(copy)` files removed)."""
    excluded = {Path(rel).name for rel in KSDD2_EXCLUDED_FILES}
    split_dir = KSDD2_ROOT / split
    if not split_dir.is_dir():
        raise SystemExit(f"KSDD2 split directory missing: {split_dir}")
    return [p for p in sorted(split_dir.glob("*.png"))
            if not p.name.endswith("_GT.png") and p.name not in excluded]


def ksdd2_label(image: Path) -> int:
    """Official KSDD2 rule: positive iff the mask `X_GT.png` has a non-zero pixel."""
    import cv2

    mask = image.with_name(f"{image.stem}_GT.png")
    if not mask.is_file():
        return 0
    raw = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise FileNotFoundError(mask)
    return 1 if (raw > 0).any() else 0


def build_ksdd2(shots: list[int], seeds: list[int]) -> dict:
    """Support manifest + query list for the KSDD2 confirmation set.

    KSDD2 has no historical `data/splits/<dataset>/manifest.json`, so there is no
    prefix to preserve: the references are the prefix of one shuffled sequence per
    seed, built with exactly the rule the other datasets use
    (`sorted normal training images -> random.Random(seed).shuffle -> prefix K`).
    Only training images whose mask is empty are admissible references; the query
    list is the whole official test split (1004 images).
    """
    references: list[str] = []
    train_counts = {"pos": 0, "neg": 0}
    for image in ksdd2_split_images("train"):
        if ksdd2_label(image) == 1:
            train_counts["pos"] += 1
        else:
            train_counts["neg"] += 1
            references.append(image.relative_to(KSDD2_ROOT).as_posix())
    if len(references) < max(shots):
        raise SystemExit(f"{KSDD2}: only {len(references)} normal training images, "
                         f"need {max(shots)}")

    categories: dict[str, dict] = {KSDD2_CATEGORY: {}}
    for seed in seeds:
        shuffled = references[:]
        random.Random(int(seed)).shuffle(shuffled)
        categories[KSDD2_CATEGORY][str(seed)] = {str(k): shuffled[:k] for k in shots}

    queries: list[dict] = []
    test_counts = {"pos": 0, "neg": 0}
    for image in ksdd2_split_images("test"):
        label = ksdd2_label(image)
        test_counts["pos" if label else "neg"] += 1
        relative = image.relative_to(KSDD2_ROOT).as_posix()
        mask = image.with_name(f"{image.stem}_GT.png")
        queries.append({"sample_id": relative, "image": relative,
                        "mask": (mask.relative_to(KSDD2_ROOT).as_posix()
                                 if mask.is_file() else None),
                        "label": label})

    selected = sorted({rel for seed_map in categories[KSDD2_CATEGORY].values()
                       for rels in seed_map.values() for rel in rels})
    return {
        "schema_version": 1,
        "kind": "support_manifest_k_extended",
        "dataset": KSDD2,
        "root": str(KSDD2_ROOT),
        "shots": sorted(shots),
        "seeds": sorted(seeds),
        "nested": True,
        "extension_rule": ("sorted normal (empty-mask) training images -> "
                           "random.Random(seed).shuffle -> prefix; K=1/2/4/8 are "
                           "prefixes of one sequence per seed"),
        "source_manifest": None,
        "historical_shots": None,
        "prefix_checks": [],
        "prefix_invariance_all_match": None,
        "n_prefix_checks": 0,
        "seeds_without_history": [{"category": KSDD2_CATEGORY, "seed": int(seed),
                                   "n_normal_candidates": len(references)}
                                  for seed in seeds],
        "n_seeds_without_history": len(seeds),
        "n_normal_candidates": len(references),
        "selected_file_sha256": {
            rel: sha256(KSDD2_ROOT.joinpath(*Path(rel).parts)) for rel in selected},
        "categories": categories,
        "queries": {KSDD2_CATEGORY: queries},
        "query_counts": {"n": len(queries), **test_counts},
        "official_counts": KSDD2_OFFICIAL_COUNTS,
        "observed_counts": {"train": train_counts, "test": test_counts},
        "counts_match_official": bool(train_counts == KSDD2_OFFICIAL_COUNTS["train"]
                                      and test_counts == KSDD2_OFFICIAL_COUNTS["test"]),
        "excluded_files": list(KSDD2_EXCLUDED_FILES),
        "geometry": {"canvas_wh": [224, 630], "grid_wh": [16, 45], "patch": 14,
                     "mask_rule": "nearest-neighbour resize onto the canvas, then binarise > 0"},
        "frozen_spec": ({"path": str(KSDD2_F_SPEC), "sha256": sha256(KSDD2_F_SPEC)}
                        if KSDD2_F_SPEC.is_file() else None),
    }


def build(dataset: str, shots: list[int], seeds: list[int]) -> dict:
    if dataset == KSDD2:
        return build_ksdd2(shots, seeds)
    source_path = ROOT / "data" / "splits" / dataset / "manifest.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    root = Path(source["root"])
    if not root.is_dir():
        raise SystemExit(f"dataset root missing: {root}")

    historical_shots = [int(s) for s in source["shots"]]
    categories = sorted(source["categories"])
    out_categories: dict[str, dict] = {}
    prefix_checks: list[dict] = []
    overlap: dict[str, int] = {}
    added: dict[str, list[str]] = {}
    seeds_without_history: list[dict] = []

    for category in categories:
        candidates = normal_candidates(root, dataset, category)
        if len(candidates) < max(shots):
            raise SystemExit(f"{dataset}/{category}: only {len(candidates)} normal images, need {max(shots)}")
        out_categories[category] = {}
        sequences: dict[int, list[str]] = {}
        for seed in seeds:
            shuffled = candidates[:]
            random.Random(int(seed)).shuffle(shuffled)
            sequences[seed] = shuffled
            out_categories[category][str(seed)] = {str(k): shuffled[:k] for k in shots}

        for seed in seeds:
            ref_by_seed = source["categories"][category].get(str(seed))
            if ref_by_seed is None:
                continue
            for k in historical_shots:
                expected = list(ref_by_seed[str(k)])
                got = sequences[seed][:k]
                prefix_checks.append({
                    "category": category, "seed": int(seed), "shot": k,
                    "match": bool(expected == got),
                    "n": len(expected),
                })
                if expected != got:
                    raise SystemExit(
                        f"prefix mismatch {dataset}/{category}/seed{seed}/K{k}: "
                        f"{expected} != {got}")

        for pair in (("0", "1"), ("0", "2"), ("1", "2")):
            if all(seed in out_categories[category] for seed in pair):
                overlap[f"{dataset}/{category}/s{pair[0]}_k8-vs-s{pair[1]}_k8"] = len(
                    set(out_categories[category][pair[0]]["8"])
                    & set(out_categories[category][pair[1]]["8"]))

        # Seeds that the historical manifest never had (the seed 3..7 extension) contribute no
        # prefix check and no historical K=4 set; they are recorded instead of silently skipped.
        without_history = [int(seed) for seed in seeds
                           if str(seed) not in source["categories"][category]]
        for seed in without_history:
            seeds_without_history.append({"category": category, "seed": seed,
                                          "n_normal_candidates": len(candidates)})

        hist_k4 = {p for seed in seeds if str(seed) in source["categories"][category]
                   for p in source["categories"][category][str(seed)]["4"]}
        for seed in seeds:
            new = [p for p in out_categories[category][str(seed)]["8"] if p not in hist_k4]
            added[f"{category}/seed{seed}"] = new

    new_files = sorted({p for rows in added.values() for p in rows})
    new_hashes = {p: sha256(root.joinpath(*Path(p).parts)) for p in new_files}

    selected = sorted({
        rel for seed_map in out_categories.values()
        for shot_map in seed_map.values() for rels in shot_map.values() for rel in rels
    })
    selected_hashes = {p: sha256(root.joinpath(*Path(p).parts)) for p in selected}

    return {
        "schema_version": 1,
        "kind": "support_manifest_k_extended",
        "dataset": dataset,
        "root": str(root),
        "shots": sorted(shots),
        "seeds": sorted(seeds),
        "nested": True,
        "extension_rule": ("sorted normal training images -> random.Random(seed).shuffle -> prefix; "
                           "K=8 continues the same sequence that produced K=1/2/4"),
        "source_manifest": str(source_path),
        "source_manifest_sha256": sha256(source_path),
        "historical_shots": historical_shots,
        "prefix_checks": prefix_checks,
        "prefix_invariance_all_match": bool(all(c["match"] for c in prefix_checks)),
        "n_prefix_checks": len(prefix_checks),
        "seeds_without_history": seeds_without_history,
        "n_seeds_without_history": len(seeds_without_history),
        "added_at_k8": added,
        "added_file_sha256": new_hashes,
        "selected_file_sha256": selected_hashes,
        "overlap_between_seeds_at_k8": overlap,
        "categories": out_categories,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", nargs="+", default=["mpdd", "btad"])
    ap.add_argument("--shots", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--out-name", default="support_manifest.json")
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    written = []
    for dataset in args.dataset:
        payload = build(dataset, args.shots, args.seeds)
        name = args.out_name if len(args.dataset) == 1 else args.out_name.replace(
            ".json", f"_{dataset}.json")
        path = args.output / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"dataset": dataset, "path": str(path),
                          "prefix_checks": payload["n_prefix_checks"],
                          "prefix_all_match": payload["prefix_invariance_all_match"],
                          "sha256": sha256(path)}, ensure_ascii=False))
        written.append(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
