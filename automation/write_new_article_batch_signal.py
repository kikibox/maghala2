#!/usr/bin/env python3
"""Persist the article ZIP names whose exact hash is not recorded as uploaded."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'article-content-queue';PACKAGES=OUT/'packages'
MANIFEST=PACKAGES/'manifest.json';STATE=OUT/'ftps-upload-state.json';SIGNAL=OUT/'.new-batch-signal'

def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def load(path,default):
 try:data=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return default
 return data if isinstance(data,dict) else default

def main()->int:
 if not MANIFEST.exists():
  print('No article package manifest; durable signal left unchanged');return 0
 tracked=load(STATE,{'files':{}}).get('files',{})
 manifest=load(MANIFEST,{'packages':[]});pending=[]
 for row in manifest.get('packages',[]):
  name=str(row.get('zip') or ((row.get('batch') or '')+'.zip')).strip()
  path=PACKAGES/Path(name).name
  if not name or not path.exists():continue
  digest=sha256(path);size=path.stat().st_size;previous=tracked.get(path.name,{})
  if previous.get('sha256')!=digest or int(previous.get('size',-1))!=size:pending.append(path.name)
 if pending:
  value='\n'.join(sorted(set(pending)))+'\n'
  SIGNAL.write_text(value,encoding='utf-8')
  print(f'article_ftps_pending={len(pending)} names={pending}')
 else:
  print('article_ftps_pending=0; durable signal left unchanged')
 return 0
if __name__=='__main__':raise SystemExit(main())
