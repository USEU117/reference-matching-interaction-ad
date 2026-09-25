"""Read existing metrics only; build the three additional manuscript tables."""
from pathlib import Path
import csv, json, hashlib, statistics

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXP = ROOT / 'experiments/dynamic_fusion'
sources = []
def read(path):
    sources.append({'path':path.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

rows = read(EXP/'unified_fusion_paper_support_20260913/p1_matrix/metrics_all_units.csv')
rows += read(EXP/'generalization_mvtec_visa_20260915/p1_matrix/metrics_all_units.csv')
base = EXP/'representation_matching_interaction_20260914'
for seed in (0,1):
    for shot in (1,4):
        for category in ('01','02','03'):
            for r in read(base/f'04_new_encoder/units/btad_s{seed}_k{shot}/{category}__corrected/metrics.csv'):
                rows.append(dict(r,dataset='btad',seed=str(seed),shot=str(shot),category=category))
names={'mpdd':'MPDD','btad':'BTAD','mvtec':'MVTec AD','visa':'VisA'}
counts={'mpdd':6,'btad':3,'mvtec':15,'visa':12}
metrics=['image_auroc','image_ap','pixel_auroc','pixel_ap']
image_rows=[]
for dataset in names:
    for method in ('A1_J','A1_L'):
        selected=[r for r in rows if r['dataset']==dataset and r['method']==method and int(r['seed']) in (0,1) and int(r['shot']) in (1,4)]
        assert len(selected)==4*counts[dataset], (dataset,method,len(selected))
        assert len({(r['seed'],r['shot'],r['category']) for r in selected})==len(selected)
        means=[]
        for metric in metrics:
            means.append(statistics.mean(statistics.mean(float(r[metric]) for r in selected if int(r['seed'])==seed and int(r['shot'])==shot) for seed in (0,1) for shot in (1,4)))
        image_rows.append([names[dataset],'Dual-encoder baseline — '+('joint matching' if method=='A1_J' else 'independent matching')]+[f'{v:.4f}' for v in means])

tables=json.loads((HERE/'tables.json').read_text(encoding='utf-8'))
previous_layouts={k:tables.get(k,{}) for k in ('image_metrics','harmonised','method_protocols')}
tables['image_metrics']={
 'caption':'Image-level and pixel-level point estimates for the dual-encoder anchors under matched support conditions.',
 'headers':['Dataset','Anchor','Image AUROC','Image AP','Pixel AUROC','Pixel AP'],
 'rows':image_rows,'widths':[3.0,2.0,3.0,3.0,3.0,3.0],'left_cols':[0,1], 'bold_rows':list(range(8)),
 'note':'Seeds 0 and 1; K = 1 and 4; equal category means followed by equal condition means. Categories: MPDD 6, BTAD 3, MVTec AD 15, VisA 12. Pixel metrics use the retained output canvas at stride eight; BTAD uses corrected coordinates. These are current controlled-pipeline point estimates, not the common-original-region metrics of Tables 11 and 12. No image-level confidence interval is available. Bold identifies the study anchors, not statistically optimal results.'}
harm=read(base/'05_baselines_harmonised_20260922/harmonised_macro.csv')
labels={'controlled_A1_J':'Dual-encoder baseline / Joint matching','controlled_A1_L':'Dual-encoder baseline / Independent matching','anomalydino_canvas':'AnomalyDINO','anomalydino_canvas_rotation':'AnomalyDINO + rotation','PatchCore_harmonised448':'PatchCore 448'}
assert set(r['method'] for r in harm)==set(labels),set(r['method'] for r in harm)
harmrows=[]
for dataset in names:
    for method,label in labels.items():
        r=next(r for r in harm if r['dataset']==dataset and r['method']==method)
        harmrows.append([names[dataset],label,f"{float(r['macro_pixel_ap']):.4f}",f"{float(r['macro_pixel_auroc']):.4f}",f"[{float(r['interval_pixel_ap_lo']):.4f}, {float(r['interval_pixel_ap_hi']):.4f}]"])
tables['harmonised']={
 'label':'S1','caption':'Restricted harmonised-geometry comparison at seed 0 and K = 1.',
 'headers':['Dataset','Configuration','Pixel AP','Pixel AUROC','95% AP interval'],
 'rows':harmrows,'widths':[2.5,5,2.5,2.5,4.5],'left_cols':[0,1], 'bold_rows':[i for i,r in enumerate(harmrows) if r[1].startswith('Dual-encoder baseline')],
 'note':'Short side 448; frozen common valid region and the same rank-based pooling. This covers 36 of the 144 category-condition units. PatchCore 448 was recomputed; the other four configurations reuse compatible predictions. Additional crops may be required to respect the frozen intersection. SubspaceAD, WinCLIP+ and zero-shot AnomalyCLIP are excluded because their square-stretch input paths are outside this subset. Points use full-grid common-region pixels; intervals use stride-eight pixels and 1000 image-bootstrap replicates. Intervals apply only to pixel AP, are individual marginal 95% intervals, and are neither family-adjusted nor paired cross-method difference intervals. Pixel AUROC has point values only. This is not a ranking or a significance comparison. Bold identifies the study anchors, not optimal results; Tables 11 and 12 remain unchanged.'}
protocols=[
 ['Dual-encoder baseline / Joint matching','DINOv2-B/14: short side 448; AnomalyCLIP visual: square 518, mapped to the DINOv2 grid','None','All normal support descriptors; shared neighbor across branches'],
 ['Dual-encoder baseline / Independent matching','Same as the baseline with joint matching','None','Same bank; independent branch neighbors'],
 ['AnomalyDINO','Short side 448; aspect-preserving canvas','None','Frozen DINOv2 patch memory'],
 ['AnomalyDINO + rotation','Same canvas','Support rotations','Rotated reference descriptors augment the patch memory'],
 ['PatchCore 128','Resize 144; center crop 128','None','Local compact memory/coreset configuration; 256-dimensional projected features'],
 ['PatchCore 224','Resize 256; center crop 224','None','Recorded upstream-style memory/coreset configuration; 1024-dimensional projected features'],
 ['SubspaceAD 256','Square stretch 256; fp16','None','Normal-support subspace; documented local setting'],
 ['WinCLIP+','Square stretch 240','No rotation','Frozen visual-language model, prompt ensemble and normal-reference features'],
 ['AnomalyCLIP zero-shot','Square stretch 518','No rotation','Auxiliary-domain-trained prompt learner; no target support bank']]
tables['method_protocols']={
 'label':'S2','caption':'Input and reference protocols of the configurations in Tables 11 and 12.',
 'headers':['Configuration','Input geometry','Augmentation','Reference construction / scoring'],
 'rows':protocols,'widths':[3.4,4.7,2.5,6.4],'left_cols':[0,1,2,3],'bold_rows':[0,1],
 'note':'These are the evaluated configurations, not interchangeable official recipes. SubspaceAD uses 256-pixel fp16 inputs without augmentation; its upstream few-shot script specifies 672 pixels and aug_count = 30. On the recorded 6 GB GPU, the 672-pixel attempt did not complete 12 query images in at least 15 minutes and reached 5797/6144 MiB. The local 256 setting is therefore explicitly a deviation. AnomalyCLIP uses inherited auxiliary-domain-trained prompt checkpoints, with MVTec-trained prompts for MPDD, BTAD and VisA and VisA-trained prompts for MVTec AD; target-domain evaluation is zero-shot. It has 36 units rather than the 144 support-conditioned units of the other configurations. Encoders are frozen and no target-domain gradient optimization is used. Memory, coreset or subspace construction remains preparation computation. Bold marks the study anchors, not optimal results.'}
for key,old in previous_layouts.items():
    for field in ('widths','headers','left_cols','dedupe_cols'):
        if field in old:tables[key][field]=old[field]
(HERE/'tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'docs/paper_complete_review_20260920/additional_table_sources.json').write_text(json.dumps({'sources':sources,'aggregation':'Equal categories, then equal seed/shot conditions; existing metrics only','image_table_rows':image_rows},indent=2),encoding='utf-8')
print('Added Table 21, Table S1, Table S2')

