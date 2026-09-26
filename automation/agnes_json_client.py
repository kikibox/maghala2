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


def call(base,prompt,attempts=None):
 if not base.AGNES_KEY:raise RuntimeError('AGNES_API_KEY is missing')
 if attempts is None:attempts=max(4,int(os.getenv('AGNES_JSON_ATTEMPTS','5')))
 last=None
 for attempt in range(1,attempts+1):
  retry_note=''
  if attempt>1:
   retry_note=(
    '\nپاسخ قبلی ناقص، خالی یا JSON نامعتبر بود. پاسخ را از ابتدا و به‌طور کامل بازسازی کن. '
    'فقط یک شیء JSON معتبر و بدون Markdown یا توضیح برگردان؛ همه کوتیشن‌ها و نویسه‌های کنترلی داخل رشته‌ها را درست escape کن. '
    f'خطای قبلی: {str(last)[:180]}')
  payload={
   'model':base.AGNES_MODEL,
   'messages':[
    {'role':'system','content':'شما نویسنده و بازبین ارشد فارسی در حوزه آبیاری کشاورزی هستید. فقط یک شیء JSON کامل و معتبر برگردانید؛ هیچ متن دیگری ننویسید.'},
    {'role':'user','content':prompt+retry_note},
   ],
   'temperature':0.25 if attempt>1 else 0.45,
   'max_tokens':20000,
  }
  try:
   base_timeout=max(60,int(os.getenv('AGNES_REQUEST_TIMEOUT','180')))
   request_timeout=min(360,base_timeout+(attempt-1)*30)
   data=base.fetch_json(
    base.AGNES_BASE+'/chat/completions',
    {'Authorization':'Bearer '+base.AGNES_KEY,'Content-Type':'application/json','User-Agent':'navar-city-content-queue-v8'},
    payload,timeout=request_timeout)
   raw=data.get('choices',[{}])[0].get('message',{}).get('content','')
   return parse_object(raw)
  except Exception as exc:
   last=exc
   print(f'agnes_json_retry attempt={attempt}/{attempts} timeout={request_timeout}s error={str(exc)[:240]}',flush=True)
   if attempt<attempts:time.sleep(min(20,2**attempt))
 raise RuntimeError('Agnes JSON response invalid after retries: '+str(last))
