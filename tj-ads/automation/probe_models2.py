import json, os, re, sys, time, urllib.request, pathlib
base = (os.getenv('AGNES_API_BASE') or 'https://apihub.agnes-ai.com/v1').rstrip('/')
key = os.getenv('AGNES_API_KEY', '').strip()
def call(msgs, model, mt=3000):
    req = urllib.request.Request(base + '/chat/completions', data=json.dumps({'model': model, 'messages': msgs, 'temperature': 0.1, 'max_tokens': mt}).encode(),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'User-Agent': 'navar-probe'})
    with urllib.request.urlopen(req, timeout=240) as r: return json.loads(r.read())['choices'][0]['message']['content'].strip()
item = json.load(open('tj-ads/artifacts/tj-ads/items/rudaki-02.json', encoding='utf-8'))
ps = [re.sub(r'<[^>]+>', '', p).strip() for p in re.findall(r'<p>(.*?)</p>', item['source_fa']['html'], re.S)]
ps = [p for p in ps if len(p) > 250][:3]
I = json.load(open('tj-ads/config/i18n.json', encoding='utf-8'))
GL_TG = I['glossary']['tg-TJ'] + " Place names: رودکی = Рӯдакӣ; Душанбе; водии Ҳисор = водии Ҳисор."
GL_RU = I['glossary']['ru-RU'] + " Place names: رودکی = Рудаки; Гиссарская долина."
out = {'persian': ps, 'runs': {}}
def tr(text, src, dst, model, gl):
    sysm = 'You are a precise agricultural localization editor. Return only the translation text.'
    u = f'Translate this {src} text into {dst}. {gl} Natural, correct, fluent language; do not invent facts; keep meaning exact.\n\n{text}'
    return call([{'role': 'system', 'content': sysm}, {'role': 'user', 'content': u}], model)
for model in ('agnes-3.0-flash', 'agnes-2.5-flash'):
    for name in ('fa>tg', 'fa>ru>tg', 'fa>ru'):
        res = []
        for p in ps:
            try:
                if name == 'fa>tg': res.append(tr(p, 'Persian', 'Tajik (Cyrillic)', model, GL_TG))
                elif name == 'fa>ru': res.append(tr(p, 'Persian', 'Russian', model, GL_RU))
                else:
                    r = tr(p, 'Persian', 'Russian', model, GL_RU); res.append(tr(r, 'Russian', 'Tajik (Cyrillic)', model, GL_TG))
            except Exception as e: res.append('ERR ' + str(e)[:120])
        out['runs'][f'{model} {name}'] = res
d = pathlib.Path('tj-ads/artifacts/tj-ads'); (d / 'probe2.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8'); print('done')
