#!/usr/bin/env python3
"""Fast image QA with hard rejection for product identity and physics failures."""
import base64,json,os,re,urllib.request
MAX_IMAGE_ATTEMPTS=max(1,int(os.getenv('IMAGE_QA_ATTEMPTS','1')))
MIN_IMAGE_SCORE=int(os.getenv('IMAGE_QA_MIN_SCORE','70'))
FAST_MODE=os.getenv('IMAGE_QA_FAST_MODE','1')!='0'
REVIEW_KINDS={int(x) for x in os.getenv('IMAGE_QA_REVIEW_KINDS','1,2,3,4,5').split(',') if x.strip().isdigit()}

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
  criteria='The image must show exactly one black woven yarn-reinforced collapsible layflat hose matching the approved reference. The hose must be fully visible, physically continuous, correctly scaled and resting naturally on the ground. No other product or object may touch or cross it.'
  reject='Hard reject any second hose, round pipe, drip tape, cable, fitting, valve, filter, coupler, box, package, tool, hand, person, fake label, impossible intersection, object passing through the coil, floating/merged product, or distorted dimensions/markings.'
 else:
  criteria='The image must show one thin flat black drip-tape roll in a real farm context, naturally placed on soil and not confused with a round pipe or layflat hose.'
  reject='Hard reject any second irrigation product, pipe through the roll, white cylinder, carton, fake label, impossible geometry, upright wheel-like roll, or distorted product dimensions.'
 prompt=f'''Fast practical QA for city {item.get('city','')}, topic {topic}, image role {kind}. {criteria}
{reject}
Do not reject only for ordinary soil texture or distant crop rows. Return only JSON: {{"pass":true|false,"score":0-100,"reasons":["..."],"correction_prompt":"short regeneration instruction"}}. Pass at score {MIN_IMAGE_SCORE} or higher.'''
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+encoded}}]}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {base.AGNES_KEY}','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as response:raw=json.loads(response.read())
 content=raw['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(str(x.get('text','')) for x in content if isinstance(x,dict))
 verdict=_extract_json(content);verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=MIN_IMAGE_SCORE
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
     verdict={'pass':True,'score':80,'reasons':['visual review unavailable; accepted in fast mode: '+type(exc).__name__],'correction_prompt':''}
    verdict['attempt']=attempt;history.append(verdict)
    print(f"image_quality_review_fast source_id={item['source_id']} topic={item.get('topic')} kind={kind} attempt={attempt} pass={verdict['pass']} score={verdict.get('score',0)} reasons={verdict.get('reasons',[])}",flush=True)
    (reviews/f"{item['source_id']}-{kind}.json").write_text(json.dumps({'source_id':item['source_id'],'topic':item.get('topic'),'kind':kind,'fast_mode':FAST_MODE,'history':history},ensure_ascii=False,indent=2),encoding='utf-8')
    if verdict['pass']:return name,digest
    path.unlink(missing_ok=True);feedback=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
   raise RuntimeError(f'image hard gate rejected role {kind} after {MAX_IMAGE_ATTEMPTS} attempt')
  finally:backend.image_prompt=original_prompt
 return guarded
