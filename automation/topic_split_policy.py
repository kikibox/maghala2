#!/usr/bin/env python3
"""Split city topics and enforce the single packaged layflat reference policy."""
import json,re
from pathlib import Path
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
TOPICS={'tape20':{'slug_suffix':'navar-tip-20cm','title_fa':'نوار تیپ ۲۰ سانتی','focus':'انتخاب و خرید نوار تیپ آبیاری ۲۰ سانتی‌متر','image_focus':'one black flat drip-tape roll on soil','forbidden':'Do not show layflat hose, yarn hose, PE pipe, filters, valves, couplers or other irrigation hardware.'},'layflat':{'slug_suffix':'looleh-nakhi-tashoo','title_fa':'لوله نخی و لوله تاشو','focus':'انتخاب و خرید لوله نخی و لوله تاشو کشاورزی برای انتقال آب','image_focus':'only the one packaged black woven yarn-reinforced collapsible layflat hose roll from the approved reference','forbidden':'Do not show drip tape, a second hose, round pipe, cable, fitting, valve, filter, coupler, box, tool, hand, person or any other product. Do not unwrap or install the packaged roll.'}}
SOIL_VARIANTS=['fine loamy brown soil with realistic clods','sandy-loam tan soil with granular texture','clay-loam soil with darker natural patches','stony agricultural soil with scattered pebbles']
def _topic_item(item,key):
 t=TOPICS[key];new=dict(item);new['base_source_id']=item.get('base_source_id',item.get('source_id'));new['topic']=key;new['topic_title']=t['title_fa'];new['topic_focus']=t['focus'];new['topic_forbidden']=t['forbidden'];new['source_id']=f"{item.get('source_id')}-{key}";base_slug=re.sub(r'-(navar-tip-20cm|looleh-nakhi-tashoo)$','',str(item.get('slug','')));new['slug']=f"{base_slug}-{t['slug_suffix']}";new['status']='pending';new['attempts']=0
 for k in ('started_at','completed_at','failed_at','last_error','images','word_count'):new.pop(k,None)
 return new
def _split_items(items):
 out=[];seen=set()
 for item in items:
  if item.get('topic') in TOPICS:
   key=(item.get('base_source_id',item.get('source_id')),item.get('topic'))
   if key not in seen:seen.add(key);out.append(item)
  else:
   for key in ('tape20','layflat'):
    ni=_topic_item(item,key);ident=(ni.get('base_source_id'),ni.get('topic'))
    if ident not in seen:seen.add(ident);out.append(ni)
 return out
def _patch_queue_file(base):
 if not base.QUEUE.exists():return
 q=json.loads(base.QUEUE.read_text(encoding='utf-8'));q['items']=_split_items(q.get('items',[]));q['updated_at']=base.now();q['scope']='all missing cities split into tape20 and layflat topics';q['version']=max(int(q.get('version',1)),2);q['topics_per_city']=2;q['topic_policy']=TOPICS;base.QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
def install_queue_split(base):
 original=base.initialize
 def initialize(force=False):
  q=original(force);q['items']=_split_items(q.get('items',[]));q['scope']='all missing cities split into tape20 and layflat topics';q['version']=max(int(q.get('version',1)),2);q['topics_per_city']=2;q['topic_policy']=TOPICS;q['updated_at']=base.now();base.QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
  try:base.write_status(q,'topic_split_ready')
  except Exception:pass
  return q
 base.initialize=initialize;_patch_queue_file(base)
def _extract_paragraph_context(item,kind,topic_key='tape20'):
 research=item.get('city_research') or {};seed=abs(hash(str(item.get('source_id',''))+':'+str(kind)));return 'generic Iranian crop rows only; do not invent a specific crop',''+SOIL_VARIANTS[seed%len(SOIL_VARIANTS)],'simple natural agricultural background'
def install_image_policy(image_prompt_policy):
 def reference_images(kind,item=None):
  return [LAYFLAT_REFERENCE_PACKAGE] if isinstance(item,dict) and item.get('topic')=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]
 def image_prompt(item,kind):
  if item.get('topic','tape20')=='layflat':return 'Photorealistic product photograph. Use only the one approved packaged layflat hose reference image. Show exactly one packaged black woven yarn-reinforced hose roll, fully visible and physically intact. Do not unwrap, install, hold or add any second hose, pipe, tape, fitting, box, tool, hand, person or other product. Nothing may cross or pass through the package. Respect its dimensions, weave, straps and genuine markings. No invented text or watermark.'
  return 'Photorealistic product photograph of one black flat drip-tape roll on natural soil. No layflat hose, pipe, fittings, packaging, tools or other product. No impossible geometry or invented text.'
 image_prompt_policy.reference_images=reference_images;image_prompt_policy.image_prompt=image_prompt
def install_all():
 import city_content_queue as base, image_prompt_policy
 install_queue_split(base);install_image_policy(image_prompt_policy)
