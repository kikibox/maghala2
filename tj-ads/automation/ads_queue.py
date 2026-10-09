#!/usr/bin/env python3
"""Tajikistan ad-post queue: text + images (Agnes, same keys as maghala2) + reversible MySQL SQL.

Mirrors kikibox/maghala2 city_content_queue.py, but for the custom post type `tajikistan`
(Tajik, Cyrillic). Posts are inserted as DRAFT. See docs/RULES.md.

Usage:
  python automation/ads_queue.py --init-only          # create artifacts/tj-ads/queue.json
  python automation/ads_queue.py                      # process one batch (BATCH_SIZE)
  python automation/ads_queue.py --mock --limit 3     # offline dry-run with fake text/images
  python automation/ads_queue.py --only-place rudaki --tier A
"""
import argparse, base64, datetime as dt, hashlib, html, io, itertools, json, os, random, re, sys, time, urllib.error, urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'config'
OUT = ROOT / 'artifacts/tj-ads'
ITEMS, IMAGES, SQL, ROLLBACK = OUT / 'items', OUT / 'images', OUT / 'sql', OUT / 'rollback'
QUEUE, STATUS = OUT / 'queue.json', OUT / 'status.json'
DBG = OUT / 'debug'

SITE = 'https://navar-abyari.ir'
for _p in (ROOT.parent / 'automation', ROOT / 'automation'):          # maghala2/automation when run from the branch
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.append(str(_p))
try:
    import image_prompt_policy as IPP      # maghala2: AFP reference images, crop identity lock, phone watermark
except Exception:                          # standalone / missing Pillow assets
    IPP = None
POST_TYPE = 'tajikistan'
TABLE, META = os.getenv('WP_POSTS_TABLE', 'ha_posts'), os.getenv('WP_POSTMETA_TABLE', 'ha_postmeta')
UPLOAD_DIR = (os.getenv('TJ_IMAGE_UPLOAD_SUBDIR') or '2026/10/navar-tj-ads').strip('/')   # wp-content/uploads/<UPLOAD_DIR>/file.webp
POST_STATUS = os.getenv('POST_STATUS', 'draft')            # draft until the owner reviews

AGNES_BASE = (os.getenv('AGNES_API_BASE') or 'https://apihub.agnes-ai.com/v1').rstrip('/')
AGNES_KEYS = []
for _n in ['AGNES_API_KEY'] + [f'AGNES_API_KEY{i}' for i in range(2, 15)]:   # same secret names as maghala2
    _v = os.getenv(_n, '').strip()
    if _v and _v not in AGNES_KEYS:
        AGNES_KEYS.append(_v)
AGNES_KEY = AGNES_KEYS[0] if AGNES_KEYS else ''
_KEYS = itertools.count()
AGNES_MODEL = os.getenv('AGNES_MODEL') or 'agnes-3.0-flash'
IMAGE_TOKEN = (os.getenv('IMAGE_API_KEY') or AGNES_KEY).strip()
IMAGE_MODEL = os.getenv('IMAGE_MODEL') or 'agnes-image-2.5-flash'
IMAGE_ENDPOINT = os.getenv('IMAGE_ENDPOINT') or f'{AGNES_BASE}/images/generations'

BATCH = max(1, int(os.getenv('BATCH_SIZE', '3')))
MIN_WORDS = int(os.getenv('MIN_WORDS', '1050'))
MIN_LINKS, MAX_LINKS = int(os.getenv('MIN_INTERNAL_LINKS', '4')), int(os.getenv('MAX_INTERNAL_LINKS', '7'))
TARGET_WORDS = int(MIN_WORDS * 1.3)
MAX_ATTEMPTS = max(1, int(os.getenv('MAX_ATTEMPTS', '4')))
IMAGES_PER_POST = 3

TG_LETTERS = 'А-Яа-яЁёҒғӢӣҚқӮӯҲҳҶҷ'
WORD_RE = re.compile(rf'[{TG_LETTERS}]+(?:-[{TG_LETTERS}]+)?')
HREF_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']+)', re.I)
ARABIC_RE = re.compile(r'[\u0600-\u06ff\u0750-\u077f]')
LATIN_WORD_RE = re.compile(r'\b[A-Za-z]{2,}\b')
RUSSIAN_ONLY = re.compile(r'[ыщьЫЩЬ]|\b(что|это|для|при|как|или|если|который|также|можно)\b', re.I)
PRICE_RE = re.compile(r'\d[\d\s.,]*\s*(сомонӣ|сомони|сом\b|доллар|\$|USD|дирам|риал|томон|₽|руб)', re.I)


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def cfg(name):
    return json.loads((CFG / name).read_text(encoding='utf-8'))


def esc(s):
    return str(s).replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r').replace('\0', '')


def words(text):
    return len(WORD_RE.findall(re.sub(r'<[^>]+>', ' ', text or '')))


def internal_links(text):
    return [u for u in HREF_RE.findall(text or '') if 'navar-abyari.ir' in u]


def fetch_json(url, headers=None, payload=None, timeout=420):
    req = urllib.request.Request(url, data=(json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None), headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'HTTP {e.code} {url}: {e.read().decode("utf-8", "replace")[:800]}')


# ---------------------------------------------------------------- queue

def write_status(q, result):
    c = Counter(x['status'] for x in q['items'])
    STATUS.write_text(json.dumps({'result': result, 'updated_at': now(), 'total': len(q['items']), **{k: c[k] for k in ('pending', 'processing', 'completed', 'failed', 'blocked_image_model')}, 'text_model': AGNES_MODEL, 'image_model': IMAGE_MODEL, 'batch_size': BATCH}, ensure_ascii=False, indent=2), encoding='utf-8')


def save(q):
    q['updated_at'] = now()
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')


def initialize(force=False):
    for p in (OUT, ITEMS, IMAGES, SQL, ROLLBACK):
        p.mkdir(parents=True, exist_ok=True)
    if QUEUE.exists() and not force:
        return json.loads(QUEUE.read_text(encoding='utf-8'))
    titles = json.loads((ROOT / 'data/titles.json').read_text(encoding='utf-8'))
    q = {'version': 1, 'created_at': now(), 'updated_at': now(), 'scope': 'Tajikistan ads, 50 places', 'post_type': POST_TYPE, 'text_model': AGNES_MODEL, 'image_model': IMAGE_MODEL,
         'rules': {'post_status': POST_STATUS, 'minimum_words': MIN_WORDS, 'internal_links': [MIN_LINKS, MAX_LINKS], 'images_per_post': IMAGES_PER_POST, 'faq': 3},
         'items': titles}
    save(q); write_status(q, 'initialized')
    return q


# ---------------------------------------------------------------- prompt

CROP_CONTEXT = {
    'A': 'Дар сарчашмаи санҷидашуда ба худи ин макон ишора шудааст: {fact}',
    'B': 'Ин зироат дар минтақаи ({zone}) мувофиқи сарчашмаи ошкоро парвариш мешавад. Рақам ва омори иловагӣ насозед.',
    'C': 'Мувофиқи сарчашмаи ошкоро, ин зироат дар саросари Тоҷикистон парвариш мешавад. Дар бораи ин макон рақам ё омори хос насозед.',
}
SCENES = {
    'tape': ['wide field view with black drip irrigation tape laid along {crop} rows, soft morning light',
             'close-up of drip tape emitters wetting soil next to young {crop} plants',
             'farmer hands (no face) connecting drip tape to a flat-lay supply line and filter at the field edge'],
    'pipe': ['black polyethylene (PE) main pipeline running along the edge of a {crop} field, clean farm setting',
             'close-up of PE pipe fittings and a valve feeding drip tape lines on a {crop} plot',
             'worker hands (no face) fitting a connector on a black PE pipe near {crop} rows'],
    'layflat': ['thread-reinforced layflat hose carrying water from an irrigation canal to a {crop} field, partly inflated',
                'close-up of the woven reinforcement texture of a blue/black layflat hose, rolled and laid on soil',
                'rolled layflat hose beside a pump and canal, with {crop} rows in the background'],
}
CROP_EN = {c['id']: c['name_en'].lower() for c in cfg('crops.json')['crops']}


def pick_pool(item, pool, rng):
    links = pool['links']
    keep = [pool['pillar']] + [x for x in links if x['tag'] == 'trust' and x['url'].endswith(('tg-tj-tamos/', 'tg-tj-kafolat/', 'tj-rules/', 'tg-tj-hizmatrasoni/'))]
    typed = [x for x in links if x['tag'] == {'tape': 'tape', 'pipe': 'layflat', 'layflat': 'layflat'}[item['product']]]
    rng.shuffle(typed)
    guide = [x for x in links if x['tag'] == 'guide']
    rng.shuffle(guide)
    return keep + typed[:3] + guide[:2]


def build_prompt(item, place, products, gov, pool_links):
    prod = products['products'][item['product']]
    crop_line = ''
    if item['crop']:
        pc = next(c for c in place['crops'] if c['crop'] == item['crop'])
        fact = next((f['text_tg'] for f in place['place_facts']), '')
        crop_line = CROP_CONTEXT[pc['evidence']].format(fact=fact or '—', zone=place['zone_label_tg'])
    facts = '\n'.join('- ' + f['text_tg'] for f in place['place_facts']) or '- (рақам ва омори хоси макон нест; дар матн наёваред)'
    seed = random.Random(item['id']).choice(gov['cooperation_paragraph_seeds_tg'])
    links = '\n'.join(f"L{i} = {x['title']}" for i, x in enumerate(pool_links, 1))
    return f'''Write a NEW, original, SEO-optimised advertising/information article in TAJIK (Cyrillic script, tg-TJ). No Russian, no Persian/Arabic letters, no Latin words except the brand "AFP".
POST TITLE (use exactly, do NOT repeat it as H1): {item['title']}
PLACE: {item['place_tg']} ({'city' if item['kind']=='city' else 'district'}), region {place['region_tg']}; agro-zone: {place['zone_label_tg']}.
PRODUCT: {prod['name_tg']}  (site synonyms: {', '.join(prod.get('site_synonyms_tg', [])) or '-'}). Product facts you may use: {'; '.join(prod['facts_ok'])}.
CROP: {item['crop_tg'] or '(no single crop: speak about row crops in general)'}. {crop_line}
VERIFIED LOCAL FACTS (only these may be stated as facts about the place):
{facts}

STRICT RULES
1. HTML only: h2/h3/p/ul/ol/li/table/strong/a/details/summary. No H1. LENGTH: write about {TARGET_WORDS} Tajik words (hard minimum {MIN_WORDS}); every h2 section needs 2-4 substantial paragraphs. Natural, practical, farmer-oriented Tajik. Do not copy template phrases; vary sentence openings.
2. Row crops only (no orchards, vineyards, greenhouses). Do not claim the crop is "the main crop" of the place unless it is in VERIFIED LOCAL FACTS.
3. NEVER invent: prices, discounts, yields, statistics, dates, awards, certificates, a representative/agency/warehouse/service centre in Tajikistan, free or local delivery, or any government/president endorsement. No numbers with currency.
4. Commercial wording: prices and purchase terms are agreed by phone/form; the products carry a warranty but after-sales and delivery terms to Tajikistan are agreed separately. Put the marker [[[CONTACT_BOX]]] once (the script inserts phone and safe wording).
5. Government context: write ONE short original paragraph (2-3 sentences) in the spirit of: "{seed}" - rephrase it, never copy it, never attribute words to the president, never imply endorsement. It must contain the link [[L1|natural anchor text]] (the pillar page).
6. Structure: intro (mention place + product + crop) → [[[IMAGE_1]]] → h2 why/when this product fits the crop → h2 how to choose (include one small table of general selection criteria, no catalogue numbers you are unsure of) → [[[IMAGE_2]]] → h2 installation and care (ol) → h2 water saving and field practice (no invented local data) → h2 cooperation paragraph (rule 5) → [[[CONTACT_BOX]]] → [[[IMAGE_3]]] → FAQ: exactly 3 questions, each as <details class="navar-faq"><summary><h3>question</h3></summary><div><p>answer</p></div></details> → final <h2>Маводи алоқаманд</h2><ul> with related links (placeholders). ALL markers [[[IMAGE_1]]], [[[IMAGE_2]]], [[[IMAGE_3]]], [[[CONTACT_BOX]]] are mandatory, each exactly once, on their own line.
7. INTERNAL LINKS: NEVER write URLs or <a> tags. To link, write the placeholder [[L<number>|anchor text in Tajik]] using ONLY the numbers from this list. Use between {MIN_LINKS} and {MAX_LINKS} DIFFERENT placeholders in total; [[L1|...]] (pillar) is mandatory:
{links}
8. Return ONLY valid JSON: {{"html": "...", "excerpt": "<=160 chars Tajik", "meta_title": "<=60 chars Tajik", "meta_description": "<=155 chars Tajik", "focus_keyword": "2-4 Tajik words", "image_alts": ["alt1","alt2","alt3"]}}'''


SYSTEM = 'Шумо муҳаррири ҳирфаии забони тоҷикӣ (хати кириллӣ) дар мавзӯи обёрии кишоварзӣ ҳастед. Фақат JSON-и дуруст баргардонед.'


def parse_object(raw):
    text = str(raw or '').strip()
    if not text:
        raise ValueError('empty Agnes response')
    cands = [text] + re.findall(r'```(?:json)?\s*(.*?)\s*```', text, re.I | re.S)
    i, j = text.find('{'), text.rfind('}')
    if 0 <= i < j:
        cands.append(text[i:j + 1])
    err = []
    for c in cands:
        try:
            v = json.loads(c)
            v = json.loads(v) if isinstance(v, str) else v
            if isinstance(v, dict):
                return v
        except Exception as e:
            err.append(str(e))
    raise ValueError('no valid JSON object: ' + '; '.join(err[-2:]))


def agnes(prompt, attempts=3):
    if not AGNES_KEYS:
        raise RuntimeError('AGNES_API_KEY is missing')
    last = None
    for k in range(1, attempts + 1):
        try:
            key = AGNES_KEYS[next(_KEYS) % len(AGNES_KEYS)]
            data = fetch_json(AGNES_BASE + '/chat/completions', {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': 'navar-tj-ads-queue'},
                              {'model': AGNES_MODEL, 'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': prompt}], 'temperature': 0.45 if k == 1 else 0.25, 'max_tokens': 20000},
                              timeout=min(360, 180 + 30 * (k - 1)))
            return parse_object(data.get('choices', [{}])[0].get('message', {}).get('content', ''))
        except Exception as e:
            last = e
            print(f'agnes retry {k}/{attempts}: {str(e)[:200]}', flush=True)
            time.sleep(min(20, 2 ** k))
    raise RuntimeError('Agnes failed: ' + str(last))


# ---------------------------------------------------------------- validation

def urlnorm(u):
    import urllib.parse as up
    p = up.urlparse(u)
    return f"{p.scheme or 'https'}://{p.netloc}{up.quote(up.unquote(p.path), safe='/')}"


def sanitize_links(text, allowed):
    allowed_n = {urlnorm(u) for u in allowed}

    def keep(m):
        tag = m.group(0)
        h = re.search(r'href=["\']([^"\']+)', tag, re.I)
        if not h or urlnorm(h.group(1)) in allowed_n:
            return tag
        return re.sub(r'</?a\b[^>]*>', '', tag)
    return re.sub(r'<a\b[^>]*>.*?</a>', keep, text, flags=re.I | re.S)


PH_RE = re.compile(r'\[\[\s*L(\d+)\s*(?:\|\s*(.*?))?\s*\]\]', re.S)
RAW_URL_RE = re.compile(r'https?://[^\s<>"\')]+')


def resolve_links(text, pool_links):
    """Turn [[L3|anchor]] placeholders into <a href>; drop stray URLs/foreign links (model never writes hrefs)."""
    def ph(m):
        i = int(m.group(1))
        if not 1 <= i <= len(pool_links): return m.group(2) or ''
        x = pool_links[i - 1]
        return f'<a href="{x["url"]}">{html.escape(m.group(2) or x["title"], quote=False)}</a>'
    text = PH_RE.sub(ph, text)
    allowed = [x['url'] for x in pool_links]
    text = sanitize_links(text, allowed)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>' if urlnorm(m.group(2)) in {urlnorm(u) for u in allowed} else m.group(1), text)
    # raw URLs in visible text (not inside href="...")
    text = re.sub(r'(?<![\w"\'=/])' + RAW_URL_RE.pattern, '', text)
    return text


def validate(obj, item, allowed, products):
    """Return list of problems (empty = OK)."""
    body = obj.get('html', '')
    plain = re.sub(r'<[^>]+>', ' ', body)
    bad = []
    if words(body) < MIN_WORDS: bad.append(f'words {words(body)} < {MIN_WORDS}')
    used = {urlnorm(u) for u in internal_links(body)}
    if not (MIN_LINKS <= len(used) <= MAX_LINKS): bad.append(f'links {len(used)} not in {MIN_LINKS}-{MAX_LINKS}')
    if used - {urlnorm(u) for u in allowed}: bad.append('link outside approved pool')
    if urlnorm(cfg('link_pool.json')['pillar']['url']) not in used: bad.append('pillar link missing')
    for i in range(1, 4):
        if body.count(f'[[[IMAGE_{i}]]]') != 1: bad.append(f'IMAGE_{i} marker count')
    if body.count('[[[CONTACT_BOX]]]') != 1: bad.append('CONTACT_BOX marker count')
    if len(re.findall(r'<details\b', body)) != 3: bad.append('FAQ must be exactly 3 <details>')
    if re.search(r'<h1\b', body, re.I): bad.append('H1 not allowed')
    if len(re.findall(r'<h2\b', body, re.I)) < 4: bad.append('need >=4 h2')
    if ARABIC_RE.search(plain): bad.append('Arabic/Persian letters')
    if RUSSIAN_ONLY.search(plain): bad.append('Russian-only letters/words')
    latin = [w for w in LATIN_WORD_RE.findall(plain) if w not in ('AFP', 'PE', 'LIF')]
    if latin: bad.append('Latin words: ' + ','.join(latin[:5]))
    if PRICE_RE.search(plain): bad.append('price-like text')
    for phrase in products['forbidden_claims_tg']:
        if phrase.lower() in plain.lower(): bad.append('forbidden claim: ' + phrase)
    if item['crop_tg'] and item['crop_tg'] not in plain: bad.append('crop name missing')
    if item['place_tg'] not in plain: bad.append('place name missing')
    if products['products'][item['product']]['name_tg'].split()[-1] not in plain: bad.append('product term missing')
    for k in ('excerpt', 'meta_title', 'meta_description', 'focus_keyword'):
        if not obj.get(k): bad.append('missing ' + k)
    if len(obj.get('meta_title', '')) > 70: bad.append('meta_title too long')
    if len(obj.get('image_alts', [])) != 3: bad.append('need 3 image_alts')
    return bad


def make_content(item, place, products, gov, pool, mock=False):
    rng = random.Random(item['id'])
    pool_links = pick_pool(item, pool, rng)
    allowed = [x['url'] for x in pool_links]
    base_prompt = build_prompt(item, place, products, gov, pool_links)
    prompt, last, obj, history = base_prompt, [], None, []
    for attempt in range(5):
        new = mock_content(item, pool_links) if mock else agnes(prompt)
        if new.get('html'): obj = new
        obj['html'] = resolve_links(obj.get('html', ''), pool_links)
        last = validate(obj, item, allowed, products)
        history.append({'attempt': attempt + 1, 'problems': last, 'words': words(obj.get('html', ''))})
        if not last:
            return obj
        extra = ''
        m = ARABIC_RE.findall(re.sub(r'<[^>]+>', ' ', obj.get('html', '')))
        if m: extra += ' Offending Arabic/Persian characters: ' + ''.join(sorted(set(m))) + ' - replace them with Tajik Cyrillic.'
        prompt = (base_prompt + '\n\nPREVIOUS DRAFT (HTML, links already resolved; keep good parts):\n' + obj.get('html', '')[:30000] +
                  '\n\nQC rejected this draft: ' + '; '.join(last) + '.' + extra +
                  f'\nReturn the COMPLETE improved JSON again. If words are too few, EXPAND every section with concrete practical detail until about {TARGET_WORDS} words. Use [[L<n>|anchor]] placeholders for links and keep all [[[...]]] markers exactly once.')
    DBG.mkdir(parents=True, exist_ok=True)
    (DBG / f"{item['id']}.json").write_text(json.dumps({'history': history, 'last_html': obj.get('html', '') if obj else ''}, ensure_ascii=False, indent=1), encoding='utf-8')
    raise RuntimeError('Text QA failed: ' + '; '.join(last))


def mock_content(item, pool_links):
    """Offline stand-in used by --mock to test the pipeline (NOT real content)."""
    filler = ' '.join(['Ин матн барои санҷиши ҷараёни кор навишта шудааст ва мазмуни воқеӣ надорад.'] * 1)
    ps = ' '.join([f"{item['place_tg']} {item['crop_tg']} {item['title'].split()[0]} " + filler] * 1)
    link = lambda i: f'<a href="{pool_links[i]["url"]}">{pool_links[i]["title"]}</a>'
    prod = cfg('products.json')['products'][item['product']]['name_tg']
    body = f'<p>{ps} {prod}.</p>[[[IMAGE_1]]]' + ''.join(f'<h2>Бахши {i}</h2><p>' + ' '.join([f'{item["place_tg"]} {item["crop_tg"]} {prod} обёрӣ киштзор деҳқон об замин ҳосил'] * 30) + '</p>' for i in range(1, 5)) \
        + f'<p>Ҳамкорӣ: {link(0)}</p>[[[CONTACT_BOX]]][[[IMAGE_2]]][[[IMAGE_3]]]' + ' '.join(f'<details class="navar-faq"><summary><h3>Савол {i}?</h3></summary><div><p>Ҷавоб.</p></div></details>' for i in range(3)) \
        + '<h2>Маводи алоқаманд</h2><ul>' + ''.join(f'<li>{link(i)}</li>' for i in range(1, 4)) + '</ul>'
    body += '<p>' + ' '.join(['дар киштзор обёрии қатрагӣ мунтазам ва камхарҷ аст'] * 120) + '</p>'
    return {'html': body, 'excerpt': item['title'][:150], 'meta_title': item['title'][:58], 'meta_description': item['title'][:150], 'focus_keyword': f"{item['crop_tg']} {item['place_tg']}".strip(), 'image_alts': [f"{item['crop_tg']} {item['place_tg']} {i}" for i in (1, 2, 3)]}


# ---------------------------------------------------------------- images

PRODUCT_EN = {'tape': 'drip irrigation tape', 'pipe': 'black polyethylene (PE) irrigation pipe', 'layflat': 'thread-reinforced layflat hose'}


def image_item(item):
    """Item in the shape maghala2's image_prompt_policy expects (English brief; 'layflat' keyword selects the layflat reference)."""
    crop = CROP_EN.get(item['crop'], 'row crops')
    title = f"{PRODUCT_EN[item['product']]} for {crop} field, {item['place_en']} {('city' if item['kind'] == 'city' else 'district')}, Tajikistan"
    return {'id': item['id'], 'slug': item['slug'], 'title': title, 'focus': title, 'excerpt': ''}


def image_prompt(item, kind):
    if IPP and item['product'] != 'pipe':   # PE pipe has no AFP reference image -> own scene prompt
        try:
            return IPP.image_prompt(image_item(item), kind)
        except Exception as e:
            print('image_prompt_policy failed, using fallback:', str(e)[:120], flush=True)
    crop = CROP_EN.get(item['crop'], 'vegetable')
    scene = SCENES[item['product']][kind - 1].format(crop=crop)
    return (f"Photorealistic editorial agriculture photo, Central Asian farmland (Tajikistan), {scene}. Natural light, realistic colours, no text, no logo, no watermark, "
            f"no labels, no signage, no identifiable faces, no landmarks, 16:9 composition")


def reference_images(item, kind):
    # AFP product reference only for tape/layflat; PE pipe has no packshot, so no reference is sent
    if IPP and item['product'] in ('tape', 'layflat'):
        try:
            return IPP.reference_images(kind, image_item(item))
        except Exception as e:
            print('reference_images failed:', str(e)[:120], flush=True)
    return None


def to_webp(blob):
    """Normalise to 16:9, 1200x675, AFP phone watermark (as in maghala2), WebP q60."""
    from PIL import Image
    im = Image.open(io.BytesIO(blob)).convert('RGB')
    w, h = im.size
    if w / h > 16 / 9:
        nw = int(h * 16 / 9); l = (w - nw) // 2; im = im.crop((l, 0, l + nw, h))
    else:
        nh = int(w * 9 / 16); t = (h - nh) // 2; im = im.crop((0, t, w, t + nh))
    im = im.resize((1200, 675), Image.Resampling.LANCZOS)
    if IPP:
        im = IPP.add_phone_watermark(im)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=60, method=6)
    return buf.getvalue()


def generate_image(item, kind, mock=False):
    name = f"{item['slug']}-{kind}.webp"
    if mock:
        from PIL import Image
        buf = io.BytesIO(); Image.new('RGB', (1200, 675), (40 + kind * 30, 120, 60)).save(buf, 'WEBP'); blob = buf.getvalue()
    else:
        if not IMAGE_TOKEN: raise RuntimeError('IMAGE_API_KEY/AGNES_API_KEY is missing')
        extra = {'response_format': 'b64_json'}
        refs = reference_images(item, kind)
        if refs: extra['image'] = refs
        raw, last = None, None
        for k in range(1, 4):
            try:
                key = AGNES_KEYS[next(_KEYS) % len(AGNES_KEYS)] if AGNES_KEYS else IMAGE_TOKEN
                data = fetch_json(IMAGE_ENDPOINT, {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'navar-tj-ads-queue'},
                                  {'model': IMAGE_MODEL, 'prompt': image_prompt(item, kind), 'size': '1024x768', 'return_base64': True, 'extra_body': extra}, 600)
                row = data['data'][0]
                if row.get('b64_json'): raw = base64.b64decode(row['b64_json'])
                elif row.get('url'):
                    with urllib.request.urlopen(row['url'], timeout=180) as r: raw = r.read()
                else: raise RuntimeError('Image response has neither b64_json nor url')
                if len(raw) < 10000: raise RuntimeError('Generated image is unexpectedly small')
                break
            except Exception as e:
                last = e; raw = None
                print(f'image retry {k}/3: {str(e)[:200]}', flush=True); time.sleep(5 * k)
        if raw is None: raise RuntimeError('Image generation failed: ' + str(last))
        blob = to_webp(raw)
    (IMAGES / name).write_bytes(blob)
    return name, hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------- SQL

def contact_box():
    prod = cfg('products.json')
    ph = prod['company']['phone_display']
    s = prod['safe_commercial_statements_tg']
    return (f'<div class="navar-tj-contact"><p><strong>Тамос бо AFP:</strong> <a href="tel:{ph.replace(" ", "")}">{ph}</a> · '
            f'<a href="{SITE}/tg-tj-tamos/">саҳифаи тамос</a> · <a href="{SITE}/tg-tj-shakli-darhost/">шакли дархост</a></p><p>{" ".join(s)}</p></div>')


def render_body(item, obj, image_names):
    body = obj['html'].replace('[[[CONTACT_BOX]]]', contact_box())
    urls = []
    for i, (name, alt) in enumerate(zip(image_names, obj['image_alts']), 1):
        url = f'{SITE}/wp-content/uploads/{UPLOAD_DIR}/{name}'
        urls.append(url)
        body = body.replace(f'[[[IMAGE_{i}]]]', f'<figure class="wp-block-image size-large"><img src="{url}" alt="{html.escape(alt, quote=True)}" loading="lazy"/><figcaption>{html.escape(alt)}</figcaption></figure>')
    return body, urls


def ins_post(title, body, excerpt, slug, status, ptype, parent='0', mime='', guid=''):
    return (f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`,`to_ping`,`pinged`,`post_content_filtered`) "
            f"SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(body)}','{esc(title)}','{esc(excerpt)}','{status}','closed','closed','{esc(slug)}',NOW(),UTC_TIMESTAMP(),{parent},'{esc(guid)}',0,'{ptype}','{mime}',0,'','','' "
            f"FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM `{TABLE}` WHERE `post_name`='{esc(slug)}' AND `post_type`='{ptype}');")


def ins_attachment(alt, name, url):
    return (f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`,`to_ping`,`pinged`,`post_content_filtered`) "
            f"SELECT 1,NOW(),UTC_TIMESTAMP(),'','{esc(alt)}','','inherit','open','closed','{esc(name)}',NOW(),UTC_TIMESTAMP(),@pid,'{esc(url)}',0,'attachment','image/webp',0,'','','' "
            f"FROM DUAL WHERE @pid IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{TABLE}` WHERE `guid`='{esc(url)}');")


def ins_meta(var, key, val):
    return f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT {var},'{esc(key)}','{esc(val)}' FROM DUAL WHERE {var} IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE `post_id`={var} AND `meta_key`='{esc(key)}');"


def sql_for(item, obj, image_names):
    body, urls = render_body(item, obj, image_names)
    slug = item['slug']
    q = ['START TRANSACTION;', ins_post(item['title'], body, obj['excerpt'], slug, POST_STATUS, POST_TYPE),
         f"SET @pid := (SELECT `ID` FROM `{TABLE}` WHERE `post_name`='{esc(slug)}' AND `post_type`='{POST_TYPE}' ORDER BY `ID` LIMIT 1);"]
    meta = [('_rank_math_title', obj['meta_title']), ('_rank_math_description', obj['meta_description']), ('rank_math_focus_keyword', obj['focus_keyword']),
            ('_navar_translation_language', 'tg-TJ'), ('_navar_tj_ad', '1'), ('_navar_tj_place', item['place']), ('_navar_tj_place_name', item['place_tg']), ('_navar_tj_region', item['region']),
            ('_navar_tj_product', item['product']), ('_navar_tj_crop', item['crop'] or ''), ('_navar_tj_crop_evidence', item['crop_evidence']), ('_navar_tj_tier', item['tier']), ('_navar_tj_queue_id', item['id'])]
    q += [ins_meta('@pid', k, v) for k, v in meta]
    for i, (name, url) in enumerate(zip(image_names, urls), 1):
        alt = obj['image_alts'][i - 1]
        q.append(ins_attachment(alt, name.rsplit('.', 1)[0], url))
        q.append(f"SET @m{i} := (SELECT `ID` FROM `{TABLE}` WHERE `guid`='{esc(url)}' AND `post_type`='attachment' ORDER BY `ID` LIMIT 1);")
        q.append(ins_meta(f'@m{i}', '_wp_attached_file', f'{UPLOAD_DIR}/{name}'))
        rel = f'{UPLOAD_DIR}/{name}'
        q.append(ins_meta(f'@m{i}', '_wp_attachment_metadata', f'a:3:{{s:5:"width";i:1200;s:6:"height";i:675;s:4:"file";s:{len(rel.encode())}:"{rel}";}}'))
        q.append(ins_meta(f'@m{i}', '_wp_attachment_image_alt', alt))
    q.append(f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @pid,'_thumbnail_id',@m1 FROM DUAL WHERE @pid IS NOT NULL AND @m1 IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE `post_id`=@pid AND `meta_key`='_thumbnail_id');")
    q.append('COMMIT;')
    rb = ['START TRANSACTION;',
          f"SET @pid := (SELECT `ID` FROM `{TABLE}` WHERE `post_name`='{esc(slug)}' AND `post_type`='{POST_TYPE}' ORDER BY `ID` LIMIT 1);",
          f"DELETE FROM `{META}` WHERE `post_id` IN (SELECT `ID` FROM `{TABLE}` WHERE `post_parent`=@pid AND `post_type`='attachment') AND @pid IS NOT NULL;",
          f"DELETE FROM `{TABLE}` WHERE `post_parent`=@pid AND `post_type`='attachment' AND @pid IS NOT NULL;",
          f"DELETE FROM `{META}` WHERE `post_id`=@pid AND @pid IS NOT NULL;",
          f"DELETE FROM `{TABLE}` WHERE `ID`=@pid AND `post_type`='{POST_TYPE}' AND @pid IS NOT NULL;", 'COMMIT;']
    return '\n'.join(q) + '\n', '\n'.join(rb) + '\n', body


# ---------------------------------------------------------------- run

def process(q, only_place=None, tier=None, limit=None, mock=False):
    place_cfg = {p['slug']: p for p in cfg('places.json')['places']}
    products, gov, pool = cfg('products.json'), cfg('government_context.json'), cfg('link_pool.json')
    cand = [x for x in q['items'] if x['status'] == 'pending' and x['attempts'] < MAX_ATTEMPTS and (not only_place or x['place'] == only_place) and (not tier or x['tier'] == tier)]
    batch = cand[: (limit or BATCH)]
    if not batch:
        write_status(q, 'complete'); return
    for item in batch:
        item.update(status='processing', attempts=item['attempts'] + 1, started_at=now()); save(q)
        try:
            obj = make_content(item, place_cfg[item['place']], products, gov, pool, mock)
            names, hashes = [], []
            for k in range(1, IMAGES_PER_POST + 1):
                n, h = generate_image(item, k, mock); names.append(n); hashes.append(h)
                if not mock: time.sleep(2)
            ins, rb, body = sql_for(item, obj, names)
            (SQL / f"{item['id']}.sql").write_text(ins, encoding='utf-8'); (ROLLBACK / f"{item['id']}.sql").write_text(rb, encoding='utf-8')
            (ITEMS / f"{item['id']}.json").write_text(json.dumps({**item, **{k: v for k, v in obj.items() if k != 'html'}, 'html': body, 'images': names, 'image_sha256': hashes}, ensure_ascii=False, indent=1), encoding='utf-8')
            item.update(status='completed', completed_at=now(), word_count=words(body), images=names, last_error='')
        except Exception as e:
            msg = str(e)[:900]
            blocked = ('IMAGE_API_KEY' in msg or 'HTTP 401' in msg or 'HTTP 403' in msg)
            item.update(status='blocked_image_model' if blocked else 'failed', failed_at=now(), last_error=msg)
            save(q)
            if blocked:
                write_status(q, 'blocked_image_model'); raise
        save(q); write_status(q, 'processing')
    (OUT / 'create-all-completed.sql').write_text('-- Review before import. Posts are inserted as ' + POST_STATUS + '.\nSET NAMES utf8mb4;\n' + '\n'.join(p.read_text(encoding='utf-8') for p in sorted(SQL.glob('*.sql'))), encoding='utf-8')
    (OUT / 'rollback-all-completed.sql').write_text('SET NAMES utf8mb4;\n' + '\n'.join(p.read_text(encoding='utf-8') for p in sorted(ROLLBACK.glob('*.sql'))), encoding='utf-8')
    write_status(q, 'ready')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--init-only', action='store_true'); ap.add_argument('--force-init', action='store_true')
    ap.add_argument('--mock', action='store_true', help='offline dry-run with fake text/images'); ap.add_argument('--limit', type=int)
    ap.add_argument('--only-place'); ap.add_argument('--tier', choices=['A', 'B', 'C'])
    a = ap.parse_args()
    q = initialize(a.force_init)
    if a.init_only:
        print(f"queue ready: {len(q['items'])} items"); return
    process(q, a.only_place, a.tier, a.limit, a.mock)


if __name__ == '__main__':
    main()
