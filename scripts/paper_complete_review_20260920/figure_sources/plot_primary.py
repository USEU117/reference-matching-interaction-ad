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
def save(fig,name):
 fig.savefig(O/(name+'.png'),dpi=350);fig.savefig(O/(name+'.pdf'));plt.close(fig)
def nums(s):return [float(x) for x in re.findall(r'[+−-]?\d+\.\d+',s.replace('−','-'))]
fig,axs=plt.subplots(1,2,figsize=(17/2.54,4.5));fig.subplots_adjust(left=.13,right=.98,top=.88,bottom=.2,wspace=.48)
for ax,ds,rows in zip(axs,['MPDD','BTAD'],[tables['effects']['rows'][:4],tables['effects']['rows'][4:]]):
 for i,row in enumerate(rows):
  val=float(row[2].replace('−','-'));lo,hi=nums(row[3]);ax.errorbar(val,3-i,xerr=[[val-lo],[hi-val]],fmt='o',color='#2e6f9e' if ds=='MPDD' else '#b27c20',capsize=3)
 ax.axvline(0,color='#89939a',lw=1);ax.set_yticks(range(4),[r'$𝐸_{\mathrm{BAL,L}}$',r'$𝐸_{\mathrm{BAL,J}}$',r'$𝐸_{\mathrm{TRI,L}}$',r'$𝐸_{\mathrm{TRI,J}}$']);ax.set_title(('(a) ' if ds=='MPDD' else '(b) ')+ds+' · S effects',loc='left',fontweight='bold');ax.set_xlabel('Effect (AP points)');ax.grid(axis='x',alpha=.2);ax.set_ylim(-.6,3.6)
save(fig,'fig4a_representation_effects')
fig,axs=plt.subplots(2,2,figsize=(17/2.54,7.0));fig.subplots_adjust(left=.2,right=.98,top=.9,bottom=.135,hspace=.55,wspace=.5)
enc=tables['encoders']['rows']
# Two scope groups, read straight from the current table: the shared four-condition scope
# (S, D, E1, E2, E3) sits above the wider twelve-condition scope (E1, E2, E3). y ticks carry the
# (4)/(12) scope of each row so the panel mirrors the rows of the encoder table.
def _enc_label(nm):
 b,scope=nm.strip().split(' ',1);return b,scope.strip('()')
Y4={'S':7,'D':6,'E1':5,'E2':4,'E3':3};Y12={'E1':1,'E2':0,'E3':-1}
yp=[];yl=[]
for row in enc:
 b,scope=_enc_label(row[0]);yp.append((Y4 if scope=='4' else Y12)[b]);yl.append(b+' ('+scope+')')
for j,ax in enumerate(axs.flat):
 for row,y in zip(enc,yp):
  val,lo,hi=nums(row[j+1]);ax.errorbar(val,y,xerr=[[val-lo],[hi-val]],fmt='o',color='#2e6f9e' if j<2 else '#b27c20',capsize=3)
 ax.set_yticks(yp,yl);ax.set_ylim(-2.2,8.2);ax.axhline(2,color='#d5d9dc',lw=.9);ax.axvline(0,color='#89939a',lw=1);ax.grid(axis='x',alpha=.2)
 x0,x1=ax.get_xlim();ax.set_xticks([t for t in ax.get_xticks() if x0<=t<=x1])   # drop out-of-range ticks (they would print in the gutter between columns)
 ax.set_title(f'({chr(97+j)}) '+('MPDD' if j<2 else 'BTAD')+' '+(r'$𝐼_{\mathrm{TRI}}$' if j%2==0 else r'$𝐼_{\mathrm{BAL}}$'),loc='left',fontweight='bold');ax.set_xlabel('Interaction (AP points)')
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
  axs[0].plot([int(x['shot']) for x in rr],vals,style,marker='o',color=col,label=ds.upper()+' '+(r'$𝐼_{\mathrm{TRI}}$' if c=='I_TRI' else r'$𝐼_{\mathrm{BAL}}$'))
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
ax.set_yticks(range(len(rr)),[x['dataset'].upper()+' '+x['category'].replace('_',' ') for x in rr[::-1]]);ax.axvline(0,color='#89939a',lw=1);ax.grid(axis='x',alpha=.2);ax.set_xlabel(r'$𝐼_{\mathrm{TRI}}$ (AP points)');ax.set_title('(c) Category-level sensitivity',loc='left',fontweight='bold');save(fig,'fig5b_categories')
(O/'primary_sources.json').write_text(json.dumps({'fig4a':'polished effects table; S, observed means and individual 95% intervals','fig4b':'polished encoders table; shared four-condition scope (4) and wider twelve-condition scope (12), bootstrap replicate means and 98.75% intervals, separate four-comparison family per encoder and scope','fig5a':{'budget':str(D/'03_robustness/interaction_K_curve.csv'),'seed':str(R/'experiments/dynamic_fusion/seeds_extension_20260917/interaction_by_seed.csv')},'fig5b':str(D/'03_robustness/interaction_per_category.csv')},indent=2),encoding='utf-8')
print('Primary plots written')
