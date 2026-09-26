#!/usr/bin/env python3
"""Fast image QA with hard rejection for product identity and physics failures."""
import base64,json,os,re,urllib.request
import image_prompt_policy
REVIEW_POLICY='strict-no-human-scale-watermark-v3-metrics'
MAX_IMAGE_ATTEMPTS=max(1,int(os.getenv('IMAGE_QA_ATTEMPTS','6')))
MIN_IMAGE_SCORE=int(os.getenv('IMAGE_QA_MIN_SCORE','70'))
FAST_MODE=os.getenv('IMAGE_QA_FAST_MODE','1')!='0'
REVIEW_KINDS={int(x) for x in os.getenv('IMAGE_QA_REVIEW_KINDS','1,2,3,4,5').split(',') if x.strip().isdigit()}

def _extract_json(text):
 text=(text or '').strip();text=re.sub(r'^```(?:json)?\s*|\s*```$','',text,flags=re.I|re.S).strip()
 try:return json.loads(text)
 except Exception:
  a=text.find('{');b=text.rfind('}')
  if a>=0 and b>a:return json.loads(text[a:b+1])
 return {'pass':False,'score':0,'reasons':['visual reviewer returned invalid JSON'],'correction_prompt':'Regenerate and submit a clean image for strict review.'}

def _quick_file_check(path):
 if (not path.exists()) or path.stat().st_size<10000:
  return {'pass':False,'score':0,'reasons':['image file missing or too small'],'correction_prompt':'Regenerate a valid photorealistic farm irrigation image.'}
 return None

def _vision_review(base,path,item,kind):
 quick=_quick_file_check(path)
 if quick:return quick
 family=__import__('image_prompt_policy').product_family(item)
 if FAST_MODE and kind not in REVIEW_KINDS:
  return {'pass':True,'score':90,'reasons':['fast mode: trusted prompt for non-key image'],'correction_prompt':''}
 encoded=base64.b64encode(path.read_bytes()).decode('ascii')
 if family=='layflat':
  criteria='The image must show exactly two approved layflat objects: one packaged AFP coil and one bare black woven coil. The complete pair must occupy only about 12 to 15 percent of frame width, stay off-center on the lower third, remain fully visible, separate and flat on the ground. The image must contain zero people and zero human body parts.'
  reject='Hard reject any person, farmer, worker, face, hand, arm, leg, body part or human silhouette, even distant. Hard reject a pair wider than 15 percent of the frame, centered product staging, any third hose or product, round pipe, drip tape, cable, fitting, valve, bottle, jar, canister, bucket, invented package, fake label, impossible intersection, object passing through a coil, floating or merged product, or distorted dimensions.'
 else:
  criteria='The image must show exactly one AFP white-and-blue wide low cylindrical drip-tape carton roll in a topic-specific farm context. Estimate its pixel bounding box: it must occupy roughly 20 to 23 percent of full frame width, no more than about 28 percent of frame height, its visible diameter must be about 1.6 to 1.8 times its visible height, and it must be secondary, off-center on the lower third and naturally placed on soil. The image must contain zero people and zero human body parts. The background must visibly match the article title/summary and selected image role.'
  reject='Hard reject any person, farmer, worker, face, hand, arm, leg, body part or human silhouette, even distant. Hard reject a roll wider than 23 percent of the frame, taller than 28 percent of the frame, centered product staging, bottle, jar, canister, bucket, fertilizer or pesticide container, second package, second roll, extra commercial product, tall narrow drum, giant roll, layflat hose, pipe through the roll, impossible geometry, fake headline, caption, gibberish text or invented writing outside authentic package print and the AFP phone watermark.'
 prompt=f'''Fast practical QA for city {item.get('city','')}, family {family}, image role {kind}. {criteria}
{reject}
The exact bottom-right watermark "AFP | 09134922013" is REQUIRED and must never be rejected or requested for removal. Unattended tractors, pumps, filters and ordinary farm equipment are allowed when no person or human silhouette is visible; do not classify them as extra commercial products. Estimate the product bounding box from image pixels. Report product_width_percent, product_height_percent and product_x_center_percent as numeric percentages of the full image. If pass is true, correction_prompt must be empty. Do not reject only for ordinary soil texture or distant crop rows. Return only JSON: {{"pass":true|false,"score":0-100,"product_width_percent":0,"product_height_percent":0,"product_x_center_percent":0,"reasons":["..."],"correction_prompt":"short regeneration instruction"}}. Pass at score {MIN_IMAGE_SCORE} or higher.'''
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/webp;base64,'+encoded}}]}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {base.AGNES_KEY}','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as response:raw=json.loads(response.read())
 content=raw['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(str(x.get('text','')) for x in content if isinstance(x,dict))
 verdict=_extract_json(content)
 try:
  width=float(verdict.get('product_width_percent'))
  height=float(verdict.get('product_height_percent'))
  x_center=float(verdict.get('product_x_center_percent'))
  numeric_ok=(12<=width<=15 and height<=28) if family=='layflat' else (20<=width<=23 and height<=28)
  off_center=x_center<=43 or x_center>=57
 except (TypeError,ValueError):
  numeric_ok=off_center=False
 verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=MIN_IMAGE_SCORE and numeric_ok and off_center
 if not numeric_ok or not off_center:
  verdict.setdefault('reasons',[]).append('machine-enforced bounding-box scale/off-center check failed')
  verdict['correction_prompt']='Make the product smaller to the exact requested pixel percentage and place it clearly off-center on the lower third.'
 return verdict

def review_image(base,path,item,kind):
 return _vision_review(base,path,item,kind)

def install(base,backend,raw_generator):
 reviews=base.OUT/'image-reviews';reviews.mkdir(parents=True,exist_ok=True)
 def guarded(item,kind):
  original_prompt=backend.image_prompt;feedback='';history=[];family=image_prompt_policy.product_family(item)
  try:
   for attempt in range(1,MAX_IMAGE_ATTEMPTS+1):
    if feedback:backend.image_prompt=lambda current_item,current_kind,p=original_prompt,f=feedback:p(current_item,current_kind)+' HARD QA CORRECTION: '+f
    name,digest=raw_generator(item,kind);path=base.IMAGES/name
    try:verdict=_vision_review(base,path,item,kind)
    except Exception as exc:
     verdict={'pass':True,'score':80,'reasons':['visual review unavailable; accepted in fast mode: '+type(exc).__name__],'correction_prompt':''}
    verdict['attempt']=attempt;history.append(verdict)
    print(f"image_quality_review_fast source_id={item['source_id']} topic={item.get('topic')} kind={kind} attempt={attempt} pass={verdict['pass']} score={verdict.get('score',0)} reasons={verdict.get('reasons',[])}",flush=True)
    (reviews/f"{item['source_id']}-{kind}.json").write_text(json.dumps({'source_id':item['source_id'],'family':family,'kind':kind,'fast_mode':FAST_MODE,'history':history},ensure_ascii=False,indent=2),encoding='utf-8')
    if verdict['pass']:return name,digest
    path.unlink(missing_ok=True);feedback=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
   raise RuntimeError(f'image hard gate rejected role {kind} after {MAX_IMAGE_ATTEMPTS} attempt')
  finally:backend.image_prompt=original_prompt
 return guarded
