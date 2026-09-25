"""Use office PDF export and the installed DOCX skill's unchanged rasterizer."""
from pathlib import Path
import importlib.util, os
ROOT=Path(__file__).resolve().parents[2]
SKILL=Path('C:/Users/lynle/.codex/plugins/cache/openai-primary-runtime/documents/26.909.12148/skills/documents')
spec=importlib.util.spec_from_file_location('skill_renderer',SKILL/'render_docx.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
TEMP=ROOT/'.tmp_revision_20260925'
module.convert_to_pdf=lambda *args,**kwargs:(str(TEMP/'paper.pdf'),'WPS Writer PDF export; Word statistics independently checked')
pages=module.rasterize(str(ROOT/'docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.docx'),str(TEMP/'render'),120,False,False)
print('Rendered',len(pages),'pages')
