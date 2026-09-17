#!/usr/bin/env python3
import json,time
import rewrite_city_samples as b

CITY_TYPES={'zanjan','shiraz','isfahan','mashhad','ahvaz','yazd','ardabil','qazvin','hamadan','shahrekord','arak','zahedan'}

def mask_content(text):
    tokens=[]
    def repl(match):
        token=f'[[[NAVAR_KEEP_{len(tokens)}]]]';tokens.append(match.group(0));return token
    return b.KEEP.sub(repl,text),tokens

def restore_content(text,tokens):
    missing=[]
    for i,value in enumerate(tokens):
        token=f'[[[NAVAR_KEEP_{i}]]]'
        if token not in text:missing.append(token)
        else:text=text.replace(token,value)
    return text,missing

def main():
    if not b.DUMP.exists(): raise RuntimeError(f'Dump missing: {b.DUMP}')
    if not b.KEY: raise RuntimeError('AGNES_API_KEY is missing')
    posts=b.load_posts();groups={t:[] for t in CITY_TYPES}
    for p in posts:
        if p['post_status']=='publish' and p['post_type'] in CITY_TYPES and b.plain(p['post_content']):groups[p['post_type']].append(p)
    groups={k:sorted(v,key=lambda x:int(x['ID'])) for k,v in groups.items() if v};selected=[]
    for pt in sorted(groups):
        selected.extend(groups[pt][:3-len(selected)])
        if len(selected)==3:break
    if len(selected)!=3:raise RuntimeError(f'Expected 3 city posts, found {len(selected)}')
    b.OUT.mkdir(parents=True,exist_ok=True)
    for pattern in ('sample-*.json','report.json','rewrite-samples.sql','rollback-samples.sql'): 
        for old in b.OUT.glob(pattern):old.unlink()
    (b.OUT/'selection.json').write_text(json.dumps({'city_groups':{k:len(v) for k,v in sorted(groups.items())},'selected':[{'id':int(p['ID']),'post_type':p['post_type'],'title':p['post_title']} for p in selected]},ensure_ascii=False,indent=2),encoding='utf-8')
    updates=['START TRANSACTION;'];rollback=['START TRANSACTION;'];accepted=[];report=[]
    for pos,p in enumerate(selected,1):
        masked,tokens=mask_content(p['post_content']);reason=''
        for attempt in range(1,5):
            prompt=f'''این مقاله مخصوص یکی از شهرهای ایران است. آن را کاملاً به فارسی طبیعی، حرفه‌ای و منحصربه‌فرد بازنویسی کن؛ ترجمه نکن. نام شهر، هدف جستجو، معنی و اطلاعات فنی را حفظ کن و واقعیت یا آمار جدید نساز. ترتیب توضیحات و جمله‌بندی را واقعاً تغییر بده؛ مترادف‌سازی سطحی و keyword stuffing ممنوع است. تمام placeholderهای [[[NAVAR_KEEP_n]]] را دقیقاً بدون تغییر و فقط یک‌بار در جای مناسب نگه دار. ساختار HTML/Gutenberg را حفظ کن. طول متن کمتر از ۷۰٪ متن اصلی نشود. فقط post_content نهایی را بده.\nعنوان: {p['post_title']}\nشهر/post type: {p['post_type']}\nبازخورد قبلی: {reason or 'ندارد'}\n\n{masked}'''
            raw=b.agnes(prompt);new,missing_placeholders=restore_content(raw,tokens)
            missing=b.protected(p['post_content'])-b.protected(new);score=b.similarity(p['post_content'],new);peer=max([b.similarity(new,x) for x in accepted] or [0]);ratio=len(b.plain(new))/max(1,len(b.plain(p['post_content'])))
            if missing_placeholders:reason=f'placeholderها حذف شده‌اند: {missing_placeholders[:8]}';continue
            if missing:reason=f'عناصر محافظت‌شده حذف شده: {list(missing.elements())[:8]}';continue
            if ratio<.62:reason=f'خروجی کوتاه است: {ratio:.2f}';continue
            if score>.86 or peer>.82:reason=f'شباهت زیاد است: original={score:.3f}, peer={peer:.3f}';continue
            break
        else:raise RuntimeError(f'Post {p["ID"]} failed QA: {reason}')
        accepted.append(new);sample={'id':int(p['ID']),'post_type':p['post_type'],'title':p['post_title'],'slug':p['post_name'],'original':p['post_content'],'rewritten':new,'original_chars':len(b.plain(p['post_content'])),'rewritten_chars':len(b.plain(new)),'similarity':round(score,4)}
        (b.OUT/f'sample-{pos}-{p["ID"]}.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2),encoding='utf-8');report.append({k:sample[k] for k in ('id','post_type','title','slug','original_chars','rewritten_chars','similarity')})
        updates.append(f"UPDATE `ha_posts` SET `post_content`='{b.escsql(new)}',`post_modified`=NOW(),`post_modified_gmt`=UTC_TIMESTAMP() WHERE `ID`={int(p['ID'])} AND `post_type`='{b.escsql(p['post_type'])}';");rollback.append(f"UPDATE `ha_posts` SET `post_content`='{b.escsql(p['post_content'])}' WHERE `ID`={int(p['ID'])};")
        print(f'[{pos}/3] {p["ID"]} {p["post_type"]} {p["post_title"]}',flush=True);time.sleep(1)
    (b.OUT/'rewrite-samples.sql').write_text('\n'.join(updates+['COMMIT;'])+'\n',encoding='utf-8');(b.OUT/'rollback-samples.sql').write_text('\n'.join(rollback+['COMMIT;'])+'\n',encoding='utf-8');(b.OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
