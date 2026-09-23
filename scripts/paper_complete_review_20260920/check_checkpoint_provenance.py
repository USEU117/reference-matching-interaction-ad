"""Compare retained ZIP bytes with local checkpoints without loading model pickles."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
def sha(stream):
    h=hashlib.sha256()
    for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
archive=ROOT/'methods/anomalyclip-main-full.zip'
with archive.open('rb') as f:archive_hash=sha(f)
assert archive_hash=='533ed87b6658cdb247d063a249cefea54ab81623cb11683c6f02345b9a6ceafe'
rows=[]
with zipfile.ZipFile(archive) as z:
    for p in sorted((ROOT/'methods/AnomalyCLIP-main/checkpoints').glob('*/epoch_*.pth')):
        suffix=p.relative_to(ROOT/'methods').as_posix()
        entries=[n for n in z.namelist() if n.lower().endswith(suffix.lower())]
        assert len(entries)==1,(p,entries)
        with p.open('rb') as f:a=sha(f)
        with z.open(entries[0]) as f:b=sha(f)
        assert a==b,p
        rows.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':a,'zip_entry':entries[0],'archive_entry_sha256':b,'match':True})
assert len(rows)==30
out={'verification_date':'2026-09-23','archive':archive.relative_to(ROOT).as_posix(),'archive_sha256':archive_hash,'recorded_upstream_commit':'3911738c0867544f545a076ad78f3f11d9ecbfdf','matched_files':len(rows),'checkpoints':rows,'boundary':'Byte identity with retained source archive; this does not independently authenticate an unrecorded remote download URL.'}
(ROOT/'docs/ANOMALYCLIP_CHECKPOINT_PROVENANCE_20260923.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('30/30 checkpoint SHA-256 values match archive entries')
