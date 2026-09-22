import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const R='D:/STUDY/My_github/sci_project',T=R+'/.tmp_complete_figures_20260920',O=R+'/docs/paper_complete_teacher_review_20260920',F=O+'/figures';
const {Presentation,PresentationFile}=await import(pathToFileURL('C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const ppt=Presentation.create({slideSize:{width:1280,height:1060}});
const figures=JSON.parse(await fs.readFile(R+'/scripts/paper_complete_teacher_review_20260920/figures.json','utf8'));
const manifest=[];let n=0;
for(const [key,f] of Object.entries(figures)){
  const label=f.label??String(++n);
  const parts=f.parts??[f.path];
  for(let i=0;i<parts.length;i++)manifest.push({figure:label,part:i+1,key,image:path.join(F,path.basename(parts[i])),caption:f.part_captions?.[i]??(i===0?f.caption:f.continuation_caption??f.caption),native:({framework:1,matching:2,constructions:3,encoders_geo:4})[key]??null});
}
await fs.mkdir(F+'/multimethod',{recursive:true});
for(const filename of (await fs.readdir(T+'/qualitative')).filter(f=>/\.(png|pdf|json)$/.test(f)).sort())await fs.copyFile(T+'/qualitative/'+filename,F+'/multimethod/'+filename);
const names=(await fs.readdir(F+'/multimethod')).filter(f=>f.endsWith('.png')).sort();
if(names.length!==36)throw Error('Expected 36 category panels, found '+names.length);
for(const filename of names)manifest.push({figure:'Category appendix',part:1,key:filename.replace('.png',''),image:F+'/multimethod/'+filename,caption:'Seed 0; K = 4. Three samples per category selected by largest per-image AP spread across six configurations, ties by sample identity. Each row uses the common valid evaluation region and one shared score range. A1 J / A1 L, AnomalyDINO / reference rotation, and PatchCore 128 / 224 are six configurations from the study and two external method families. Full sample identities, AP values, geometry and selection records are retained in the adjacent dataset JSON. Selected extremes are illustrative, not a representative performance estimate.'});
for(const [i,item] of manifest.entries()){
 const slide=ppt.slides.add();slide.background.fill='#FFFFFF';item.slide=i+1;
 const blob=new Uint8Array(await fs.readFile(item.image));
 slide.images.add({blob,contentType:'image/png',alt:'Figure '+item.figure+' part '+item.part,fit:'contain',position:{left:12,top:12,width:1256,height:1036}});
 slide.speakerNotes.textFrame.setText('Figure '+item.figure+'; part '+item.part+'\n'+item.caption+'\nImage: '+item.image+'\nReproducible sources: scripts/paper_complete_teacher_review_20260920/');
}
await (await PresentationFile.exportPptx(ppt)).save(T+'/all_images.pptx');
await fs.writeFile(O+'/FIGURE_SLIDE_INDEX.json',JSON.stringify(manifest,null,2));
await fs.writeFile(O+'/图件与PPT页码索引.md','# 图件与 PPT 页码索引\n\n| PPT 页 | 论文图号 | 分页 | 图文件 |\n|---|---|---|---|\n'+manifest.map(x=>`| ${x.slide} | ${x.figure} | ${x.part} | ${path.basename(x.image)} |`).join('\n')+'\n\n第 1、2、3、12 页为原生可编辑方法图；其余为高分辨率科学绘图，数值与布局可通过配套脚本修改后重新生成。每页备注保留图注、实验口径和来源。\n');
console.log('Built',manifest.length,'slides');
