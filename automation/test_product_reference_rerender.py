#!/usr/bin/env python3
"""Generate no-human/no-container drip-tape review samples before production rollout."""
from __future__ import annotations
import base64,hashlib,io,json,os,time,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];ASSETS=Path(__file__).with_name('assets');OUT=ROOT/'artifacts'/'product-rerender-test'
API=os.getenv('IMAGE_ENDPOINT') or os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')+'/images/generations';KEY=(os.getenv('IMAGE_API_KEY') or os.getenv('AGNES_API_KEY','')).strip();MODEL=os.getenv('IMAGE_MODEL') or os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash');PHONE='AFP | 09134922013'
SCENES=[
 ('01-crop-disease','آفات و بیماری های باقلا با آبیاری قطره ای','The article explains how field symptoms, moisture management and drip irrigation practices affect disease pressure in fava bean crops; show visible crop-row evidence without chemical props.'),
 ('02-tape-spacing','فاصله نوار تیپ در کشت رزماری','The article compares recommended drip-tape spacing for rosemary according to row geometry, soil texture and irrigation uniformity; emphasize parallel beds and spacing.'),
 ('03-yield-context','میزان برداشت اسفناج در هکتار با نوار تیپ','The article explains how uniform water distribution, crop density and field management influence spinach yield per hectare; show a healthy uniform spinach field.'),
]
def refs():return ['data:image/webp;base64,'+(ASSETS/'afp-tape.webp.b64').read_text().strip()]
def prompt(title,summary):return f'''Create one photorealistic 16:9 agricultural editorial photograph. Article title: {title}. Article summary for visual grounding: {summary} The background, crop condition, irrigation layout and equipment must be specifically derived from this summary and remain the main subject. ABSOLUTELY NO PEOPLE: no farmer, worker, face, hand, arm, leg, body part, human silhouette or distant human figure. Show exactly one commercial product object in the entire image: reconstruct the attached AFP 1000-meter drip-tape roll as a true three-dimensional wide cylindrical object in its white-and-blue carton sleeve, with the same diameter-to-height ratio, central top hole, straight carton walls, blue lower band, printed-panel layout, colors and readable AFP and Drip Irrigation Tape marks. No bottle, jar, canister, bucket, fertilizer container, pesticide container, second package, second roll, advertisement or invented companion product anywhere. Use a deliberately small distant scale: the complete roll occupies only 10 to 12 percent of frame width, remains low and clearly below knee height in real-world scale, sits about five metres from the camera, and stays near the far lower-left or lower-right third. Preserve abundant field context around it; never center it and never use foreground perspective enlargement. The topic-specific field is the hero and the roll is a secondary prop. Match perspective, depth of field, contact shadow, reflected soil light and slight soil interaction. No sticker, cut-out, halo, collage, floating object, fake writing, giant packaging or cropped product.'''
def watermark(im):
 c=im.convert('RGBA');o=Image.new('RGBA',c.size,(0,0,0,0));d=ImageDraw.Draw(o)
 try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',27)
 except OSError:f=ImageFont.load_default()
 b=d.textbbox((0,0),PHONE,font=f);w,h=b[2]-b[0],b[3]-b[1];m,px,py=18,16,10;x=c.width-w-m-2*px;y=c.height-h-m-2*py;d.rounded_rectangle((x,y,c.width-m,c.height-m),radius=8,fill=(0,0,0,178));d.text((x+px,y+py-b[1]),PHONE,font=f,fill='white');return Image.alpha_composite(c,o).convert('RGB')
def call(name,title,summary):
 payload={'model':MODEL,'prompt':prompt(title,summary),'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':refs()}};last=None
 for attempt in range(1,4):
  try:
   req=urllib.request.Request(API,data=json.dumps(payload).encode(),method='POST',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-tape-no-people-test/1.0'})
   with urllib.request.urlopen(req,timeout=600) as r:data=json.loads(r.read())
   row=(data.get('data') or [{}])[0]
   if row.get('b64_json'):blob=base64.b64decode(row['b64_json'])
   elif row.get('url'):
    with urllib.request.urlopen(row['url'],timeout=300) as r:blob=r.read()
   else:raise RuntimeError('image response missing')
   im=Image.open(io.BytesIO(blob)).convert('RGB');w,h=im.size;target=16/9
   if w/h>target:nw=int(h*target);x=(w-nw)//2;im=im.crop((x,0,x+nw,h))
   else:nh=int(w/target);y=(h-nh)//2;im=im.crop((0,y,w,y+nh))
   im=watermark(im.resize((1200,675),Image.Resampling.LANCZOS));buf=io.BytesIO();im.save(buf,'WEBP',quality=72,method=6);raw=buf.getvalue();path=OUT/f'tape-no-people-{name}.webp';path.write_bytes(raw);return {'variant':name,'file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'title':title,'summary':summary,'scale':'10-12 percent prompt; target visual result 17-20 percent'}
  except Exception as exc:
   last=exc
   if attempt<3:time.sleep(30*attempt)
 raise RuntimeError(f'{name} failed: {last}')
def main():
 if not KEY:raise RuntimeError('IMAGE_API_KEY/AGNES_API_KEY is missing')
 OUT.mkdir(parents=True,exist_ok=True)
 for p in OUT.glob('tape-no-people-*.webp'):p.unlink()
 records=[call(name,title,summary) for name,title,summary in SCENES]
 (OUT/'tape-no-people-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print(json.dumps(records,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
