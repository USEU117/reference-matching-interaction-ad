# Interaction between Additional Visual Representations and Normal Reference Matching in Few-Shot Industrial Anomaly Localization

## Abstract

Few-shot industrial anomaly localization uses a small set of normal images to identify anomalous regions in unseen queries. Combining pretrained visual encoders can enrich the available descriptors, but an additional branch also changes effective weights and the normal patches selected as references. We study whether the benefit of an additional representation depends on this reference-selection constraint. With frozen encoders, shared support images, and fixed distance weights, we compare joint matching, which selects one reference patch across branches, with independent matching, which selects a reference separately in each branch. Duplicate-branch and weight-preserving controls distinguish new representations from reweighting, and paired differences of representation effects quantify their interaction with matching. Adding DINOv2-S yields positive interactions of 0.77 and 0.60 pixel average-precision percentage points on MPDD, with multiplicity-adjusted intervals excluding zero, whereas BTAD provides insufficient evidence of interaction. A prespecified WideResNet50-2 branch yields positive interactions of 0.50–0.97 points on both datasets. These estimates use stride-eight pixel evaluation; full-pixel point estimates retain their directions. The results show that additional-branch value and its dependence on matching are distinct, and that the latter varies with the encoder and dataset rather than following branch count alone. A confirmation set whose expectation was frozen before any of its features were encoded meets that expectation, with positive interactions for both encoders and both contrasts; the same contrasts on four datasets are positive on MPDD, MVTec AD and VisA and essentially zero on BTAD, and on MPDD both the sign of the interaction and the exclusion of zero are insensitive to the canvas-correspondence convention, including an optimal-transport variant that additionally smooths the C branch.

Keywords: few-shot anomaly localization; frozen visual encoders; normal reference matching; fixed feature fusion; representation interaction.

## 1 Introduction

Industrial visual inspection must locate defects whose appearance is difficult to enumerate before deployment. A new product may provide only a few verified normal images, while representative examples of scratches, contamination, missing parts, or structural defects remain unavailable. Industrial anomaly benchmarks make this distinction concrete by providing normal training images and heterogeneous test anomalies [1, 2, 3, 4]. Under a few-shot normal-reference protocol, the objective is to identify departures from the available normal appearance without learning a target defect classifier.

Frozen pretrained encoders offer a practical starting point. Their local descriptors allow a query patch to be compared with a memory of normal support patches, avoiding target-domain gradient optimization. AnomalyDINO demonstrates the value of this simple approach with DINOv2 features [5, 6]. Multiple encoders can supply different descriptions of the same image, and recent methods already combine visual and vision-language pretrained representations [7, 8]. However, a higher score for an entire fusion system does not explain which part of adding an encoder produced the change.

Three factors become entangled in a direct comparison between two and three equally weighted branches. The additional encoder changes the available representation, the total weight assigned to existing information, and potentially the support patch selected under a shared matching rule. For example, copying one existing branch adds no information, yet changes its effective weight from one half to two thirds when three branch distances are averaged. Replacing that copy with a different encoder is a separate intervention. Treating both changes as the contribution of a third branch can therefore overstate, or conceal, the value of the new representation.

Normal-reference selection introduces another distinction. Joint matching requires all branches to score the same normal support patch before the best candidate is selected. Independent matching lets each branch choose its own closest normal patch before the distances are averaged. Additional features can change the selected reference under either fixed rule; adding a branch does not itself change the rule. Independent matching cannot yield a larger raw minimum-distance score than joint matching under the assumptions in Section 3.3. Nevertheless, a smaller anomaly score does not necessarily improve the ranking of defective and normal pixels. The performance consequence must be measured rather than inferred from the distance inequality.

This question connects established research on multimodal fusion with work on consistent neighborhoods in multi-view anomaly detection [9, 10, 11, 12]. We do not introduce nearest-neighbor matching, early or late fusion, or the idea of shared neighborhoods. Our focus is narrower: under frozen visual encoders, fixed weights, and identical few-shot supports, does the localization benefit of replacing an existing representation depend on whether normal references are shared across branches? We examine both the absolute representation effect and the direct difference between that effect under the two matching rules.

The contributions are as follows.

1. **A common formulation of reference selection in fixed visual fusion.** We express joint and independent matching on the same aligned normal patch bank, with the same branch distances and weights. This separates the descriptors being combined from the constraint on which support patch may explain a query. The formulation makes the reference-selection difference explicit and distinguishes a raw score constraint from a localization-performance claim. Its contribution is a precise analytical basis for this setting, rather than a new matching operator or an original distance inequality.

2. **A controlled representation-replacement design that isolates the matching interaction.** Starting from a dual-visual anchor, we use an exact duplicate branch to expose effective-weight changes, replace that duplicate with a genuinely different encoder at fixed slot weights, and add a complementary control that preserves the weight of the original representation group. Crossing each construction with both matching rules yields a direct representation-by-matching interaction. This design answers whether a representation becomes more useful under a different reference constraint, instead of attributing every two-to-three-branch difference to new information.

3. **Evidence that the interaction depends on the encoder and data conditions.** The DINOv2-S replacement has positive matching interactions on MPDD but no clear aggregate interaction on BTAD, despite positive representation effects on BTAD. A prespecified WideResNet50-2 replacement produces positive interactions in both datasets; a direct comparison detects larger interactions than DINOv2-S on BTAD but leaves their difference uncertain on MPDD. These findings distinguish the usefulness of an added representation from its dependence on matching. Reference-budget, category, qualitative, baseline, and resource analyses delimit the observations rather than forming a separate methodological contribution.

The study is an analysis of controlled fusion choices, not a claim that one three-encoder network is universally preferable. The original dual-encoder configuration, referred to as A1 below, serves as an anchor. Its earlier project name, DCFnet, is not used to rename all variants or to imply a newly validated network architecture.

## 2 Related Work

Industrial anomaly localization methods differ in how they represent normality, how much target adaptation they require, and how they combine evidence. We organize the relevant work around normal-model learning, local reference memories, foundation-model fusion, and multi-view neighborhoods. The last group is necessary because shared versus independent neighborhood structure predates the present industrial setting.

### 2.1 Reconstruction and Normal Model Learning

Reconstruction methods identify anomalies through departures from an estimated normal appearance. SLSG combines generative pretraining, simulated anomalies, and graph-based modeling of normal embeddings [13]. RealNet uses diffusion-based anomaly synthesis and feature and residual selection to improve anomaly-sensitive reconstruction evidence [14]. These methods illustrate how a fitted normal model or anomaly discriminator can improve separation, while introducing training objectives and adaptation decisions. They address a different trade-off from a fixed normal-reference system that performs no target optimization.

Distributional patch models offer another description of normality. PaDiM models the distribution of pretrained patch embeddings with multivariate Gaussians [15]. This avoids reconstructing an image, but the estimated normal distribution depends on the available samples and feature dimensionality. Our study instead retains observed support descriptors and changes only their representation composition and reference-selection rule. It does not establish that fixed retrieval is preferable to fitted models in settings with larger normal training sets.

### 2.2 Feature Memories and Few Shot Normal References

PatchCore uses a representative memory of normal local descriptors and nearest-neighbor scoring [16]. Its coreset and image preprocessing affect both normal coverage and computational cost. AnomalyDINO shows that frozen DINOv2 patches provide a strong basis for few-shot detection [5]. These methods motivate an explicit account of the memory candidates, selected feature layers, and spatial coverage when interpreting a fusion comparison.

Several recent studies modify the representation or the normal reference rather than simply increasing the number of encoders. FEAD enriches sparse normal patterns through conditional feature transformation and multi-frequency modeling [17]. K-NG studies few-shot online detection through an evolving Neural Gas representation [18]. PGAD combines global invariance and multiscale local evidence with score calibration [19], while FastRef refines normal prototypes at test time [20]. SubspaceAD models frozen visual descriptors through a principal subspace [21], and DCP-SFR addresses the preservation of shallow defect information in deep representations [22]. These approaches show that reference coverage, cue retention, and adaptation can materially alter anomaly scores. Our fixed-memory setting deliberately excludes query-conditioned updates so that they do not confound the comparison between matching rules.

### 2.3 Foundation Models and Multi Branch Fusion

Vision-language pretraining provides transferable visual and textual representations [23]. WinCLIP combines prompt ensembles and local visual features for zero- and few-shot anomaly detection [24]. AnomalyCLIP learns object-agnostic prompts for normality and abnormality [8], PromptAD learns from normal target samples [25], and InCTRL uses in-context residual learning with sample prompts [26]. AA-CLIP introduces anomaly-aware alignment [27], and FAPrompt develops fine-grained abnormality prompts [28]. UniVAD broadens training-free reference-based anomaly detection across different domains [29]. These methods differ in their training data, prompt use, adaptation, and inference paths; they should not all be described as requiring target defect supervision.

The present C branch retains only the visual descriptor path of AnomalyCLIP. Its use of a vision-language pretrained backbone does not make our inference a text-image fusion system. No text-encoder score or learned prompt output enters the anomaly score. This distinction matters when comparing the controlled visual branches with complete published vision-language systems.

Sea-CLIP is especially close because it combines CLIP and DINOv2 representations for few-shot anomaly detection [7]. Its matching and decoder components already involve both shared-reference-like operations and independent nearest-neighbor evidence. Its complete architecture is not identical to our symmetric weighted-distance comparison, but it precludes claiming that combining these encoders or coupling their references is new. M3DM combines RGB and point-cloud information with multiple memories [30], and CIF uses hypergraph structural commonality to guide few-shot multimodal reference memories [31]. The architectural analysis underlying 3D-ADNAS examines conditional benefits of fusion modules and alternative fusion stages [9]. Thus, neither multimodal fusion nor the conditional value of an added module is a new general proposition of this paper.

Our contribution differs in the controlled question. We hold the normal support identities and distance weights fixed while replacing one visual representation, then estimate how that replacement effect changes when a common reference constraint is removed. We do not infer this interaction from the overall scores of different end-to-end architectures, and we do not claim a comprehensive comparison with all of those systems.

### 2.4 Multi View Neighborhood Consistency

Multi-view anomaly detection explicitly studies disagreement and consistency across representations. MUVAD uses neighborhood information to distinguish cross-view inconsistency from anomalies that are unusual in multiple views [11]. Neighborhood Consensus Networks align neighborhood structures across views [12], while ECMOD uses contrastive representation learning with neighborhood-consistency information [32]. SCoNE directly addresses consistent local neighborhoods across views and discusses the limitations of recovering them from independently represented neighborhoods [10]. These studies establish that the choice between separate and consistent neighborhoods is an existing research problem.

The present task differs from unsupervised outlier detection on generic multi-view instances. We use verified normal image supports, dense frozen visual features, and pixel-level industrial localization. The branch set changes through explicit duplicate and representation-replacement controls, and the quantity of interest is a paired performance interaction. This scope provides the basis for our claim of additional evidence; it does not confer novelty on shared-reference selection itself.

Taken together, the four groups offer different ways to define normality and combine information. Learned models adapt normal or anomalous structure, memories retain observed local evidence, foundation-model systems expand the descriptors available, and multi-view methods organize their neighborhood relationships. Our study connects the last two questions within a fixed-memory industrial protocol. The closest prior work motivates a restrained research claim: isolating the role of normal-reference matching in the benefit of an added visual representation, with explicit weight controls and bounded empirical conclusions.

## 3 Framework and Methods

### 3.1 Problem Statement

For category $c$, the input consists of $K$ verified normal support images and a query image $x$. The support set is

{{eq:1}}

Here $x_i^c$ is support image $i$ of category $c$, and the query may be normal or anomalous. Category labels specify the relevant support bank; no target defect class is predicted. We use $p$ for a query patch, $r$ for an aligned support-patch index that contains both support-image identity and spatial position, and $b$ for a visual branch. The same index $r$ denotes the corresponding support location in every branch after spatial alignment. It does not require a query patch to match the same spatial coordinate in its support image.

The native outputs are a continuous pixel anomaly map $A_t$ and an image-level score $s_{\mathrm{img},t}$, where the matching-rule label $t$ is either J or L. A displayed defect contour is derived from the same map through a separately specified visualization threshold. It is not an additional learned output, a defect-category label, or a threshold calibrated for deployment. Test labels and masks are used for offline evaluation and example selection, not for selecting a reference during query inference. Because the datasets have already informed project analysis, we distinguish this inference restriction from a claim of wholly unseen evaluation.

### 3.2 Overview Structure

Figure 1 separates support-bank construction from query scoring. Each image passes through the same frozen visual encoders. Their spatial feature grids are mapped to a common query or support canvas and normalized branch by branch. All normal support patches are retained in aligned branch memories. These memories are fixed for a particular category, support seed, and $K$; the upper path in Figure 1(a) builds that bank, and the lower path in Figure 1(b) scores a query against it without writing back.

{{figure:framework}}

The anchor uses DINOv2-B and the AnomalyCLIP visual path. We then duplicate the B descriptor or replace the duplicate with DINOv2-S, and repeat a restricted comparison with a prespecified WideResNet50-2 descriptor. Each representation construction is scored under both matching rules. Spatial alignment and normalization are shared operations; joint and independent matching are the comparison factor. After patch scoring, the same resizing and smoothing steps generate the output map. No foreground mask, region-of-interest selector, dynamic gate, learned fusion head, or online memory update is added.

### 3.3 Normal Reference Matching

Let $F_b$ denote a branch feature tensor and $R_b$ its deterministic mapping to the common spatial lattice. At location $p$, branch-wise normalization produces a unit descriptor $g_{b,p}$. The branch distance between a query descriptor and a support descriptor is

{{eq:2}}

All reported constructions use nonnegative distance weights $w_b$ summing to one. The descriptors in Equation (2) are nonzero; numerical norm handling follows the archived implementation. With the same aligned candidate set $\mathcal{R}_c$ in every branch, joint matching is

{{eq:3}}

Joint matching first sums the branch distances for each single candidate $r$, then selects the candidate with the smallest weighted distance. Equivalently, concatenating the normalized branch descriptors with coefficients equal to the square roots of their distance weights yields a unit joint descriptor. Half its squared Euclidean distance equals the weighted cosine distance. Thus, feature coefficients and distance weights must not be confused: equal thirds in distance require equal square-root coefficients, followed by the corresponding joint normalization.

Independent matching reverses the order of branch combination and candidate minimization:

{{eq:4}}

Each branch can now select a different support patch. We denote the corresponding reference indices by $r_J$ and $r_{b,L}$ when discussing selected neighbors. Ties can select different indices with identical scores, so reference identity should be interpreted together with distance rather than as a unique explanation of every query.

Figure 2 shows both rules over the same aligned bank: panel (a) fixes one query patch and the candidate reference rows, and panel (b) contrasts the single shared row required by $J$ with the branch-specific rows allowed by $L$. The two panels use identical candidate sets, descriptors, and weights, so they differ only in the order of combination and candidate minimization.

{{figure:matching}}

The difference between the two raw patch scores is

{{eq:5}}

For every candidate, each branch distance is at least its own minimum; weighting and summing preserves that inequality, and minimizing the weighted sum does not reverse it. This is a standard algebraic property, not a new theorem. Equality holds when the branch minima admit a common minimizer, among other degenerate cases. A positive gap measures the cost in distance of imposing a common reference. It does not measure an improvement in defect localization, since average precision depends on the ordering of normal and anomalous pixels. The same distinction applies after common linear resizing and smoothing.

### 3.4 Representation Constructions and Weight Controls

We use upright branch labels B for DINOv2-B, S for DINOv2-S, C for the AnomalyCLIP visual descriptor, and D for WideResNet50-2. These identifiers are distinct from italic mathematical indices. Table 1 defines the constructions; their labels are kept unchanged in the text, tables, and figures.

{{table:design}}

Figure 3 shows the same four constructions as slot diagrams and states what each successive step isolates. Reading the constructions together with Table 1 is sufficient to tell a change of effective weight from a change of descriptor.

{{figure:constructions}}

Comparing DUP with A1 changes the effective weight of B without adding a new representation. DUP is also numerically equivalent to a two-branch B/C construction with weights two thirds and one third. Replacing the copied B descriptor in DUP with S produces TRI at identical slot weights. TRI minus DUP therefore measures the effect of that representation replacement rather than the entire difference between two and three encoders.

BAL provides a complementary comparison. In the S experiment, the combined DINO family weight remains one half, while C retains one half, allowing the B allocation to be split between B and S. In the D experiment, BAL preserves the total non-C weight but should not be called a DINO-family-preserving construction, since D is a convolutional ImageNet encoder. Neither control proves that its chosen weights are optimal. The duplicate is reused exactly, rather than obtained through another stochastic feature extraction, so it cannot add information through numerical randomness.

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

All differences are formed within matched conditions and within each resampling replicate before aggregation. We never infer an interaction by contrasting two separate significance decisions or by subtracting confidence-interval endpoints. These are established contrast estimators used to answer the representation question, not a proposed statistical method.

### 3.6 Anomaly Outputs and Computational Cost

The patch scores form the matrix $a_t$ on the common lattice, are bilinearly resized to the $H$ by $W$ output canvas, and are smoothed with a Gaussian of standard deviation four pixels; $u$ indexes an output pixel. The image score is the maximum map response:

{{eq:11}}

The controlled evaluation restores patch scores to the retained image canvas, with dimensions H by W; it is 448 by 448 for square images and 448 by 588 for BTAD category 03. Ground truth follows the same resized and cropped image extent. This bookkeeping is distinct from cross-method evaluation in original-image coordinates, described in Section 4.1.3. Pixel metrics use continuous scores. For illustrative contours only, thresholding produces

{{eq:12}}

Here $\tau_{\mathrm{vis}}$ is a visualization rule, not a universal fixed operating threshold. The qualitative figures use the exact map normalization and Otsu rule stated in their captions. Ground-truth boundaries are displayed separately. Neither the figure nor Equation (12) establishes a calibrated defect segmentation system.

If a bank contains $N_c$ normal patches, a query contains $n$ patches, and the combined descriptor dimension is $d$, exhaustive matching requires order $nN_cd$ distance work and order $N_cd$ feature storage. Joint matching can use one weighted concatenation index, whereas independent matching requires the corresponding branch-wise searches. Implementations can have different overheads even when the arithmetic order is the same. Larger support budgets increase reference storage, and an actual additional encoder incurs feature-extraction cost; reusing a duplicate does not incur that encoder cost. Training-free describes the absence of target optimization, not zero preparation cost or negligible inference cost.

### 3.7 Model Configuration

Table 2 records the frozen feature paths and the shared processing choices. Figure S1 summarises the same configuration as native input geometry, aligned grids, retained descriptor widths and the resulting fused width. The B and S encoders use DINOv2 patch features [6]. C uses a CLIP ViT-L/14 visual backbone with AnomalyCLIP's diagonally prominent attention map path [23, 8]. Its 518-pixel input yields a 37 by 37 grid; the final returned patch tensor is retained after projection, excluding the class token. Although the inherited setup loads prompt-related checkpoint material, no text or prompt score is used in our visual-only inference.

{{table:models}}

The common lattice follows the B canvas. Inputs are resized with preserved aspect ratio to a short side of 448 pixels and cropped from the top left to dimensions divisible by 14. The C grid is mapped to that retained image extent rather than blindly stretched to the uncropped source. On BTAD category 03, the resized extent is 448 by 597 pixels and the retained canvas is 448 by 588. The current evaluation maps both predictions and masks through the corresponding coordinates. Geometric consistency does not imply identical receptive fields or learned semantic alignment between encoders.

The D branch was specified before its results were generated. It uses ImageNet-pretrained WideResNet50-2, bilinearly resamples layer2 and layer3 to the B lattice, concatenates their 512- and 1024-channel outputs, and normalizes the resulting 1536-dimensional descriptor. Its query-feature cache is stored in float16 and converted to float32 for normalization and scoring; this storage choice is recorded in the reproduction manifest. The B/S/C features and D features do not share a universal 768-dimensional output. All encoder parameters remain frozen, so target optimizer, learning rate, training epochs, and training-loss curves are not applicable.

## 4 Experimental Evaluations

### 4.1 Experimental Design

#### 4.1.1 Datasets and Reference Protocol

The current-theme experiments use the Metal Parts Defect Detection dataset (MPDD) and the beanTech Anomaly Detection dataset (BTAD) [2, 3]. Their six and three categories, respectively, provide different normal appearances and defect distributions. The old project's MVTec AD and VisA experiments are not reused as if they evaluated the new representation-by-matching design. A later extension does run the same controlled contrasts on MVTec AD and VisA as frozen validation sets, and on KolektorSDD2 as a confirmation set whose expectation was frozen before any of its features were encoded; those runs are new, they are reported separately in Sections 4.2.9 to 4.2.13, and they are not the old project's experiments. MPDD has informed development, and BTAD has already been examined in the project; neither the present interaction analysis nor the encoder extension is described as a fresh unseen-dataset confirmation.

Table 3 records the evaluation scope of both studies, including the seed and support budgets that each one uses and which of them the encoder comparison reuses.

{{table:protocol}}

For each category and seed, the support sequence is fixed and smaller budgets are prefixes of the same sequence. All methods in a paired comparison use exactly the same support images and query images. The S study uses seeds 0, 1, and 2 on MPDD and 0 and 1 on BTAD, with $K$ equal to 1, 2, 4, and 8. This gives 72 and 24 category-seed-budget units, respectively, or 12 and 8 dataset-level support conditions. These are repeated evaluations on shared data, not 96 independent datasets.

The prespecified D extension uses seeds 0 and 1 and $K$ equal to 1 and 4 on both datasets, giving 36 category-level units. A1 and DUP controls are rescored within that scope. The S-to-D interaction comparison also uses that restricted scope, avoiding differences caused by unequal support-condition coverage. No additional encoder or dataset was selected after comparing multiple candidate extension results.

#### 4.1.2 Baselines and Control Scope

The primary controlled matrix consists of single-branch B, S, and C together with the J/L forms of A1, DUP, TRI, and BAL. These are eleven analysis configurations, not eleven independently proposed algorithms. Two further constructions check numerical equivalence of the duplicated representation and its effective-weight formulation. The D extension adds the D-only path and its TRI/BAL combinations. Single-branch removal is a matched control; it should not be presented as evidence for an independently novel network module.

For practical context, we also evaluate native-method configurations of AnomalyDINO and PatchCore [5, 16]. AnomalyDINO is run on the native image canvas both with and without the reference-rotation option. PatchCore includes an official-resolution 224-pixel configuration with 1024-dimensional projected features and the earlier local 128-pixel/256-dimensional configuration. The latter is retained to expose configuration sensitivity, rather than being treated as the sole representative of PatchCore. Backbones, feature dimensions, preprocessing, reference augmentation, and search pipelines remain method-specific in this comparison; consequently it does not isolate matching or establish a general state-of-the-art ranking.

#### 4.1.3 Evaluation Metrics and Uncertainty

Pixel AP is the primary metric because it evaluates anomaly ranking while emphasizing precision and recall under sparse defect pixels. Within each category, pixel scores and labels are pooled across its test images; category APs are then averaged equally. Support conditions are averaged with equal weight at the dataset level. This differs from pooling all categories into one AP and from averaging per-image AP. Pixel area under the receiver operating characteristic curve (AUROC) is a secondary diagnostic; it is not substituted for AP when interpreting the primary interaction.

We distinguish three evaluation grids. The main resampling analysis uses a regular stride-eight subset of the retained output-canvas grid, which bounds the computational cost of image-level resampling. Full-pixel evaluation uses every output pixel and provides point estimates for a resolution-sensitivity check. The cross-method comparison maps each method's prediction to its actual coverage in original-image coordinates and evaluates only their common valid intersection. Tables and captions identify these grids explicitly; their AP values are not placed in a single interchangeable ranking.

Uncertainty is estimated by 1000 paired image-level bootstrap replicates, sampling with replacement within each fixed category, without additional normal/abnormal stratification. A sampled image contributes its sampled pixels as a block, and the same replicate stream is shared across methods, seeds, and budgets. Conditions and categories are aggregated within a replicate before its contrast is summarized. The base random seed is 20260913; the deterministic stream also incorporates dataset identity, category identity, and replicate index. These intervals characterize test-image sampling conditional on the selected categories, encoders, and finite support manifests. They do not resample the population of possible support sets or provide uncertainty over arbitrary future datasets.

For the four primary S interactions, two constructions across two datasets, we report 95% exploratory intervals and 98.75% percentile intervals corresponding to a four-comparison Bonferroni adjustment. The four D interactions and the four matched encoder differences are separate exploratory families with the same adjustment. The extensions reported in Sections 4.2.9 to 4.2.12 use the levels stated with them: the 95% interval for the confirmation set, which receives no family adjustment, and the 95%, 98.75% and 99.375% levels for the eight-cell four-dataset family. These are approximate family adjustments built on bootstrap intervals; 1000 replicates limit precision in the extreme tails. They are not a single simultaneous guarantee over all subsequent subgroup plots and secondary metrics. The interaction analysis is post hoc to earlier project exploration, even though the D specification was frozen before D results.

We use 0.5 AP percentage points as a descriptive scale for judging the magnitude of an interaction, not as an established industrial utility threshold or an acceptance criterion selected independently of this project. A point estimate above that scale does not mean its interval lies above it. An interval spanning zero is treated as insufficient evidence of a direction, not as statistical equivalence. Full-pixel results currently have no bootstrap intervals and cannot support claims of full-pixel statistical significance.

#### 4.1.4 Implementation and Computing Environment

The archived runs use an NVIDIA GeForce RTX 3060 Laptop GPU with 6 GB VRAM, an Intel Core i9-12900H processor, and 16 GB system RAM. Encoders run in evaluation mode without gradient updates. Query features are cached to avoid repeating feature extraction for each controlled score variant; scoring and evaluation still run for every applicable support condition. Exact search implements the distance definitions in Section 3, with FAISS used where appropriate [33]. No target loss is optimized.

The manuscript uses the final geometry-consistent BTAD revision. Earlier BTAD category-03 ground-truth and feature-grid transformations were audited, then affected point estimates and bootstrap comparisons were regenerated. Original point estimates are reported as such; bootstrap means are retained in the source tables but are not substituted for them. This distinction also applies to per-budget aggregates, which average all available seeds rather than displaying only the last processed seed.

Resource measurements are reported by stage and configuration. Historical controlled runs did not record all per-unit feature and scoring times, so a later partial timing is not reconstructed into an end-to-end latency. PatchCore's combined memory-and-scoring stage cannot be split retrospectively. Per-process GPU memory is unavailable for PatchCore in the current instrumentation, and device-wide usage is not substituted for it. These restrictions affect practical comparisons but do not alter the stored anomaly predictions.

### 4.2 Results and Analysis

#### 4.2.1 Overall Controlled Results

Table 4 reports the eight configurations required for the S interaction. Under the complete S support scope, the A1 anchor reaches pixel AP of 0.3729 with joint matching and 0.3791 with independent matching on MPDD. On corrected BTAD, the corresponding values are 0.6408 and 0.6498. Independent matching has a positive average effect at the anchor, but these averages alone do not establish that another encoder benefits from that change. That question requires comparing representation effects within each matching rule.

{{table:main}}

The configurations do not admit one uniform ordering. On MPDD, TRI remains below the A1 anchor under both matching rules, even though TRI improves over its information-matched DUP control under L. BAL L is close to A1 L. On BTAD, both TRI and BAL exceed their corresponding controls, while BAL has the highest observed AP among these eight configurations. This is a ranking within the fixed controlled matrix and current data, not evidence that the selected weights or branch set are globally optimal.

Table 5 isolates the change that the rest of the study is built on, the matching effect M = P(L) − P(J). It differs from the anchor comparison only in the selection rule, because the support identities, descriptors and weights are all held fixed. On MPDD the anchor gains +0.618 AP percentage points and on corrected BTAD +0.900, and both intervals exclude zero; the other three constructions move in the same direction, from +0.321 for the duplicate control to +1.213 for BAL on MPDD. A rule that raises the score of every construction does not yet say whether a newly added representation benefits from that rule, which is the question taken up in Sections 4.2.3 and 4.2.4.

{{table:matching}}

Single-branch diagnostics bound this comparison from one side. On MPDD, where these runs share the primary geometry revision, each branch alone scores below the fused anchor: 0.348 for B, 0.326 for S and 0.283 for C, against 0.373 and 0.379 for A1 under the two rules. Combining descriptors therefore helps relative to every single branch, which is why the study keeps a fused anchor rather than asking whether one encoder is enough. The corresponding BTAD diagnostics are not reported here: the corrected BTAD-03 geometry rescore covers only the eight interaction configurations, so placing the two revisions in one comparison would confound geometry with the encoder.

#### 4.2.2 Separating Reweighting from New Information

DUP lowers mean AP relative to A1 under both matching rules in both datasets (Table 4). On MPDD, the observed differences are approximately −0.80 AP percentage points under J and −1.10 under L. Thus, increasing the apparent number of branches from two to three can change performance without introducing new information. The duplicated B descriptor simply increases the effective B weight while reducing the C weight.

This result explains why the direct TRI-to-A1 comparison does not identify the contribution of S. TRI contains both a change in effective weights relative to A1 and a new descriptor relative to DUP. The TRI-to-DUP contrast fixes the branch slots and their distance weights; BAL-to-A1 addresses a complementary allocation in which C and the combined non-C weight remain unchanged. The controls do not establish that equal two-branch weights are universally preferable. They demonstrate that the weight shift is consequential in the present configuration and therefore must be separated from representation value.

#### 4.2.3 Absolute Representation Effects

Table 6 reports the S effects in AP percentage points. On MPDD, TRI minus DUP changes from −0.224 under J to +0.548 under L. The latter 95% interval spans −0.092 to +1.160, so a positive absolute gain remains uncertain. BAL minus A1 changes from −0.510 to +0.085, again with an interval spanning zero. Independent matching makes the observed representation change more favorable, but this should not be rewritten as an established absolute improvement from adding S on MPDD.

{{table:effects}}

BTAD illustrates a different situation. The TRI replacement effects are +1.553 points under J and +1.503 under L; their exploratory 95% intervals are both above zero. BAL also has positive estimated effects under both rules. Here, additional S information is useful relative to the specified controls, yet the very similar TRI effects suggest that its usefulness need not depend strongly on the matching rule. Direct interaction inference, rather than separate effect intervals, resolves that distinction in the next subsection.

Figure 4(a) plots these eight S effects with their intervals on one axis, so the two rules can be compared directly within each contrast.

{{figure:effects}}

#### 4.2.4 Direct Interaction and Encoder Dependence

The direct S interactions on MPDD are +0.772 points for TRI and +0.595 for BAL (Table 7). Their adjusted 98.75% intervals are [+0.346, +1.211] and [+0.189, +1.030], respectively. Both exclude zero. Their point estimates exceed the descriptive 0.5-point scale, but their interval lower bounds do not, so the data do not establish an effect uniformly above that practical reference magnitude. Figure 4(b) places these two interactions on the same axis as the later D extension and the four datasets of Section 4.2.10.

{{table:s_interaction}}

On BTAD, the S interactions are −0.050 and −0.119 points, with both adjusted intervals spanning zero. The small negative points are not evidence of a general advantage for joint matching. Combined with Table 6, the result is that S has positive representation effects under the tested rules while the current data do not clearly resolve a difference between those effects. This is distinct from saying that matching is irrelevant or that the two rules are equivalent.

The prespecified D extension provides a second representation condition. Table 8 reports its full-pixel localization results under the restricted four-condition scope. On MPDD, TRI D L reaches AP 0.4107 compared with 0.3554 for DUP L; on BTAD, it reaches 0.6591 compared with 0.6335. The corresponding full-pixel representation effects are approximately +5.53 and +2.57 AP percentage points. These are absolute representation effects, not the much smaller interaction estimates. D alone has lower pixel AP than these fused constructions, showing that the fusion result cannot be explained simply by selecting D's standalone score. Figure 4(a) shows the four D effects that this scope supports.

{{table:d_full}}

All four D interactions are positive, with adjusted intervals excluding zero (Table 9): +0.974 and +0.628 points on MPDD, and +0.622 and +0.501 on BTAD. The full-pixel points retain these directions. This establishes that a positive interaction in the observed setting is not confined to adding a smaller DINOv2 encoder. It does not establish the same result for arbitrary convolutional backbones or for additional datasets.

{{table:d_interaction}}

A direct comparison between the S and the D series inside Figure 4(a) would confound the encoder with support-condition coverage. Table 10 instead restricts S to the D seeds and budgets and directly estimates the D-minus-S interaction difference. The observed differences on BTAD are +0.623 and +0.585 points, with adjusted intervals [+0.255, +0.945] and [+0.204, +1.060]. On MPDD, the observed differences are +0.207 and +0.081, and the intervals span zero. The bootstrap means differ from the observed points, particularly on MPDD, and are shown in a separate column rather than being mislabeled as point estimates.

{{table:encoder_diff}}

These comparisons support encoder dependence on BTAD under the matched scope. On MPDD, the uncertainty does not resolve an S-to-D interaction difference; it is not evidence that the encoders are equivalent. More generally, a larger interaction does not mean that an encoder is better in every absolute metric. The available image-level metrics illustrate this separation: under the four-condition BTAD scope, BAL D L has image AP 0.9372 versus 0.9468 for A1 L even though its full-pixel AP is higher. Image-score pooling and pixel ranking answer different evaluation questions.

#### 4.2.5 Support Budget and Category Conditions

Figure 5(a) shows the seed-averaged S interaction against the nested support budget. On MPDD both contrasts strengthen as K grows: the TRI interaction rises from +0.41 percentage points at one support to +0.75, +0.88 and +1.01 at two, four and eight supports, and BAL rises from +0.37 to +0.83. On the corrected BTAD revision the same contrast weakens and changes sign, moving from +0.20 points at one support to +0.09 at two, −0.14 at four and −0.23 at eight, where the interval no longer includes zero. The curves therefore support a budget-dependent description, not a monotone law that more normal references consistently amplify the benefit of independent matching.

{{figure:budget_category}}

Adding normal candidates cannot increase the exact minimum raw distance when the bank is nested and the descriptors remain fixed. However, AP depends on score ordering, and an interaction is a difference of four performance values. Neither AP nor the interaction inherits a monotonicity guarantee from the minimum-distance operation. The distinction also explains why a numerical constraint gap should not be treated as a defect-performance measure.

Category analyses further limit the aggregate interpretation. Figure 5(b) resolves the TRI interaction by category: all six MPDD categories carry a positive estimate, led by connector and tubes, whereas the three BTAD categories stay close to zero and category 02 is slightly negative. Omitting any one MPDD category leaves the TRI aggregate interaction positive in the recorded leave-one-category analysis. On corrected BTAD, omitting category 02 changes the TRI aggregate direction. With only three BTAD categories, the average is sensitive to category composition. Per-category and per-budget intervals are exploratory follow-up analyses and do not inherit the primary family's multiplicity guarantee. They identify conditions worth testing on new data rather than proving a causal role for category identity or defect size.

The stride-eight and full-pixel aggregate interaction directions agree for the S and D summaries. This is a useful numerical sensitivity check because sparse pixel sampling can alter the contribution of small defects. It does not eliminate that concern, and no claim of full-pixel significance follows from point agreement. In particular, the selected qualitative examples include tiny defects whose per-image AP can change markedly when only a few sampled pixels are positive.

#### 4.2.6 Qualitative Localization and Predicted Contours

Figures 6 and 7 show five MPDD cases from seed 0 and four normal supports, with three improvements and two degradations for A1 L versus A1 J. The cases are selected by extreme stored per-image AP changes from the fixed closeout candidate list. Selection is based on localization performance, not on the average reduction in raw score. These panels illustrate the anchor's matching behavior; they are not a substitute for the direct representation interaction in Tables 7 and 9.

{{figure:cases_good}}

The heatmaps for each case use one common minimum and maximum over its J and L maps after resizing and smoothing. The L map is quantized into 256 bins, and Otsu's between-class-variance criterion selects a visualization threshold, taking the smallest maximizing bin if tied. The cyan contour traces the resulting predicted mask. It is derived entirely from the model score. For visual inspection only, a square crop is centered on the bounding box of the ground-truth defect mask, with side length clipped between 96 and 260 pixels after a 1.8-fold expansion; the same crop is applied to all columns. The ground truth determines this display region and the evaluation labels, but not the predicted mask.

{{figure:cases_bad}}

Improved AP does not imply an accurate defect boundary at an arbitrary operating threshold. The small contours in the examples may cover only the strongest part of a scratch or mismatch, while secondary activations can remain elsewhere in the map. The degradation cases in Figure 7 likewise show that independent matching can change the relative responses unfavorably even though its raw patch distances are no larger. These observations motivate keeping continuous localization evidence, thresholded visualization, and deployment segmentation accuracy as separate claims. No ground-truth outline is substituted for a predicted output.

#### 4.2.7 Native Baseline Context and Computational Cost

Table 11 evaluates the native baselines and A1 on the intersection of their actual valid image regions. A1 L has the highest observed AP in this comparison, followed by A1 J. The rotation-enabled AnomalyDINO configuration improves on its non-rotation version, and the official-resolution PatchCore configuration improves substantially on the earlier local low-resolution variant. These changes show why an inadequately configured baseline can give a misleading impression of practical advantage.

{{table:baselines}}

The common region covers 76.56% of the MPDD canvas and 70.49% on average for BTAD; BTAD category 03 has a smaller intersection of approximately 58.36%. Restricting evaluation avoids inventing predictions in cropped-away borders, but also removes those borders from the evaluation task. Different backbones, reference augmentation, resolutions, and post-processing remain. Consequently, the observed ranking is useful local context, not proof that A1 exceeds the complete published methods under every native or full-image protocol. AnomalyDINO also uses the S backbone employed in the controlled study, so it is not an independent test of a wholly unrelated representation family.

Table 12 reports the runtime stages for which instrumentation is available. Reference rotation increases AnomalyDINO's recorded processing time along with its AP. The D extension separately records approximately 55.4 seconds of query encoding, 8.3 seconds of reference encoding, and 266.3 seconds of controlled scoring across its archived scope, with feature reuse between configurations. Its recorded peak allocated GPU memory is approximately 417.7 MB. Those stage totals are partially instrumented and do not constitute a synchronized complete-run latency or the simultaneous memory footprint of all encoders.

{{table:resources}}

Figure 8 shows the same recorded quantities per unit, together with the peak process RAM that Table 12 does not list.

{{figure:resources}}

The evidence does not support a fair end-to-end speed ranking between A1 and the native baselines: A1's historical matrix lacks comparable per-unit timing, and PatchCore lacks a measured per-process GPU peak. A combined latency–VRAM chart that filled those gaps would be misleading. The available measurements instead show concrete costs and their boundaries. Enlarging the encoder set incurs feature-extraction work and increases stored descriptor dimensions; increasing the support budget enlarges the normal bank. Whether a particular AP gain justifies that cost remains application-dependent.

#### 4.2.8 Discussion and Limitations

The practical implication is to inspect the source of a fusion gain before enlarging an encoder set. A duplicate control tests whether effective weights already change the result. A representation replacement at fixed weights tests whether the new descriptor helps. Crossing that replacement with the matching rule tests a different question: whether reference selection changes its value. The MPDD and BTAD results show why these questions cannot be collapsed into a single three-branch-versus-two-branch comparison.

The interpretation remains limited in several ways. First, the primary interaction was formulated after earlier project exploration, and the datasets are not untouched confirmation sets. Second, the bootstrap conditions on the observed categories and fixed support manifests; its intervals do not characterize arbitrary future support choices. Third, only one prespecified heterogeneous encoder was added, with a smaller seed and budget scope than the S study. Fourth, full-pixel intervals and complete deployment resource measurements remain unavailable. Fifth, qualitative cases are selected extremes, and their Otsu contours are display choices rather than calibrated defect masks. Sixth, the operations that every construction shares, namely spatial mapping, branch normalization and scoring from concatenated descriptors, are held fixed rather than ablated at the primary scope, so this study does not quantify how much each of them contributes and does not present them as validated modules; Section 4.2.13 reports one single-condition ablation of a shared operation, which is exploratory for the same reason. Finally, the geometric alignment is deterministic canvas correspondence, not a learned guarantee that receptive fields describe exactly the same object part.

These limitations do not turn a negative or uncertain interaction into a failed experiment. BTAD with S separates positive representation value from uncertain matching dependence, while the D comparison provides an encoder-specific difference under matched conditions. The study's contribution is this controlled and qualified account. A future learned selector, foreground filter, or dynamic fusion module would require its own implementation and evidence; none is implied by the present results.

#### 4.2.9 A Confirmation Set Frozen Before Its Features Were Encoded

Every interaction reported so far comes from data that the project had already examined, so a positive result could reflect the development work that preceded it. KolektorSDD2 (KSDD2) supplies a confirmation set with a single categorical expectation, frozen at 11:59 UTC on 18 September 2026, before any KSDD2 feature file existed: both the S and the D branch are expected to show a positive $I_{TRI}$ and a positive $I_{BAL}$ with 95% intervals that exclude zero. If any of those intervals includes zero, the expectation fails on this dataset and this manuscript has to say so.

The dataset contributes one category, a single production item, so the category macro average reduces to that category. Its positivity rule is fixed as "a sample is positive if and only if its ground-truth mask has at least one non-zero pixel", which gives 110 positive and 894 negative test images out of 1004. The frozen canvas is 224 by 630 pixels on a 16 by 45 patch grid with a patch size and stride of 14. The D branch reuses that same fixed canvas, so its input extent equals the B canvas exactly; this resolves one ambiguity in the D branch text, which was written for the two older datasets. The C branch keeps its own 518-pixel preprocessing and is re-gridded onto the B canvas as everywhere else. The scope is seeds 0, 1 and 2 with $K$ equal to 1, 2, 4 and 8, giving twelve support conditions.

Only the 95% intervals are reported for this set. The frozen specification states the reason: the family adjustment used for the exploratory tables would relax the criterion after the results were seen, which is not admissible for a confirmation set. Table 13 reports the four cells.

{{table:ksdd2_confirmation}}

All four point estimates are positive and all four 95% intervals exclude zero, so the frozen expectation is met on this dataset. We record for transparency that the same four cells also exclude zero at 98.75%, but the frozen judgement remains the 95% interval. The confirmation set deliberately does not enter the four-dataset table of Section 4.2.10, whose adjustment family was fixed over the exploratory cells.

#### 4.2.10 The Interaction on Two Further Datasets and the Wider Family

The same two contrasts were later run on MVTec AD and VisA under the study's own aggregation rule, so that the generalization datasets can be read beside MPDD and BTAD. Table 14 reports all four datasets at the 95%, 98.75% and 99.375% levels; the last level matches the eight-cell family that this table actually covers, whereas the 98.75% level remains the four-cell family of Section 4.2.4.

{{table:generalization}}

The four datasets do not behave alike, and we keep their readings separate instead of summarizing them as a replication. On MPDD both interactions are positive and exclude zero at the widest level reported here. On MVTec AD both are positive, with the narrowest intervals in the table, and they also exclude zero at the widest level; their point estimates, about +0.4 points, are the smallest of the three positive datasets. On VisA both are positive and the largest in the table, which is expected rather than independent evidence, because VisA is in-domain for the C branch: its frozen AnomalyCLIP checkpoint was trained on that dataset. BTAD is a true null. Its point estimates are an order of magnitude smaller than those of the positive datasets and both intervals span zero at all three levels, so no direction is established there, and the table must not be read as four consistent significant replications.

Three qualifications belong with the table. First, MVTec AD and VisA are frozen validation sets, not untouched confirmation sets; only KolektorSDD2 was frozen before its features were encoded. Second, the BTAD row pools the study's canonical-mask series, whereas the primary BTAD tables use the corrected geometry for category 03; the two differ by about 0.03 point in the point estimate and both fail to exclude zero, so the reading is unchanged, but the numbers should not be quoted interchangeably. Third, the estimate column is the mean of the replicate distribution rather than the condition-averaged observed difference used in Table 7, a difference of 0.01 point on MPDD; stride-one point estimates now exist for all four datasets (+0.787 and +0.601 points on MPDD, −0.045 and −0.115 on BTAD, +0.423 and +0.386 on MVTec AD, +0.896 and +0.760 on VisA).

The role strings are the ones recorded by the table itself: development for MPDD, external frozen validation for BTAD and MVTec AD, and in-domain frozen validation for VisA. The frozen encoder specification records BTAD as a holdout; both strings describe the same fact, that BTAD had been examined in the project before these runs.

#### 4.2.11 Further Frozen Encoders and Support-Set Variation

Three further frozen encoders entered the extra slot after the S and D results were known, so they are exploratory transfer checks rather than prespecified confirmations. E1 is the original DINO self-distillation ViT-S/8 with 384-dimensional descriptors; E2 is ConvNeXt-Tiny with 576; E3 is Swin-Tiny with 576. Each is mapped to the B canvas and normalized exactly like the other branches, and the same TRI and BAL contrasts are formed at the frozen slot weights. Table 15 lists each encoder's interaction in the four-condition scope shared with S and D and in the wider twelve-condition scope recorded for the additional encoders.

{{table:encoders}}

The scope column is not cosmetic. The rows marked with four conditions pool the same conditions as S and D, seeds 0 and 1 with $K$ equal to 1 and 4, so their paired E-minus-S differences are same-condition pairs. The rows marked with twelve conditions pool seeds 0 to 2 with $K$ equal to 1, 2, 4 and 8, the wider scope recorded for the three additional encoders alongside the primary one. Both scopes are given because they change some of the zero-exclusion decisions.

Within the four-condition scope the additional encoders split on MPDD: E3 has positive interactions in both contrasts with intervals above zero, E1 has positive points in both but its BAL interval spans zero, E2 has none, and S and D remain positive. On BTAD all three additional encoders have a positive $I_{TRI}$ with an interval above zero, while for $I_{BAL}$ only E2 and E3 do. In the twelve-condition scope E1's MPDD BAL interval also clears zero, while E3's BTAD BAL interval no longer does. Across both scopes the only statement that survives concerns E2: it is the single encoder whose MPDD TRI interaction is negative and lies below the S interaction with a paired interval that excludes zero, at −0.712 points in the four-condition scope and −0.733 in the twelve-condition scope. The paired E-minus-S differences exclude zero in few cells, and which cells they are depends on the scope: in the four-condition scope E2 on MPDD TRI, E1 and E3 on BTAD TRI, and E2 and E3 on BTAD BAL; in the twelve-condition scope E2 on MPDD in both contrasts, E3 on MPDD TRI, E1 on BTAD TRI and E2 on BTAD BAL. We therefore read the extra encoders as a transfer check whose ordering is scope-sensitive, not as a ranking of encoders.

Single-branch sanity is verified for all three additional encoders, each with forty-eight stored single-branch units and a passing single-branch gate. E1 spans pixel AUROC 0.916 to 0.992 with a mean of 0.967, E2 spans 0.887 to 0.984 with a mean of 0.953, and E3 spans 0.906 to 0.998 with a mean of 0.952. These units cover the MPDD study revision and the corrected BTAD revision, so the interaction estimates do not rest on fused-construction rows alone.

A separate extension varies the support set rather than the encoder. Eight seeds were run, of which seeds 0 to 2 keep their own query encodings and seeds 3 to 7 share a single query block, so the latter isolate the support-set contribution; the same test images are scored under every seed and only the normal references change. Table 16 summarizes the per-seed interaction, and Figure 5(c) draws the same series.

{{table:seed_variance}}

This batch is reported descriptively, and its reproduction gate passes: with the aggregation aligned, the recomputed per-condition series reproduce the published ones to a maximum absolute difference of 2.602e-18 AP on MPDD over 24 compared cells and 6.722e-18 on BTAD over 16, against a tolerance of 1e-9. The earlier apparent difference of 0.032 AP on MPDD and 0.007 on BTAD came from comparing a published dataset macro average with a single-category value, that is an aggregation-level mismatch rather than data drift, and it disappears once the aggregation is aligned. The descriptive reading is that the MPDD interaction keeps its sign at every seed, while on BTAD neither contrast does, which is consistent with the small BTAD point estimates of Table 14 and with the judgement that no direction is established there. We do not go beyond that observation.

#### 4.2.12 Does the Conclusion Depend on the Correspondence Convention?

Geometric alignment in this study is a deterministic canvas correspondence, not a learned or verified part-level correspondence. We therefore replaced the correspondence between the B and the C rows in four ways on MPDD, using six categories, seeds 0 and 1, $K$ equal to 1 and 4, four support conditions and the study's shared bootstrap stream: the canvas rule itself; a closed-form orthogonal Procrustes map fitted on the support rows and applied to the query and reference rows alike; a position permutation of the C rows, identical for queries and references; and a Sinkhorn optimal-transport correspondence whose cost matrix is the cross-branch cosine distance of the support descriptors, with its entropy regularizer fixed a priori at 0.1 times the interquartile range of that matrix. The transport rule mixes each C row over several canvas positions instead of relabeling it. We also report the exact assignment obtained from the same cost matrix as the regularizer tends to zero.

{{table:correspondence}}

{{table:correspondence_sensitivity}}

Both readings are robust. Across the seven settings, the canvas rule, Procrustes, the permutation and four regularizer values including the exact assignment, all fourteen point estimates are positive and all fourteen intervals exclude zero at the 98.75% family level. The exact assignment is the strongest of the set, and the only cell whose lower bound sits close to zero is the intermediate 0.05 regularizer value on $I_{BAL}$, at +0.006 points.

Two properties of the transport rule belong with this table. The soft mixing also changes the multiset of the C descriptors, since each row becomes a weighted combination of roughly 15 to 40 canvas positions, with a median row-maximum weight of 0.044, whereas the canvas rule, Procrustes and the position permutation all preserve that multiset; the exact assignment preserves it as well while sharing the cost matrix with the soft rule. The sweep is nonetheless reported in full rather than summarized by its prescribed regularizer, so that a reader can see that neither the sign nor the interval separation of the interaction depends on that constant. Table 18 gives that sweep for MPDD and BTAD and repeats the wide-scope additional-encoder rows of Table 15 beside it.

The transport plans themselves carry almost no canvas-position information: the median diagonal mass is 0.000949 against a chance value of 0.000977, and the fitted Procrustes map sits at a Frobenius distance of about 39 from the identity, so neither solves a position-level correspondence. We also record the verification of the new variant: it recovers a known synthetic assignment exactly, it reproduces the stored patch scores when the plan is forced to the identity with a maximum absolute difference of 6.4e-07, and the three earlier variants reproduce to at most 1.8e-06 once the new code path is present. The intervals in this table are percentile bounds of the image-level bootstrap series, formed inside each replicate and aggregated over categories and conditions before the percentile is taken, which is the convention of the primary tables. On MPDD the canvas row reproduces the S branch's interaction of Table 15 under that convention: its replicate mean is +0.695 against +0.695 and its interval [+0.193, +1.160] is the same, the two agreeing to 2.4e-07 in the bounds, so the 0.07-point gap between the point column of Table 17 and the S row of Table 15 is the difference between the condition-averaged difference and the replicate mean rather than a difference between scoring chains. On BTAD this harness still scores through its own path, and its BTAD numbers must not be mixed with the D, E1 or E2 numbers.

On BTAD all four variants were run, together with the same sweep over four regularizer values. No interval excludes zero for either contrast: the canvas rule gives +0.001 points [−0.183, +0.299] for $I_{TRI}$ and −0.080 [−0.270, +0.226] for $I_{BAL}$, Procrustes gives +0.001 [−0.183, +0.299] and −0.080 [−0.270, +0.226], the position permutation gives +0.234 [−0.058, +0.715] and +0.217 [−0.112, +0.773], and the soft mixing at the prescribed regularizer gives +0.115 [−0.109, +0.465] and +0.103 [−0.156, +0.561]. The regularizer sweep spans the same range: the exact assignment gives +0.220 [−0.044, +0.660] and +0.148 [−0.181, +0.699], the intermediate 0.05 value gives +0.162 [−0.080, +0.554] and +0.156 [−0.151, +0.653], and the widest mixing at 0.5 gives +0.061 [−0.124, +0.363] and +0.025 [−0.170, +0.353]. All fourteen intervals span zero, so on this dataset neither replacing the correspondence nor changing the amount of smoothing in the transport rule changes the judgement, which was already "no evidence of a direction".

#### 4.2.13 Closure of the Geometric, Seed and Backbone Extensions

Three further checks close gaps recorded in Section 4.2.8 without changing the primary conclusions.

The corrected BTAD category-03 geometry was recomputed on a finer stride-four evaluation grid covering all three categories. The reproduction check against the study revision passes on four cells with a maximum absolute difference of 7.0e-08, and the nested-support check records no violation in sixteen tests. The resulting dataset-level adjusted intervals are −0.011 points [−0.224, +0.251] for $I_{TRI}$ and −0.085 [−0.296, +0.177] for $I_{BAL}$; neither excludes zero, so the coarser stride-eight reading of Section 4.2.4 is unchanged at the finer grid. Figure S3 collects the supporting geometry panels and the eight per-image cases.

The eight-seed extension of Section 4.2.11 pools all three BTAD categories, including 03, under the canonical-mask convention, a 448 by 588 mask on the 32 by 42 grid that was verified on disk. That is not the corrected-geometry convention used for the primary BTAD tables, so the two sets of numbers should not be quoted interchangeably; the batch is descriptive in any case, even though its reproduction gate now passes at the dataset macro level.

E3 places a third backbone family in the extra slot: a window-attention hierarchical transformer whose two retained stages match the strides and the channel split of the D branch, giving a 576-dimensional descriptor on the B canvas. Its interactions appear in Table 15, and like E1 and E2 it was selected after the S and D results were known. Figure S2 reports the one completed ablation of a shared operation, at seed 0 with $K$ equal to 1; because that scope is a single condition with one run per ablation, the panel is exploratory, carries no interval, and is not evidence that any shared operation has been validated.

A consolidated list of the supplementary material — Figures S1 to S3 and the per-sample figures, tables and baseline table that this text does not embed, with their file locations — is given at the end of the manuscript.


## 5 Conclusion

We studied how normal-reference matching changes the benefit of an additional visual representation in few-shot industrial anomaly localization. A common fixed-memory formulation, an exact duplicate control, and two representation-replacement contrasts separate effective weights, new descriptors, and reference-selection constraints. Joint and independent matching are existing operations; the result of interest is their directly estimated interaction with the representation change.

With DINOv2-S, MPDD shows positive matching interactions while the absolute gains under independent matching remain uncertain. BTAD shows positive representation effects without a clear aggregate matching interaction. The prespecified WideResNet50-2 extension yields positive interactions on both datasets. A paired comparison supports larger D interactions on BTAD, while leaving the S-to-D difference uncertain on MPDD. Full-pixel point estimates preserve these aggregate directions, but full-pixel intervals have not been computed.

These findings support checking both effective weights and normal-reference selection when enlarging a frozen encoder set. They do not establish that independent matching or additional encoders are universally optimal. The limited datasets, conditional bootstrap inference, common-region baseline comparison, and incomplete resource coverage bound the conclusions. Further work should test the same controlled question on untouched datasets and quantify complete deployment costs before treating the observed interactions as a general design rule.

Two extensions bound and extend these conclusions. A confirmation set whose expectation was frozen before any of its features were encoded meets that expectation, so the direction of the MPDD result is not an artefact of the development that preceded it, and the same contrasts on two further datasets are clearly positive on MVTec AD and VisA, essentially zero on BTAD, and largest on the dataset that is in-domain for the C branch. The sign of the interaction is insensitive to the canvas-correspondence convention, and so is the exclusion of zero: on MPDD all fourteen intervals exclude zero under every correspondence variant and regularizer value, including the transport variant that additionally smooths the C branch, whose weakest cell keeps its lower bound at +0.006 points, while on BTAD no variant excludes zero, so the judgement there is unchanged. The encoder-transfer and support-seed extensions remain exploratory: their condition scopes differ from the primary one, and the seed batch's reproduction gate passes at the dataset macro level.

## Data and Code Availability

All five datasets are public and come from their original providers; none of them is redistributed with this study. `data/README.md` records, per dataset, the source, the download location, the archive size and checksum, and the licence. MPDD is obtained from a mirror of the provider's release [2] and BTAD from its public distribution server [3]; for these two, `data/README.md` does not yet record a licence term, so their redistribution terms remain to be settled before any dataset copy is shared. MVTec AD is distributed under CC BY-NC-SA 4.0 (non-commercial) [1], VisA under CC BY 4.0 [4], and KolektorSDD2 under CC BY-NC-SA 4.0 (non-commercial) [34]. The support manifests that define every reported condition are the frozen files `data/splits/<dataset>/manifest.json` together with their SHA-256 sidecars; what the study versions is the split definition, not the images.

The code, configurations and derived artefacts are organised so that each reported workflow has a documented entry point and a machine-readable summary. The directory-to-product-to-command index is `docs/ARTIFACT_INDEX.md`; the workflow specifications and their verification gates are under `docs/specs/`; and the artefact-to-figure binding table is `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`. Support manifests, feature-path specifications, geometry revisions, per-condition metrics, paired bootstrap outputs and figure-generation sources are retained in the project archive. The accompanying release checklist states what a public or hand-over package contains, what is deliberately excluded and why, and the order in which the excluded feature caches have to be regenerated (`docs/REPRODUCIBILITY_PACKAGE.md`).

The frozen results were produced with the pinned interpreter and package set recorded in `docs/environment_matrix.md` and listed in `requirements_repro.txt`; feature caches and dataset files are not part of the versioned sources and must be regenerated or obtained separately.

The public location of the reproduction package has not been finalized, so this draft claims no public package and no permanent archive. Three items are left for the authors and are marked as placeholders in this source: the repository address `[[REPO_URL]]`, the archived snapshot identifier `[[ZENODO_DOI]]`, and the licence of the released package `[[LICENSE]]`.

## References

{{references}}

## Supplementary Method Figures

{{figure:encoders_geo}}

## Supplementary Results Figures

{{figure:shared_op_ablation}}

{{figure:extra_cases}}

The supplementary material consists of Figures S1 to S3 together with the per-sample material that the text does not embed: Figure S1 records the frozen branches and their native geometry (cited from Section 3.7), Figure S2 the one completed shared-operation ablation and Figure S3 the geometry panels with the eight per-image cases (both cited from Section 4.2.13); Table 18 in Section 4.2.12 reports the transport regularizer sweep on MPDD and BTAD with the wide-scope additional-encoder rows of Table 15 beside it, and the correspondence tables it belongs to are cited from Section 4.2.12; the thirty-six multi-method per-sample comparison figures in the Figure 7 convention, covering MPDD, BTAD, MVTec AD and VisA, are archived as `docs/figures_reference_matching_20260914/fig7_multimethod_*.png` with their figure-to-script-to-data binding in `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`, the per-unit and per-image tables behind them are stored with each scored unit as `metrics.csv` and `per_image.csv` in the project archive, and the shared-region baseline table those figures draw on is `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv`.
