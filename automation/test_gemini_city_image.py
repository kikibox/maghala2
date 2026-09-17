#!/usr/bin/env python3
import base64,hashlib,json,os,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/city-content-queue/test-images'; OUT.mkdir(parents=True,exist_ok=True)
KEY=os.getenv('GEMINI_API_KEY','').strip()
if not KEY: raise RuntimeError('GEMINI_API_KEY is missing')
MODEL='gemini-3.1-flash-image'
prompt=('Create a photorealistic editorial agriculture photograph for a Persian city article about Davoudabad, Markazi province, Iran. '
        'Show a wide modern farm field at golden hour, with long rows of drip irrigation tape clearly visible beside healthy young crops, '
        'realistic soil, irrigation filter and fittings, and a subtle central-Iran landscape. Natural colors, professional commercial photography. '
        'No people, no text, no logo, no watermark, no labels. Compose specifically for a 16:9 website hero image.')
payload={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseModalities':['TEXT','IMAGE'],'imageConfig':{'aspectRatio':'16:9','imageSize':'2K'}}}
url=f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'
req=urllib.request.Request(url,data=json.dumps(payload).encode(),method='POST',headers={'x-goog-api-key':KEY,'Content-Type':'application/json','User-Agent':'navar-city-image-test/1.0'})
try:
    with urllib.request.urlopen(req,timeout=420) as response: result=json.loads(response.read())
    image=None; mime=None
    for candidate in result.get('candidates',[]):
        for part in candidate.get('content',{}).get('parts',[]):
            inline=part.get('inlineData') or part.get('inline_data')
            if inline and inline.get('data'):
                image=base64.b64decode(inline['data']); mime=inline.get('mimeType') or inline.get('mime_type') or 'image/png'; break
        if image: break
    if not image or len(image)<10000: raise RuntimeError('Gemini returned no usable image')
    ext='.jpg' if 'jpeg' in mime else '.png'; path=OUT/('davoudabad-markazi-gemini-test'+ext); path.write_bytes(image)
    status={'result':'success','city':'داودآباد','province':'مرکزی','model':MODEL,'content_type':mime,'bytes':len(image),'sha256':hashlib.sha256(image).hexdigest(),'file':path.name}
except urllib.error.HTTPError as exc:
    body=exc.read().decode('utf-8','replace')[:1600]; status={'result':'failed','city':'داودآباد','province':'مرکزی','model':MODEL,'error':f'HTTP {exc.code}: {body}'}
    (OUT/'gemini-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); raise RuntimeError(status['error'])
except Exception as exc:
    status={'result':'failed','city':'داودآباد','province':'مرکزی','model':MODEL,'error':str(exc)[:1600]}
    (OUT/'gemini-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); raise
(OUT/'gemini-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(status,ensure_ascii=False,indent=2))
