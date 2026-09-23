"""Apply native DrawingML sub/superscript baselines to the Figure 1 candidate deck.

Migrated from `.tmp_figure_revision_20260920/patch_pptx.py` on 2026-09-23 so the Figure 1 chain
is reproducible from version control.  Reads `candidate.pptx` + `math_baselines.json` produced by
`build_main.mjs` and writes `candidate_math.pptx` into the same scratch directory.
"""
from pathlib import Path
from lxml import etree as E
import os
import zipfile, json, copy

ROOT = Path(__file__).resolve().parents[2]
T = Path(os.environ.get("FIG1_SCRATCH", ROOT / ".tmp_figure_revision_20260920"))
ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(T / 'candidate.pptx') as z:
    parts = {n: z.read(n) for n in z.namelist()}
root = E.fromstring(parts['ppt/slides/slide1.xml'])
byname = {sp.find('p:nvSpPr/p:cNvPr', ns).get('name'): sp for sp in root.findall('.//p:sp', ns)}
for row in json.loads((T / 'math_baselines.json').read_text()):
    sp = byname[row['shape']]
    runs = sp.findall('p:txBody/a:p/a:r', ns)
    r = runs[row['run']]
    pr = r.find('a:rPr', ns)
    if pr is None:
        pr = E.SubElement(r, '{' + ns['a'] + '}rPr')
    pr.set('baseline', str(row['base']))
# Upright encoder/construction labels must not be auto-italicized.
sp = byname['support-description']
para = sp.find('p:txBody/a:p', ns)
r = para.find('a:r', ns)
assert r.find('a:t', ns).text == 'K normal images'
r.find('a:t', ns).text = 'K'
r.find('a:rPr', ns).set('i', '1')
r2 = copy.deepcopy(r)
r2.find('a:t', ns).text = ' normal images'
r2.find('a:rPr', ns).set('i', '0')
para.insert(list(para).index(r) + 1, r2)
parts['ppt/slides/slide1.xml'] = E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
with zipfile.ZipFile(T / 'candidate_math.pptx', 'w', zipfile.ZIP_DEFLATED) as z:
    for n, v in parts.items():
        z.writestr(n, v)
print('Patched', len(json.loads((T / 'math_baselines.json').read_text())), 'native subscript runs ->', T / 'candidate_math.pptx')
