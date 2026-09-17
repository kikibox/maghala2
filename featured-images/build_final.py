#!/usr/bin/env python3
import base64,gzip,hashlib,json,zipfile
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'featured-images'/'outputs'; ART=ROOT/'artifacts'; ART.mkdir(exist_ok=True); STATE=ROOT/'state'/'featured-images-progress.json'; ATTACHMENT_ID_START=502321
def esc(v):return str(v).replace('\\','\\\\').replace("'","\\'").replace('\r','\\r').replace('\n','\\n')
def q(v):return "'"+esc(v)+"'"
def ps(s):return f's:{len(s.encode("utf-8"))}:"{s}";'
def pi(n):return f'i:{int(n)};'
def pa(items):return f'a:{len(items)}:{{'+''.join((pi(k) if isinstance(k,int) else ps(k))+v for k,v in items)+'}'
def main():
 state=json.loads(STATE.read_text())
 if state.get('remaining_sources')!=0 or state.get('completed_images')!=306:raise SystemExit(f'Queue incomplete: {state}')
 records=sorted((json.loads(p.read_text(encoding='utf-8')) for p in OUT.glob('*/*.json')),key=lambda x:x['post_id'])
 if len(records)!=306 or len({r['post_id'] for r in records})!=306:raise SystemExit(f'Expected 306 records, got {len(records)}')
 for r in records:
  p=OUT/str(r['source_id'])/Path(r['upload_relative_path']).name
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:raise SystemExit(f'Invalid image {p}')
 now=datetime.now(timezone.utc).replace(microsecond=0); local=now+timedelta(hours=3,minutes=30); dt=local.strftime('%Y-%m-%d %H:%M:%S'); gmt=now.strftime('%Y-%m-%d %H:%M:%S'); posts=[]; metas=[]; thumbs=[]
 for i,r in enumerate(records):
  aid=ATTACHMENT_ID_START+i; rel=r['upload_relative_path']; name=Path(rel).name; stem=Path(name).stem[:190]; guid='https://navar-abyari.ir/wp-content/uploads/'+rel; vals=[aid,1,dt,gmt,'',r['title'],'','inherit','closed','closed','',stem,'','',dt,gmt,'',0,guid,0,'attachment','image/webp',0]; posts.append('('+', '.join(q(v) for v in vals)+')'); md=pa([('width',pi(1200)),('height',pi(675)),('file',ps(rel)),('sizes',pa([])),('image_meta',pa([]))]); metas += [f'({aid},{q("_wp_attached_file")},{q(rel)})',f'({aid},{q("_wp_attachment_metadata")},{q(md)})',f'({aid},{q("_wp_attachment_image_alt")},{q(r["title"])})']; thumbs.append(f'({r["post_id"]},{q("_thumbnail_id")},{q(aid)})')
 s='\n-- Unique featured images for all 306 translated articles\nSET NAMES utf8mb4;\nSTART TRANSACTION;\n\n'; s+='INSERT INTO `ha_posts` (`ID`,`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_password`,`post_name`,`to_ping`,`pinged`,`post_modified`,`post_modified_gmt`,`post_content_filtered`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) VALUES\n'+',\n'.join(posts)+';\n\n'; s+='INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES\n'+',\n'.join(metas)+';\n\n'; s+="DELETE FROM `ha_postmeta` WHERE `post_id` BETWEEN 502015 AND 502320 AND `meta_key`='_thumbnail_id';\n"; s+='INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES\n'+',\n'.join(thumbs)+';\nCOMMIT;\n'; s+="SELECT COUNT(*) AS translated_articles_with_featured_images FROM `ha_postmeta` WHERE `post_id` BETWEEN 502015 AND 502320 AND `meta_key`='_thumbnail_id';\n"
 automated=gzip.open(ART/'generated-translations.sql.gz','rt',encoding='utf-8').read(); manual=gzip.decompress(base64.b64decode((ROOT/'sqlbuild'/'manual-739.sql.gz.b64').read_text().strip())).decode(); final='-- Navar multilingual translations with unique featured images\n'+manual+'\n'+automated+'\n'+s; sql=ART/'navar-multilingual-with-featured-images.sql'; sql.write_text(final,encoding='utf-8')
 with gzip.GzipFile(filename='',mode='wb',fileobj=open(ART/'navar-multilingual-with-featured-images.sql.gz','wb'),mtime=0) as gz:gz.write(final.encode())
 package=ART/'navar-multilingual-featured-package.zip'; package.unlink(missing_ok=True)
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.write(sql,sql.name);z.write(ART/'navar-multilingual-with-featured-images.sql.gz','navar-multilingual-with-featured-images.sql.gz')
  for r in records:
   p=OUT/str(r['source_id'])/Path(r['upload_relative_path']).name;z.write(p,'wp-content/uploads/'+r['upload_relative_path'])
  z.writestr('README-fa.txt','پوشه wp-content را در ریشه وردپرس ادغام کنید؛ سپس فایل SQL را Import کنید. قبل از اجرا پشتیبان بگیرید. خروجی بررسی انتهای SQL باید 306 باشد.\n')
 report={'translated_articles':306,'unique_featured_images':306,'attachment_id_start':ATTACHMENT_ID_START,'attachment_id_end':ATTACHMENT_ID_START+305,'sql_bytes':sql.stat().st_size,'sql_sha256':hashlib.sha256(sql.read_bytes()).hexdigest(),'sql_gzip_sha256':hashlib.sha256((ART/'navar-multilingual-with-featured-images.sql.gz').read_bytes()).hexdigest(),'package_bytes':package.stat().st_size,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'generated_at_utc':now.isoformat()};(ART/'navar-multilingual-featured-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
