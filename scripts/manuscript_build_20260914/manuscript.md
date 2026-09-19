# Interaction between Additional Visual Representations and Normal Reference Matching in Few-Shot Industrial Anomaly Localization

## Abstract

Few-shot industrial anomaly localization uses a small set of normal images to identify anomalous regions in unseen queries. Combining pretrained visual encoders can enrich the available descriptors, but an additional branch also changes effective weights and the normal patches selected as references. We study whether the benefit of an additional representation depends on this reference-selection constraint. With frozen encoders, shared support images, and fixed distance weights, we compare joint matching, which selects one reference patch across branches, with independent matching, which selects a reference separately in each branch. Duplicate-branch and weight-preserving controls distinguish new representations from reweighting, and paired differences of representation effects quantify their interaction with matching. Adding DINOv2-S yields positive interactions of 0.77 and 0.60 pixel average-precision percentage points on MPDD, with multiplicity-adjusted intervals excluding zero, whereas BTAD provides insufficient evidence of interaction. A prespecified WideResNet50-2 branch yields positive interactions of 0.50–0.97 points on both datasets. These estimates use stride-eight pixel evaluation; full-pixel point estimates retain their directions. The results show that additional-branch value and its dependence on matching are distinct, and that the latter varies with the encoder and dataset rather than following branch count alone. A confirmation set whose expectation was frozen before any of its features were encoded meets that expectation, with positive interactions for both encoders and both contrasts; the same contrasts on four datasets are positive on MPDD, MVTec AD and VisA and essentially zero on BTAD, and on MPDD both the sign of the interaction and the exclusion of zero are insensitive to the canvas-correspondence convention, including an optimal-transport variant that additionally smooths the C branch.

Keywords: few-shot anomaly localization; frozen visual encoders; normal reference matching; fixed feature fusion; representation interaction.

## 1 Introduction

Industrial visual inspection must locate defects whose appearance is difficult to enumerate before deployment. A new product may provide only a few verified normal images, while representative examples of scratches, contamination, missing parts, or structural defects remain unavailable. Industrial anomaly benchmarks make this distinction concrete by providing normal training images and heterogeneous test anomalies [@mvtec;@mpdd;@btad;@visa]. Under a few-shot normal-reference protocol, the objective is to identify departures from the available normal appearance without learning a target defect classifier.

Frozen pretrained encoders offer a practical starting point. Their local descriptors allow a query patch to be compared with a memory of normal support patches, avoiding target-domain gradient optimization. AnomalyDINO demonstrates the value of this simple approach with DINOv2 features [@anomalydino;@dinov2]. Multiple encoders can supply different descriptions of the same image, and recent methods already combine visual and vision-language pretrained representations [@sea;@anomalyclip]. However, a higher score for an entire fusion system does not explain which part of adding an encoder produced the change.

Three factors become entangled in a direct comparison between two and three equally weighted branches. The additional encoder changes the available representation, the total weight assigned to existing information, and potentially the support patch selected under a shared matching rule. For example, copying one existing branch adds no information, yet changes its effective weight from one half to two thirds when three branch distances are averaged. Replacing that copy with a different encoder is a separate intervention. Treating both changes as the contribution of a third branch can therefore overstate, or conceal, the value of the new representation.

Normal-reference selection introduces another distinction. Joint matching requires all branches to score the same normal support patch before the best candidate is selected. Independent matching lets each branch choose its own closest normal patch before the distances are averaged. Additional features can change the selected reference under either fixed rule; adding a branch does not itself change the rule. Independent matching cannot yield a larger raw minimum-distance score than joint matching under the assumptions in Section 3.3. Nevertheless, a smaller anomaly score does not necessarily improve the ranking of defective and normal pixels. The performance consequence must be measured rather than inferred from the distance inequality.

This question connects established research on multimodal fusion with work on consistent neighborhoods in multi-view anomaly detection [@adnas;@scone;@muvad;@ncnets]. We do not introduce nearest-neighbor matching, early or late fusion, or the idea of shared neighborhoods. Our focus is narrower: under frozen visual encoders, fixed weights, and identical few-shot supports, does the localization benefit of replacing an existing representation depend on whether normal references are shared across branches? We examine both the absolute representation effect and the direct difference between that effect under the two matching rules.

The contributions are as follows.

1. **A common formulation of reference selection in fixed visual fusion.** We express joint and independent matching on the same aligned normal patch bank, with the same branch distances and weights. This separates the descriptors being combined from the constraint on which support patch may explain a query. The formulation makes the reference-selection difference explicit and distinguishes a raw score constraint from a localization-performance claim. Its contribution is a precise analytical basis for this setting, rather than a new matching operator or an original distance inequality.

2. **A controlled representation-replacement design that isolates the matching interaction.** Starting from a dual-visual anchor, we use an exact duplicate branch to expose effective-weight changes, replace that duplicate with a genuinely different encoder at fixed slot weights, and add a complementary control that preserves the weight of the original representation group. Crossing each construction with both matching rules yields a direct representation-by-matching interaction. This design answers whether a representation becomes more useful under a different reference constraint, instead of attributing every two-to-three-branch difference to new information.

3. **Evidence that the interaction depends on the encoder and data conditions.** The DINOv2-S replacement has positive matching interactions on MPDD but no clear aggregate interaction on BTAD, despite positive representation effects on BTAD. A prespecified WideResNet50-2 replacement produces positive interactions in both datasets; a direct comparison detects larger interactions than DINOv2-S on BTAD but leaves their difference uncertain on MPDD. These findings distinguish the usefulness of an added representation from its dependence on matching. Reference-budget, category, qualitative, baseline, and resource analyses delimit the observations rather than forming a separate methodological contribution.

The study is an analysis of controlled fusion choices, not a claim that one three-encoder network is universally preferable. The original dual-encoder configuration, referred to as A1 below, serves as an anchor. Its earlier project name, DCFnet, is not used to rename all variants or to imply a newly validated network architecture.

## 2 Related Work

Industrial anomaly localization methods differ in how they represent normality, how much target adaptation they require, and how they combine evidence. We organize the relevant work around normal-model learning, local reference memories, foundation-model fusion, and multi-view neighborhoods. The last group is necessary because shared versus independent neighborhood structure predates the present industrial setting.

### 2.1 Reconstruction and Normal Model Learning

Reconstruction methods identify anomalies through departures from an estimated normal appearance. SLSG combines generative pretraining, simulated anomalies, and graph-based modeling of normal embeddings [@slsg]. RealNet uses diffusion-based anomaly synthesis and feature and residual selection to improve anomaly-sensitive reconstruction evidence [@realnet]. These methods illustrate how a fitted normal model or anomaly discriminator can improve separation, while introducing training objectives and adaptation decisions. They address a different trade-off from a fixed normal-reference system that performs no target optimization.

Distributional patch models offer another description of normality. PaDiM models the distribution of pretrained patch embeddings with multivariate Gaussians [@padim]. This avoids reconstructing an image, but the estimated normal distribution depends on the available samples and feature dimensionality. Our study instead retains observed support descriptors and changes only their representation composition and reference-selection rule. It does not establish that fixed retrieval is preferable to fitted models in settings with larger normal training sets.

### 2.2 Feature Memories and Few Shot Normal References

PatchCore uses a representative memory of normal local descriptors and nearest-neighbor scoring [@patchcore]. Its coreset and image preprocessing affect both normal coverage and computational cost. AnomalyDINO shows that frozen DINOv2 patches provide a strong basis for few-shot detection [@anomalydino]. These methods motivate an explicit account of the memory candidates, selected feature layers, and spatial coverage when interpreting a fusion comparison.

Several recent studies modify the representation or the normal reference rather than simply increasing the number of encoders. FEAD enriches sparse normal patterns through conditional feature transformation and multi-frequency modeling [@fead]. K-NG studies few-shot online detection through an evolving Neural Gas representation [@kng]. PGAD combines global invariance and multiscale local evidence with score calibration [@pgad], while FastRef refines normal prototypes at test time [@fastref]. SubspaceAD models frozen visual descriptors through a principal subspace [@subspacead], and DCP-SFR addresses the preservation of shallow defect information in deep representations [@dcp_sfr]. These approaches show that reference coverage, cue retention, and adaptation can materially alter anomaly scores. Our fixed-memory setting deliberately excludes query-conditioned updates so that they do not confound the comparison between matching rules.

### 2.3 Foundation Models and Multi Branch Fusion

Vision-language pretraining provides transferable visual and textual representations [@clip]. WinCLIP combines prompt ensembles and local visual features for zero- and few-shot anomaly detection [@winclip]. AnomalyCLIP learns object-agnostic prompts for normality and abnormality [@anomalyclip], PromptAD learns from normal target samples [@promptad], and InCTRL uses in-context residual learning with sample prompts [@inctrl]. AA-CLIP introduces anomaly-aware alignment [@aaclip], and FAPrompt develops fine-grained abnormality prompts [@faprompt]. UniVAD broadens training-free reference-based anomaly detection across different domains [@univad]. These methods differ in their training data, prompt use, adaptation, and inference paths; they should not all be described as requiring target defect supervision.

The present C branch retains only the visual descriptor path of AnomalyCLIP. Its use of a vision-language pretrained backbone does not make our inference a text-image fusion system. No text-encoder score or learned prompt output enters the anomaly score. This distinction matters when comparing the controlled visual branches with complete published vision-language systems.

Sea-CLIP is especially close because it combines CLIP and DINOv2 representations for few-shot anomaly detection [@sea]. Its matching and decoder components already involve both shared-reference-like operations and independent nearest-neighbor evidence. Its complete architecture is not identical to our symmetric weighted-distance comparison, but it precludes claiming that combining these encoders or coupling their references is new. M3DM combines RGB and point-cloud information with multiple memories [@m3dm], and CIF uses hypergraph structural commonality to guide few-shot multimodal reference memories [@cif]. The architectural analysis underlying 3D-ADNAS examines conditional benefits of fusion modules and alternative fusion stages [@adnas]. Thus, neither multimodal fusion nor the conditional value of an added module is a new general proposition of this paper.

Our contribution differs in the controlled question. We hold the normal support identities and distance weights fixed while replacing one visual representation, then estimate how that replacement effect changes when a common reference constraint is removed. We do not infer this interaction from the overall scores of different end-to-end architectures, and we do not claim a comprehensive comparison with all of those systems.

### 2.4 Multi View Neighborhood Consistency

Multi-view anomaly detection explicitly studies disagreement and consistency across representations. MUVAD uses neighborhood information to distinguish cross-view inconsistency from anomalies that are unusual in multiple views [@muvad]. Neighborhood Consensus Networks align neighborhood structures across views [@ncnets], while ECMOD uses contrastive representation learning with neighborhood-consistency information [@ecmod]. SCoNE directly addresses consistent local neighborhoods across views and discusses the limitations of recovering them from independently represented neighborhoods [@scone]. These studies establish that the choice between separate and consistent neighborhoods is an existing research problem.

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

Table 2 records the frozen feature paths and the shared processing choices. Figure S1 summarises the same configuration as native input geometry, aligned grids, retained descriptor widths and the resulting fused width. The B and S encoders use DINOv2 patch features [@dinov2]. C uses a CLIP ViT-L/14 visual backbone with AnomalyCLIP's diagonally prominent attention map path [@clip;@anomalyclip]. Its 518-pixel input yields a 37 by 37 grid; the final returned patch tensor is retained after projection, excluding the class token. Although the inherited setup loads prompt-related checkpoint material, no text or prompt score is used in our visual-only inference.

{{table:models}}

The common lattice follows the B canvas. Inputs are resized with preserved aspect ratio to a short side of 448 pixels and cropped from the top left to dimensions divisible by 14. The C grid is mapped to that retained image extent rather than blindly stretched to the uncropped source. On BTAD category 03, the resized extent is 448 by 597 pixels and the retained canvas is 448 by 588. The current evaluation maps both predictions and masks through the corresponding coordinates. Geometric consistency does not imply identical receptive fields or learned semantic alignment between encoders.

The D branch was specified before its results were generated. It uses ImageNet-pretrained WideResNet50-2, bilinearly resamples layer2 and layer3 to the B lattice, concatenates their 512- and 1024-channel outputs, and normalizes the resulting 1536-dimensional descriptor. Its query-feature cache is stored in float16 and converted to float32 for normalization and scoring; this storage choice is recorded in the reproduction manifest. The B/S/C features and D features do not share a universal 768-dimensional output. All encoder parameters remain frozen, so target optimizer, learning rate, training epochs, and training-loss curves are not applicable.

## 4 Experimental Evaluations

### 4.1 Experimental Design

#### 4.1.1 Datasets and Reference Protocol

The current-theme experiments use the Metal Parts Defect Detection dataset (MPDD) and the beanTech Anomaly Detection dataset (BTAD) [@mpdd;@btad]. Their six and three categories, respectively, provide different normal appearances and defect distributions. The old project's MVTec AD and VisA experiments are not reused as if they evaluated the new representation-by-matching design. A later extension does run the same controlled contrasts on MVTec AD and VisA as frozen validation sets, and on KolektorSDD2 as a confirmation set whose expectation was frozen before any of its features were encoded; those runs are new, they are reported separately in Sections 4.2.9 to 4.2.13, and they are not the old project's experiments. MPDD has informed development, and BTAD has already been examined in the project; neither the present interaction analysis nor the encoder extension is described as a fresh unseen-dataset confirmation.

Table 3 records the evaluation scope of both studies, including the seed and support budgets that each one uses and which of them the encoder comparison reuses.

{{table:protocol}}

For each category and seed, the support sequence is fixed and smaller budgets are prefixes of the same sequence. All methods in a paired comparison use exactly the same support images and query images. The S study uses seeds 0, 1, and 2 on MPDD and 0 and 1 on BTAD, with $K$ equal to 1, 2, 4, and 8. This gives 72 and 24 category-seed-budget units, respectively, or 12 and 8 dataset-level support conditions. These are repeated evaluations on shared data, not 96 independent datasets.

The prespecified D extension uses seeds 0 and 1 and $K$ equal to 1 and 4 on both datasets, giving 36 category-level units. A1 and DUP controls are rescored within that scope. The S-to-D interaction comparison also uses that restricted scope, avoiding differences caused by unequal support-condition coverage. No additional encoder or dataset was selected after comparing multiple candidate extension results.

#### 4.1.2 Baselines and Control Scope

The primary controlled matrix consists of single-branch B, S, and C together with the J/L forms of A1, DUP, TRI, and BAL. These are eleven analysis configurations, not eleven independently proposed algorithms. Two further constructions check numerical equivalence of the duplicated representation and its effective-weight formulation. The D extension adds the D-only path and its TRI/BAL combinations. Single-branch removal is a matched control; it should not be presented as evidence for an independently novel network module.

For practical context, we also evaluate native-method configurations of AnomalyDINO and PatchCore [@anomalydino;@patchcore]. AnomalyDINO is run on the native image canvas both with and without the reference-rotation option. PatchCore includes an official-resolution 224-pixel configuration with 1024-dimensional projected features and the earlier local 128-pixel/256-dimensional configuration. The latter is retained to expose configuration sensitivity, rather than being treated as the sole representative of PatchCore. Backbones, feature dimensions, preprocessing, reference augmentation, and search pipelines remain method-specific in this comparison; consequently it does not isolate matching or establish a general state-of-the-art ranking.

#### 4.1.3 Evaluation Metrics and Uncertainty

Pixel AP is the primary metric because it evaluates anomaly ranking while emphasizing precision and recall under sparse defect pixels. Within each category, pixel scores and labels are pooled across its test images; category APs are then averaged equally. Support conditions are averaged with equal weight at the dataset level. This differs from pooling all categories into one AP and from averaging per-image AP. Pixel area under the receiver operating characteristic curve (AUROC) is a secondary diagnostic; it is not substituted for AP when interpreting the primary interaction.

We distinguish three evaluation grids. The main resampling analysis uses a regular stride-eight subset of the retained output-canvas grid, which bounds the computational cost of image-level resampling. Full-pixel evaluation uses every output pixel and provides point estimates for a resolution-sensitivity check. The cross-method comparison maps each method's prediction to its actual coverage in original-image coordinates and evaluates only their common valid intersection. Tables and captions identify these grids explicitly; their AP values are not placed in a single interchangeable ranking.

Uncertainty is estimated by 1000 paired image-level bootstrap replicates, sampling with replacement within each fixed category, without additional normal/abnormal stratification. A sampled image contributes its sampled pixels as a block, and the same replicate stream is shared across methods, seeds, and budgets. Conditions and categories are aggregated within a replicate before its contrast is summarized. The base random seed is 20260913; the deterministic stream also incorporates dataset identity, category identity, and replicate index. These intervals characterize test-image sampling conditional on the selected categories, encoders, and finite support manifests. They do not resample the population of possible support sets or provide uncertainty over arbitrary future datasets.

For the four primary S interactions, two constructions across two datasets, we report 95% exploratory intervals and 98.75% percentile intervals corresponding to a four-comparison Bonferroni adjustment. The four D interactions and the four matched encoder differences are separate exploratory families with the same adjustment. The extensions reported in Sections 4.2.9 to 4.2.12 use the levels stated with them: the 95% interval for the confirmation set, which receives no family adjustment, and the 95%, 98.75% and 99.375% levels for the eight-cell four-dataset family. These are approximate family adjustments built on bootstrap intervals; 1000 replicates limit precision in the extreme tails. They are not a single simultaneous guarantee over all subsequent subgroup plots and secondary metrics. The interaction analysis is post hoc to earlier project exploration, even though the D specification was frozen before D results.

We use 0.5 AP percentage points as a descriptive scale for judging the magnitude of an interaction, not as an established industrial utility threshold or an acceptance criterion selected independently of this project. A point estimate above that scale does not mean its interval lies above it. An interval spanning zero is treated as insufficient evidence of a direction, not as statistical equivalence. Full-pixel results currently have no bootstrap intervals and cannot support claims of full-pixel statistical significance.

#### 4.1.4 Implementation and Computing Environment

The archived runs use an NVIDIA GeForce RTX 3060 Laptop GPU with 6 GB VRAM, an Intel Core i9-12900H processor, and 16 GB system RAM. Encoders run in evaluation mode without gradient updates. Query features are cached to avoid repeating feature extraction for each controlled score variant; scoring and evaluation still run for every applicable support condition. Exact search implements the distance definitions in Section 3, with FAISS used where appropriate [@faiss]. No target loss is optimized.

The manuscript uses the final geometry-consistent BTAD revision. Earlier BTAD category-03 ground-truth and feature-grid transformations were audited, then affected point estimates and bootstrap comparisons were regenerated. Original point estimates are reported as such; bootstrap means are retained in the source tables but are not substituted for them. This distinction also applies to per-budget aggregates, which average all available seeds rather than displaying only the last processed seed.

Resource measurements are reported by stage and configuration. Historical controlled runs did not record all per-unit feature and scoring times, so a later partial timing is not reconstructed into an end-to-end latency. PatchCore's combined memory-and-scoring stage cannot be split retrospectively. Per-process GPU memory is unavailable for PatchCore in the current instrumentation, and device-wide usage is not substituted for it. These restrictions affect practical comparisons but do not alter the stored anomaly predictions.

### 4.2 Results and Analysis

{{results}}

## 5 Conclusion

We studied how normal-reference matching changes the benefit of an additional visual representation in few-shot industrial anomaly localization. A common fixed-memory formulation, an exact duplicate control, and two representation-replacement contrasts separate effective weights, new descriptors, and reference-selection constraints. Joint and independent matching are existing operations; the result of interest is their directly estimated interaction with the representation change.

With DINOv2-S, MPDD shows positive matching interactions while the absolute gains under independent matching remain uncertain. BTAD shows positive representation effects without a clear aggregate matching interaction. The prespecified WideResNet50-2 extension yields positive interactions on both datasets. A paired comparison supports larger D interactions on BTAD, while leaving the S-to-D difference uncertain on MPDD. Full-pixel point estimates preserve these aggregate directions, but full-pixel intervals have not been computed.

These findings support checking both effective weights and normal-reference selection when enlarging a frozen encoder set. They do not establish that independent matching or additional encoders are universally optimal. The limited datasets, conditional bootstrap inference, common-region baseline comparison, and incomplete resource coverage bound the conclusions. Further work should test the same controlled question on untouched datasets and quantify complete deployment costs before treating the observed interactions as a general design rule.

Two extensions bound and extend these conclusions. A confirmation set whose expectation was frozen before any of its features were encoded meets that expectation, so the direction of the MPDD result is not an artefact of the development that preceded it, and the same contrasts on two further datasets are clearly positive on MVTec AD and VisA, essentially zero on BTAD, and largest on the dataset that is in-domain for the C branch. The sign of the interaction is insensitive to the canvas-correspondence convention, and so is the exclusion of zero: on MPDD all fourteen intervals exclude zero under every correspondence variant and regularizer value, including the transport variant that additionally smooths the C branch, whose weakest cell keeps its lower bound at +0.006 points, while on BTAD no variant excludes zero, so the judgement there is unchanged. The encoder-transfer and support-seed extensions remain exploratory: their condition scopes differ from the primary one, and the seed batch's reproduction gate passes at the dataset macro level.

## Data and Code Availability

All five datasets are public and come from their original providers; none of them is redistributed with this study. `data/README.md` records, per dataset, the source, the download location, the archive size and checksum, and the licence. MPDD is obtained from a mirror of the provider's release [@mpdd] and BTAD from its public distribution server [@btad]; for these two, the terms now recorded in `data/README.md` are CC BY-NC-SA 4.0 (MPDD, as recorded from the provider repository licence file) and CC BY-SA 4.0 (BTAD, as recorded from the original authors' repository), and their redistribution terms remain to be settled with the providers before any dataset copy is shared. MVTec AD is distributed under CC BY-NC-SA 4.0 (non-commercial) [@mvtec], VisA under CC BY 4.0 [@visa], and KolektorSDD2 under CC BY-NC-SA 4.0 (non-commercial) [@ksdd2]. The support manifests that define every reported condition are the frozen files `data/splits/<dataset>/manifest.json` together with their SHA-256 sidecars; what the study versions is the split definition, not the images.

The code, configurations and derived artefacts are organised so that each reported workflow has a documented entry point and a machine-readable summary. The directory-to-product-to-command index is `docs/ARTIFACT_INDEX.md`; the workflow specifications and their verification gates are under `docs/specs/`; and the artefact-to-figure binding table is `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`. Support manifests, feature-path specifications, geometry revisions, per-condition metrics, paired bootstrap outputs and figure-generation sources are retained in the project archive. The accompanying release checklist states what a public or hand-over package contains, what is deliberately excluded and why, and the order in which the excluded feature caches have to be regenerated (`docs/REPRODUCIBILITY_PACKAGE.md`).

The frozen results were produced with the pinned interpreter and package set recorded in `docs/environment_matrix.md` and listed in `requirements_repro.txt`; feature caches and dataset files are not part of the versioned sources and must be regenerated or obtained separately.

The public location of the reproduction package has not been finalized. The package will be made public when the paper is published, and the archive DOI will be provided upon acceptance, so this draft claims no public package and no permanent archive at this time. Licensing is split three ways. The code is released under the MIT Licence (repository root `LICENSE`, Copyright (c) 2026 LiYuening). The derived artefacts released with the package - derived tables, figures and the manuscript sources - carry the same licence as the code; any item that the root `LICENSE` does not explicitly cover remains for the authors to confirm. Dataset licences are separate and are not covered by the code licence, and the datasets themselves are not redistributed here.

## References

{{references}}

## Supplementary Method Figures

{{figure:encoders_geo}}

## Supplementary Results Figures

{{figure:shared_op_ablation}}

{{figure:extra_cases}}

The supplementary material consists of Figures S1 to S3 together with the per-sample material that the text does not embed: Figure S1 records the frozen branches and their native geometry (cited from Section 3.7), Figure S2 the one completed shared-operation ablation and Figure S3 the geometry panels with the eight per-image cases (both cited from Section 4.2.13); Table 18 in Section 4.2.12 reports the transport regularizer sweep on MPDD and BTAD with the wide-scope additional-encoder rows of Table 15 beside it, and the correspondence tables it belongs to are cited from Section 4.2.12; the thirty-six multi-method per-sample comparison figures in the Figure 7 convention, covering MPDD, BTAD, MVTec AD and VisA, are archived as `docs/figures_reference_matching_20260914/fig7_multimethod_*.png` with their figure-to-script-to-data binding in `docs/figures_reference_matching_20260914/FIGURE_BINDING.md`, the per-unit and per-image tables behind them are stored with each scored unit as `metrics.csv` and `per_image.csv` in the project archive, and the shared-region baseline table those figures draw on is `experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_multi_dataset/baseline_common_region.csv`.
