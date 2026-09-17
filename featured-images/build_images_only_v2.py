#!/usr/bin/env python3
import gzip,hashlib,json,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'featured-images'/'outputs'; ART=ROOT/'artifacts'; ART.mkdir(exist_ok=True)
def esc(v):return str(v).replace('\\','\\\\').replace("'","\\'").replace('\r','\\r').replace('\n','\\n')
def q(v):return "'"+esc(v)+"'"
def ps(s):return f's:{len(s.encode("utf-8"))}:"{s}";'
def pi(n):return f'i:{int(n)};'
def pa(items):return f'a:{len(items)}:{{'+''.join((pi(k) if isinstance(k,int) else ps(k))+v for k,v in items)+'}'
def main():
 records=sorted((json.loads(p.read_text(encoding='utf-8')) for p in OUT.glob('*/*.json')),key=lambda r:r['post_id'])
 if len(records)!=306 or len({r['post_id'] for r in records})!=306:raise SystemExit(f'Expected 306 records; found {len(records)}')
 for r in records:
  p=OUT/str(r['source_id'])/Path(r['upload_relative_path']).name
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:raise SystemExit(f'Invalid image {p}')
 now=datetime.now(timezone.utc).replace(microsecond=0); local=now+timedelta(hours=3,minutes=30); dt=local.strftime('%Y-%m-%d %H:%M:%S'); gmt=now.strftime('%Y-%m-%d %H:%M:%S')
 sql=['-- Navar featured-images-only v2: dynamic attachment IDs','SET NAMES utf8mb4;','START TRANSACTION;']
 for r in records:
  rel=r['upload_relative_path']; stem=Path(rel).stem[:190]; guid='https://navar-abyari.ir/wp-content/uploads/'+rel
  md=pa([('width',pi(1200)),('height',pi(675)),('file',ps(rel)),('sizes',pa([])),('image_meta',pa([]))])
  vals=[1,dt,gmt,'',r['title'],'','inherit','closed','closed','',stem,'','',dt,gmt,'',0,guid,0,'attachment','image/webp',0]
  sql += [f"SET @old_attachment_id := (SELECT `post_id` FROM `ha_postmeta` WHERE `meta_key`='_wp_attached_file' AND `meta_value`={q(rel)} ORDER BY `meta_id` LIMIT 1);",'DELETE FROM `ha_postmeta` WHERE `post_id`=@old_attachment_id;',"DELETE FROM `ha_posts` WHERE `ID`=@old_attachment_id AND `post_type`='attachment';",'INSERT INTO `ha_posts` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_password`,`post_name`,`to_ping`,`pinged`,`post_modified`,`post_modified_gmt`,`post_content_filtered`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) VALUES ('+', '.join(q(v) for v in vals)+');','SET @attachment_id := LAST_INSERT_ID();',f'INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES (@attachment_id,{q("_wp_attached_file")},{q(rel)}),(@attachment_id,{q("_wp_attachment_metadata")},{q(md)}),(@attachment_id,{q("_wp_attachment_image_alt")},{q(r["title"])});',f"DELETE FROM `ha_postmeta` WHERE `post_id`={r['post_id']} AND `meta_key`='_thumbnail_id';",f'INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES ({r["post_id"]},{q("_thumbnail_id")},@attachment_id);']
 sql += ['COMMIT;',"SELECT COUNT(*) AS translated_articles_with_featured_images FROM `ha_postmeta` WHERE `post_id` BETWEEN 502015 AND 502320 AND `meta_key`='_thumbnail_id';"]
 text='\n'.join(sql)+'\n'; sqlp=ART/'navar-featured-images-only-v2.sql'; sqlp.write_text(text,encoding='utf-8'); gzp=ART/'navar-featured-images-only-v2.sql.gz'
 with gzip.GzipFile(filename='',mode='wb',fileobj=open(gzp,'wb'),mtime=0) as g:g.write(text.encode())
 zipp=ART/'navar-featured-images-only-v2-package.zip';zipp.unlink(missing_ok=True)
 with zipfile.ZipFile(zipp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.write(sqlp,sqlp.name);z.write(gzp,gzp.name)
  for r in records:
   p=OUT/str(r['source_id'])/Path(r['upload_relative_path']).name;z.write(p,'wp-content/uploads/'+r['upload_relative_path'])
  z.writestr('README-fa.txt','نسخه v2 از شناسه خودکار دیتابیس برای attachmentها استفاده می‌کند و با شناسه پست‌های موجود تداخل ندارد. wp-content را ادغام و سپس SQL را Import کنید. خروجی نهایی باید 306 باشد.\n')
 report={'mode':'featured-images-only-v2-dynamic-ids','articles':306,'images':306,'attachment_ids':'dynamic via AUTO_INCREMENT','sql_bytes':sqlp.stat().st_size,'sql_sha256':hashlib.sha256(sqlp.read_bytes()).hexdigest(),'sql_gzip_sha256':hashlib.sha256(gzp.read_bytes()).hexdigest(),'package_bytes':zipp.stat().st_size,'package_sha256':hashlib.sha256(zipp.read_bytes()).hexdigest(),'generated_at_utc':now.isoformat()};(ART/'navar-featured-images-only-v2-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
