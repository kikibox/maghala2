#!/usr/bin/env python3
import hashlib,json,os,urllib.error,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/city-content-queue/test-images'; OUT.mkdir(parents=True,exist_ok=True)
KEY=os.getenv('POLLINATIONS_API_KEY','').strip()
if not KEY: raise RuntimeError('POLLINATIONS_API_KEY is missing')
MODEL='z-image'
prompt=('Photorealistic editorial agriculture photograph for a Persian city article about Davoudabad, Markazi province, Iran. '
        'Wide modern farm field at golden hour, long rows of drip irrigation tape clearly visible beside healthy young crops, '
        'realistic soil, filter and irrigation fittings, subtle central Iran landscape, natural colors, professional commercial photography, '
        'no people, no text, no logo, no watermark, no labels, 16:9 composition.')
params=urllib.parse.urlencode({'model':MODEL,'width':1200,'height':675,'seed':1002536,'safe':'true'})
url='https://gen.pollinations.ai/image/'+urllib.parse.quote(prompt,safe='')+'?'+params
req=urllib.request.Request(url,headers={'Authorization':'Bearer '+KEY,'Accept':'image/*','User-Agent':'navar-city-image-test/1.0'})
try:
    with urllib.request.urlopen(req,timeout=420) as response:
        blob=response.read(); content_type=response.headers.get('Content-Type','')
    if not content_type.startswith('image/') or len(blob)<10000: raise RuntimeError(f'Unexpected response: {content_type}, {len(blob)} bytes')
    ext='.png' if 'png' in content_type else '.jpg'; path=OUT/('davoudabad-markazi-pollinations-test'+ext); path.write_bytes(blob)
    status={'result':'success','city':'داودآباد','province':'مرکزی','model':MODEL,'content_type':content_type,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'file':path.name}
except urllib.error.HTTPError as exc:
    body=exc.read().decode('utf-8','replace')[:1200]; status={'result':'failed','city':'داودآباد','province':'مرکزی','model':MODEL,'error':f'HTTP {exc.code}: {body}'}
    (OUT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); raise RuntimeError(status['error'])
except Exception as exc:
    status={'result':'failed','city':'داودآباد','province':'مرکزی','model':MODEL,'error':str(exc)[:1200]}
    (OUT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); raise
(OUT/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(status,ensure_ascii=False,indent=2))
