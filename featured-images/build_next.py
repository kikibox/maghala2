#!/usr/bin/env python3
import io, json, re, time, hashlib
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFont
ROOT=Path(__file__).resolve().parents[1]; TRANS=ROOT/'translations'; OUT=ROOT/'featured-images'/'outputs'; STATE=ROOT/'state'/'featured-images-progress.json'; STATUS=ROOT/'docs'/'featured-images-status.md'; BASE='https://navar-abyari.ir/wp-json/wp/v2'
LANGS=('ar-IQ','tg-TJ'); COLORS={'ar-IQ':(191,113,32),'tg-TJ':(0,132,145)}; LABELS={'ar-IQ':'AR  |  IRAQ','tg-TJ':'TJ  |  TAJIKISTAN'}
def fetch(url,binary=False):
 last=None
 for attempt in range(5):
  try:
   with urlopen(Request(url,headers={'User-Agent':'NavarFeaturedImageBuilder/1.0','Accept':'*/*'}),timeout=60) as r:data=r.read()
   return data if binary else json.loads(data.decode())
  except Exception as e:last=e; time.sleep(2**attempt)
 raise RuntimeError(f'Failed after retries: {url}: {last}')
def sources():return [739]+sorted(int(p.name) for p in TRANS.iterdir() if p.is_dir())
def post_id_for(s,l):return 502015+sources().index(s)*2+(1 if l=='tg-TJ' else 0)
def info_for(s,l):
 p=TRANS/str(s)/f'{l}.json'
 if p.exists():return json.loads(p.read_text(encoding='utf-8'))
 if s==739:return {'source_id':739,'language':l,'source_title':'انواع سیستم های آبیاری','title':'أنواع أنظمة الري' if l=='ar-IQ' else 'Навъҳои системаҳои обёрӣ','slug':'anwa-anthimat-al-ray' if l=='ar-IQ' else 'navhoi-sistemahoi-obyor'}
 raise FileNotFoundError(p)
def source_image(s,title):
 post=fetch(f'{BASE}/posts/{s}?_fields=featured_media,content,title'); url=''; media_id=int(post.get('featured_media') or 0)
 if media_id:url=(fetch(f'{BASE}/media/{media_id}?_fields=source_url').get('source_url') or '')
 if not url:
  m=re.search(r'<img[^>]+src=["\']([^"\']+)',((post.get('content') or {}).get('rendered') or ''),re.I)
  if m:url=m.group(1).replace('&#038;','&')
 if url:
  try:return Image.open(io.BytesIO(fetch(url,True))).convert('RGB'),url,media_id
  except Exception:pass
 im=Image.new('RGB',(1200,675),(28,74,48)); d=ImageDraw.Draw(im)
 for y in range(675):
  t=y/674; d.line((0,y,1200,y),fill=(int(34+120*t),int(88+78*t),int(60+15*t)))
 for x in range(-200,1400,85):d.line((600,330,x,675),fill=(208,183,87),width=5)
 for x in range(80,1180,90):d.ellipse((x,235+(x%3)*20,x+16,520),fill=(183,157,65))
 return im,'procedural:'+title,0
def font(size,bold=False):
 for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
  if Path(p).exists():return ImageFont.truetype(p,size)
 return ImageFont.load_default()
def build_variant(base,lang,s,target,slug):
 im=ImageOps.fit(base,(1200,675),method=Image.Resampling.LANCZOS).convert('RGB'); im=ImageEnhance.Contrast(im).enhance(1.07)
 ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov); c=COLORS[lang]
 for y in range(360,675):d.line((0,y,1200,y),fill=(5,17,22,int(15+150*((y-360)/315))))
 d.rectangle((0,0,16,675),fill=(*c,255)); d.rounded_rectangle((45,45,270,105),radius=20,fill=(5,20,25,210),outline=(*c,255),width=3); d.text((70,61),LABELS[lang],font=font(24,True),fill='white'); d.rounded_rectangle((45,570,355,630),radius=18,fill=(*c,225)); d.text((70,586),'AFP  •  NAVAR ABYARI',font=font(22,True),fill='white')
 im=Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB'); out=OUT/str(s); out.mkdir(parents=True,exist_ok=True); safe=re.sub(r'[^a-z0-9-]+','-',slug.lower()).strip('-')[:120]; path=out/f'{target}-{safe}-{lang.lower().replace("-","")}.webp'; im.save(path,'WEBP',quality=84,method=6); return path
def write_status(st):
 pct=st['completed_images']*100/st['total_images']; filled=round(pct/5); bar='█'*filled+'░'*(20-filled); next_id=st.get('next_source_id') or 'تمام‌شده'; last=st.get('last_completed_source_id') or '—'
 text=f'''# وضعیت زنده ساخت تصاویر شاخص

> این صفحه پس از پایان هر مقاله به‌صورت خودکار به‌روزرسانی می‌شود.

## {pct:.2f}% — `{bar}`

| شاخص | مقدار |
|---|---:|
| کل مقاله‌های منبع | {st['total_sources']} |
| منابع تکمیل‌شده | {st['completed_sources']} |
| کل تصاویر | {st['total_images']} |
| تصاویر ساخته‌شده | {st['completed_images']} |
| تصاویر باقی‌مانده | {st['total_images']-st['completed_images']} |
| آخرین source ID | {last} |
| source ID بعدی | {next_id} |

- [مشاهده اجرای GitHub Actions](https://github.com/pedisaimon-source/navar-abyari/actions/workflows/featured-images.yml)
- [مشاهده تصاویر ساخته‌شده](https://github.com/pedisaimon-source/navar-abyari/tree/main/featured-images/outputs)
'''
 STATUS.parent.mkdir(exist_ok=True); STATUS.write_text(text,encoding='utf-8')
def main():
 srcs=sources(); state=json.loads(STATE.read_text()) if STATE.exists() else {}; done=set(map(int,state.get('completed_source_ids',[]))); pending=[x for x in srcs if x not in done]
 if not pending:
  if state:write_status(state)
  print(json.dumps({'status':'complete','total_images':306}));return
 s=pending[0]; probe=info_for(s,'ar-IQ'); base,url,mid=source_image(s,probe.get('source_title','')); created=[]
 for lang in LANGS:
  info=info_for(s,lang); target=post_id_for(s,lang); path=build_variant(base,lang,s,target,info['slug']); rec={'source_id':s,'post_id':target,'language':lang,'title':info['title'],'slug':info['slug'],'source_image_url':url,'source_media_id':mid,'upload_relative_path':f'2026/09/navar-featured/{path.name}','bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':1200,'height':675,'mime_type':'image/webp'}; path.with_suffix('.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8'); created.append(rec)
 done.add(s); remaining=[x for x in srcs if x not in done]; state={'total_sources':len(srcs),'total_images':306,'completed_sources':len(done),'completed_images':len(done)*2,'remaining_sources':len(remaining),'completed_source_ids':sorted(done),'next_source_id':remaining[0] if remaining else None,'last_completed_source_id':s}; STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8'); write_status(state); print(json.dumps({'status':'created','source_id':s,'created':created,'progress':state},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
