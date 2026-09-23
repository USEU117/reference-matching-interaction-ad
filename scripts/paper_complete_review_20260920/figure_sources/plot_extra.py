from pathlib import Path
import json,sys,inspect,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[3];T=R/'.tmp_complete_figures_20260920';O=T/'plots'
plt.rcParams.update({'font.family':'Times New Roman','font.size':11.5,'mathtext.fontset':'stix','axes.spines.top':False,'axes.spines.right':False})
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from plot_fonts import configure_math
configure_math()
def save(fig,name):
    for ext in ['png','pdf']:fig.savefig(O/f'{name}.{ext}',dpi=350)
    plt.close(fig)
a=json.loads((R/'docs/figures_reference_matching_20260914/figS2_shared_op_ablation.json').read_text(encoding='utf-8'))
fig,axs=plt.subplots(2,1,figsize=(17/2.54,5.7));fig.subplots_adjust(left=.13,right=.98,top=.87,bottom=.12,hspace=.65)
abl=['baseline','ABL_S','ABL_C','ABL_N'];x=np.arange(4)
for i,(ds,con,col) in enumerate([('mpdd','I_TRI','#2e6f9e'),('mpdd','I_BAL','#91b9d0'),('btad','I_TRI','#b27c20'),('btad','I_BAL','#e5c590')]):
    axs[0].bar(x+(i-1.5)*.19,[a['interaction_percentage_points'][f'{ds}|{con}|{v}'] for v in abl],.18,color=col,label=ds.upper()+' '+('$𝐼_{\\mathrm{TRI}}$' if con=='I_TRI' else '$𝐼_{\\mathrm{BAL}}$'))
for i,(ds,col) in enumerate([('mpdd','#2e6f9e'),('btad','#b27c20')]):axs[1].bar(x+(i-.5)*.3,[a['level_pixel_ap_J'][f'{ds}|{v}'] for v in abl],.29,color=col,label=ds.upper())
for ax,title,yl in zip(axs,['(a) Matching interactions','(b) Mean pixel AP under joint matching'],['Interaction (AP points)','Pixel AP']):
    ax.set_xticks(x,['Baseline','ABL-S','ABL-C','ABL-N']);ax.set_title(title,loc='left',fontweight='bold');ax.set_ylabel(yl);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
axs[0].axhline(0,color='gray',lw=.8);fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False);axs[1].set_ylim(0,.85);axs[1].legend(frameon=False,ncol=2,loc="upper right")
save(fig,'figS2_shared_op_ablation')
tab=json.loads((R/'scripts/paper_complete_review_20260920/tables.json').read_text(encoding='utf-8'))['resources']
fig,axs=plt.subplots(1,2,figsize=(17/2.54,3.9));fig.subplots_adjust(left=.12,right=.98,top=.82,bottom=.24,wspace=.4)
for i,ax in enumerate(axs):
    rr=tab['rows'][i*3:(i+1)*3];v=np.array([float(r[2]) for r in rr]);e=np.array([float(r[3]) for r in rr]);ax.bar(range(3),v,color='#2e6f9e',label='Processing');ax.bar(range(3),e,bottom=v,color='#b27c20',label='Evaluation');ax.set_xticks(range(3),['ADino','ADino\nrot.','PC 224']);ax.set_title(['(a) MPDD','(b) BTAD'][i],loc='left',fontweight='bold');ax.set_ylabel('Recorded stage time (s)');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False);save(fig,'fig8_resources')
sys.path.insert(0,str(R/'scripts/representation_matching_interaction_20260914'));sys.path.insert(0,str(R/'scripts/figures_reference_matching_20260914'))
import freeze_s0 as f
audit=json.loads((R/'experiments/dynamic_fusion/representation_matching_interaction_20260914/01_geometry/C_TO_B_COORDINATE_AUDIT.json').read_text(encoding='utf-8'))
fig,axs=plt.subplots(2,1,figsize=(17/2.54,5.5));fig.subplots_adjust(left=.16,right=.97,top=.85,bottom=.12,hspace=.55)
for i,(ax,rec) in enumerate(zip(axs,audit['records'][:2])):
    xs=np.linspace(0,rec['grid'][1],200);shift=(xs+.5)/rec['grid'][1]*(rec['x_extent_ratio']-1)*rec['c_side'];ax.plot(xs,shift,color='#a5453b',label='Approximate minus corrected');ax.axhline(0,color='#999999',ls='--',label='No shift');ax.set_title(f"({chr(97+i)}) {rec['dataset'].upper()} / {rec['category'].replace('_',' ')}",loc='left',fontweight='bold');ax.set_xlabel('Canvas column');ax.set_ylabel('Shift (C-grid cells)');ax.grid(alpha=.2)
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False);save(fig,'panel_c_to_b_shift')
src=inspect.getsource(f.boundary_figure)
src=src.replace('ax.legend(fontsize=MIN_FONT_PT, loc="lower right")','')
src=re.sub(r'    fig.suptitle\(.*?fontsize=MIN_FONT_PT\)','    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False)',src,flags=re.S)
src=src.replace("rect=(0, 0, 1, 0.88)","rect=(0, 0, 1, 0.80)")
exec(src,f.__dict__);f.boundary_figure(O/'panel_canvas_coverage')
import s2_robustness as s
s.CASE_ROWS_PER_PAGE=2;s.CASE_TOP_IN=.12
src=inspect.getsource(s._build_case_page)
src=re.sub(r'    suptitle = .*?    top = CASE_TOP_IN','    top = CASE_TOP_IN',src,flags=re.S)
src=src.replace('axes.imshow(first, cmap="inferno")','axes.imshow(first, cmap="inferno", vmin=min(float(p[1].min()) for p in row["panels"] if p[0]=="score"), vmax=max(float(p[1].max()) for p in row["panels"] if p[0]=="score"))')
src=src.replace('            else:\n                axes.imshow(first)','            elif kind == "mask":\n                axes.imshow(first, cmap="gray", vmin=0, vmax=1)\n            else:\n                axes.imshow(first)')
exec(src,s.__dict__)
old=s._case_row
def case_row(*args):
    row=old(*args);row['titles']=[None if t is None else t.replace('_',' ') for t in row['titles']];row['titles'][1]='GT mask';row['panels'][1]=('mask',(row['panels'][1][2]>0).astype(float),None);row['heading']=row['heading'].replace('I_TRI','TRI interaction').replace('I_BAL','BAL interaction').replace('most_positive','positive extreme').replace('most_negative','negative extreme');return row
s._case_row=case_row
s.render_cases(s.read_case_selection(R/'experiments/dynamic_fusion/representation_matching_interaction_20260914/03_robustness/interaction_case_selection.csv'),O/'panel_interaction_cases')
print('Extra panels complete')

