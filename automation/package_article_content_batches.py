#!/usr/bin/env python3
"""Build immutable, upload-ready 50-article ZIP packages."""
from __future__ import annotations
import hashlib,json,os,re,shutil,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'article-content-queue';PACKAGES=OUT/'packages'
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
   sql=z.read('sql/create-batch.sql').decode('utf-8')
   actual={str(x.get('id') or '') for x in manifest.get('posts',[])}
   if manifest.get('batch')!=name or actual!=expected or int(manifest.get('post_count',0))!=len(batch):return None
   if 'sql/rollback-batch.sql' not in names or f'USE `{DB_NAME}`;' not in sql[:500]:return None
   if len([x for x in names if x.startswith('items/') and x.endswith('.json')])<len(batch):return None
   if not any(x.startswith('wp-content/uploads/') for x in names):return None
   manifest.update(zip=path.name,zip_sha256=sha256(path),zip_bytes=path.stat().st_size)
   return manifest
 except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,json.JSONDecodeError):return None

def build(batch,name):
 work=PACKAGES/name
 if work.exists():shutil.rmtree(work)
 (work/'sql').mkdir(parents=True);(work/'items').mkdir();image_root=work/'wp-content'/'uploads'/UPLOAD_SUBDIR;image_root.mkdir(parents=True)
 preamble=['SET NAMES utf8mb4;',f'USE `{DB_NAME}`;']
 create=[f'-- Create {len(batch)} generated articles ({name})',*preamble]
 rollback=[f'-- Roll back {len(batch)} generated articles ({name})',*preamble]
 posts=[];files=[]
 for item in batch:
  key=item_id(item);posts.append({'id':key,'title':item.get('title'),'slug':item.get('slug'),'vertical':item.get('vertical'),'completed_at':item.get('completed_at'),'word_count':item.get('word_count')})
  cf=OUT/'sql'/f'{key}.sql';rf=OUT/'rollback'/f'{key}.sql';jf=OUT/'items'/f'{key}.json'
  if not cf.exists() or not rf.exists() or not jf.exists():raise RuntimeError(f'Incomplete artifacts for completed article {key}')
  create.append(f'\n-- article: {key}\n'+cf.read_text(encoding='utf-8'));rollback.append(f'\n-- article: {key}\n'+rf.read_text(encoding='utf-8'))
  shutil.copy2(jf,work/'items'/jf.name);files.append(f'items/{jf.name}')
  data=load(jf,{})
  for image in data.get('images',[]):
   image_name=Path(image['name'] if isinstance(image,dict) else image).name;src=OUT/'images'/image_name
   if not src.exists():raise RuntimeError(f'Image missing for {key}: {image_name}')
   shutil.copy2(src,image_root/image_name);files.append(f'wp-content/uploads/{UPLOAD_SUBDIR}/{image_name}')
 (work/'sql'/'create-batch.sql').write_text('\n'.join(create)+'\n',encoding='utf-8');(work/'sql'/'rollback-batch.sql').write_text('\n'.join(rollback)+'\n',encoding='utf-8')
 readme='1) پوشه wp-content را در ریشه وردپرس آپلود کنید.\n2) پس از تهیه نسخه پشتیبان، sql/create-batch.sql را اجرا کنید.\n3) برای بازگشت، sql/rollback-batch.sql را اجرا کنید.\n'
 (work/'README-fa.txt').write_text(readme,encoding='utf-8');files+=['sql/create-batch.sql','sql/rollback-batch.sql','README-fa.txt']
 manifest={'batch':name,'post_count':len(batch),'upload_subdir':UPLOAD_SUBDIR,'posts':posts,'files':sorted(set(files))}
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
  name=f'batch-{batch_no:03d}-articles-{start+1:04d}-{start+len(batch):04d}';archive=PACKAGES/f'{name}.zip'
  record=healthy(archive,name,batch) if archive.exists() else None
  if record:print(f'Already packaged; preserved: {archive.name}')
  else:record=build(batch,name);print(f'Created or repaired: {archive.name}')
  records.append(record)
 (PACKAGES/'manifest.json').write_text(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(records),'packages':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(records)},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
