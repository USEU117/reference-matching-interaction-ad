"""Re-layout archived six-configuration panels without recomputing predictions.

PDF image objects are extracted losslessly from the original complete archive.
Sample order, AP values and colour endpoints come from its adjacent JSON.  This
also prevents accidentally reusing an incomplete later export with n/a columns.
"""
from pathlib import Path
import hashlib, io, json, sys
import fitz
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[3]
ARCHIVE=ROOT/'docs/figures_reference_matching_20260914'
OUT=ROOT/'docs/paper_complete_review_20260920/figures/multimethod'
sys.path.insert(0,str(ROOT/'scripts/figures_reference_matching_20260914'))
from figure_font_gate import assert_min_font_pt,assert_no_text_text_overlap,assert_text_inside_page
plt.rcParams.update({'font.family':'Times New Roman','font.size':11.5,'pdf.fonttype':42})
HEADERS=['Query','Ground\ntruth','Baseline\nJoint\nmatching','Baseline\nIndependent\nmatching','Anomaly\nDINO','Anomaly\nDINO\n+ rotation','PatchCore\n128','PatchCore\n224']
W=17/2.54; DPI=350
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports=[]
for dataset in ['mpdd','btad','mvtec','visa']:
    source_json=ARCHIVE/f'fig7_multimethod_{dataset}_s0_k4.json'
    record=json.loads(source_json.read_text(encoding='utf-8'))
    assert not record['missing']
    for spec in record['figures']:
        assert len(spec['columns'])==6 and not spec['columns_na']
        source=ARCHIVE/(spec['name']+'.pdf')
        pdf=fitz.open(source); page=pdf[0]
        infos=[i for i in page.get_image_info(xrefs=True) if i['bbox'][2]-i['bbox'][0]<page.rect.width/3]
        groups=[]
        for item in sorted(infos,key=lambda i:(i['bbox'][1],i['bbox'][0])):
            if not groups or abs(item['bbox'][1]-groups[-1][0]['bbox'][1])>2:groups.append([])
            groups[-1].append(item)
        assert len(groups)==3 and all(len(g)==8 for g in groups),(source,[len(g) for g in groups])
        samples=sorted([s for s in record['samples'] if s['category']==spec['category']],key=lambda s:s['selection_rank'])
        assert len(samples)==3
        assert all(s['sample_id'] in page.get_text() for s in samples),source
        # One shared header serves all rows; this gives names room without shrinking.
        width_pt=W*72; margin=6; gap=4
        col=(width_pt-2*margin-7*gap)/8
        panel_h=min(76,col*spec['region_grid'][0]/spec['region_grid'][1])
        header_h=46; row_h=18+panel_h+14+6+15+7
        height_pt=header_h+3*row_h+3
        fig=plt.figure(figsize=(W,height_pt/72),dpi=DPI)
        def txt(x,y,s,**kw):return fig.text(x/width_pt,1-y/height_pt,s,fontsize=11.5,va='top',**kw)
        for c,label in enumerate(HEADERS):txt(margin+c*(col+gap)+col/2,2,label,ha='center',linespacing=1.0)
        panel_hashes=[]
        for ri,(group,sample) in enumerate(zip(groups,samples)):
            top=header_h+ri*row_h
            txt(margin,top,f"{dataset.upper()} · {sample['sample_id']}",ha='left')
            for ci,item in enumerate(sorted(group,key=lambda i:i['bbox'][0])):
                raw=pdf.extract_image(item['xref'])['image']; panel_hashes.append(hashlib.sha256(raw).hexdigest())
                arr=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))
                ax=fig.add_axes([(margin+ci*(col+gap))/width_pt,1-(top+18+panel_h)/height_pt,col/width_pt,panel_h/height_pt])
                ax.imshow(arr,interpolation='none',aspect='auto');ax.set_axis_off()
                if ci>=2:
                    value=sample['per_sample_pixel_ap_by_method'][spec['columns'][ci-2]]
                    assert value is not None
                    txt(margin+ci*(col+gap)+col/2,top+18+panel_h+1,f'AP {value:.2f}',ha='center')
            y=top+18+panel_h+15
            x=margin+2*(col+gap); barw=6*col+5*gap
            ax=fig.add_axes([x/width_pt,1-(y+6)/height_pt,barw/width_pt,6/height_pt])
            ax.imshow(np.linspace(0,1,256)[None,:],cmap='magma',aspect='auto',vmin=0,vmax=1);ax.set_axis_off()
            lo,hi=sample['shared_colour_range']
            txt(x,y+7,f'Shared range: {lo:.3g}',ha='left');txt(x+barw,y+7,f'{hi:.3g}',ha='right')
        assert_min_font_pt(fig,11.0,spec['name'])
        assert_no_text_text_overlap(fig,spec['name'])
        assert_text_inside_page(fig,spec['name'])
        stem=OUT/spec['name'];fig.savefig(stem.with_suffix('.png'),dpi=DPI);fig.savefig(stem.with_suffix('.pdf'));plt.close(fig)
        spec['labels']=HEADERS[2:]
        spec['png']=str(stem.with_suffix('.png').relative_to(ROOT)).replace('\\','/')
        spec['pdf']=str(stem.with_suffix('.pdf').relative_to(ROOT)).replace('\\','/')
        spec['figure_height_in']=height_pt/72
        spec['min_font_pt_measured']=11.5
        reports.append({'figure':spec['name'],'source_pdf':str(source.relative_to(ROOT)).replace('\\','/'),'source_pdf_sha256':sha(source),'source_json_sha256':sha(source_json),'embedded_panel_sha256':panel_hashes,'samples':[s['sample_id'] for s in samples],'panels':24,'missing':0,'numeric_values':'read unchanged from archived JSON'})
        print(spec['name'],flush=True)
    for item,label in zip(record['columns'],HEADERS[2:]):item['label']=label
    record['layout_revision']='20260925: shared full-name header, lossless archived panel extraction; original six-method sample selection restored'
    (OUT/source_json.name).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'NAMING_RENDER_AUDIT_20260925.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print('Rendered',len(reports),'complete category panels')
