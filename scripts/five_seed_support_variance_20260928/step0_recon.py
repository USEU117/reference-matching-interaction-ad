"""Inventory the on-disk coverage needed by the five-seed support-variance experiment.

Read-only.  Writes ``experiments/dynamic_fusion/five_seed_support_variance_20260928/
recon_inventory.json`` so the pre-run state (which seeds/units already exist) is archived
before anything new executes.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NEW = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914"
EXT = NEW / "05_baselines_ext_20260921"
R = ROOT / "experiments/dynamic_fusion/unified_fusion_paper_support_20260913"
GEN = ROOT / "experiments/dynamic_fusion/generalization_mvtec_visa_20260915"
EXTSEED = ROOT / "experiments/dynamic_fusion/seeds_extension_20260917"
OUT = ROOT / "outputs/dynamic_fusion/unified_fusion_paper_support_20260913"
WS = ROOT / "experiments/dynamic_fusion/five_seed_support_variance_20260928"

UNIT_RE = re.compile(r"^(?P<ds>[a-z0-9]+)_s(?P<seed>\d+)_k(?P<shot>\d+)$")


def units_below(root: Path) -> dict:
    found: dict[str, set[str]] = {}
    if not root.is_dir():
        return {}
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        m = UNIT_RE.match(path.name)
        if m:
            found.setdefault(m.group("ds"), set()).add(
                f"s{m.group('seed')}_k{m.group('shot')}")
    return {k: sorted(v) for k, v in found.items()}


def files_by_seed(root: Path) -> dict:
    counts: dict[str, int] = {}
    if not root.is_dir():
        return counts
    for path in sorted(root.glob("*.npz")):
        m = re.search(r"_s(\d+)_k(\d+)_", path.name)
        key = f"s{m.group(1)}_k{m.group(2)}" if m else "other"
        counts[key] = counts.get(key, 0) + 1
    return counts


def manifest_seeds(path: Path) -> dict:
    if not path.is_file():
        return {"exists": False}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    cats = data.get("categories", {})
    seeds, shots = set(), set()
    for per_seed in cats.values():
        for seed, per_shot in per_seed.items():
            seeds.add(int(seed))
            shots.update(int(s) for s in per_shot)
    return {"exists": True, "seeds": sorted(seeds), "shots": sorted(shots),
            "categories": len(cats)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for part in iter(lambda: fh.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def main() -> int:
    inv: dict = {"root": str(ROOT)}

    inv["a1_units"] = {
        "R_p1_matrix": units_below(R / "p1_matrix/units"),
        "R_p3_external": units_below(R / "p3_external/units"),
        "EXTSEED_p1_matrix": units_below(EXTSEED / "p1_matrix/units"),
        "EXTSEED_p3_external": units_below(EXTSEED / "p3_external/units"),
        "GEN_p1_matrix": units_below(GEN / "p1_matrix/units"),
        "NEW_01_geometry": units_below(NEW / "01_geometry/units"),
    }
    inv["extseed_top"] = sorted(p.name for p in EXTSEED.iterdir()) if EXTSEED.is_dir() else []

    inv["canonical"] = {}
    for name, root in (("study", OUT / "canonical"), ("GEN", GEN / "canonical"),
                       ("EXTSEED", EXTSEED / "canonical"), ("WS", WS / "canonical")):
        entry = {}
        for branch in ("B", "S", "C"):
            entry[branch] = units_below(root / branch) if (root / branch).is_dir() else {}
        inv["canonical"][name] = entry

    inv["region_maps"] = {
        "anomalydino_canvas": files_by_seed(NEW / "05_baselines/region_maps/anomalydino_canvas"),
        "anomalydino_canvas_rotation": files_by_seed(
            NEW / "05_baselines/region_maps/anomalydino_canvas_rotation"),
        "subspacead_ext": files_by_seed(
            EXT / "subspacead/region_maps/subspacead_native_fp16"),
        "winclip_ext": files_by_seed(EXT / "winclip_plus/region_maps/winclip_native_240"),
        "anomalyclip_ext": files_by_seed(
            EXT / "anomalyclip_zs/region_maps/anomalyclip_zeroshot_518"),
    }

    inv["patchcore"] = {
        "local128": {
            "mpdd": units_below(ROOT / "outputs/patchcore/closeout/mpdd_closeout"),
            "btad": units_below(ROOT / "outputs/patchcore/closeout/btad_closeout"),
            "mvtec": units_below(ROOT / "outputs/patchcore/closeout/mvtec_closeout"),
            "visa": units_below(ROOT / "outputs/patchcore/closeout/visa_closeout"),
        },
        "official224": {
            "mpdd": units_below(ROOT / "outputs/patchcore/closeout_official224/mpdd_official224"),
            "btad": units_below(ROOT / "outputs/patchcore/closeout_official224/btad_official224"),
            "mvtec": units_below(ROOT / "outputs/patchcore/closeout_official224/mvtec_official224"),
            "visa": units_below(ROOT / "outputs/patchcore/closeout_official224/visa_official224"),
        },
    }

    inv["faithful_gt"] = sorted(
        p.name for p in (NEW / "01_geometry/gt").glob("btad_s*_faithful.npz")) \
        if (NEW / "01_geometry/gt").is_dir() else []

    inv["splits_manifests"] = {
        ds: manifest_seeds(ROOT / "data/splits" / ds / "manifest.json")
        for ds in ("mpdd", "btad", "mvtec", "visa")}

    inv["support_manifests"] = {}
    for label, root in (("study", R / "p0_support"),
                        ("GEN", GEN / "p0_support"), ("EXTSEED", EXTSEED / "p0_support"),
                        ("WS", WS / "p0_support")):
        inv["support_manifests"][label] = sorted(p.name for p in root.glob("*.json")) \
            if root.is_dir() else []

    inv["csv"] = {}
    for label, path in (("frozen", NEW / "05_baselines_multi_dataset/baseline_common_region.csv"),
                        ("ext", EXT / "baseline_common_region_ext.csv"),
                        ("recomputed", EXT / "recomputed_intersection"
                                         "/baseline_common_region_recomputed_all_methods.csv")):
        if path.is_file():
            rows = path.read_text(encoding="utf-8-sig").splitlines()
            inv["csv"][label] = {"path": str(path.relative_to(ROOT)),
                                 "lines": len(rows) - 1, "sha256": sha256(path)}
        else:
            inv["csv"][label] = {"path": str(path.relative_to(ROOT)), "exists": False}

    ws = WS / "recon_inventory.json"
    ws.parent.mkdir(parents=True, exist_ok=True)
    ws.write_text(json.dumps(inv, ensure_ascii=False, indent=2, default=sorted),
                  encoding="utf-8")
    print(json.dumps({"written": str(ws), "sections": sorted(inv)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
