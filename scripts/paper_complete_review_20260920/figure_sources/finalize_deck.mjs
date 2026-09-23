import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const T=path.join(R,'.tmp_revision_20260923');
const S='C:/Users/lynle/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
process.env.RUNTIME_NODE_MODULES='C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(S+'/container_tools/artifact_tool_utils.mjs').href);
const manifest=JSON.parse(await fs.readFile(R+'/docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json','utf8'));
const name=process.argv[2]??'All_Figures_Complete_20260923.pptx';
const result=await finalizePresentation({workspaceDir:R,candidatePath:T+'/assembled.pptx',finalPath:R+'/docs/paper_complete_review_20260920/'+name,
 pythonExecutable:'C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
 integrityValidatorPath:S+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:S+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,10096500','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:manifest.length,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'user_request',families:['Times New Roman','Cambria Math']},verifyArtifactToolImport:true,
 receiptPath:T+'/'+name+'.validation.json'});
console.log(JSON.stringify(result));
