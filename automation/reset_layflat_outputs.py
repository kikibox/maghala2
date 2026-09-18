#!/usr/bin/env python3
"""Reset completed layflat posts once for the packaged-reference-only policy."""
import json
from pathlib import Path
POLICY_VERSION='layflat-packaged-reference-only-v13-once'
def reset_layflat(root=None):
 root=Path(root or Path(__file__).resolve().parents[1]);out=root/'artifacts'/'city-content-queue';qpath=out/'queue.json'
 if not qpath.exists():return 0
 q=json.loads(qpath.read_text(encoding='utf-8'))
 if q.get('layflat_reset_policy_version')==POLICY_VERSION:return 0
 changed=0
 for item in q.get('items',[]):
  if item.get('topic')=='layflat' and item.get('status')=='completed':
   item['status']='pending';item['attempts']=0;item['needs_regeneration']=True;item['regeneration_reason']='rebuild with only the approved packaged layflat reference; no hand-held reference'
   item['layflat_reset_policy_version']=POLICY_VERSION
   for key in ('completed_at','failed_at','started_at','images','word_count','last_error'):item.pop(key,None)
   sid=str(item.get('source_id'))
   for folder in ('items','sql','rollback'):
    for path in (out/folder).glob(sid+'*'):path.unlink(missing_ok=True)
   for path in (out/'images').glob('*'+sid+'*'):path.unlink(missing_ok=True)
   changed+=1
 q['layflat_reset_policy_version']=POLICY_VERSION;q['layflat_reset_policy']='completed layflat posts rebuilt with only the approved packaged reference';q['updated_at']=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).replace(microsecond=0).isoformat();qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');return changed
if __name__=='__main__':print('layflat_reset_count=',reset_layflat())
