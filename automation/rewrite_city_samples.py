#!/usr/bin/env python3
import gzip,html,json,os,re,time,urllib.request,urllib.error
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];DUMP=ROOT/'database/incoming/navaraby_wp569.sql.gz';OUT=ROOT/'artifacts/city-posts-sample';OUT.mkdir(parents=True,exist_ok=True)
BASE=os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/');KEY=os.getenv('AGNES_API_KEY','').strip();MODEL=os.getenv('AGNES_MODEL','agnes-2.5-flash')
COLS=['ID','post_author','post_date','post_date_gmt','post_content','post_title','post_excerpt','post_status','comment_status','ping_status','post_password','post_name','to_ping','pinged','post_modified','post_modified_gmt','post_content_filtered','post_parent','guid','menu_order','post_type','post_mime_type','comment_count']
EXCLUDE={'post','page','attachment','revision','nav_menu_item','product','product_variation','faq','shop_order','shop_coupon','wp_template','wp_template_part','wp_navigation','custom_css','customize_changeset'}
KEEP=re.compile(r'https?://[^\s"\'<>]+|\[[^\]]+\]|<!--.*?-->|<img\b[^>]*>|\b(?:\+?98|0)?9\d{9}\b|\b\d+(?:[.,]\d+)?\b',re.I|re.S)

def unescape(s):
    mp={'0':'\0','b':'\b','n':'\n','r':'\r','t':'\t','Z':'\x1a',"'":"'",'"':'"','\\':'\\'}
    return re.sub(r'\\(.)',lambda m:mp.get(m.group(1),m.group(1)),s,flags=re.S)
def parse_values(text):
    i=0;n=len(text)
    while i<n:
        while i<n and text[i]!='(':i+=1
        if i>=n:return
        i+=1;row=[];buf=[];quoted=False;esc=False;was=False
        while i<n:
            c=text[i]
            if quoted:
                if esc:buf.append('\\'+c);esc=False
                elif c=='\\':esc=True
                elif c=="'":quoted=False
                else:buf.append(c)
            else:
                if c=="'":quoted=True;was=True
                elif c in ',)':
                    raw=''.join(buf).strip();row.append(None if not was and raw.upper()=='NULL' else unescape(raw));buf=[];was=False
                    if c==')':yield row;i+=1;break
                else:buf.append(c)
            i+=1
def load_posts():
    rows=[];collect=False;parts=[]
    with gzip.open(DUMP,'rt',encoding='utf-8',errors='replace',newline='') as f:
        for line in f:
            if line.startswith('INSERT INTO `ha_posts`'):
                collect=True;parts=[line.split(' VALUES',1)[1] if ' VALUES' in line else '']
            elif collect:parts.append(line)
            else:continue
            if not line.rstrip().endswith(';'):continue
            collect=False
            for vals in parse_values(''.join(parts).rstrip().rstrip(';')):
                if len(vals)==len(COLS):rows.append(dict(zip(COLS,vals)))
    if not rows:raise RuntimeError('No ha_posts rows found')
    return rows
def plain(s):
    s=html.unescape(s or '');s=re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>',' ',s,flags=re.I|re.S)
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>|\[[^\]]+\]',' ',s)).strip()
def norm(s):return re.sub(r'\s+',' ',re.sub(r'[\W_\d]+',' ',plain(s).replace('\u200c',' '),flags=re.U)).strip()
def similarity(a,b):return SequenceMatcher(None,norm(a),norm(b),autojunk=False).ratio()
def protected(s):return Counter(KEEP.findall(s or ''))
def escsql(s):return (s or '').replace('\\','\\\\').replace("'","\\'").replace('\0','\\0').replace('\n','\\n').replace('\r','\\r').replace('\x1a','\\Z')
def agnes(prompt):
    payload={'model':MODEL,'messages':[{'role':'system','content':'شما ویراستار ارشد فارسی هستید. فقط محتوای نهایی فارسی را برگردانید.'},{'role':'user','content':prompt}],'temperature':0.75,'max_tokens':12000}
    req=urllib.request.Request(BASE+'/chat/completions',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':f'Bearer {KEY}','Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-city-samples'})
    try:
        with urllib.request.urlopen(req,timeout=300) as r:data=json.load(r)
    except urllib.error.HTTPError as e:raise RuntimeError(f'Agnes HTTP {e.code}: {e.read().decode("utf-8","replace")[:1000]}')
    text=data['choices'][0]['message']['content'].strip();return re.sub(r'^```(?:html)?\s*|\s*```$','',text)
def main():
    if not DUMP.exists():raise RuntimeError(f'Dump missing: {DUMP}')
    if not KEY:raise RuntimeError('AGNES_API_KEY is missing')
    posts=load_posts();groups=defaultdict(list)
    for p in posts:
        if p['post_status']=='publish' and p['post_type'] not in EXCLUDE and plain(p['post_content']):groups[p['post_type']].append(p)
    eligible={k:sorted(v,key=lambda x:int(x['ID'])) for k,v in groups.items() if len(v)>=3}
    selected=[]
    for pt in sorted(eligible):
        for p in eligible[pt]:
            selected.append(p)
            if len(selected)==3:break
        if len(selected)==3:break
    if len(selected)<3:raise RuntimeError(f'Only {len(selected)} eligible city posts found; groups={ {k:len(v) for k,v in eligible.items()} }')
    (OUT/'selection.json').write_text(json.dumps({'eligible_groups':{k:len(v) for k,v in eligible.items()},'selected':[{'id':int(p['ID']),'post_type':p['post_type'],'title':p['post_title']} for p in selected]},ensure_ascii=False,indent=2),encoding='utf-8')
    samples=[];updates=['START TRANSACTION;'];rollback=['START TRANSACTION;'];accepted=[]
    for pos,p in enumerate(selected,1):
        reason=''
        for attempt in range(1,4):
            prompt=f'''این پست شهری ایران را کاملاً به فارسی طبیعی و یکتا بازنویسی کن. ترجمه نکن. شهر، معنا، اطلاعات فنی، اعداد، تلفن‌ها، نشانی‌ها، URLها، shortcodeها، تصاویر و HTML/Gutenberg را حفظ کن. ادعای تازه نساز. ترتیب و جمله‌بندی را واقعاً تغییر بده و از مترادف‌سازی سطحی و keyword stuffing پرهیز کن. فقط post_content نهایی را بده.\nعنوان: {p['post_title']}\nنوع نوشته: {p['post_type']}\nبازخورد تلاش قبل: {reason or 'ندارد'}\n\n{p['post_content']}'''
            new=agnes(prompt);missing=protected(p['post_content'])-protected(new);score=similarity(p['post_content'],new);peer=max([similarity(new,x) for x in accepted] or [0])
            if missing:reason=f'عناصر محافظت‌شده حذف شد: {list(missing.elements())[:8]}';continue
            if len(plain(new))<max(450,int(len(plain(p['post_content']))*.7)):reason='خروجی کوتاه است';continue
            if score>.82 or peer>.78:reason=f'شباهت زیاد است: original={score:.3f}, peer={peer:.3f}';continue
            break
        else:raise RuntimeError(f'Post {p["ID"]} failed QA: {reason}')
        accepted.append(new);sample={'id':int(p['ID']),'post_type':p['post_type'],'title':p['post_title'],'slug':p['post_name'],'original':p['post_content'],'rewritten':new,'original_chars':len(plain(p['post_content'])),'rewritten_chars':len(plain(new)),'similarity':round(score,4)};samples.append(sample)
        (OUT/f'sample-{pos}-{p["ID"]}.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2),encoding='utf-8')
        updates.append(f"UPDATE `ha_posts` SET `post_content`='{escsql(new)}',`post_modified`=NOW(),`post_modified_gmt`=UTC_TIMESTAMP() WHERE `ID`={int(p['ID'])} AND `post_type`='{escsql(p['post_type'])}';")
        rollback.append(f"UPDATE `ha_posts` SET `post_content`='{escsql(p['post_content'])}' WHERE `ID`={int(p['ID'])};");print(f'[{pos}/3] {p["ID"]} {p["post_title"]}',flush=True);time.sleep(1)
    (OUT/'rewrite-samples.sql').write_text('\n'.join(updates+['COMMIT;'])+'\n',encoding='utf-8');(OUT/'rollback-samples.sql').write_text('\n'.join(rollback+['COMMIT;'])+'\n',encoding='utf-8');(OUT/'report.json').write_text(json.dumps([{k:s[k] for k in ('id','post_type','title','slug','original_chars','rewritten_chars','similarity')} for s in samples],ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
