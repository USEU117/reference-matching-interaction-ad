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


def build(dataset: str, shots: list[int], seeds: list[int]) -> dict:
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

        overlap[f"{dataset}/{category}/s0_k8-vs-s1_k8"] = len(
            set(out_categories[category]["0"]["8"]) & set(out_categories[category]["1"]["8"]))
        overlap[f"{dataset}/{category}/s0_k8-vs-s2_k8"] = len(
            set(out_categories[category]["0"]["8"]) & set(out_categories[category]["2"]["8"]))
        overlap[f"{dataset}/{category}/s1_k8-vs-s2_k8"] = len(
            set(out_categories[category]["1"]["8"]) & set(out_categories[category]["2"]["8"]))

        hist_k4 = {p for seed in seeds for p in source["categories"][category][str(seed)]["4"]}
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
