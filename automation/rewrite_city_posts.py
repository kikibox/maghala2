#!/usr/bin/env python3
import argparse,csv,gzip,hashlib,html,json,os,re,time,urllib.request,urllib.error
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path

COLS=['ID','post_author','post_date','post_date_gmt','post_content','post_title','post_excerpt','post_status','comment_status','ping_status','post_password','post_name','to_ping','pinged','post_modified','post_modified_gmt','post_content_filtered','post_parent','guid','menu_order','post_type','post_mime_type','comment_count']
EXCLUDED={'attachment','revision','nav_menu_item','page','product','product_variation','faq','shop_order','shop_coupon','wp_template','wp_template_part','wp_navigation','custom_css','customize_changeset','post'}
PROTECTED=re.compile(r'https?://[^\s"\'<>]+|\[[^\]]+\]|<!--.*?-->|<img\b[^>]*>|\b(?:\+?98|0)?9\d{9}\b|\b\d+(?:[.,]\d+)?\b',re.I|re.S)
BASE=os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')
KEY=os.getenv('AGNES_API_KEY','').strip();MODEL=os.getenv('AGNES_MODEL','agnes-2.5-flash').strip()

def open_text(p):return gzip.open(p,'rt',encoding='utf-8',errors='replace',newline='') if str(p).endswith('.gz') else open(p,encoding='utf-8',errors='replace',newline='')
def unescape(s):
    if s is None:return None
    mp={'0':'\0','b':'\b','n':'\n','r':'\r','t':'\t','Z':'\x1a',"'":"'",'"':'"','\\':'\\'}
    return re.sub(r'\\(.)',lambda m:mp.get(m.group(1),m.group(1)),s,flags=re.S)
def tuples(text):
    i,n=0,len(text)
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
def load_posts(path):
    rows=[];collect=False;parts=[]
    with open_text(path) as f:
        for line in f:
            if line.startswith('INSERT INTO `ha_posts`'):
                collect=True;parts=[line.split(' VALUES',1)[1] if ' VALUES' in line else '']
            elif collect:parts.append(line)
            else:continue
            if not line.rstrip().endswith(';'):continue
            collect=False
            for vals in tuples(''.join(parts).rstrip().rstrip(';')):
                if len(vals)==len(COLS):rows.append(dict(zip(COLS,vals)))
    if not rows:raise SystemExit('No ha_posts rows found; expected table prefix ha_.')
    return rows
def plain(s):
    s=html.unescape(s or '');s=re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>',' ',s,flags=re.I|re.S)
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>|\[[^\]]+\]',' ',s)).strip()
def norm(s):return re.sub(r'\s+',' ',re.sub(r'[\W_\d]+',' ',plain(s).replace('\u200c',' '),flags=re.U)).strip()
def sim(a,b):return SequenceMatcher(None,norm(a),norm(b),autojunk=False).ratio()
def choose(posts,explicit):
    pub=[p for p in posts if p['post_status']=='publish' and plain(p['post_content'])];groups=defaultdict(list)
    for p in pub:groups[p['post_type']].append(p)
    wanted={x.strip() for x in explicit.split(',') if x.strip()} if explicit else {t for t,r in groups.items() if t not in EXCLUDED and len(r)>=3}
    rows=[p for p in pub if p['post_type'] in wanted]
    if not rows:raise SystemExit('No city posts selected. Run audit with explicit post_types.')
    return rows,wanted
def audit(posts,explicit,out,dump):
    rows,wanted=choose(posts,explicit);groups=defaultdict(list)
    for p in rows:groups[p['post_type']].append(p)
    inventory=[]
    for pt,items in sorted(groups.items()):
        for p in items:
            best=max(((sim(p['post_content'],q['post_content']),q['ID']) for q in items if q['ID']!=p['ID']),default=(0,None))
            inventory.append({'id':p['ID'],'post_type':pt,'title':p['post_title'],'slug':p['post_name'],'characters':len(plain(p['post_content'])),'nearest_similarity':round(best[0],4),'nearest_id':best[1]})
    out.mkdir(parents=True,exist_ok=True)
    with open(out/'inventory.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=inventory[0].keys());w.writeheader();w.writerows(inventory)
    report={'dump_sha256':hashlib.sha256(Path(dump).read_bytes()).hexdigest(),'selected_post_types':sorted(wanted),'post_count':len(rows),'similarity_ge_0_80':sum(x['nearest_similarity']>=.8 for x in inventory),'similarity_ge_0_90':sum(x['nearest_similarity']>=.9 for x in inventory)}
    (out/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));return rows
def request_agnes(prompt):
    payload={'model':MODEL,'messages':[{'role':'system','content':'شما ویراستار ارشد فارسی و متخصص محتوای مفید و غیرتکراری شهری هستید.'},{'role':'user','content':prompt}],'temperature':0.75,'max_tokens':12000}
    req=urllib.request.Request(BASE+'/chat/completions',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':f'Bearer {KEY}','Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-city-rewrite'})
    try:
        with urllib.request.urlopen(req,timeout=300) as r:data=json.load(r)
    except urllib.error.HTTPError as e:raise RuntimeError(f'Agnes HTTP {e.code}: {e.read().decode("utf-8","replace")[:1000]}')
    text=data['choices'][0]['message']['content'].strip();return re.sub(r'^```(?:html)?\s*|\s*```$','',text)
def protected(s):return Counter(PROTECTED.findall(s or ''))
def escsql(s):return (s or '').replace('\\','\\\\').replace("'","\\'").replace('\0','\\0').replace('\n','\\n').replace('\r','\\r').replace('\x1a','\\Z')
def rewrite(rows,out,limit):
    if not KEY:raise SystemExit('AGNES_API_KEY is missing')
    work=rows[:limit] if limit else rows;originals=[p['post_content'] for p in rows];accepted=[];updates=['START TRANSACTION;'];rollback=['START TRANSACTION;'];log=[]
    for pos,p in enumerate(work,1):
        peer_titles=[q['post_title'] for q in rows if q['post_type']==p['post_type'] and q['ID']!=p['ID']];reason=''
        for attempt in range(1,4):
            prompt=f'''محتوای وردپرس زیر را از ابتدا به فارسی طبیعی بازنویسی کن. معنا، قصد جستجو، اطلاعات فنی، اعداد، تلفن‌ها، نشانی‌ها، URLها، shortcodeها، تصاویر و ساختار HTML/Gutenberg را دقیق حفظ کن. متن باید مخصوص شهر عنوان باشد ولی هیچ واقعیت یا آمار تازه نساز. ترتیب توضیح و جمله‌بندی واقعاً تازه باشد، نه صرفاً مترادف‌سازی. از keyword stuffing و پاراگراف تکراری پرهیز کن. فقط post_content نهایی را برگردان.\nعنوان: {p['post_title']}\nنوع: {p['post_type']}\nعنوان‌های مشابه: {', '.join(peer_titles[:8])}\nبازخورد قبلی: {reason or 'ندارد'}\n\n{p['post_content']}'''
            new=request_agnes(prompt);missing=protected(p['post_content'])-protected(new);mx=max([sim(new,x) for x in originals+accepted] or [0])
            if missing:reason=f'عناصر محافظت‌شده حذف شده: {list(missing.elements())[:10]}';continue
            if len(plain(new))<max(450,int(len(plain(p['post_content']))*.70)):reason='خروجی کوتاه است';continue
            if mx>.78:reason=f'شباهت زیاد است: {mx:.3f}';continue
            break
        else:raise SystemExit(f'Post {p["ID"]} failed QA: {reason}')
        accepted.append(new);updates.append(f"UPDATE `ha_posts` SET `post_content`='{escsql(new)}',`post_modified`=NOW(),`post_modified_gmt`=UTC_TIMESTAMP() WHERE `ID`={int(p['ID'])} AND `post_type`='{escsql(p['post_type'])}';");rollback.append(f"UPDATE `ha_posts` SET `post_content`='{escsql(p['post_content'])}' WHERE `ID`={int(p['ID'])};")
        log.append({'id':int(p['ID']),'post_type':p['post_type'],'title':p['post_title'],'old_chars':len(plain(p['post_content'])),'new_chars':len(plain(new)),'old_new_similarity':round(sim(p['post_content'],new),4)});print(f'[{pos}/{len(work)}] {p["ID"]} OK');time.sleep(1)
    (out/'rewrite.sql').write_text('\n'.join(updates+['COMMIT;'])+'\n',encoding='utf-8');(out/'rollback.sql').write_text('\n'.join(rollback+['COMMIT;'])+'\n',encoding='utf-8');(out/'rewrite-report.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
ap=argparse.ArgumentParser();ap.add_argument('command',choices=['audit','rewrite']);ap.add_argument('--dump',required=True);ap.add_argument('--post-types',default='');ap.add_argument('--out',type=Path,required=True);ap.add_argument('--max-posts',type=int,default=0)
a=ap.parse_args();rows=audit(load_posts(a.dump),a.post_types,a.out,a.dump)
if a.command=='rewrite':rewrite(rows,a.out,a.max_posts)
