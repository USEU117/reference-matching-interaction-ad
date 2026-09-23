# Third-Party Notices

This repository contains **research code and results** for a few-shot industrial anomaly-detection
study. The project's own code is released under the MIT license (see the root [`LICENSE`](LICENSE)).
That license covers the project's original code only. The items below keep their own terms, and the
project's MIT license does **not** override them.

**Summary of what this repository does NOT redistribute:**

- No raw dataset images or masks are redistributed here. Datasets must be obtained from their
  original providers.
- No pretrained model weights are redistributed here. Weights must be obtained from their original
  providers.
- Third-party method source trees are not redistributed here; only upstream provenance and local
  diffs are kept (see section 3).

Where a license term could not be confirmed from a first-hand source, it is marked **to be verified**
rather than guessed.

---

## 1. Datasets

This repository does **not** redistribute the raw datasets. All datasets are downloaded separately
from their providers by the user and remain subject to their own licenses. If you cite or reuse any
part of the derived material in this repository (figures, per-image maps, derived views), you must
follow the attribution rules of the corresponding dataset license.

| Dataset | License | Attribution required if referenced |
|---|---|---|
| MVTec AD | **CC BY-NC-SA 4.0** (source: <https://www.mvtec.com/research-teaching/datasets/mvtec-ad>) | Credit the creator (MVTec Software GmbH); link to the CC BY-NC-SA 4.0 deed; state that changes were made; **non-commercial use only**; ShareAlike — derivatives must be licensed under the same terms. |
| VisA | **CC BY 4.0** (source: <https://registry.opendata.aws/visa/>; project: <https://github.com/amazon-research/spot-diff>) | Credit the dataset authors (Amazon / the Spot-the-Difference authors); link to the CC BY 4.0 deed; state that changes were made. Commercial use is allowed by the license. |
| BTAD | **CC BY-SA 4.0** (source: <https://github.com/pankajmishra000/VT-ADL>) | Credit the original dataset authors (VT-ADL authors); link to the CC BY-SA 4.0 deed; state that changes were made; ShareAlike — derivatives must be licensed under the same terms. Note: the MIT file in the upstream repository root applies to the VT-ADL **code**, not to the BTAD data. |
| MPDD | **CC BY-NC-SA 4.0** (source: <https://github.com/stepanje/MPDD>) | Credit the dataset authors; link to the CC BY-NC-SA 4.0 deed; state that changes were made; **non-commercial use only**; ShareAlike. Note: the local copy here was obtained from a third-party mirror rather than the official distribution channel; the exact upstream provenance and the scope of permitted redistribution are **to be verified** with the provider. |
| KolektorSDD2 (KSDD2) | **CC BY-NC-SA 4.0** (source: <https://www.vicos.si/resources/kolektorsdd2/>) | Credit the dataset authors (ViCoS); link to the CC BY-NC-SA 4.0 deed; state that changes were made; **non-commercial use only**; ShareAlike. Commercial use requires contacting the authors. |

---

## 2. Derived reference-view images (license-bearing)

The directory `experiments/dynamic_fusion/v2/branch_cache_queue/reference_views/` contains
**945 PNG images**. These are **derived views** of the BTAD and MPDD *normal* reference images,
produced by brightness and contrast perturbations (factors 0.90 / 1.10, plus an identity copy) via
`scripts/prepare_normal_reference_views.py` (see `VIEW_SPECS` in that script).

Consequences:

- These images are **derivative works of BTAD (CC BY-SA 4.0) and MPDD (CC BY-NC-SA 4.0)** and remain
  bound by those licenses: **attribution**, **ShareAlike** for BTAD/MPDD derivatives, and
  **non-commercial** for MPDD.
- The project's **MIT license does NOT cover these images.** Treat them as dataset-derived material,
  not as project code.
- If you reproduce or redistribute these derived views, keep the origin attribution for BTAD and
  MPDD and respect the non-commercial (MPDD) and ShareAlike (BTAD/MPDD) conditions.

---

## 3. Upstream method repositories (`methods/`, `patches/`)

The `methods/` directory holds **local checkouts** of third-party anomaly-detection implementations;
they are **git-ignored and not redistributed** by this repository. The tracked `patches/` directory
contains **only local diffs** against those upstream trees, not upstream source:

| Upstream project | Local diff kept under `patches/` |
|---|---|
| AnomalyCLIP | `patches/anomalyclip-test-cache.patch` |
| AnomalyDINO | `patches/anomalydino-unified.patch` |
| PatchCore | `patches/patchcore-unified-cache.patch` |
| PromptAD | `patches/promptad-export-npz.patch`, `patches/promptad-unified-manifest.patch` |
| WinCLIP / WinCLIP+ | `patches/winclip-unified.patch`, `patches/winclip-mvtec-unified.patch` |

Each upstream project keeps its own license. Only the upstream provenance and the local diffs are
kept here; **the upstream source code is not redistributed**. UniVAD and SubspaceAD are also present
under `methods/` for local experimentation; their upstream licenses are **to be verified** against
each upstream repository before any redistribution.

---

## 4. Pretrained weights

No pretrained model weights are redistributed in this repository (size and licensing). This applies
to, among others, **DINOv2**, **CLIP**, **WideResNet50-2**, **BERT**, **GroundingDINO**, and
**SAM-HQ**. Each must be obtained from its original provider and used under that provider's license.
The root MIT license does not cover third-party weights. The per-file inventory (paths, byte sizes,
SHA-256, acquisition notes) is recorded in [`docs/MODEL_WEIGHTS.md`](docs/MODEL_WEIGHTS.md); the
license status for any weight not explicitly listed there is **to be confirmed**, and no license is
inferred in its place.

---

## 5. Items marked "to be verified"

- MPDD: exact upstream provenance and redistribution scope (local copy came from a mirror).
- UniVAD / SubspaceAD upstream licenses.
- License status of pretrained weights not explicitly recorded in `docs/MODEL_WEIGHTS.md`.

These are stated as open items rather than filled with assumed terms.
