#!/usr/bin/env python3
"""Build immutable, upload-ready 50-article ZIP packages."""
from __future__ import annotations
import hashlib,json,os,re,shutil,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'article-content-queue';PACKAGES=OUT/'packages'
TRANS=OUT/'translations';TRANS_SQL=OUT/'translation-sql';TRANS_ROLLBACK=OUT/'translation-rollback'
LANGUAGES=('ar-IQ','tg-TJ','en-US')
BATCH_SIZE=max(1,int(os.getenv('PACKAGE_BATCH_SIZE','50')))
UPLOAD_SUBDIR=(os.getenv('ARTICLE_IMAGE_UPLOAD_SUBDIR') or '2026/09/navar-article-generated').strip('/')
DB_NAME=os.getenv('WORDPRESS_DB_NAME','navaraby_wp569').strip()
if not re.fullmatch(r'[A-Za-z0-9_]+',DB_NAME):raise RuntimeError('WORDPRESS_DB_NAME contains unsafe characters')

def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def load(path,default):
 try:value=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return default
 return value if isinstance(value,dict) else default

def item_id(item):return str(item.get('id') or '')

def normalize_sql(sql):
 sql=sql.replace('SET NAMES utf8mb4;', "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_520_ci;\nSET collation_connection = 'utf8mb4_unicode_520_ci';")
 sql=sql.replace('meta_value=@queue_key','meta_value COLLATE utf8mb4_unicode_520_ci = @queue_key COLLATE utf8mb4_unicode_520_ci')
 return sql

def translation_artifacts(key):
 rows=[]
 for lang in LANGUAGES:
  rows.append({
   'lang':lang,
   'html':TRANS/key/f'{lang}.html',
   'json':TRANS/key/f'{lang}.json',
   'sql':TRANS_SQL/f'{key}-{lang}.sql',
   'rollback':TRANS_ROLLBACK/f'{key}-{lang}.sql',
  })
 return rows

def batch_ready(batch):
 return all(
  all(all(row[name].exists() for name in ('html','json','sql','rollback')) for row in translation_artifacts(item_id(item)))
  for item in batch
 )

def ordered_completed(completed,old):
 by_id={item_id(x):x for x in completed};locked=[];seen=set()
 for package in old.get('packages',[]):
  for post in package.get('posts',[]):
   key=str(post.get('id') or '')
   if key in by_id and key not in seen:locked.append(by_id[key]);seen.add(key)
 remaining=[x for x in completed if item_id(x) not in seen]
 remaining.sort(key=lambda x:(x.get('completed_at',''),item_id(x)))
 return locked+remaining

def healthy(path,name,batch):
 expected={item_id(x) for x in batch}
 try:
  with zipfile.ZipFile(path) as z:
   if z.testzip() is not None:return None
   names=set(z.namelist())
   manifest=json.loads(z.read('manifest.json').decode('utf-8'))
   create_name=f'sql/create-{name}.sql' if f'sql/create-{name}.sql' in names else 'sql/create-batch.sql'
   rollback_name=f'sql/rollback-{name}.sql' if f'sql/rollback-{name}.sql' in names else 'sql/rollback-batch.sql'
   sql=z.read(create_name).decode('utf-8')
   actual={str(x.get('id') or '') for x in manifest.get('posts',[])}
   if manifest.get('batch')!=name or actual!=expected or int(manifest.get('post_count',0))!=len(batch):return None
   if int(manifest.get('source_post_count',0))!=len(batch):return None
   if int(manifest.get('translation_post_count',0))!=len(batch)*len(LANGUAGES):return None
   if int(manifest.get('total_post_count',0))!=len(batch)*(1+len(LANGUAGES)):return None
   if tuple(manifest.get('languages',[]))!=LANGUAGES:return None
   if rollback_name not in names or f'USE `{DB_NAME}`;' not in sql[:500]:return None
   if 'SET NAMES utf8mb4;' in sql or 'meta_value=@queue_key' in sql:return None
   if 'SET NAMES utf8mb4 COLLATE utf8mb4_unicode_520_ci;' not in sql:return None
   translation_keys=set(re.findall(r'article-translation:([A-Za-z0-9_-]+):(ar-IQ|tg-TJ|en-US)',sql))
   if len(translation_keys)!=len(batch)*len(LANGUAGES):return None
   if len([x for x in names if x.startswith('items/') and x.endswith('.json')])<len(batch):return None
   if len([x for x in names if x.startswith('translations/') and x.endswith('.json')])<len(batch)*len(LANGUAGES):return None
   if not any(x.startswith('wp-content/uploads/') for x in names):return None
   manifest.update(zip=path.name,zip_sha256=sha256(path),zip_bytes=path.stat().st_size)
   return manifest
 except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,json.JSONDecodeError):return None

def build(batch,name):
 work=PACKAGES/name
 if work.exists():shutil.rmtree(work)
 (work/'sql').mkdir(parents=True);(work/'items').mkdir();(work/'translations').mkdir();image_root=work/'wp-content'/'uploads'/UPLOAD_SUBDIR;image_root.mkdir(parents=True)
 preamble=['SET NAMES utf8mb4 COLLATE utf8mb4_unicode_520_ci;',"SET collation_connection = 'utf8mb4_unicode_520_ci';",f'USE `{DB_NAME}`;']
 create=[f'-- Create {len(batch)} Persian articles and {len(batch)*len(LANGUAGES)} linked translations ({name})',*preamble]
 rollback_header=[f'-- Roll back {len(batch)} Persian articles and {len(batch)*len(LANGUAGES)} linked translations ({name})',*preamble]
 translation_rollbacks=[];source_rollbacks=[]
 posts=[];files=[]
 for item in batch:
  key=item_id(item);posts.append({'id':key,'title':item.get('title'),'slug':item.get('slug'),'vertical':item.get('vertical'),'completed_at':item.get('completed_at'),'word_count':item.get('word_count')})
  cf=OUT/'sql'/f'{key}.sql';rf=OUT/'rollback'/f'{key}.sql';jf=OUT/'items'/f'{key}.json'
  if not cf.exists() or not rf.exists() or not jf.exists():raise RuntimeError(f'Incomplete artifacts for completed article {key}')
  create.append(f'\n-- Persian source article: {key}\n'+normalize_sql(cf.read_text(encoding='utf-8')))
  source_rollbacks.append(f'\n-- Persian source rollback: {key}\n'+normalize_sql(rf.read_text(encoding='utf-8')))
  shutil.copy2(jf,work/'items'/jf.name);files.append(f'items/{jf.name}')
  for row in translation_artifacts(key):
   if not all(row[name].exists() for name in ('html','json','sql','rollback')):raise RuntimeError(f'Incomplete translation artifacts for {key}/{row["lang"]}')
   create.append(f'\n-- Linked translation: {key}/{row["lang"]}\n'+normalize_sql(row['sql'].read_text(encoding='utf-8')))
   translation_rollbacks.append(f'\n-- Translation rollback: {key}/{row["lang"]}\n'+normalize_sql(row['rollback'].read_text(encoding='utf-8')))
   target=work/'translations'/key;target.mkdir(parents=True,exist_ok=True)
   shutil.copy2(row['html'],target/row['html'].name);shutil.copy2(row['json'],target/row['json'].name)
   files.extend([f'translations/{key}/{row["html"].name}',f'translations/{key}/{row["json"].name}'])
  data=load(jf,{})
  for image in data.get('images',[]):
   image_name=Path(image['name'] if isinstance(image,dict) else image).name;src=OUT/'images'/image_name
   if not src.exists():raise RuntimeError(f'Image missing for {key}: {image_name}')
   shutil.copy2(src,image_root/image_name);files.append(f'wp-content/uploads/{UPLOAD_SUBDIR}/{image_name}')
 rollback=rollback_header+list(reversed(translation_rollbacks))+list(reversed(source_rollbacks))
 create_name=f'create-{name}.sql';rollback_name=f'rollback-{name}.sql'
 (work/'sql'/create_name).write_text('\n'.join(create)+'\n',encoding='utf-8');(work/'sql'/rollback_name).write_text('\n'.join(rollback)+'\n',encoding='utf-8')
 readme=f'این بسته شامل ۵۰ مقاله فارسی + ۱۵۰ ترجمه متصل (عربی، تاجیکی و انگلیسی) است.\n1) پوشه wp-content را در ریشه وردپرس آپلود کنید.\n2) پس از تهیه نسخه پشتیبان، sql/{create_name} را اجرا کنید.\n3) برای بازگشت، sql/{rollback_name} را اجرا کنید.\n'
 (work/'README-fa.txt').write_text(readme,encoding='utf-8');files += [f'sql/{create_name}',f'sql/{rollback_name}','README-fa.txt']
 manifest={'batch':name,'post_count':len(batch),'source_post_count':len(batch),'translation_post_count':len(batch)*len(LANGUAGES),'total_post_count':len(batch)*(1+len(LANGUAGES)),'languages':list(LANGUAGES),'upload_subdir':UPLOAD_SUBDIR,'posts':posts,'files':sorted(set(files))}
 (work/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 archive=PACKAGES/f'{name}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for file in sorted(work.rglob('*')):
   if file.is_file():z.write(file,file.relative_to(work))
 manifest.update(zip=archive.name,zip_sha256=sha256(archive),zip_bytes=archive.stat().st_size);return manifest

def main():
 qpath=OUT/'queue.json'
 if not qpath.exists():print('no queue.json; skipping article packages');return 0
 completed=[x for x in load(qpath,{}).get('items',[]) if x.get('status')=='completed'];PACKAGES.mkdir(parents=True,exist_ok=True)
 old=load(PACKAGES/'manifest.json',{'packages':[]});ordered=ordered_completed(completed,old);records=[]
 for batch_no,start in enumerate(range(0,len(ordered),BATCH_SIZE),1):
  batch=ordered[start:start+BATCH_SIZE]
  if len(batch)<BATCH_SIZE:break
  if not batch_ready(batch):
   print(f'Deferred unified package {batch_no}: translations are not complete yet')
   break
  name=f'batch-{batch_no:03d}-articles-{start+1:04d}-{start+len(batch):04d}';archive=PACKAGES/f'{name}.zip'
  record=healthy(archive,name,batch) if archive.exists() else None
  if record:print(f'Already packaged; preserved: {archive.name}')
  else:record=build(batch,name);print(f'Created or repaired: {archive.name}')
  records.append(record)
 (PACKAGES/'manifest.json').write_text(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(records),'packages':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(records)},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
