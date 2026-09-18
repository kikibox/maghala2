#!/usr/bin/env python3
"""Launch queue with research grounding, QA v8, SEO images, topic references, 3 details FAQ, and cleanup."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
run_path=HERE/'run_agnes_city_queue.py';review_path=HERE/'reviewed_publish_city_queue.py'
def replace_once(source,old,new,label):
    count=source.count(old)
    # Older queue runners do not contain this optional cleanup block; the
    # review layer below already applies cleanup and validation. Do not make
    # an otherwise compatible queue fail before processing starts.
    if count==0 and label=='cleanup and faq preservation':
        return source
    if count!=1:raise RuntimeError('Cannot patch '+label)
    return source.replace(old,new,1)
run_source=run_path.read_text(encoding='utf-8')
run_source=replace_once(run_source,'RAW_AGNES=base.agnes\n','''import image_prompt_policy
import city_research
import faq_policy
import text_cleanup_policy
image_prompt_policy.install(backend)
RAW_AGNES=base.agnes
IMAGE_ROLE_SLUGS={1:'تصویر-شاخص',2:'انتخاب-محصول',3:'جزئیات-فنی',4:'نصب-مزرعه',5:'اتصال-و-کاربرد'}
def seo_image_name(item,kind):
 topic=item.get('topic','tape20')
 topic_slug='لوله-نخی-تاشو' if topic=='layflat' else 'نوار-تیپ-20-سانتی'
 raw=f"{topic_slug}-{item['slug']}-{IMAGE_ROLE_SLUGS[kind]}".replace('ي','ی').replace('ك','ک').replace('‌','-')
 safe=''.join(ch if(ch.isalnum()or ch=='-')else'-'for ch in raw)
 while '--' in safe:safe=safe.replace('--','-')
 return safe.strip('-')+'.jpg'
''','v8 helpers')
a="def agnes_draft(item,links):\n    approved=links[:12];link_lines='\\n'.join(f\"- {x['title']} | {x['url']}\" for x in approved)\n"
run_source=replace_once(run_source,a,a+"    research=city_research.research_city(item,RAW_AGNES,base.OUT)\n    research_context=city_research.prompt_context(research)\n    topic_focus=item.get('topic_focus','انتخاب و خرید نوار آبیاری ۲۰ سانتی‌متر')\n    topic_forbidden=item.get('topic_forbidden','')\n    faq_instruction=faq_policy.instruction()\n",'city research')
a="    prompt=f'''برای شهر {item['city']} در شهرستان {item['county']}، استان {item['province']} یک مقاله کاملاً جدید، فارسی، کاربردی و سئوشده درباره انتخاب و خرید نوار آبیاری بنویس."
b="    prompt=f'''برای شهر {item['city']} در شهرستان {item['county']}، استان {item['province']} یک مقاله کاملاً جدید، فارسی، کاربردی و سئوشده درباره {topic_focus} بنویس. {topic_forbidden} فقط یافته‌های دارای شاهد و confidence بالا یا متوسط را با scope صحیح به کار ببر. اگر status تحقیق insufficient_evidence است هیچ محصول، خاک، اقلیم، آب، رسوب یا ویژگی محلی را حدس نزن. عنوان کوتاه و سئویی باشد: حداکثر ۶۵ کاراکتر و نزدیک به الگوی «خرید [محصول] در [شهر]». اگر موضوع نوار تیپ است فاصله قطره‌چکان فقط ۲۰ سانتی‌متر است. اگر موضوع لوله نخی و تاشو است تمرکز متن روی انتقال آب، جنس، سایز، فشار، اتصال، دوام و کاربرد لوله نخی/تاشو باشد، نه رول نوار تیپ. نشانگر IMAGE_1 را داخل متن نگذار؛ تصویر ۱ فقط تصویر شاخص است. {faq_instruction} تحقیق سریع: {research_context}."
run_source=replace_once(run_source,a,b,'v8 drafting prompt')
run_source=replace_once(run_source,"        if not faq_policy.has_faq_at_end(body):errors.append('three details FAQ items required at end')\n        if not errors:\n            obj['city_research']=research\n            obj['topic']=item.get('topic')\n            obj['topic_focus']=topic_focus\n            return obj\n","        obj=text_cleanup_policy.apply(obj,item); body=obj.get('html','')\n        if '[[[IMAGE_1]]]' in body: errors.append('IMAGE_1 marker leaked into body')\n        if not faq_policy.has_faq_at_end(body):errors.append('three details FAQ items required at end')\n        if not errors:\n            obj['city_research']=research\n            obj['topic']=item.get('topic')\n            obj['topic_focus']=topic_focus\n            return obj\n",'cleanup and faq preservation')
a="    refs=image_prompt_policy.reference_images(kind,item)\n    payload={'model':MODEL,'prompt':backend.image_prompt(item,kind),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':refs}}"
# keep if already patched from prior version
if a not in run_source:
    run_source=replace_once(run_source,"    payload={'model':MODEL,'prompt':backend.image_prompt(item,kind),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json'}}",a,'topic-specific image references')
run_source=replace_once(run_source,'''    name=f"{item['source_id']}-{kind}.jpg";(base.IMAGES/name).write_bytes(blob);return name,hashlib.sha256(blob).hexdigest()''','''    name=seo_image_name(item,kind);(base.IMAGES/name).write_bytes(blob);return name,hashlib.sha256(blob).hexdigest()''','SEO filenames')
run_source=replace_once(run_source,'backend.generate_image=agnes_generate_image\n','backend.seo_image_name=seo_image_name\nbackend.generate_image=agnes_generate_image\n','SEO helper exposure')
original=review_path.read_text(encoding='utf-8')
review=replace_once(original,'import hashlib,json,os,re,time\n','import hashlib,json,os,re,time,urllib.parse\nimport research_grounding_review\nimport faq_policy\nimport text_cleanup_policy\n','review imports')
review=replace_once(review,'QUALITY_GATE_VERSION=6','QUALITY_GATE_VERSION=9','quality gate version')
review=replace_once(review,'''    path=base.IMAGES/f"{item['source_id']}-{kind}.jpg"''','''    path=base.IMAGES/queue.seo_image_name(item,kind)''','image cache')
review=replace_once(review,"        url=str(link.get('url',''));title=str(link.get('title',''))\n        return any(x in url for x in BLOCKED_LINK_TERMS) or any(x in title for x in BLOCKED_TITLE_TERMS)","        url=str(link.get('url',''));decoded_url=urllib.parse.unquote(url);title=str(link.get('title',''))\n        return any(x in url or x in decoded_url for x in BLOCKED_LINK_TERMS) or any(x in title for x in BLOCKED_TITLE_TERMS)",'decoded unsafe links')
review=replace_once(review,"    body=obj.get('html','');errors=language_errors(body)+technical_errors(body)","    obj=text_cleanup_policy.apply(obj,item)\n    body=obj.get('html','');errors=language_errors(body)+technical_errors(body)+research_grounding_review.validate_grounding(obj,item,obj.get('city_research',{}))\n    if '[[[IMAGE_1]]]' in body: errors.append('IMAGE_1 marker leaked into body')\n    if not faq_policy.has_faq_at_end(body): errors.append('three details FAQ items required at end')\n    if item.get('topic')=='layflat' and any(term in body for term in ['رول نوار تیپ','خرید نوار تیپ ۲۰','فاصله قطره‌چکان ۲۰']): errors.append('layflat article still focuses on drip tape')",'grounding faq cleanup validation')
review=replace_once(review,'ادعاهای ساختگی درباره اقلیم محلی، قیمت، نمایندگی، موجودی، ارسال و مشخصات محصول را حذف کن.','هر ادعای محلی درباره اقلیم، خاک، آب، رسوب، شوری، محصول و زمان کشت را فقط با شاهد صریح city_research و scope صحیح نگه دار؛ اگر تحقیق insufficient_evidence است همه این ادعاها و حدس‌های محلی را حذف کن. عنوان را کوتاه و سئویی کن: حداکثر ۶۵ کاراکتر و شامل محصول و شهر. نشانگر IMAGE_1 را از متن حذف کن چون فقط تصویر شاخص است. اگر topic=layflat است متن را روی لوله نخی و لوله تاشو نگه دار و تصاویر/توضیحات نوار تیپ را موضوع اصلی نکن. اگر topic=tape20 است فقط فاصله قطره‌چکان ۲۰ سانتی‌متر مجاز است. در انتهای مقاله بخش سوالات متداول را دقیقاً با ساختار h3 + details/summary و دقیقاً ۳ سوال بساز؛ قبل از آن جمله تماس واتساپ بیاور. بعد از FAQ بخش محتوایی h2 یا h3 جدید نساز. ادعاهای قیمت، ارز، بهترین فصل نصب، نمایندگی، موجودی و ارسال را حذف کن.','grounded editorial prompt with cleanup')
review=replace_once(review,'        obj=rebuild_internal_links(base.agnes(review_prompt),links)\n        errors=validate_reviewed(obj,item,links)',"        obj=base.agnes(review_prompt)\n        obj['city_research']=draft.get('city_research',{})\n        obj['topic']=draft.get('topic')\n        obj=research_grounding_review.rewrite_grounded(obj,item,obj['city_research'],base.agnes,base.MIN_WORDS)\n        obj=rebuild_internal_links(obj,links)\n        obj=text_cleanup_policy.apply(obj,item)\n        errors=validate_reviewed(obj,item,links)",'v9 grounding cleanup pass')
review=replace_once(review,"            obj['editorial_review']={'passed':True,'review_model':base.AGNES_MODEL,'attempt':attempt,'quality_gate_version':QUALITY_GATE_VERSION,'checks':['Persian language','technical plausibility','SEO fields','minimum length','safe internal links','image markers']}\n            return obj","            obj=text_cleanup_policy.apply(obj,item)\n            obj['city_research']=draft.get('city_research',{})\n            obj['topic']=draft.get('topic')\n            obj['editorial_review']={'passed':True,'review_model':base.AGNES_MODEL,'attempt':attempt,'quality_gate_version':QUALITY_GATE_VERSION,'checks':['Persian language','technical plausibility','SEO fields','minimum length','safe internal links','no visible IMAGE_1 marker','short SEO title','evidence-aware city research','topic-specific product focus','three collapsible FAQ details at end']}\n            return obj","QA v9 stamp")
review_path.write_text(review,encoding='utf-8')
try:exec(compile(run_source,str(run_path),'exec'),{'__name__':'__main__','__file__':str(run_path)})
finally:review_path.write_text(original,encoding='utf-8')
for artifact in (HERE.parent/'artifacts'/'city-content-queue'/'items').glob('*.json'):
    try:
        data=json.loads(artifact.read_text(encoding='utf-8'))
        if data.get('status')=='completed' and int(data.get('editorial_review',{}).get('quality_gate_version',0))>=9:
            data.pop('failed_at',None);data.pop('last_error',None);artifact.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception:pass
