#!/usr/bin/env python3
"""Run the Cloudflare city queue with publish status in generated SQL."""
import json
import city_content_queue as base
import city_content_queue_cloudflare as queue

_original_sql_for=queue.sql_for

def published_sql_for(item,obj,image_names):
    insert,rollback,body=_original_sql_for(item,obj,image_names)
    insert=insert.replace("'draft','closed','closed'","'publish','closed','closed'",1)
    return insert,rollback,body

queue.sql_for=published_sql_for
base.IMAGE_MODEL=queue.MODEL
state=base.initialize(False)
queue.migrate(state)
state['rules']['draft_only']=False
state['rules']['post_status']='publish'
state['updated_at']=base.now()
base.QUEUE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
queue.process(state)
combined=base.OUT/'create-all-completed.sql'
if combined.exists():
    text=combined.read_text(encoding='utf-8').replace('-- Review before importing. All generated posts are drafts.','-- Review before importing. Generated posts use publish status.')
    combined.write_text(text,encoding='utf-8')
