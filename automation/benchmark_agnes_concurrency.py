#!/usr/bin/env python3
"""Measure safe text/image API concurrency without touching the article queue."""
from __future__ import annotations
import argparse,base64,datetime as dt,io,json,os,time,urllib.error,urllib.request
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'benchmarks'
TEXT_BASE=(os.getenv('AGNES_API_BASE') or 'https://apihub.agnes-ai.com/v1').rstrip('/')
TEXT_KEY=(os.getenv('AGNES_API_KEY') or '').strip()
TEXT_MODEL=os.getenv('AGNES_MODEL') or 'agnes-3.0-flash'
IMAGE_KEY=(os.getenv('IMAGE_API_KEY') or TEXT_KEY).strip()
IMAGE_ENDPOINT=os.getenv('IMAGE_ENDPOINT') or f'{TEXT_BASE}/images/generations'
IMAGE_MODEL=os.getenv('IMAGE_MODEL') or 'agnes-image-2.5-flash'


def neutral_input()->str:
    image=Image.new('RGB',(1024,576),(232,234,228));buf=io.BytesIO();image.save(buf,'PNG',optimize=True)
    return 'data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')


def post(url,key,payload,timeout):
    req=urllib.request.Request(url,data=json.dumps(payload,ensure_ascii=False).encode(),method='POST',headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Accept':'application/json','User-Agent':'maghala2-concurrency-benchmark/1.0'})
    started=time.perf_counter()
    try:
        with urllib.request.urlopen(req,timeout=timeout) as response:
            data=json.loads(response.read());return {'ok':True,'status':response.status,'seconds':round(time.perf_counter()-started,3),'response':data}
    except urllib.error.HTTPError as exc:
        detail=exc.read().decode('utf-8','replace')[:500]
        return {'ok':False,'status':exc.code,'seconds':round(time.perf_counter()-started,3),'error':detail}
    except Exception as exc:
        return {'ok':False,'status':None,'seconds':round(time.perf_counter()-started,3),'error':f'{type(exc).__name__}: {exc}'}


def text_request(_):
    payload={'model':TEXT_MODEL,'messages':[{'role':'user','content':'Return only this JSON object: {"ok":true}'}],'temperature':0,'max_tokens':80}
    result=post(TEXT_BASE+'/chat/completions',TEXT_KEY,payload,180)
    if result['ok']:
        content=(result.pop('response').get('choices') or [{}])[0].get('message',{}).get('content','')
        result['valid_response']='ok' in str(content).lower()
        result['ok']=result['ok'] and result['valid_response']
    return result


def image_request(_):
    payload={'model':IMAGE_MODEL,'prompt':'Photorealistic wide 16:9 Iranian farm field, natural daylight, no text, no logo, no product close-up.','size':'1024x768','return_base64':True,'extra_body':{'response_format':'b64_json','image':[neutral_input()]}}
    result=post(IMAGE_ENDPOINT,IMAGE_KEY,payload,600)
    if result['ok']:
        row=(result.pop('response').get('data') or [{}])[0]
        result['valid_response']=bool(row.get('b64_json') or row.get('url'))
        result['ok']=result['ok'] and result['valid_response']
    return result


def measure(name,level,worker):
    started=time.perf_counter();rows=[]
    with ThreadPoolExecutor(max_workers=level,thread_name_prefix=name) as pool:
        futures=[pool.submit(worker,index) for index in range(level)]
        for future in as_completed(futures):rows.append(future.result())
    elapsed=round(time.perf_counter()-started,3);success=sum(bool(row.get('ok')) for row in rows)
    return {'service':name,'concurrency':level,'requests':level,'successes':success,'failures':level-success,'wall_seconds':elapsed,'max_request_seconds':max((row.get('seconds',0) for row in rows),default=0),'statuses':sorted({str(row.get('status')) for row in rows}),'results':rows}


def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument('--levels',default=os.getenv('BENCHMARK_LEVELS','1,2,4'));parser.add_argument('--text-only',action='store_true');parser.add_argument('--image-only',action='store_true');args=parser.parse_args()
    levels=sorted({max(1,int(x)) for x in args.levels.split(',') if x.strip()})
    if not TEXT_KEY and not args.image_only:raise RuntimeError('AGNES_API_KEY is missing')
    if not IMAGE_KEY and not args.text_only:raise RuntimeError('IMAGE_API_KEY/AGNES_API_KEY is missing')
    rows=[]
    for level in levels:
        if not args.image_only:rows.append(measure('text',level,text_request))
        if not args.text_only:rows.append(measure('image',level,image_request))
    safe={service:max([r['concurrency'] for r in rows if r['service']==service and r['failures']==0],default=0) for service in ('text','image')}
    report={'created_at':dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),'levels':levels,'text_model':TEXT_MODEL,'image_model':IMAGE_MODEL,'separate_image_endpoint':IMAGE_ENDPOINT!=TEXT_BASE+'/images/generations','safe_concurrency':safe,'runs':rows}
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'latest.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary=['# Agnes concurrency benchmark','',f'- Text model: `{TEXT_MODEL}`',f'- Image model: `{IMAGE_MODEL}`',f'- Safe text concurrency: **{safe["text"]}**',f'- Safe image concurrency: **{safe["image"]}**','', '| Service | Concurrency | Success | Failure | Wall time |','|---|---:|---:|---:|---:|']
    for row in rows:summary.append(f"| {row['service']} | {row['concurrency']} | {row['successes']} | {row['failures']} | {row['wall_seconds']}s |")
    (OUT/'latest.md').write_text('\n'.join(summary)+'\n',encoding='utf-8');print('\n'.join(summary));return 0


if __name__=='__main__':raise SystemExit(main())
