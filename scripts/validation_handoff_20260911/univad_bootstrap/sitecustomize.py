"""Startup bootstrap for running the vendored official UniVAD on this machine.

Put this directory on PYTHONPATH when launching the official entry points
(`segment_components.py` / `test_univad.py`); `site` imports `sitecustomize`
automatically, so the vendored sources stay byte-identical.

It provides two things.

1. `models/GroundingDINO` is added to `sys.path`.
   Upstream's README installs GroundingDINO with `pip install -e models/GroundingDINO`,
   and `groundingdino/datasets/transforms.py` uses absolute `from groundingdino...`
   imports, so the package has to be importable by name. This reproduces the *path*
   half of that editable install.

2. A stand-in for the compiled `groundingdino._C` op.
   The other half of `pip install -e` is the C++/CUDA extension
   `MultiScaleDeformableAttention`. It cannot be built on this machine: there is no
   CUDA toolkit (`nvcc` is absent), and `csrc/MsDeformAttn/*.cu` needs it. Without the
   extension `ms_deform_attn.py` still imports (the `from groundingdino import _C` is
   wrapped in try/except) but any CUDA forward pass dies with `NameError: _C`.

   We therefore publish a module object as `groundingdino._C` whose
   `ms_deform_attn_forward` / `ms_deform_attn_backward` delegate to GroundingDINO's own
   reference implementation, `multi_scale_deformable_attn_pytorch` - the exact code the
   upstream repo runs in its CPU branch. The arithmetic is therefore upstream's, not an
   approximation introduced here; only the execution path changes (pure PyTorch instead
   of the fused CUDA kernel), which costs speed, not accuracy.

   Both package instances see this module: upstream imports the model classes through
   the relative path (`models.GroundingDINO.groundingdino...`) while the op is pulled in
   with the absolute `from groundingdino import _C`, and the absolute name is the one we
   register.
"""
from __future__ import annotations

import os
import sys
import types

try:
    import torch
except Exception as _exc:  # noqa: BLE001
    torch = None
    print(f"[univad-bootstrap] torch unavailable: {type(_exc).__name__}: {_exc}", file=sys.stderr)

_UNIVAD = os.path.abspath(os.environ.get("UNIVAD_DIR", os.getcwd()))
_GD = os.path.join(_UNIVAD, "models", "GroundingDINO")
if os.path.isdir(_GD) and _GD not in sys.path:
    sys.path.insert(0, _GD)


def _reference_msda_module() -> types.ModuleType:
    shim = types.ModuleType("groundingdino._C")
    shim.__doc__ = (
        "Pure-PyTorch stand-in for the uncompiled MultiScaleDeformableAttention CUDA op. "
        "Delegates to GroundingDINO's own multi_scale_deformable_attn_pytorch reference code."
    )

    def _ref():
        from groundingdino.models.GroundingDINO.ms_deform_attn import (
            multi_scale_deformable_attn_pytorch,
        )
        return multi_scale_deformable_attn_pytorch

    def ms_deform_attn_forward(value, value_spatial_shapes, value_level_start_index,
                               sampling_locations, attention_weights, im2col_step):
        return _ref()(value, value_spatial_shapes, sampling_locations, attention_weights)

    def ms_deform_attn_backward(value, value_spatial_shapes, value_level_start_index,
                                sampling_locations, attention_weights, grad_output,
                                im2col_step):
        v = value.detach().requires_grad_(True)
        loc = sampling_locations.detach().requires_grad_(True)
        att = attention_weights.detach().requires_grad_(True)
        out = _ref()(v, value_spatial_shapes, loc, att)
        grads = torch.autograd.grad(out, (v, loc, att), grad_outputs=grad_output,
                                    allow_unused=True)
        return tuple(grads)

    shim.ms_deform_attn_forward = ms_deform_attn_forward
    shim.ms_deform_attn_backward = ms_deform_attn_backward
    return shim


def _install_c_shim() -> None:
    if "groundingdino._C" in sys.modules:
        return
    if torch is None:
        print("[univad-bootstrap] _C shim skipped: torch is unavailable", file=sys.stderr)
        return
    shim = _reference_msda_module()
    sys.modules["groundingdino._C"] = shim
    try:
        import groundingdino
        groundingdino._C = shim
    except Exception:  # noqa: BLE001
        pass
    print("[univad-bootstrap] groundingdino._C -> reference PyTorch MultiScaleDeformableAttention "
          "(the CUDA op cannot be compiled: no CUDA toolkit on this machine)", file=sys.stderr)


_install_c_shim()
