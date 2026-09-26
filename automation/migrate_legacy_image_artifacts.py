#!/usr/bin/env python3
"""One-time reset of artifacts produced before the current image policy."""
import datetime as dt,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'city-content-queue';QUEUE=OUT/'queue.json';STATUS=OUT/'status.json';MARKER=OUT/'image-policy-migration.json';CURRENT_POLICY='field-first-multimodal-image-review-v3'
def now():return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def main():
 if MARKER.exists():
  try:
   state=json.loads(MARKER.read_text(encoding='utf-8'))
   if state.get('current_policy')==CURRENT_POLICY and state.get('completed') is True:print(f'image_policy_migration=already_completed policy={CURRENT_POLICY}',flush=True);return
  except Exception:pass
 if not QUEUE.exists():raise RuntimeError('Queue file is missing; refusing artifact reset')
 queue=json.loads(QUEUE.read_text(encoding='utf-8'));reset_ids=[];runtime_keys=('completed_at','failed_at','started_at','last_error','word_count','images')
 for item in queue.get('items',[]):
  if item.get('status')!='pending' or int(item.get('attempts',0))>0:
   reset_ids.append(item.get('source_id'));item['status']='pending';item['attempts']=0
   for key in runtime_keys:item.pop(key,None)
 deleted={}
 for folder_name in ('items','images','image-reviews','sql','rollback'):
  folder=OUT/folder_name;count=0
  if folder.exists():
   for path in folder.iterdir():
    if path.is_file():path.unlink();count+=1
  deleted[folder_name]=count
 for name in ('create-all-completed.sql','rollback-all-completed.sql'):
  path=OUT/name
  if path.exists():path.unlink();deleted[name]=1
 queue['updated_at']=now();queue.setdefault('rules',{})['image_policy_version']=CURRENT_POLICY;queue['rules']['legacy_image_artifacts_reset']=True;queue['rules']['image_quality_review_required']=True
 QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf-8');counts=Counter(item.get('status') for item in queue.get('items',[]))
 STATUS.write_text(json.dumps({'result':'reset_for_image_repair','updated_at':now(),'total':len(queue.get('items',[])),'pending':counts['pending'],'processing':counts['processing'],'completed':counts['completed'],'failed':counts['failed'],'blocked_image_model':counts['blocked_image_model'],'image_model':'agnes-image-2.5-flash','batch_size':1,'image_policy_version':CURRENT_POLICY,'legacy_items_reset':len(reset_ids)},ensure_ascii=False,indent=2),encoding='utf-8')
 marker={'current_policy':CURRENT_POLICY,'completed':True,'completed_at':now(),'reset_source_ids':reset_ids,'deleted_files':deleted};MARKER.write_text(json.dumps(marker,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'image_policy_migration=completed policy={CURRENT_POLICY} reset_items={len(reset_ids)} deleted={deleted}',flush=True)
if __name__=='__main__':main()
