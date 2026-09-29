"""Child-process entry point: arm the mirror paths, then run one archived module.

Usage (the orchestrators set these through the environment, not on the command line):

    python scripts/five_seed_support_variance_20260928/fsv_run.py <the module's own argv>

    FSV_TARGET   module name to import and run, e.g. run_baseline_anomalydino
    FSV_CALL     optional "module:function" - call that function instead of main(),
                 with FSV_KWARGS (JSON object) as keyword arguments
    FSV_POOL     if set, ProcessPool workers arm themselves too (needed by the region
                 evaluation, which otherwise reads the archived directories)

``FUSION_CANONICAL_ROOT`` is set before anything project-related is imported, so modules
that read it at import time (engine_v2, s8_common_region) resolve the five-seed root.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))

sys.path.insert(0, str(ROOT / "scripts/representation_matching_interaction_20260914"))
sys.path.insert(0, str(ROOT / "scripts/baseline_expansion_20260921"))
sys.path.insert(0, str(ROOT / "scripts/paper_evidence_closeout_20260914"))
sys.path.insert(0, str(ROOT / "scripts/unified_fusion_paper_support_v1"))

os.environ["FUSION_CANONICAL_ROOT"] = str(
    ROOT / "experiments/dynamic_fusion/five_seed_support_variance_20260928/canonical")

import fsv_common as P  # noqa: E402  (must come after the environment is prepared)


def main() -> int:
    import importlib

    call = os.environ.get("FSV_CALL")
    target = os.environ.get("FSV_TARGET")
    module_name = call.partition(":")[0] if call else target
    if not module_name:
        raise SystemExit("FSV_TARGET (or FSV_CALL) must be set")
    P.arm()
    module = importlib.import_module(module_name)
    # arm() has to run *again* now that the target module is in sys.modules: the
    # per-module redirections (NEW/R/SPLITS/RAW_OUT/...) are applied by attribute.
    P.arm()
    if os.environ.get("FSV_POOL"):
        P.enable_pool_initializer()
    if call:
        _, _, function_name = call.partition(":")
        kwargs = json.loads(os.environ.get("FSV_KWARGS") or "{}")
        result = getattr(module, function_name)(**kwargs)
        print(json.dumps({"fsv_call": call, "kwargs": kwargs, "result": result},
                         ensure_ascii=False, default=str))
        return 0
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
