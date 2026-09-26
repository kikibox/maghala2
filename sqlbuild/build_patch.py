#!/usr/bin/env python3
import gzip, hashlib, html, json, os, re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT=Path(__file__).resolve().parents[1]
TRANS=ROOT/'translations'; OUT=ROOT/'artifacts'; OUT.mkdir(exist_ok=True)
POST_ID_START=502017; META_ID_START=67470
CATEGORY={'ar-IQ':259,'tg-TJ':261}; PREFIX={'ar-IQ':'iraq','tg-TJ':'tj','en-US':'en'}; LANGS=('ar-IQ','tg-TJ','en-US')

def esc(v):
 s=str(v); return s.replace('\\','\\\\').replace("'","\\'").replace('\0','\\0').replace('\r','\\r').replace('\n','\\n')
def q(v): return "'"+esc(v)+"'"
def normalize_slug(v): return unquote(str(v or '')).strip('/').lower()

LEADING_TOC_RE=re.compile(r'^\s*<div\b(?=[^>]*\bid\s*=\s*(["\'])toc_container\1)[^>]*>.*?</div>\s*',re.I|re.S)
HEADING_LIST_RE=re.compile(r'(?P<heading><h(?P<level>[2-4])\b[^>]*>.*?</h(?P=level)>)\s*(?P<list><(?P<listtag>ul|ol)\b[^>]*>.*?</(?P=listtag)>)\s*',re.I|re.S)
TAG_RE=re.compile(r'<[^>]+>')
SIMPLE_TRANSLATE_RE=re.compile(r'\s*<div\b(?=[^>]*\bid\s*=\s*(["\'])simple-translate\1)[^>]*>.*\Z',re.I|re.S)
def plain_text(x): return re.sub(r'\s+',' ',html.unescape(TAG_RE.sub(' ',x))).strip().lower()
def is_toc_heading(text):
 c=re.sub(r'[\s\u200c\u200f\u200e]+',' ',text).strip()
 exact={'فهرست مطالب','فهرست محتوا','قائمة المحتويات','فهرس المحتويات','المحتويات','мундариҷа','мундариҷаи мақола','ҷадвали мундариҷа'}
 return c in exact or ('فهرست' in c and ('مطالب' in c or 'محتوا' in c)) or ('محتو' in c and ('قائمة' in c or 'فهرس' in c)) or 'мундариҷ' in c
def clean_body(body):
 stats={'container_toc':0,'manual_toc':0,'browser_junk':0}
 cleaned,n=LEADING_TOC_RE.subn('',body,count=1); stats['container_toc']=n
 def remove_manual(m):
  if is_toc_heading(plain_text(m.group('heading'))): stats['manual_toc']+=1; return ''
  return m.group(0)
 cleaned=HEADING_LIST_RE.sub(remove_manual,cleaned)
 cleaned,n=SIMPLE_TRANSLATE_RE.subn('',cleaned,count=1); stats['browser_junk']=n
 return cleaned.strip()+'\n',stats

folders=sorted((p for p in TRANS.iterdir() if p.is_dir()),key=lambda p:int(p.name))
if not folders: raise SystemExit('No automated translation folders found')
records=[]; slug_maps={x:{} for x in LANGS}; used=set(); cleanup_totals={'container_toc':0,'manual_toc':0,'browser_junk':0}
for language_group in (('ar-IQ','tg-TJ'),('en-US',)):
 for folder in folders:
  source_id=int(folder.name)
  for lang in language_group:
   hp=folder/f'{lang}.html'; jp=folder/f'{lang}.json'
   if not hp.exists() or not jp.exists(): raise SystemExit(f'Missing files for {source_id}:{lang}')
   m=json.loads(jp.read_text(encoding='utf-8')); body,stats=clean_body(hp.read_text(encoding='utf-8'))
   for k,v in stats.items(): cleanup_totals[k]+=v
   if not m.get('validated') or m.get('language')!=lang or int(m.get('source_id'))!=source_id: raise SystemExit(f'Invalid manifest for {source_id}:{lang}')
   if len(body)<100 or not m.get('title') or not m.get('slug'): raise SystemExit(f'Empty translation for {source_id}:{lang}')
   slug=re.sub(r'[^a-z0-9-]+','-',m['slug'].lower()).strip('-')[:180] or f'translation-{source_id}'; original=slug; n=2
   while slug in used: slug=f'{original}-{source_id}-{n}'; n+=1
   used.add(slug); m['_final_slug']=slug; slug_maps[lang][normalize_slug(m.get('source_slug'))]=slug; records.append((source_id,lang,m,body))
slug_maps['ar-IQ']['انواع-سیستم-های-آبیاری']='anwa-anthimat-al-ray'; slug_maps['tg-TJ']['انواع-سیستم-های-آبیاری']='navhoi-sistemahoi-obyor'; slug_maps['en-US']['انواع-سیستم-های-آبیاری']='types-of-irrigation-systems'
href_re=re.compile(r'href=("|\')(.*?)(\1)',re.I)
def localize(body,lang):
 def repl(m):
  parsed=urlparse(m.group(2))
  if parsed.netloc and parsed.netloc.lower() not in ('navar-abyari.ir','www.navar-abyari.ir'): return m.group(0)
  path=unquote(parsed.path).strip('/')
  if not path or path.startswith(('iraq/','iq/','tj/','en/','wp-content/','wp-admin/','wp-json/')): return m.group(0)
  target=slug_maps[lang].get(normalize_slug(path.split('/')[-1]))
  if not target: return m.group(0)
  new='https://navar-abyari.ir/'+PREFIX[lang]+'/'+target+'/'
  if parsed.query: new+='?'+parsed.query
  if parsed.fragment: new+='#'+parsed.fragment
  return f'href={m.group(1)}{new}{m.group(1)}'
 return href_re.sub(repl,body)

now_utc=datetime.now(timezone.utc).replace(microsecond=0); now_local=now_utc+timedelta(hours=3,minutes=30)
modified=now_local.strftime('%Y-%m-%d %H:%M:%S'); modified_gmt=now_utc.strftime('%Y-%m-%d %H:%M:%S')
post_rows=[]; meta_rows=[]; rel_rows=[]; dynamic_rel_rows=[]; hotfix_rows=[]; manifest_rows=[]; english_post_rows=[]; english_meta_rows=[]; english_rel_rows=[]; post_id=POST_ID_START; meta_id=META_ID_START
for source_id,lang,m,body in records:
 source_date=str(m.get('source_date') or modified).replace('T',' ')[:19]
 if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',source_date): source_date=modified
 try: source_gmt=(datetime.strptime(source_date,'%Y-%m-%d %H:%M:%S')-timedelta(hours=3,minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
 except ValueError: source_gmt=modified_gmt
 localized=localize(body,lang)
 values=[post_id,1,source_date,source_gmt,localized,m['title'],'','publish','closed','closed','',m['_final_slug'],'','',modified,modified_gmt,'',0,'https://navar-abyari.ir/?p='+str(post_id),0,'post','',0]
 post_row='('+', '.join(q(v) for v in values)+')';post_rows.append(post_row)
 if lang=='en-US':english_post_rows.append(post_row)
 for key,val in [('_navar_translation_source_id',source_id),('_navar_translation_language',lang),('_yoast_wpseo_title',m.get('seo_title','')),('_yoast_wpseo_metadesc',m.get('seo_description',''))]:
  meta_row=f'({meta_id},{post_id},{q(key)},{q(val)})';meta_rows.append(meta_row)
  if lang=='en-US':english_meta_rows.append(meta_row)
  meta_id+=1
 if lang in CATEGORY:
  rel_row=f'({post_id},{CATEGORY[lang]},0)';rel_rows.append(rel_row)
 else:
  rel_sql=f"INSERT INTO `ha_term_relationships` (`object_id`,`term_taxonomy_id`,`term_order`) SELECT {post_id},tt.term_taxonomy_id,0 FROM `ha_term_taxonomy` tt JOIN `ha_terms` t ON t.term_id=tt.term_id WHERE tt.taxonomy='category' AND t.slug IN ('en','english') ORDER BY (t.slug='en') DESC LIMIT 1;"
  dynamic_rel_rows.append(rel_sql);english_rel_rows.append(rel_sql)
 hotfix_rows.append(f'UPDATE `ha_posts` SET `post_content`={q(localized)}, `post_modified`={q(modified)}, `post_modified_gmt`={q(modified_gmt)} WHERE `ID`={post_id} AND `post_type`=\'post\';')
 manifest_rows.append({'post_id':post_id,'source_id':source_id,'language':lang,'slug':m['_final_slug'],'category_term_taxonomy_id':CATEGORY.get(lang),'category_slug':'en' if lang=='en-US' else None}); post_id+=1
header=f'-- Corrected multilingual translation patch for navar-abyari.ir\n-- Canonical prefixes: /iraq/, /tj/, /en/.\n-- Automated units: {len(records)}.\nSET NAMES utf8mb4;\nSTART TRANSACTION;\n\n'
posts='INSERT INTO `ha_posts` (`ID`,`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_password`,`post_name`,`to_ping`,`pinged`,`post_modified`,`post_modified_gmt`,`post_content_filtered`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) VALUES\n'+',\n'.join(post_rows)+';\n\n'
meta='INSERT INTO `ha_postmeta` (`meta_id`,`post_id`,`meta_key`,`meta_value`) VALUES\n'+',\n'.join(meta_rows)+';\n\n'
rels='INSERT INTO `ha_term_relationships` (`object_id`,`term_taxonomy_id`,`term_order`) VALUES\n'+',\n'.join(rel_rows)+';\n\n'+'\n'.join(dynamic_rel_rows)+"\n\nUPDATE `ha_term_taxonomy` SET `count`=(SELECT COUNT(*) FROM `ha_term_relationships` r WHERE r.term_taxonomy_id=`ha_term_taxonomy`.`term_taxonomy_id`) WHERE `taxonomy`='category';\n\nCOMMIT;\n"
sql=header+posts+meta+rels
(OUT/'generated-translations.sql').write_text(sql,encoding='utf-8')
with gzip.GzipFile(filename='',mode='wb',fileobj=open(OUT/'generated-translations.sql.gz','wb'),mtime=0) as gz: gz.write(sql.encode())
english_header='-- English-only translation import. Requires category slug en or english.\nSET NAMES utf8mb4;\nSTART TRANSACTION;\n\n'
english_posts='INSERT INTO `ha_posts` (`ID`,`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_password`,`post_name`,`to_ping`,`pinged`,`post_modified`,`post_modified_gmt`,`post_content_filtered`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) VALUES\n'+',\n'.join(english_post_rows)+';\n\n'
english_meta='INSERT INTO `ha_postmeta` (`meta_id`,`post_id`,`meta_key`,`meta_value`) VALUES\n'+',\n'.join(english_meta_rows)+';\n\n'
english_sql=english_header+english_posts+english_meta+'\n'.join(english_rel_rows)+"\nUPDATE `ha_term_taxonomy` SET `count`=(SELECT COUNT(*) FROM `ha_term_relationships` r WHERE r.term_taxonomy_id=`ha_term_taxonomy`.`term_taxonomy_id`) WHERE `taxonomy`='category';\nCOMMIT;\n"
(OUT/'generated-english-translations.sql').write_text(english_sql,encoding='utf-8')
with gzip.GzipFile(filename='',mode='wb',fileobj=open(OUT/'generated-english-translations.sql.gz','wb'),mtime=0) as gz: gz.write(english_sql.encode())
hotfix='-- Hotfix for translations already imported into navar-abyari.ir\nSET NAMES utf8mb4;\nSTART TRANSACTION;\n'+'\n'.join(hotfix_rows)+'\nCOMMIT;\n'
(OUT/'fix-imported-translations.sql').write_text(hotfix,encoding='utf-8')
with gzip.GzipFile(filename='',mode='wb',fileobj=open(OUT/'fix-imported-translations.sql.gz','wb'),mtime=0) as gz: gz.write(hotfix.encode())
report={'automated_source_articles':len(folders),'automated_translation_units':len(records),'post_id_start':POST_ID_START,'post_id_end':post_id-1,'meta_id_start':META_ID_START,'meta_id_end':meta_id-1,'cleanup':cleanup_totals,'sql_bytes':len(sql.encode()),'sql_sha256':hashlib.sha256(sql.encode()).hexdigest(),'gzip_sha256':hashlib.sha256((OUT/'generated-translations.sql.gz').read_bytes()).hexdigest(),'hotfix_sql_sha256':hashlib.sha256(hotfix.encode()).hexdigest(),'hotfix_gzip_sha256':hashlib.sha256((OUT/'fix-imported-translations.sql.gz').read_bytes()).hexdigest(),'generated_at_utc':now_utc.isoformat(),'rows':manifest_rows}
(OUT/'generated-translations-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False,indent=2))
