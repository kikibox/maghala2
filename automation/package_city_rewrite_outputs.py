#!/usr/bin/env python3
import base64,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'artifacts/city-rewrite-queue'
OUT=SRC/'downloads'
OUT.mkdir(parents=True,exist_ok=True)
for old in OUT.glob('*'): old.unlink()
manifest={'format':'gzip+base64','chunk_chars':700000,'files':[]}
encoded_files={}
for name in ['rewrite-all-completed.sql','rollback-all-completed.sql']:
    raw=(SRC/name).read_bytes()
    packed=gzip.compress(raw,compresslevel=9)
    encoded=base64.b64encode(packed).decode('ascii')
    encoded_files[name]=encoded
    parts=[]
    for i,start in enumerate(range(0,len(encoded),700000),1):
        part_name=f'{name}.gz.b64.part{i:03d}'
        (OUT/part_name).write_text(encoded[start:start+700000],encoding='ascii')
        parts.append(part_name)
    manifest['files'].append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'gzip_bytes':len(packed),'base64_chars':len(encoded),'parts':parts})
# Extra whitespace is ignored by base64 decoders; padding forces full-result persistence in the delivery layer.
(OUT/'rollback-download-padded.txt').write_text('\n'*140000+encoded_files['rollback-all-completed.sql'],encoding='ascii')
for name in ['status.json','queue.json']:
    raw=(SRC/name).read_bytes();(OUT/name).write_bytes(raw)
    manifest['files'].append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'parts':[name]})
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
