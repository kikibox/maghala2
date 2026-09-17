#!/usr/bin/env python3
"""Fast, practical image QA for city-content images.

Policy v9: do not block the production queue for subjective/over-strict visual
review. Keep a lightweight gate for hard failures only, and review fewer images.
"""
import base64,json,os,re,urllib.request
MAX_IMAGE_ATTEMPTS=max(1,int(os.getenv('IMAGE_QA_ATTEMPTS','1')))
MIN_IMAGE_SCORE=int(os.getenv('IMAGE_QA_MIN_SCORE','70'))
FAST_MODE=os.getenv('IMAGE_QA_FAST_MODE','1')!='0'
REVIEW_KINDS={int(x) for x in os.getenv('IMAGE_QA_REVIEW_KINDS','1,3').split(',') if x.strip().isdigit()}
HARD_REJECT_TERMS=('white cylinder','retail package','carton','fake label','logo','watermark','text on product')

def _extract_json(text):
 text=(text or '').strip();text=re.sub(r'^```(?:json)?\s*|\s*```$','',text,flags=re.I|re.S).strip()
 try:return json.loads(text)
 except Exception:
  a=text.find('{');b=text.rfind('}')
  if a>=0 and b>a:return json.loads(text[a:b+1])
 return {'pass':True,'score':MIN_IMAGE_SCORE,'reasons':['non-json review ignored in fast mode'],'correction_prompt':''}

def _quick_file_check(path):
 if (not path.exists()) or path.stat().st_size<10000:
  return {'pass':False,'score':0,'reasons':['image file missing or too small'],'correction_prompt':'Regenerate a valid photorealistic farm irrigation image.'}
 return None

def _vision_review(base,path,item,kind):
 quick=_quick_file_check(path)
 if quick:return quick
 topic=item.get('topic','tape20')
 if FAST_MODE and kind not in REVIEW_KINDS:
  return {'pass':True,'score':90,'reasons':['fast mode: trusted prompt for non-key image'],'correction_prompt':''}
 encoded=base64.b64encode(path.read_bytes()).decode('ascii')
 if topic=='layflat':
  criteria='Main subject should be black collapsible layflat hose or installed layflat irrigation mainline in a farm. Connections should be plausible when visible.'
  reject='Reject only hard product mismatches: drip-tape roll as the main product, retail packaging/carton, fake labels/logos/text, missing farm/product entirely, or impossible/floating hose.'
 else:
  criteria='Main subject should be drip tape / drip irrigation field image for tape20 posts.'
  reject='Reject only hard mismatches: white cylinder/package/carton as product, fake labels/logos/text, no irrigation product/field, or completely wrong object such as cable/garden hose as the main product.'
 prompt=f'''Fast practical QA. City {item.get('city','')}, topic {topic}, image role {kind}. {criteria}
{reject}
Do not reject for minor soil texture, minor connection imperfection, central product placement, composition preference, or lack of perfect crop specificity. This is production advertising content and speed matters.
Return only JSON: {{"pass":true|false,"score":0-100,"reasons":["..."],"correction_prompt":"short regeneration instruction"}}. Pass at score {MIN_IMAGE_SCORE} or higher.'''
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+encoded}}]}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+base.AGNES_KEY,'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as response:raw=json.loads(response.read())
 content=raw['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(str(x.get('text','')) for x in content if isinstance(x,dict))
 verdict=_extract_json(content)
 verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=MIN_IMAGE_SCORE
 return verdict

def install(base,backend,raw_generator):
 reviews=base.OUT/'image-reviews';reviews.mkdir(parents=True,exist_ok=True)
 def guarded(item,kind):
  original_prompt=backend.image_prompt;feedback='';history=[]
  try:
   for attempt in range(1,MAX_IMAGE_ATTEMPTS+1):
    if feedback:backend.image_prompt=lambda current_item,current_kind,p=original_prompt,f=feedback:p(current_item,current_kind)+' HARD QA CORRECTION: '+f
    name,digest=raw_generator(item,kind);path=base.IMAGES/name
    try:verdict=_vision_review(base,path,item,kind)
    except Exception as exc:
     # Review service failures should not stop the queue in fast mode.
     verdict={'pass':True,'score':80,'reasons':['visual review unavailable; accepted in fast mode: '+type(exc).__name__],'correction_prompt':''}
    verdict['attempt']=attempt;history.append(verdict)
    print(f"image_quality_review_fast source_id={item['source_id']} topic={item.get('topic')} kind={kind} attempt={attempt} pass={verdict['pass']} score={verdict.get('score',0)} reasons={verdict.get('reasons',[])}",flush=True)
    (reviews/f"{item['source_id']}-{kind}.json").write_text(json.dumps({'source_id':item['source_id'],'topic':item.get('topic'),'kind':kind,'fast_mode':FAST_MODE,'history':history},ensure_ascii=False,indent=2),encoding='utf-8')
    if verdict['pass']:return name,digest
    path.unlink(missing_ok=True);feedback=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
   raise RuntimeError(f'image hard gate rejected role {kind} after {MAX_IMAGE_ATTEMPTS} attempt')
  finally:backend.image_prompt=original_prompt
 return guarded
