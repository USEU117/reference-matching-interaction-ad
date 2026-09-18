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

The direct S interactions on MPDD are +0.772 points for TRI and +0.595 for BAL (Table 7). Their adjusted 98.75% intervals are [+0.346, +1.211] and [+0.189, +1.030], respectively. Both exclude zero. Their point estimates exceed the descriptive 0.5-point scale, but their interval lower bounds do not, so the data do not establish an effect uniformly above that practical reference magnitude. Figure 4(c) places these two interactions on the same axis as the later D extension.

{{table:s_interaction}}

On BTAD, the S interactions are −0.050 and −0.119 points, with both adjusted intervals spanning zero. The small negative points are not evidence of a general advantage for joint matching. Combined with Table 6, the result is that S has positive representation effects under the tested rules while the current data do not clearly resolve a difference between those effects. This is distinct from saying that matching is irrelevant or that the two rules are equivalent.

The prespecified D extension provides a second representation condition. Table 8 reports its full-pixel localization results under the restricted four-condition scope. On MPDD, TRI D L reaches AP 0.4107 compared with 0.3554 for DUP L; on BTAD, it reaches 0.6591 compared with 0.6335. The corresponding full-pixel representation effects are approximately +5.53 and +2.57 AP percentage points. These are absolute representation effects, not the much smaller interaction estimates. D alone has lower pixel AP than these fused constructions, showing that the fusion result cannot be explained simply by selecting D's standalone score. Figure 4(b) shows the four D effects that this scope supports.

{{table:d_full}}

All four D interactions are positive, with adjusted intervals excluding zero (Table 9): +0.974 and +0.628 points on MPDD, and +0.622 and +0.501 on BTAD. The full-pixel points retain these directions. This establishes that a positive interaction in the observed setting is not confined to adding a smaller DINOv2 encoder. It does not establish the same result for arbitrary convolutional backbones or for additional datasets.

{{table:d_interaction}}

A comparison between Figures 4(a) and 4(b) would confound the encoder with support-condition coverage. Table 10 instead restricts S to the D seeds and budgets and directly estimates the D-minus-S interaction difference. The observed differences on BTAD are +0.623 and +0.585 points, with adjusted intervals [+0.255, +0.945] and [+0.204, +1.060]. On MPDD, the observed differences are +0.207 and +0.081, and the intervals span zero. The bootstrap means differ from the observed points, particularly on MPDD, and are shown in a separate column rather than being mislabeled as point estimates.

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

The interpretation remains limited in several ways. First, the primary interaction was formulated after earlier project exploration, and the datasets are not untouched confirmation sets. Second, the bootstrap conditions on the observed categories and fixed support manifests; its intervals do not characterize arbitrary future support choices. Third, only one prespecified heterogeneous encoder was added, with a smaller seed and budget scope than the S study. Fourth, full-pixel intervals and complete deployment resource measurements remain unavailable. Fifth, qualitative cases are selected extremes, and their Otsu contours are display choices rather than calibrated defect masks. Sixth, the operations that every construction shares, namely spatial mapping, branch normalization and scoring from concatenated descriptors, are held fixed rather than ablated, so this study does not quantify how much each of them contributes and does not present them as validated modules. Finally, the geometric alignment is deterministic canvas correspondence, not a learned guarantee that receptive fields describe exactly the same object part.

These limitations do not turn a negative or uncertain interaction into a failed experiment. BTAD with S separates positive representation value from uncertain matching dependence, while the D comparison provides an encoder-specific difference under matched conditions. The study's contribution is this controlled and qualified account. A future learned selector, foreground filter, or dynamic fusion module would require its own implementation and evidence; none is implied by the present results.
