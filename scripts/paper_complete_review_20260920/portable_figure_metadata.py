"""Re-emit active figure provenance with repository-relative paths, preserving values."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/paper_complete_review_20260920/figures'
PREFIX=re.compile(r'^[A-Za-z]:/+STUDY/+My_github/+(?:sci_project|reference-matching-interaction-ad)/+',re.I)
def portable(value):
    if isinstance(value,str):
        text=value.replace('\\','/')
        text=re.sub('/+','/',text)
        return PREFIX.sub('',text) if PREFIX.match(text) else value
    if isinstance(value,list):return [portable(x) for x in value]
    if isinstance(value,dict):return {k:portable(v) for k,v in value.items()}
    return value
changes=[]
for source in sorted(list((OUT/'multimethod').glob('*.json'))+[OUT/'primary_sources.json']):
    before=source.read_bytes()
    value=json.loads(before.decode('utf-8-sig'))
    result=portable(value)
    if result!=value:
        source.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    changes.append({'path':str(source.relative_to(ROOT)).replace('\\','/'),'paths_changed':result!=value,
                    'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
(OUT/'portable_metadata_revision23.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
print('Checked',len(changes),'active provenance files; changed',sum(x['paths_changed'] for x in changes))
