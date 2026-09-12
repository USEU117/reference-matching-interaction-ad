# E8-6 Method clarifications (text / formula / caption vs code)

Rule for this document: **the historical implementation is not modified.** This
file only records what the code actually does and whether the manuscript says
the same thing. Where they differ, the discrepancy is reported, not silently
"fixed".

## 1. Post-processing order: bilinear resize first, then Gaussian

Code (authoritative, frozen):

- `methods/anomalydino/src/utils.py:14-17`
  ```python
  def dists2map(dists, shape):
      return gaussian_filter(
          cv2.resize(dists, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR), sigma=4
      )
  ```
- Project harness `scripts/validation_handoff_20260911/common.py:132-138`
  (`dists_to_maps`) performs exactly the same two steps in the same order.

Manuscript wording:

- `docs/manuscript_english_polished_20260906/English_content.md:106` —
  "We arrange patch scores on the DINO grid as a score matrix a, bilinearly
  resize to 448 x 448, and apply Gaussian smoothing with sigma = 4 pixels at
  that output resolution."
- same file `:110` defines Resize as bilinear resizing to 448 x 448 and the
  Gaussian operator as smoothing;
- `:112` Figure 3 caption — "its scores are bilinearly resized and
  Gaussian-smoothed";
- `:146` Table 1 row — "Post-processing | Bilinear resize, then Gaussian
  sigma = 4; image maximum".

**Verdict: CONSISTENT.** The order (resize -> Gaussian at 448) is stated in the
text, the equation legend, the Figure 3 caption and Table 1, and matches both the
vendored official code and the project harness. No manuscript change required.

## 2. DPAM vs DAPM spelling

The official AnomalyCLIP source tree in this repo contains **both** spellings:

- parameter / attribute name `DPAM_layer`:
  `methods/AnomalyCLIP-main/AnomalyCLIP_lib/AnomalyCLIP.py:298,303,345,346,347,356,377,478,479`
  (e.g. `def forward(self, x, out_layers=[6,12,18,24], DPAM_layer=None, ffn=False)`);
- method function name `DAPM_replace`:
  `AnomalyCLIP.py:345` `def DAPM_replace(self, DPAM_layer)`, called as
  `model.visual.DAPM_replace(DPAM_layer = 20)` in
  `methods/AnomalyCLIP-main/test.py:71`, `test_one_example.py:64`, `train.py:42`.
- upstream comments keep the `DPAM_layer` spelling: `train.py:70-72`
  ("DPAM_layer represents the number of layer refined by DPAM from top to
  bottom ... DPAM_layer = 20 as default").

Manuscript wording:

- `English_content.md:137` Table 1 — "DPAM / layer output | DPAM_layer = 20;
  request 6/12/18/24; retain layer 24, exclude CLS";
- `:116` — "removes the DPAM-modified CLIP branch".

**Verdict: MINOR NAMING MISMATCH, not a factual error.** The manuscript uses the
upstream *parameter* spelling `DPAM` (`DPAM_layer`), while the upstream *method
function* is spelled `DAPM` (`DAPM_replace`). Both denote the same
Depth-Aware Patch Matching module. Recommended action (documentation only, does
not touch code): add a one-line footnote at the first use — "the upstream
reference implementation names the module's method `DAPM_replace` while its
layer hyper-parameter is `DPAM_layer`; the value used throughout is 20." No
implementation change is made or implied.

## 3. Pure-visual identity; `anomalyclip_text` is a historical directory name

The cached CLIP branch is stored under directories named `anomalyclip_text`.
This is a **historical artifact name** and must not be read as evidence that a
text score participates in inference.

Evidence that the branch is visual-only:

- `scripts/export_anomalyclip_mpdd_features.py` exports **visual patch tokens**
  from the frozen CLIP ViT-L/14@336 visual tower; no prompt learner and no text
  tower output is exported or stored.
- The E0 input manifest records the branch as a 768-d patch tensor with a
  37x37 native grid at 518 input (`E0/input_manifest.json`), i.e. the projected
  visual patch tensor, not a text embedding.
- `English_content.md:150` — "These counts exclude the unused text tower and
  prompt learner."
- `English_content.md:118` — "The CLIP-image-only control likewise uses its
  visual descriptors without text, with matched reference identities and the
  same downstream metric convention."
- `docs/AI_HANDOFF_VALIDATION_AND_INNOVATION_20260911_CN.md:367` — the artifact
  tag `anomalyclip_text` is an old name and the exporter actually writes visual
  patches; one "must not infer from the string that a text score was used".

**Verdict: manuscript is consistent and already declares visual-only.** No text
edit required; the paragraph above is the explicit reconciliation for reviewers
who see the directory name.

## 4. Summary table

| Item | Code | Manuscript | Verdict | Action |
|---|---|---|---|---|
| Order of resize/Gaussian | resize to 448 then `gaussian_filter(sigma=4)` | same, in text + Eq. legend + Fig.3 caption + Table 1 | CONSISTENT | none |
| DPAM / DAPM | param `DPAM_layer`, method `DAPM_replace` | uses `DPAM` | naming mismatch (same module) | optional footnote |
| Branch identity | visual patch tokens only | declared visual-only | CONSISTENT | none |

## 5. Cost measurement calibers are not interchangeable

Two cost tables in this handoff measure different things and must not be read as
the same number repeated:

| Table | Unit measured | Scope | Stage boundary |
|---|---|---|---|
| `E1/costs_per_config.csv` = `E4/cost_delta.csv` | project harness, one category, K=4 | `metal_plate` only, single shot | CPU faiss scoring only (no 448 resize / Gaussian) |
| `E8/end_to_end_cost_*.csv` | staged end-to-end, p50/p95 | 2 shots x 2 categories (`bracket_black`, `metal_plate`) | memory-bank build + steady state **including** 1-NN search, bilinear resize to 448 and Gaussian σ=4 per image |

Consequently, for the same configuration B+C, `E1`/`E4` report a per-image
latency of ~53.5 ms while `E8` reports a p50 of ~102 ms: the E8 steady-state
stage carries the post-processing that E1/E4 excluded, and it averages over two
categories and two shot settings. Both use `faiss.IndexFlatL2` on CPU for the
1-NN search. Report the two tables separately, or compare only rows produced by
the same table; do not subtract one from the other.

The E8 encoder-stage forward times (ViT-B/14 p50 80.5 ms, ViT-S/14 p50 48.6 ms)
are a third caliber again: single-image `prepare_image` + `extract_features` on
CUDA without cache I/O, memory-bank build or post-processing.

No file under `methods/AnomalyCLIP-main/` or `methods/anomalydino/` was modified,
and no historical result was recomputed for this section.
