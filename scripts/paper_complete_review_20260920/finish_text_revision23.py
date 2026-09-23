from pathlib import Path
import json,re
HERE=Path(__file__).resolve().parent
m=(HERE/'manuscript.md').read_text(encoding='utf-8')
r=(HERE/'results.md').read_text(encoding='utf-8')
start=r.index('The harmonised-geometry table is a supplementary')
end=r.index('## 5 Discussion',start)
supp=r[start:end]
r=r[:start]+r[end:]
r=r.replace('{{figure:protocol_sensitivity}}','')
r=r.replace('**Supplementary image-level and protocol tables.** The image-level metrics table reports the available image AUROC and image AP point estimates alongside the pixel metrics.','**Image-level metrics.** Table 21 reports image AUROC and image AP alongside stride-eight pixel metrics for the two anchors on all four datasets, using the matched four conditions (seeds 0 and 1; K = 1 and 4).')
r=r.replace('{{table:image_metrics}}','{{table:image_metrics}}\n\nTable S1 gives the restricted harmonised-geometry subset, Table S2 records each evaluated input and reference protocol, and Figure S6 shows configuration sensitivity in the external-method context. These supplement the controlled attribution study; they do not define a cross-method ranking.')
m=m.replace('However, the inherited checkpoint still carries its training-data provenance, so removing text at inference does not turn an in-domain dataset into an unseen-domain test.','The export code loads a prompt-learner checkpoint but obtains these descriptors directly from the frozen visual encoder; the learned prompt is not called on this path and does not update its visual weights. We retain the historical in-domain designation for VisA conservatively, without attributing the C descriptors to prompt learning or claiming an untouched-domain test.')
m=m.replace('VisA is in-domain validation because the inherited AnomalyCLIP checkpoint was trained on VisA. This provenance applies even though inference uses only visual descriptors.','VisA remains in-domain frozen validation: a VisA-trained prompt checkpoint was loaded in the historical export setup, although the active visual-only path neither calls that prompt learner nor loads its weights into the visual encoder. VisA therefore does not provide unseen-domain evidence, and the loaded checkpoint is not evidence that it changes the C descriptors.')
m=m.replace('## Supplementary Method Figures','## Supplementary Protocol Tables\n\n'+supp+'## Supplementary Method Figures')
m=m.replace('{{figure:speed_vram}}','{{figure:speed_vram}}\n\n{{figure:protocol_sensitivity}}')
(HERE/'manuscript.md').write_text(m,encoding='utf-8')
(HERE/'results.md').write_text(r,encoding='utf-8')
t=json.loads((HERE/'tables.json').read_text(encoding='utf-8'))
for k,sp in t.items():
    # Table 11 freeze lifted by author decision (2026-09-23): its note may be extended
    # (the "not a ranking" and native-protocol qualifiers). Its six value columns and the
    # existing note wording are unchanged, and none of the substitutions below matches
    # that note, so it passes through this loop untouched.
    for field in ('note','caption'):
        if field in sp:
            sp[field]=sp[field].replace('Section 4.2.14','Section 4.2.4')
            if k=='four_dataset':sp[field]=sp[field].replace('Section 4.2.4','Section 4.2.1')
            sp[field]=sp[field].replace('VisA is in-domain for the inherited C checkpoint.','VisA retains the conservative in-domain role; the loaded prompt learner does not enter the visual-only C path (Section 4.1.1).')
(HERE/'tables.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=json.loads((HERE/'figures.json').read_text(encoding='utf-8'))
f['stability']['width']=17
f['stability']['caption']='Numerical stability of stored bootstrap estimates, not model training or an all-method stability comparison. The same prefixes of 50–1000 stored replicates underlie both pages; the prefixes are dependent and 1000 is a reference value, not a true parameter. (a) Change from the 1000-replicate estimate (10^-3 pixel AP); the grey band is the measured N >= 200 bound. (b) Individual 95% interval width relative to its 1000-replicate width. The fixed +/-5% reference band is not a prespecified pass criterion: the measured maximum deviation for N >= 500 is 6.8%, and every series remains inside the band only from N = 700 on this grid. KSDD2 is separate confirmation, outside the four-dataset family. These individual intervals do not replace the adjusted primary intervals.'
(HERE/'figures.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=HERE.parent/'figures_reference_matching_20260914/build_figS4_bootstrap_convergence.py'
s=p.read_text(encoding='utf-8').replace('height_in = 9.4','height_in = 7.5').replace('inches(5.00), 0.865, inches(2.95)','inches(4.05), 0.865, inches(2.35)').replace('inches(1.08), 0.865, inches(2.95)','inches(0.60), 0.865, inches(2.35)').replace('inches(9.05)','inches(7.25)')
p.write_text(s,encoding='utf-8')
