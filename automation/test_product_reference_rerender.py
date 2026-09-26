#!/usr/bin/env python3
"""Benchmark gradual product scale changes without changing the 3D reference method."""
from __future__ import annotations
import base64,hashlib,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];ASSETS=Path(__file__).with_name('assets');OUT=ROOT/'artifacts'/'product-rerender-test'
API=os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations';KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip();MODEL=os.getenv('IMAGE_MODEL') or os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');PHONE='AFP | 09134922013'
VARIANTS=[
 ('05-pair-far-corrected','Use the selected 05-pair-far scale: the complete two-object group occupies approximately 12 to 15 percent of frame width, low on the soil and about four metres from the camera.'),
]
def refs():return ['data:image/webp;base64,'+(ASSETS/'afp-layflat.webp.b64').read_text().strip(),'data:image/jpeg;base64,'+(ASSETS/'afp-layflat-bare.jpg.b64').read_text().strip()]
def prompt(scale):return '''Create one photorealistic 16:9 agricultural editorial photograph whose background is a technical farm water-transfer scene with a pump, manifold, connected layflat line and cultivated field; the article-related water-transfer activity and equipment are the main subject. For this test, include no people at all. Reconstruct exactly two separate attached-reference objects as true three-dimensional secondary objects integrated into soil, lighting and perspective. Object one: the packaged AFP layflat coil with the same low wide proportions, folded printed cardboard pieces, crossing straps, center opening, AFP and layflat markings. Object two: the unboxed black woven layflat hose coil exactly like its reference: a low flat horizontal coil made of many tight concentric layers, short hollow brown cardboard center, visible diagonal woven fabric texture, realistic compressed thickness, and one short loose hose end. The bare coil has no carton, no logo and no writing. Never turn the bare coil into smooth round tubing, a tall cable spool, an upright wheel, a solid tire or a plastic pipe coil. Both objects rest flat, horizontal and parallel to the soil. Do not paste flat cutouts; match contact shadows, reflected soil light, perspective, depth of field and slight soil interaction. '''+scale+''' Keep the pair off-center on the lower third. Do not add any third package, roll, jar, container, advertisement or invented product. The background must remain more important than the products.'''

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
 contact_sheet(images);(OUT/'layflat-05-corrected-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print(json.dumps(records,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
