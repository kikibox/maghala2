#!/usr/bin/env python3
"""Upload only signaled new/changed 50-article ZIPs over explicit FTPS."""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from upload_city_batches_ftps import connect
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'article-content-queue';PACKAGES=OUT/'packages'
SIGNAL=OUT/'.new-batch-signal';STATE=OUT/'ftps-upload-state.json'

def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def load(path,default):
 try:data=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return default
 return data if isinstance(data,dict) else default
def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def main():
 state=load(STATE,{'files':{}});tracked=state.setdefault('files',{});pending=[];skipped=0
 if SIGNAL.exists():
  for raw in SIGNAL.read_text(encoding='utf-8').splitlines():
   name=Path(raw.strip()).name
   if not name:continue
   if not name.endswith('.zip'):name+='.zip'
   path=PACKAGES/name
   if not path.exists():raise RuntimeError(f'signaled article package missing: {name}')
   digest=sha256(path);size=path.stat().st_size;previous=tracked.get(name,{})
   if previous.get('sha256')==digest and int(previous.get('size',-1))==size:skipped+=1
   else:pending.append((path,digest,size))
 if not pending:
  print(json.dumps({'uploaded':0,'skipped':skipped,'checked':skipped},ensure_ascii=False));return 0
 ftp=connect();uploaded=0
 try:
  for path,digest,size in pending:
   temp=f'.{path.name}.uploading'
   with path.open('rb') as stream:ftp.storbinary(f'STOR {temp}',stream,blocksize=1024*1024)
   remote_size=ftp.size(temp)
   if remote_size!=size:
    try:ftp.delete(temp)
    finally:raise RuntimeError(f'size verification failed for {path.name}: local={size} remote={remote_size}')
   try:ftp.delete(path.name)
   except Exception:pass
   ftp.rename(temp,path.name)
   tracked[path.name]={'sha256':digest,'size':size,'uploaded_at':now()};uploaded+=1
   print(f'Uploaded and verified article package: {path.name} ({size} bytes)')
 finally:
  try:ftp.quit()
  except Exception:ftp.close()
 state['last_run']={'uploaded':uploaded,'skipped':skipped,'checked':uploaded+skipped,'completed_at':now()}
 STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(state['last_run'],ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
