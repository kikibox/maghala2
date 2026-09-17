#!/usr/bin/env python3
import base64,json,os,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/city-content-queue/test-images'; OUT.mkdir(parents=True,exist_ok=True)
TOKEN=os.getenv('CLOUDFLARE_API_TOKEN','').strip(); ACCOUNT=os.getenv('CLOUDFLARE_ACCOUNT_ID','').strip()
if not TOKEN or not ACCOUNT: raise RuntimeError('Cloudflare Actions secrets are missing')
MODEL='@cf/leonardo/lucid-origin'
url='https://'+'api.cloudflare.com/client/v4/accounts/'+ACCOUNT+'/ai/run/'+MODEL
prompt=('Photorealistic editorial agriculture photograph for a Persian city article about Davoudabad, Markazi province, Iran. '
        'Wide modern farm field at golden hour, long rows of drip irrigation tape clearly visible beside healthy young crops, '
        'realistic soil, irrigation filter and fittings, subtle central Iran landscape, natural colors, professional commercial photography, '
        'no people, no text, no logo, no watermark, no labels, 16:9 website hero composition.')
payload={'prompt':prompt,'width':1200,'height':675,'num_steps':20,'guidance':4.5,'seed':1002536}
req=urllib.request.Request(url,data=json.dumps(payload).encode(),method='POST',headers={'Authorization':'Bearer '+TOKEN,'Content-Type':'application/json','Accept':'application/json','User-Agent':'navar-cloudflare-test/1.0'})
try:
    with urllib.request.urlopen(req,timeout=300) as response: data=json.loads(response.read())
    if not data.get('success'): raise RuntimeError('Cloudflare returned success=false: '+json.dumps(data)[:1200])
    image=(data.get('result') or {}).get('image')
    if not image: raise RuntimeError('Cloudflare authenticated but returned no image')
    blob=base64.b64decode(image)
    if len(blob)<1000: raise RuntimeError('Cloudflare returned an unusable image')
    path=OUT/'davoudabad-markazi-cloudflare-lucid-origin.jpg'; path.write_bytes(blob)
    status={'result':'success','provider':'Cloudflare Workers AI','model':MODEL,'account_verified':True,'image_bytes':len(blob),'file':path.name,'width':1200,'height':675,'steps':20}
except urllib.error.HTTPError as exc:
    body=exc.read().decode('utf-8','replace')[:1600]; status={'result':'failed','provider':'Cloudflare Workers AI','model':MODEL,'error':f'HTTP {exc.code}: {body}'}
    (OUT/'cloudflare-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); raise RuntimeError(status['error'])
except Exception as exc:
    status={'result':'failed','provider':'Cloudflare Workers AI','model':MODEL,'error':str(exc)[:1600]}
    (OUT/'cloudflare-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); raise
(OUT/'cloudflare-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(status,ensure_ascii=False,indent=2))
