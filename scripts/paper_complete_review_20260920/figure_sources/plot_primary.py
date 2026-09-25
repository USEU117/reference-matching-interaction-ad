from pathlib import Path
import json,csv,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[3];T=R/'.tmp_complete_figures_20260920';O=T/'plots';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Times New Roman','font.size':11,'axes.titlesize':11,'axes.labelsize':11,'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':11,'mathtext.fontset':'stix','axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':350})
tables=json.loads((R/'scripts/paper_complete_review_20260920/tables.json').read_text(encoding='utf-8'))
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from plot_fonts import configure_math
configure_math()
from display_labels import CONSTRUCTION_LABELS, ENCODER_LABELS, INTERACTION_LABELS, formula_subscript
def save(fig,name):
 fig.savefig(O/(name+'.png'),dpi=350);fig.savefig(O/(name+'.pdf'));plt.close(fig)
def nums(s):return [float(x) for x in re.findall(r'[+−-]?\d+\.\d+',s.replace('−','-'))]
fig,axs=plt.subplots(1,2,figsize=(17/2.54,4.5));fig.subplots_adjust(left=.13,right=.98,top=.88,bottom=.2,wspace=.48)
EFFECT_ROW_SPECS = [('TRI','J'), ('TRI','L'), ('BAL','J'), ('BAL','L')]
for ax,ds,rows in zip(axs,['MPDD','BTAD'],[tables['effects']['rows'][:4],tables['effects']['rows'][4:]]):
 assert len(rows)==len(EFFECT_ROW_SPECS)
 for i,(row,(construction,rule)) in enumerate(zip(rows,EFFECT_ROW_SPECS)):
  val=float(row[2].replace('−','-'));lo,hi=nums(row[3]);ax.errorbar(val,3-i,xerr=[[val-lo],[hi-val]],fmt='o',color='#2e6f9e' if ds=='MPDD' else '#b27c20',capsize=3)
 ax.axvline(0,color='#89939a',lw=1);ax.set_yticks(range(4),[rf'$E_{{\mathrm{{{formula_subscript(c, r)}}}}}$' for c,r in EFFECT_ROW_SPECS[::-1]]);ax.set_title(('(a) ' if ds=='MPDD' else '(b) ')+ds+' · representation effects',loc='left',fontweight='bold');ax.set_xlabel('Effect (AP points)');ax.grid(axis='x',alpha=.2);ax.set_ylim(-.6,3.6)
save(fig,'fig4a_representation_effects')
fig,axs=plt.subplots(2,2,figsize=(17/2.54,7.0));fig.subplots_adjust(left=.27,right=.98,top=.9,bottom=.135,hspace=.55,wspace=.9)
enc=tables['encoders']['rows']
# Fixed row order keeps plotting independent of reader-facing table labels.
ENCODER_ROW_SPECS = [('S',4), ('D',4), ('E1',4), ('E1',12), ('E2',4), ('E2',12), ('E3',4), ('E3',12)]
Y4={'S':7,'D':6,'E1':5,'E2':4,'E3':3};Y12={'E1':1,'E2':0,'E3':-1}
yp=[];yl=[]
assert len(enc)==len(ENCODER_ROW_SPECS)
for row,(b,scope) in zip(enc,ENCODER_ROW_SPECS):
 yp.append((Y4 if scope==4 else Y12)[b]);yl.append(ENCODER_LABELS[b]+' ('+str(scope)+')')
for j,ax in enumerate(axs.flat):
 for row,y in zip(enc,yp):
  val,lo,hi=nums(row[j+1]);ax.errorbar(val,y,xerr=[[val-lo],[hi-val]],fmt='o',color='#2e6f9e' if j<2 else '#b27c20',capsize=3)
 ax.set_yticks(yp,yl);ax.set_ylim(-2.2,8.2);ax.axhline(2,color='#d5d9dc',lw=.9);ax.axvline(0,color='#89939a',lw=1);ax.grid(axis='x',alpha=.2)
 x0,x1=ax.get_xlim();ax.set_xticks([t for t in ax.get_xticks() if x0<=t<=x1])   # drop out-of-range ticks (they would print in the gutter between columns)
 contrast='I_TRI' if j%2==0 else 'I_BAL';construction='TRI' if contrast=='I_TRI' else 'BAL';ax.set_title(f'({chr(97+j)}) '+('MPDD' if j<2 else 'BTAD')+'\n'+CONSTRUCTION_LABELS[construction],loc='left',fontweight='bold');ax.set_xlabel('Interaction (AP points)')
save(fig,'fig4b_matched_encoders')
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
D=R/'experiments/dynamic_fusion/representation_matching_interaction_20260914'
ks=rows(D/'03_robustness/interaction_K_curve.csv');cats=rows(D/'03_robustness/interaction_per_category.csv');seeds=rows(R/'experiments/dynamic_fusion/seeds_extension_20260917/interaction_by_seed.csv')
fig,axs=plt.subplots(2,1,figsize=(17/2.54,5.7));fig.subplots_adjust(left=.13,right=.97,top=.88,bottom=.12,hspace=.65)
for ds,col in [('mpdd','#2e6f9e'),('btad','#b27c20')]:
 for c,style in [('I_TRI','-'),('I_BAL','--')]:
  rr=sorted([x for x in ks if x['dataset']==ds and x['interaction']==c and int(x['seed'])==-1 and x['evaluation_revision']==('study' if ds=='mpdd' else 'corrected')],key=lambda x:int(x['shot']))
  assert len(rr)==4,(ds,c,len(rr))
  vals=[float(x['point_delta'] or x['mean_delta'])*100 for x in rr]
  construction='TRI' if c=='I_TRI' else 'BAL';axs[0].plot([int(x['shot']) for x in rr],vals,style,marker='o',color=col,label=ds.upper()+' '+CONSTRUCTION_LABELS[construction])
  rr=sorted([x for x in seeds if x['dataset']==ds and x['contrast']==c],key=lambda x:int(x['seed']))
  assert len(rr)==8
  axs[1].plot([int(x['seed']) for x in rr],[float(x['point_delta'])*100 for x in rr],style,color=col,alpha=.85)
  for x in rr:axs[1].plot(int(x['seed']),float(x['point_delta'])*100,'o',color=col,mfc=col if int(x['seed'])<3 else 'white')
for ax,title,xlabel in zip(axs,['(a) Nested support budgets','(b) Eight support seeds'],[r'Support budget $𝐾$','Support seed']):
 ax.axhline(0,color='#89939a',lw=1);ax.set_title(title,loc='left',fontweight='bold');ax.set_xlabel(xlabel);ax.set_ylabel('Interaction\n(AP points)');ax.grid(alpha=.2)
axs[0].set_xticks([1,2,4,8]);axs[1].set_xticks(range(8));fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.54,1.0))
save(fig,'fig5a_budget_seed')
rr=[x for x in cats if x['interaction']=='I_TRI' and ((x['dataset']=='mpdd' and x['evaluation_revision']=='study') or (x['dataset']=='btad' and x['evaluation_revision']=='corrected'))]
assert len(rr)==9
fig,ax=plt.subplots(figsize=(17/2.54,4.8));fig.subplots_adjust(left=.34,right=.97,top=.9,bottom=.17)
for i,x in enumerate(rr):
 v,lo,hi=[float(x[k])*100 for k in ['mean_delta','ci95_low','ci95_high']];ax.errorbar(v,len(rr)-1-i,xerr=[[v-lo],[hi-v]],fmt='o',color='#2e6f9e' if x['dataset']=='mpdd' else '#b27c20',capsize=3)
ax.set_yticks(range(len(rr)),[x['dataset'].upper()+' '+x['category'].replace('_',' ') for x in rr[::-1]]);ax.axvline(0,color='#89939a',lw=1);ax.grid(axis='x',alpha=.2);ax.set_xlabel(INTERACTION_LABELS['I_TRI']+' (AP points)');ax.set_title('(c) Category-level sensitivity · '+INTERACTION_LABELS['I_TRI'],loc='left',fontweight='bold');save(fig,'fig5b_categories')
(O/'primary_sources.json').write_text(json.dumps({'fig4a':'polished effects table; S, observed means and individual 95% intervals','fig4b':'polished encoders table; shared four-condition scope (4) and wider twelve-condition scope (12), bootstrap replicate means and 98.75% intervals, separate four-comparison family per encoder and scope','fig5a':{'budget':str(D/'03_robustness/interaction_K_curve.csv'),'seed':str(R/'experiments/dynamic_fusion/seeds_extension_20260917/interaction_by_seed.csv')},'fig5b':str(D/'03_robustness/interaction_per_category.csv')},indent=2),encoding='utf-8')
print('Primary plots written')
