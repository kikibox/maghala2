#!/usr/bin/env python3
"""Generate product-free farm scenes, then integrate exact AFP objects at fixed scale."""
from __future__ import annotations
import base64,hashlib,io,json,os,time,urllib.error,urllib.request
from collections import deque
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageFont
ROOT=Path(__file__).resolve().parents[1]
ASSETS=Path(__file__).with_name('assets')
OUT=ROOT/'artifacts'/'product-rerender-test'
API=os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations'
KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip()
MODEL=os.getenv('IMAGE_MODEL') or os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash')
PHONE_LABEL='AFP | 09134922013'
CASES={
 'tape':{'assets':['afp-tape.webp.b64'],'widths':[126],'positions':[(105,492)]},
 'layflat-pair':{'assets':['afp-layflat.webp.b64','afp-layflat-bare.jpg.b64'],'widths':[102,94],'positions':[(92,500),(208,507)]},
}
def data_image(filename):
 raw=base64.b64decode((ASSETS/filename).read_text(encoding='ascii').strip())
 return Image.open(io.BytesIO(raw)).convert('RGB')
def neutral_reference():
 im=Image.new('RGB',(1024,576),(215,220,210));d=ImageDraw.Draw(im);d.rectangle((0,0,1024,330),fill=(204,220,230));d.rectangle((0,330,1024,576),fill=(145,126,92));b=io.BytesIO();im.save(b,'JPEG',quality=88);return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
def background_prompt(name):
 subject='a drip-irrigated crop field' if name=='tape' else 'a farm water-transfer installation area'
 return f'''Create a photorealistic wide 16:9 Iranian agricultural editorial background showing {subject}. The field work, crop rows, irrigation context and landscape are the only subjects. Reserve an empty level patch of bare soil in the lower-left middle distance, about 15 percent of frame width, for later placement of a small product prop. No product, package, carton, roll, coil, hose bundle, logo, writing or advertisement anywhere. No person may stand in or touch the reserved soil patch. Natural daylight, realistic perspective, detailed soil, wide environmental composition.'''
def generate_background(name):
 payload={'model':MODEL,'prompt':background_prompt(name),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':[neutral_reference()]}}
 last=None
 for attempt in range(1,4):
  req=urllib.request.Request(API,data=json.dumps(payload).encode(),method='POST',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-controlled-composite-test/1.0'})
  try:
   with urllib.request.urlopen(req,timeout=600) as r:data=json.loads(r.read())
   row=(data.get('data') or [{}])[0]
   if row.get('b64_json'):blob=base64.b64decode(row['b64_json'])
   elif row.get('url'):
    with urllib.request.urlopen(row['url'],timeout=300) as r:blob=r.read()
   else:raise RuntimeError('image response missing')
   im=Image.open(io.BytesIO(blob)).convert('RGB');w,h=im.size;target=16/9
   if w/h>target:nw=int(h*target);left=(w-nw)//2;im=im.crop((left,0,left+nw,h))
   else:nh=int(w/target);top=(h-nh)//2;im=im.crop((0,top,w,top+nh))
   return im.resize((1200,675),Image.Resampling.LANCZOS)
  except Exception as exc:
   last=exc
   if attempt<3:time.sleep(15*attempt)
 raise RuntimeError(f'background failed: {last}')
def cutout_white(im):
 im=im.convert('RGBA');w,h=im.size;pix=im.load();seen=bytearray(w*h);q=deque()
 def bg(x,y):
  r,g,b,_=pix[x,y];return min(r,g,b)>=214 and max(r,g,b)-min(r,g,b)<=42
 for x in range(w):
  for y in (0,h-1):
   i=y*w+x
   if not seen[i] and bg(x,y):seen[i]=1;q.append((x,y))
 for y in range(h):
  for x in (0,w-1):
   i=y*w+x
   if not seen[i] and bg(x,y):seen[i]=1;q.append((x,y))
 while q:
  x,y=q.popleft()
  for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
   if 0<=nx<w and 0<=ny<h:
    i=ny*w+nx
    if not seen[i] and bg(nx,ny):seen[i]=1;q.append((nx,ny))
 alpha=Image.new('L',(w,h),255);a=alpha.load()
 for y in range(h):
  for x in range(w):
   if seen[y*w+x]:a[x,y]=0
 alpha=alpha.filter(ImageFilter.GaussianBlur(0.7));im.putalpha(alpha)
 box=im.getbbox();return im.crop(box) if box else im
def add_object(scene,obj,width,pos):
 ratio=width/obj.width;obj=obj.resize((width,max(1,int(obj.height*ratio))),Image.Resampling.LANCZOS)
 # A small soft contact shadow and warm soil color cast integrate the object.
 shadow=Image.new('RGBA',scene.size,(0,0,0,0));d=ImageDraw.Draw(shadow);x,y=pos;d.ellipse((x-5,y+obj.height-10,x+obj.width+7,y+obj.height+7),fill=(30,20,10,95));shadow=shadow.filter(ImageFilter.GaussianBlur(7));scene=Image.alpha_composite(scene.convert('RGBA'),shadow)
 tint=Image.new('RGBA',obj.size,(125,92,58,18));obj=Image.alpha_composite(obj,tint)
 scene.alpha_composite(obj,pos)
 # Irregular soil crumbs over the bottom edge prevent a pasted-on boundary.
 occ=Image.new('RGBA',scene.size,(0,0,0,0));od=ImageDraw.Draw(occ)
 for i in range(0,obj.width,9):
  yy=y+obj.height-2-(i%4);od.ellipse((x+i,yy,x+i+7,yy+4),fill=(92,70,45,105))
 return Image.alpha_composite(scene,occ)
def watermark(image):
 c=image.convert('RGBA');o=Image.new('RGBA',c.size,(0,0,0,0));d=ImageDraw.Draw(o)
 try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',27)
 except OSError:f=ImageFont.load_default()
 b=d.textbbox((0,0),PHONE_LABEL,font=f);w,h=b[2]-b[0],b[3]-b[1];m,px,py=18,16,10;x=c.width-w-m-2*px;y=c.height-h-m-2*py;d.rounded_rectangle((x,y,c.width-m,c.height-m),radius=8,fill=(0,0,0,178));d.text((x+px,y+py-b[1]),PHONE_LABEL,font=f,fill='white');return Image.alpha_composite(c,o).convert('RGB')
def build(name,case):
 scene=generate_background(name).convert('RGBA')
 for filename,width,pos in zip(case['assets'],case['widths'],case['positions']):scene=add_object(scene,cutout_white(data_image(filename)),width,pos)
 out=watermark(scene);buf=io.BytesIO();out.save(buf,'WEBP',quality=72,method=6);blob=buf.getvalue();path=OUT/f'{name}-controlled-composite.webp';path.write_bytes(blob);return {'case':name,'file':path.name,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'method':'product-free-scene plus scale-locked perspective-aware composite','max_product_width_px':max(case['widths'])}
def main():
 if not KEY:raise RuntimeError('IMAGE_API_KEY/AGNES_API_KEY is missing')
 OUT.mkdir(parents=True,exist_ok=True);rows=[build(n,c) for n,c in CASES.items()];(OUT/'controlled-composite-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
