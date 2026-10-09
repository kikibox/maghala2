import json, os, urllib.request, time, pathlib
base = (os.getenv('AGNES_API_BASE') or 'https://apihub.agnes-ai.com/v1').rstrip('/')
key = os.getenv('AGNES_API_KEY', '').strip()
out = {'models': None, 'samples': {}}
def call(path, payload=None, timeout=240):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode() if payload else None,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'User-Agent': 'navar-probe'})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())
try:
    m = call('/models'); ids = [x.get('id') for x in m.get('data', [])]; out['models'] = ids
except Exception as e:
    out['models_error'] = str(e)[:300]; ids = ['agnes-3.0-flash']
skip = ('image', 'video', 'embed', 'audio', 'tts', 'whisper', 'vision-gen')
cands = [i for i in ids if i and not any(s in i.lower() for s in skip)][:14]
prompt = ('Нависед 130 калимаи тоҷикӣ (хати кириллӣ) дар бораи он ки чаро лентаи обёрии қатрагӣ барои киштзори пахта дар ноҳияи Рӯдакӣ мувофиқ аст ва чӣ тавр онро насб кардан лозим. '
          'Забони табиӣ, оддӣ ва дуруст; ҳеҷ калимаи русӣ ё форсӣ надошта бошад; рақам ва омори сохта наоред.')
for c in cands:
    t = time.time()
    try:
        r = call('/chat/completions', {'model': c, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0.3, 'max_tokens': 1500})
        out['samples'][c] = {'sec': round(time.time() - t), 'text': r['choices'][0]['message'].get('content', '')}
    except Exception as e:
        out['samples'][c] = {'error': str(e)[:200]}
p = pathlib.Path('tj-ads/artifacts/tj-ads'); p.mkdir(parents=True, exist_ok=True)
(p / 'probe.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print('done', len(cands))
