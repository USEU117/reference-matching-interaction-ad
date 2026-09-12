"""Run the official UniVAD evaluation on a single MVTec category.

Why this exists
---------------
`test_univad.py` scores all 15 MVTec classes in one pass and then, for every class in
`test_data.get_cls_names()`, calls `roc_auc_score` on that class's collected results.
With 6 GiB of VRAM the full dataset cannot be scored here (stage 1 alone is ~2 s/image
for 2,000+ images, and stage 2 has to keep CLIP ViT-L/14, DINOv2 ViT-g/14 and DINO
ViT-S/8 resident). `--class_name` filters the *forward* work but not `get_cls_names()`,
so the run dies in the metric block on the first class with no samples.

This script re-creates `test_univad.py`'s loop for exactly one category: same
`MVTecDataset` with `aug_rate=-1`, same `Resize((448,448))+ToTensor`, same k-shot normal
frame assembled from `train/good/<round+i>.png`, same `UniVAD.setup` / `UniVAD.forward`
calls, same score/mask collection, and the same two metrics
(`roc_auc_score(gt_sp, pr_sp)` and `roc_auc_score(gt_px.ravel(), pr_px.ravel())`).
The model and dataset classes are the vendored upstream ones, unmodified.

GPU memory
----------
DINOv2 ViT-g/14 is 4.55 GiB of fp32 weights on its own. `--dinov2-dtype float16` casts
that backbone to fp16 and casts its outputs back to fp32, so the rest of the model (CLIP
tower, DINO ViT-S/8, CFA) keeps running in fp32. This is a precision deviation and must
be reported as such; it is the only change that makes stage 2 fit in the card.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]


def host_rss_gib() -> float:
    """Resident set size of this process in GiB (used only for memory diagnostics)."""
    try:
        import psutil  # noqa: PLC0415
        return psutil.Process().memory_info().rss / 2**30
    except Exception:
        pass
    try:  # Windows fallback: no third-party dependency
        import ctypes  # noqa: PLC0415

        class _Counters(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]

        counters = _Counters()
        counters.cb = ctypes.sizeof(_Counters)
        ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
        return counters.WorkingSetSize / 2**30
    except Exception:
        return float("nan")


def make_forward_features_cast(net, dtype):
    """Cast `forward_features` to `dtype` and return its dict in the original dtype."""
    import torch

    net.to(dtype=dtype)
    original = net.forward_features

    def forward_features_cast(x, *args, **kwargs):
        if torch.is_tensor(x) and x.is_floating_point():
            x = x.to(dtype)
        out = original(x, *args, **kwargs)
        if isinstance(out, dict):
            return {k: (v.float() if torch.is_tensor(v) and v.is_floating_point() else v)
                    for k, v in out.items()}
        return out

    net.forward_features = forward_features_cast


def install_chunked_cosine_similarity(rows: int = 16) -> None:
    """Replace `F.cosine_similarity` with a chunked, bit-identical version.

    `UniVAD.forward` evaluates `F.cosine_similarity(x1, x2, dim=2)` with `x1` of shape
    (Na, 1, C) and `x2` of shape (1, Nb, C). The broadcast product is (Na, Nb, C) =
    1024*1024*1024 fp32 = 4 GiB, and that single tensor is what OOMs on a 6 GiB card.

    The replacement normalises both operands first and then walks the broadcast axis in
    blocks, doing the identical elementwise product and per-row reduction. Measured
    agreement with the stock op is exact: max abs difference 0.000e+00 on
    (1024,1,1024)x(1,1024,1024) and on the `max(dim=1)` reduction that UniVAD applies
    immediately afterwards (see .tmp_univad/probe_cosine.py). Only the peak allocation
    changes.
    """
    import torch
    import torch.nn.functional as F

    stock = F.cosine_similarity

    def cosine_similarity(x1, x2, dim=1, eps=1e-8):
        if x1.dim() != 3 or x2.dim() != 3 or dim != 2:
            return stock(x1, x2, dim=dim, eps=eps)
        if x2.shape[0] == 1 and x1.shape[1] == 1:
            axis, base, other = 0, x1, x2
        elif x1.shape[0] == 1 and x2.shape[1] == 1:
            axis, base, other = 1, x2, x1
        else:
            return stock(x1, x2, dim=dim, eps=eps)
        n1 = base / base.pow(2).sum(dim=dim, keepdim=True).sqrt().clamp_min(eps)
        n2 = other / other.pow(2).sum(dim=dim, keepdim=True).sqrt().clamp_min(eps)
        out = []
        for s in range(0, n1.shape[axis], rows):
            piece = n1[s:s + rows] if axis == 0 else n1[:, s:s + rows]
            out.append((piece * n2).sum(dim=dim))
        return torch.cat(out, dim=axis)

    F.cosine_similarity = cosine_similarity
    torch.nn.functional.cosine_similarity = cosine_similarity
    print(f"[stage2] F.cosine_similarity -> chunked (rows={rows}); the stock op would "
          f"materialise a (Nb, Na, C) broadcast = 4 GiB per call", flush=True)


def install_posix_glob() -> None:
    """Make `glob.glob` return forward-slash paths (Windows portability shim).

    UniVAD's MULTI branch calls `utils.filter_algorithm.filter_bg_noise`, which sorts the
    cached heat-mask directories with `int(x.split("/")[-1])`. On Windows `glob.glob`
    returns `./heat_masks/<cls>_heat/train\\0`, so the split yields `train\\0` and the run
    dies with `ValueError: invalid literal for int() with base 10: 'train\\\\0'`.
    Normalising to forward slashes reproduces the string upstream sees on Linux; every
    consumer of these paths (`cv2.imread`, `os.makedirs`, `open`) accepts it on Windows.
    """
    import glob as glob_module

    stock_glob = glob_module.glob

    def glob_posix(pattern, *args, **kwargs):
        return [p.replace("\\", "/") for p in stock_glob(pattern, *args, **kwargs)]

    glob_module.glob = glob_posix
    print("[stage2] glob.glob -> forward-slash paths (filter_bg_noise needs POSIX separators)",
          flush=True)


def comparable(settings: dict | None) -> dict | None:
    """Settings minus the per-category fields, for the aggregate homogeneity check."""
    if settings is None:
        return None
    return {k: v for k, v in settings.items() if k not in ("class_filter", "argv")}


def aggregate_reports(inputs: list, report: str | None) -> int:
    """Combine per-category stage-2 reports into one per-category + macro report.

    One process per category is required on this 6 GiB card: a single long-lived
    process gets evicted by unrelated desktop VRAM traffic after a few tens of images
    and then stalls for minutes per image, while a fresh process runs at ~1.4 s/image.
    Category order follows the order the inputs are listed in (dataset order).
    """
    rows, seconds, peaks, settings, per_class = [], 0.0, [], None, []
    for path in inputs:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        run = payload.get("run", [])
        if len(run) != 1:
            raise SystemExit(f"{path}: expected exactly one category row, got {len(run)}")
        rows.append(run[0])
        timing = payload.get("timing", {})
        seconds += float(timing.get("seconds", 0.0))
        peaks.append(timing.get("peak_vram_gib"))
        per_class.append({"report": path, "category": run[0]["category"],
                          "test_images": run[0]["test_images"],
                          "s_per_image": timing.get("s_per_image"),
                          "peak_vram_gib": timing.get("peak_vram_gib")})
        if settings is None:
            settings = payload.get("settings")
        elif comparable(payload.get("settings")) != comparable(settings):
            raise SystemExit(f"{path}: settings differ from the first report; "
                             "refusing to aggregate heterogeneous runs")

    total_images = sum(r["test_images"] for r in rows)
    macro = {
        "categories": len(rows),
        "macro_image_auroc": round(float(np.mean([r["image_auroc"] for r in rows])), 5),
        "macro_pixel_auroc": round(float(np.mean([r["pixel_auroc"] for r in rows])), 5),
    }
    print("[stage2] per-category: " + json.dumps(rows), flush=True)
    print("[stage2] macro: " + json.dumps(macro), flush=True)
    if report:
        with open(report, "w", encoding="utf-8") as fh:
            json.dump({"run": rows, "macro": macro, "settings": settings,
                       "per_class_processes": per_class,
                       "timing": {"seconds": round(seconds, 1),
                                  "s_per_image": round(seconds / max(total_images, 1), 3),
                                  "peak_vram_gib": max([p for p in peaks if p] or [0.0]),
                                  "aggregated_from": len(inputs)}},
                      fh, indent=2)
        print(f"[stage2] wrote {report}", flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--univad-dir", default=str(REPO / "methods" / "univad_official"))
    ap.add_argument("--dataset", default="mvtec")
    # The trailing separator matters: MVTecDataset returns
    # `os.path.join(root, img_path)` and UniVAD resolves the stage-1 mask with
    # `image_path.split('/data/')[-1]`. On Windows the join would insert a backslash
    # ("\\data\\mvtec" + "\\" + "bottle/..."), the '/data/' split would not match, and the
    # mask lookup would silently resolve to a nonexistent path. A trailing '/' keeps the
    # joined path POSIX-style, which is the string upstream sees on Linux.
    ap.add_argument("--data-path", default="./data/mvtec/")
    ap.add_argument("--image-size", type=int, default=448)
    ap.add_argument("--k-shot", type=int, default=1)
    ap.add_argument("--round", type=int, default=0)
    ap.add_argument("--class-name", default="all",
                    help="'all' mirrors test_univad.py's full pass; a class name restricts it")
    ap.add_argument("--limit", type=int, default=0,
                    help="score at most N images (0 = no cap); for memory diagnostics")
    ap.add_argument("--mem-log-every", type=int, default=0,
                    help="print allocated/reserved VRAM and host RSS every N images (0 = off)")
    ap.add_argument("--empty-cache-every", type=int, default=0,
                    help="call torch.cuda.empty_cache() every N images (0 = off)")
    ap.add_argument("--dinov2-dtype", choices=["float32", "float16"], default="float32")
    ap.add_argument("--memory-safe-cosine", action="store_true",
                    help="chunk F.cosine_similarity to avoid the 4 GiB broadcast")
    ap.add_argument("--cosine-rows", type=int, default=16)
    ap.add_argument("--report", default=None)
    ap.add_argument("--aggregate-inputs", default=None,
                    help="comma-separated per-class stage-2 JSONs; combine them into "
                         "--report and exit (used because the 6 GiB card needs one "
                         "short-lived process per category)")
    args = ap.parse_args()

    if args.aggregate_inputs:
        return aggregate_reports(args.aggregate_inputs.split(","), args.report)

    os.chdir(args.univad_dir)
    sys.path.insert(0, os.getcwd())

    import torch  # noqa: E402
    import torchvision  # noqa: E402
    import torchvision.transforms as transforms  # noqa: E402
    from PIL import Image  # noqa: E402
    from sklearn.metrics import roc_auc_score  # noqa: E402
    from tqdm import tqdm  # noqa: E402

    from UniVAD import UniVAD  # noqa: E402
    from datasets.mvtec import MVTecDataset  # noqa: E402

    image_size, k_shot = args.image_size, args.k_shot
    cls_target = args.class_name

    if args.memory_safe_cosine:
        install_chunked_cosine_similarity(args.cosine_rows)
    install_posix_glob()

    if args.dinov2_dtype == "float16":
        # UniVAD.__init__ builds the DINOv2 backbone through torch.hub and immediately
        # hands it to ComponentFeatureExtractor, which moves it to the device itself; so
        # the cast has to happen inside the hub loader. Otherwise 4.55 GiB of fp32
        # weights would reach the card before we ever get a chance to shrink them.
        hub_load = torch.hub.load

        def hub_load_dtype(repo_or_dir, model, *a, **kw):
            net = hub_load(repo_or_dir, model, *a, **kw)
            if str(model).startswith("dinov2_"):
                make_forward_features_cast(net, torch.float16)
                print(f"[stage2] {model} backbone cast to torch.float16", flush=True)
            return net

        torch.hub.load = hub_load_dtype

    model = UniVAD(image_size=image_size)
    model = model.to("cuda")
    model.eval()
    print("[stage2] UniVAD built; alloc=%.2f GiB free=%.2f GiB"
          % (torch.cuda.memory_allocated() / 2**30, torch.cuda.mem_get_info()[0] / 2**30),
          flush=True)

    transform = transforms.Compose(
        [transforms.Resize((image_size, image_size)), transforms.ToTensor()]
    )
    test_data = MVTecDataset(root=args.data_path, transform=transform,
                             target_transform=transform, aug_rate=-1, mode="test")
    image_transform = transforms.Compose(
        [transforms.Resize((image_size, image_size)), transforms.ToTensor()]
    )

    all_classes = args.class_name in ("all", "ALL", "")
    if all_classes:
        indices = list(range(len(test_data)))
    else:
        target = cls_target.replace("_", " ").lower()
        indices = [i for i, row in enumerate(test_data.data_all)
                   if row["cls_name"].replace("_", " ").lower() == target]
        if not indices:
            raise SystemExit(f"no test images for {cls_target!r}")
    if args.limit:
        indices = indices[: args.limit]
    print(f"[stage2] scoring {len(indices)} test images "
          f"({'all classes' if all_classes else cls_target})", flush=True)

    results = {"cls": [], "gt_sp": [], "pr_sp": [], "gt_px": [], "pr_px": []}
    cls_last = None
    normal_paths = None
    t0 = time.perf_counter()
    for n, i in enumerate(tqdm(indices, desc="univad")):
        items = test_data[i]
        image = items["img"].unsqueeze(0).to("cuda")
        image_pil = items["img_pil"]
        image_path = items["img_path"]
        cls_name = items["cls_name"]

        gt_mask = items["img_mask"].clone()
        gt_mask[gt_mask > 0.5], gt_mask[gt_mask <= 0.5] = 1, 0
        results["cls"].append(cls_name)
        results["gt_px"].append(gt_mask.squeeze(0).numpy())
        results["gt_sp"].append(items["anomaly"])

        if cls_name != cls_last:
            # same k-shot normal frame as test_univad.py: train/good/<round+i>.png
            normal_paths = [
                "./data/mvtec/" + cls_name.replace(" ", "_") + "/train/good/"
                + str(j).zfill(3) + ".png"
                for j in range(args.round, args.round + k_shot)
            ]
            normal_images = torch.cat(
                [image_transform(Image.open(p).convert("RGB")).unsqueeze(0)
                 for p in normal_paths], dim=0
            ).to("cuda")
            model.setup({"few_shot_samples": normal_images,
                         "dataset_category": cls_name.replace(" ", "_"),
                         "image_path": normal_paths})
            cls_last = cls_name
            print(f"[stage2] setup {cls_name!r}: gate={model.gate} "
                  f"alloc={torch.cuda.memory_allocated()/2**30:.2f} GiB "
                  f"free={torch.cuda.mem_get_info()[0]/2**30:.2f} GiB", flush=True)

        with torch.no_grad():
            pred = model(image, image_path, image_pil)
        results["pr_sp"].append(pred["pred_score"].item())
        results["pr_px"].append(pred["pred_mask"].detach().cpu().numpy())
        if n == 0:
            print("[stage2] first image forward done; peak=%.2f GiB"
                  % (torch.cuda.max_memory_allocated() / 2**30), flush=True)
        if args.empty_cache_every and (n + 1) % args.empty_cache_every == 0:
            torch.cuda.empty_cache()
        if args.mem_log_every and (n + 1) % args.mem_log_every == 0:
            print("[stage2] n=%d alloc=%.2f reserved=%.2f peak=%.2f host_rss=%.2f GiB"
                  % (n + 1,
                     torch.cuda.memory_allocated() / 2**30,
                     torch.cuda.memory_reserved() / 2**30,
                     torch.cuda.max_memory_allocated() / 2**30,
                     host_rss_gib()), flush=True)
    secs = time.perf_counter() - t0

    rows = []
    cls_arr = np.array(results["cls"])
    # dataset order, matching the order test_univad.py's log table uses
    order = [c.replace("_", " ") for c in test_data.get_cls_names()]
    for obj in sorted(set(results["cls"]),
                      key=lambda c: order.index(c) if c in order else len(order)):
        sel = np.where(cls_arr == obj)[0]
        rows.append({
            "category": obj.replace(" ", "_"), "test_images": int(len(sel)),
            "image_auroc": round(float(roc_auc_score(
                np.array(results["gt_sp"])[sel], np.array(results["pr_sp"])[sel])), 5),
            "pixel_auroc": round(float(roc_auc_score(
                np.array(results["gt_px"])[sel].ravel(),
                np.array(results["pr_px"])[sel].ravel())), 5),
        })
    macro = {
        "categories": len(rows),
        "macro_image_auroc": round(float(np.mean([r["image_auroc"] for r in rows])), 5),
        "macro_pixel_auroc": round(float(np.mean([r["pixel_auroc"] for r in rows])), 5),
    }
    print("[stage2] per-category: " + json.dumps(rows), flush=True)
    print("[stage2] macro: " + json.dumps(macro), flush=True)

    payload = {
        "run": rows, "macro": macro,
        "settings": {"dataset": args.dataset, "k_shot": k_shot, "round": args.round,
                     "image_size": image_size, "dinov2_dtype": args.dinov2_dtype,
                     "memory_safe_cosine": bool(args.memory_safe_cosine),
                     "cosine_rows": args.cosine_rows,
                     "empty_cache_every": args.empty_cache_every,
                     "limit": args.limit,
                     "class_filter": "all" if all_classes else cls_target,
                     "argv": sys.argv[1:]},
        "timing": {"seconds": round(secs, 1),
                   "s_per_image": round(secs / max(len(indices), 1), 3),
                   "peak_vram_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2)},
    }
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"[stage2] wrote {args.report}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
