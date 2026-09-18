#!/usr/bin/env python3
"""Requeue the five most recently completed posts for image-policy redesign."""
import datetime as dt,json
from pathlib import Path

POLICY_VERSION='recent-five-single-product-image-redesign-v12'

def now():return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def reset_recent(limit=5):
 root=Path(__file__).resolve().parents[1];out=root/'artifacts'/'city-content-queue';qpath=out/'queue.json'
 if not qpath.exists():raise RuntimeError('Queue file is missing')
 q=json.loads(qpath.read_text(encoding='utf-8'))
 if q.get('recent_image_reset_policy_version')==POLICY_VERSION:
  print('recent_image_reset=already_completed',flush=True);return []
 completed=[x for x in q.get('items',[]) if x.get('status')=='completed' and x.get('completed_at')]
 selected=sorted(completed,key=lambda x:x.get('completed_at',''),reverse=True)[:limit]
 ids=[]
 for item in selected:
  sid=str(item.get('source_id'));ids.append(sid)
  artifact=out/'items'/f'{sid}.json'
  if artifact.exists():
   try:
    data=json.loads(artifact.read_text(encoding='utf-8'))
    for name in data.get('images',[]) or []:(out/'images'/str(name)).unlink(missing_ok=True)
   except Exception:pass
  for folder in ('items','sql','rollback','image-reviews'):
   for path in (out/folder).glob(sid+'*'):path.unlink(missing_ok=True)
  item['status']='pending';item['attempts']=0;item['needs_regeneration']=True;item['regeneration_reason']='redesign last five images with single-product physics policy'
  for key in ('completed_at','failed_at','started_at','word_count','images','last_error'):item.pop(key,None)
 for path in (out/'packages').glob('*.zip'):
  path.unlink(missing_ok=True)
 for name in ('create-all-completed.sql','rollback-all-completed.sql'):(out/name).unlink(missing_ok=True)
 q['recent_image_reset_policy_version']=POLICY_VERSION;q['recent_image_reset_ids']=ids;q['updated_at']=now();q.setdefault('rules',{})['single_layflat_product_image_required']=True;q['rules']['image_physics_review_required']=True
 qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'recent_image_reset_count={len(ids)} ids={ids}',flush=True);return ids

if __name__=='__main__':reset_recent()
