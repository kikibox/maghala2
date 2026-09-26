#!/usr/bin/env python3
"""Package immutable multilingual translations in 50-source-article batches."""
from __future__ import annotations
import hashlib,json,os,re,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'/'article-content-queue';QUEUE=OUT/'queue.json';TRANS=OUT/'translations';SQL=OUT/'translation-sql';ROLLBACK=OUT/'translation-rollback';PACKAGES=OUT/'translation-packages'
LANGUAGES=('ar-IQ','tg-TJ','en-US');BATCH_SIZE=max(1,int(os.getenv('TRANSLATION_PACKAGE_BATCH_SIZE','50')));DB_NAME=os.getenv('WORDPRESS_DB_NAME','navaraby_wp569').strip()
if not re.fullmatch(r'[A-Za-z0-9_]+',DB_NAME):raise RuntimeError('WORDPRESS_DB_NAME contains unsafe characters')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path,default):
 try:value=json.loads(path.read_text(encoding='utf-8'))
 except (OSError,json.JSONDecodeError):return default
 return value if isinstance(value,dict) else default
def healthy(path,name,ids):
 try:
  with zipfile.ZipFile(path) as z:
   if z.testzip() is not None:return None
   names=set(z.namelist());m=json.loads(z.read('manifest.json').decode('utf-8'));sql=z.read('sql/create-batch.sql').decode('utf-8')
   if m.get('batch_name')!=name or set(m.get('source_ids',[]))!=set(ids) or f'USE `{DB_NAME}`;' not in sql[:500]:return None
   if not {'sql/create-batch.sql','sql/rollback-batch.sql','README-fa.txt'}<=names:return None
   m.update(zip=path.name,bytes=path.stat().st_size,sha256=digest(path));return m
 except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,json.JSONDecodeError):return None
def build(rows,index,name):
 work=PACKAGES/name
 if work.exists():shutil.rmtree(work)
 (work/'sql').mkdir(parents=True);(work/'translations').mkdir();preamble=['SET NAMES utf8mb4;',f'USE `{DB_NAME}`;'];create=[f'-- Create multilingual translation batch {name}',*preamble];rollback=[f'-- Roll back multilingual translation batch {name}',*preamble];files=[];ids=[]
 for item in rows:
  key=str(item['id']);ids.append(key)
  for lang in LANGUAGES:
   html=TRANS/key/f'{lang}.html';meta=TRANS/key/f'{lang}.json';sql=SQL/f'{key}-{lang}.sql';back=ROLLBACK/f'{key}-{lang}.sql'
   required=(html,meta,sql,back)
   if not all(x.exists() for x in required):raise RuntimeError(f'Incomplete translation artifacts for {key}/{lang}')
   target=work/'translations'/key;target.mkdir(parents=True,exist_ok=True);shutil.copy2(html,target/html.name);shutil.copy2(meta,target/meta.name)
   files += [str((target/html.name).relative_to(work)),str((target/meta.name).relative_to(work))]
   create.append(f'\n-- translation: {key}/{lang}\n'+sql.read_text(encoding='utf-8'));rollback.insert(3,f'\n-- rollback translation: {key}/{lang}\n'+back.read_text(encoding='utf-8'))
 (work/'sql'/'create-batch.sql').write_text('\n'.join(create)+'\n',encoding='utf-8');(work/'sql'/'rollback-batch.sql').write_text('\n'.join(rollback)+'\n',encoding='utf-8')
 readme='1) از دیتابیس نسخه پشتیبان تهیه کنید.\n2) sql/create-batch.sql را یک‌بار اجرا کنید.\n3) برای حذف این ترجمه‌ها sql/rollback-batch.sql را اجرا کنید.\n'
 (work/'README-fa.txt').write_text(readme,encoding='utf-8');files+=['sql/create-batch.sql','sql/rollback-batch.sql','README-fa.txt']
 manifest={'batch':index,'batch_name':name,'source_article_count':len(rows),'translation_post_count':len(rows)*len(LANGUAGES),'languages':list(LANGUAGES),'source_ids':ids,'files':sorted(files)};(work/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 archive=PACKAGES/f'{name}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for file in sorted(work.rglob('*')):
   if file.is_file():z.write(file,file.relative_to(work))
 manifest.update(zip=archive.name,bytes=archive.stat().st_size,sha256=digest(archive));return manifest
def main():
 if not QUEUE.exists():return 0
 completed=[x for x in load(QUEUE,{}).get('items',[]) if x.get('status')=='completed'];completed.sort(key=lambda x:(x.get('completed_at',''),str(x.get('id',''))));PACKAGES.mkdir(parents=True,exist_ok=True);old=load(PACKAGES/'manifest.json',{'packages':[]});records=[]
 for index,start in enumerate(range(0,len(completed),BATCH_SIZE),1):
  rows=completed[start:start+BATCH_SIZE]
  if len(rows)<BATCH_SIZE:break
  ids=[str(x['id']) for x in rows]
  if any(not all((TRANS/key/f'{lang}.json').exists() for lang in LANGUAGES) for key in ids):continue
  name=f'translation-batch-{index:03d}-sources-{start+1:04d}-{start+len(rows):04d}';archive=PACKAGES/f'{name}.zip';record=healthy(archive,name,ids) if archive.exists() else None
  if record:print(f'Already packaged; preserved: {archive.name}')
  else:record=build(rows,index,name);print(f'Created or repaired: {archive.name}')
  records.append(record)
 manifest={'batch_size':BATCH_SIZE,'ready_batches':len(records),'packages':records};(PACKAGES/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
