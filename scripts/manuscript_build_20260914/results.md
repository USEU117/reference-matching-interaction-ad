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

The four datasets do not behave alike, and we keep their readings separate instead of summarizing them as a replication. On MPDD both interactions are positive and exclude zero at the widest level reported here. On MVTec AD both are positive, with the narrowest intervals in the table, and they also exclude zero at the widest level; their point estimates, about +0.4 points, are the smallest of the three positive datasets. On VisA both are positive and the largest in the table, which is expected rather than independent evidence, because VisA is in-domain for the C branch: its frozen AnomalyCLIP checkpoint was trained on that dataset. On BTAD the point estimate is close to zero and both intervals span zero at all three levels, so the current data are insufficient to determine the direction of the interaction there; the point estimates are an order of magnitude smaller than those of the positive datasets, and the table must not be read as four consistent significant replications. This is not evidence of equivalence between the two rules; it means only that no direction is established there.

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
