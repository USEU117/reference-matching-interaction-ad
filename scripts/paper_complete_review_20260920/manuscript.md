# Disentangling Representation Effects and Normal Reference Matching in Few-Shot Industrial Anomaly Localization

[[AUTHORS]]

[[AFFILIATIONS]]

Corresponding author: [[CORRESPONDING_AUTHOR]]

## Abstract

Combining pretrained visual encoders can improve few-shot industrial anomaly localization, but an apparent fusion gain may reflect changed weights, additional information, or altered normal-reference selection. We introduce a controlled decomposition that distinguishes these effects using frozen encoders and identical normal supports. An exact duplicate control isolates reweighting; complementary representation replacements measure the value of additional descriptors at fixed slot or branch-group weights. Crossing these constructions with joint and independent reference matching yields a paired interaction that separates absolute representation effects from their dependence on matching. For DINOv2-S, the two primary interactions on the Metal Parts Defect Detection (MPDD) dataset are +0.772 and +0.595 pixel average-precision percentage points, whereas their directions remain unresolved on the BeanTech Anomaly Detection (BTAD) dataset. Further validation supports positive interactions on MVTec AD and VisA, with VisA treated as in-domain. A separately specified KolektorSDD2 confirmation meets all four directional criteria for DINOv2-S and WideResNet50-2. Encoder and support-set analyses reveal meaningful variation across conditions. The resulting evidence shows why representation composition and reference selection should be assessed together and provides a practical way to distinguish additional-feature value from reweighting and matching effects. Code and reproduction materials are available at https://github.com/USEU117/reference-matching-interaction-ad.

Keywords: few-shot anomaly localization; frozen visual encoders; normal reference matching; fixed feature fusion; representation interaction.

## 1 Introduction

Industrial visual inspection must locate defects whose appearance is difficult to enumerate before deployment. A new product may provide only a few verified normal images, while representative scratches, contamination, missing parts, or structural defects remain unavailable. Industrial anomaly benchmarks reflect this setting through normal training images and heterogeneous test anomalies [@mvtec;@mpdd;@btad;@visa]. Few-shot anomaly localization therefore relies on a small normal support set to identify departures from expected appearance without training a target defect classifier.

Frozen pretrained encoders provide local descriptors that can be compared directly with a memory of normal support patches. AnomalyDINO demonstrates the effectiveness of DINOv2 features for this purpose [@anomalydino;@dinov2]. Combining encoders can enrich these descriptors, and recent systems already integrate visual and vision-language pretrained representations [@sea;@anomalyclip]. However, comparing the final scores of a two-branch and a three-branch system leaves a central design question unresolved: what makes the additional representation useful?

Two confounding effects complicate that comparison. First, adding an equally weighted branch also changes the weights of existing information. Copying one of two original branches adds no information, yet increases its effective weight from one half to two thirds. Replacing that copy with a different encoder is a distinct intervention whose benefit cannot be read directly from the original two-versus-three comparison. Second, the selected normal reference depends on how branch evidence is combined. Joint matching scores one shared support patch across branches before selecting the best candidate; independent matching allows each branch to select its own closest reference. A new descriptor can alter both the distance evidence and the chosen reference under a fixed matching rule.

This coupling makes absolute representation gains and matching dependence different questions. Independent matching has a lower or equal raw minimum-distance score, but average precision depends on the ranking of normal and anomalous pixels rather than score magnitude alone. Similarly, an added representation may help under both matching rules while showing little evidence that its gain depends on the rule. A controlled comparison must distinguish these possibilities instead of attributing the complete fusion gain to representation diversity.

Prior research establishes the importance of fusion design and consistent neighborhoods [@adnas;@scone;@muvad;@ncnets]. We build on those ideas to isolate a specific unresolved attribution problem in dense industrial localization. With frozen encoders, identical supports and fixed distance weights, we cross two representation replacements with two reference-selection rules. The resulting paired contrasts quantify the value of the added descriptor and the change in that value when the shared-reference constraint is removed. This provides an interpretable basis for deciding whether a fusion improvement comes from reweighting, additional information, or their interaction with reference selection.

The contributions are as follows.

1. **A controlled decomposition of additional-representation value.** We construct an exact duplicate control that exposes the weight change hidden in an ordinary two-versus-three-branch comparison. Replacing the duplicate at fixed slot weights isolates the representation change, while a complementary construction preserves the combined weight of the original visual branch and the added branch while retaining the AnomalyCLIP branch weight. Together, these controls distinguish new descriptor information from redistribution of existing evidence and make the attribution of a fusion gain testable.

2. **A paired characterization of representation–matching dependence.** We cross both representation constructions with joint and independent normal-reference matching on the same support bank. The resulting difference-in-differences quantifies how reference selection changes the effect of an added representation. Reporting this interaction alongside absolute representation effects separates two practically different outcomes: a useful representation with little established matching dependence, and a favorable matching interaction without a clear absolute gain. The contribution lies in this controlled formulation of the industrial fusion problem, using established matching operators and statistical contrasts.

3. **Separation of representation gains from reference-sharing sensitivity.** We identify a separation between an encoder's absolute utility and its sensitivity to reference selection. On MPDD, adding DINOv2-S produces positive matching interactions without establishing a positive absolute effect under independent matching; on BTAD, its absolute effects are positive while the interaction direction remains unresolved. WideResNet50-2, additional datasets and a separately specified KolektorSDD2 confirmation extend the analysis beyond this contrast. These patterns explain why a favorable fusion score alone is insufficient to choose an encoder or a reference-sharing rule, and provide a concrete basis for evaluating those choices together.

The study centers on this attribution problem. Its dual-encoder anchor, A1, provides a fixed reference for controlled comparisons; the results support conditional design choices rather than a universal encoder ranking.

## 2 Related Work

Research on industrial anomaly localization offers several ways to represent normal appearance, store reference evidence and combine pretrained features. Their differences matter for the present question: an improvement in a complete system can arise from training, reference coverage, fusion weights or reference selection. We review these choices together to explain which aspects our fixed-support comparison isolates.

Learned normal models identify anomalies through deviations from expected appearance or feature structure. SLSG combines generative pretraining, simulated anomalies and graph-based embedding modeling [@slsg]. RealNet uses diffusion-based anomaly synthesis with feature and residual selection [@realnet]. PaDiM instead fits multivariate Gaussian distributions to pretrained patch embeddings [@padim]. These methods offer different ways to estimate normality, with corresponding training, adaptation and sample-size requirements. Learning a normal distribution or reconstruction target can improve discrimination, but its effect is difficult to separate from encoder composition when the complete learning procedure changes. For our attribution question, this motivates freezing both the encoders and the target adaptation procedure; it does not imply that learned normal models are inferior under larger training sets.

Memory-based methods retain observed normal descriptors for local comparison. PatchCore combines a representative feature memory with nearest-neighbor scoring [@patchcore], while AnomalyDINO demonstrates effective few-shot localization with frozen DINOv2 patches [@anomalydino]. Their performance depends on the descriptor, the coverage of the reference memory and the preprocessing that defines the evaluated image region.

Recent work expands these choices beyond adding encoders. FEAD enriches sparse normal patterns through conditional feature transformation and multi-frequency modeling [@fead]. K-NG studies few-shot online detection using an evolving Neural Gas representation [@kng]. PGAD combines global invariance, multiscale local evidence and score calibration [@pgad], and FastRef refines normal prototypes at test time [@fastref]. SubspaceAD models frozen descriptors through a principal subspace [@subspacead], while DCP-SFR preserves shallow defect information in deep representations [@dcp_sfr]. These approaches highlight the roles of reference coverage, cue retention and adaptation. These methods address valuable limitations of sparse supports, yet changes to memory coverage or prototype adaptation also change which normal evidence a query can retrieve. Their overall improvements therefore answer a broader question than the effect of replacing one frozen descriptor. We hold the support identities and bank construction fixed to obtain that narrower comparison. The cost is that the study does not capture benefits from adaptive memories or target-specific feature learning.

Contrastive Language–Image Pretraining (CLIP) provides transferable visual and textual representations [@clip]. WinCLIP combines prompt ensembles and local visual features for zero- and few-shot detection [@winclip]. AnomalyCLIP learns object-agnostic normality and abnormality prompts [@anomalyclip], PromptAD learns from normal target samples [@promptad], and InCTRL uses in-context residual learning with sample prompts [@inctrl]. AA-CLIP introduces anomaly-aware alignment [@aaclip], FAPrompt develops fine-grained abnormality prompts [@faprompt], and UniVAD extends training-free reference-based detection across domains [@univad]. Their supervision, adaptation and inference paths differ. The AnomalyCLIP visual branch, denoted **C**, uses only visual descriptors; text scores and learned prompt outputs do not enter anomaly scoring. This makes the scoring paths comparable as visual descriptor branches. However, the inherited checkpoint still carries its training-data provenance, so removing text at inference does not turn an in-domain dataset into an unseen-domain test.

Sea-CLIP is especially relevant because it combines CLIP and DINOv2 representations for few-shot detection and includes shared-reference-like and independent nearest-neighbor evidence [@sea]. M3DM integrates RGB and point-cloud features with multiple memories [@m3dm], and CIF uses hypergraph structural commonality to guide multimodal reference memories [@cif]. The architectural analysis in 3D-ADNAS examines conditional benefits of fusion modules and fusion stages [@adnas]. These studies establish encoder combination and fusion design as existing approaches. Sea-CLIP is the closest practical motivation: combining CLIP and DINOv2 is already feasible, and reference selection already participates in such systems. A comparison of complete architectures, however, also changes feature processing or decoding. To interpret the contribution of an additional descriptor, its weight and support candidates must be controlled separately from those architectural choices.

Our emphasis is the attribution of the added representation's effect under controlled weights and references. We replace one descriptor while retaining support identities and slot weights, then measure how its effect changes under a different reference-sharing constraint. This differs from attributing a performance difference between complete architectures to one added representation, because other architectural and adaptation choices remain fixed.

Multi-view anomaly detection studies how neighborhood agreement relates to anomalous behavior. MUVAD uses neighborhoods to distinguish cross-view inconsistency from instances that are unusual across views [@muvad]. Neighborhood Consensus Networks align neighborhood structures [@ncnets], ECMOD combines contrastive learning with neighborhood-consistency information [@ecmod], and SCoNE addresses consistent local neighborhoods across views [@scone]. Shared and independent neighborhoods are therefore established concepts with relevance beyond industrial images. Their motivation also explains a tension in industrial localization: a shared reference can preserve correspondence across descriptors, whereas independent references can better accommodate each descriptor's nearest normal evidence. Neither rationale alone determines pixel-level ranking quality. This motivates measuring the representation effect under both rules rather than selecting a rule from the distance inequality.

Dense industrial localization introduces a specific setting: verified normal image supports, frozen patch descriptors and pixel-level evaluation. We investigate how changing the branch representation affects performance within this setting, using duplicate and balanced controls to identify the interaction with reference selection. The contribution concerns the controlled representation comparison and its empirical consequences, while the underlying neighborhood concepts come from prior work.

Taken together, prior work explains how normal evidence is learned or stored, how its representation is expanded and how references are shared. Existing methods motivate all three choices; our study connects them through a factorized comparison that separates representation gain from reweighting and quantifies its dependence on matching. This distinction allows an observed fusion improvement to be interpreted at the level of the design choice that produced it.

## 3 Framework and Methods

### 3.1 Problem Statement

For category $c$, the input consists of $K$ verified normal support images and a query image $x$. The support set is

{{eq:1}}

Here $x_i^c$ is support image $i$ of category $c$, and the query may be normal or anomalous. Category labels specify the relevant support bank; no target defect class is predicted. We use $p$ for a query patch, $r$ for an aligned support-patch index that contains both support-image identity and spatial position, and $b$ for a visual branch. The same index $r$ denotes the corresponding support location in every branch after spatial alignment. It does not require a query patch to match the same spatial coordinate in its support image.

The outputs are a continuous pixel anomaly map $A_t$ and an image-level score $s_{\mathrm{img},t}$, where the matching-rule label $t$ is **J** (joint matching) or **L** (independent matching). A displayed defect contour is derived from the map using a visualization threshold, as specified in Section 3.6. Test labels and masks are used only for offline evaluation and example selection. Dataset roles are distinguished in Section 4.1.1.

### 3.2 Framework Overview

Support-bank construction and query scoring use the same frozen visual paths. Each support image is encoded, spatially mapped to the common lattice, and normalized branch by branch. All support patches are retained, with one aligned row identity across branches. The bank is fixed for a category, support seed and $K$. A query follows the same feature path, searches that bank, and produces patch scores under one of the two matching rules. The query never updates the bank. Figure 1 shows the shared feature path, the two reference-selection rules and the weight-controlled representation comparisons.

{{figure:framework}}

The anchor combines DINOv2-B with the AnomalyCLIP visual path. Controlled variants duplicate the **B** descriptor (the DINOv2-B visual encoder) or replace that copy with a different frozen encoder. Shared resizing and smoothing convert patch scores to the continuous output map, whose spatial maximum gives the image score. Both matching rules are evaluated as fixed experimental conditions. Figure 2 shows their candidate selection. All encoders and fusion weights remain unchanged during target inference.

### 3.3 Normal Reference Matching

Let $F_b$ denote a branch feature tensor and $R_b$ its deterministic mapping to the common spatial lattice. At location $p$, branch-wise normalization produces a unit descriptor $g_{b,p}$. The branch distance between a query descriptor and a support descriptor is

{{eq:2}}

All reported constructions use nonnegative distance weights $w_b$ summing to one. The descriptors in Equation (2) are nonzero; numerical norm handling follows the archived implementation. With the same aligned candidate set $\mathcal{R}_c$ in every branch, joint matching is

{{eq:3}}

Joint matching first sums the branch distances for each single candidate $r$, then selects the candidate with the smallest weighted distance. Equivalently, concatenating the normalized branch descriptors with coefficients equal to the square roots of their distance weights yields a unit joint descriptor. Half its squared Euclidean distance equals the weighted cosine distance. Thus, feature coefficients and distance weights must not be confused: equal thirds in distance require equal square-root coefficients, followed by the corresponding joint normalization.

Independent matching reverses the order of branch combination and candidate minimization:

{{eq:4}}

Each branch can now select a different support patch. We denote the corresponding reference indices by $r_J$ and $r_{b,L}$ when discussing selected neighbors. Ties can select different indices with identical scores, so reference identity should be interpreted together with distance rather than as a unique explanation of every query.

The difference between the two raw patch scores is

{{eq:5}}

For every candidate, each branch distance is at least its own minimum; weighting and summing preserves that inequality, and minimizing the weighted sum does not reverse it. Equality holds when the branch minima admit a common minimizer. A positive gap measures the distance cost of imposing a common reference. Localization quality must be assessed separately, because average precision depends on the ordering of normal and anomalous pixels. The same distinction applies after common linear resizing and smoothing.

{{figure:matching}}

### 3.4 Representation Constructions and Weight Controls

Branch labels **B** (DINOv2-B visual encoder), **S** (DINOv2-S visual encoder), **C** (AnomalyCLIP visual branch) and **D** (WideResNet50-2 branch) denote the four frozen encoders. Table 1 defines the dual-encoder anchor **A1**, the duplicate-weight control **DUP**, the equal-weight replacement **TRI** and the balanced replacement **BAL**. Branch and construction labels, matching-rule identifiers and descriptive subscripts are upright; scalar variables and score functions are italic; feature vectors and full maps are bold italic.

{{table:design}}

Comparing DUP with A1 changes only how the fixed weights are split, without adding a new representation. DUP is also numerically equivalent to a two-branch B/C construction with weights two thirds and one third. Replacing the copied B descriptor in DUP with S produces TRI at identical slot weights. TRI minus DUP therefore measures the effect of that representation replacement rather than the entire difference between two and three encoders.

BAL provides a complementary comparison. In the S experiment, the combined DINO family weight remains one half, while C retains one half, allowing the B allocation to be split between B and S. In the D experiment, BAL preserves the total non-C weight but should not be called a DINO-family-preserving construction, since D is a convolutional ImageNet encoder. The weights are fixed experimental choices. DUP reuses the exact cached B descriptor, ensuring that the duplicate introduces neither new information nor feature-extraction randomness.

Figure 3 summarizes the constructions and their paired contrasts.

{{figure:constructions}}

### 3.5 Representation Effects and Their Matching Interaction

Let $P$ denote category-macro pixel average precision (AP), first calculated for a specified support condition and evaluation grid. Under matching rule $t$, the two representation effects are

{{eq:6}}

{{eq:7}}

The direct interaction is the difference between the same representation effect under L and J:

{{eq:8}}

{{eq:9}}

A positive interaction means that independent matching makes the representation change more beneficial or less harmful. It does not establish that the representation effect under L is itself positive. We therefore report the absolute effects together with the interactions. Conversely, a positive representation effect with an interaction interval spanning zero supports the usefulness of the representation under the observed conditions without clearly establishing dependence on matching.

The D comparison uses the same definitions with D replacing S. To compare their interactions, both are restricted to the same seeds and support budgets. For either construction label $q$ in TRI or BAL, the encoder comparison is

{{eq:10}}

All differences are formed within matched conditions and each resampling replicate before aggregation. This paired calculation directly estimates the interaction and the between-encoder difference, rather than comparing separate significance decisions.

### 3.6 Anomaly Outputs and Computational Cost

The patch scores form the matrix $a_t$ on the common lattice, are bilinearly resized to the $H$ by $W$ output canvas, and are smoothed with a Gaussian of standard deviation four pixels; $u$ indexes an output pixel. The image score is the maximum map response:

{{eq:11}}

The controlled evaluation restores patch scores to the retained image canvas, with dimensions $H$ by $W$; it is 448 by 448 for square images, 448 by 588 for BTAD category 03, and 630 pixels high by 224 pixels wide for KolektorSDD2. Ground truth follows the same resized and cropped image extent. Cross-method evaluation uses original-image coordinates, as described in Section 4.1.3. Pixel metrics use continuous scores. For illustrative contours only, thresholding produces

{{eq:12}}

Here $\tau_{\mathrm{vis}}$ is a visualization rule, not a universal fixed operating threshold. The archived qualitative examples use min-max normalization followed by 256-bin Otsu thresholding. No test mask determines this threshold. Equation (12) defines a display operation; the evaluated model outputs remain the continuous anomaly map and image score. A deployment threshold would require separate calibration.

If a bank contains $N_c$ normal patches, a query contains $n$ patches, and the combined descriptor dimension is $d$, exhaustive matching requires order $nN_cd$ distance work and order $N_cd$ feature storage. Joint matching can use one weighted concatenation index, whereas independent matching requires the corresponding branch-wise searches. Implementations can have different overheads even when the arithmetic order is the same. Larger support budgets increase reference storage, and an actual additional encoder incurs feature-extraction cost; reusing a duplicate does not incur that encoder cost. Here, training-free denotes the absence of target optimization; reference preparation and inference still incur computation.

### 3.7 Model Configuration

Table 2 records the frozen feature paths and the shared processing choices; Figure S1 shows the corresponding descriptor geometry. The B and S encoders use DINOv2 patch features [@dinov2]. C uses a CLIP Vision Transformer (ViT-L/14) visual backbone with AnomalyCLIP's diagonally prominent attention map (DPAM) path [@clip;@anomalyclip]. Its 518-pixel input yields a 37 by 37 grid; the final returned patch tensor is retained after projection, excluding the class token. Only the visual descriptor path contributes to inference.


The common lattice follows the B canvas. Inputs are resized with preserved aspect ratio to a short side of 448 pixels and cropped from the top left to dimensions divisible by 14. The C grid is mapped to the retained image extent. On BTAD category 03, the resized extent is 448 by 597 pixels and the retained canvas is 448 by 588. The corrected BTAD analysis maps both predictions and masks through the corresponding coordinates; extensions using the historical canonical mask convention are identified separately. Geometric consistency does not imply identical receptive fields or learned semantic alignment between encoders.

The D branch was specified before its results were generated. It uses ImageNet-pretrained WideResNet50-2, bilinearly resamples layer2 and layer3 to the B lattice, concatenates their 512- and 1024-channel outputs, and normalizes the resulting 1536-dimensional descriptor. Its query-feature cache is stored in float16 and converted to float32 for normalization and scoring; this storage choice is recorded in the reproduction manifest. Branch dimensions are listed separately in Table 2. Exploratory slots additionally use original DINO ViT-S/8 (**E1**), ConvNeXt-Tiny (**E2**), and Swin-Tiny (**E3**). They follow the same mapping and unit-normalization steps. KolektorSDD2 uses its prespecified 630 by 224 canvas for B, S and D; C retains its own input path before spatial mapping. All encoder parameters remain frozen, so target optimizer, learning rate, training epochs, and training-loss curves are not applicable.

{{table:models}}

## 4 Experimental Evaluations

### 4.1 Experimental Design

#### 4.1.1 Datasets and Reference Protocol

We evaluate the representation-by-matching design on the Metal Parts Defect Detection dataset (MPDD), the BeanTech Anomaly Detection dataset (BTAD), MVTec Anomaly Detection (MVTec AD), Visual Anomaly (VisA) and KolektorSDD2 [@mpdd;@btad;@mvtec;@visa;@ksdd2]. Table 3 distinguishes their roles and support scopes. MPDD informed development. BTAD and MVTec AD serve as external validation datasets for the frozen comparison, although both had been explored before this analysis. VisA is in-domain validation because the inherited AnomalyCLIP checkpoint was trained on VisA. This provenance applies even though inference uses only visual descriptors. Only the KolektorSDD2 directional confirmation was specified before encoding that dataset's features.

{{table:protocol}}

For each category and seed, verified normal training images form a fixed support sequence; smaller $K$ values are nested prefixes. The same supports and query images are used by every method in a paired comparison. Seeds 0, 1 and 2 crossed with $K$ equal to 1, 2, 4 and 8 yield twelve dataset-level support conditions; the primary BTAD analysis uses seeds 0 and 1 and therefore eight conditions. These are repeated evaluations on common test data, not independent datasets. KolektorSDD2 supplies 1004 test images, including 110 with nonempty defect masks and 894 without defects; only verified normal training images enter the support bank.

The original D extension and the matched five-encoder comparison use seeds 0 and 1 with $K$ equal to 1 and 4 on MPDD and BTAD. Additional E1–E3 results on twelve conditions are reported as exploratory scope checks. A separate eight-seed extension uses seeds 0 through 7 and all four budgets. Its BTAD category-03 masks follow the canonical convention, so its estimates are not substituted for the corrected-geometry primary estimates.

#### 4.1.2 Controlled Constructions and External Baselines

The primary matrix includes single-branch B, S and C and both matching rules for A1, DUP, TRI and BAL. Single-branch paths diagnose descriptor quality, while the eight combined configurations identify the two interaction contrasts. The D extension adds D-only scoring and its TRI/BAL variants. E1–E3 entered after the S and D results and are exploratory encoder substitutions. They test sensitivity to the added representation.

AnomalyDINO and PatchCore provide native-method context [@anomalydino;@patchcore]. AnomalyDINO is evaluated with and without support rotation. PatchCore includes the 224-pixel input and 1024-dimensional projected-feature configuration as well as the earlier local 128-pixel and 256-dimensional configuration. Both are retained to reveal configuration sensitivity. Each method keeps its own preprocessing, features and search implementation, while support seeds and budgets are matched. This comparison assesses practical configurations and does not isolate the matching factor or constitute a comprehensive state-of-the-art benchmark.

#### 4.1.3 Metrics and Statistical Inference

Pixel average precision (AP) is the primary localization metric. Scores and labels are pooled over test images within each category, then category APs are averaged equally. Dataset-level estimates average the applicable support conditions equally. This differs from pooling all categories into a single AP or averaging per-image AP. Pixel area under the receiver operating characteristic curve (AUROC) is a secondary diagnostic. Performance tables use AP on the 0–1 scale; effects and interactions use AP percentage points, equal to 100 times an AP difference.

Three spatial evaluation conventions remain separate. The main bootstrap analysis samples pixels on a regular stride-eight grid of the retained output canvas. Full-pixel estimates use every output-canvas pixel; finer stride-four checks test sensitivity to the sampled grid. External-method comparisons instead map predictions into original-image coordinates and evaluate their common valid intersection. Geometry conventions, pixel strides and support scopes are stated with each table; scores from these settings are not interchangeable.

We use 1000 paired image-level bootstrap replicates. Images are sampled with replacement within each fixed category, without additional normal/abnormal stratification. Each sampled image contributes its evaluated pixels as a block. The same deterministic replicate stream, based on seed 20260913 together with dataset identity, category identity and replicate index, is shared across methods and support conditions. Contrasts are formed within each replicate after the required category and condition aggregation. Intervals are conditional on observed categories and support manifests; they do not estimate uncertainty over unseen datasets or arbitrary future support sets.

The primary four S interactions, four D interactions and four matched D-minus-S contrasts each have their own exploratory four-comparison family, reported with 98.75% percentile intervals. The extended four-dataset S table has eight cells and reports 99.375% intervals; these are approximate Bonferroni adjustments. Encoder-transfer comparisons retain a separate four-cell family per encoder, with no simultaneous guarantee over all exploratory analyses. With 1000 replicates, extreme percentile endpoints have limited precision.

KolektorSDD2 retains its specified conjunction criterion: all four S/D interactions must be positive and their individual 95% intervals must exclude zero. This conjunction uses individual intervals and does not imply simultaneous 95% coverage. Excluding zero supports an interaction direction under the stated protocol; practical value also depends on the effect size and absolute representation gain. An interval spanning zero leaves the direction unresolved.

Observed condition-averaged point estimates and bootstrap means are labelled separately. Full-pixel estimates provide resolution checks; full-pixel bootstrap intervals are unavailable. The eight-seed study describes support sensitivity separately rather than treating its between-seed variation as part of the primary conditional interval.

#### 4.1.4 Implementation and Reproducibility

The recorded machine has an NVIDIA GeForce RTX 3060 Laptop GPU with 6 GB VRAM, an Intel Core i9-12900H processor and 16 GB RAM. Encoders run in evaluation mode, with cached query features reused across controlled variants. Exact nearest-neighbor search implements Section 3, using Facebook AI Similarity Search (FAISS) where applicable [@faiss]. Feature extraction, reference construction and score evaluation are distinct computational stages; cached-stage times cannot be interpreted as end-to-end deployment latency.

The primary BTAD tables use corrected category-03 coordinates. The four-dataset and eight-seed extensions retain their archived canonical-mask convention and are reported separately. Geometric audits verify the retained image extent and support nesting. Duplicate descriptors reuse the exact cached values. Reproduction uses support manifests, frozen branch specifications and paired bootstrap streams; no target loss is optimized and no test-mask feedback selects a normal reference.

Resource reporting is restricted to measurements whose stages and devices are identifiable. VisA's extension includes mixed CPU/GPU execution and is excluded from speed or GPU-memory rankings. A separate synchronized benchmark now measures all six configurations on six MPDD units, including query feature extraction. Its reference preparation and query scoring boundary is stated in Section 4.2.14; the older stage records remain separate.

### 4.2 Results and Analysis

{{results}}

## 5 Conclusion

This study separates the value of additional frozen visual representations from reweighting and normal-reference selection in few-shot industrial anomaly localization. Exact duplication and complementary fixed-weight replacements make the representation change explicit. Crossing these controls with joint and independent matching reveals whether its value depends on sharing a normal reference, beyond any absolute gain from the added encoder.

The results demonstrate why this distinction matters. DINOv2-S shows positive matching interactions on MPDD, MVTec AD and VisA, while its interaction direction remains unresolved on BTAD despite positive absolute representation effects. WideResNet50-2 yields positive interactions on both primary datasets, and the separately specified KolektorSDD2 confirmation meets all four directional criteria. Encoder and support-set analyses identify substantial variation; correspondence transformations preserve positive MPDD interactions within the tested settings, while BTAD interval directions remain unresolved.

The resulting design guidance is to evaluate representation composition and reference selection together under explicit weight controls. Its scope remains conditional on the tested encoders, support sets and dataset provenance. Future work should extend prospective comparisons to additional production settings, test correspondence effects under broader prospective conditions, and evaluate calibrated thresholds and deployment costs across more datasets and operating conditions. These steps would connect the controlled attribution of fusion gains to practical inspection decisions.

## Data and Code Availability

MPDD, BTAD, MVTec AD, VisA and KolektorSDD2 are distributed by their respective providers [@mpdd;@btad;@mvtec;@visa;@ksdd2]. The local study archive retains support manifests, feature specifications, geometry revisions, prediction caches, per-condition metrics, bootstrap outputs and analysis scripts. A local reproduction package includes the analysis entry points, dependency records, support manifests and figure bindings. Raw datasets and feature caches remain separate.

Licensing is split three ways. The code is released under the MIT Licence (repository root `LICENSE`, Copyright (c) 2026 LiYuening). The derived artefacts released with the package - derived tables, figures and the manuscript sources - carry the same licence as the code; any item that the root `LICENSE` does not explicitly cover remains for the authors to confirm. Dataset licences are separate and are not covered by the code licence, and the datasets themselves are not redistributed here. The public repository holding the code and the reproduction materials is https://github.com/USEU117/reference-matching-interaction-ad; a permanent archive DOI for the complete study has not yet been established.

Funding: [[FUNDING]]. Competing interests: The authors declare no competing interests. Ethics: Not applicable; the study analyses industrial image data only, with no human or animal subjects.

## References

{{references}}


## Supplementary Method Figures

{{figure:encoders_geo}}

## Supplementary Results Figures

{{figure:shared_op_ablation}}

{{figure:extra_cases}}

{{figure:stability}}

{{figure:speed_vram}}

The accompanying figure deck includes the complete set of 36 category-level comparisons with the native methods, using the same shared-region evaluation as Table 11. These selected examples supplement the aggregate results; they are not an independently sampled performance estimate. Their source records preserve the sample identities, per-image AP and common-region geometry.
