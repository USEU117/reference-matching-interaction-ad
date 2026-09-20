"""One-off probe: is the local128 / official224 preprocess difference real?

The benchmark measured `MVTecDataset.__getitem__` at 18.4 s summed over the six local128 units
against 14.3 s for official224, although local128 resizes to a *smaller* target (144/128 vs
256/224).  This times exactly that transform list on the same files, both ways, without any
CUDA work.
"""
import importlib.util
import statistics as st
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "methods/patchcore/patchcore-inspection-main/src"))
import torch  # noqa: E402
from torchvision import transforms  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "mvtec_mod", ROOT / "methods/patchcore/patchcore-inspection-main/src/patchcore/datasets/mvtec.py")
mvtec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mvtec)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
VIEWS = ROOT / "experiments/dynamic_fusion/representation_matching_interaction_20260914/_bench_speed_vram/patchcore_views"

for category in ("bracket_black", "bracket_brown", "bracket_white"):
    for unit in ("mpdd_s0_k1", "mpdd_s0_k4"):
        root = VIEWS / f"{unit}_{category}"
        for label, resize, imagesize in (("local128", 144, 128), ("official224", 256, 224)):
            dataset = mvtec.MVTecDataset(str(root), classname=category, resize=resize,
                                        imagesize=imagesize, split=mvtec.DatasetSplit.TEST,
                                        seed=0)
            samples = list(dataset.data_to_iterate)
            for pass_index in range(2):
                t0 = time.perf_counter()
                for index in range(len(samples)):
                    dataset[index]
                elapsed = time.perf_counter() - t0
                if pass_index == 1:
                    src = dataset.transform_img.transforms[0]
                    print("%-22s %-12s n=%-4d %-11s %.3f s  (resize->%s crop->%s)"
                          % (f"{unit}_{category}", label, len(samples), "warm+timed",
                             elapsed, resize, imagesize), flush=True)
