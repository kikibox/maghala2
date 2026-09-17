#!/usr/bin/env python3
import gzip,hashlib,json,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'featured-images'/'outputs'; ART=ROOT/'artifacts'; ART.mkdir(exist_ok=True); A0=502321
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
 now=datetime.now(timezone.utc).replace(microsecond=0); local=now+timedelta(hours=3,minutes=30); dt=local.strftime('%Y-%m-%d %H:%M:%S'); gmt=now.strftime('%Y-%m-%d %H:%M:%S'); posts=[]; metas=[]; thumbs=[]
 for i,r in enumerate(records):
  aid=A0+i; rel=r['upload_relative_path']; stem=Path(rel).stem[:190]; guid='https://navar-abyari.ir/wp-content/uploads/'+rel
  vals=[aid,1,dt,gmt,'',r['title'],'','inherit','closed','closed','',stem,'','',dt,gmt,'',0,guid,0,'attachment','image/webp',0]
  posts.append('('+', '.join(q(v) for v in vals)+')')
  md=pa([('width',pi(1200)),('height',pi(675)),('file',ps(rel)),('sizes',pa([])),('image_meta',pa([]))])
  metas += [f'({aid},{q("_wp_attached_file")},{q(rel)})',f'({aid},{q("_wp_attachment_metadata")},{q(md)})',f'({aid},{q("_wp_attachment_image_alt")},{q(r["title"])})']
  thumbs.append(f'({r["post_id"]},{q("_thumbnail_id")},{q(aid)})')
 sql='''-- Navar featured-images-only patch (safe after translations already exist)
SET NAMES utf8mb4;
START TRANSACTION;
DELETE FROM `ha_postmeta` WHERE `post_id` BETWEEN 502321 AND 502626;
DELETE FROM `ha_posts` WHERE `ID` BETWEEN 502321 AND 502626 AND `post_type`='attachment';
DELETE FROM `ha_postmeta` WHERE `post_id` BETWEEN 502015 AND 502320 AND `meta_key`='_thumbnail_id';

'''
 sql+='INSERT INTO `ha_posts` (`ID`,`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_password`,`post_name`,`to_ping`,`pinged`,`post_modified`,`post_modified_gmt`,`post_content_filtered`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) VALUES\n'+',\n'.join(posts)+';\n\n'
 sql+='INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES\n'+',\n'.join(metas)+';\n\n'
 sql+='INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES\n'+',\n'.join(thumbs)+';\nCOMMIT;\n\n'
 sql+="SELECT COUNT(*) AS translated_articles_with_featured_images FROM `ha_postmeta` WHERE `post_id` BETWEEN 502015 AND 502320 AND `meta_key`='_thumbnail_id';\n"
 sqlp=ART/'navar-featured-images-only.sql'; sqlp.write_text(sql,encoding='utf-8'); gzp=ART/'navar-featured-images-only.sql.gz'
 with gzip.GzipFile(filename='',mode='wb',fileobj=open(gzp,'wb'),mtime=0) as g:g.write(sql.encode())
 zipp=ART/'navar-featured-images-only-package.zip';zipp.unlink(missing_ok=True)
 with zipfile.ZipFile(zipp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.write(sqlp,sqlp.name);z.write(gzp,gzp.name)
  for r in records:
   p=OUT/str(r['source_id'])/Path(r['upload_relative_path']).name;z.write(p,'wp-content/uploads/'+r['upload_relative_path'])
  z.writestr('README-fa.txt','این بسته فقط تصاویر شاخص را به ۳۰۶ ترجمه موجود اضافه می‌کند و ترجمه‌ها را دوباره درج نمی‌کند. ابتدا wp-content را ادغام و سپس SQL را Import کنید. خروجی بررسی باید 306 باشد.\n')
 report={'mode':'featured-images-only-idempotent','articles':306,'images':306,'attachment_id_start':A0,'attachment_id_end':A0+305,'sql_bytes':sqlp.stat().st_size,'sql_sha256':hashlib.sha256(sqlp.read_bytes()).hexdigest(),'sql_gzip_sha256':hashlib.sha256(gzp.read_bytes()).hexdigest(),'package_bytes':zipp.stat().st_size,'package_sha256':hashlib.sha256(zipp.read_bytes()).hexdigest(),'generated_at_utc':now.isoformat()};(ART/'navar-featured-images-only-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
