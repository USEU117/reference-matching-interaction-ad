# Disentangling Representation Effects and Normal Reference Matching in Few-Shot Industrial Anomaly Localization

[[AUTHORS]]

[[AFFILIATIONS]]

Corresponding author: [[CORRESPONDING_AUTHOR]]

## Abstract

Combining pretrained visual encoders can improve few-shot industrial anomaly localization, but an apparent fusion gain may reflect changed weights, additional information, or altered normal-reference selection. We introduce a controlled decomposition that distinguishes these effects using frozen encoders and identical normal supports. An exact duplicate control isolates reweighting; complementary representation replacements measure the value of additional descriptors at fixed slot or branch-group weights. Crossing these constructions with joint and independent reference matching yields a paired interaction that separates absolute representation effects from their dependence on matching. For DINOv2-S, the two primary interactions on the Metal Parts Defect Detection (MPDD) dataset are +0.772 and +0.595 pixel average-precision percentage points, whereas their directions remain unresolved on the BeanTech Anomaly Detection (BTAD) dataset. Further validation supports positive interactions on MVTec AD and VisA, with VisA treated as in-domain. A separately specified KolektorSDD2 confirmation meets all four directional criteria for DINOv2-S and WideResNet50-2. Encoder and support-set analyses reveal meaningful variation across conditions. The resulting evidence shows why representation composition and reference selection should be assessed together and provides a practical way to distinguish additional-feature value from reweighting and matching effects. Code and reproduction materials are available at https://github.com/USEU117/reference-matching-interaction-ad.

Keywords: few-shot anomaly localization; frozen visual encoders; normal reference matching; fixed feature fusion; representation interaction.

## 1 Introduction

Industrial visual inspection must locate defects whose appearance is difficult to enumerate before deployment. A new product may provide only a few verified normal images, while representative scratches, contamination, missing parts, or structural defects remain unavailable. Industrial anomaly benchmarks reflect this setting through normal training images and heterogeneous test anomalies [1, 2, 3, 4]. Few-shot anomaly localization therefore relies on a small normal support set to identify departures from expected appearance without training a target defect classifier.

Frozen pretrained encoders provide local descriptors that can be compared directly with a memory of normal support patches. AnomalyDINO demonstrates the effectiveness of DINOv2 features for this purpose [5, 6]. Combining encoders can enrich these descriptors, and recent systems already integrate visual and vision-language pretrained representations [7, 8]. However, comparing the final scores of a two-branch and a three-branch system leaves a central design question unresolved: what makes the additional representation useful?

Two confounding effects complicate that comparison. First, adding an equally weighted branch also changes the weights of existing information. Copying one of two original branches adds no information, yet increases its effective weight from one half to two thirds. Replacing that copy with a different encoder is a distinct intervention whose benefit cannot be read directly from the original two-versus-three comparison. Second, the selected normal reference depends on how branch evidence is combined. Joint matching scores one shared support patch across branches before selecting the best candidate; independent matching allows each branch to select its own closest reference. A new descriptor can alter both the distance evidence and the chosen reference under a fixed matching rule.

This coupling makes absolute representation gains and matching dependence different questions. Independent matching has a lower or equal raw minimum-distance score, but average precision depends on the ranking of normal and anomalous pixels rather than score magnitude alone. Similarly, an added representation may help under both matching rules while showing little evidence that its gain depends on the rule. A controlled comparison must distinguish these possibilities instead of attributing the complete fusion gain to representation diversity.

Prior research establishes the importance of fusion design and consistent neighborhoods [9, 10, 11, 12]. We build on those ideas to isolate a specific unresolved attribution problem in dense industrial localization. With frozen encoders, identical supports and fixed distance weights, we cross two representation replacements with two reference-selection rules. The resulting paired contrasts quantify the value of the added descriptor and the change in that value when the shared-reference constraint is removed. This provides an interpretable basis for deciding whether a fusion improvement comes from reweighting, additional information, or their interaction with reference selection.

The contributions are as follows.

1. **A controlled decomposition of additional-representation value.** We construct an exact duplicate control that exposes the weight change hidden in an ordinary two-versus-three-branch comparison. Replacing the duplicate at fixed slot weights isolates the representation change, while a complementary construction preserves the combined weight of the original visual branch and the added branch while retaining the AnomalyCLIP branch weight. Together, these controls distinguish new descriptor information from redistribution of existing evidence and make the attribution of a fusion gain testable.

2. **A paired characterization of representation–matching dependence.** We cross both representation constructions with joint and independent normal-reference matching on the same support bank. The resulting difference-in-differences quantifies how reference selection changes the effect of an added representation. Reporting this interaction alongside absolute representation effects separates two practically different outcomes: a useful representation with little established matching dependence, and a favorable matching interaction without a clear absolute gain. The contribution lies in this controlled formulation of the industrial fusion problem, using established matching operators and statistical contrasts.

3. **Separation of representation gains from reference-sharing sensitivity.** We identify a separation between an encoder's absolute utility and its sensitivity to reference selection. On MPDD, adding DINOv2-S produces positive matching interactions without establishing a positive absolute effect under independent matching; on BTAD, its absolute effects are positive while the interaction direction remains unresolved. WideResNet50-2, additional datasets and a separately specified KolektorSDD2 confirmation extend the analysis beyond this contrast. These patterns explain why a favorable fusion score alone is insufficient to choose an encoder or a reference-sharing rule, and provide a concrete basis for evaluating those choices together.

The study centers on this attribution problem. Its dual-encoder anchor, A1, provides a fixed reference for controlled comparisons; the results support conditional design choices rather than a universal encoder ranking.

## 2 Related Work

Research on industrial anomaly localization offers several ways to represent normal appearance, store reference evidence and combine pretrained features. Their differences matter for the present question: an improvement in a complete system can arise from training, reference coverage, fusion weights or reference selection. We review these choices together to explain which aspects our fixed-support comparison isolates.

Learned normal models identify anomalies through deviations from expected appearance or feature structure. SLSG combines generative pretraining, simulated anomalies and graph-based embedding modeling [13]. RealNet uses diffusion-based anomaly synthesis with feature and residual selection [14]. PaDiM instead fits multivariate Gaussian distributions to pretrained patch embeddings [15]. These methods offer different ways to estimate normality, with corresponding training, adaptation and sample-size requirements. Learning a normal distribution or reconstruction target can improve discrimination, but its effect is difficult to separate from encoder composition when the complete learning procedure changes. For our attribution question, this motivates freezing both the encoders and the target adaptation procedure; it does not imply that learned normal models are inferior under larger training sets.

Memory-based methods retain observed normal descriptors for local comparison. PatchCore combines a representative feature memory with nearest-neighbor scoring [16], while AnomalyDINO demonstrates effective few-shot localization with frozen DINOv2 patches [5]. Their performance depends on the descriptor, the coverage of the reference memory and the preprocessing that defines the evaluated image region.

Recent work expands these choices beyond adding encoders. FEAD enriches sparse normal patterns through conditional feature transformation and multi-frequency modeling [17]. K-NG studies few-shot online detection using an evolving Neural Gas representation [18]. PGAD combines global invariance, multiscale local evidence and score calibration [19], and FastRef refines normal prototypes at test time [20]. SubspaceAD models frozen descriptors through a principal subspace [21], while DCP-SFR preserves shallow defect information in deep representations [22]. These approaches highlight the roles of reference coverage, cue retention and adaptation. These methods address valuable limitations of sparse supports, yet changes to memory coverage or prototype adaptation also change which normal evidence a query can retrieve. Their overall improvements therefore answer a broader question than the effect of replacing one frozen descriptor. We hold the support identities and bank construction fixed to obtain that narrower comparison. The cost is that the study does not capture benefits from adaptive memories or target-specific feature learning.

Contrastive Language–Image Pretraining (CLIP) provides transferable visual and textual representations [23]. WinCLIP combines prompt ensembles and local visual features for zero- and few-shot detection [24]. AnomalyCLIP learns object-agnostic normality and abnormality prompts [8], PromptAD learns from normal target samples [25], and InCTRL uses in-context residual learning with sample prompts [26]. AA-CLIP introduces anomaly-aware alignment [27], FAPrompt develops fine-grained abnormality prompts [28], and UniVAD extends training-free reference-based detection across domains [29]. Their supervision, adaptation and inference paths differ. The AnomalyCLIP visual branch, denoted **C**, uses only visual descriptors; text scores and learned prompt outputs do not enter anomaly scoring. This makes the scoring paths comparable as visual descriptor branches. However, the inherited checkpoint still carries its training-data provenance, so removing text at inference does not turn an in-domain dataset into an unseen-domain test.

Sea-CLIP is especially relevant because it combines CLIP and DINOv2 representations for few-shot detection and includes shared-reference-like and independent nearest-neighbor evidence [7]. M3DM integrates RGB and point-cloud features with multiple memories [30], and CIF uses hypergraph structural commonality to guide multimodal reference memories [31]. The architectural analysis in 3D-ADNAS examines conditional benefits of fusion modules and fusion stages [9]. These studies establish encoder combination and fusion design as existing approaches. Sea-CLIP is the closest practical motivation: combining CLIP and DINOv2 is already feasible, and reference selection already participates in such systems. A comparison of complete architectures, however, also changes feature processing or decoding. To interpret the contribution of an additional descriptor, its weight and support candidates must be controlled separately from those architectural choices.

Our emphasis is the attribution of the added representation's effect under controlled weights and references. We replace one descriptor while retaining support identities and slot weights, then measure how its effect changes under a different reference-sharing constraint. This differs from attributing a performance difference between complete architectures to one added representation, because other architectural and adaptation choices remain fixed.

Multi-view anomaly detection studies how neighborhood agreement relates to anomalous behavior. MUVAD uses neighborhoods to distinguish cross-view inconsistency from instances that are unusual across views [11]. Neighborhood Consensus Networks align neighborhood structures [12], ECMOD combines contrastive learning with neighborhood-consistency information [32], and SCoNE addresses consistent local neighborhoods across views [10]. Shared and independent neighborhoods are therefore established concepts with relevance beyond industrial images. Their motivation also explains a tension in industrial localization: a shared reference can preserve correspondence across descriptors, whereas independent references can better accommodate each descriptor's nearest normal evidence. Neither rationale alone determines pixel-level ranking quality. This motivates measuring the representation effect under both rules rather than selecting a rule from the distance inequality.

Dense industrial localization introduces a specific setting: verified normal image supports, frozen patch descriptors and pixel-level evaluation. We investigate how changing the branch representation affects performance within this setting, using duplicate and balanced controls to identify the interaction with reference selection. The contribution concerns the controlled representation comparison and its empirical consequences, while the underlying neighborhood concepts come from prior work.

Taken together, prior work explains how normal evidence is learned or stored, how its representation is expanded and how references are shared. Existing methods motivate all three choices; our study connects them through a factorized comparison that separates representation gain from reweighting and quantifies its dependence on matching. This distinction allows an observed fusion improvement to be interpreted at the level of the design choice that produced it.

## 3 Framework and Methods

### 3.1 Problem Statement

For category $c$, the input consists of $K$ verified normal support images and a query image $x$. The support set is

$$
\mathcal{X}_c=\{\boldsymbol{x}_i^c:i=1,\ldots,K\}\tag{1}
$$

Here $x_i^c$ is support image $i$ of category $c$, and the query may be normal or anomalous. Category labels specify the relevant support bank; no target defect class is predicted. We use $p$ for a query patch, $r$ for an aligned support-patch index that contains both support-image identity and spatial position, and $b$ for a visual branch. The same index $r$ denotes the corresponding support location in every branch after spatial alignment. It does not require a query patch to match the same spatial coordinate in its support image.

The outputs are a continuous pixel anomaly map $A_t$ and an image-level score $s_{\mathrm{img},t}$, where the matching-rule label $t$ is **J** (joint matching) or **L** (independent matching). A displayed defect contour is derived from the map using a visualization threshold, as specified in Section 3.6. Test labels and masks are used only for offline evaluation and example selection. Dataset roles are distinguished in Section 4.1.1.

### 3.2 Framework Overview

Support-bank construction and query scoring use the same frozen visual paths. Each support image is encoded, spatially mapped to the common lattice, and normalized branch by branch. All support patches are retained, with one aligned row identity across branches. The bank is fixed for a category, support seed and $K$. A query follows the same feature path, searches that bank, and produces patch scores under one of the two matching rules. The query never updates the bank. Figure 1 shows the shared feature path, the two reference-selection rules and the weight-controlled representation comparisons.

![Figure 1 part 1](docs/paper_complete_review_20260920/figures/fig1_framework.png)

Figure 1. Controlled framework and representation comparisons. (a) K normal support images form a fixed, aligned reference bank. (b) The query follows the same frozen feature path. J (joint matching) selects one shared reference row; L (independent matching) selects a row independently in each branch. Shared resizing and Gaussian smoothing produce the continuous map $A_t$, whose maximum is the image score. The second image panel is a thresholded display of the same map, not another learned output. (c) The duplicate-weight control DUP isolates reweighting; the equal-weight replacement TRI and the balanced replacement BAL define the representation effects and their matching interactions. B and C denote DINOv2-B and AnomalyCLIP visual features; S and D denote DINOv2-S and WideResNet50-2. The displayed map is the archived A1 (dual-encoder anchor) J result for MPDD metal_plate/test/scratches/026.png at seed 0 and K = 1. Multiple support thumbnails illustrate the general input, not that example's support count. The contour uses 256-bin Otsu thresholding solely for visualization.

The anchor combines DINOv2-B with the AnomalyCLIP visual path. Controlled variants duplicate the **B** descriptor (the DINOv2-B visual encoder) or replace that copy with a different frozen encoder. Shared resizing and smoothing convert patch scores to the continuous output map, whose spatial maximum gives the image score. Both matching rules are evaluated as fixed experimental conditions. Figure 2 shows their candidate selection. All encoders and fusion weights remain unchanged during target inference.

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

For every candidate, each branch distance is at least its own minimum; weighting and summing preserves that inequality, and minimizing the weighted sum does not reverse it. Equality holds when the branch minima admit a common minimizer. A positive gap measures the distance cost of imposing a common reference. Localization quality must be assessed separately, because average precision depends on the ordering of normal and anomalous pixels. The same distinction applies after common linear resizing and smoothing.

![Figure 2 part 1](docs/paper_complete_review_20260920/figures/fig2_matching.png)

Figure 2. Joint and independent matching on the same fixed bank. (a) One query patch and the candidate reference rows r = 1, ..., 8; the shaded cell in each branch row marks the candidate that branch finds closest. The cells are ordering indicators only and carry no measured value. (b) J (joint matching) requires a single shared reference row for all branches and then minimizes the weighted sum of distances over candidates, whereas L (independent matching) lets each branch take its own nearest row before the weighted sum is formed. Both panels use the same aligned candidate set, the same branch descriptors and the same nonnegative weights that sum to one, so the two panels differ only in the order of combination and candidate minimization. (c) The ordering constraint $L(p)$ less than or equal to $J(p)$ follows from minimizing over a less restricted reference assignment. The gap is a raw-score difference, not an AP improvement.

### 3.4 Representation Constructions and Weight Controls

Branch labels **B** (DINOv2-B visual encoder), **S** (DINOv2-S visual encoder), **C** (AnomalyCLIP visual branch) and **D** (WideResNet50-2 branch) denote the four frozen encoders. Table 1 defines the dual-encoder anchor **A1**, the duplicate-weight control **DUP**, the equal-weight replacement **TRI** and the balanced replacement **BAL**. Branch and construction labels, matching-rule identifiers and descriptive subscripts are upright; scalar variables and score functions are italic; feature vectors and full maps are bold italic.

Table 1. Fixed representation constructions and the purpose of each control.

| Construction | Full name | Distance weights | Controlled comparison |
| --- | --- | --- | --- |
| A1 | Dual-encoder anchor (DINOv2-B + AnomalyCLIP visual) | B 1/2; C 1/2 | Dual-visual anchor |
| DUP | Duplicate-weight control (copy of B, no new encoder) | B 1/3; B copy 1/3; C 1/3 | Reweight existing information; no new encoder |
| TRI | Equal-weight replacement (S or D in the copied slot) | B 1/3; S or D 1/3; C 1/3 | Replace the duplicate at fixed slot weights |
| BAL | Balanced replacement (S or D in a quarter slot) | B 1/4; S or D 1/4; C 1/2 | Preserve C and total non-C weights |

Each construction is evaluated under J and L. Bold identifies the study anchor, not a claim of best performance. For S, BAL also preserves the combined DINO-family weight. B, S, C and D denote the frozen DINOv2-B, DINOv2-S, AnomalyCLIP visual and WideResNet50-2 branches; J and L denote joint and independent reference matching.

Comparing DUP with A1 changes only how the fixed weights are split, without adding a new representation. DUP is also numerically equivalent to a two-branch B/C construction with weights two thirds and one third. Replacing the copied B descriptor in DUP with S produces TRI at identical slot weights. TRI minus DUP therefore measures the effect of that representation replacement rather than the entire difference between two and three encoders.

BAL provides a complementary comparison. In the S experiment, the combined DINO family weight remains one half, while C retains one half, allowing the B allocation to be split between B and S. In the D experiment, BAL preserves the total non-C weight but should not be called a DINO-family-preserving construction, since D is a convolutional ImageNet encoder. The weights are fixed experimental choices. DUP reuses the exact cached B descriptor, ensuring that the duplicate introduces neither new information nor feature-extraction randomness.

Figure 3 summarizes the constructions and their paired contrasts.

![Figure 3 part 1](docs/paper_complete_review_20260920/figures/fig3_constructions.png)

Figure 3. Fixed representation constructions and the contrasts built from them. (a) A1 (dual-encoder anchor), DUP (duplicate-weight control), TRI (equal-weight replacement) and BAL (balanced replacement) with their distance weights; a slot keeps the same colour across panels. (b) A1 to DUP changes only how the fixed weights are split, raising the effective B (DINOv2-B) weight from 1/2 to 2/3 and lowering the C (AnomalyCLIP visual) weight from 1/2 to 1/3, with no new representation added, and is therefore the weight-confounding control; DUP to TRI puts a real encoder into the slot at an unchanged weight; A1 to BAL keeps the non-C family total and the C weight equal. (c) The four contrasts estimated in this paper. The TRI-to-A1 difference moves both factors at once and is never attributed to S (DINOv2-S) alone. The extra slot is instantiated by five frozen encoders: S and D (WideResNet50-2) were pre-specified, while E1, E2 and E3 were added after the S and D results were known and are exploratory transfer checks. These are analysis configurations in one frozen pipeline, not trained networks.

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

All differences are formed within matched conditions and each resampling replicate before aggregation. This paired calculation directly estimates the interaction and the between-encoder difference, rather than comparing separate significance decisions.

### 3.6 Anomaly Outputs and Computational Cost

The patch scores form the matrix $a_t$ on the common lattice, are bilinearly resized to the $H$ by $W$ output canvas, and are smoothed with a Gaussian of standard deviation four pixels; $u$ indexes an output pixel. The image score is the maximum map response:

$$
\boldsymbol{A}_t=\operatorname{Gauss}_{\sigma=4}(\operatorname{Resize}_{H\times W}(\boldsymbol{a}_t)),\quad s_{\mathrm{img},t}=\max_u A_{t,u}\tag{11}
$$

The controlled evaluation restores patch scores to the retained image canvas, with dimensions $H$ by $W$; it is 448 by 448 for square images, 448 by 588 for BTAD category 03, and 630 pixels high by 224 pixels wide for KolektorSDD2. Ground truth follows the same resized and cropped image extent. Cross-method evaluation uses original-image coordinates, as described in Section 4.1.3. Pixel metrics use continuous scores. For illustrative contours only, thresholding produces

$$
\boldsymbol{M}_{\mathrm{vis},t}(u)=\mathbf{1}[A_{t,u}\geq\tau_{\mathrm{vis}}]\tag{12}
$$

Here $\tau_{\mathrm{vis}}$ is a visualization rule, not a universal fixed operating threshold. The archived qualitative examples use min-max normalization followed by 256-bin Otsu thresholding. No test mask determines this threshold. Equation (12) defines a display operation; the evaluated model outputs remain the continuous anomaly map and image score. A deployment threshold would require separate calibration.

If a bank contains $N_c$ normal patches, a query contains $n$ patches, and the combined descriptor dimension is $d$, exhaustive matching requires order $nN_cd$ distance work and order $N_cd$ feature storage. Joint matching can use one weighted concatenation index, whereas independent matching requires the corresponding branch-wise searches. Implementations can have different overheads even when the arithmetic order is the same. Larger support budgets increase reference storage, and an actual additional encoder incurs feature-extraction cost; reusing a duplicate does not incur that encoder cost. Here, training-free denotes the absence of target optimization; reference preparation and inference still incur computation.

### 3.7 Model Configuration

Table 2 records the frozen feature paths and the shared processing choices; Figure S1 shows the corresponding descriptor geometry. The B and S encoders use DINOv2 patch features [6]. C uses a CLIP Vision Transformer (ViT-L/14) visual backbone with AnomalyCLIP's diagonally prominent attention map (DPAM) path [8, 23]. Its 518-pixel input yields a 37 by 37 grid; the final returned patch tensor is retained after projection, excluding the class token. Only the visual descriptor path contributes to inference.


The common lattice follows the B canvas. Inputs are resized with preserved aspect ratio to a short side of 448 pixels and cropped from the top left to dimensions divisible by 14. The C grid is mapped to the retained image extent. On BTAD category 03, the resized extent is 448 by 597 pixels and the retained canvas is 448 by 588. The corrected BTAD analysis maps both predictions and masks through the corresponding coordinates; extensions using the historical canonical mask convention are identified separately. Geometric consistency does not imply identical receptive fields or learned semantic alignment between encoders.

The D branch was specified before its results were generated. It uses ImageNet-pretrained WideResNet50-2, bilinearly resamples layer2 and layer3 to the B lattice, concatenates their 512- and 1024-channel outputs, and normalizes the resulting 1536-dimensional descriptor. Its query-feature cache is stored in float16 and converted to float32 for normalization and scoring; this storage choice is recorded in the reproduction manifest. Branch dimensions are listed separately in Table 2. Exploratory slots additionally use original DINO ViT-S/8 (**E1**), ConvNeXt-Tiny (**E2**), and Swin-Tiny (**E3**). They follow the same mapping and unit-normalization steps. KolektorSDD2 uses its prespecified 630 by 224 canvas for B, S and D; C retains its own input path before spatial mapping. All encoder parameters remain frozen, so target optimizer, learning rate, training epochs, and training-loss curves are not applicable.

Table 2. Frozen feature paths and shared model configuration.

| Component | Full name | Input and retained feature path | Descriptor / target training |
| --- | --- | --- | --- |
| B | DINOv2-B visual encoder (frozen) | DINOv2 ViT-B/14; final patch features; short side 448 | 768 dimensions; frozen |
| S | DINOv2-S visual encoder (frozen) | DINOv2 ViT-S/14; final patch features; short side 448 | 384 dimensions; frozen |
| C | AnomalyCLIP visual branch (frozen) | CLIP ViT-L/14 visual + DPAM; 518 × 518; retain layer 24 after projection | 768 dimensions; frozen |
| D | WideResNet50-2 branch (frozen) | WideResNet50-2; ImageNet1K V1; layer2 + layer3 on B canvas | 512 + 1024 = 1536; frozen |
| E1 | Original DINO ViT-S/8 encoder (frozen, exploratory) | Original DINO ViT-S/8; final patch features | 384 dimensions; frozen |
| E2 | ConvNeXt-Tiny encoder (frozen, exploratory) | ConvNeXt-Tiny; two retained stages | 576 dimensions; frozen |
| E3 | Swin-Tiny encoder (frozen, exploratory) | Swin-Tiny; two retained stages | 576 dimensions; frozen |
| Alignment | Shared canvas alignment | Common B grid; bilinear mapping; align_corners false | 32 × 32 for a 448 × 448 canvas |
| Normalization | Shared per-branch normalization | Per-branch unit normalization; joint coefficients are square roots of distance weights | No learned scale or fusion parameter |
| Memory and scoring | Shared memory and scoring | All aligned support patches; exact nearest-neighbor matching | Fixed bank per category, seed and K |
| Output | Shared output mapping | Resize to retained H × W canvas; Gaussian standard deviation 4 pixels | Continuous map; maximum image score |
| Optimization | No target optimization | No target loss, optimizer, learning rate or training epochs | 0 target-trainable parameters |

C requests layers 6, 12, 18 and 24, uses a DPAM layer setting of 20 and retains the final patch tensor. No text scores enter the model. The fixed KolektorSDD2 canvas is 630 high × 224 wide; other inputs follow the B canvas. D is prespecified; E1–E3 are exploratory.

## 4 Experimental Evaluations

### 4.1 Experimental Design

#### 4.1.1 Datasets and Reference Protocol

We evaluate the representation-by-matching design on the Metal Parts Defect Detection dataset (MPDD), the BeanTech Anomaly Detection dataset (BTAD), MVTec Anomaly Detection (MVTec AD), Visual Anomaly (VisA) and KolektorSDD2 [1, 2, 3, 4, 33]. Table 3 distinguishes their roles and support scopes. MPDD informed development. BTAD and MVTec AD serve as external validation datasets for the frozen comparison, although both had been explored before this analysis. VisA is in-domain validation because the inherited AnomalyCLIP checkpoint was trained on VisA. This provenance applies even though inference uses only visual descriptors. Only the KolektorSDD2 directional confirmation was specified before encoding that dataset's features.

Table 3. Dataset roles and support scopes.

| Dataset | Classes | Role | S conditions | D conditions |
| --- | --- | --- | --- | --- |
| MPDD | 6 | Development | 12: seeds 0–2 | 4: seeds 0–1; K = 1, 4 |
| BTAD | 3 | External frozen validation | 8: seeds 0–1 | 4: seeds 0–1; K = 1, 4 |
| MVTec AD | 15 | External frozen validation | 12: seeds 0–2 | Not evaluated |
| VisA | 12 | In-domain frozen validation | 12: seeds 0–2 | Not evaluated |
| KolektorSDD2 | 1 | Separate confirmation | 12: seeds 0–2 | 12: seeds 0–2; all budgets |

All S studies use K = 1, 2, 4 and 8. KolektorSDD2 uses the same four budgets for D. Supports are nested within seed and shared across paired methods. Extra-encoder comparisons on MPDD/BTAD use the four D conditions; their wider twelve-condition runs are exploratory. VisA is in-domain for the inherited C checkpoint.

For each category and seed, verified normal training images form a fixed support sequence; smaller $K$ values are nested prefixes. The same supports and query images are used by every method in a paired comparison. Seeds 0, 1 and 2 crossed with $K$ equal to 1, 2, 4 and 8 yield twelve dataset-level support conditions; the primary BTAD analysis uses seeds 0 and 1 and therefore eight conditions. These are repeated evaluations on common test data, not independent datasets. KolektorSDD2 supplies 1004 test images, including 110 with nonempty defect masks and 894 without defects; only verified normal training images enter the support bank.

The original D extension and the matched five-encoder comparison use seeds 0 and 1 with $K$ equal to 1 and 4 on MPDD and BTAD. Additional E1–E3 results on twelve conditions are reported as exploratory scope checks. A separate eight-seed extension uses seeds 0 through 7 and all four budgets. Its BTAD category-03 masks follow the canonical convention, so its estimates are not substituted for the corrected-geometry primary estimates.

#### 4.1.2 Controlled Constructions and External Baselines

The primary matrix includes single-branch B, S and C and both matching rules for A1, DUP, TRI and BAL. Single-branch paths diagnose descriptor quality, while the eight combined configurations identify the two interaction contrasts. The D extension adds D-only scoring and its TRI/BAL variants. E1–E3 entered after the S and D results and are exploratory encoder substitutions. They test sensitivity to the added representation.

AnomalyDINO and PatchCore provide native-method context [5, 16]. AnomalyDINO is evaluated with and without support rotation. PatchCore includes the 224-pixel input and 1024-dimensional projected-feature configuration as well as the earlier local 128-pixel and 256-dimensional configuration. Both are retained to reveal configuration sensitivity. Each method keeps its own preprocessing, features and search implementation, while support seeds and budgets are matched. This comparison assesses practical configurations and does not isolate the matching factor or constitute a comprehensive state-of-the-art benchmark.

#### 4.1.3 Metrics and Statistical Inference

Pixel average precision (AP) is the primary localization metric. Scores and labels are pooled over test images within each category, then category APs are averaged equally. Dataset-level estimates average the applicable support conditions equally. This differs from pooling all categories into a single AP or averaging per-image AP. Pixel area under the receiver operating characteristic curve (AUROC) is a secondary diagnostic. Performance tables use AP on the 0–1 scale; effects and interactions use AP percentage points, equal to 100 times an AP difference.

Three spatial evaluation conventions remain separate. The main bootstrap analysis samples pixels on a regular stride-eight grid of the retained output canvas. Full-pixel estimates use every output-canvas pixel; finer stride-four checks test sensitivity to the sampled grid. External-method comparisons instead map predictions into original-image coordinates and evaluate their common valid intersection. Geometry conventions, pixel strides and support scopes are stated with each table; scores from these settings are not interchangeable.

We use 1000 paired image-level bootstrap replicates. Images are sampled with replacement within each fixed category, without additional normal/abnormal stratification. Each sampled image contributes its evaluated pixels as a block. The same deterministic replicate stream, based on seed 20260913 together with dataset identity, category identity and replicate index, is shared across methods and support conditions. Contrasts are formed within each replicate after the required category and condition aggregation. Intervals are conditional on observed categories and support manifests; they do not estimate uncertainty over unseen datasets or arbitrary future support sets.

The primary four S interactions, four D interactions and four matched D-minus-S contrasts each have their own exploratory four-comparison family, reported with 98.75% percentile intervals. The extended four-dataset S table has eight cells and reports 99.375% intervals; these are approximate Bonferroni adjustments. Encoder-transfer comparisons retain a separate four-cell family per encoder, with no simultaneous guarantee over all exploratory analyses. With 1000 replicates, extreme percentile endpoints have limited precision.

KolektorSDD2 retains its specified conjunction criterion: all four S/D interactions must be positive and their individual 95% intervals must exclude zero. This conjunction uses individual intervals and does not imply simultaneous 95% coverage. Excluding zero supports an interaction direction under the stated protocol; practical value also depends on the effect size and absolute representation gain. An interval spanning zero leaves the direction unresolved.

Observed condition-averaged point estimates and bootstrap means are labelled separately. Full-pixel estimates provide resolution checks; full-pixel bootstrap intervals are unavailable. The eight-seed study describes support sensitivity separately rather than treating its between-seed variation as part of the primary conditional interval.

#### 4.1.4 Implementation and Reproducibility

The recorded machine has an NVIDIA GeForce RTX 3060 Laptop GPU with 6 GB VRAM, an Intel Core i9-12900H processor and 16 GB RAM. Encoders run in evaluation mode, with cached query features reused across controlled variants. Exact nearest-neighbor search implements Section 3, using Facebook AI Similarity Search (FAISS) where applicable [34]. Feature extraction, reference construction and score evaluation are distinct computational stages; cached-stage times cannot be interpreted as end-to-end deployment latency.

The primary BTAD tables use corrected category-03 coordinates. The four-dataset and eight-seed extensions retain their archived canonical-mask convention and are reported separately. Geometric audits verify the retained image extent and support nesting. Duplicate descriptors reuse the exact cached values. Reproduction uses support manifests, frozen branch specifications and paired bootstrap streams; no target loss is optimized and no test-mask feedback selects a normal reference.

Resource reporting is restricted to measurements whose stages and devices are identifiable. VisA's extension includes mixed CPU/GPU execution and is excluded from speed or GPU-memory rankings. A separate synchronized benchmark now measures all six configurations on six MPDD units, including query feature extraction. Its reference preparation and query scoring boundary is stated in Section 4.2.14; the older stage records remain separate.

### 4.2 Results and Analysis

#### 4.2.1 Overall Controlled Results

Table 4 reports the eight configurations required for the S interaction. Under the complete S support scope, the A1 anchor reaches pixel AP of 0.3729 with joint matching and 0.3791 with independent matching on MPDD. On corrected BTAD, the corresponding values are 0.6408 and 0.6498. Independent matching has a positive average effect at the anchor, but these averages alone do not establish that another encoder benefits from that change. That question requires comparing representation effects within each matching rule.

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

The configurations do not admit one uniform ordering. On MPDD, TRI remains below the A1 anchor under both matching rules, even though TRI improves over its information-matched DUP control under L. BAL L is close to A1 L. On BTAD, both TRI and BAL exceed their corresponding controls, while BAL has the highest observed AP among these eight configurations. This is a ranking within the fixed controlled matrix and current data, not evidence that the selected weights or branch set are globally optimal.

Table 5 isolates the change that the rest of the study is built on, the matching effect, defined as the AP under L minus the AP under J. It differs from the anchor comparison only in the selection rule, because the support identities, descriptors and weights are all held fixed. On MPDD the anchor gains +0.618 AP percentage points and on corrected BTAD +0.900, and both intervals exclude zero; the other three constructions move in the same direction, from +0.321 for the duplicate control to +1.213 for BAL on MPDD. A rule that raises the score of every construction does not yet say whether a newly added representation benefits from that rule, which is the question taken up in Sections 4.2.3 and 4.2.4.

Table 5. Matching effect (AP under L minus AP under J) for the four constructions under identical support conditions.

| Dataset / construction | Point | Bootstrap mean | 95% interval |
| --- | --- | --- | --- |
| MPDD / A1 | +0.618 | +0.637 | [+0.337, +0.977] |
| MPDD / DUP | +0.321 | +0.349 | [+0.137, +0.580] |
| MPDD / TRI | +1.093 | +1.111 | [+0.701, +1.544] |
| MPDD / BAL | +1.213 | +1.253 | [+0.839, +1.722] |
| BTAD / A1 | +0.900 | +0.916 | [+0.732, +1.172] |
| BTAD / DUP | +0.631 | +0.638 | [+0.518, +0.785] |
| BTAD / TRI | +0.582 | +0.617 | [+0.373, +0.889] |
| BTAD / BAL | +0.780 | +0.826 | [+0.541, +1.171] |

Pixel AP percentage points, stride eight. The matching difference is formed within one construction, so it changes only the selection rule: a positive value means independent matching scores higher than joint matching. Values are condition-averaged observed differences and are shown next to, never replaced by, the bootstrap means. MPDD uses 12 support conditions (seeds 0, 1, 2) and corrected BTAD uses 8 (seeds 0, 1). Bold identifies the A1 anchor. These are descriptive summaries of the matching rule and are not part of the three adjusted families defined in Section 4.1.3, so no family-adjusted interval is claimed for them.

Single-branch diagnostics bound this comparison from one side. On MPDD, where these runs share the primary geometry revision, each branch alone scores below the fused anchor: 0.348 for B, 0.326 for S and 0.283 for C, against 0.373 and 0.379 for A1 under the two rules. Combining descriptors therefore helps relative to every single branch, which is why the study keeps a fused anchor rather than asking whether one encoder is enough. The corresponding BTAD diagnostics are not reported here: the corrected BTAD-03 geometry rescore covers only the eight interaction configurations, so placing the two revisions in one comparison would confound geometry with the encoder.

#### 4.2.2 Separating Reweighting from New Information

DUP lowers mean AP relative to A1 under both matching rules in both datasets (Table 4). On MPDD, the observed differences are approximately −0.80 AP percentage points under J and −1.10 under L. Thus, increasing the apparent number of branches from two to three can change performance without introducing new information. The duplicated B descriptor simply increases the effective B weight while reducing the C weight.

This result explains why the direct TRI-to-A1 comparison does not identify the contribution of S. TRI contains both a change in effective weights relative to A1 and a new descriptor relative to DUP. The TRI-to-DUP contrast fixes the branch slots and their distance weights; BAL-to-A1 addresses a complementary allocation in which C and the combined non-C weight remain unchanged. The controls do not establish that equal two-branch weights are universally preferable. They demonstrate that the weight shift is consequential in the present configuration and therefore must be separated from representation value.

#### 4.2.3 Absolute Representation Effects

Table 6 reports the S effects in AP percentage points. On MPDD, TRI minus DUP changes from −0.224 under J to +0.548 under L. The latter 95% interval spans −0.092 to +1.160, so a positive absolute gain remains uncertain. BAL minus A1 changes from −0.510 to +0.085, again with an interval spanning zero. Independent matching makes the observed representation change more favorable, but this should not be rewritten as an established absolute improvement from adding S on MPDD.

Table 6. Absolute effects of replacing or adding S under each matching rule.

| Dataset | Effect | Point | 95% interval |
| --- | --- | --- | --- |
| MPDD | $E_{TRI,J}$ | −0.224 | [−0.968, +0.478] |
| MPDD | $E_{TRI,L}$ | +0.548 | [−0.092, +1.160] |
| MPDD | $E_{BAL,J}$ | −0.510 | [−1.135, +0.123] |
| MPDD | $E_{BAL,L}$ | +0.085 | [−0.434, +0.708] |
| BTAD | $E_{TRI,J}$ | +1.553 | [+0.637, +2.465] |
| BTAD | $E_{TRI,L}$ | +1.503 | [+0.585, +2.495] |
| BTAD | $E_{BAL,J}$ | +0.974 | [+0.177, +1.803] |
| BTAD | $E_{BAL,L}$ | +0.854 | [+0.057, +1.753] |

Pixel AP percentage points, stride eight. Values are condition-averaged observed differences, not bootstrap means. MPDD uses 12 support conditions and BTAD uses 8; each dataset name is printed once for its group. Intervals are exploratory; the primary adjusted interaction intervals appear in Table 7.

BTAD illustrates a different situation. The TRI replacement effects are +1.553 points under J and +1.503 under L; their exploratory 95% intervals are both above zero. BAL also has positive estimated effects under both rules. Here, additional S information is useful relative to the specified controls, yet the very similar TRI effects suggest that its usefulness need not depend strongly on the matching rule. Direct interaction inference, rather than separate effect intervals, resolves that distinction in the next subsection.

The first page of Figure 4 plots the eight S effects by dataset, allowing the two rules to be compared within each contrast.

![Figure 4 part 1](docs/paper_complete_review_20260920/figures/fig4a_representation_effects.png)

Figure 4. Absolute representation effects for S (DINOv2-S). Panels show observed effects in MPDD and corrected-geometry BTAD with individual 95% paired image-bootstrap intervals. MPDD uses seeds 0–2 and BTAD seeds 0, 1, with K = 1, 2, 4, 8. Units are AP percentage points. These absolute effects differ from the matching interactions shown on the continuation page.

![Figure 4 part 2](docs/paper_complete_review_20260920/figures/fig4b_matched_encoders.png)

Figure 4 continued. Matched-scope encoder interactions. All five encoders use seeds 0, 1 and K = 1, 4 in this comparison; points are observed condition means and bars are 98.75% paired intervals with a separate four-comparison family for each encoder. E1–E3 are exploratory substitutions. The different primary S (DINOv2-S) scope and wider encoder scope remain separately identified in the tables.

#### 4.2.4 Direct Interaction and Encoder Dependence

The direct S interactions on MPDD are +0.772 points for TRI and +0.595 for BAL (Table 7). Their adjusted 98.75% intervals are [+0.346, +1.211] and [+0.189, +1.030], respectively. Both exclude zero. Their point estimates exceed the descriptive 0.5-point scale, but their interval lower bounds do not, so the data do not establish an effect uniformly above that practical reference magnitude. The continuation of Figure 4 compares all five encoders under a matched four-condition scope; the broader dataset evidence is reported separately in Section 4.2.10.

Table 7. Direct representation-by-matching interactions for S.

| Dataset / contrast | Point | 95% interval | 98.75% interval | Full-pixel point |
| --- | --- | --- | --- | --- |
| MPDD / $I_{TRI}$ | +0.772 | [+0.426, +1.118] | [+0.346, +1.211] | +0.787 |
| MPDD / $I_{BAL}$ | +0.595 | [+0.322, +0.927] | [+0.189, +1.030] | +0.601 |
| BTAD / $I_{TRI}$ | −0.050 | [−0.192, +0.186] | [−0.235, +0.244] | −0.044 |
| BTAD / $I_{BAL}$ | −0.119 | [−0.265, +0.110] | [−0.306, +0.167] | −0.117 |

AP percentage points. The point estimates and intervals use stride eight; the last column uses all pixels and has no interval. The four stride-eight interactions form one Bonferroni-adjusted exploratory family. A positive interaction alone does not imply a positive absolute representation effect.

On BTAD, the S interactions are −0.050 and −0.119 points, with both adjusted intervals spanning zero. The small negative points are not evidence of a general advantage for joint matching. Combined with Table 6, the result is that S has positive representation effects under the tested rules while the current data do not clearly resolve a difference between those effects. This is distinct from saying that matching is irrelevant or that the two rules are equivalent.

The prespecified D extension provides a second representation condition. Table 8 reports its full-pixel localization results under the restricted four-condition scope. On MPDD, TRI D L reaches AP 0.4107 compared with 0.3554 for DUP L; on BTAD, it reaches 0.6591 compared with 0.6335. The corresponding full-pixel representation effects are approximately +5.53 and +2.57 AP percentage points. These are absolute representation effects, not the much smaller interaction estimates. D alone has lower pixel AP than these fused constructions, showing that the fusion result cannot be explained simply by selecting D's standalone score. Table 8 reports the full-pixel values supporting these D effects.

Table 8. Full-pixel localization for the prespecified D extension.

| Configuration | MPDD AP | MPDD AUROC | BTAD AP | BTAD AUROC |
| --- | --- | --- | --- | --- |
| D | 0.3452 | 0.9708 | 0.4449 | 0.9542 |
| A1 J | 0.3622 | 0.9658 | 0.6361 | 0.9745 |
| A1 L | 0.3687 | 0.9688 | 0.6455 | 0.9755 |
| DUP J | 0.3510 | 0.9626 | 0.6270 | 0.9734 |
| DUP L | 0.3554 | 0.9647 | 0.6335 | 0.9742 |
| TRI D J | 0.3960 | 0.9731 | 0.6464 | 0.9743 |
| TRI D L | 0.4107 | 0.9768 | 0.6591 | 0.9758 |
| BAL D J | 0.3942 | 0.9736 | 0.6401 | 0.9749 |
| BAL D L | 0.4076 | 0.9773 | 0.6545 | 0.9766 |

All output-canvas pixels, seeds 0 and 1, K = 1 and 4. Each number averages category metrics and the four support conditions. No full-pixel confidence intervals were computed. The D-only row does not use the C branch. Bold identifies A1.

All four D interactions are positive, with adjusted intervals excluding zero (Table 9): +0.974 and +0.628 points on MPDD, and +0.622 and +0.501 on BTAD. The full-pixel points retain these directions. This establishes that a positive interaction in the observed setting is not confined to adding a smaller DINOv2 encoder. It does not establish the same result for arbitrary convolutional backbones or for additional datasets.

Table 9. Direct matching interactions with D replacing S.

| Dataset / contrast | Point | 95% interval | 98.75% interval | Full-pixel point |
| --- | --- | --- | --- | --- |
| MPDD / TRI | +0.974 | [+0.602, +1.472] | [+0.514, +1.689] | +1.033 |
| MPDD / BAL | +0.628 | [+0.279, +1.218] | [+0.162, +1.394] | +0.694 |
| BTAD / TRI | +0.622 | [+0.373, +0.917] | [+0.298, +1.003] | +0.624 |
| BTAD / BAL | +0.501 | [+0.239, +0.883] | [+0.188, +0.995] | +0.496 |

AP percentage points. All four support conditions use seeds 0 and 1 and K = 1 and 4. Intervals are stride-eight paired percentile intervals, with the four D contrasts forming their own adjustment family. The final column has no interval.

Directly comparing the full-scope S effects with the restricted-scope D effects would confound encoder choice with support-condition coverage. Table 10 instead restricts S to the D seeds and budgets and directly estimates the D-minus-S interaction difference. The observed differences on BTAD are +0.623 and +0.585 points, with adjusted intervals [+0.255, +0.945] and [+0.204, +1.060]. On MPDD, the observed differences are +0.207 and +0.081, and the intervals span zero. The bootstrap means differ from the observed points, particularly on MPDD, and are shown in a separate column rather than being mislabeled as point estimates.

Table 10. Matched difference between D and S interactions.

| Dataset / contrast | Observed difference | Bootstrap mean | 98.75% interval | Full-pixel difference |
| --- | --- | --- | --- | --- |
| MPDD / TRI | +0.207 | +0.326 | [−0.296, +1.118] | +0.264 |
| MPDD / BAL | +0.081 | +0.139 | [−0.372, +0.806] | +0.075 |
| BTAD / TRI | +0.623 | +0.603 | [+0.255, +0.945] | +0.616 |
| BTAD / BAL | +0.585 | +0.576 | [+0.204, +1.060] | +0.575 |

AP percentage points; D interaction minus S interaction. S is restricted to the identical seeds 0 and 1 and K = 1 and 4. Intervals come from within-replicate differences, not differences of interval endpoints. Four encoder comparisons form a separate exploratory adjustment family. Full-pixel differences have no intervals.

These comparisons support encoder dependence on BTAD under the matched scope. On MPDD, the uncertainty does not resolve an S-to-D interaction difference; it is not evidence that the encoders are equivalent. More generally, a larger interaction does not mean that an encoder is better in every absolute metric. The available image-level metrics illustrate this separation: under the four-condition BTAD scope, BAL D L has image AP 0.9372 versus 0.9468 for A1 L even though its full-pixel AP is higher. Image-score pooling and pixel ranking answer different evaluation questions.

#### 4.2.5 Support Budget and Category Conditions

Figure 5(a) shows the seed-averaged S interaction against the nested support budget. On MPDD both contrasts strengthen as K grows: the TRI interaction rises from +0.41 percentage points at one support to +0.75, +0.88 and +1.01 at two, four and eight supports, and BAL rises from +0.37 to +0.83. On the corrected BTAD revision the same contrast weakens and changes sign, moving from +0.20 points at one support to +0.09 at two, −0.14 at four and −0.23 at eight, where the interval no longer includes zero. The curves therefore support a budget-dependent description, not a monotone law that more normal references consistently amplify the benefit of independent matching.

![Figure 5 part 1](docs/paper_complete_review_20260920/figures/fig5a_budget_seed.png)

Figure 5. Sensitivity to support budget and seed. (a) Seed-averaged bootstrap means across nested K budgets, using the MPDD study revision and corrected BTAD revision. (b) Observed interaction points for eight support seeds; seeds 0–2 have separate query blocks and seeds 3–7 share a cached block. The seed extension uses canonical BTAD masks. Filled and open markers distinguish these groups. Lines connect evaluated settings and do not imply independent samples or a fitted trend. Units are AP percentage points.

![Figure 5 part 2](docs/paper_complete_review_20260920/figures/fig5b_categories.png)

Figure 5 continued. (c) Category-level TRI interactions as bootstrap means with individual 95% intervals. MPDD uses the study revision and BTAD the corrected revision. This exploratory comparison has no multiplicity adjustment across categories.

Adding normal candidates cannot increase the exact minimum raw distance when the bank is nested and the descriptors remain fixed. However, AP depends on score ordering, and an interaction is a difference of four performance values. Neither AP nor the interaction inherits a monotonicity guarantee from the minimum-distance operation. The distinction also explains why a numerical constraint gap should not be treated as a defect-performance measure.

Category analyses further limit the aggregate interpretation. Figure 5(c) resolves the TRI interaction by category: all six MPDD categories carry a positive estimate, led by connector and tubes, whereas the three BTAD categories stay close to zero and category 02 is slightly negative. Omitting any one MPDD category leaves the TRI aggregate interaction positive in the recorded leave-one-category analysis. On corrected BTAD, omitting category 02 changes the TRI aggregate direction. With only three BTAD categories, the average is sensitive to category composition. Per-category and per-budget intervals are exploratory follow-up analyses and do not inherit the primary family's multiplicity guarantee. They identify conditions worth testing on new data rather than proving a causal role for category identity or defect size.

The stride-eight and full-pixel aggregate interaction directions agree for the S and D summaries. This is a useful numerical sensitivity check because sparse pixel sampling can alter the contribution of small defects. It does not eliminate that concern, and no claim of full-pixel significance follows from point agreement. In particular, the selected qualitative examples include tiny defects whose per-image AP can change markedly when only a few sampled pixels are positive.

#### 4.2.6 Qualitative Localization and Predicted Contours

Figures 6 and 7 show five MPDD cases from seed 0 and four normal supports, with three improvements and two degradations for A1 L versus A1 J. The cases are selected by extreme stored per-image AP changes from the fixed closeout candidate list. Selection is based on localization performance, not on the average reduction in raw score. These panels illustrate the anchor's matching behavior; they are not a substitute for the direct representation interaction in Tables 7 and 9.

![Figure 6 part 1](docs/paper_complete_review_20260920/figures/qualitative_improvements_part1.png)

Figure 6. Three selected MPDD improvements for A1 L (the dual-encoder anchor under independent matching) relative to A1 J (joint matching) at seed 0 and K = 4. Values are stored stride-eight per-image AP, rather than the category-pooled AP used in the main tables. J/L heatmaps share one full-map min-max range per row. The cyan L contour uses 256-bin Otsu thresholding on that normalized score. Red hollow rectangles define identical GT-centered visual crops, enlarged below. GT is used for evaluation and crop placement, never to generate the predicted contour. These are selected extremes, not a random test sample.

![Figure 6 part 2](docs/paper_complete_review_20260920/figures/qualitative_improvements_part2.png)

Figure 6 continued. The third selected improvement, with the same scale, crop, and contour conventions.

The heatmaps for each case use one common minimum and maximum over its J and L maps after resizing and smoothing. The L map is quantized into 256 bins, and Otsu's between-class-variance criterion selects a visualization threshold, taking the smallest maximizing bin if tied. The cyan contour traces the resulting predicted mask. It is derived entirely from the model score. For visual inspection only, a square crop is centered on the bounding box of the ground-truth defect mask, with side length clipped between 96 and 260 pixels after a 1.8-fold expansion; the same crop is applied to all columns. The ground truth determines this display region and the evaluation labels, but not the predicted mask.

![Figure 7 part 1](docs/paper_complete_review_20260920/figures/qualitative_mpdd_matching_degradations.png)

Figure 7. Two selected MPDD degradations under the same A1 (dual-encoder anchor) comparison and display protocol as Figure 6. Lower raw scores under independent matching do not guarantee improved pixel ordering or a complete contour. The cases illustrate matching behaviour at the anchor and are not direct evidence of the representation interaction. A companion per-sample comparison set, generated from the same common valid region as Table 11, places selected samples beside the native baselines at seed 0 with K = 4: MPDD (six method columns, six categories), BTAD (six, three), MVTec AD (six, fifteen) and VisA (six, twelve). Each class shows the three test images with the largest spread of per-sample pixel AP, the panels of a row share one colour scale, and in the current set every method column carries data for every displayed unit; a column whose per-sample dump did not cover a unit would be retained as n/a rather than dropped. The set is archived with the figure sources.

Improved AP does not imply an accurate defect boundary at an arbitrary operating threshold. The small contours in the examples may cover only the strongest part of a scratch or mismatch, while secondary activations can remain elsewhere in the map. The degradation cases in Figure 7 likewise show that independent matching can change the relative responses unfavorably even though its raw patch distances are no larger. These observations motivate keeping continuous localization evidence, thresholded visualization, and deployment segmentation accuracy as separate claims. No ground-truth outline is substituted for a predicted output.

#### 4.2.7 Native Baseline Context and Computational Cost

Table 11 evaluates six configurations on the intersection of their actual valid image regions across four datasets. A1 L has the highest observed AP on MPDD, BTAD and VisA among these configurations. On MVTec AD, AnomalyDINO without and with rotation reaches 0.5643 and 0.5637, respectively, above A1 L at 0.5570. The rotation-enabled AnomalyDINO configuration improves on its non-rotation version, and the official-resolution PatchCore configuration improves substantially on the earlier local low-resolution variant. These changes show why an inadequately configured baseline can give a misleading impression of practical advantage.

Table 11. External-method context from six configurations on a common valid region.

| Configuration | MPDD | BTAD | MVTec AD | VisA |
| --- | --- | --- | --- | --- |
| A1 L | 0.3698 | 0.6474 | 0.5570 | 0.3763 |
| A1 J | 0.3611 | 0.6380 | 0.5530 | 0.3713 |
| AnomalyDINO + rotation | 0.3214 | 0.5840 | 0.5637 | 0.3469 |
| AnomalyDINO | 0.3130 | 0.5614 | 0.5643 | 0.3291 |
| PatchCore 224 / 1024 | 0.2275 | 0.3760 | 0.4955 | 0.3111 |
| PatchCore 128 / 256 | 0.1649 | 0.2886 | 0.3966 | 0.2554 |

Category-macro pixel AP, averaged over seeds 0 and 1 and K = 1 and 4. All 864 method-category-condition rows are included. Average retained coverage is 76.56%, 70.49%, 76.56% and 59.07%, respectively. Methods differ in backbone, resolution and augmentation. Bold identifies A1, not a statistical superiority claim.

The common region covers 76.56% of MPDD, 70.49% on average for BTAD, 76.56% of MVTec AD and 59.07% of VisA; BTAD category 03 has a smaller intersection of approximately 58.36%. Restricting evaluation avoids inventing predictions in cropped-away borders, but also removes those borders from the evaluation task. Different backbones, reference augmentation, resolutions, and post-processing remain. Consequently, the observed ranking is useful local context, not proof that A1 exceeds the complete published methods under every native or full-image protocol. AnomalyDINO also uses the S backbone employed in the controlled study, so it is not an independent test of a wholly unrelated representation family.

An extension of this comparison is reported separately in Table 12 rather than being merged into the six frozen columns: that table repeats the six configurations above as frozen values and adds three further external families evaluated on the same common-region rule under their own native protocols, so it is context for this section and not a ranking.

Table 12. Extension of Table 11 with three further external families under their own native protocols.

| Configuration | Protocol | MPDD | BTAD | MVTec AD | VisA |
| --- | --- | --- | --- | --- | --- |
| A1 L | controlled, frozen | 0.3698 | 0.6474 | 0.5570 | 0.3763 |
| A1 J | controlled, frozen | 0.3611 | 0.6380 | 0.5530 | 0.3713 |
| AnomalyDINO + rotation | native, frozen normal modelling | 0.3214 | 0.5840 | 0.5637 | 0.3469 |
| AnomalyDINO | native, frozen normal modelling | 0.3130 | 0.5614 | 0.5643 | 0.3291 |
| PatchCore 224 / 1024 | native, frozen normal modelling | 0.2275 | 0.3760 | 0.4955 | 0.3111 |
| PatchCore 128 / 256 | native, frozen normal modelling | 0.1649 | 0.2886 | 0.3966 | 0.2554 |
| SubspaceAD 256 fp16 | native, frozen normal modelling | 0.3194 | 0.5869 | 0.4988 | 0.3203 |
| WinCLIP+ 240 | native, vision-language few-shot | 0.1887 | 0.1137 | 0.3079 | 0.1112 |
| AnomalyCLIP zero-shot 518 | native, zero-shot on the target domain (upstream auxiliary-domain-trained prompt learner) | 0.2724 | 0.4108 | 0.4262 | 0.1938 |

Category-macro pixel AP on the intersection of the regions the participating methods actually score. The six upper configurations are the frozen values of Table 11, copied row by row and not recomputed; the three added families keep their native input resolutions and protocols, stated in the Protocol column, and are therefore not compared under the controlled support protocol. Adding a method can change the common region, and a method whose scored extent is a subregion of the others would change the frozen values above when the table is recomputed; for the three families added here the joint recomputation was carried out and reproduced the frozen rows to the digit (864 rows, zero mismatches; 36 of 36 region rectangles identical), because each of them covers the full original image. The AnomalyCLIP row is a single native configuration with no seed or support-budget loop and is not paired with the four-condition rows. It uses an auxiliary-domain-trained prompt learner and is zero-shot on the target domain: the learner was fitted on an auxiliary dataset (VisA for the MVTec AD column and MVTec AD for the other three datasets, following the upstream convention of never fitting a learner on the dataset it evaluates), with no target-dataset fitting. Its checkpoint is supplied with the upstream AnomalyCLIP source archive (commit 3911738c0867544f545a076ad78f3f11d9ecbfdf, ZIP SHA256 533ED87B6658CDB247D063A249CEFEA54AB81623CB11683C6F02345B9A6CEAFE) and is an upstream-published auxiliary-domain-trained weight, not a checkpoint trained by this project. Methods differ in backbone, resolution, augmentation and training provenance, so the table provides context and is not a ranking.

Table 13 reports the runtime stages for which instrumentation is available. Reference rotation increases AnomalyDINO's recorded processing time along with its AP. The D extension separately records approximately 55.4 seconds of query encoding, 8.3 seconds of reference encoding, and 266.3 seconds of controlled scoring across its archived scope, with feature reuse between configurations. Its recorded peak allocated GPU memory is approximately 417.7 MiB. Those stage totals are partially instrumented and do not constitute a synchronized complete-run latency or the simultaneous memory footprint of all encoders.

Table 13. Recorded native-method runtime stages and process GPU memory.

| Dataset | Configuration | Processing s | Evaluation s | GPU peak MiB |
| --- | --- | --- | --- | --- |
| MPDD | AnomalyDINO no rotation | 44.47 | 8.38 | 111.6–112.5 |
| MPDD | AnomalyDINO rotation | 82.74 | 8.22 | 111.6–112.5 |
| MPDD | PatchCore 224 | 99.75 | 23.40 | Unavailable |
| BTAD | AnomalyDINO no rotation | 53.19 | 16.39 | 118.8 |
| BTAD | AnomalyDINO rotation | 135.38 | 16.89 | 118.8 |
| BTAD | PatchCore 224 | 115.45 | 40.85 | Unavailable |

Mean seconds per complete dataset condition over seeds 0 and 1 and K = 1 and 4; MPDD has 458 queries and BTAD 741. Processing is bank plus retrieval for AnomalyDINO and the combined native stage for PatchCore. GPU cells report the range of process peaks across conditions; each dataset name is printed once for its group. Cached feature extraction and other unrecorded stages are not added; these are not end-to-end per-image latencies. A1 has no comparable complete historical timing.

Figure 8 shows the historical processing and evaluation stages for the two datasets in Table 13. These records remain distinct from the synchronized benchmark in Section 4.2.14.

![Figure 8 part 1](docs/paper_complete_review_20260920/figures/fig8_resources.png)

Figure 8. Historical processing and evaluation times from Table 13. Bars are mean seconds per complete dataset condition over seeds 0, 1 and K = 1, 4. Processing includes bank construction and retrieval for AnomalyDINO and an inseparable combined stage for PatchCore. Feature extraction is incompletely covered. These totals are historical stage measurements, not per-image latency; Figure S5 provides separately measured inference stages on three MPDD categories.

The historical records omit some stages and cannot be reconstructed as complete per-image latency. Section 4.2.14 supplies a separate measurement of timed reference-preparation and query-scoring stages on a restricted MPDD scope. Increasing the encoder set adds feature-extraction work and descriptor storage, while increasing the support budget enlarges the bank. Whether an AP improvement justifies these costs remains application-dependent.

#### 4.2.8 Discussion and Limitations

The practical implication is to inspect the source of a fusion gain before enlarging an encoder set. A duplicate control tests whether effective weights already change the result. A representation replacement at fixed weights tests whether the new descriptor helps. Crossing that replacement with the matching rule tests a different question: whether reference selection changes its value. The MPDD and BTAD results show why these questions cannot be collapsed into a single three-branch-versus-two-branch comparison.

The interpretation remains limited in several ways. First, the primary interaction was formulated after earlier project exploration, and the datasets are not untouched confirmation sets. Second, the bootstrap conditions on the observed categories and fixed support manifests; its intervals do not characterize arbitrary future support choices. Third, only one prespecified heterogeneous encoder was added, with a smaller seed and budget scope than the S study. Fourth, full-pixel intervals remain unavailable, and the synchronized resource benchmark covers one machine and three MPDD categories rather than all datasets. Fifth, qualitative cases are selected extremes, and their Otsu contours are display choices rather than calibrated defect masks. Sixth, the operations that every construction shares, namely spatial mapping, branch normalization and scoring from concatenated descriptors, are held fixed rather than ablated at the primary scope, so this study does not quantify how much each of them contributes and does not present them as validated modules; Section 4.2.13 reports single-condition ablations of shared operations, which is exploratory for the same reason. Finally, the geometric alignment is deterministic canvas correspondence, not a learned guarantee that receptive fields describe exactly the same object part.

These limitations do not turn a negative or uncertain interaction into a failed experiment. BTAD with S separates positive representation value from uncertain matching dependence, while the D comparison provides an encoder-specific difference under matched conditions. The study's contribution is this controlled and qualified account. A future learned selector, foreground filter, or dynamic fusion module would require its own implementation and evidence; none is implied by the present results.

#### 4.2.9 Separately Specified Confirmation on KolektorSDD2

KolektorSDD2 (KSDD2) provides a separately specified confirmation beyond the previously explored datasets. Before any KSDD2 feature file existed, the specification frozen at 11:59 UTC on 18 September 2026 required all four S and D interactions to be positive with individual 95% intervals excluding zero. Success was defined by this conjunction; a single interval spanning zero would fail the specified criterion.

The dataset contributes one category, a single production item, so the category macro average reduces to that category. Its positivity rule is fixed as "a sample is positive if and only if its ground-truth mask has at least one non-zero pixel", which gives 110 positive and 894 negative test images out of 1004. The frozen canvas is 630 pixels high by 224 pixels wide, giving a 45 by 16 patch grid with patch size and stride 14. The D branch reuses that same fixed canvas, so its input extent equals the B canvas exactly; this resolves one ambiguity in the D branch text, which was written for the two older datasets. The C branch keeps its own 518-pixel preprocessing and is re-gridded onto the B canvas as everywhere else. The scope is seeds 0, 1 and 2 with $K$ equal to 1, 2, 4 and 8, giving twelve support conditions.

Table 14 reports the four individual 95% intervals specified in advance. This conjunction criterion is retained rather than changed after observing the results. The intervals do not provide a simultaneous 95% coverage guarantee, and the confirmation set remains separate from the exploratory adjustment families.

Table 14. Confirmation-set interactions on KolektorSDD2, whose expected direction was frozen before any of its features were encoded.

| Branch | Contrast | Point | 95% interval | Excludes zero |
| --- | --- | --- | --- | --- |
| S | $I_{TRI}$ | +0.539 | [+0.299, +0.823] | Yes |
| S | $I_{BAL}$ | +0.343 | [+0.129, +0.579] | Yes |
| D | $I_{TRI}$ | +0.499 | [+0.212, +0.851] | Yes |
| D | $I_{BAL}$ | +0.367 | [+0.128, +0.653] | Yes |

AP percentage points, stride eight, 1000 paired replicates. One category and twelve support conditions (seeds 0, 1, 2 with K = 1, 2, 4 and 8). The frozen specification fixes the judgement as the 95% interval, so no family adjustment is applied to this confirmation set; the same four cells also exclude zero at 98.75%, which is recorded for transparency only. Each branch name is printed once for its two rows.

All four point estimates are positive and all four 95% intervals exclude zero, so the frozen expectation is met on this dataset. We record for transparency that the same four cells also exclude zero at 98.75%, but the frozen judgement remains the 95% interval. The confirmation set deliberately does not enter the four-dataset table of Section 4.2.10, whose adjustment family was fixed over the exploratory cells.

#### 4.2.10 Validation across Four Datasets

The same two contrasts were later run on MVTec AD and VisA under the study's own aggregation rule, so that the generalization datasets can be read beside MPDD and BTAD. Table 15 reports all four datasets at the 95%, 98.75% and 99.375% levels; the last level matches the eight-cell family that this table actually covers, whereas the 98.75% level remains the four-cell family of Section 4.2.4.

Table 15. The two interactions on all four datasets, with the interval levels that the wider family requires.

| Dataset (role) | Contrast | Estimate | 95% | 98.75% | 99.375% |
| --- | --- | --- | --- | --- | --- |
| MPDD (development) | $I_{TRI}$ | +0.762 | [+0.426, +1.118] | [+0.346, +1.211] | [+0.324, +1.250] |
| MPDD (development) | $I_{BAL}$ | +0.615 | [+0.322, +0.927] | [+0.189, +1.030] | [+0.152, +1.081] |
| BTAD (external frozen validation) | $I_{TRI}$ | −0.020 | [−0.192, +0.192] | [−0.237, +0.238] | [−0.245, +0.261] |
| BTAD (external frozen validation) | $I_{BAL}$ | −0.087 | [−0.258, +0.109] | [−0.300, +0.179] | [−0.313, +0.201] |
| MVTec AD (external frozen validation) | $I_{TRI}$ | +0.432 | [+0.342, +0.530] | [+0.324, +0.553] | [+0.309, +0.570] |
| MVTec AD (external frozen validation) | $I_{BAL}$ | +0.402 | [+0.313, +0.503] | [+0.297, +0.529] | [+0.287, +0.534] |
| VisA (in-domain frozen validation) | $I_{TRI}$ | +0.927 | [+0.788, +1.064] | [+0.754, +1.112] | [+0.738, +1.114] |
| VisA (in-domain frozen validation) | $I_{BAL}$ | +0.810 | [+0.673, +0.959] | [+0.631, +1.011] | [+0.611, +1.018] |

AP percentage points, stride eight, 1000 paired bootstrap replicates. The estimate is the mean of the replicate distribution, not the condition-averaged observed difference used in Table 7; on MPDD the two differ by 0.01 point. The 98.75% level is a Bonferroni adjustment over the four MPDD and BTAD cells and the 99.375% level over the eight cells this table covers. The BTAD row pools the study's canonical-mask series rather than the corrected geometry used in Section 4.2.4, which moves the point estimate by about 0.03 point without changing the judgement. Stride-one point estimates are now available for all four datasets (+0.787 and +0.601 points on MPDD, −0.045 and −0.115 on BTAD, +0.423 and +0.386 on MVTec AD, +0.896 and +0.760 on VisA, each pair ordered as $I_{TRI}$ then $I_{BAL}$). KolektorSDD2 is reported separately in Table 14 and is not part of this family. Each dataset name is printed once for its two rows.

The four datasets do not behave alike, and we keep their readings separate instead of summarizing them as a replication. On MPDD both interactions are positive and exclude zero at the widest level reported here. On MVTec AD both are positive, with the narrowest intervals in the table, and they also exclude zero at the widest level; their point estimates, about +0.4 points, are the smallest of the three positive datasets. On VisA both are positive and the largest in the table, which does not provide independent unseen-domain evidence because VisA is in-domain for the C branch: its frozen AnomalyCLIP checkpoint was trained on that dataset. On BTAD the point estimate is close to zero and both intervals span zero at all three levels, so the current data are insufficient to determine the direction of the interaction there; the point estimates are an order of magnitude smaller than those of the positive datasets, and the table must not be read as four consistent significant replications. This is not evidence of equivalence between the two rules; it means only that no direction is established there.

Three qualifications belong with the table. First, MVTec AD and VisA are frozen validation sets, not untouched confirmation sets; only KolektorSDD2 was frozen before its features were encoded. Second, the BTAD row pools the study's canonical-mask series, whereas the primary BTAD tables use the corrected geometry for category 03; the two differ by about 0.03 point in the point estimate and both fail to exclude zero, so the reading is unchanged, but the numbers should not be quoted interchangeably. Third, the estimate column is the mean of the replicate distribution rather than the condition-averaged observed difference used in Table 7, a difference of 0.01 point on MPDD; stride-one point estimates now exist for all four datasets (+0.787 and +0.601 points on MPDD, −0.045 and −0.115 on BTAD, +0.423 and +0.386 on MVTec AD, +0.896 and +0.760 on VisA).

The role strings are the ones recorded by the table itself: development for MPDD, external frozen validation for BTAD and MVTec AD, and in-domain frozen validation for VisA. The frozen encoder specification records BTAD as a holdout; both strings describe the same fact, that BTAD had been examined in the project before these runs.

#### 4.2.11 Further Frozen Encoders and Support-Set Variation

Three further frozen encoders entered the extra slot after the S and D results were known, so they are exploratory transfer checks rather than prespecified confirmations. E1 is the original DINO self-distillation ViT-S/8 with 384-dimensional descriptors; E2 is ConvNeXt-Tiny with 576; E3 is Swin-Tiny with 576. Each is mapped to the B canvas and normalized exactly like the other branches, and the same TRI and BAL contrasts are formed at the frozen slot weights. Table 16 lists each encoder's interaction in the four-condition scope shared with S and D and in the wider twelve-condition scope recorded for the additional encoders.

Table 16. Interactions of the five frozen encoders, in the four-condition scope shared with S and D and in the wider twelve-condition scope.

| Encoder (conditions) | MPDD $I_{TRI}$ | MPDD $I_{BAL}$ | BTAD $I_{TRI}$ | BTAD $I_{BAL}$ |
| --- | --- | --- | --- | --- |
| S (4) | +0.695 [+0.193, +1.160] | +0.547 [+0.078, +0.962] | +0.029 [−0.189, +0.293] | −0.052 [−0.273, +0.208] |
| D (4) | +1.020 [+0.514, +1.689] | +0.686 [+0.162, +1.394] | +0.631 [+0.298, +1.003] | +0.524 [+0.188, +0.995] |
| E1 (4) | +0.811 [+0.246, +1.362] | +0.488 [−0.136, +1.091] | +0.583 [+0.172, +1.056] | +0.224 [−0.158, +0.649] |
| E1 (12) | +0.995 [+0.529, +1.504] | +0.747 [+0.290, +1.309] | +0.441 [+0.067, +0.829] | +0.174 [−0.138, +0.516] |
| E2 (4) | −0.018 [−0.358, +0.298] | +0.076 [−0.315, +0.588] | +0.278 [+0.152, +0.494] | +0.422 [+0.158, +0.872] |
| E2 (12) | −0.038 [−0.266, +0.170] | +0.036 [−0.235, +0.443] | +0.178 [+0.090, +0.315] | +0.226 [+0.063, +0.491] |
| E3 (4) | +1.253 [+0.644, +2.056] | +0.745 [+0.055, +1.425] | +0.488 [+0.217, +0.906] | +0.465 [+0.171, +0.955] |
| E3 (12) | +1.397 [+0.803, +2.215] | +0.939 [+0.355, +1.620] | +0.298 [+0.073, +0.578] | +0.180 [−0.029, +0.442] |

AP percentage points, stride eight; each cell gives the replicate mean followed by the 98.75% paired interval, the Bonferroni level for that encoder's four cells. Cells marked (4) pool seeds 0 and 1 with K = 1 and 4, the primary scope shared with S and D, so their paired differences against S are same-condition pairs; cells marked (12) pool seeds 0, 1, 2 with K = 1, 2, 4 and 8, the wider scope recorded for the three additional encoders. Both scopes are given because they change some of the zero-exclusion decisions. No family adjustment covers the additional encoders as a group, because E1, E2 and E3 were added after the S and D results were known.

The four-condition scope uses seeds 0 and 1 with $K$ equal to 1 and 4 for every encoder, enabling paired encoder comparisons. The wider scope uses seeds 0, 1 and 2 with all four budgets. It is reported separately because support coverage changes some interval-exclusion decisions.

Within the four-condition scope the additional encoders split on MPDD: E3 has positive interactions in both contrasts with intervals above zero, E1 has positive points in both but its BAL interval spans zero, E2 has none, and S and D remain positive. On BTAD all three additional encoders have a positive $I_{TRI}$ with an interval above zero, while for $I_{BAL}$ only E2 and E3 do. In the twelve-condition scope E1's MPDD BAL interval also clears zero, while E3's BTAD BAL interval no longer does. Across both scopes the only statement that survives concerns E2: it is the single encoder whose MPDD TRI interaction is negative and lies below the S interaction with a paired interval that excludes zero, at −0.712 points in the four-condition scope and −0.733 in the twelve-condition scope. The paired E-minus-S differences exclude zero in few cells, and which cells they are depends on the scope: in the four-condition scope E2 on MPDD TRI, E1 and E3 on BTAD TRI, and E2 and E3 on BTAD BAL; in the twelve-condition scope E2 on MPDD in both contrasts, E3 on MPDD TRI, E1 on BTAD TRI and E2 on BTAD BAL. We therefore read the extra encoders as a transfer check whose ordering is scope-sensitive, not as a ranking of encoders.

Single-branch sanity is verified for all three additional encoders, each with forty-eight stored single-branch units and a passing single-branch gate. E1 spans pixel AUROC 0.916 to 0.992 with a mean of 0.967, E2 spans 0.887 to 0.984 with a mean of 0.953, and E3 spans 0.906 to 0.998 with a mean of 0.952. These units cover the MPDD study revision and the corrected BTAD revision, so the interaction estimates do not rest on fused-construction rows alone.

A separate extension varies the support set rather than the encoder. Eight seeds were run, of which seeds 0 to 2 keep their own query encodings and seeds 3 to 7 share a single query block, so the latter isolate the support-set contribution; the same test images are scored under every seed and only the normal references change. Table 17 summarizes the per-seed interaction, and Figure 5(b) draws the same series.

Table 17. Descriptive variation across eight support seeds.

| Series | Mean point | SD across seeds | Same sign at every seed | Seeds excluding zero (95%) | Support / test uncertainty |
| --- | --- | --- | --- | --- | --- |
| MPDD $I_{TRI}$ | +0.679 | 0.221 | Yes | 7 of 8 | 0.48 |
| MPDD $I_{BAL}$ | +0.548 | 0.159 | Yes | 6 of 8 | 0.37 |
| BTAD $I_{TRI}$ | +0.125 | 0.136 | No | 3 of 8 | 0.68 |
| BTAD $I_{BAL}$ | +0.036 | 0.129 | No | 0 of 8 | 0.65 |

AP percentage points. Seeds 0–2 retain separate query encodings; seeds 3–7 share a query block and vary the support set alone. The final column is the between-seed standard deviation divided by the median bootstrap half-width. Values are descriptive, use canonical BTAD masks, and do not replace the corrected-geometry primary analysis. Figure 5(b) shows the same per-seed series.

The seed-level series reproduce the stored dataset-macro summaries to numerical precision. MPDD retains positive interaction points at every seed, whereas BTAD changes sign. This variation describes sensitivity to the observed supports and complements the conditional image-bootstrap intervals; it is not an additional independent replication.

#### 4.2.12 Correspondence Sensitivity

Geometric alignment in this study is a deterministic canvas correspondence, not a learned or verified part-level correspondence. We therefore replaced the correspondence between the B and the C rows in four ways on MPDD, using six categories, seeds 0 and 1, $K$ equal to 1 and 4, four support conditions and the study's shared bootstrap stream: the canvas rule itself; a closed-form orthogonal Procrustes map fitted on the support rows and applied to the query and reference rows alike; a position permutation of the C rows, identical for queries and references; and a Sinkhorn optimal-transport correspondence whose cost matrix is the cross-branch cosine distance of the support descriptors, with its entropy regularizer fixed a priori at 0.1 times the interquartile range of that matrix. The transport rule mixes each C row over several canvas positions instead of relabeling it. We also report the exact assignment obtained from the same cost matrix as the regularizer tends to zero.

Table 18. The same interaction under five correspondence conventions on MPDD.

| Correspondence | $I_{TRI}$ point | $I_{TRI}$ 98.75% | $I_{BAL}$ point | $I_{BAL}$ 98.75% |
| --- | --- | --- | --- | --- |
| Canvas rule (identity) | +0.767 | [+0.193, +1.160] | +0.547 | [+0.078, +0.962] |
| Procrustes (orthogonal) | +0.767 | [+0.193, +1.160] | +0.547 | [+0.078, +0.962] |
| Position permutation | +0.799 | [+0.273, +1.283] | +0.813 | [+0.310, +1.480] |
| OT, exact assignment | +0.834 | [+0.207, +1.274] | +0.910 | [+0.327, +1.462] |
| OT, soft mixing | +0.591 | [+0.191, +1.077] | +0.570 | [+0.043, +0.971] |

AP percentage points; six MPDD categories, seeds 0 and 1, K = 1 and 4, four support conditions, 1000 paired replicates, the same bootstrap stream for every row. Intervals use a four-comparison adjustment within each setting across two datasets and two contrasts, not a simultaneous guarantee over all settings; the 98.75% bounds, and are percentile bounds of the image-level bootstrap series, formed inside each replicate and aggregated over categories and support conditions before the percentile is taken. The exact assignment is the limit of the transport rule as its regulariser tends to zero and uses the same cost matrix; the soft-mixing row fixes that regulariser a priori at 0.1 times the interquartile range of the support cost matrix. The canvas row reproduces the S branch's MPDD interaction of Table 16 - its replicate mean is +0.695 with the same interval - and the point column of this table differs from that row only because it reports the condition-averaged difference rather than the replicate mean. On BTAD this harness scores through its own path, so its numbers belong to that chain and are not mixed with the D, E1 or E2 rows.

Table 19. Sensitivity to the transport regularizer on MPDD and BTAD.

| Setting | MPDD $I_{TRI}$ | MPDD $I_{BAL}$ | BTAD $I_{TRI}$ | BTAD $I_{BAL}$ |
| --- | --- | --- | --- | --- |
| OT, exact assignment (regulariser 0) | +0.834 [+0.207, +1.274] | +0.910 [+0.327, +1.462] | +0.220 [−0.044, +0.660] | +0.148 [−0.181, +0.699] |
| OT, regulariser 0.05 IQR | +0.580 [+0.169, +1.007] | +0.624 [+0.006, +1.037] | +0.162 [−0.080, +0.554] | +0.156 [−0.151, +0.653] |
| OT, regulariser 0.10 IQR (prescribed) | +0.591 [+0.191, +1.077] | +0.570 [+0.043, +0.971] | +0.115 [−0.109, +0.465] | +0.103 [−0.156, +0.561] |
| OT, regulariser 0.50 IQR | +0.725 [+0.327, +1.165] | +0.751 [+0.253, +1.151] | +0.061 [−0.124, +0.363] | +0.025 [−0.170, +0.353] |

Observed condition means and 98.75% paired image-bootstrap intervals in AP percentage points. Seeds 0, 1; K = 1, 4; 1000 replicates; stride-eight pixels. Each setting has a separate four-comparison adjustment across two datasets and two contrasts. No adjustment covers the whole sweep. IQR is the interquartile range of support costs. BTAD uses the separate correspondence implementation.

Across the seven settings, the canvas rule, Procrustes, the permutation and four regularizer values including the exact assignment, all fourteen point estimates are positive and all fourteen MPDD 98.75% intervals exclude zero. Each setting has a four-comparison adjustment, without a simultaneous guarantee across the full sweep. Exact assignment gives the largest observed point estimates among these settings, and the only cell whose lower bound sits close to zero is the intermediate 0.05 regularizer value on $I_{BAL}$, at +0.006 points.

Two properties of the transport rule belong with this table. The soft mixing also changes the multiset of the C descriptors, since each row becomes a weighted combination of roughly 15 to 40 canvas positions, with a median row-maximum weight of 0.044, whereas a position permutation and exact assignment preserve the descriptor multiset. An orthogonal Procrustes map changes the descriptor values but preserves within-branch distances when applied consistently to queries and references. The sweep is nonetheless reported in full rather than summarized by its prescribed regularizer, so that a reader can see that neither the sign nor the interval separation of the interaction depends on that constant. Table 19 gives the transport sweep for MPDD and BTAD. The separate encoder-scope comparison remains in Table 16.

The transport plans themselves carry almost no canvas-position information: the median diagonal mass is 0.000949 against a chance value of 0.000977, and the fitted Procrustes map sits at a Frobenius distance of about 39 from the identity, so neither solves a position-level correspondence. We also record the verification of the new variant: it recovers a known synthetic assignment exactly, it reproduces the stored patch scores when the plan is forced to the identity with a maximum absolute difference of 6.4e-07, and the three earlier variants reproduce to at most 1.8e-06 once the new code path is present. The intervals in this table are percentile bounds of the image-level bootstrap series, formed inside each replicate and aggregated over categories and conditions before the percentile is taken, which is the convention of the primary tables. On MPDD the canvas row reproduces the S branch's interaction of Table 16 under that convention: its replicate mean is +0.695 against +0.695 and its interval [+0.193, +1.160] is the same, the two agreeing to 2.4e-07 in the bounds, so the 0.07-point gap between the point column of Table 18 and the S row of Table 16 is the difference between the condition-averaged difference and the replicate mean rather than a difference between scoring chains. On BTAD this harness still scores through its own path, and its BTAD numbers must not be mixed with the D, E1 or E2 numbers.

On BTAD all four variants were run, together with the same sweep over four regularizer values. No interval excludes zero for either contrast: the canvas rule gives +0.001 points [−0.183, +0.299] for $I_{TRI}$ and −0.080 [−0.270, +0.226] for $I_{BAL}$, Procrustes gives +0.001 [−0.183, +0.299] and −0.080 [−0.270, +0.226], the position permutation gives +0.234 [−0.058, +0.715] and +0.217 [−0.112, +0.773], and the soft mixing at the prescribed regularizer gives +0.115 [−0.109, +0.465] and +0.103 [−0.156, +0.561]. The regularizer sweep spans the same range: the exact assignment gives +0.220 [−0.044, +0.660] and +0.148 [−0.181, +0.699], the intermediate 0.05 value gives +0.162 [−0.080, +0.554] and +0.156 [−0.151, +0.653], and the widest mixing at 0.5 gives +0.061 [−0.124, +0.363] and +0.025 [−0.170, +0.353]. All fourteen intervals span zero, so on this dataset neither replacing the correspondence nor changing the amount of smoothing in the transport rule changes the judgement, which was already "no evidence of a direction".

#### 4.2.13 Geometry and Shared-Operation Sensitivity

Three further checks close gaps recorded in Section 4.2.8 without changing the primary conclusions.

The corrected BTAD category-03 geometry was recomputed on a finer stride-four evaluation grid covering all three categories. The reproduction check against the study revision passes on four cells with a maximum absolute difference of 7.0e-08, and the nested-support check records no violation in sixteen tests. The resulting bootstrap means and 98.75% intervals are −0.011 points [−0.224, +0.251] for $I_{TRI}$ and −0.085 [−0.296, +0.177] for $I_{BAL}$; neither excludes zero, so the coarser stride-eight reading of Section 4.2.4 is unchanged at the finer grid. Figure S3 collects the supporting geometry panels and the eight per-image cases.

The eight-seed extension of Section 4.2.11 pools all three BTAD categories, including 03, under the canonical-mask convention, a 448 by 588 mask on the 32 by 42 grid that was verified on disk. That is not the corrected-geometry convention used for the primary BTAD tables, so the two sets of numbers should not be quoted interchangeably; the batch is descriptive in any case, even though its reproduction gate now passes at the dataset macro level.

E3 places a third backbone family in the extra slot: a window-attention hierarchical transformer whose two retained stages match the strides and the channel split of the D branch, giving a 576-dimensional descriptor on the B canvas. Its interactions appear in Table 16, and like E1 and E2 it was selected after the S and D results were known. Figure S2 reports the exploratory ablations of shared operations, at seed 0 with $K$ equal to 1; because that scope is a single condition with one run per ablation, the panel is exploratory, carries no interval, and is not evidence that any shared operation has been validated.

Figures S1–S5 provide method geometry, exploratory ablation, additional cases, bootstrap stability and synchronized resource measurements. The accompanying deck also contains the complete category-level multi-method case set.


#### 4.2.14 Timed Inference Stages and GPU Allocation

The new benchmark supplements the historical stage records with a common measurement procedure for all six configurations (Table 20 and Figure S5). Its scope is deliberately restricted to the three MPDD bracket categories at seed 0 and $K$ equal to 1 and 4. Each of the six category–budget units has one warm-up and three timed repeats, yielding 144 successful runs including warm-ups and no failures in the final measurement file. The 216 unique query images are visited twice across the two budgets. Reference preparation is included, so dividing the total by 432 would not yield query-only latency.

For each repeat, recorded stage times are summed over all six units; the table reports the median and observed range of the three resulting totals. A1 J and A1 L require 197.118 and 195.300 seconds, respectively, whereas the tested AnomalyDINO and PatchCore configurations range from 24.190 to 78.863 seconds. A1 therefore has a substantial encoding cost in this scope; the small J–L timing difference does not support a general speed advantage. Its median allocated peak is 2376.8 MiB with both B and C resident, compared with 111.6 MiB for AnomalyDINO and approximately 403–410 MiB for PatchCore. These measurements document the cost of the tested implementations rather than a universally optimized hardware ranking.

The timer covers measured preprocessing, encoding and scoring stages, including support-bank work. It excludes model and dataset setup, metric evaluation and output-file writes. For A1 and AnomalyDINO, the reported total is the sum of stage timers; for PatchCore, it is fit plus predict, with scoring represented by the residual after preprocessing and encoding. No independent complete-process wall-clock measurement or query-only latency distribution is available. The methods retain different native resolutions and preprocessing, so common instrumentation does not make their workloads identical. Allocated-memory peaks are process-local PyTorch measurements in MiB. The archived 1 Hz device-wide nvidia-smi increases are separate observations affected by the device baseline and other activity; they are not substituted for these process peaks.

Table 20. Timed-stage sums and allocated GPU peaks on the restricted MPDD benchmark.

| Configuration | Median time (s) | Time range (s) | Peak allocation (MiB) |
| --- | --- | --- | --- |
| A1 J | 197.118 | 196.823–197.424 | 2376.8 |
| A1 L | 195.300 | 195.162–195.491 | 2376.8 |
| AnomalyDINO | 30.959 | 30.871–36.532 | 111.6 |
| AnomalyDINO + rotation | 78.863 | 78.794–79.012 | 111.6 |
| PatchCore 128 | 24.190 | 24.080–24.331 | 403.1 |
| PatchCore 224 | 36.931 | 36.557–37.162 | 409.8 |

Time: median and observed min–max across three repeat-level sums of six units. Memory: median of 18 timed unit peaks. Seed 0; K = 1, 4; three MPDD categories; one warm-up per unit. Timing boundaries and native-protocol differences are specified in Section 4.2.14 and Figure S5. Bold marks the study anchors, not the fastest or best result.

#### 4.2.15 Stability of Bootstrap Estimates

Because the pipeline uses frozen encoders and no target-domain optimizer, a training loss or epoch-convergence curve is not defined. Figure S4 instead examines numerical stability of the stored bootstrap estimator by successively taking prefixes of each 1000-replicate array. Across the ten dataset–contrast series and the displayed prefixes of at least 500 replicates, the largest deviation from the final mean is approximately 0.00013 pixel AP and the largest relative interval-width deviation is 6.8%. At prefixes of at least 200, the latter can still reach 17.1%. These observations support the numerical stability of the reported 1000-replicate summaries on the tested prefixes; they do not establish model convergence or remove sampling uncertainty. The plotted intervals are individual 95% intervals, while the adjusted inferential families remain those specified for the respective primary, generalization and confirmation analyses.



## 5 Conclusion

This study separates the value of additional frozen visual representations from reweighting and normal-reference selection in few-shot industrial anomaly localization. Exact duplication and complementary fixed-weight replacements make the representation change explicit. Crossing these controls with joint and independent matching reveals whether its value depends on sharing a normal reference, beyond any absolute gain from the added encoder.

The results demonstrate why this distinction matters. DINOv2-S shows positive matching interactions on MPDD, MVTec AD and VisA, while its interaction direction remains unresolved on BTAD despite positive absolute representation effects. WideResNet50-2 yields positive interactions on both primary datasets, and the separately specified KolektorSDD2 confirmation meets all four directional criteria. Encoder and support-set analyses identify substantial variation; correspondence transformations preserve positive MPDD interactions within the tested settings, while BTAD interval directions remain unresolved.

The resulting design guidance is to evaluate representation composition and reference selection together under explicit weight controls. Its scope remains conditional on the tested encoders, support sets and dataset provenance. Future work should extend prospective comparisons to additional production settings, test correspondence effects under broader prospective conditions, and evaluate calibrated thresholds and deployment costs across more datasets and operating conditions. These steps would connect the controlled attribution of fusion gains to practical inspection decisions.

## Data and Code Availability

MPDD, BTAD, MVTec AD, VisA and KolektorSDD2 are distributed by their respective providers [1, 2, 3, 4, 33]. The local study archive retains support manifests, feature specifications, geometry revisions, prediction caches, per-condition metrics, bootstrap outputs and analysis scripts. A local reproduction package includes the analysis entry points, dependency records, support manifests and figure bindings. Raw datasets and feature caches remain separate.

Licensing is split three ways. The code is released under the MIT Licence (repository root `LICENSE`, Copyright (c) 2026 LiYuening). The derived artefacts released with the package - derived tables, figures and the manuscript sources - carry the same licence as the code; any item that the root `LICENSE` does not explicitly cover remains for the authors to confirm. Dataset licences are separate and are not covered by the code licence, and the datasets themselves are not redistributed here. The public repository holding the code and the reproduction materials is https://github.com/USEU117/reference-matching-interaction-ad; a permanent archive DOI for the complete study has not yet been established.

Funding: [[FUNDING]]. Competing interests: The authors declare no competing interests. Ethics: Not applicable; the study analyses industrial image data only, with no human or animal subjects.

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


## Supplementary Method Figures

![Figure S1 part 1](docs/paper_complete_review_20260920/figures/figS1_encoders.png)

Figure S1. Frozen encoder branches and their shared scoring path. (a) B and S are DINOv2-B and DINOv2-S; C is the AnomalyCLIP visual branch; D concatenates WRN50-2 layer2 and layer3. The 448-pixel square input and 32 by 32 grid illustrate the square primary canvas; the BTAD-03 canvas is 32 by 42, and KSDD2 uses its separately specified geometry. (b) E1 is original DINO ViT-S/8, E2 ConvNeXt-Tiny and E3 Swin-Tiny; these substitutions were selected after S and D and are exploratory. (c) Bilinear mapping to the B grid with align_corners = False and per-position unit normalization define the common distance path. Encoders, weights and reference identities remain frozen; no target training, coreset, PCA or weight search is introduced.

## Supplementary Results Figures

![Figure S2 part 1](docs/paper_complete_review_20260920/figures/figS2_shared_op_ablation.png)

Figure S2. Exploratory shared-operation ablations. (a) The interaction under each ablation, shown as dataset means. (b) The absolute mean pixel AP that the same ablations move, over the four constructions under the joint rule. The operations every construction shares are removed one at a time: ABL-S drops the Gaussian smoothing of the patch scores, ABL-N drops the per-branch normalization and scores with squared Euclidean distance, and ABL-C replaces score-level fusion with naive concatenation, which can move only the BAL contrast because the coefficients equal the weights for equal slots. The scope is a single condition, seed 0 with K = 1, and one run per ablation, so no interval exists and none is drawn; the panel is therefore exploratory and does not show that a shared operation has been validated.

![Figure S3 part 1](docs/paper_complete_review_20260920/figures/panel_c_to_b_shift.png)

Figure S3. Supporting geometry audit. Approximate minus coordinate-corrected C-grid positions for BTAD category 03 and the square MPDD bracket-black example. The non-square canvas introduces a horizontal displacement; the square example has zero displacement. These are coordinate diagnostics, not additional performance measurements.

![Figure S3 part 2](docs/paper_complete_review_20260920/figures/panel_canvas_coverage.png)

Figure S3 continued. The B/S (DINOv2-B / DINOv2-S) canvas and PatchCore-224 center crop in original image coordinates for the same two geometry examples. Rectangles are computed from the frozen preprocessing transforms.

![Figure S3 part 3](docs/paper_complete_review_20260920/figures/panel_interaction_cases.png)

Figure S3 continued. Two of the eight frozen per-image interaction cases at seed 0 and K = 4. The original query, ground-truth display and four contrast maps are shown in aligned columns. The four raw patch-score maps in each row use one shared color range; they illustrate the contrast before final smoothing. The displayed interaction is in AP units, not percentage points. Cases are selected extremes and do not estimate population performance.

![Figure S3 part 4](docs/paper_complete_review_20260920/figures/panel_interaction_cases_p2.png)

Figure S3 continued. Two of the eight frozen per-image interaction cases at seed 0 and K = 4. The original query, ground-truth display and four contrast maps are shown in aligned columns. The four raw patch-score maps in each row use one shared color range; they illustrate the contrast before final smoothing. The displayed interaction is in AP units, not percentage points. Cases are selected extremes and do not estimate population performance.

![Figure S3 part 5](docs/paper_complete_review_20260920/figures/panel_interaction_cases_p3.png)

Figure S3 continued. Two of the eight frozen per-image interaction cases at seed 0 and K = 4. The original query, ground-truth display and four contrast maps are shown in aligned columns. The four raw patch-score maps in each row use one shared color range; they illustrate the contrast before final smoothing. The displayed interaction is in AP units, not percentage points. Cases are selected extremes and do not estimate population performance.

![Figure S3 part 6](docs/paper_complete_review_20260920/figures/panel_interaction_cases_p4.png)

Figure S3 continued. Two of the eight frozen per-image interaction cases at seed 0 and K = 4. The original query, ground-truth display and four contrast maps are shown in aligned columns. The four raw patch-score maps in each row use one shared color range; they illustrate the contrast before final smoothing. The displayed interaction is in AP units, not percentage points. Cases are selected extremes and do not estimate population performance.

![Figure S4 part 1](docs/paper_complete_review_20260920/figures/figS4_bootstrap_convergence.png)

Figure S4. Numerical stability of stored bootstrap estimates, not training convergence. Prefixes of 50, 100, 200, 300, 400, 500, 600, 700, 800, 900 and 1000 stored replicates are reused without new draws, and the same frozen arrays underlie both pages. (a) Change of each prefix estimate from its 1000-replicate value, in 10^-3 pixel AP, for the ten dataset-contrast series; the grey band marks the measured N >= 200 bound and the dotted line the recommended N = 1000. (b) Width of each individual 95% percentile interval relative to its width at 1000 replicates for the same ten series; the shaded grey band is a fixed reference band of 5% either side, not a pre-specified pass criterion, the dashed vertical line marks N = 500 and the dotted line the recommended N = 1000. The measured largest relative width deviation on prefixes of at least 500 replicates is 6.8%, and on the plotted grid every series stays inside that fixed reference band only from N = 700. MPDD is development, BTAD holdout, MVTec AD external frozen validation, VisA in-domain validation, and KSDD2 separate confirmation; these roles and their inferential families are not pooled. This diagnostic concerns Monte Carlo stability conditional on the stored data, not adequacy of sampling or model training.

![Figure S4 part 2](docs/paper_complete_review_20260920/figures/figS4_bootstrap_stability.png)

Figure S4 continued. The same stored prefixes shown at their absolute scale: prefix means and individual 95% percentile intervals of the two interaction contrasts, in 10^-3 pixel AP. On the displayed prefixes of at least 500 replicates the largest mean deviation from the 1000-replicate value is approximately 0.00013 pixel AP and the largest relative interval-width deviation is 6.8%, while at prefixes of at least 200 the latter can still reach 17.1%. These are individual 95% intervals and do not replace the multiplicity-adjusted intervals used for the principal conclusions.

![Figure S5 part 1](docs/paper_complete_review_20260920/figures/figS5_speed_vram.png)

Figure S5. Timed inference stages and in-process GPU allocation on three MPDD categories (bracket_black, bracket_brown and bracket_white), seed 0 and K = 1, 4: six units, 216 unique queries and 432 query visits. One warm-up and three timed repeats are run per unit. (a) Bars stack the medians of repeat-level stage sums across six units; circles and whiskers show the median and observed min–max of their total across three repeats, not confidence intervals. Stage medians need not sum exactly to the median total. (b) Bars show the median PyTorch allocated-memory peak across 18 timed unit runs, with observed min–max. MiB denotes 2^20 bytes. A1 (dual-encoder anchor) holds B (DINOv2-B) and C (AnomalyCLIP visual) in the same process. ADino denotes AnomalyDINO, rot. reference rotation, and PC PatchCore at the indicated native input resolution. All six configurations use the same instrumentation, but retain their native preprocessing and model protocols. Timing includes reference/query preprocessing, encoding and scoring; model loading, dataset setup, metric evaluation and result writes are excluded. PatchCore score time is the fit-plus-predict residual after measured preprocessing and encoding. These are timed-stage sums, not independently timed complete-process wall-clock or query-only latency.

The accompanying figure deck includes the complete set of 36 category-level comparisons with the native methods, using the same shared-region evaluation as Table 11. These selected examples supplement the aggregate results; they are not an independently sampled performance estimate. Their source records preserve the sample identities, per-image AP and common-region geometry.
