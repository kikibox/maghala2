#!/usr/bin/env python3
"""Split city queue topics and enforce product-correct image prompts.

Current image policy v12:
- tape20: only the drip tape roll product in a farm context; no pipes/system parts.
  The product roll must sit naturally on soil, never upright like a wheel, never
  wrapped around/encircling another pipe, spool, box, label, or cylinder.
- layflat: the approved black yarn-reinforced layflat hose reference is mandatory.
"""
import json
import re
from pathlib import Path

DRIP_TAPE_ROLL_REFERENCE = 'https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_ROLL = 'https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
LAYFLAT_REFERENCE_INSTALLED = 'https://navar-abyari.ir/wp-content/uploads/Gemini_Generated_Image_305tna305tna305t.webp'

TOPICS = {
    'tape20': {
        'slug_suffix': 'navar-tip-20cm',
        'title_fa': 'نوار تیپ ۲۰ سانتی',
        'focus': 'انتخاب و خرید نوار تیپ آبیاری ۲۰ سانتی‌متر',
        'image_focus': 'only one black drip irrigation tape roll product lying flat or slightly angled on real farm soil; no central white core, no packaging, no pipe through the roll, no object inside the roll',
        'forbidden': 'Do not show layflat hose, yarn hose, foldable hose, PE main pipe, filters, regulators, valves, couplers, lateral pipe networks or installed irrigation system hardware in tape20 images. Do not put a pipe, cylinder, package, label or any object inside the roll. Do not make the roll stand upright like a wheel. Only show the drip tape roll product naturally placed on soil.',
    },
    'layflat': {
        'slug_suffix': 'looleh-nakhi-tashoo',
        'title_fa': 'لوله نخی و لوله تاشو',
        'focus': 'انتخاب و خرید لوله نخی و لوله تاشو کشاورزی برای انتقال آب',
        'image_focus': 'the exact approved product family: black woven yarn-reinforced collapsible layflat hose like the reference image لوله-نخی-2-اینچ-1.webp, visibly used as roll, partly unrolled hose, or mainline in a real farm',
        'forbidden': 'Do not make 20 cm drip tape the article subject. Do not use thin drip-tape roll imagery as the main product. Do not generate a smooth generic black pipe, PE pipe, garden hose, corrugated hose, cable, or random irrigation tube. The visible product must resemble the approved black woven layflat/yarn hose reference.',
    },
}

CROP_HINTS = {'صیفی':'vegetable beds with cucumbers, tomatoes, peppers, melons or watermelons when supported by the paragraph or city research','سبزی':'leafy vegetable rows and low vegetable beds','گوجه':'tomato rows with stakes or low tomato plants','خیار':'cucumber rows or trellised cucumber beds','فلفل':'pepper crop rows','هندوانه':'watermelon field with vines on soil','خربزه':'melon field with low vines on soil','سیب زمینی':'potato ridges and furrows','پیاز':'onion rows in raised beds'}
SOIL_VARIANTS=['fine loamy brown soil with small clods and realistic tractor furrows','sandy-loam tan soil with granular texture and wetting patterns near the product','clay-loam soil with darker moist patches, cracked dry margins and uneven aggregates','stony agricultural soil with scattered pebbles, clods and compacted row shoulders','raised vegetable beds with crumbly tilled soil and visible wet-dry contrast']
TAPE_BACKGROUNDS=['low camera angle focused on a horizontally placed roll product with crop rows softly visible behind it','diagonal crop rows with the drip tape roll staged naturally on soil, no pipe line passing through it','close product advertising view with realistic soil texture, clean hollow center, and no label/core object','wide farm context view where the drip tape roll is the only irrigation product shown','technical product-only scene focused on roll texture, edges and flat tape layers, no pipes or fittings']
LAYFLAT_BACKGROUNDS=['low camera angle focused on the black woven layflat hose texture with farm rows behind it','diagonal farm rows with the approved-style black layflat hose crossing the foreground','close equipment view where woven hose wall, flattened body and real coupler are visible','wide field view with the black layflat mainline as the visible hero product','technical scene focused on installed layflat hose, takeoff valves, laterals and soil texture']

def _topic_item(item, topic_key):
    topic=TOPICS[topic_key]; new=dict(item); new['base_source_id']=item.get('base_source_id',item.get('source_id')); new['topic']=topic_key; new['topic_title']=topic['title_fa']; new['topic_focus']=topic['focus']; new['topic_forbidden']=topic['forbidden']; new['source_id']=f"{item.get('source_id')}-{topic_key}"; base_slug=re.sub(r'-(navar-tip-20cm|looleh-nakhi-tashoo)$','',str(item.get('slug',''))); new['slug']=f"{base_slug}-{topic['slug_suffix']}"; new['status']='pending'; new['attempts']=0
    for key in ('started_at','completed_at','failed_at','last_error','images','word_count'): new.pop(key,None)
    return new

def _split_items(items):
    out=[]; seen=set()
    for item in items:
        if item.get('topic') in TOPICS:
            key=(item.get('base_source_id',item.get('source_id')),item.get('topic'))
            if key not in seen: seen.add(key); out.append(item)
            continue
        for topic_key in ('tape20','layflat'):
            ni=_topic_item(item,topic_key); key=(ni.get('base_source_id'),ni.get('topic'))
            if key not in seen: seen.add(key); out.append(ni)
    return out

def _patch_queue_file(base):
    qpath=base.QUEUE
    if not qpath.exists(): return
    q=json.loads(qpath.read_text(encoding='utf-8')); q['items']=_split_items(q.get('items',[])); q['updated_at']=base.now(); q['scope']='all missing cities split into tape20 and layflat topics'; q['version']=max(int(q.get('version',1)),2); q['topics_per_city']=2; q['topic_policy']=TOPICS; qpath.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')

def install_queue_split(base):
    original_initialize=base.initialize
    def initialize(force=False):
        q=original_initialize(force); q['items']=_split_items(q.get('items',[])); q['scope']='all missing cities split into tape20 and layflat topics'; q['version']=max(int(q.get('version',1)),2); q['topics_per_city']=2; q['topic_policy']=TOPICS; q['updated_at']=base.now(); base.QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
        try: base.write_status(q,'topic_split_ready')
        except Exception: pass
        return q
    base.initialize=initialize; _patch_queue_file(base)

def _extract_paragraph_context(item,kind,topic_key='tape20'):
    research=item.get('city_research') or {}; text=json.dumps(research,ensure_ascii=False)+' '+str(item.get('topic_focus',''))+' '+str(item.get('city','')); crops=[v for k,v in CROP_HINTS.items() if k in text]; crop_context=crops[0] if crops else 'generic Iranian crop rows only; do not invent a specific crop if research does not support it'; seed=abs(hash(str(item.get('source_id',''))+':'+str(kind))); bg_list=LAYFLAT_BACKGROUNDS if topic_key=='layflat' else TAPE_BACKGROUNDS; return crop_context,SOIL_VARIANTS[seed%len(SOIL_VARIANTS)],bg_list[(seed//7)%len(bg_list)]

def install_image_policy(image_prompt_policy):
    def reference_images(kind,item=None):
        topic_key=(item or {}).get('topic') if isinstance(item,dict) else None
        return [LAYFLAT_REFERENCE_ROLL,LAYFLAT_REFERENCE_INSTALLED] if topic_key=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]
    def image_prompt(item,kind):
        topic_key=item.get('topic','tape20'); topic=TOPICS.get(topic_key,TOPICS['tape20']); crop_context,soil,bg=_extract_paragraph_context(item,kind,topic_key)
        if topic_key=='layflat':
            scenes={1:'hero advertising image: approved black woven yarn-reinforced layflat hose clearly visible and central in a farm',2:'product close-up: recreate black woven 2-inch layflat hose roll appearance from approved reference on real soil',3:'installed field system: same black woven layflat hose is the mainline with credible takeoff valves/couplers',4:'technical connection detail: approved-style woven layflat hose connected to laterals with realistic hardware',5:'wide irrigation-system view: approved-style black layflat hose is hero product and main supply line'}
            extra='MANDATORY: product must visibly match لوله-نخی-2-اینچ-1.webp. Do not substitute drip tape, PE pipe, smooth hose, corrugated pipe or generic tubing.'
        else:
            scenes={1:'product-only hero: one black drip tape roll lying flat or low-angle on soil, not upright, not encircling anything',2:'close product view: black 20 cm drip tape roll on tilled soil, clean empty center or dark shadow only, no white core/label/package',3:'contextual product shot: drip tape roll staged in field, crop rows behind it, no installed line running through or behind the roll as product',4:'technical product-only angle: roll slightly unrolled to show flat tape edge, no valves, filters, PE pipes, layflat hoses or connections',5:'wide advertising composition: farm background and one drip tape roll as clear subject, no irrigation network, no long pipes and no fittings'}
            extra='CRITICAL: the roll must not be vertical like a tire/wheel; must not surround, wrap around, contain, or be pierced by another pipe/tube/cylinder/spool/package. No AFP/logo/label on the product; only the separately added bottom-right watermark is allowed. Only the product roll and farm soil/crops.'
        return ('Photorealistic agricultural advertising photograph in Iran. '+f'Article topic: {topic["focus"]}. {topic["forbidden"]} {extra} '+f'Paragraph/crop context: {crop_context}. Soil: {soil}. Composition: {bg}. '+f'Scene: {scenes.get(kind,scenes[1])}. Product focus: {topic["image_focus"]}. '+'No landmarks. No Persian or Arabic text. No letters, digits, labels, captions, signs, packaging, logos, brands, or generated watermarks. Clean 16:9 composition.')
    image_prompt_policy.reference_images=reference_images; image_prompt_policy.image_prompt=image_prompt

def install_all():
    import city_content_queue as base
    import image_prompt_policy
    install_queue_split(base); install_image_policy(image_prompt_policy)
