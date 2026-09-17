#!/usr/bin/env python3
import concurrent.futures,json,os,time
from pathlib import Path
import city_rewrite_queue as q

WORKERS=max(1,int(os.getenv('PARALLEL_WORKERS','4')))
BATCH=max(WORKERS,int(os.getenv('BATCH_SIZE','20')))

def missing_list(value):
    if hasattr(value,'elements'):return list(value.elements())
    return list(value)

def rewrite_one(item,post,index):
    try:
        candidates=q.relevant_links(post,index)
        masked,kept=q.mask_content(post['post_content'])
        existing=q.internal_urls(post['post_content'])
        allowed=existing|{x['url'] for x in candidates}
        link_lines='\n'.join(f"- {x['title']} | {x['url']}" for x in candidates)
        reason=''
        for attempt in range(1,5):
            prompt=f'''مقاله شهری زیر را از پایه و فقط به فارسی طبیعی و حرفه‌ای بازنویسی کن؛ ترجمه نکن. خروجی دست‌کم {q.MIN_WORDS} کلمه و ترجیحاً ۱۲۰۰ تا ۱۵۰۰ کلمه باشد. نام شهر و هدف جستجو حفظ شود. ساختار و جمله‌بندی را واقعاً تغییر بده تا شباهت حداکثر {q.MAX_SIMILARITY:.0%} باشد. اطلاعات فنی موجود را حفظ کن اما قیمت، آمار، ضمانت، ادعای محلی، زمان حمل یا واقعیت تازه نساز. متن را با راهنمای انتخاب، نصب، نگهداری، فیلتراسیون، فشار کاری، خطاهای رایج و پرسش‌های متداولِ عمومی گسترش بده. هیچ واژه چینی، عربی، ویتنامی یا انگلیسی غیرضروری در متن فارسی وارد نکن.
تمام placeholderهای [[[NAVAR_KEEP_n]]] را دقیقاً یک‌بار و بدون تغییر نگه دار. HTML، تصاویر، shortcodeها، شماره‌ها، تلفن‌ها و لینک‌های موجود حذف نشوند.
لینک‌سازی داخلی اجباری است: حداقل {q.MIN_INTERNAL_LINKS} لینک طبیعی و مرتبط قرار بده. فقط از URLهای تأییدشده زیر استفاده کن. لینک به خود صفحه، انکرتکست نامرتبط و عبارت «اینجا کلیک کنید» ممنوع است.
فقط HTML نهایی post_content را برگردان.

عنوان: {post['post_title']}
نوع/استان: {post['post_type']}
بازخورد تلاش قبل: {reason or 'ندارد'}

لینک‌های تأییدشده:
{link_lines}

محتوای اصلی:
{masked}'''
            raw=q.agnes(prompt)
            new,missing_tokens=q.restore_content(raw,kept)
            words=q.count_words(new)
            score=q.base.similarity(post['post_content'],new)
            new_links=q.internal_urls(new)
            missing_protected=q.base.protected(post['post_content'])-q.base.protected(new)
            invalid=new_links-allowed
            if missing_tokens:reason=f'placeholder missing: {missing_tokens[:5]}';continue
            if missing_protected:reason=f'protected elements missing: {missing_list(missing_protected)[:5]}';continue
            if words<q.MIN_WORDS:reason=f'word count {words} < {q.MIN_WORDS}';continue
            if score>q.MAX_SIMILARITY:reason=f'similarity {score:.3f} > {q.MAX_SIMILARITY:.3f}';continue
            if len(new_links)<q.MIN_INTERNAL_LINKS:reason=f'internal links {len(new_links)} < {q.MIN_INTERNAL_LINKS}';continue
            if invalid:reason=f'unapproved links: {sorted(invalid)[:4]}';continue
            break
        else:raise RuntimeError(reason or 'QA failed')
        result={'id':item['id'],'post_type':post['post_type'],'title':post['post_title'],'slug':post['post_name'],'original':post['post_content'],'rewritten':new,'original_words':q.count_words(post['post_content']),'rewritten_words':words,'similarity':round(score,4),'internal_links':sorted(new_links),'completed_at':q.now()}
        (q.POSTS_OUT/f"{item['id']}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        (q.SQL_OUT/f"{item['id']}.sql").write_text(f"UPDATE `ha_posts` SET `post_content`='{q.base.escsql(new)}',`post_modified`=NOW(),`post_modified_gmt`=UTC_TIMESTAMP() WHERE `ID`={item['id']} AND `post_type`='{q.base.escsql(post['post_type'])}';\n",encoding='utf-8')
        (q.ROLLBACK_OUT/f"{item['id']}.sql").write_text(f"UPDATE `ha_posts` SET `post_content`='{q.base.escsql(post['post_content'])}' WHERE `ID`={item['id']};\n",encoding='utf-8')
        return {'status':'completed','completed_at':q.now(),'word_count':words,'similarity':round(score,4),'internal_link_count':len(new_links),'last_error':''}
    except Exception as exc:
        return {'status':'failed','failed_at':q.now(),'last_error':str(exc)[:700]}

def main():
    if not q.KEY:raise RuntimeError('AGNES_API_KEY is missing')
    posts=q.base.load_posts();index=q.build_link_index(posts)
    data=q.initialize(posts,index,False)
    by_id={int(p['ID']):p for p in posts if str(p.get('ID','')).isdigit()}
    for item in data['items']:
        if item['status']=='processing':item['status']='failed';item['last_error']='Recovered stale processing state'
    batch=[x for x in data['items'] if x['status'] in {'pending','failed'} and x.get('attempts',0)<4][:BATCH]
    if not batch:
        q.build_combined(data);q.write_status(data,'complete');return
    for item in batch:
        item['status']='processing';item['attempts']=item.get('attempts',0)+1;item['started_at']=q.now()
    data['updated_at']=q.now();q.QUEUE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');q.write_status(data,'processing')
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures={pool.submit(rewrite_one,item,by_id.get(item['id']),index):item for item in batch}
        for future in concurrent.futures.as_completed(futures):
            item=futures[future]
            try:update=future.result()
            except Exception as exc:update={'status':'failed','failed_at':q.now(),'last_error':str(exc)[:700]}
            item.update(update);data['updated_at']=q.now()
            q.QUEUE.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');q.write_status(data,'processing')
            print(f"{item['status']} {item['id']} words={item.get('word_count','-')} links={item.get('internal_link_count','-')} error={item.get('last_error','')}",flush=True)
    q.build_combined(data)
    retryable=any(x['status'] in {'pending','processing','failed'} and x.get('attempts',0)<4 for x in data['items'])
    q.write_status(data,'ready' if retryable else 'complete')

if __name__=='__main__':main()
