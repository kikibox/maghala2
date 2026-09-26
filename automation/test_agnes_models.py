#!/usr/bin/env python3
"""Verify Agnes 3.0 Flash text and Agnes Image 2.0 Flash with one safe image."""
import base64,io,json,os,urllib.error,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/city-content-queue/test-images';OUT.mkdir(parents=True,exist_ok=True)
KEY=os.getenv('AGNES_API_KEY','').strip();BASE=os.getenv('AGNES_API_BASE','https://apihub.agnes-ai.com/v1').rstrip('/')
TEXT_MODEL=os.getenv('AGNES_MODEL','agnes-3.0-flash');IMAGE_MODEL=os.getenv('AGNES_IMAGE_MODEL','agnes-image-2.5-flash')
STATUS=OUT/'agnes-models-status.json';IMAGE=OUT/'davoudabad-markazi-agnes-image-2-test.jpg'
if not KEY:raise RuntimeError('AGNES_API_KEY is missing')

def request(path,payload,timeout=420):
 req=urllib.request.Request(BASE+path,data=json.dumps(payload,ensure_ascii=False).encode(),method='POST',headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-agnes-model-test/1.0'})
 try:
  with urllib.request.urlopen(req,timeout=timeout) as response:return json.loads(response.read())
 except urllib.error.HTTPError as exc:raise RuntimeError(f"HTTP {exc.code} {path}: {exc.read().decode('utf-8','replace')[:1600]}")

def download(url):
 with urllib.request.urlopen(url,timeout=300) as response:return response.read()

def add_watermark(blob):
 im=Image.open(io.BytesIO(blob)).convert('RGB');draw=ImageDraw.Draw(im,'RGBA');text='AFP Pipe | 09134922013'
 fp='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';font=ImageFont.truetype(fp,max(20,im.width//42)) if Path(fp).exists() else ImageFont.load_default()
 box=draw.textbbox((0,0),text,font=font);tw,th=box[2]-box[0],box[3]-box[1];pad=max(12,im.width//70);x=im.width-tw-pad*2;y=im.height-th-pad*2
 draw.rounded_rectangle((x-pad,y-pad,im.width-pad//2,im.height-pad//2),radius=10,fill=(0,0,0,165));draw.text((x,y),text,font=font,fill=(255,255,255,245))
 out=io.BytesIO();im.save(out,'JPEG',quality=92,optimize=True);return out.getvalue()

status={'text_model':TEXT_MODEL,'image_model':IMAGE_MODEL,'text_result':'failed','image_result':'not_started'}
try:
 text=request('/chat/completions',{'model':TEXT_MODEL,'messages':[{'role':'system','content':'فقط یک JSON معتبر برگردان.'},{'role':'user','content':'یک JSON با کلید status و مقدار ok برگردان.'}],'temperature':0,'max_tokens':100})
 content=text['choices'][0]['message']['content'];
 if not content:raise RuntimeError('Agnes text model returned empty content')
 status['text_result']='success';status['image_result']='failed'
 prompt=('Photorealistic editorial agriculture photograph made for a Persian article about drip irrigation tape in Davoudabad, Markazi province, Iran. '
         'Wide healthy crop rows, accurate drip irrigation tape and fittings, natural central Iran farm scenery, professional commercial lighting, '
         'no generated text, no logos, no watermark, no people, 4:3 composition.')
 image=request('/images/generations',{'model':IMAGE_MODEL,'prompt':prompt,'size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json'}},600)
 row=(image.get('data') or [{}])[0]
 if row.get('b64_json'):blob=base64.b64decode(row['b64_json'])
 elif row.get('url'):blob=download(row['url'])
 else:raise RuntimeError('Agnes image response has neither b64_json nor url')
 blob=add_watermark(blob)
 if len(blob)<10000:raise RuntimeError('Agnes generated image is unexpectedly small')
 IMAGE.write_bytes(blob);status.update(image_result='success',image_bytes=len(blob),image_file=IMAGE.name)
except Exception as exc:
 status['error']=str(exc)[:1800];STATUS.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8');raise
STATUS.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(status,ensure_ascii=False,indent=2))
