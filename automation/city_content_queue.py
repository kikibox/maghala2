#!/usr/bin/env python3



"""Generate missing Iranian city posts, GitHub Models images, and reversible SQL."""



import base64,datetime as dt,hashlib,html,json,os,re,time,urllib.error,urllib.request



from collections import Counter

import random



from pathlib import Path



import rewrite_city_samples as base



ROOT=Path(__file__).resolve().parents[1]



OUT=ROOT/'artifacts/city-content-queue'; ITEMS=OUT/'items'; IMAGES=OUT/'images'; SQL=OUT/'sql'; ROLLBACK=OUT/'rollback'; QUEUE=OUT/'queue.json'; STATUS=OUT/'status.json'



DATA_COMMIT='474942269f75ec247e1af5684f5e3eca9f304431'



DATA_BASE='https://'+'raw.githubusercontent.com/sajaddp/list-of-cities-in-Iran/'+DATA_COMMIT+'/dist/json'



SITE='https://navar-abyari.ir'; TABLE='ha_posts'; META='ha_postmeta'



AGNES_BASE=os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/'); AGNES_KEY=os.getenv('AGNES_API_KEY','').strip(); AGNES_MODEL=os.getenv('AGNES_MODEL','agnes-2.5-flash')



IMAGE_TOKEN=(os.getenv('GITHUB_MODELS_TOKEN') or os.getenv('GITHUB_TOKEN') or '').strip(); IMAGE_MODEL=os.getenv('IMAGE_MODEL','openai/gpt-image-1'); IMAGE_ENDPOINT=os.getenv('IMAGE_ENDPOINT','https://models.github.ai/inference/images/generations')



BATCH=max(1,int(os.getenv('BATCH_SIZE','3'))); MIN_WORDS=int(os.getenv('MIN_WORDS','1050')); MIN_LINKS=int(os.getenv('MIN_INTERNAL_LINKS','4')); MAX_ATTEMPTS=max(1,int(os.getenv('MAX_ATTEMPTS','4')))



PROVINCE_TYPES={100:'arak',101:'gilan',102:'mazandaran',103:'post',104:'orumiyeh',105:'post',106:'ahvaz',107:'shiraz',108:'post',109:'mashhad',110:'isfahan',111:'zahedan',112:'kurdistan',113:'hamadan',114:'shahrekord',115:'post',116:'post',117:'post',118:'bushehr',119:'zanjan',120:'semnan',121:'yazd',122:'bandarabbas',123:'tehran',124:'ardabil',125:'post',126:'qazvin',127:'golestan',128:'post',129:'post',130:'karaj'}



WORD_RE=re.compile(r'[\u0600-\u06ff\u200c]+|[A-Za-z]+'); HREF_RE=re.compile(r'<a\b[^>]*href=["\']([^"\']+)',re.I)



def now():return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()



def fetch_json(url,headers=None,payload=None,timeout=420):



 req=urllib.request.Request(url,data=(json.dumps(payload,ensure_ascii=False).encode() if payload is not None else None),headers=headers or {})



 try:



  with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)



 except urllib.error.HTTPError as e:raise RuntimeError(f'HTTP {e.code} {url}: {e.read().decode("utf-8","replace")[:800]}')



def normalize(s):



 s=html.unescape(str(s or '')).replace('ي','ی').replace('ك','ک').replace('\u200c',' '); return re.sub(r'[^\u0600-\u06ff0-9]+','',s).lower()



def esc(s):return base.escsql(str(s))



def slugify(name,province):



 s=re.sub(r'[\s_]+','-',name.strip().replace('ي','ی').replace('ك','ک')); return re.sub(r'-+','-',s).strip('-')+'-'+re.sub(r'[\s_]+','-',province.strip())



def words(text):return len(WORD_RE.findall(re.sub(r'<[^>]+>',' ',text or '')))



def internal_links(text):return {u for u in HREF_RE.findall(text or '') if 'navar-abyari.ir' in u}



def sitemap_index():
 """Return resolved sitemap posts (post-sitemap1.xml + post-sitemap2.xml), using a
 git-tracked cache (link-index-sitemap.json) when present so the ~180 REST title
 lookups only happen once per fresh cache. Falls back to a slug label if the
 REST API is unreachable."""
 import urllib.request as _ur, json as _json, re as _re, urllib.parse as _up
 cache = OUT / 'link-index-sitemap.json'
 if cache.exists():
     try:
         c = _json.loads(cache.read_text(encoding='utf-8'))
         if c.get('count', 0) > 0:
             return c['links']
     except Exception:
         pass
 urls = set()
 for sm in ('post-sitemap1.xml', 'post-sitemap2.xml'):
     try:
         req = _ur.Request(f'{SITE}/{sm}', headers={'User-Agent': 'navar-fix'})
         with _ur.urlopen(req, timeout=60) as r:
             urls.update(_re.findall(r'<loc>(.*?)</loc>', r.read().decode('utf-8','replace')))
     except Exception:
         pass
 if not urls:
     return []
 links = []
 for url in sorted(urls):
     path = _up.urlparse(url).path.strip('/')
     title = None
     try:
         slug = _up.unquote(path)
         req = _ur.Request(f'{SITE}/wp-json/wp/v2/posts?slug={_up.quote(slug)}&per_page=1',
                           headers={'User-Agent': 'navar-fix'})
         with _ur.urlopen(req, timeout=15) as r:
             rows = _json.loads(r.read().decode('utf-8','replace'))
             if rows:
                 t = rows[0].get('title')
                 if isinstance(t, dict):
                     title = t.get('raw') or None
                 elif isinstance(t, str) and t:
                     title = t
     except Exception:
         pass
     if not title:
         title = path.replace('%','').replace('-',' ').strip() or 'مقاله'
     links.append({'title': title, 'url': url, 'post_type': 'post'})
 OUT.mkdir(parents=True, exist_ok=True)
 cache.write_text(_json.dumps({'count':len(links),'links':links}, ensure_ascii=False, indent=1), encoding='utf-8')
 return links
def existing_index(posts):



 names=set();links=[]



 for p in posts:



  if p.get('post_status') not in {'publish','draft','pending','future','private'}:continue



  title=re.sub(r'^(خرید|قیمت|فروش)\s+','',p.get('post_title') or ''); names|={normalize(title),normalize(p.get('post_name') or '')}; slug=(p.get('post_name') or '').strip('/')



  if slug:



   pt=p.get('post_type') or 'post';links.append({'title':p.get('post_title') or slug,'url':f'{SITE}/{slug}/' if pt=='post' else f'{SITE}/{pt}/{slug}/','post_type':pt})



 return names,links



def write_status(q,result):



 c=Counter(x['status'] for x in q['items']);STATUS.write_text(json.dumps({'result':result,'updated_at':now(),'total':len(q['items']),'pending':c['pending'],'processing':c['processing'],'completed':c['completed'],'failed':c['failed'],'blocked_image_model':c['blocked_image_model'],'image_model':IMAGE_MODEL,'batch_size':BATCH},ensure_ascii=False,indent=2),encoding='utf-8')



def initialize(force=False):



 for p in (OUT,ITEMS,IMAGES,SQL,ROLLBACK):p.mkdir(parents=True,exist_ok=True)



 if QUEUE.exists() and not force:return json.loads(QUEUE.read_text(encoding='utf-8'))



 posts=base.load_posts();existing,links=existing_index(posts);provinces={int(x['id']):x for x in fetch_json(DATA_BASE+'/provinces.json')};counties={int(x['id']):x for x in fetch_json(DATA_BASE+'/counties.json')};cities=fetch_json(DATA_BASE+'/cities-filtered.json');seen=set();rows=[]



 for c in cities:



  name=str(c['name']).strip();province=provinces.get(int(c['province_id']));county=counties.get(int(c['county_id']))



  if not province or not county or re.search(r'\d$',name):continue



  key=(int(c['province_id']),normalize(name))



  if key in seen:continue



  seen.add(key);n=normalize(name)



  if n in existing or any(n and n in x for x in existing):continue



  rows.append({'source_id':int(c['id']),'city':name,'county':county['name'],'province':province['name'],'province_id':int(c['province_id']),'post_type':PROVINCE_TYPES[int(c['province_id'])],'slug':slugify(name,province['name']),'status':'pending','attempts':0})



 rows.sort(key=lambda x:(x['province_id'],x['county'],x['city']))



 q={'version':1,'created_at':now(),'updated_at':now(),'source':f'sajaddp/list-of-cities-in-Iran@{DATA_COMMIT}','scope':'all missing cities','text_model':AGNES_MODEL,'image_model':IMAGE_MODEL,'images_per_post':3,'rules':{'draft_only':True,'minimum_words':MIN_WORDS,'minimum_internal_links':MIN_LINKS},'items':rows,'link_index':links};QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');write_status(q,'initialized');return q



def agnes(prompt):



 if not AGNES_KEY:raise RuntimeError('AGNES_API_KEY is missing')



 data=fetch_json(AGNES_BASE+'/chat/completions',{'Authorization':f'Bearer {AGNES_KEY}','Content-Type':'application/json','User-Agent':'navar-city-content-queue'},{'model':AGNES_MODEL,'messages':[{'role':'system','content':'شما نویسنده ارشد فارسی در حوزه آبیاری کشاورزی هستید. فقط JSON معتبر برگردانید.'},{'role':'user','content':prompt}],'temperature':0.66,'max_tokens':20000});raw=data['choices'][0]['message']['content'].strip();return json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',raw))



def make_content(item,links):



 approved=links[:]

 if len(approved)>12:

  random.Random(str(item.get('source_id',''))).shuffle(approved)

  approved=approved[:12];link_lines='\n'.join(f"- {x['title']} | {x['url']}" for x in approved);prompt=f'''برای شهر {item['city']} در شهرستان {item['county']}، استان {item['province']} یک مقاله کاملاً جدید و سئوشده درباره انتخاب و خرید نوار آبیاری بنویس. متن فارسی طبیعی، دست‌کم {MIN_WORDS} کلمه، بدون ادعای ساختگی درباره اقلیم، قیمت، نمایندگی یا ارسال محلی باشد. ساختار HTML فقط با h2/h3/p/ul/ol/table/strong/a باشد و H1 نداشته باشد. موضوعات: نیازسنجی مزرعه، انتخاب ضخامت و فاصله قطره‌چکان، فشار و فیلتراسیون، طراحی، نصب، نگهداری، خطاها، FAQ و جمع‌بندی. حداقل {MIN_LINKS} و حداکثر ۷ لینک داخلی فقط از فهرست زیر استفاده کن. سه نشانگر دقیق [[[IMAGE_1]]], [[[IMAGE_2]]], [[[IMAGE_3]]] را هرکدام یک‌بار و بین بخش‌های مناسب بگذار. JSON با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.\nلینک‌های مجاز:\n{link_lines}'''



 for _ in range(4):



  obj=agnes(prompt);body=obj.get('html','');allowed={x['url'] for x in approved}
  body=sanitize_links(body,allowed)
  used=internal_links(body)



  if words(body)>=MIN_WORDS and MIN_LINKS<=len(used)<=7 and all(body.count(f'[[[IMAGE_{i}]]]')==1 for i in range(1,4)) and not(used-allowed):return obj



  prompt+='\nنسخه قبلی کنترل کیفیت را رد کرد؛ طول، لینک‌ها یا نشانگرهای تصویر را دقیق اصلاح کن.'



 raise RuntimeError('Text QA failed after 4 attempts')



def image_prompt(item,kind):



 scenes={1:'wide hero view of a modern Iranian agricultural field with drip irrigation tape clearly visible',2:'close technical view of drip irrigation tape, filter and pressure regulator in a clean farm setting',3:'farmer hands inspecting irrigation tape rows, no identifiable face'};return f"Photorealistic editorial agriculture image, {scenes[kind]}, visual cues consistent with {item['province']} province without landmarks or unverifiable claims, natural light, no text, no logo, no watermark, no labels, no fake writing, 16:9 composition"



def generate_image(item,kind):



 if not IMAGE_TOKEN:raise RuntimeError('GITHUB_MODELS_TOKEN/GITHUB_TOKEN is missing')



 data=fetch_json(IMAGE_ENDPOINT,{'Authorization':f'Bearer {IMAGE_TOKEN}','Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-city-content-queue'},{'model':IMAGE_MODEL,'prompt':image_prompt(item,kind),'size':'1536x1024','quality':'medium','n':1},300);row=data['data'][0]



 if row.get('b64_json'):blob=base64.b64decode(row['b64_json'])



 elif row.get('url'):



  with urllib.request.urlopen(row['url'],timeout=180) as r:blob=r.read()



 else:raise RuntimeError('Image response has neither b64_json nor url')



 if len(blob)<10000:raise RuntimeError('Generated image is unexpectedly small')



 name=f"{item['source_id']}-{kind}.png";(IMAGES/name).write_bytes(blob);return name,hashlib.sha256(blob).hexdigest()



def sanitize_links(html_text, allowed_urls):
    """Keep only <a> anchors whose href is in allowed_urls; drop other internal
    links so the model cannot use URLs outside the related-content pool."""
    import re as _re
    allowed_set = set(allowed_urls)

    def _keep(match):
        tag = match.group(0)
        m = _re.search(r'href=["\']([^"\']+)', tag, _re.I)
        if not m:
            return tag
        href = m.group(1)
        if href in allowed_set or 'navar-abyari.ir' not in href:
            return tag
        # Internal link not in the approved pool -> strip tag but keep text
        return _re.sub(r'</?a\b[^>]*>', '', tag)

    return _re.sub(r'<a\b[^>]*>.*?</a>', _keep, html_text, flags=_re.I | _re.S)
def sql_for(item,obj,image_names):



 title=obj['title'];body=obj['html'];urls=[]



 for i,name in enumerate(image_names,1):



  url=f'{SITE}/wp-content/uploads/2026/09/navar-city-generated/{name}';urls.append(url);body=body.replace(f'[[[IMAGE_{i}]]]',f'<figure class="wp-block-image size-large"><img src="{url}" alt="نوار آبیاری در {item["city"]} - تصویر {i}"/><figcaption>کاربرد نوار آبیاری در مدیریت مزرعه</figcaption></figure>')



 pt=item['post_type'];slug=item['slug'];excerpt=obj.get('excerpt','');q=['START TRANSACTION;',f"SET @existing_post=(SELECT ID FROM `{TABLE}` WHERE `post_name`='{esc(slug)}' OR (`post_type`='{esc(pt)}' AND `post_title`='{esc(title)}') LIMIT 1);",f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(body)}','{esc(title)}','{esc(excerpt)}','publish','open','open','{esc(slug)}',NOW(),UTC_TIMESTAMP(),0,'',0,'{esc(pt)}','',0 WHERE @existing_post IS NULL;",'SET @post_id=COALESCE(@existing_post,LAST_INSERT_ID());']



 for key,val in [('_rank_math_title',obj.get('meta_title','')),('_rank_math_description',obj.get('meta_description','')),('rank_math_focus_keyword',obj.get('focus_keyword','')),('_navar_geo_level','city'),('_navar_city',item['city']),('_navar_county',item['county']),('_navar_province',item['province'])]:q.append(f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'{esc(key)}','{esc(val)}' WHERE NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@post_id AND meta_key='{esc(key)}');")



 for idx,(name,url) in enumerate(zip(image_names,urls),1):q.append(f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) VALUES (1,NOW(),UTC_TIMESTAMP(),'','{esc(item['city'])} - تصویر {idx}','','inherit','open','closed','{esc(name.rsplit('.',1)[0])}',NOW(),UTC_TIMESTAMP(),@post_id,'{esc(url)}',0,'attachment','image/webp',0); SET @media_{idx}=LAST_INSERT_ID(); INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) VALUES (@media_{idx},'_wp_attached_file','2026/09/navar-city-generated/{esc(name)}');")



 q+=['INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES (@post_id,\'_thumbnail_id\',@media_1);','COMMIT;'];rollback=f"START TRANSACTION; DELETE pm FROM `{META}` pm JOIN `{TABLE}` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}' LIMIT 1) AND p.post_type='attachment'; DELETE FROM `{TABLE}` WHERE post_parent=(SELECT ID FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}' LIMIT 1) AND post_type='attachment'; DELETE pm FROM `{META}` pm JOIN `{TABLE}` p ON p.ID=pm.post_id WHERE p.post_name='{esc(slug)}' AND p.post_type='{esc(pt)}'; DELETE FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}'; COMMIT;\n";return '\n'.join(q)+'\n',rollback,body



def process(q):



 if any(x['status']=='blocked_image_model' for x in q['items']):write_status(q,'blocked_image_model');raise RuntimeError(q.get('image_model_error','Image model is blocked'))



 # Process only pending items during normal scheduled runs. Failed items are



 # preserved for diagnosis and explicit repair runs instead of blocking the queue.



 batch=[x for x in q['items'] if x['status']=='pending' and x['attempts']<MAX_ATTEMPTS][:BATCH]



 # Refresh link_index with sitemap posts so related-content isn't limited to the stale DB dump

 try:

  existing_urls={l['url'] for l in q.get('link_index',[])}

  smlinks=[l for l in sitemap_index() if l['url'] not in existing_urls]

  if smlinks:

   q['link_index']=q.get('link_index',[])+smlinks

   print(f'link_index extended by {len(smlinks)} sitemap posts, total now {len(q["link_index"])}',flush=True)

 except Exception as _e:

  print(f'sitemap_index warning: {type(_e).__name__}: {_e}',flush=True)

 if not batch:write_status(q,'complete');return



 for item in batch:



  item.update(status='processing',attempts=item['attempts']+1,started_at=now());QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')



  try:



   obj=make_content(item,q['link_index']);names=[];hashes=[]



   for kind in range(1,4):name,digest=generate_image(item,kind);names.append(name);hashes.append(digest);time.sleep(2)



   insert,rollback,body=sql_for(item,obj,names);(SQL/f"{item['source_id']}.sql").write_text(insert,encoding='utf-8');(ROLLBACK/f"{item['source_id']}.sql").write_text(rollback,encoding='utf-8');(ITEMS/f"{item['source_id']}.json").write_text(json.dumps({**item,**obj,'html':body,'images':names,'image_sha256':hashes},ensure_ascii=False,indent=2),encoding='utf-8');item.update(status='completed',completed_at=now(),word_count=words(body),images=names,last_error='')



  except Exception as e:



   msg=str(e)[:900];blocked=('models.github.ai' in msg or 'Image response' in msg or 'GITHUB_MODELS_TOKEN' in msg or 'HTTP 4' in msg);item.update(status='blocked_image_model' if blocked else 'failed',failed_at=now(),last_error=msg)



   if blocked:q['image_model_error']=msg;QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');write_status(q,'blocked_image_model');raise



  q['updated_at']=now();QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');write_status(q,'processing')



 (OUT/'create-all-completed.sql').write_text('\n'.join(['-- Review before importing. Generated posts will be published.']+[p.read_text(encoding='utf-8') for p in sorted(SQL.glob('*.sql'))]),encoding='utf-8');(OUT/'rollback-all-completed.sql').write_text('\n'.join(p.read_text(encoding='utf-8') for p in sorted(ROLLBACK.glob('*.sql'))),encoding='utf-8');write_status(q,'ready')



def main():



 import argparse



 ap=argparse.ArgumentParser();ap.add_argument('--init-only',action='store_true');ap.add_argument('--force-init',action='store_true');a=ap.parse_args();q=initialize(a.force_init)



 if not a.init_only:process(q)



if __name__=='__main__':main()



