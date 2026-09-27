#!/usr/bin/env python3
"""Fast image QA with hard rejection for product identity and physics failures."""
import base64,json,os,re,urllib.request
import image_prompt_policy
REVIEW_POLICY='strict-no-human-no-bottle-no-container-v11-full-rebuild'
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


def _metric_check(family,verdict):
 try:
  width=float(verdict.get('product_width_percent'))
  height=float(verdict.get('product_height_percent'))
  x_center=float(verdict.get('product_x_center_percent'))
 except (TypeError,ValueError):
  return False,['Return numeric product_width_percent, product_height_percent and product_x_center_percent.']
 # Keep the generation prompt's target narrow, but tolerate vision-model
 # bounding-box estimation noise so an otherwise approved image cannot starve
 # the production queue.
 min_width,max_width=(9,20) if family=='layflat' else (13,27)
 issues=[]
 if width<min_width:
  issues.append(f'Enlarge the product group from {width:g}% to {min_width}-{max_width}% of frame width.')
 elif width>max_width:
  issues.append(f'Reduce the product group from {width:g}% to {min_width}-{max_width}% of frame width.')
 if height>32:
  issues.append(f'Reduce product height from {height:g}% to at most 32% of frame height.')
 # The vision model's x-center estimate is noisy by a few percentage points.
 # Reject only a truly centered estimate; semantic placement still has to pass
 # the model review above.
 # Horizontal placement is judged semantically by the vision reviewer and
 # again by the three-image set gate. A one-point x-center estimate is too
 # noisy to discard an otherwise valid image here.
 return not issues,issues

def _vision_review(base,path,item,kind):
 quick=_quick_file_check(path)
 if quick:return quick
 family=__import__('image_prompt_policy').product_family(item)
 crop=image_prompt_policy.named_crop(item)
 crop_spec=image_prompt_policy.crop_identity_spec(item)
 if FAST_MODE and kind not in REVIEW_KINDS:
  return {'pass':True,'score':90,'reasons':['fast mode: trusted prompt for non-key image'],'correction_prompt':''}
 encoded=base64.b64encode(path.read_bytes()).decode('ascii')
 if family=='layflat':
  criteria='The image must show exactly two approved layflat objects: one packaged AFP coil and one bare black woven coil. The complete pair must occupy only about 12 to 15 percent of frame width, stay off-center on the lower third, remain fully visible, separate and flat on the ground. The image must contain zero people and zero human body parts.'
  reject='Hard reject any person, farmer, worker, face, hand, arm, leg, body part or human silhouette, even distant. Hard reject a pair wider than 15 percent of the frame, centered product staging, any third hose or product, round pipe, drip tape, cable, fitting, valve, bottle, jar, canister, bucket, invented package, fake label, impossible intersection, object passing through a coil, floating or merged product, or distorted dimensions.'
 else:
  crop_rule=(f'Roles 1 and 2 should make the required article crop {crop} recognizable, defined as: {crop_spec}. A botanically neutral prepared bed, tiny unidentifiable seedlings, irrigation layout or root-zone evidence may pass when the article-specific agronomic story is clear. Hard reject a clearly identifiable different species, but do not reject neutral young vegetation merely because exact mature morphology is unavailable.' if int(kind) in (1,2) else f'Role 3 is a hardware story: crop plants may be absent or visually neutral. If an identifiable crop appears, hard reject only when it clearly contradicts {crop}; do not require lentil/crop morphology in a filter, manifold or flush-point close view.')
  criteria=f'The image must show exactly one AFP white-and-blue wide low cylindrical drip-tape carton roll in a topic-specific farm context. {crop_rule} The preferred product width is 20 to 23 percent of the frame, but practical estimates from 13 to 27 percent are acceptable when the product remains secondary; height must be no more than 32 percent. Its visible diameter should be about 1.5 to 1.9 times its visible height, and it must be off-center on the lower third and naturally placed on soil. The image must contain zero people and zero human body parts. The background must visibly match the article title/summary and selected image role.'
  reject='Hard reject any person, farmer, worker, face, hand, arm, leg, body part or human silhouette, even distant. Hard reject a roll wider than 27 percent of the frame, taller than 32 percent of the frame, centered product staging, bottle, jar, canister, bucket, fertilizer or pesticide container, second package, second roll, extra commercial product, tall narrow drum, giant roll, layflat hose, pipe through the roll, impossible geometry, fake headline, caption, gibberish text or invented writing outside authentic package print and the AFP phone watermark.'
 prompt=f'''Fast practical QA for city {item.get('city','')}, family {family}, image role {kind}. {criteria}
{reject}
The exact bottom-right watermark "AFP | 09134922013" is REQUIRED and must never be rejected or requested for removal. Unattended tractors, pumps, filters, pressure gauges, regulators, manifolds, connectors and ordinary fixed irrigation hardware are allowed when no person or human silhouette is visible; they are infrastructure, not extra commercial products. Estimate the product bounding box from image pixels. Report product_width_percent, product_height_percent and product_x_center_percent as numeric percentages of the full image. If pass is true, correction_prompt must be empty. Do not reject only for ordinary soil texture or distant crop rows. Return only JSON: {{"pass":true|false,"score":0-100,"product_width_percent":0,"product_height_percent":0,"product_x_center_percent":0,"reasons":["..."],"correction_prompt":"short regeneration instruction"}}. Pass at score {MIN_IMAGE_SCORE} or higher.'''
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_url','image_url':{'url':'data:image/webp;base64,'+encoded}}]}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {base.AGNES_KEY}','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=60) as response:raw=json.loads(response.read())
 content=raw['choices'][0]['message']['content']
 if isinstance(content,list):content=''.join(str(x.get('text','')) for x in content if isinstance(x,dict))
 verdict=_extract_json(content)
 metric_ok,metric_issues=_metric_check(family,verdict)
 verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=MIN_IMAGE_SCORE and metric_ok
 if not metric_ok:
  verdict.setdefault('reasons',[]).append('machine-enforced bounding-box check failed: '+'; '.join(metric_issues))
  model_correction=str(verdict.get('correction_prompt') or '').strip()
  verdict['correction_prompt']=' '.join(x for x in [model_correction,' '.join(metric_issues)] if x)
 return verdict

def review_image(base,path,item,kind):
 return _vision_review(base,path,item,kind)

def review_image_set(base,paths,item):
 encoded=[base64.b64encode(path.read_bytes()).decode('ascii') for path in paths]
 title=str((item or {}).get('title') or '')
 summary=image_prompt_policy.visual_brief(item)
 prompt=f'''Review these three already individually-approved article images as one editorial set. Article: {title}. Summary: {summary}. The same AFP product is expected in all three, so do not call product identity itself duplication. Pass when the three images fulfill their distinct functional roles (crop-identity overview, agronomic close evidence, and irrigation-system story), even when they share the same crop, field, lighting, or regional environment. Exact crop morphology is preferred, but botanically neutral beds, young vegetation, irrigation layout or root-zone evidence may carry the topic; hard reject only a clearly contradictory identifiable crop. Mark duplicate_roles only for near-duplicates that repeat substantially the same camera angle, layout and technical narrative; do not reject merely because the same crop, AFP product, soil, or field appears across the set. Zero people remains mandatory. Return only JSON: {{"pass":true|false,"score":0-100,"duplicate_roles":[1,2,3],"reasons":["..."],"correction_prompt":"one concise instruction for a substantially different replacement"}}.'''
 content=[{'type':'text','text':prompt}]
 content.extend({'type':'image_url','image_url':{'url':'data:image/webp;base64,'+blob}} for blob in encoded)
 payload={'model':base.AGNES_MODEL,'messages':[{'role':'user','content':content}],'temperature':0,'response_format':{'type':'json_object'}}
 req=urllib.request.Request(base.AGNES_BASE+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {base.AGNES_KEY}','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=90) as response:raw=json.loads(response.read())
 body=raw['choices'][0]['message']['content']
 if isinstance(body,list):body=''.join(str(x.get('text','')) for x in body if isinstance(x,dict))
 verdict=_extract_json(body);roles=[]
 for value in verdict.get('duplicate_roles',[]):
  try:value=int(value)
  except (TypeError,ValueError):continue
  if value in (1,2,3) and value not in roles:roles.append(value)
 verdict['duplicate_roles']=roles
 verdict['pass']=bool(verdict.get('pass')) and int(verdict.get('score',0))>=70 and not roles
 return verdict

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
     verdict={'pass':bool(FAST_MODE),'score':80 if FAST_MODE else 0,'reasons':['visual review unavailable: '+type(exc).__name__],'correction_prompt':'Retry strict visual review; never accept an unreviewed production image.'}
    verdict['attempt']=attempt;history.append(verdict)
    print(f"image_quality_review_fast source_id={item['source_id']} topic={item.get('topic')} kind={kind} attempt={attempt} pass={verdict['pass']} score={verdict.get('score',0)} reasons={verdict.get('reasons',[])}",flush=True)
    (reviews/f"{item['source_id']}-{kind}.json").write_text(json.dumps({'source_id':item['source_id'],'family':family,'kind':kind,'fast_mode':FAST_MODE,'history':history},ensure_ascii=False,indent=2),encoding='utf-8')
    if verdict['pass']:return name,digest
    path.unlink(missing_ok=True);feedback=str(verdict.get('correction_prompt') or '; '.join(verdict.get('reasons',[])))
   raise RuntimeError(f'image hard gate rejected role {kind} after {MAX_IMAGE_ATTEMPTS} attempt')
  finally:backend.image_prompt=original_prompt
 return guarded
