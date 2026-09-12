"""Verify a chunked replacement for `F.cosine_similarity` used by UniVAD's forward.

UniVAD calls `F.cosine_similarity(x1, x2, dim=2)` with x1 of shape (Na,1,C) and x2 of
shape (1,Nb,C); the broadcast product is (Na,Nb,C) = 1024*1024*1024 fp32 = 4 GiB, which
is what OOMs on this card. The chunked version normalises both operands first and then
walks the broadcast axis in blocks - the same normalisation, the same elementwise product
and the same per-row reduction, just not materialised all at once.

Checks performed here:
  1. does the stock op mutate its inputs in place?
  2. does the chunked version agree with the stock op (and by how much)?
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

torch.manual_seed(0)


def chunked(x1, x2, dim=2, eps=1e-8, rows=64):
    bshape = torch.broadcast_shapes(x1.shape, x2.shape)
    n1 = x1 / x1.pow(2).sum(dim=dim, keepdim=True).sqrt().clamp_min(eps)
    n2 = x2 / x2.pow(2).sum(dim=dim, keepdim=True).sqrt().clamp_min(eps)
    axis = 0 if n2.shape[0] == 1 else 1
    base, other = (n1, n2) if axis == 0 else (n2, n1)
    assert other.shape[axis] == 1 and base.shape[axis] == bshape[axis], (base.shape, other.shape)
    out = []
    for s in range(0, base.shape[axis], rows):
        piece = base[s:s + rows] if axis == 0 else base[:, s:s + rows]
        out.append((piece * other).sum(dim=dim))
    return torch.cat(out, dim=axis)


# 1. in-place mutation check
a = torch.randn(3, 1, 5)
b = torch.randn(1, 4, 5)
a0, b0 = a.clone(), b.clone()
_ = F.cosine_similarity(a, b, dim=2)
print("stock mutates x1:", not torch.equal(a, a0), " x2:", not torch.equal(b, b0))

# 2. agreement on the real shape (small Na so the stock op fits in host-visible memory)
for Na, Nb, C in [(1024, 1024, 1024), (256, 1024, 1024), (37, 1024, 1024), (1024, 512, 1024)]:
    x1 = torch.randn(Na, 1, C, device="cuda")
    x2 = torch.randn(1, Nb, C, device="cuda")
    ref = F.cosine_similarity(x1, x2, dim=2)
    got = chunked(x1, x2, dim=2, rows=32)
    d = (ref - got).abs().max().item()
    scale = ref.abs().max().item()
    print(f"Na={Na:5d} Nb={Nb:5d} C={C}: max_abs_diff={d:.3e} (max|ref|={scale:.3f}) "
          f"allclose={torch.allclose(ref, got, atol=1e-6)}")
    del x1, x2, ref, got
    torch.cuda.empty_cache()

# 3. as used by UniVAD: x1 -> (Na,1,C) then max over dim=1
x1 = torch.randn(1024, 1, 1024, device="cuda")
x2 = torch.randn(1, 1024, 1024, device="cuda")
ref = torch.max(F.cosine_similarity(x1, x2, dim=2), dim=1)[0]
got = torch.max(chunked(x1, x2, dim=2, rows=32), dim=1)[0]
print("max-over-dim1 max_abs_diff:", (ref - got).abs().max().item(),
      "allclose:", torch.allclose(ref, got, atol=1e-6))
print("DONE", flush=True)
