// Figure 1 (framework) generator — migrated into version control on 2026-09-23.
// Previously lived in the gitignored `.tmp_figure_revision_20260920/` scratch directory, which
// made the main framework figure unreproducible from the repository.  Behaviour is unchanged:
// only the root resolution and the output directory were parameterised.
//
// Chain (see run_pipeline.ps1):
//   build_main.mjs      -> .tmp_figure_revision_20260920/candidate.pptx (+ math_baselines.json, layout.json)
//   patch_math.py       -> .tmp_figure_revision_20260920/candidate_math.pptx
//   finalize_figure.mjs -> docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx
//   export_slide.ps1    -> docs/paper_complete_review_20260920/figures/fig1_framework.png (PowerPoint COM, 2560x2120)
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(HERE,'..','..');
const T=process.env.FIG1_SCRATCH?path.resolve(process.env.FIG1_SCRATCH):path.join(ROOT,'.tmp_figure_revision_20260920');
const OUT=process.env.FIG1_OUT_DIR?path.resolve(process.env.FIG1_OUT_DIR):path.join(ROOT,'docs','paper_complete_review_20260920','figures');
const ARTIFACT_TOOL=process.env.ARTIFACT_TOOL??'C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const {Presentation,PresentationFile}=await import(pathToFileURL(ARTIFACT_TOOL).href);
const {C}=await import(pathToFileURL(path.join(ROOT,'scripts/figures_reference_matching_20260914/style.mjs')).href);
const {image,frame,contourOverlay}=await import(pathToFileURL(path.join(ROOT,'scripts/figures_reference_matching_20260914/assets.mjs')).href);
await fs.mkdir(T,{recursive:true});
await fs.mkdir(OUT,{recursive:true});
const A=path.join(ROOT,'scripts/figures_reference_matching_20260914/assets');
const W=1280,H=1060,FS=30;
const p=Presentation.create({slideSize:{width:W,height:H}});const s=p.slides.add();s.background.fill='#FFFFFF';
const manifest=[],scripts=[];
function rect(name,x,y,w,h,fill,line='none',lw=1.8){return s.shapes.add({name,geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:lw,style:'solid'}})}
function text(name,value,x,y,w,h,{size=FS,bold=false,color=C.ink,align='left',font='Times New Roman'}={}){
  const sh=rect(name,x,y,w,h,'none');sh.text.set(String(value).split('\n').map(v=>[{run:v,textStyle:{typeface:font,fontSize:size+'px',bold,italic:false,color}}]));
  sh.text.style={typeface:font,fontSize:size,color,alignment:align,verticalAlignment:'middle',autoFit:'none',wrap:'none',lineSpacing:1.0,insets:{top:0,bottom:0,left:0,right:0}};
  manifest.push({name,text:value,x,y,w,h,size,kind:'text'});return sh;
}
// Editable mathematical runs, with native DrawingML baseline applied after export.
// Scalar indices are italic; descriptive indices and operators remain upright.
const v=(t,bold=false)=>({t,i:true,bold}),u=t=>({t}),sub=(t,i=false)=>({t,i,base:-25000}),sup=(t,i=false)=>({t,i,base:30000});
function math(name,tokens,x,y,w,h,{size=FS,align='center',color=C.ink}={}){
 const sh=rect(name,x,y,w,h,'none');
 sh.text.set([tokens.map((a,idx)=>{if(a.base)scripts.push({shape:name,run:idx,base:a.base});return{run:a.t,textStyle:{typeface:'Cambria Math',fontSize:(a.base?size*.69:size)+'px',bold:!!a.bold,italic:!!a.i,color}}})]);
 sh.text.style={typeface:'Cambria Math',fontSize:size,color,alignment:align,verticalAlignment:'middle',autoFit:'none',wrap:'none',insets:{top:0,right:0,bottom:0,left:0}};
 manifest.push({name,text:tokens.map(t=>t.t).join(''),x,y,w,h,size,kind:'math'});return sh;
}
let seq=0;
function arrow(a,b,{color=C.ink,dash=false,head=true,width=2.4}={}){
 const an=rect('anchor-'+seq++,a[0]-.5,a[1]-.5,1,1,'none');const bn=rect('anchor-'+seq++,b[0]-.5,b[1]-.5,1,1,'none');
 const dx=b[0]-a[0],dy=b[1]-a[1];const sides=Math.abs(dx)>=Math.abs(dy)?(dx>=0?['right','left']:['left','right']):(dy>=0?['bottom','top']:['top','bottom']);
 // DrawingML headEnd is the source; tailEnd is the destination.
 const c=s.shapes.connect(an,bn,{kind:'straight',fromSide:sides[0],toSide:sides[1],line:{style:dash?'dashed':'solid',fill:color,width},head:{type:'none'},tail:{type:head?'triangle':'none',width:'med',length:'med'}});
 manifest.push({kind:'arrow',a,b,headAt:'destination',dash});return c;
}
function route(points,opts={}){for(let i=0;i<points.length-1;i++)arrow(points[i],points[i+1],{...opts,head:i===points.length-2})}
function section(label,title,y){text('section-'+label,`(${label}) ${title}`,26,y,1180,44,{size:36,bold:true});}
function grid(name,x,y,rows,cols,cw,ch,fill,stroke){for(let i=0;i<rows;i++)for(let j=0;j<cols;j++)rect(`${name}-${i}-${j}`,x+j*(cw+2),y+i*(ch+2),cw,ch,fill,stroke,1);}
rect('memory-band',12,8,1256,298,C.bandCool);
rect('query-band',12,348,1256,390,C.bandWarm);
rect('control-band',12,752,1256,294,C.bandNeutral);
section('a','Construct the normal reference bank',18);
// Multiple support images show the general input; the caption identifies the K=1 output example.
for(const [i,xy]of [[0,[27,90]],[1,[64,114]],[2,[101,138]]]){
 await image(s,'support-'+i,path.join(A,['support_000_224.png','support_001_224.png','support_029_224.png'][i]),xy[0],xy[1],100,100,{fit:'contain'});
 frame(s,'support-border-'+i,xy[0],xy[1],100,100,C.grayLine,1.5);
}
math('support-set',[v('x',true),sub('i',true),sup('c',true)],24,245,72,40);
text('support-description','K normal\nsupport images',100,235,200,60);
// K in this descriptive line is changed to an italic run by the OOXML audit patch.
rect('frozen-box',300,80,286,220,C.white,C.grayLine,2);
text('frozen-title','Frozen encoders',306,83,274,42,{bold:true,align:'center'});
for(const [i,label,fill,line,y,h]of [[0,'DINOv2-B/14',C.blueFill,C.blueLine,127,33],[1,'AnomalyCLIP visual',C.amberFill,C.amberLine,162,33],[2,'DINOv2-S/14 or\nWideResNet50-2',C.greenFill,C.greenLine,197,60]]){
 rect('branch-'+i,307,y,272,h,fill,line,1.5);
 // Long encoder names reflow over two lines inside the editable branch rows.
 text('branch-label-'+i,label,307,y-2,272,h+4,{size:30,color:line,align:'center'});
}
text('frozen-note','Replacement options',304,263,278,35,{align:'center'});
arrow([211,167],[262,167]);arrow([592,167],[628,167]);
rect('alignment-box',635,80,223,220,C.tealFill,C.tealLine,2);
text('alignment-title','Align grids',646,85,200,39,{bold:true,align:'center'});
grid('feature-grid',653,136,3,3,23,23,'#D3E7EA',C.tealLine);
math('unit-norm',[u('ℓ'),sub('2'),u(' unit')],736,148,110,52);
text('aligned-note','Unit descriptors',621,263,252,35,{align:'center'});
arrow([865,167],[896,167]);
rect('bank-box',905,80,350,220,C.bankFill,C.bankLine,2);
text('bank-title','Fixed reference bank',914,84,332,41,{bold:true,align:'center'});
grid('bank',923,139,3,8,37,25,C.bankFill,C.bankLine);
rect('bank-accent',920,164,313,29,'none',C.blueLine,2.5);
math('candidate-set',[v('r'),u(' ∈ ℛ'),sub('c',true)],917,263,143,40,{color:C.blueLine});
text('bank-note','All patches',1070,263,184,35,{size:30,align:'center'});
route([[1219,300],[1219,325],[844,325],[844,414]],{dash:true,color:C.bankLine,width:1.8});
text('read-only','Read only',1040,297,170,36,{color:C.bankLine});

section('b','Score the query using the fixed bank',358);
await image(s,'query-image',path.join(A,'query_026_448.png'),28,433,150,150,{fit:'contain'});
frame(s,'query-frame',28,433,150,150,C.grayLine,1.5);
math('query-input',[u('Query '),v('x',true)],26,594,158,45);
arrow([183,509],[213,509]);
rect('query-encoder-path',220,438,198,143,C.white,C.grayLine,2);
text('query-path-title','Same frozen\nfeature path',226,445,186,81,{bold:true,align:'center'});
text('query-path-steps','Align + normalize',212,580.5,216,60,{align:'center'});
grid('query-grid',269,536,1,4,24,22,C.tealFill,C.tealLine);
arrow([423,509],[452,509]);
rect('matching-box',459,421,430,235,C.violetFill,C.violetLine,2);
text('matching-title','Reference matching',467,425,414,42,{bold:true,align:'center'});
const j=[v('J'),u('('),v('p'),u(') = min'),sub('r',true),u(' ∑'),sub('b',true),v(' w'),sub('b',true),v(' d'),sub('b',true),u('('),v('p'),u(','),v('r'),u(')')];
const l=[v('L'),u('('),v('p'),u(') = ∑'),sub('b',true),v(' w'),sub('b',true),u(' min'),sub('r',true),v(' d'),sub('b',true),u('('),v('p'),u(','),v('r'),u(')')];
rect('j-background',470,473,408,48,'#E4DBF1',C.violetLine,1.2);math('joint-equation',j,474,470,400,55);
rect('l-background',470,529,408,48,C.redFill,C.redLine,1.2);math('independent-equation',l,474,525,400,55);
math('resize-smooth',[u('Resize '),v('H'),u(' × '),v('W'),u('   Gaussian '),v('σ'),u(' = 4')],466,597,420,48,{size:30});
arrow([674,579],[674,595],{width:1.8});arrow([895,620],[930,620]);
text('matching-explanation','Joint: one shared row\nIndependent: separate rows',454,663,440,67,{align:'center'});
rect('outputs-box',938,420,316,288,C.white,C.grayLine,2);
text('output-heading','Output and display',943,422,307,42,{bold:true,align:'center'});
await image(s,'anomaly-map',path.join(A,'scoremap_concat_magma.png'),950,478,130,130,{fit:'contain'});
frame(s,'map-frame',950,478,130,130,C.grayLine,1.2);
const contours=JSON.parse(await fs.readFile(path.join(A,'contours.json'),'utf8'));
const polys=contours.A1.contours;
if(!polys) throw Error('Inspect contour object keys: '+Object.keys(contours));
await contourOverlay(s,'threshold-display',path.join(A,'query_026_448.png'),polys,1108,478,130);
frame(s,'contour-frame',1108,478,130,130,C.grayLine,1.2);
math('map-label',[v('A',true),sub('t',true)],950,613,130,42);
text('display-label','Contour',1106,613,135,42,{align:'center'});
math('image-score',[v('s'),sub('img,'),sub('t',true),u(' = max'),sub('u',true),v(' A',true),sub('t,u',true)],944,660,304,42);
math('display-only',[u('Contour uses '),v('τ'),sub('vis'),u(' for display only')],31,694.5,400,60,{align:'left'});

section('c','Representation effects and matching interactions',762);
const controls=[['Dual-encoder\nbaseline','Original encoder pair'],['Duplicate-branch\ncontrol','Copy existing features'],['Equal-weight\nreplacement','Replace the duplicate'],['Balanced\nreplacement','Preserve group weights']];
for(let i=0;i<4;i++){
 const x=26+i*314;
 text('control-label-'+i,controls[i][0],x,806,302,60,{size:30,bold:true,align:'center'});
 text('control-weights-'+i,controls[i][1],x,868,302,34,{size:30,align:'center'});
}
function E(label){return[v('E'),sub(label),sub(','),sub('t',true)]}
function perf(label){return[v('P'),u('('),u(label),sub('t',true),u(')')]}
math('tri-effect',[...E('Equal'),u(' = '),...perf('Equal'),u(' − '),...perf('Duplicate')],24,911,610,48);
math('bal-effect',[...E('Balanced'),u(' = '),...perf('Balanced'),u(' − '),...perf('Baseline')],649,911,610,48);
function interaction(label){return[v('I'),sub(label),u(' = '),v('E'),sub(label),sub(','),sub('L'),u(' − '),v('E'),sub(label),sub(','),sub('J')]}
math('tri-interaction',interaction('Equal'),24,966,610,48);
math('bal-interaction',interaction('Balanced'),649,966,610,48);
text('matched-condition-note','Identical supports and query images within every paired comparison',30,1015,1220,33,{align:'center'});
s.speakerNotes.textFrame.setText(`Scientific sources: scripts/manuscript_build_20260914 and docs/manuscript_polished_20260919. Real image assets: ${A}. MPDD metal_plate/test/scratches/026.png, A1 joint matching, seed 0 K=1. Score map follows stored resize and Gaussian sigma=4 processing. Red contour uses archived 256-bin Otsu polygons without loading a test mask. Three support thumbnails illustrate the general K-image input; they do not claim the output example used all three. The four constructions are the dual-encoder baseline, duplicate-branch control, equal-weight replacement, and balanced replacement. The frozen encoder names are DINOv2-B/14, AnomalyCLIP visual, and the replacement options DINOv2-S/14 or WideResNet50-2. p is query-patch index, b branch index, r normal-bank candidate. Native model outputs are the continuous anomaly map and its spatial maximum. Contour is display only. The replacement slot is a fixed construction, never a runtime switch. All diagrams and labels are editable native shapes, with real images embedded.`);
await(await PresentationFile.exportPptx(p)).save(path.join(T,'candidate.pptx'));
await fs.writeFile(path.join(T,'math_baselines.json'),JSON.stringify(scripts,null,2));
await fs.writeFile(path.join(T,'figure_manifest.json'),JSON.stringify({W,H,font:'Times New Roman',mathFont:'Cambria Math',minBaseSizePx:30,embeddedWidthCm:17,minPrintedPt:30*.75*17/(1280/96*2.54),elements:manifest},null,2));
await fs.writeFile(path.join(T,'layout.json'),await(await s.export({format:'layout'})).text());
const shot=await p.export({slide:s,format:'png',scale:2});
await fs.writeFile(path.join(T,'main_figure_export.png'),new Uint8Array(await shot.arrayBuffer()));
console.log('Native editable candidate generated:',path.join(T,'candidate.pptx'));
