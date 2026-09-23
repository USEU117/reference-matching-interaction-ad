# Interaction between Additional Visual Representations and Normal Reference Matching in Few-Shot Industrial Anomaly Localization

## Abstract

Few-shot industrial anomaly localization compares query images with a small normal support set. Adding a pretrained visual encoder changes both the available representation and its interaction with normal-reference selection. We investigate this dependence using frozen encoders, identical supports, and fixed distance weights. Joint matching selects one support patch shared across branches; independent matching selects a reference separately for each branch. An exact duplicate control isolates reweighting, while two representation-replacement contrasts quantify how matching changes the value of additional descriptors. With DINOv2-S, the primary MPDD interactions are +0.772 and +0.595 pixel average-precision percentage points, whereas BTAD does not establish an interaction direction. Extensions to MVTec AD and VisA yield positive interactions, with VisA treated as in-domain validation. A separately specified KolektorSDD2 confirmation meets all four directional criteria for DINOv2-S and WideResNet50-2. Additional encoder and support-seed analyses reveal substantial conditional variation, including an inconclusive ConvNeXt interaction on MPDD. Correspondence perturbations retain positive MPDD mean interactions, although these sensitivity results currently support descriptive rather than inferential conclusions. These findings distinguish representation usefulness from matching dependence and identify the conditions under which additional frozen features provide stronger localization gains.

Keywords: few-shot anomaly localization; frozen visual encoders; normal reference matching; fixed feature fusion; representation interaction.

## 1 Introduction

Industrial visual inspection must locate defects whose appearance is difficult to enumerate before deployment. A new product may provide only a few verified normal images, while representative examples of scratches, contamination, missing parts, or structural defects remain unavailable. Industrial anomaly benchmarks make this distinction concrete by providing normal training images and heterogeneous test anomalies [1, 2, 3, 4]. Under a few-shot normal-reference protocol, the objective is to identify departures from the available normal appearance without learning a target defect classifier.

Frozen pretrained encoders offer a practical starting point. Their local descriptors allow a query patch to be compared with a memory of normal support patches, avoiding target-domain gradient optimization. AnomalyDINO demonstrates the value of this simple approach with DINOv2 features [5, 6]. Multiple encoders can supply different descriptions of the same image, and recent methods already combine visual and vision-language pretrained representations [7, 8]. However, a higher score for an entire fusion system does not explain which part of adding an encoder produced the change.

Three factors become entangled in a direct comparison between two and three equally weighted branches. The additional encoder changes the available representation, the total weight assigned to existing information, and potentially the support patch selected under a shared matching rule. For example, copying one existing branch adds no information, yet changes its effective weight from one half to two thirds when three branch distances are averaged. Replacing that copy with a different encoder is a separate intervention. Treating both changes as the contribution of a third branch can therefore overstate, or conceal, the value of the new representation.

Normal-reference selection introduces another distinction. Joint matching requires all branches to score the same normal support patch before the best candidate is selected. Independent matching lets each branch choose its own closest normal patch before the distances are averaged. Additional features can change the selected reference under either fixed rule; adding a branch does not itself change the rule. Independent matching cannot yield a larger raw minimum-distance score than joint matching under the assumptions in Section 3.3. Nevertheless, a smaller anomaly score does not necessarily improve the ranking of defective and normal pixels. The performance consequence must be measured rather than inferred from the distance inequality.

This question connects established research on multimodal fusion with work on consistent neighborhoods in multi-view anomaly detection [9, 10, 11, 12]. We do not introduce nearest-neighbor matching, early or late fusion, or the idea of shared neighborhoods. Our focus is narrower: under frozen visual encoders, fixed weights, and identical few-shot supports, does the localization benefit of replacing an existing representation depend on whether normal references are shared across branches? We examine both the absolute representation effect and the direct difference between that effect under the two matching rules.

The contributions are as follows.

1. **A factorized account of representation value and normal-reference selection.** We formulate frozen multi-encoder localization on a common normal patch bank, distinguishing the descriptors, their distance weights, and the requirement to share a reference. This exposes why a lower independent-matching score cannot by itself establish better localization. The resulting account identifies the ambiguity in attributing the benefit of a larger encoder set to representation diversity alone; the matching operators and their distance inequality are established tools, not newly invented algorithms.

2. **Two complementary controls for the value of an additional representation.** An exact duplicate of the original descriptor separates the effect of reweighting from introducing information. Replacing that copy at fixed slot weights measures a representation change directly, while a second construction preserves the original branch-group weight. Applying both changes under both matching rules distinguishes absolute representation gains from gains that depend on reference selection. The contribution is the controlled decomposition of a fusion design question, rather than a new evaluation metric or a generic ablation procedure.

3. **A conditional empirical finding with a separate confirmation and explicit counterexamples.** Across five industrial datasets, matching dependence varies with the representation and data: the DINOv2-S interaction is positive on MPDD, MVTec AD and VisA but unresolved on BTAD, whereas the prespecified WideResNet50-2 extension is positive on both primary datasets. A separately specified KolektorSDD2 confirmation supports all four directional expectations. Further encoder, support-set and correspondence analyses show where the finding weakens, including ConvNeXt on MPDD and sensitivity to support selection. Correspondence substitutions provide a further descriptive robustness check whose inferential limitations are made explicit. These multi-branch results bound the design conclusion instead of presenting experimental evaluation itself as a methodological innovation.

The central question is therefore when normal-reference constraints alter representation value. The dual-encoder construction A1 is an analysis anchor; the study does not propose a universally superior three-encoder architecture.

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

$$
\mathcal{X}_c=\{\boldsymbol{x}_i^c:i=1,\ldots,K\}\tag{1}
$$

Here $x_i^c$ is support image $i$ of category $c$, and the query may be normal or anomalous. Category labels specify the relevant support bank; no target defect class is predicted. We use $p$ for a query patch, $r$ for an aligned support-patch index that contains both support-image identity and spatial position, and $b$ for a visual branch. The same index $r$ denotes the corresponding support location in every branch after spatial alignment. It does not require a query patch to match the same spatial coordinate in its support image.

The native outputs are a continuous pixel anomaly map $A_t$ and an image-level score $s_{\mathrm{img},t}$, where the matching-rule label $t$ is either J or L. A displayed defect contour is derived from the same map through a separately specified visualization threshold. It is not an additional learned output, a defect-category label, or a threshold calibrated for deployment. Test labels and masks are used for offline evaluation and example selection, not for selecting a reference during query inference. The roles of development, frozen validation and separately specified confirmation data are distinguished in Section 4.1.1.

### 3.2 Overview Structure

Support-bank construction and query scoring use the same frozen visual paths. Each support image is encoded, spatially mapped to the common lattice, and normalized branch by branch. All support patches are retained, with one aligned row identity across branches. The bank is fixed for a category, support seed and $K$. A query follows the same feature path, searches that bank, and produces patch scores under one of the two matching rules. The query never updates the bank.

The anchor combines DINOv2-B with the AnomalyCLIP visual path. Controlled variants duplicate the B descriptor or replace that copy with a different frozen encoder. Shared resizing and smoothing convert patch scores to the continuous output map, whose spatial maximum gives the image score. Matching is an experimental factor, not a learned runtime switch. No dynamic gate, learned fusion head, foreground selector or target-domain gradient optimization is introduced.

### 3.3 Normal Reference Matching

Let $F_b$ denote a branch feature tensor and $R_b$ its deterministic mapping to the common spatial lattice. At location $p$, branch-wise normalization produces a unit descriptor $g_{b,p}$. The branch distance between a query descriptor and a support descriptor is

$$
d_b(p,r)=1-\boldsymbol{g}_{b,p}^{\mathsf{T}}\boldsymbol{g}_{b,r}\tag{2}
$$

All reported constructions use nonnegative distance weights $w_b$ summing to one. The descriptors in Equation (2) are nonzero; numerical norm handling follows the archived implementation. With the same aligned candidate set $\mathcal{R}_c$ in every branch, joint matching is

$$
J(p)=\min_{r\in\mathcal{R}_c}\sum_b w_b d_b(p,r)\tag{3}
$$

Joint matching first sums the branch distances for each single candidate $r$, then selects the candidate with the smallest weighted distance. Equivalently, concatenating the normalized branch descriptors with coefficients equal to the square roots of their distance weights yields a unit joint descriptor. Half its squared Euclidean distance equals the weighted cosine distance. Thus, feature coefficients and distance weights must not be confused: equal thirds in distance require equal square-root coefficients, followed by the corresponding joint normalization.

Independent matching reverses the order of branch combination and candidate minimization:

$$
L(p)=\sum_b w_b\min_{r\in\mathcal{R}_c}d_b(p,r)\tag{4}
$$

Each branch can now select a different support patch. We denote the corresponding reference indices by $r_J$ and $r_{b,L}$ when discussing selected neighbors. Ties can select different indices with identical scores, so reference identity should be interpreted together with distance rather than as a unique explanation of every query.

The difference between the two raw patch scores is

$$
G(p)=J(p)-L(p)\geq0\tag{5}
$$

For every candidate, each branch distance is at least its own minimum; weighting and summing preserves that inequality, and minimizing the weighted sum does not reverse it. This is a standard algebraic property, not a new theorem. Equality holds when the branch minima admit a common minimizer, among other degenerate cases. A positive gap measures the cost in distance of imposing a common reference. It does not measure an improvement in defect localization, since average precision depends on the ordering of normal and anomalous pixels. The same distinction applies after common linear resizing and smoothing.

### 3.4 Representation Constructions and Weight Controls

We use upright branch labels B for DINOv2-B, S for DINOv2-S, C for the AnomalyCLIP visual descriptor, and D for WideResNet50-2. These identifiers are distinct from italic mathematical indices. Table 1 defines the constructions; their labels are kept unchanged throughout the paper. Matching labels J and L are upright identifiers, whereas the score functions in Equations (3)–(5) are italic. Scalars and indices are italic; feature vectors and full maps are bold italic; operators and descriptive subscripts are upright.

Table 1. Fixed representation constructions and the purpose of each control.

| Construction | Distance weights | Controlled comparison |
| --- | --- | --- |
| A1 | B 1/2; C 1/2 | Dual-visual anchor |
| DUP | B 1/3; B copy 1/3; C 1/3 | Reweight existing information; no new encoder |
| TRI | B 1/3; extra encoder 1/3; C 1/3 | Replace the duplicate at fixed slot weights |
| BAL | B 1/4; extra encoder 1/4; C 1/2 | Preserve C and total non-C weights |

Each construction is crossed with J and L. The extra slot is S or D in the main study and E1–E3 in exploratory extensions. Bold identifies the A1 anchor, not a best-performance claim.

Comparing DUP with A1 changes the effective weight of B without adding a new representation. DUP is also numerically equivalent to a two-branch B/C construction with weights two thirds and one third. Replacing the copied B descriptor in DUP with S produces TRI at identical slot weights. TRI minus DUP therefore measures the effect of that representation replacement rather than the entire difference between two and three encoders.

BAL provides a complementary comparison. In the S experiment, the combined DINO family weight remains one half, while C retains one half, allowing the B allocation to be split between B and S. In the D experiment, BAL preserves the total non-C weight but should not be called a DINO-family-preserving construction, since D is a convolutional ImageNet encoder. Neither control proves that its chosen weights are optimal. The duplicate is reused exactly, rather than obtained through another stochastic feature extraction, so it cannot add information through numerical randomness.

### 3.5 Representation Effects and Their Matching Interaction

Let $P$ denote category-macro pixel average precision (AP), first calculated for a specified support condition and evaluation grid. Under matching rule $t$, the two representation effects are

$$
E_{\mathrm{TRI},t}=P(\mathrm{TRI}_t)-P(\mathrm{DUP}_t)\tag{6}
$$

$$
E_{\mathrm{BAL},t}=P(\mathrm{BAL}_t)-P(\mathrm{A1}_t)\tag{7}
$$

The direct interaction is the difference between the same representation effect under L and J:

$$
I_{\mathrm{TRI}}=E_{\mathrm{TRI},\mathrm{L}}-E_{\mathrm{TRI},\mathrm{J}}\tag{8}
$$

$$
I_{\mathrm{BAL}}=E_{\mathrm{BAL},\mathrm{L}}-E_{\mathrm{BAL},\mathrm{J}}\tag{9}
$$

A positive interaction means that independent matching makes the representation change more beneficial or less harmful. It does not establish that the representation effect under L is itself positive. We therefore report the absolute effects together with the interactions. Conversely, a positive representation effect with an interaction interval spanning zero supports the usefulness of the representation under the observed conditions without clearly establishing dependence on matching.

The D comparison uses the same definitions with D replacing S. To compare their interactions, both are restricted to the same seeds and support budgets. For either construction label $q$ in TRI or BAL, the encoder comparison is

$$
\Delta I_q=I_{q,\mathrm{D}}-I_{q,\mathrm{S}},\quad q\in\{\mathrm{TRI},\mathrm{BAL}\}\tag{10}
$$

All differences are formed within matched conditions and within each resampling replicate before aggregation. We never infer an interaction by contrasting two separate significance decisions or by subtracting confidence-interval endpoints. These are established contrast estimators used to answer the representation question, not a proposed statistical method.

### 3.6 Anomaly Outputs and Computational Cost

The patch scores form the matrix $a_t$ on the common lattice, are bilinearly resized to the $H$ by $W$ output canvas, and are smoothed with a Gaussian of standard deviation four pixels; $u$ indexes an output pixel. The image score is the maximum map response:

$$
\boldsymbol{A}_t=\operatorname{Gauss}_{\sigma=4}(\operatorname{Resize}_{H\times W}(\boldsymbol{a}_t)),\quad s_{\mathrm{img},t}=\max_u A_{t,u}\tag{11}
$$

The controlled evaluation restores patch scores to the retained image canvas, with dimensions  $H$ by $W$; it is 448 by 448 for square images, 448 by 588 for BTAD category 03, and 630 pixels high by 224 pixels wide for KolektorSDD2. Ground truth follows the same resized and cropped image extent. This bookkeeping is distinct from cross-method evaluation in original-image coordinates, described in Section 4.1.3. Pixel metrics use continuous scores. For illustrative contours only, thresholding produces

$$
\boldsymbol{M}_{\mathrm{vis},t}(u)=\mathbf{1}[A_{t,u}\geq\tau_{\mathrm{vis}}]\tag{12}
$$

Here $\tau_{\mathrm{vis}}$ is a visualization rule, not a universal fixed operating threshold. The archived qualitative examples use min-max normalization followed by 256-bin Otsu thresholding. No test mask determines this threshold. Equation (12) defines a display operation; the evaluated model outputs remain the continuous anomaly map and image score. A deployment threshold would require separate calibration.

If a bank contains $N_c$ normal patches, a query contains $n$ patches, and the combined descriptor dimension is $d$, exhaustive matching requires order $nN_cd$ distance work and order $N_cd$ feature storage. Joint matching can use one weighted concatenation index, whereas independent matching requires the corresponding branch-wise searches. Implementations can have different overheads even when the arithmetic order is the same. Larger support budgets increase reference storage, and an actual additional encoder incurs feature-extraction cost; reusing a duplicate does not incur that encoder cost. Training-free describes the absence of target optimization, not zero preparation cost or negligible inference cost.

### 3.7 Model Configuration

Table 2 records the frozen feature paths and the shared processing choices. The B and S encoders use DINOv2 patch features [6]. C uses a CLIP ViT-L/14 visual backbone with AnomalyCLIP's diagonally prominent attention map path [23, 8]. Its 518-pixel input yields a 37 by 37 grid; the final returned patch tensor is retained after projection, excluding the class token. Although the inherited setup loads prompt-related checkpoint material, no text or prompt score is used in our visual-only inference.

Table 2. Frozen feature paths and shared model configuration.

| Component | Input and retained feature path | Descriptor / target training |
| --- | --- | --- |
| B | DINOv2 ViT-B/14; final patch features; short side 448 | 768 dimensions; frozen |
| S | DINOv2 ViT-S/14; final patch features; short side 448 | 384 dimensions; frozen |
| C | CLIP ViT-L/14 visual + DPAM; 518 × 518; retain layer 24 after projection | 768 dimensions; frozen |
| D | WideResNet50-2; ImageNet1K V1; layer2 + layer3 on B canvas | 512 + 1024 = 1536; frozen |
| E1 | Original DINO ViT-S/8; final patch features | 384 dimensions; frozen |
| E2 | ConvNeXt-Tiny; two retained stages | 576 dimensions; frozen |
| E3 | Swin-Tiny; two retained stages | 576 dimensions; frozen |
| Alignment | Common B grid; bilinear mapping; align_corners false | 32 × 32 for a 448 × 448 canvas |
| Normalization | Per-branch unit normalization; joint coefficients are square roots of distance weights | No learned scale or fusion parameter |
| Memory and scoring | All aligned support patches; exact nearest-neighbor matching | Fixed bank per category, seed and K |
| Output | Resize to retained H × W canvas; Gaussian standard deviation 4 pixels | Continuous map; maximum image score |
| Optimization | No target loss, optimizer, learning rate or training epochs | 0 target-trainable parameters |

C requests layers 6, 12, 18 and 24, uses DPAM_layer = 20 and retains the final patch tensor. No text scores enter the model. The fixed KolektorSDD2 canvas is 630 high × 224 wide; other inputs follow the B canvas. D is prespecified; E1–E3 are exploratory.

The common lattice follows the B canvas. Inputs are resized with preserved aspect ratio to a short side of 448 pixels and cropped from the top left to dimensions divisible by 14. The C grid is mapped to that retained image extent rather than blindly stretched to the uncropped source. On BTAD category 03, the resized extent is 448 by 597 pixels and the retained canvas is 448 by 588. The corrected BTAD analysis maps both predictions and masks through the corresponding coordinates; extensions using the historical canonical mask convention are identified separately. Geometric consistency does not imply identical receptive fields or learned semantic alignment between encoders.

The D branch was specified before its results were generated. It uses ImageNet-pretrained WideResNet50-2, bilinearly resamples layer2 and layer3 to the B lattice, concatenates their 512- and 1024-channel outputs, and normalizes the resulting 1536-dimensional descriptor. Its query-feature cache is stored in float16 and converted to float32 for normalization and scoring; this storage choice is recorded in the reproduction manifest. The B/S/C features and D features do not share a universal 768-dimensional output. Exploratory slots additionally use original DINO ViT-S/8 (E1), ConvNeXt-Tiny (E2), and Swin-Tiny (E3). They follow the same mapping and unit-normalization steps. KolektorSDD2 uses its prespecified 630 by 224 canvas for B, S and D; C retains its own input path before spatial mapping. All encoder parameters remain frozen, so target optimizer, learning rate, training epochs, and training-loss curves are not applicable.

## 4 Experimental Evaluations

### 4.1 Experimental Design

#### 4.1.1 Datasets and Reference Protocol

We evaluate the current representation-by-matching design on MPDD, BTAD, MVTec AD, VisA and KolektorSDD2 [2, 3, 1, 4, 33]. Table 3 distinguishes their roles and support scopes. MPDD informed development. BTAD and MVTec AD are frozen external validation datasets but had already been examined in the project. VisA is in-domain validation because the inherited AnomalyCLIP checkpoint was trained on VisA. Its visual-only inference does not erase this provenance. Only the KolektorSDD2 directional confirmation was specified before encoding that dataset's features.

Table 3. Dataset roles and support scopes of the current study.

| Dataset | Classes | Role | S conditions | D conditions |
| --- | --- | --- | --- | --- |
| MPDD | 6 | Development | 12: seeds 0–2 | 4: seeds 0–1; K = 1, 4 |
| BTAD | 3 | External frozen validation | 8: seeds 0–1 | 4: seeds 0–1; K = 1, 4 |
| MVTec AD | 15 | External frozen validation | 12: seeds 0–2 | Not evaluated |
| VisA | 12 | In-domain frozen validation | 12: seeds 0–2 | Not evaluated |
| KolektorSDD2 | 1 | Separate confirmation | 12: seeds 0–2 | 12: seeds 0–2; all budgets |

All S studies use K = 1, 2, 4 and 8. KSDD2 uses the same four budgets for D. Supports are nested within seed and shared across paired methods. Extra-encoder comparisons on MPDD/BTAD use the four D conditions; their wider twelve-condition runs are exploratory. VisA is in-domain for the inherited C checkpoint.

For each category and seed, verified normal training images form a fixed support sequence; smaller $K$ values are nested prefixes. The same supports and query images are used by every method in a paired comparison. Seeds 0, 1 and 2 crossed with $K$ equal to 1, 2, 4 and 8 yield twelve dataset-level support conditions; the primary BTAD analysis uses seeds 0 and 1 and therefore eight conditions. These are repeated evaluations on common test data, not independent datasets. KolektorSDD2 supplies 1004 test images, including 110 with nonempty defect masks and 894 without defects; only verified normal training images enter the support bank.

The original D extension and the matched five-encoder comparison use seeds 0 and 1 with $K$ equal to 1 and 4 on MPDD and BTAD. Additional E1–E3 results on twelve conditions are reported as exploratory scope checks. A separate eight-seed extension uses seeds 0 through 7 and all four budgets. Its BTAD category-03 masks follow the canonical convention, so its estimates are not substituted for the corrected-geometry primary estimates.

#### 4.1.2 Controlled Constructions and External Baselines

The primary matrix includes single-branch B, S and C and both matching rules for A1, DUP, TRI and BAL. Single-branch paths diagnose descriptor quality, while the eight combined configurations identify the two interaction contrasts. The D extension adds D-only scoring and its TRI/BAL variants. E1–E3 entered after the S and D results and are exploratory encoder substitutions. They are not independently proposed algorithms or prospectively selected replications.

AnomalyDINO and PatchCore provide native-method context [5, 16]. AnomalyDINO is evaluated with and without support rotation. PatchCore includes the 224-pixel input and 1024-dimensional projected-feature configuration as well as the earlier local 128-pixel and 256-dimensional configuration. Both are retained to reveal configuration sensitivity. Each method keeps its own preprocessing, features and search implementation, while support seeds and budgets are matched. This comparison assesses practical configurations and does not isolate the matching factor or constitute a comprehensive state-of-the-art benchmark.

#### 4.1.3 Metrics and Statistical Inference

Pixel average precision (AP) is the primary localization metric. Scores and labels are pooled over test images within each category, then category APs are averaged equally. Dataset-level estimates average the applicable support conditions equally. This differs from pooling all categories into a single AP or averaging per-image AP. Pixel AUROC is a secondary diagnostic. Performance tables use AP on the 0–1 scale; effects and interactions use AP percentage points, equal to 100 times an AP difference.

Three spatial evaluation conventions remain separate. The main bootstrap analysis samples pixels on a regular stride-eight grid of the retained output canvas. Full-pixel estimates use every output-canvas pixel; finer stride-four checks test sensitivity to the sampled grid. External-method comparisons instead map predictions into original-image coordinates and evaluate their common valid intersection. Geometry conventions, pixel strides and support scopes are stated with each table; scores from these settings are not interchangeable.

We use 1000 paired image-level bootstrap replicates. Images are sampled with replacement within each fixed category, without additional normal/abnormal stratification. Each sampled image contributes its evaluated pixels as a block. The same deterministic replicate stream, based on seed 20260913 together with dataset identity, category identity and replicate index, is shared across methods and support conditions. Contrasts are formed within each replicate after the required category and condition aggregation. Intervals are conditional on observed categories and support manifests; they do not estimate uncertainty over unseen datasets or arbitrary future support sets.

The primary four S interactions, four D interactions and four matched D-minus-S contrasts each have their own exploratory four-comparison family, reported with 98.75% percentile intervals. The extended four-dataset S table has eight cells and reports 99.375% intervals; these are approximate Bonferroni adjustments. Encoder-transfer comparisons retain a separate four-cell family per encoder, with no simultaneous guarantee over all exploratory analyses. With 1000 replicates, extreme percentile endpoints have limited precision.

KolektorSDD2 retains its specified conjunction criterion: all four S/D interactions must be positive and their individual 95% intervals must exclude zero. Those intervals are not described as simultaneous 95% coverage. A wider interval would be more conservative for an individual positive-effect claim, not a relaxation of the criterion. We preserve the specified decision rather than selecting a new interval level after observing results. The absence of zero from an interval addresses direction; it does not establish practical utility. Conversely, an interval spanning zero does not prove a true zero effect or statistical equivalence.

Observed condition-averaged point estimates and bootstrap means are labelled separately. Full-pixel estimates are resolution checks and have no bootstrap intervals in this draft. The eight-seed study describes support sensitivity separately rather than treating its between-seed variation as part of the primary conditional interval.

#### 4.1.4 Implementation and Reproducibility

The recorded machine has an NVIDIA GeForce RTX 3060 Laptop GPU with 6 GB VRAM, an Intel Core i9-12900H processor and 16 GB RAM. Encoders run in evaluation mode, with cached query features reused across controlled variants. Exact nearest-neighbor search implements Section 3, using FAISS where applicable [34]. Feature extraction, reference construction and score evaluation are distinct computational stages; cached-stage times cannot be interpreted as end-to-end deployment latency.

The primary BTAD tables use corrected category-03 coordinates. The four-dataset and eight-seed extensions retain their archived canonical-mask convention and are reported separately. Geometric audits verify the retained image extent and support nesting. Duplicate descriptors reuse the exact cached values. Reproduction uses support manifests, frozen branch specifications and paired bootstrap streams; no target loss is optimized and no test-mask feedback selects a normal reference.

Resource reporting is restricted to measurements whose stages and devices are identifiable. VisA's extension includes mixed CPU/GPU execution and is excluded from speed or GPU-memory rankings. Incomplete historical A1 timing and unavailable PatchCore process GPU-memory measurements are left unestimated. These limitations concern efficiency comparisons and are not filled with device-wide readings or inferred latencies.

### 4.2 Results and Analysis

#### 4.2.1 Controlled Performance and the Weight Confound

Table 4 reports the eight configurations needed to identify the primary S interactions. A1 reaches pixel AP 0.3729 under J and 0.3791 under L on MPDD; corrected BTAD yields 0.6408 and 0.6498. Independent matching improves the observed anchor average, but an anchor improvement alone does not show that an additional representation benefits from the same change.

Table 4. Primary controlled matrix with the S representation.

| Configuration | MPDD AP | MPDD SD | BTAD AP | BTAD SD |
| --- | --- | --- | --- | --- |
| A1 J | 0.3729 | 0.0424 | 0.6408 | 0.0134 |
| A1 L | 0.3791 | 0.0434 | 0.6498 | 0.0129 |
| DUP J | 0.3649 | 0.0438 | 0.6316 | 0.0136 |
| DUP L | 0.3681 | 0.0445 | 0.6379 | 0.0133 |
| TRI J | 0.3626 | 0.0433 | 0.6471 | 0.0108 |
| TRI L | 0.3736 | 0.0463 | 0.6529 | 0.0086 |
| BAL J | 0.3678 | 0.0409 | 0.6505 | 0.0113 |
| BAL L | 0.3799 | 0.0437 | 0.6583 | 0.0090 |

Pixel AP on the stride-eight canvas grid. SD is the sample standard deviation across the 12 MPDD or 8 BTAD fixed support conditions; it is not a confidence interval or variation across independent test datasets. BTAD uses corrected coordinates. The table contains the eight configurations required by the interaction; single-branch diagnostics are retained in the archive. Bold identifies the A1 anchor.

DUP lowers AP relative to A1 under both matching rules in both datasets. On MPDD, duplicating B changes AP by approximately −0.80 percentage points under J and −1.10 under L, despite introducing no new information. The effective B weight rises from one half to two thirds while C falls to one third. This provides a concrete reason to separate branch count from representation value.

The construction ordering also differs across datasets. MPDD TRI remains below A1 under either matching rule, even though TRI L improves over its DUP control. BAL L is close to A1 L. On BTAD, TRI and BAL exceed their respective controls and BAL L has the highest observed AP within this eight-configuration matrix. These are conditional results for fixed weights; they do not identify an optimal branch set or fusion weight.

#### 4.2.2 Representation Value and Matching Dependence

The absolute representation effects in Table 5 clarify what a positive interaction means. On MPDD, TRI minus DUP changes from −0.224 points under J to +0.548 under L. The L effect's 95% interval is [−0.092, +1.160], so its absolute benefit remains uncertain. BAL minus A1 similarly changes from −0.510 to +0.085 points. Removing the shared-reference constraint makes both changes more favorable without establishing that adding S improves the absolute localization performance.

Table 5. Absolute effects of replacing the representation with S.

| Dataset | Contrast / rule | Observed effect | 95% interval |
| --- | --- | --- | --- |
| MPDD | $E_{TRI,J}$ | −0.224 | [−0.968, +0.478] |
| MPDD | $E_{TRI,L}$ | +0.548 | [−0.092, +1.160] |
| MPDD | $E_{BAL,J}$ | −0.510 | [−1.135, +0.123] |
| MPDD | $E_{BAL,L}$ | +0.085 | [−0.434, +0.708] |
| BTAD | $E_{TRI,J}$ | +1.553 | [+0.637, +2.465] |
| BTAD | $E_{TRI,L}$ | +1.503 | [+0.585, +2.495] |
| BTAD | $E_{BAL,J}$ | +0.974 | [+0.177, +1.803] |
| BTAD | $E_{BAL,L}$ | +0.854 | [+0.057, +1.753] |

AP percentage points on stride-eight pixels; MPDD uses twelve support conditions and BTAD eight with corrected geometry. Individual 95% intervals are exploratory. Positive interaction does not require either absolute effect to be positive.

BTAD separates these questions in the opposite way. TRI has positive representation effects of +1.553 and +1.503 points under J and L, respectively; both exploratory 95% intervals exclude zero. BAL also has positive effects under both rules. S is useful relative to the specified controls, but its benefit is similar under the two matching rules.

Table 6 estimates that difference directly. MPDD has S interactions of +0.772 and +0.595 points, with 98.75% intervals [+0.346, +1.211] and [+0.189, +1.030]. Corrected BTAD has interactions of −0.050 and −0.119 points, and both intervals span zero. Thus, the primary data support positive matching dependence on MPDD while leaving its direction unresolved on BTAD. A small, inconclusive estimate is not proof that the interaction is exactly zero.

Table 6. Direct interactions for S and the prespecified D extension.

| Dataset | Encoder | Contrast | Observed interaction | 98.75% interval |
| --- | --- | --- | --- | --- |
| MPDD | S | $I_{TRI}$ | +0.772 | [+0.346, +1.211] |
| MPDD | S | $I_{BAL}$ | +0.595 | [+0.189, +1.030] |
| MPDD | D | $I_{TRI}$ | +0.974 | [+0.514, +1.689] |
| MPDD | D | $I_{BAL}$ | +0.628 | [+0.162, +1.394] |
| BTAD | S | $I_{TRI}$ | −0.050 | [−0.235, +0.244] |
| BTAD | S | $I_{BAL}$ | −0.119 | [−0.306, +0.167] |
| BTAD | D | $I_{TRI}$ | +0.622 | [+0.298, +1.003] |
| BTAD | D | $I_{BAL}$ | +0.501 | [+0.188, +0.995] |

AP percentage points, stride eight. S uses twelve MPDD and eight corrected-BTAD conditions; D uses four conditions per dataset. Four contrasts per encoder form separate exploratory adjustment families. Between-encoder comparisons must use identical support scopes; these rows alone do not provide that comparison.

The prespecified D extension yields positive interactions on both primary datasets: +0.974 and +0.628 points on MPDD, and +0.622 and +0.501 on BTAD. All four adjusted intervals exclude zero. On the four-condition full-pixel scope, TRI D L reaches AP 0.4107 on MPDD versus 0.3554 for DUP L, and 0.6591 on BTAD versus 0.6335. Those larger differences are absolute representation gains, not the interaction itself.

A direct D-minus-S comparison restricts S to the same four conditions. The observed interaction differences on BTAD are +0.623 and +0.585 points, with adjusted intervals [+0.255, +0.945] and [+0.204, +1.060]. MPDD differences are +0.207 and +0.081 points with intervals spanning zero. This supports an encoder-specific difference on BTAD while leaving the relative interactions unresolved on MPDD. It does not follow from comparing two separate significance decisions.

#### 4.2.3 Validation across Additional Datasets

Table 7 extends the S contrasts to MVTec AD and VisA and reports an eight-cell exploratory adjustment across the four datasets. Both interactions remain positive with intervals above zero on MPDD, MVTec AD and VisA. MVTec AD's stride-eight bootstrap means are +0.432 and +0.402 points; VisA's are +0.927 and +0.810. The full-pixel observed points retain these directions. BTAD's canonical-mask estimates remain small with intervals spanning zero.

Table 7. Extended S interactions across four datasets.

| Dataset | Contrast | Bootstrap mean | 99.375% interval | Full-pixel point |
| --- | --- | --- | --- | --- |
| MPDD | $I_{TRI}$ | +0.762 | [+0.324, +1.250] | +0.787 |
| MPDD | $I_{BAL}$ | +0.615 | [+0.152, +1.081] | +0.601 |
| BTAD | $I_{TRI}$ | −0.020 | [−0.245, +0.261] | −0.045 |
| BTAD | $I_{BAL}$ | −0.087 | [−0.313, +0.201] | −0.115 |
| MVTec AD | $I_{TRI}$ | +0.432 | [+0.309, +0.570] | +0.423 |
| MVTec AD | $I_{BAL}$ | +0.402 | [+0.287, +0.534] | +0.386 |
| VISA | $I_{TRI}$ | +0.927 | [+0.738, +1.114] | +0.896 |
| VISA | $I_{BAL}$ | +0.810 | [+0.611, +1.018] | +0.760 |

AP percentage points. Bootstrap means and intervals use stride eight and an eight-cell exploratory family; the final column uses all pixels and has no interval. Twelve support conditions per dataset except BTAD (eight). BTAD here uses canonical masks, not the corrected-geometry primary table. These estimates are labelled as bootstrap means and must not be substituted for observed stride-eight point estimates.

The dataset roles limit the interpretation. MVTec AD adds external frozen validation, whereas VisA is in-domain for the inherited C checkpoint. The larger VisA interaction cannot be attributed causally to that provenance, but it cannot be presented as unseen-domain confirmation either. The BTAD canonical-mask row and corrected-geometry primary row differ slightly and are not substituted for each other. Both analyses leave the interaction direction uncertain.

The extended table deliberately distinguishes its bootstrap means from its full-pixel observed estimates. Differences between those columns reflect both the estimator summary and pixel sampling, so they are not a pure resolution-effect estimate. The archived paired full-pixel and stride-eight analyses provide the appropriate within-scope sensitivity check. Across the primary aggregate S and D results, their directions agree; full-pixel statistical significance is not claimed.

#### 4.2.4 Separately Specified Confirmation on KolektorSDD2

KolektorSDD2 tests a directional expectation recorded before its features were encoded: both TRI and BAL interactions should be positive for S and D, and all four individual 95% intervals should exclude zero. The specification was frozen on 18 September 2026 at 11:59 UTC. Later logged clarifications specify the D input canvas and retain the original 95% decision rule; they do not convert this local record into an external preregistration.

Table 8 reports the twelve-condition result for its single category. S produces observed interactions of +0.539 and +0.343 points; D produces +0.499 and +0.367. All four individual 95% intervals exclude zero, meeting the specified conjunction criterion. The confirmation is reported separately from the eight-cell validation table and its adjustment family.

Table 8. Separately specified confirmation on KolektorSDD2.

| Encoder | Contrast | Observed interaction | 95% interval |
| --- | --- | --- | --- |
| S | $I_{TRI}$ | +0.539 | [+0.299, +0.823] |
| S | $I_{BAL}$ | +0.343 | [+0.129, +0.579] |
| D | $I_{TRI}$ | +0.499 | [+0.212, +0.851] |
| D | $I_{BAL}$ | +0.367 | [+0.128, +0.653] |

AP percentage points, stride eight, 1000 paired bootstrap replicates, twelve support conditions and one category. The decision requires all four positive effects to have individual 95% intervals excluding zero. These are not simultaneous 95% intervals. The specified conjunction criterion is retained.

This result extends positive interactions beyond the original development dataset under a prospectively stated expectation. It does not prove that earlier analysis was free of selection effects, establish simultaneous 95% coverage of four intervals, or guarantee transfer to another manufacturing process. A single-category confirmation broadens the evidence while leaving substantial variation in products, defect types and support sets untested.

#### 4.2.5 Encoder Transfer under Matched Conditions

The exploratory E1–E3 substitutions test whether the finding is specific to the two main extra encoders. Table 9 uses the same seeds and budgets for all five slots and reports observed points rather than bootstrap means. Original DINO (E1) and Swin-Tiny (E3) yield positive TRI interactions with adjusted intervals above zero on MPDD; ConvNeXt-Tiny (E2) has a small negative point and an interval spanning zero. Only E3 also has a clearly positive BAL interaction on MPDD under this scope. On BTAD, all three extra encoders have positive TRI interactions with intervals above zero; E2 and E3 also have positive BAL interactions.

Table 9. Encoder substitution under the same four support conditions.

| Encoder | MPDD TRI | MPDD BAL | BTAD TRI | BTAD BAL |
| --- | --- | --- | --- | --- |
| S | +0.767 [+0.193, +1.160] | +0.547 [+0.078, +0.962] | −0.001 [−0.189, +0.293] | −0.084 [−0.273, +0.208] |
| D | +0.974 [+0.514, +1.689] | +0.628 [+0.162, +1.394] | +0.622 [+0.298, +1.003] | +0.501 [+0.188, +0.995] |
| E1 | +0.819 [+0.246, +1.362] | +0.486 [−0.136, +1.091] | +0.568 [+0.172, +1.056] | +0.210 [−0.158, +0.649] |
| E2 | −0.019 [−0.358, +0.298] | +0.039 [−0.315, +0.588] | +0.269 [+0.152, +0.494] | +0.398 [+0.158, +0.872] |
| E3 | +1.287 [+0.644, +2.056] | +0.796 [+0.055, +1.425] | +0.478 [+0.217, +0.906] | +0.448 [+0.171, +0.955] |

Each cell gives the observed interaction in AP percentage points followed by its 98.75% interval. All rows use seeds 0 and 1 with K = 1 and 4. D was prespecified; E1–E3 are post hoc. The four cells for each encoder have a separate adjustment family; no joint guarantee covers all encoder substitutions.

Paired differences against S provide a stronger comparison than ranking these points. On MPDD, the E2-minus-S TRI difference has an adjusted interval below zero, supporting a smaller interaction for this substitution. On BTAD, D, E1 and E3 exceed S for TRI, whereas D, E2 and E3 exceed S for BAL under the matched four-condition analysis. The remaining paired comparisons are inconclusive. These findings establish conditional differences for the tested encoders, not an ordering of CNNs versus transformers in general.

The wider twelve-condition E1–E3 runs change some interval decisions: E1's MPDD BAL interval excludes zero, while E3's BTAD BAL interval no longer does. These wider estimates must not be compared directly with four-condition S/D values as if only the encoder changed. Accordingly, Table 9 retains the matched scope, while wider runs serve as a sensitivity analysis. The encoder substitutions were selected after observing the main study and remain exploratory.

#### 4.2.6 Support Variation and Spatial Evaluation

Table 10 summarizes the eight-seed extension. MPDD has positive point estimates under every seed for both contrasts, with mean interactions +0.679 and +0.548 points. Seven of eight individual TRI intervals and six of eight BAL intervals exclude zero at 95%. BTAD changes sign across seeds in both contrasts, and its mean points are much smaller. Counts of interval exclusions are descriptive and are not eight independent replications, because every seed uses the same test images.

Table 10. Descriptive support-set sensitivity across eight random seeds.

| Series | Mean point | SD over seeds | All points positive | 95% exclusions | Uncertainty ratio |
| --- | --- | --- | --- | --- | --- |
| MPDD $I_{TRI}$ | +0.679 | 0.221 | Yes | 7 of 8 | 0.48 |
| MPDD $I_{BAL}$ | +0.548 | 0.159 | Yes | 6 of 8 | 0.37 |
| BTAD $I_{TRI}$ | +0.125 | 0.136 | No | 3 of 8 | 0.68 |
| BTAD $I_{BAL}$ | +0.036 | 0.129 | No | 0 of 8 | 0.65 |

AP percentage points except the final ratio. Eight seeds, K = 1, 2, 4 and 8; seeds 0–2 retain their own query features and seeds 3–7 share one cached query block. BTAD uses canonical masks. The final column uses the paired-replicate estimate of between-seed SD divided by the median test-bootstrap half-width, not simply the displayed SD divided by that width. This is a descriptive sensitivity ratio, not a variance decomposition or a confidence interval.

Support variation is not negligible beside conditional test-image uncertainty. The paired-replicate between-seed SD divided by the median test-bootstrap half-width is 0.48 for MPDD TRI and 0.68 for BTAD TRI. These ratios compare two descriptive scales, not independent variance components. The seed study also retains canonical BTAD masks, whereas the primary corrected-geometry analysis uses a different revision. The distinction prevents geometric changes from being attributed to support sampling.

Larger nested banks cannot increase an exact nearest-neighbor raw distance when descriptors remain fixed. AP and its interaction contrast do not inherit that monotonicity: they depend on the relative ordering of normal and anomalous pixels across several configurations. Per-budget and per-category analyses therefore describe observed heterogeneity rather than a monotone design law. Finer-grid BTAD analyses and corrected-coordinate checks retain the conclusion that no aggregate S interaction direction is established. Full-pixel points add a resolution check but do not replace missing full-pixel bootstrap intervals.

#### 4.2.7 Correspondence Sensitivity and Its Statistical Scope

The common bank aligns branch rows by their support-image and canvas coordinates. This does not guarantee semantic correspondence of receptive fields. A separate sensitivity harness evaluates the canvas convention, an orthogonal Procrustes transformation, a spatial permutation, and support-based optimal transport. The soft transport rule replaces a C descriptor by a weighted mixture of reference positions; an exact-assignment limit instead changes the correspondence without averaging descriptors.

Table 11. Observed interactions under correspondence transformations.

| Variant | MPDD TRI | MPDD BAL | BTAD TRI | BTAD BAL |
| --- | --- | --- | --- | --- |
| Canvas correspondence | +0.767 | +0.547 | +0.001 | −0.080 |
| Orthogonal Procrustes | +0.767 | +0.547 | +0.001 | −0.080 |
| Spatial permutation | +0.799 | +0.813 | +0.234 | +0.217 |
| Soft transport (0.1 IQR) | +0.591 | +0.570 | +0.115 | +0.103 |
| Exact assignment | +0.834 | +0.910 | +0.220 | +0.148 |
| Soft transport (0.05 IQR) | +0.580 | +0.624 | +0.162 | +0.156 |
| Soft transport (0.5 IQR) | +0.725 | +0.751 | +0.061 | +0.025 |

AP percentage points; means over four support conditions (seeds 0, 1; K = 1, 4) in a separate sensitivity harness. IQR denotes the interquartile range of support costs. No confidence intervals are reported: the archived interval fields are percentiles of four condition points, not image-bootstrap confidence intervals. These values must not replace primary-pipeline estimates.

All reported MPDD condition-averaged interaction points are positive, including soft transport and exact assignment. The pattern is descriptive: the harness's columns labelled as confidence intervals are computed from the four condition-level interaction values, rather than from the available image-bootstrap replicate series. They therefore do not establish confidence coverage or multiplicity-adjusted significance. Table 11 reports the observed means only, and no zero-exclusion conclusion is drawn from those archived ranges.

This distinction changes the interpretation of correspondence robustness. Positive aggregate points under several transformations suggest that the observed sign is not confined to the canvas convention in these four conditions. They do not prove invariance of the population interaction or validate the correspondence itself. An orthogonal transformation applied consistently to query and reference descriptors preserves within-branch distances; its unchanged result is principally a numerical consistency check. Soft transport additionally changes the representation by averaging descriptors, so its effect cannot be attributed solely to matching different locations.

The latest BTAD sensitivity runs cover the same principal variants and the transport regularizer grid, rather than only the canvas and soft-transport pair. Their observed means are reported alongside MPDD. Neither condition-level ranges nor point differences establish an inferential interaction direction on BTAD. Proper paired image-bootstrap analysis of the correspondence variants remains necessary before making statistical robustness claims.

#### 4.2.8 External Method Context and Resource Costs

Table 12 updates the native-method comparison using the completed six-method common-region table on all four validation/development datasets. It contains 864 method-category-condition rows, with the same four support conditions for each configuration. A1 L has the highest observed AP on MPDD, BTAD and VisA among these configurations. On MVTec AD, AnomalyDINO without rotation reaches 0.5643 and its rotation variant reaches 0.5637, both above A1 L at 0.5570. The results therefore do not support a blanket claim that A1 leads all datasets.

Table 12. Native-method context on a common valid region for all six methods.

| Configuration | MPDD | BTAD | MVTec AD | VisA |
| --- | --- | --- | --- | --- |
| A1 L | 0.3698 | 0.6474 | 0.5570 | 0.3763 |
| A1 J | 0.3611 | 0.6380 | 0.5530 | 0.3713 |
| AnomalyDINO + rotation | 0.3214 | 0.5840 | 0.5637 | 0.3469 |
| AnomalyDINO | 0.3130 | 0.5614 | 0.5643 | 0.3291 |
| PatchCore 224 / 1024 | 0.2275 | 0.3760 | 0.4955 | 0.3111 |
| PatchCore 128 / 256 | 0.1649 | 0.2886 | 0.3966 | 0.2554 |

Category-macro pixel AP, averaged over seeds 0 and 1 and K = 1 and 4. All 864 method-category-condition rows are included. Average retained coverage is 76.56%, 70.49%, 76.56% and 59.07%, respectively. Methods differ in backbone, resolution and augmentation. Bold identifies A1, not a statistical superiority claim.

Rotation improves AnomalyDINO on MPDD, BTAD and VisA but slightly reduces its MVTec AD average. The 224-pixel PatchCore configuration improves over the earlier 128-pixel version on every dataset. These differences reinforce the importance of method configuration, rather than treating a lower-resolution baseline as a definitive representative of the published algorithm.

The common valid region covers 76.56% of the MPDD canvas, 70.49% on average for BTAD, 76.56% for MVTec AD and 59.07% for VisA. Restricting evaluation avoids extrapolating predictions into unsupported borders but also removes those borders from the task. Backbones, augmentation and resolution still differ. Thus, the comparison supplies bounded practical context, not a full-image benchmark ranking or an isolated test of matching.

Table 13 retains native-stage timing for MPDD and BTAD where the recorded stages are interpretable. Reference rotation increases AnomalyDINO processing cost. The measurements do not include every feature-extraction stage, and PatchCore's combined processing stage cannot be separated retrospectively. A1 lacks a comparable complete historical timing record and PatchCore lacks a process GPU peak. VisA's mixed-device extension is excluded from a speed ranking.

Table 13. Recorded native-method runtime stages and process GPU memory.

| Dataset | Configuration | Processing s | Evaluation s | GPU peak MB |
| --- | --- | --- | --- | --- |
| MPDD | AnomalyDINO no rotation | 44.47 | 8.38 | 111.6–112.5 |
| MPDD | AnomalyDINO rotation | 82.74 | 8.22 | 111.6–112.5 |
| MPDD | PatchCore 224 | 99.75 | 23.40 | Unavailable |
| BTAD | AnomalyDINO no rotation | 53.19 | 16.39 | 118.8 |
| BTAD | AnomalyDINO rotation | 135.38 | 16.89 | 118.8 |
| BTAD | PatchCore 224 | 115.45 | 40.85 | Unavailable |

Mean seconds per complete dataset condition over seeds 0 and 1 and K = 1 and 4; MPDD has 458 queries and BTAD 741. Processing is bank plus retrieval for AnomalyDINO and the combined native stage for PatchCore. GPU cells report the range of process peaks across conditions; each dataset name is printed once for its group. Cached feature extraction and other unrecorded stages are not added; these are not end-to-end per-image latencies. A1 has no comparable complete historical timing.

Larger banks and genuine additional encoders require more feature storage and computation; exact duplication does not require an additional forward pass. These structural costs follow from the pipeline, while a fair latency–memory–accuracy trade-off still requires synchronized end-to-end measurements under common deployment conditions. No unrecorded A1 latency or PatchCore memory value is inferred from the existing measurements.

#### 4.2.9 Interpretation and Limitations

The main finding concerns the source of a fusion gain. A duplicate tests whether changing effective weights is consequential. A fixed-slot replacement tests whether a new descriptor adds value. Crossing that replacement with normal-reference selection tests whether the value depends on sharing a reference. MPDD and BTAD demonstrate that absolute representation gains and positive matching interactions need not occur together.

The inference remains conditional. Most datasets and the primary interaction question followed earlier project exploration; only the separately specified KolektorSDD2 test supplies prospective directional confirmation. VisA retains source-domain exposure through C. The bootstrap holds categories and support manifests fixed, whereas the support-seed extension describes another uncertainty source. Canonical and corrected BTAD geometry series answer closely related but distinct numerical questions. Extreme adjusted percentile endpoints are estimated from only 1000 replicates, and complete full-pixel confidence intervals are unavailable.

Encoder substitutions and the single-condition shared-operation ablations are exploratory. They do not validate normalization, alignment or smoothing as independent novel modules. Correspondence results currently provide descriptive sensitivity only because their stored interval columns summarize condition variation. The observed transport behavior has no established mechanism-level explanation. External baselines cover a restricted common region and two method families rather than a comprehensive recent-method benchmark, and end-to-end efficiency remains incompletely measured.

Finally, the output is continuous anomaly evidence. A displayed thresholded contour may omit weak parts of a defect or include unrelated high-response pixels. Neither AP nor a qualitative outline establishes calibrated binary segmentation at a fixed operating point. A practical detector would require a separately specified threshold-selection protocol and evaluation of its false positives and missed defects.


## 5 Conclusion

We investigated how normal-reference matching changes the value of additional frozen visual representations in few-shot industrial anomaly localization. Exact duplication and complementary fixed-weight replacements separate representation changes from simple reweighting. The paired interaction distinguishes an encoder's absolute usefulness from the extent to which that usefulness depends on sharing a normal reference.

The DINOv2-S interaction is positive on MPDD, MVTec AD and VisA, while BTAD does not establish a direction. The prespecified WideResNet50-2 extension is positive on both primary datasets, and the separate KolektorSDD2 confirmation meets all four specified directional criteria. Exploratory encoder and support-seed studies reveal conditional variation rather than a universal ranking. Positive MPDD mean interactions persist under the examined correspondence variants; their condition-level ranges do not provide valid image-bootstrap confidence intervals.

These results support treating representation composition and reference selection as interacting design choices. They do not establish that more encoders or independent matching are universally preferable, nor do they validate a calibrated binary defect detector. Dataset provenance, finite support conditions, geometry-dependent evaluation and incomplete deployment costs limit generalization. Future work should test prospectively specified encoder substitutions and calibrated operating points on additional production data, while preserving the controls that distinguish representation value from matching dependence.

## Data and Code Availability

MPDD, BTAD, MVTec AD, VisA and KolektorSDD2 are distributed by their respective providers [2, 3, 1, 4, 33]. The local study archive retains support manifests, feature specifications, geometry revisions, prediction caches, per-condition metrics, bootstrap outputs and analysis scripts. A permanent public archive for the complete current study has not yet been established.

## References

[1] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, 'MVTec AD - A comprehensive real-world dataset for unsupervised anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2019, pp. 9592-9600. https://doi.org/10.1109/cvpr.2019.00982

[2] S. Jezek, M. Jonak, R. Burget, P. Dvorak, and M. Skotak, 'Deep learning-based defect detection of metal parts: Evaluating current methods in complex conditions,' in Proc. 13th Int. Congr. Ultra Modern Telecommun. Control Syst. Workshops, 2021, pp. 66-71. https://doi.org/10.1109/icumt54235.2021.9631567

[3] P. Mishra, R. Verk, D. Fornasier, C. Piciarelli, and G. L. Foresti, 'VT-ADL: A vision transformer network for image anomaly detection and localization,' in Proc. IEEE 30th Int. Symp. Ind. Electron., 2021, pp. 1-6. https://doi.org/10.1109/isie45552.2021.9576231

[4] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, 'SPot-the-Difference self-supervised pre-training for anomaly detection and segmentation,' in Proc. Eur. Conf. Comput. Vis. (ECCV), 2022, pp. 392-408. https://doi.org/10.1007/978-3-031-20056-4_23

[5] S. Damm, M. Laszkiewicz, J. Lederer, and A. Fischer, 'AnomalyDINO: Boosting patch-based few-shot anomaly detection with DINOv2,' in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV), 2025, pp. 1319-1329. https://openaccess.thecvf.com/content/WACV2025/html/Damm_AnomalyDINO_Boosting_Patch-Based_Few-Shot_Anomaly_Detection_with_DINOv2_WACV_2025_paper.html

[6] M. Oquab et al., 'DINOv2: Learning robust visual features without supervision,' Trans. Mach. Learn. Res., 2024. https://openreview.net/forum?id=a68SUt6zFt

[7] X. Guo, Z. Chen, C. D. Castillo, H. Wang, and X. Liu, 'Sea-CLIP: Mining semantic-aware representations for few-shot anomaly detection with CLIP,' in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis. (WACV), 2026, pp. 3689-3699. https://openaccess.thecvf.com/content/WACV2026/html/Guo_Sea-CLIP_Mining_Semantic-Aware_Representations_for_Few-Shot_Anomaly_Detection_with_CLIP_WACV_2026_paper.html

[8] Q. Zhou, G. Pang, Y. Tian, S. He, and J. Chen, 'AnomalyCLIP: Object-agnostic prompt learning for zero-shot anomaly detection,' in Proc. Int. Conf. Learn. Represent. (ICLR), 2024. https://proceedings.iclr.cc/paper_files/paper/2024/hash/d7b50b8ac2c781a12f26155f48310d8d-Abstract-Conference.html

[9] K. Long, G. Xie, L. Ma, J. Liu, and Z. Lu, 'Revisiting Multimodal Fusion for 3D Anomaly Detection from an Architectural Perspective,' Proc. AAAI Conf. Artif. Intell., vol. 39, no. 12, pp. 12273–12281, 2025. https://ojs.aaai.org/index.php/AAAI/article/view/33337

[10] Y. Xu, H. Zhang, Y. Ma, Y. Zhu, and K. M. Ting, 'SCoNE: Spherical Consistent Neighborhoods Ensemble for Effective and Efficient Multi-View Anomaly Detection,' Proc. AAAI Conf. Artif. Intell., vol. 40, no. 19, pp. 16083–16090, 2026. https://ojs.aaai.org/index.php/AAAI/article/view/38643

[11] X.-R. Sheng, D.-C. Zhan, S. Lu, and Y. Jiang, 'Multi-View Anomaly Detection: Neighborhood in Locality Matters,' Proc. AAAI Conf. Artif. Intell., vol. 33, no. 1, pp. 4894–4901, 2019. https://ojs.aaai.org/index.php/AAAI/article/view/4418

[12] L. Cheng, Y. Wang, and X. Liu, 'Neighborhood Consensus Networks for Unsupervised Multi-view Outlier Detection,' Proc. AAAI Conf. Artif. Intell., vol. 35, no. 8, pp. 7099–7106, 2021. https://ojs.aaai.org/index.php/AAAI/article/view/16873

[13] M. Yang, J. Liu, Z. Yang, and Z. Wu, 'SLSG: Industrial image anomaly detection with improved feature embeddings and one-class classification,' Pattern Recognit., vol. 156, Art. no. 110862, 2024. https://doi.org/10.1016/j.patcog.2024.110862

[14] X. Zhang, M. Xu, and X. Zhou, 'RealNet: A feature selection network with realistic synthetic anomaly for anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2024, pp. 16699-16708. https://doi.org/10.1109/cvpr52733.2024.01580

[15] T. Defard, A. Setkov, A. Loesch, and R. Audigier, 'PaDiM: A patch distribution modeling framework for anomaly detection and localization,' in Pattern Recognition. ICPR International Workshops and Challenges, 2021, pp. 475-489. https://doi.org/10.1007/978-3-030-68799-1_35

[16] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler, 'Towards total recall in industrial anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2022, pp. 14318-14328. https://doi.org/10.1109/cvpr52688.2022.01392

[17] Z. Hu, X. Zeng, Y. Li, Z. Yin, E. Meng, L. Zhu, and X. Kong, 'Few-shot anomaly detection with adaptive feature transformation and descriptor construction,' Chin. J. Aeronaut., vol. 38, no. 3, Art. no. 103098, 2025. https://doi.org/10.1016/j.cja.2024.06.007

[18] S. Wei, X. Wei, Z. Ma, S. Dong, S. Zhang, and Y. Gong, 'Few-shot online anomaly detection and segmentation,' Knowl.-Based Syst., vol. 300, Art. no. 112168, 2024. https://doi.org/10.1016/j.knosys.2024.112168

[19] J. Zhou, W. Wong, and F. Liao, 'One-shot unsupervised industrial anomaly detection: Enhanced performance under extreme data scarcity,' Pattern Recognit., vol. 173, Art. no. 112759, 2026. https://doi.org/10.1016/j.patcog.2025.112759

[20] Y. Li, L. Tian, Y. Dai, W. Chen, L. Bao, and X. Liu, 'FastRef: Fast prototype refinement for few-shot industrial anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2026, pp. 43040-43049. https://openaccess.thecvf.com/content/CVPR2026/html/Li_FastRef_Fast_Prototype_Refinement_for_Few-shot_Industrial_Anomaly_Detection_CVPR_2026_paper.html

[21] C. Lendering, E. Akdag, and E. Bondarev, 'SubspaceAD: Training-free few-shot anomaly detection via subspace modeling,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2026, pp. 28557-28566. https://openaccess.thecvf.com/content/CVPR2026/html/Lendering_SubspaceAD_Training-Free_Few-Shot_Anomaly_Detection_via_Subspace_Modeling_CVPR_2026_paper.html

[22] L. Jiang, Y. Huang, Z. Xu, Y. Xu, H.-S. Wong, and S. Wu, 'Defect cue-preserved structural feature refinement for few-shot anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2026, pp. 35607-35616. https://openaccess.thecvf.com/content/CVPR2026/html/Jiang_Defect_Cue-Preserved_Structural_Feature_Refinement_for_Few-Shot_Anomaly_Detection_CVPR_2026_paper.html

[23] A. Radford et al., 'Learning transferable visual models from natural language supervision,' in Proc. 38th Int. Conf. Mach. Learn., vol. 139, 2021, pp. 8748-8763. https://proceedings.mlr.press/v139/radford21a.html

[24] J. Jeong, Y. Zou, T. Kim, D. Zhang, A. Ravichandran, and O. Dabeer, 'WinCLIP: Zero-/few-shot anomaly classification and segmentation,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2023, pp. 19606-19616. https://doi.org/10.1109/cvpr52729.2023.01878

[25] X. Li, Z. Zhang, X. Tan, C. Chen, Y. Qu, Y. Xie, and L. Ma, 'PromptAD: Learning prompts with only normal samples for few-shot anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2024, pp. 16838-16848. https://openaccess.thecvf.com/content/CVPR2024/html/Li_PromptAD_Learning_Prompts_with_only_Normal_Samples_for_Few-Shot_Anomaly_CVPR_2024_paper.html

[26] J. Zhu and G. Pang, 'Toward generalist anomaly detection via in-context residual learning with few-shot sample prompts,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2024, pp. 17826-17836. https://doi.org/10.1109/cvpr52733.2024.01688

[27] W. Ma et al., 'AA-CLIP: Enhancing zero-shot anomaly detection via anomaly-aware CLIP,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2025, pp. 4744-4754. https://doi.org/10.1109/cvpr52734.2025.00447

[28] J. Zhu, Y.-S. Ong, C. Shen, and G. Pang, 'Fine-grained abnormality prompt learning for zero-shot anomaly detection,' in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), 2025, pp. 22241-22251. https://doi.org/10.1109/iccv51701.2025.02065

[29] Z. Gu, B. Zhu, G. Zhu, Y. Chen, M. Tang, and J. Wang, 'UniVAD: A training-free unified model for few-shot visual anomaly detection,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2025, pp. 15194-15203. https://openaccess.thecvf.com/content/CVPR2025/html/Gu_UniVAD_A_Training-free_Unified_Model_for_Few-shot_Visual_Anomaly_Detection_CVPR_2025_paper.html

[30] Y. Wang, J. Peng, J. Zhang, R. Yi, Y. Wang, and C. Wang, 'Multimodal Industrial Anomaly Detection via Hybrid Fusion,' in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2023, pp. 8032–8041. https://openaccess.thecvf.com/content/CVPR2023/html/Wang_Multimodal_Industrial_Anomaly_Detection_via_Hybrid_Fusion_CVPR_2023_paper.html

[31] Y. Lin et al., 'Commonality in Few: Few-Shot Multimodal Anomaly Detection via Hypergraph-Enhanced Memory,' Proc. AAAI Conf. Artif. Intell., vol. 40, no. 9, pp. 7015–7023, 2026. https://ojs.aaai.org/index.php/AAAI/article/view/37636

[32] X. Chen, X. Wang, Y. Wang, C. Han, and L. Duan, 'Learning Enhanced Representations via Contrasting for Multi-view Outlier Detection,' in Database Systems for Advanced Applications (DASFAA), 2023, pp. 110–120. https://link.springer.com/chapter/10.1007/978-3-031-30678-5_9

[33] J. Božič, D. Tabernik, and D. Skočaj, 'Mixed supervision for surface-defect detection: from weakly to fully supervised learning,' Comput. Ind., vol. 129, Art. no. 103459, 2021. https://doi.org/10.1016/j.compind.2021.103459

[34] J. Johnson, M. Douze, and H. Jegou, 'Billion-scale similarity search with GPUs,' IEEE Trans. Big Data, vol. 7, no. 3, pp. 535-547, 2021. https://doi.org/10.1109/tbdata.2019.2921572
