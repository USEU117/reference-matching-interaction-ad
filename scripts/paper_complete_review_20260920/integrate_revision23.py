"""Synchronize manuscript figure metadata with the 23 September editorial revision."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
SRC=Path(__file__).resolve().parent
FIG='docs/paper_complete_review_20260920/figures/'
f=json.loads((SRC/'figures.json').read_text(encoding='utf-8'))
original=f['cases_bad']['path']
selected=[('mpdd','metal_plate','MPDD metal plates with scratches'),
          ('mvtec','grid','MVTec AD grid textures with glue defects'),
          ('visa','pcb1','VisA printed circuit boards')]
f['cases_bad']['parts']=[original]+[FIG+f'multimethod/fig7_multimethod_{d}_s0_k4_{c}.png' for d,c,_ in selected]
f['cases_bad']['caption']='Two selected MPDD degradations under the A1 comparison and display protocol of Figure 6. Lower raw scores under independent matching do not guarantee improved pixel ordering or a complete contour. These cases illustrate matching behaviour at the anchor, rather than the representation interaction. Only these two cases and the three Figure 6 cases include the thresholded L contour; the continuation pages and category appendix compare continuous maps.'
f['cases_bad']['part_captions']=[f['cases_bad']['caption']]+[
    'Figure 7 continued. '+description+'. Six configurations share the original-image common valid region of Table 11 at seed 0 and K = 4. Query and GT are followed immediately by the two A1 columns, then AnomalyDINO without/with reference rotation and the local 128-pixel/official 224-pixel PatchCore configurations. P-AP denotes per-image pixel AP, not category-pooled AP. Each row uses a shared score range across all six maps. Categories were selected to illustrate distinct surface, texture and circuit examples; within each category the three archived samples have the largest AP spread across configurations, with ties broken by sample identity. These selected extremes show contrasting responses, not representative performance or a method ranking. No method-specific thresholded contours are supplied on this page.'
    for _,_,description in selected]
f['protocol_sensitivity']={
    'label':'S6','width':17,
    'path':FIG+'figS6_protocol_paper_part1.png',
    'parts':[FIG+f'figS6_protocol_paper_part{i}.png' for i in [1,2]],
    'caption':'Sensitivity of the external-method context to the evaluated configuration. Each point is a dataset macro pixel AP from Table 12. Connectors link A1 joint/independent matching, AnomalyDINO without/with reference rotation, and the two PatchCore configurations. Eight configurations average seeds 0 and 1 with K = 1 and 4; AnomalyCLIP has one support-free evaluation and is not paired with those four conditions. SubspaceAD uses the local 256-pixel fp16 setting. Fixed family grouping is not a performance ordering. These native or documented local configurations retain different input geometries and implementations. Lines describe configuration changes; no confidence interval or cross-method significance test is shown. The harmonised 448-pixel subset is reported separately in Table S1.',
    'continuation_caption':'Figure S6 continued. MVTec AD and VisA under the same conventions. Values reuse the frozen external comparison summaries; no prediction or evaluation was rerun. Dataset roles remain those of the study, with VisA conservatively retained as in-domain. Table S1 covers only the five configurations compatible with its shared geometry at seed 0 and K = 1, not all methods plotted here.'
}
(SRC/'figures.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Figure 7: four pages; S6: two pages. Existing figure numbers preserved.')
