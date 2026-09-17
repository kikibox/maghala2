#!/usr/bin/env python3
import argparse,datetime as dt,html,json,os,re,time,urllib.error,urllib.parse,urllib.request
from collections import Counter
from pathlib import Path
import rewrite_city_samples as base

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/city-rewrite-queue'
QUEUE=OUT/'queue.json'; STATUS=OUT/'status.json'; LINKS=OUT/'internal-links.json'
POSTS_OUT=OUT/'posts'; SQL_OUT=OUT/'sql'; ROLLBACK_OUT=OUT/'rollback'
CITY_TYPES={'zahedan','shahrekord','arak','qazvin','ardabil','yazd','zanjan','isfahan','tehran','shiraz','mashhad','ahvaz','hamadan','kurdistan','karaj','bandarabbas','bushehr','semnan','golestan','gilan','mazandaran','orumiyeh'}
EXCLUDED_IDS={35258,35261,35264}
SITE='https://navar-abyari.ir'
BASE=os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')
KEY=os.getenv('AGNES_API_KEY','').strip(); MODEL=os.getenv('AGNES_MODEL','agnes-2.5-flash')
MIN_WORDS=int(os.getenv('MIN_WORDS','1050')); BATCH_SIZE=int(os.getenv('BATCH_SIZE','5'))
MAX_SIMILARITY=float(os.getenv('MAX_SIMILARITY','0.62')); MIN_INTERNAL_LINKS=int(os.getenv('MIN_INTERNAL_LINKS','4'))
HREF_RE=re.compile(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']',re.I)
WORD_RE=re.compile(r'[\u0600-\u06ff\u200c]+|[A-Za-z]+',re.U)
TOKEN_RE=re.compile(r'[\u0600-\u06ff\u200c]{3,}|[A-Za-z]{3,}',re.U)

def now(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
def canonical(p):
    slug=(p.get('post_name') or '').strip('/')
    if not slug:return ''
    pt=p.get('post_type')
    if pt in CITY_TYPES:return f'{SITE}/{pt}/{slug}/'
    if pt=='product':return f'{SITE}/product/{slug}/'
    if pt=='faq':return f'{SITE}/faq/{slug}/'
    return f'{SITE}/{slug}/'
def normalize_url(url):
    if not url:return ''
    url=html.unescape(url.strip())
    if url.startswith('/'):url=SITE+url
    try:
        u=urllib.parse.urlsplit(url)
        if u.netloc not in {'navar-abyari.ir','www.navar-abyari.ir'}:return ''
        path=re.sub('/+','/',u.path or '/')
        return urllib.parse.urlunsplit(('https','navar-abyari.ir',path,'',''))
    except Exception:return ''
def anchors(content):
    result=[]
    for m in re.finditer(r'<a\b[^>]*\bhref=["\']([^"\']+)["\'][^>]*>(.*?)</a>',content or '',re.I|re.S):
        url=normalize_url(m.group(1));label=base.plain(m.group(2))
        if url:result.append((url,label))
    return result
def build_link_index(posts):
    found={}
    for p in posts:
        if p.get('post_status')!='publish':continue
        url=normalize_url(canonical(p))
        if url:found.setdefault(url,{'url':url,'title':p.get('post_title') or '', 'post_type':p.get('post_type') or ''})
        for link,label in anchors(p.get('post_content') or ''):
            found.setdefault(link,{'url':link,'title':label or link,'post_type':'linked'})
    return sorted(found.values(),key=lambda x:(x['post_type'],x['title'],x['url']))
def tokens(text):return set(x.lower().replace('\u200c','') for x in TOKEN_RE.findall(base.plain(text or '')))
def relevant_links(post,index,limit=12):
    own=normalize_url(canonical(post));target=tokens((post.get('post_title') or '')+' '+base.plain(post.get('post_content') or '')[:4000]);scored=[]
    important={'page':3,'product':2,'post':2,'linked':1}
    for item in index:
        if item['url']==own:continue
        cand=tokens((item.get('title') or '')+' '+urllib.parse.unquote(item['url']))
        score=len(target&cand)*4+important.get(item.get('post_type'),0)
        if post.get('post_type') in item['url']:score+=2
        scored.append((score,item['title'],item))
    scored.sort(key=lambda x:(-x[0],x[1]))
    return [x[2] for x in scored[:limit]]
def internal_urls(content):return {u for u in (normalize_url(x) for x in HREF_RE.findall(content or '')) if u}
def count_words(content):return len(WORD_RE.findall(base.plain(content or '')))
def mask_content(text):
    vals=[]
    def repl(m):
        token=f'[[[NAVAR_KEEP_{len(vals)}]]]';vals.append(m.group(0));return token
    return base.KEEP.sub(repl,text or ''),vals
def restore_content(text,vals):
    missing=[]
    for i,val in enumerate(vals):
        token=f'[[[NAVAR_KEEP_{i}]]]'
        if token not in text:missing.append(token)
        else:text=text.replace(token,val)
    return text,missing
def agnes(prompt):
    payload={'model':MODEL,'messages':[{'role':'system','content':'شما نویسنده و ویراستار ارشد فارسی و متخصص محتوای کشاورزی هستید. فقط HTML نهایی post_content را برگردانید.'},{'role':'user','content':prompt}],'temperature':0.72,'max_tokens':20000}
    req=urllib.request.Request(BASE+'/chat/completions',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':f'Bearer {KEY}','Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-city-rewrite-queue'})
    try:
        with urllib.request.urlopen(req,timeout=420) as response:data=json.load(response)
    except urllib.error.HTTPError as e:raise RuntimeError(f'Agnes HTTP {e.code}: {e.read().decode("utf-8","replace")[:1200]}')
    text=data['choices'][0]['message']['content'].strip()
    return re.sub(r'^```(?:html)?\s*|\s*```$','',text)
def initialize(posts,index,force=False):
    OUT.mkdir(parents=True,exist_ok=True);POSTS_OUT.mkdir(exist_ok=True);SQL_OUT.mkdir(exist_ok=True);ROLLBACK_OUT.mkdir(exist_ok=True)
    if QUEUE.exists() and not force:return json.loads(QUEUE.read_text(encoding='utf-8'))
    rows=[]
    for p in posts:
        try:pid=int(p['ID'])
        except Exception:continue
        if p.get('post_status')!='publish' or p.get('post_type') not in CITY_TYPES or not base.plain(p.get('post_content') or ''):continue
        rows.append({'id':pid,'post_type':p['post_type'],'title':p.get('post_title') or '', 'slug':p.get('post_name') or '', 'status':'excluded' if pid in EXCLUDED_IDS else 'pending','attempts':0})
    rows.sort(key=lambda x:(x['post_type'],x['id']))
    q={'version':1,'created_at':now(),'updated_at':now(),'model':MODEL,'rules':{'language':'fa','translate':False,'minimum_words':MIN_WORDS,'target_words':'1200-1500','minimum_internal_links':MIN_INTERNAL_LINKS,'maximum_similarity':MAX_SIMILARITY},'excluded_ids':sorted(EXCLUDED_IDS),'items':rows}
    QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');LINKS.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');write_status(q,'initialized');return q
def write_status(q,result='ready'):
    counts=Counter(x['status'] for x in q['items'])
    status={'result':result,'updated_at':now(),'model':MODEL,'total':len(q['items']),'pending':counts['pending'],'processing':counts['processing'],'completed':counts['completed'],'failed':counts['failed'],'excluded':counts['excluded'],'minimum_words':MIN_WORDS,'minimum_internal_links':MIN_INTERNAL_LINKS,'batch_size':BATCH_SIZE}
    STATUS.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
def build_combined(q):
    done=[x for x in q['items'] if x['status']=='completed']
    update=['START TRANSACTION;'];rollback=['START TRANSACTION;']
    for item in done:
        up=SQL_OUT/f"{item['id']}.sql";rb=ROLLBACK_OUT/f"{item['id']}.sql"
        if up.exists():update.append(up.read_text(encoding='utf-8').strip())
        if rb.exists():rollback.append(rb.read_text(encoding='utf-8').strip())
    (OUT/'rewrite-all-completed.sql').write_text('\n'.join(update+['COMMIT;'])+'\n',encoding='utf-8')
    (OUT/'rollback-all-completed.sql').write_text('\n'.join(rollback+['COMMIT;'])+'\n',encoding='utf-8')
def process(posts,index,q):
    if not KEY:raise RuntimeError('AGNES_API_KEY is missing')
    by_id={int(p['ID']):p for p in posts if str(p.get('ID','')).isdigit()}
    batch=[x for x in q['items'] if x['status'] in {'pending','failed'} and x.get('attempts',0)<4][:BATCH_SIZE]
    for item in batch:
        item['status']='processing';item['attempts']=item.get('attempts',0)+1;item['started_at']=now();q['updated_at']=now();QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
        p=by_id.get(item['id']);reason=''
        try:
            if not p:raise RuntimeError('Post not found in dump')
            candidates=relevant_links(p,index);masked,kept=mask_content(p['post_content']);existing=internal_urls(p['post_content']);allowed=existing|{x['url'] for x in candidates}
            link_lines='\n'.join(f"- {x['title']} | {x['url']}" for x in candidates)
            for attempt in range(1,5):
                prompt=f'''مقاله شهری زیر را از پایه و فقط به فارسی طبیعی، حرفه‌ای و منحصربه‌فرد بازنویسی کن؛ ترجمه نکن. خروجی باید دست‌کم {MIN_WORDS} کلمه و ترجیحاً ۱۲۰۰ تا ۱۵۰۰ کلمه باشد. نام شهر و هدف جستجو را حفظ کن. ساختار، ترتیب بخش‌ها، مقدمه و جمله‌بندی را واقعاً تغییر بده تا شباهت متنی حداکثر {MAX_SIMILARITY:.0%} باشد. اطلاعات فنی موجود را حفظ کن اما آمار، قیمت، ضمانت، ادعای محلی یا واقعیت تازه نساز. برای افزایش طول، راهنمای انتخاب، نصب، نگهداری، فیلتراسیون، فشار کاری، خطاهای رایج، پرسش‌های متداول و جمع‌بندی کاربردی را با اطلاعات عمومی و غیرادعایی توضیح بده. فقط یک H1 لازم نیست چون عنوان وردپرس جداست؛ از H2/H3، پاراگراف، فهرست و جدول در صورت نیاز استفاده کن.
تمام placeholderهای [[[NAVAR_KEEP_n]]] را دقیقاً یک‌بار و بدون تغییر نگه دار. HTML/Gutenberg، تصاویر، shortcodeها، شماره‌ها، تلفن‌ها و لینک‌های موجود حذف نشوند.
لینک‌سازی داخلی اجباری است: حداقل {MIN_INTERNAL_LINKS} و حداکثر ۷ لینک داخلی طبیعی و مرتبط در متن قرار بده. فقط از URLهای فهرست تأییدشده زیر استفاده کن؛ لینک به خود صفحه، لینک تکراری، انکرتکست نامرتبط و عبارت «اینجا کلیک کنید» ممنوع است. انکرتکست باید فارسی، طبیعی و توصیفی باشد.

عنوان: {p['post_title']}
نوع/استان: {p['post_type']}
بازخورد تلاش قبل: {reason or 'ندارد'}

فهرست لینک‌های تأییدشده و مرتبط:
{link_lines}

محتوای اصلی:
{masked}'''
                raw=agnes(prompt);new,missing_tokens=restore_content(raw,kept);words=count_words(new);score=base.similarity(p['post_content'],new);new_links=internal_urls(new);missing_protected=base.protected(p['post_content'])-base.protected(new);invalid=new_links-allowed
                if missing_tokens:reason=f'placeholder missing: {missing_tokens[:5]}';continue
                if missing_protected:reason=f'protected elements missing: {list(missing_protected.elements())[:5]}';continue
                if words<MIN_WORDS:reason=f'word count {words} < {MIN_WORDS}';continue
                if score>MAX_SIMILARITY:reason=f'similarity {score:.3f} > {MAX_SIMILARITY:.3f}';continue
                if len(new_links)<MIN_INTERNAL_LINKS:reason=f'internal links {len(new_links)} < {MIN_INTERNAL_LINKS}';continue
                if invalid:reason=f'unapproved links: {sorted(invalid)[:4]}';continue
                break
            else:raise RuntimeError(reason or 'QA failed')
            result={'id':item['id'],'post_type':p['post_type'],'title':p['post_title'],'slug':p['post_name'],'original':p['post_content'],'rewritten':new,'original_words':count_words(p['post_content']),'rewritten_words':words,'similarity':round(score,4),'internal_links':sorted(new_links),'completed_at':now()}
            (POSTS_OUT/f"{item['id']}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            (SQL_OUT/f"{item['id']}.sql").write_text(f"UPDATE `ha_posts` SET `post_content`='{base.escsql(new)}',`post_modified`=NOW(),`post_modified_gmt`=UTC_TIMESTAMP() WHERE `ID`={item['id']} AND `post_type`='{base.escsql(p['post_type'])}';\n",encoding='utf-8')
            (ROLLBACK_OUT/f"{item['id']}.sql").write_text(f"UPDATE `ha_posts` SET `post_content`='{base.escsql(p['post_content'])}' WHERE `ID`={item['id']};\n",encoding='utf-8')
            item.update({'status':'completed','completed_at':now(),'word_count':words,'similarity':round(score,4),'internal_link_count':len(new_links),'last_error':''});print(f"completed {item['id']} words={words} links={len(new_links)} similarity={score:.3f}",flush=True)
        except Exception as e:
            item.update({'status':'failed','last_error':str(e)[:700],'failed_at':now()});print(f"failed {item['id']}: {e}",flush=True)
        q['updated_at']=now();QUEUE.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');write_status(q,'processing');time.sleep(1)
    build_combined(q);write_status(q,'complete' if not any(x['status'] in {'pending','processing','failed'} and x.get('attempts',0)<4 for x in q['items']) else 'ready');return q
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--init-only',action='store_true');ap.add_argument('--force-init',action='store_true');args=ap.parse_args()
    posts=base.load_posts();index=build_link_index(posts);q=initialize(posts,index,args.force_init)
    if not args.init_only:process(posts,index,q)
if __name__=='__main__':main()
