#!/usr/bin/env python3
"""Reset transient JSON failures, install robust Agnes parsing, and run QA v7."""
import json,runpy
from pathlib import Path
import city_content_queue as base
import agnes_json_client
HERE=Path(__file__).resolve().parent
if base.QUEUE.exists():
 state=json.loads(base.QUEUE.read_text(encoding='utf-8'));changed=False
 for item in state.get('items',[]):
  error=str(item.get('last_error',''))
  if item.get('status')=='failed' and any(term in error for term in ('Expecting value','JSON response invalid','empty Agnes response','no valid JSON object')):
   item['status']='pending';item['attempts']=0;changed=True
   for key in ('last_error','failed_at','started_at'):item.pop(key,None)
 if changed:
  state['updated_at']=base.now();base.QUEUE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
  print('reset_transient_json_failures=true',flush=True)
def resilient_agnes(prompt):return agnes_json_client.call(base,prompt,4)
base.agnes=resilient_agnes
runpy.run_path(str(HERE/'run_agnes_city_queue_seo.py'),run_name='__main__')
