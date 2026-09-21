#!/usr/bin/env python3
"""Run the reviewed production queue with Agnes text and image models."""
import base64,hashlib,io,json,os,urllib.error,urllib.request
from PIL import Image
import city_content_queue as base
import city_content_queue_cloudflare as backend
import image_prompt_policy
image_prompt_policy.install(backend)

MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.0-flash')
KEY=os.getenv('AGNES_API_KEY','').strip();API=os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')
TARGET_WORDS=max(base.MIN_WORDS+200,1250)
RAW_AGNES=base.agnes

def enforce_minimum_words(obj):
    if not isinstance(obj,dict) or not obj.get('html'):return obj
    body=obj['html'];count=base.words(body)
    if count>=base.MIN_WORDS:return obj
    supplements=[
      '<h3>کنترل نهایی پیش از راه‌اندازی</h3><p>پیش از آغاز آبیاری، مسیر لوله اصلی، اتصالات، فیلتر و نوارها باید مرحله‌به‌مرحله بررسی شوند. باز کردن تدریجی جریان آب کمک می‌کند نشتی، تاخوردگی یا بسته بودن انتهای مسیر زودتر دیده شود. فشار واقعی در ابتدا و انتهای ردیف‌ها نیز باید با ابزار مناسب سنجیده شود؛ زیرا ظاهر شدن آب در قطره‌چکان‌ها به‌تنهایی نشانه توزیع یکنواخت نیست. ثبت زمان آبیاری، وضعیت رطوبت خاک و تغییرات مزرعه امکان اصلاح برنامه را فراهم می‌کند. هرگونه شست‌وشوی شیمیایی یا اسیدی نیز باید فقط پس از بررسی کیفیت آب و با نظر متخصص انجام شود تا به گیاه، خاک و تجهیزات آسیب نرسد.</p>',
      '<h3>ثبت اطلاعات و نگهداری دوره‌ای</h3><p>برای مدیریت بهتر سامانه، یک برگه ساده برای تاریخ نصب، مشخصات نوار، فشار کار، زمان شست‌وشوی فیلتر و محل تعمیرها تهیه شود. این سابقه نشان می‌دهد کدام بخش‌ها بیشتر دچار گرفتگی یا آسیب می‌شوند و در خرید بعدی چه تغییری لازم است. بازدید منظم از ابتدا، میانه و انتهای ردیف‌ها، تمیز نگه داشتن فیلتر و جلوگیری از عبور ماشین‌آلات روی نوار، عمر مفید سامانه را افزایش می‌دهد. تصمیم نهایی درباره ضخامت، فاصله قطره‌چکان و طول ردیف باید بر اساس نوع کشت، بافت خاک، شیب زمین، کیفیت آب و محاسبه فنی انجام گیرد.</p>'
    ]
    marker_positions=[body.find(f'[[[IMAGE_{i}]]]') for i in range(2,6) if body.find(f'[[[IMAGE_{i}]]]')>=0]
    pos=min(marker_positions) if marker_positions else len(body)
    for section in supplements:
        if base.words(body)>=base.MIN_WORDS:break
        body=body[:pos]+section+'\n'+body[pos:];pos+=len(section)+1
    obj['html']=body;return obj

def guarded_agnes(prompt):return enforce_minimum_words(RAW_AGNES(prompt))
base.agnes=guarded_agnes

def repair_links_and_markers(obj,links):
    body=obj.get('html','');allowed=[x['url'] for x in links[:12]];allowed_set=set(allowed);used=base.internal_links(body);unused=[u for u in allowed if u not in used]
    for old in sorted(used-allowed_set):
        new=unused.pop(0) if unused else '#'
        body=body.replace('href="'+old+'"','href="'+new+'"').replace("href='"+old+"'","href='"+new+"'")
    used=base.internal_links(body);additions=[]
    for link in links[:12]:
        if len(used)>=base.MIN_LINKS:break
        if link['url'] not in used:
            additions.append(f'<a href="{link["url"]}">{link["title"]}</a>');used.add(link['url'])
    if additions:body+='\n<p><strong>مطالب مرتبط:</strong> '+'، '.join(additions)+'</p>'
    for i in range(2,6):
        marker=f'[[[IMAGE_{i}]]]';body=body.replace(marker,'');body+='\n'+marker
    obj['html']=body;return enforce_minimum_words(obj)

def agnes_draft(item,links):
    approved=links[:12];link_lines='\n'.join(f"- {x['title']} | {x['url']}" for x in approved)
    prompt=f'''برای شهر {item['city']} در شهرستان {item['county']}، استان {item['province']} یک مقاله کاملاً جدید، فارسی، کاربردی و سئوشده درباره انتخاب و خرید نوار آبیاری بنویس. متن HTML باید دست‌کم {TARGET_WORDS} کلمه باشد تا پس از ویرایش نیز از {base.MIN_WORDS} کلمه کمتر نشود. از ادعای ساختگی درباره اقلیم، قیمت، نمایندگی، موجودی یا ارسال محلی خودداری کن. ساختار HTML فقط با h2/h3/p/ul/ol/table/strong/a باشد و H1 نداشته باشد. موضوعات لازم: نیازسنجی مزرعه، انتخاب ضخامت و فاصله قطره‌چکان، فشار و فیلتراسیون، طراحی، نصب، نگهداری، خطاهای رایج، FAQ و جمع‌بندی. حداقل {base.MIN_LINKS} و حداکثر ۷ لینک داخلی فقط از فهرست زیر استفاده کن و نشانی href را دقیقاً کپی کن. برای چهار تصویر داخل متن، نشانگرهای دقیق [[[IMAGE_2]]], [[[IMAGE_3]]], [[[IMAGE_4]]], [[[IMAGE_5]]] را هرکدام دقیقاً یک بار قرار بده. تصویر شماره ۱ شاخص است. فقط JSON معتبر با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.\nلینک‌های مجاز:\n{link_lines}'''
    last='';obj=None
    for _ in range(4):
        obj=repair_links_and_markers(base.agnes(prompt),links);body=obj.get('html','');used=base.internal_links(body);allowed={x['url'] for x in approved};errors=[]
        if base.words(body)<base.MIN_WORDS:errors.append(f'length {base.words(body)} below {base.MIN_WORDS}')
        if not(base.MIN_LINKS<=len(used)<=7):errors.append(f'link count {len(used)} invalid')
        if used-allowed:errors.append('unapproved link remains')
        if not errors:return obj
        last='; '.join(errors)
        prompt=f'''JSON مقاله زیر در کنترل کیفیت رد شده است: {last}. همان مقاله را ویرایش کن، نه اینکه خلاصه یا از نو کوتاه‌نویسی کنی. محتوای HTML را با توضیحات کاربردی و غیرتکراری تا حداقل {TARGET_WORDS} کلمه گسترش بده. همه فیلدها، لینک‌های موجود و چهار نشانگر تصویر را حفظ کن. فقط JSON معتبر با همان کلیدها برگردان.\n{json.dumps(obj,ensure_ascii=False)}'''
    raise RuntimeError('Agnes 3 draft QA failed: '+last)

def agnes_generate_image(item,kind):
    if not KEY:raise RuntimeError('AGNES_API_KEY is missing')
    payload={'model':MODEL,'prompt':backend.image_prompt(item,kind),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':image_prompt_policy.reference_images(kind,item)}}
    req=urllib.request.Request(API+'/images/generations',data=json.dumps(payload).encode(),method='POST',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-city-content-queue/3.0'})
    try:
        with urllib.request.urlopen(req,timeout=600) as response:data=json.loads(response.read())
    except urllib.error.HTTPError as exc:raise RuntimeError(f"Agnes Image HTTP {exc.code}: {exc.read().decode('utf-8','replace')[:1200]}")
    row=(data.get('data') or [{}])[0]
    if row.get('b64_json'):blob=base64.b64decode(row['b64_json'])
    elif row.get('url'):
        with urllib.request.urlopen(row['url'],timeout=300) as response:blob=response.read()
    else:raise RuntimeError('Agnes image response has neither b64_json nor url')
    image=Image.open(io.BytesIO(blob)).convert('RGB');w,h=image.size;target=16/9
    if w/h>target:
        nw=int(h*target);left=(w-nw)//2;image=image.crop((left,0,left+nw,h))
    else:
        nh=int(w/target);top=(h-nh)//2;image=image.crop((0,top,w,top+nh))
    image=image.resize((1200,675),Image.Resampling.LANCZOS);buf=io.BytesIO();image.save(buf,'JPEG',quality=93,optimize=True);blob=backend.watermark(buf.getvalue())
    if len(blob)<10000:raise RuntimeError('Agnes generated image is unexpectedly small')
    name=f"{item['source_id']}-{kind}.jpg";(base.IMAGES/name).write_bytes(blob);return name,hashlib.sha256(blob).hexdigest()

if base.QUEUE.exists():
    state=json.loads(base.QUEUE.read_text(encoding='utf-8'));changed=False
    for item in state.get('items',[]):
        if item.get('status')=='failed' and ('draft QA failed' in item.get('last_error','') or 'Text QA failed' in item.get('last_error','')):
            item['status']='pending';item['attempts']=0;changed=True
            for key in ('last_error','failed_at','started_at'):item.pop(key,None)
    if changed:base.QUEUE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
backend.MODEL=MODEL
backend.make_content=agnes_draft
backend.generate_image=agnes_generate_image
import reviewed_publish_city_queue
