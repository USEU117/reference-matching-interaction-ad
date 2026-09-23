"""Paper layout for S6; reads the frozen protocol summaries without recomputation."""
from pathlib import Path
import json, hashlib, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'experiments/dynamic_fusion/representation_matching_interaction_20260914/05_baselines_harmonised_20260922/protocol_leverage.json'
OUT = ROOT / 'docs/paper_complete_review_20260920/figures'
sys.path.insert(0, str(ROOT / 'scripts/figures_reference_matching_20260914'))
from figure_font_gate import assert_min_font_pt, assert_no_text_text_overlap, assert_text_inside_page

METHODS = [
 ('controlled_A1_J','A1 J','#9A4935','o'),
 ('controlled_A1_L','A1 L','#9A4935','o'),
 ('anomalydino_canvas','AnomalyDINO','#28618A','^'),
 ('anomalydino_canvas_rotation','AnomalyDINO + rot.','#28618A','^'),
 ('PatchCore_native_local128','PatchCore 128','#28618A','D'),
 ('PatchCore_native_official224','PatchCore 224','#28618A','D'),
 ('SubspaceAD_native_fp16','SubspaceAD 256','#28618A','s'),
 ('WinCLIP_native_240','WinCLIP+ 240','#3D866B','v'),
 ('AnomalyCLIP_zeroshot_518','AnomalyCLIP 518','#3D866B','v'),
]

def main():
    payload=json.loads(SOURCE.read_text(encoding='utf-8'))
    macro=payload['macro_pixel_ap_per_method_dataset']
    plt.rcParams.update({'font.family':'Times New Roman','font.size':11.5,'axes.labelsize':11.5,
                         'xtick.labelsize':11.5,'ytick.labelsize':11.5,'axes.titlesize':11.5})
    outputs=[]
    for part,datasets in enumerate([[('mpdd','MPDD'),('btad','BTAD')],[('mvtec','MVTec AD'),('visa','VisA')]],1):
        fig,axes=plt.subplots(2,1,figsize=(17/2.54,7.6))
        fig.subplots_adjust(left=.31,right=.965,bottom=.09,top=.955,hspace=.38)
        for ax,(dataset,title) in zip(axes,datasets):
            for i,(key,label,color,marker) in enumerate(METHODS):
                ax.plot(macro[key+'|'+dataset],8-i,marker=marker,color=color,ms=6,linestyle='none')
            for a,b in [(0,1),(2,3),(4,5)]:
                ax.plot([macro[METHODS[i][0]+'|'+dataset] for i in [a,b]],[8-a,8-b],color='#6E6E6E',lw=1.3,zorder=0)
            ax.set_yticks(range(9),[m[1] for m in METHODS][::-1])
            ax.set_xlim(0,.75);ax.set_xticks([0,.15,.30,.45,.60,.75])
            ax.set_ylim(-.6,8.6);ax.set_xlabel('Macro pixel AP')
            ax.set_title(title,loc='left',weight='bold',pad=9)
            ax.grid(axis='x',color='#D9DFE5',lw=.7);ax.set_axisbelow(True)
            ax.spines[['top','right']].set_visible(False)
        fig.canvas.draw()
        assert_min_font_pt(fig,11)
        assert_no_text_text_overlap(fig)
        assert_text_inside_page(fig)
        stem=f'figS6_protocol_paper_part{part}'
        for suffix in ['png','pdf']:fig.savefig(OUT/f'{stem}.{suffix}',dpi=350)
        outputs.append({'path':str((OUT/f'{stem}.png').relative_to(ROOT)).replace('\\','/'),'datasets':[x[0] for x in datasets]})
        plt.close(fig)
    (OUT/'figS6_protocol_paper.json').write_text(json.dumps({'source':str(SOURCE.relative_to(ROOT)).replace('\\','/'),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'numerical_changes':False,'minimum_print_pt_at_17cm':11.5,
        'parts':outputs,'scope':'Protocol context; eight configurations averaged over s0/1 K1/4, AnomalyCLIP one support-free setting. No intervals or cross-method tests.'},indent=2),encoding='utf-8')
    print(json.dumps(outputs))

if __name__=='__main__':main()
