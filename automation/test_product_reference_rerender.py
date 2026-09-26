#!/usr/bin/env python3
"""Benchmark gradual product scale changes without changing the 3D reference method."""
from __future__ import annotations
import base64,hashlib,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];ASSETS=Path(__file__).with_name('assets');OUT=ROOT/'artifacts'/'product-rerender-test'
API=os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations';KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip();MODEL=os.getenv('IMAGE_MODEL') or os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');PHONE='AFP | 09134922013'
VARIANTS=[
 ('03-compact','Use the selected compact scale: the complete pair together occupies approximately 20 to 23 percent of frame width. Both coils stay clearly below knee height and sit about two metres from the camera.'),
]
def refs():return ['data:image/webp;base64,'+(ASSETS/'afp-layflat.webp.b64').read_text().strip(),'data:image/jpeg;base64,'+(ASSETS/'afp-layflat-bare.jpg.b64').read_text().strip()]
def prompt(scale):return '''Create one photorealistic 16:9 agricultural editorial photograph in a real Iranian field beside a practical water-transfer line. Keep the field activity and irrigation context dominant, with one adult worker nearby for human scale. Reconstruct exactly two attached-reference objects as true three-dimensional objects integrated into soil, lighting and perspective: first the packaged AFP layflat coil with its folded printed cardboard and crossing straps; second the bare black woven layflat coil with concentric layers and loose hose end. Keep both rolls separate, flat, horizontal and parallel to the soil; never stand either upright like a wheel. Preserve AFP and layflat markings on the packaged object and add no writing to the bare roll. Do not paste flat cutouts. Use natural three-quarter views, contact shadows, reflected soil light and slight soil interaction. '''+scale+''' Keep the pair off-center on the lower third. Do not add any third package, roll, jar, container, advertisement or invented product. No person touches, leans on or carries either coil.'''

def watermark(im):
 c=im.convert('RGBA');o=Image.new('RGBA',c.size,(0,0,0,0));d=ImageDraw.Draw(o)
 try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',27)
 except OSError:f=ImageFont.load_default()
 b=d.textbbox((0,0),PHONE,font=f);w,h=b[2]-b[0],b[3]-b[1];m,px,py=18,16,10;x=c.width-w-m-2*px;y=c.height-h-m-2*py;d.rounded_rectangle((x,y,c.width-m,c.height-m),radius=8,fill=(0,0,0,178));d.text((x+px,y+py-b[1]),PHONE,font=f,fill='white');return Image.alpha_composite(c,o).convert('RGB')
def call(name,scale):
 payload={'model':MODEL,'prompt':prompt(scale),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':refs()}}
 last=None
 for attempt in range(1,4):
  try:
   req=urllib.request.Request(API,data=json.dumps(payload).encode(),method='POST',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-scale-benchmark/1.0'})
   with urllib.request.urlopen(req,timeout=600) as r:data=json.loads(r.read())
   row=(data.get('data') or [{}])[0]
   if row.get('b64_json'):blob=base64.b64decode(row['b64_json'])
   elif row.get('url'):
    with urllib.request.urlopen(row['url'],timeout=300) as r:blob=r.read()
   else:raise RuntimeError('image response missing')
   im=Image.open(io.BytesIO(blob)).convert('RGB');w,h=im.size;target=16/9
   if w/h>target:nw=int(h*target);x=(w-nw)//2;im=im.crop((x,0,x+nw,h))
   else:nh=int(w/target);y=(h-nh)//2;im=im.crop((0,y,w,y+nh))
   im=watermark(im.resize((1200,675),Image.Resampling.LANCZOS));buf=io.BytesIO();im.save(buf,'WEBP',quality=72,method=6);raw=buf.getvalue();path=OUT/f'layflat-scale-{name}.webp';path.write_bytes(raw);return im,{'variant':name,'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'scale_instruction':scale}
  except Exception as exc:
   last=exc
   if attempt<3:time.sleep(30*attempt)
 raise RuntimeError(f'{name} failed: {last}')
def contact_sheet(rows):
 return None
def main():
 if not KEY:raise RuntimeError('IMAGE_API_KEY/AGNES_API_KEY is missing')
 OUT.mkdir(parents=True,exist_ok=True);records=[];images=[]
 for name,scale in VARIANTS:
  im,row=call(name,scale);images.append((name,im));records.append(row)
 contact_sheet(images);(OUT/'layflat-compact-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print(json.dumps(records,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
