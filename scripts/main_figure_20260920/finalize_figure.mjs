// Finalize the editable Figure 1 master (native shapes + math) into the manuscript figure pack.
// Migrated from `.tmp_figure_revision_20260920/finalize.mjs` on 2026-09-23: the root is derived from
// this file and the final path is the live (tracked) figure directory, with no review-facing wording.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const R=path.resolve(HERE,'..','..');
const T=process.env.FIG1_SCRATCH?path.resolve(process.env.FIG1_SCRATCH):path.join(R,'.tmp_figure_revision_20260920');
const S=process.env.PRESENTATION_SKILL??'C:/Users/lynle/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations';
process.env.RUNTIME_NODE_MODULES=process.env.RUNTIME_NODE_MODULES??'C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const {finalizePresentation}=await import(pathToFileURL(S+'/container_tools/artifact_tool_utils.mjs').href);
const name=process.argv[2]??'Main_Figure_Editable_Final_20260925.pptx';
const r=await finalizePresentation({workspaceDir:R,candidatePath:T+'/candidate_math.pptx',finalPath:path.join(R,'docs','main_figure_revision_20260920',name),pythonExecutable:process.env.RUNTIME_PYTHON??'C:/Users/lynle/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:S+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:S+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,10096500','--validate-bullet-geometry','--validate-heading-fit'],explicitTotalSlideCount:1,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],fontPolicy:{basis:'design',families:['Times New Roman','Cambria Math']},verifyArtifactToolImport:true,receiptPath:T+'/'+name+'.validation.json'});
console.log(JSON.stringify(r));
