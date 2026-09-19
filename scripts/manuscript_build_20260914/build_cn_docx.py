"""Build the formatted Chinese companion DOCX from 中文对照内容.md.

Moved here on 2026-09-19 from the git-ignored scratch directory
`.tmp_english_manuscript_20260914`, where the 2026-09-14 Chinese companion was built.  The
document logic is unchanged; only the paths became repository-relative and overridable from
the command line, exactly as in the English `build.py` next to this file.

The Chinese source lives with the manuscript outputs (docs/manuscript_reference_matching_20260914/
中文对照内容.md) and embeds the figure files from that directory's `figures/` folder, so the
default --out-dir is the manuscript directory itself and a default run overwrites the
checked-in 中文对照 docx; pass --out-dir for a verification run.

Usage:
    python scripts/manuscript_build_20260914/build_cn_docx.py --out-dir <tmp dir>
"""
from pathlib import Path
import argparse
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
DEFAULT_REPO_ROOT = HERE.parents[1]
DEFAULT_SRC = Path('docs/manuscript_reference_matching_20260914/中文对照内容.md')


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('--repo-root', type=Path, default=DEFAULT_REPO_ROOT,
                    help='repository root that repository-relative paths resolve against')
    ap.add_argument('--source', type=Path, default=DEFAULT_SRC,
                    help='the Chinese markdown source (中文对照内容.md)')
    ap.add_argument('--figures-dir', type=Path, default=None,
                    help='directory the figure files are loaded from; defaults to <out-dir>/figures')
    ap.add_argument('--out-dir', type=Path, default=None,
                    help='output directory for the Chinese DOCX; defaults to the paper folder')
    ap.add_argument('--reference-docx', type=Path, default=None,
                    help='retained DOCX package whose styles, page system and page footer are reused')
    return ap.parse_args()


def under(root, path):
    path = Path(path)
    return path if path.is_absolute() else (root / path)


ARGS = parse_args()
ROOT = Path(ARGS.repo_root).resolve()
SRC = under(ROOT, ARGS.source)
OUT = Path(under(ROOT, ARGS.out_dir)).resolve() if ARGS.out_dir is not None \
    else ROOT / 'docs/manuscript_reference_matching_20260914'
OUT.mkdir(parents=True, exist_ok=True)
FIGS = Path(under(ROOT, ARGS.figures_dir)).resolve() if ARGS.figures_dir is not None else OUT / 'figures'
DEST = OUT / 'Reference_Matching_Interaction_中文对照_20260914.docx'
REF = under(ROOT, ARGS.reference_docx) if ARGS.reference_docx is not None \
    else ROOT / 'docs/manuscript_english_polished_20260906/DCFnet_English_Polished_20260906.docx'
REF = Path(REF).resolve()

LATIN = 'Times New Roman'
SONG, HEI, KAI = '宋体', '黑体', '楷体'

d = Document(REF)
# Reuse the retained package, styles, page system and page footer; drop old-topic body.
for e in list(d.element.body):
    if e.tag != qn('w:sectPr'):
        d.element.body.remove(e)
for e in list(d.styles.element.iter(qn('w:pBdr'))) + list(d.element.iter(qn('w:pBdr'))):
    e.getparent().remove(e)


def style_fonts(name, latin, ea):
    st = d.styles[name]
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.font.name = latin
    rpr = st.element.find(qn('w:rPr'))
    rf = rpr.find(qn('w:rFonts'))
    rf.set(qn('w:eastAsia'), ea)


for st_name in ['Normal', 'Title', 'Heading 1', 'Heading 2', 'Heading 3', 'Caption']:
    style_fonts(st_name, LATIN, SONG)
# Chinese display faces for the title and headings, body face for text and captions.
for st_name in ['Title', 'Heading 1', 'Heading 2', 'Heading 3']:
    style_fonts(st_name, LATIN, HEI)

d.core_properties.title = '附加视觉表征与正常参考匹配之间的交互：中文对照译本（含术语与难点注释）'
d.core_properties.subject = '与英文稿 Reference_Matching_Interaction_English_Draft_20260914.docx 一一对应的中文读本'
d.core_properties.author = ''
d.core_properties.keywords = '少样本异常定位; 冻结视觉编码器; 正常参考匹配; 表征交互'


# ---------------------------------------------------------------- native math
def mr(t, roman=False, bold=False):
    x = OxmlElement('m:r'); pr = OxmlElement('m:rPr'); st = OxmlElement('m:sty')
    st.set(qn('m:val'), 'b' if roman and bold else 'p' if roman else 'bi' if bold else 'i')
    pr.append(st); x.append(pr)
    wp = OxmlElement('w:rPr'); f = OxmlElement('w:rFonts')
    for a in ['ascii', 'hAnsi']:
        f.set(qn('w:' + a), 'Cambria Math')
    wp.append(f); x.append(wp)
    tt = OxmlElement('m:t'); tt.text = t; x.append(tt); return x


def obj(tag, **parts):
    e = OxmlElement('m:' + tag)
    for name, children in parts.items():
        part = OxmlElement('m:' + name)
        for ch in children if isinstance(children, list) else [children]:
            part.append(ch)
        e.append(part)
    return e


def sub(base, index, roman=False, bold=False):
    return obj('sSub', e=[mr(base, roman, bold)], sub=index if isinstance(index, list) else [mr(index)])


def sup(base, index, roman=False, bold=False):
    return obj('sSup', e=[mr(base, roman, bold)], sup=[mr(index)])


def sub_sup(base, index, upper, bold=False):
    return obj('sSubSup', e=[mr(base, False, bold)], sub=[mr(index)], sup=[mr(upper)])


def labelindex(t):
    return [mr(part, part in ['TRI', 'BAL', 'DUP', 'A1', 'J', 'L', 'S', 'D', 'img', 'vis'])
            for part in re.split(r'(TRI|BAL|DUP|A1|img|vis|J|L|S|D)', t) if part]


def sym(t):
    t = t.replace(r'\mathrm{img}', 'img').replace(r'\mathrm{vis}', 'vis')
    if t == r'\mathcal{R}_c':
        return [sub('ℛ', 'c', True)]
    if t == r'\tau_{vis}':
        return [sub('τ', [mr('vis', True)])]
    m = re.fullmatch(r'([A-Za-z]+)_\{([^}]+)\}', t) or re.fullmatch(r'([A-Za-z]+)_([A-Za-z]+)', t)
    if t == 'x_i^c':
        return [sub_sup('x', 'i', 'c', True)]
    if m:
        b, ix = m.groups()
        return [sub(b, labelindex(ix), b in ['TRI', 'BAL', 'DUP', 'A1', 'R'], b in ['F', 'g', 'A', 'a', 'M'])]
    return [mr(t, t in ['J', 'L'] and False or t in ['P'] and False, t in ['x', 'F', 'g', 'A', 'a', 'M'])]


def mathrun(p, items):
    om = OxmlElement('m:oMath')
    for x in items:
        om.append(x)
    p._p.append(om)


def limit(name, idx):
    return obj('limLow', e=[mr(name, True)], lim=idx)


def summation(items):
    e = OxmlElement('m:nary'); pr = OxmlElement('m:naryPr'); c = OxmlElement('m:chr')
    c.set(qn('m:val'), '∑'); pr.append(c)
    h = OxmlElement('m:supHide'); h.set(qn('m:val'), '1'); pr.append(h); e.append(pr)
    for name, children in [('sub', [mr('b')]), ('sup', []), ('e', items)]:
        pp = OxmlElement('m:' + name)
        for ch in children:
            pp.append(ch)
        e.append(pp)
    return e


def configuration(name, mode):
    return sub(name, labelindex(mode), True)


def performance(name, mode):
    return [mr('P'), mr('(', True), configuration(name, mode), mr(')', True)]


def effect(name, mode):
    return sub('E', labelindex(name + ',' + mode))


def parg(name):
    return [mr('(', True), mr(name), mr(')', True)]


def distance():
    return [sub('d', 'b'), mr('(', True), mr('p'), mr(',', True), mr('r'), mr(')', True)]


def eq(n):
    if n == 1:
        nd = [sub('𝒳', 'c', True), mr(' = {', True), sub_sup('x', 'i', 'c', True), mr(' : ', True), mr('i'),
              mr(' = 1, …, ', True), mr('K'), mr('}', True)]
    elif n == 2:
        g1 = obj('sSup', e=[sub('g', labelindex('b,p'), False, True)], sup=[mr('T', True)])
        nd = distance() + [mr(' = 1 − ', True), g1, sub('g', labelindex('b,r'), False, True)]
    elif n in [3, 4]:
        mi = lambda: limit('min', [mr('r'), mr(' ∈ ', True), sub('ℛ', 'c', True)])
        term = [sub('w', 'b')] + distance()
        nd = [mr('J' if n == 3 else 'L')] + parg('p') + [mr(' = ', True)]
        nd += [mi(), summation(term)] if n == 3 else [summation([sub('w', 'b'), mi()] + distance())]
    elif n == 5:
        nd = [mr('G')] + parg('p') + [mr(' = ', True), mr('J')] + parg('p') + [mr(' − ', True), mr('L')] + parg('p') + [mr(' ≥ 0', True)]
    elif n in [6, 7]:
        name, control = ('TRI', 'DUP') if n == 6 else ('BAL', 'A1')
        nd = [effect(name, 't'), mr(' = ', True)] + performance(name, 't') + [mr(' − ', True)] + performance(control, 't')
    elif n in [8, 9]:
        name = 'TRI' if n == 8 else 'BAL'
        nd = [sub('I', [mr(name, True)]), mr(' = ', True), effect(name, 'L'), mr(' − ', True), effect(name, 'J')]
    elif n == 10:
        nd = [sub('ΔI', 'q'), mr(' = ', True), sub('I', labelindex('q,D')), mr(' − ', True), sub('I', labelindex('q,S')),
              mr(',    ', True), mr('q'), mr(' ∈ {TRI, BAL}', True)]
    elif n == 11:
        nd = [sub('A', 't', False, True), mr(' = ', True), sub('Gauss', [mr('σ'), mr('=4', True)], True), mr('(', True),
              sub('Resize', [mr('H'), mr('×', True), mr('W')], True), mr('(', True), sub('a', 't', False, True),
              mr(')),   ', True), sub('s', labelindex('img,t')), mr(' = ', True), limit('max', [mr('u')]),
              sub('A', labelindex('t,u'), False, True)]
    elif n == 12:
        nd = [sub('M', labelindex('vis,t'), False, True)] + parg('u') + [mr(' = ', True), mr('1', True), mr('[', True),
              sub('A', labelindex('t,u'), False, True), mr(' ≥ ', True), sub('τ', [mr('vis', True)]), mr(']', True)]
    p = d.add_paragraph(); p.paragraph_format.space_before = Pt(5); p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(8.5), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(17), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run('\t'); mathrun(p, nd); p.add_run('\t(' + str(n) + ')')
    return p


# ------------------------------------------------------- inline math fallback
LATEX = [(r'\mathcal{X}', '𝒳'), (r'\mathcal{R}', 'ℛ'), (r'\mathbf{1}', '1'), (r'\mathsf{T}', 'T'),
         (r'\mathrm{img}', 'img'), (r'\mathrm{vis}', 'vis'), (r'\mathrm{Gauss}', 'Gauss'),
         (r'\mathrm{Resize}', 'Resize'), (r'\text{new}', 'new'), (r'\text{control}', 'control'),
         (r'\text{TRI}', 'TRI'), (r'\text{BAL}', 'BAL'), (r'\text{DUP}', 'DUP'),
         (r'\Delta', 'Δ'), (r'\tau', 'τ'), (r'\sigma', 'σ'), (r'\ge', '≥'), (r'\le', '≤'),
         (r'\times', '×'), (r'\dots', '…'), (r'\quad', ' '), (r'\,', ' '), (r'\in', '∈'),
         (r'\min', 'min'), (r'\max', 'max'), (r'\sum_b', 'Σ'), (r'\sqrt{1/3}', '√(1/3)'),
         (r'\{', '{'), (r'\}', '}'), (r'\!', '')]


def clean_math(t):
    for a, b in LATEX:
        t = t.replace(a, b)
    return re.sub(r'\\([A-Za-z]+)', r'\1', t)


def add_math(p, text, size=None, ea=None):
    """Render a plain-math span with real Word sub/superscripts."""
    for tok in re.split(r'(\^\{[^}]*\}|_\{[^}]*\}|\^[A-Za-z0-9]|_[A-Za-z0-9])', text):
        if not tok:
            continue
        if tok.startswith('^'):
            r = p.add_run(clean_math(tok[2:-1] if tok[1] == '{' else tok[1:])); r.font.superscript = True
        elif tok.startswith('_'):
            r = p.add_run(clean_math(tok[2:-1] if tok[1] == '{' else tok[1:])); r.font.subscript = True
        else:
            r = p.add_run(clean_math(tok))
        r.italic = True
        if size:
            r.font.size = size
        if ea:
            set_run_ea(r, ea)


def set_run_ea(run, ea, latin=LATIN):
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    rf.set(qn('w:ascii'), latin); rf.set(qn('w:hAnsi'), latin); rf.set(qn('w:eastAsia'), ea)


def add_inline(p, text, size=None, ea=None):
    """Handle **bold**, `code` and $math$ inside one paragraph."""
    for part in re.split(r'(\*\*.*?\*\*|`[^`]*`|\$[^$\n]+\$)', text):
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith('`') and part.endswith('`'):
            r = p.add_run(part[1:-1]); r.font.name = 'Consolas'
        elif part.startswith('$') and part.endswith('$'):
            add_math(p, part[1:-1], size)
            continue
        else:
            r = p.add_run(part)
        if size:
            r.font.size = size
        if ea:
            set_run_ea(r, ea)


def shade(p, fill='F4F4F4'):
    pr = p._p.get_or_add_pPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), fill)
    pr.append(sh)


def bare(t):
    return re.sub(r'(\*\*|`|\$)', '', t)


# ---------------------------------------------------------------- block input
lines = SRC.read_text(encoding='utf-8').splitlines()
table_buf, in_note = [], False
NOTE_SIZE = Pt(9.5)


def flush_table():
    global table_buf
    if not table_buf:
        return
    rows = []
    for ln in table_buf:
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells):
            continue
        rows.append(cells)
    table_buf = []
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    # Proportional widths from the longest cell text, clamped, then normalized to 17 cm.
    weights = []
    for ci in range(ncol):
        longest = max(len(bare(r[ci])) for r in rows)
        weights.append(min(max(longest, 4), 40))
    total = sum(weights)
    widths = [max(1.6, round(17.0 * w / total, 2)) for w in weights]
    scale = 17.0 / sum(widths)
    widths = [round(w * scale, 2) for w in widths]

    t = d.add_table(rows=0, cols=ncol); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for col, w in zip(t.columns, widths):
        col.width = Cm(w)
    for ri, row in enumerate(rows):
        rr = t.add_row(); rp = rr._tr.get_or_add_trPr(); rp.append(OxmlElement('w:cantSplit'))
        if ri == 0:
            rp.append(OxmlElement('w:tblHeader'))
        for ci, txt in enumerate(row):
            c = rr.cells[ci]; c.width = Cm(widths[ci]); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = c._tc.get_or_add_tcPr(); bd = OxmlElement('w:tcBorders')
            for edge in ['top', 'bottom', 'left', 'right']:
                ee = OxmlElement('w:' + edge)
                on = (edge == 'top' and ri == 0) or (edge == 'bottom' and ri in [0, len(rows) - 1])
                ee.set(qn('w:val'), 'single' if on else 'nil')
                ee.set(qn('w:sz'), '8' if ri == len(rows) - 1 else '6'); ee.set(qn('w:color'), '000000')
                bd.append(ee)
            cp.append(bd)
            mar = OxmlElement('w:tcMar')
            for edge in ['top', 'bottom', 'left', 'right']:
                z = OxmlElement('w:' + edge); z.set(qn('w:w'), '70'); z.set(qn('w:type'), 'dxa'); mar.append(z)
            cp.append(mar)
            p = c.paragraphs[0]
            add_inline(p, txt, Pt(9.5))
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = LATIN
                r.font.size = Pt(9.5)
                r.bold = r.bold or ri == 0
                set_run_ea(r, SONG)
            for rp0 in p._p.iter(qn('w:rPr')):
                z = OxmlElement('w:sz'); z.set(qn('w:val'), '19'); rp0.append(z)
    tb = t._tbl.tblPr; bd = OxmlElement('w:tblBorders')
    for edge in ['top', 'bottom', 'left', 'right', 'insideH', 'insideV']:
        z = OxmlElement('w:' + edge); z.set(qn('w:val'), 'nil'); bd.append(z)
    tb.append(bd)


for raw in lines:
    line = raw.rstrip()
    stripped = line.strip()

    if stripped.startswith('|'):
        table_buf.append(stripped); continue
    flush_table()

    if not stripped:
        in_note = False
        continue
    if re.fullmatch(r'-{3,}', stripped):
        continue

    m = re.fullmatch(r'(#{1,4})\s+(.*)', stripped)
    if m:
        level, text = len(m.group(1)), m.group(2)
        p = d.add_paragraph(style='Title' if level == 1 else 'Heading %d' % min(level - 1, 3))
        add_inline(p, text)
        if level == 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        continue

    m = re.fullmatch(r'>\s*\*\*公式\s*\((\d+)\)\*\*(.*)', stripped)
    if m:
        eq(int(m.group(1))); continue

    if stripped.startswith('>'):
        body = stripped.lstrip('>').strip()
        mfig = re.match(r'\*\*图\s*(S?\d+)', body)
        if mfig:
            # Embed the same figure files the English manuscript uses, then the caption.
            # Only names that exist in the manuscript figure folder are treated as sources,
            # so dataset image names mentioned inside a caption are ignored.
            for fname in re.findall(r'[A-Za-z0-9_]+\.png', body):
                img = FIGS / fname
                if not img.exists():
                    continue
                ip = d.add_paragraph(); ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
                ip.paragraph_format.keep_with_next = True
                ip.paragraph_format.space_before = Pt(5); ip.paragraph_format.space_after = Pt(4)
                ip.add_run().add_picture(str(img), width=Cm(17))
        p = d.add_paragraph(style='Caption')
        add_inline(p, body)
        continue

    m = re.fullmatch(r'\*\*(表\s*\d+.*)\*\*', stripped)
    if m:
        p = d.add_paragraph(style='Caption')
        t = m.group(1)
        t = re.sub(r'^表\s*(\d+)', r'表 \1.', t, count=1)
        add_inline(p, t)
        p.paragraph_format.keep_with_next = True
        continue

    m = re.fullmatch(r'\*\*(〔注\s*\d+〕[^*]*)\*\*(.*)', stripped)
    if m:
        p = d.add_paragraph()
        add_inline(p, m.group(1), NOTE_SIZE, KAI)
        for r in p.runs:
            r.bold = True
        shade(p)
        p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.4)
        p.paragraph_format.keep_with_next = True
        rest = m.group(2).strip()
        in_note = True
        if rest:
            q = d.add_paragraph(); add_inline(q, rest, NOTE_SIZE, KAI); shade(q)
            q.paragraph_format.left_indent = Cm(0.4); q.paragraph_format.space_after = Pt(6)
        continue

    m = re.match(r'^(\s*)(?:[-*]|\d+\.)\s+(.*)', line)
    if m:
        indent = 0.75 + 0.6 * (len(m.group(1)) // 2)
        p = d.add_paragraph()
        p.paragraph_format.left_indent = Cm(indent)
        p.paragraph_format.first_line_indent = Cm(-0.45)
        p.paragraph_format.space_after = Pt(2)
        if in_note:
            add_inline(p, m.group(2), NOTE_SIZE, KAI); shade(p)
            p.paragraph_format.left_indent = Cm(1.0)
        else:
            add_inline(p, ('· ' if stripped[0] in '-*' else stripped.split('.')[0] + '. ') + m.group(2))
        continue

    p = d.add_paragraph()
    if in_note:
        add_inline(p, stripped, NOTE_SIZE, KAI); shade(p)
        p.paragraph_format.left_indent = Cm(0.4)
        p.paragraph_format.space_after = Pt(6)
    else:
        add_inline(p, stripped)

flush_table()
DEST.parent.mkdir(parents=True, exist_ok=True)
d.save(DEST)
print(DEST)
print('paragraphs', len(d.paragraphs), 'tables', len(d.tables), 'shapes', len(d.inline_shapes))
