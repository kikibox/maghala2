#!/usr/bin/env python3
"""Reliable Agnes JSON client with extraction and bounded retries."""
import json,os,re,time
FENCE_RE=re.compile(r"```(?:json)?\s*(.*?)\s*```",re.I|re.S)
def _decode(candidate):
 value=json.loads(candidate)
 if isinstance(value,str):value=json.loads(value)
 if not isinstance(value,dict):raise ValueError('JSON root must be an object')
 return value
def parse_object(raw):
 if isinstance(raw,dict):return raw
 text=str(raw or '').strip()
 if not text:raise ValueError('empty Agnes response')
 candidates=[text]+FENCE_RE.findall(text);start=text.find('{');end=text.rfind('}')
 if start>=0 and end>start:candidates.append(text[start:end+1])
 errors=[];seen=set()
 for candidate in candidates:
  candidate=candidate.strip()
  if not candidate or candidate in seen:continue
  seen.add(candidate)
  try:return _decode(candidate)
  except Exception as exc:errors.append(str(exc))
 raise ValueError('no valid JSON object found: '+'; '.join(errors[-3:]))
def call(base,prompt,attempts=4):
 if not base.AGNES_KEY:raise RuntimeError('AGNES_API_KEY is missing')
 last=None
 for attempt in range(1,attempts+1):
  retry_note='' if attempt==1 else '\nپاسخ قبلی خالی یا نامعتبر بود. فقط یک شیء JSON معتبر و بدون توضیح یا Markdown برگردان.'
  payload={'model':base.AGNES_MODEL,'messages':[{'role':'system','content':'شما نویسنده و بازبین ارشد فارسی در حوزه آبیاری کشاورزی هستید. فقط یک شیء JSON معتبر برگردانید.'},{'role':'user','content':prompt+retry_note}],'temperature':0.55 if attempt>1 else 0.66,'max_tokens':20000}
  try:
   request_timeout=max(30,int(os.getenv('AGNES_REQUEST_TIMEOUT','120')))
   data=base.fetch_json(base.AGNES_BASE+'/chat/completions',{'Authorization':'Bearer '+base.AGNES_KEY,'Content-Type':'application/json','User-Agent':'navar-city-content-queue-v7'},payload,timeout=request_timeout)
   raw=data.get('choices',[{}])[0].get('message',{}).get('content','')
   return parse_object(raw)
  except Exception as exc:
   last=exc;print(f'agnes_json_retry attempt={attempt}/{attempts} error={str(exc)[:240]}',flush=True)
   if attempt<attempts:time.sleep(min(12,2**attempt))
 raise RuntimeError('Agnes JSON response invalid after retries: '+str(last))
