#!/usr/bin/env python3
"""Tajikistan ad posts - same flow as maghala2's article/translation queues.

 1. Persian source article (Agnes writes Persian well)  -> never published, kept in items/<id>.json
 2. Tajik (Cyrillic) + Russian translations of that source (maghala2 translate_queue segment translator + glossary)
 3. 3 images per post (shared by both languages)
 4. SQL (+ ROLLBACK): two ordinary WordPress posts (post_type=post, status=publish) in their own categories
    (tajikistan-ads-tg / tajikistan-ads-ru) which are NOT part of the article categories.
 5. ZIP packages of PACKAGE_SIZE posts (default 50) by package_batches.py
"""
import argparse, html, json, random, re, sys, time, urllib.parse
from pathlib import Path

import ads_queue as A

try:
    import translate_queue as TQ          # maghala2/automation (repo root)
except Exception as _e:                   # standalone / mock
    TQ = None
    print('translate_queue not importable (mock only):', str(_e)[:150], flush=True)

ROOT, SITE, cfg, esc = A.ROOT, A.SITE, A.cfg, A.esc
I18N = cfg('i18n.json')
LANGS = {
    'tg-TJ': {'suffix': 'tg', 'cat_slug': 'tajikistan-ads-tg', 'cat_name': 'Тоҷикистон: лентаи обёрии қатрагӣ', 'label': 'natural Tajik in Cyrillic script suitable for Tajik farmers'},
    'ru-RU': {'suffix': 'ru', 'cat_slug': 'tajikistan-ads-ru', 'cat_name': 'Таджикистан: капельный полив', 'label': 'natural Russian suitable for farmers and irrigation professionals in Tajikistan'},
}
PWORD = re.compile(r'[\u0600-\u06ff\u200c]+')
RU_PILLAR = f"{SITE}/{I18N['pillar']['ru_slug']}/"
TG_PILLAR = cfg('link_pool.json')['pillar']['url']
TG_ONLY = re.compile(r'[ҒғӢӣҚқӮӯҲҳҶҷ]')
MIN_FA = A.MIN_WORDS
MIN_TR = int(__import__('os').getenv('MIN_TRANSLATED_WORDS', '900'))
TARGET = A.TARGET_WORDS
LANG_MODEL = {'tg-TJ': __import__('os').getenv('TG_MODEL', 'agnes-2.5-flash'), 'ru-RU': __import__('os').getenv('RU_MODEL', 'agnes-3.0-flash')}   # probe: 2.5-flash writes clearly better Tajik, 3.0-flash cleaner Russian
MAXTRY_SRC = 5
MAXTRY_TR = 3
DBG = A.OUT / 'debug'


def pwords(t): return len(PWORD.findall(re.sub(r'<[^>]+>', ' ', t or '')))
def plain(t): return re.sub(r'<[^>]+>', ' ', t or '')


# ------------------------------------------------------------------ Persian source
def titles_i18n(item):
    t = json.loads((ROOT / 'data/titles_i18n.json').read_text(encoding='utf-8')).get(item['id'])
    if not t: raise RuntimeError(f"no Persian/Russian title for {item['id']} in data/titles_i18n.json")
    return t


def pool_for(item):
    pl = A.pick_pool(item, cfg('link_pool.json'), random.Random(item['id']))
    out = []
    for x in pl:
        key = x['url'].replace(SITE, '')
        fa = I18N['link_titles'].get(key, {}).get('fa') or I18N['pillar']['fa']
        out.append({**x, 'fa': fa})
    return out


def build_prompt_fa(item, place, products, links, tt):
    pi = I18N['products'][item['product']]
    pf = I18N['places'][item['place']]['fa']; kind = 'شهر' if item['kind'] == 'city' else 'ناحیه'
    region = I18N['regions'][item['region']]['fa']; zone = I18N['zone_label'][item['zone']]['fa']
    crop_fa = I18N['crops'][item['crop']]['fa'] if item['crop'] else ''
    facts = I18N['place_facts'].get(item['place'], {}).get('fa')
    crop_line = ''
    if item['crop']:
        ev = next(c for c in place['crops'] if c['crop'] == item['crop'])['evidence']
        crop_line = I18N['crop_context_fa'][ev].format(fact=facts or '—', zone=zone)
    seed = random.Random(item['id']).choice(I18N['coop_seeds_fa'])
    ll = '\n'.join(f"L{i} = {x['fa']}" for i, x in enumerate(links, 1))
    return f'''برای مقاله‌ی تبلیغاتی ـ آموزشی با عنوان «{tt['fa']}» یک مقاله‌ی سئوشده و کاربردی به فارسی روان بنویس. مخاطب کشاورزان تاجیکستان‌اند و متن بعداً به تاجیکی و روسی ترجمه می‌شود؛ پس جمله‌ها ساده و روشن باشند، بدون ضرب‌المثل و اصطلاح ایرانی.
محل: {kind} {pf} ({region})؛ پهنه‌ی کشاورزی: {zone}.
محصول: {pi['fa']}. واقعیت‌های مجاز درباره‌ی محصول: {'؛ '.join(pi['facts_fa'])}.
محصول زراعی: {crop_fa or '(محصول مشخصی نیست؛ درباره‌ی محصولات ردیفی به‌طور کلی بنویس)'}. {crop_line}
واقعیت‌های تأییدشده درباره‌ی محل (فقط همین‌ها را می‌شود به‌عنوان واقعیت درباره‌ی محل گفت): {facts or '(هیچ عدد یا آمار خاصی برای این محل وجود ندارد؛ از خودت نساز)'}

قوانین سخت
۱) فقط HTML با h2/h3/p/ul/ol/li/table/strong/details/summary. بدون H1 و بدون تکرار عنوان در متن. هدف حدود {TARGET} کلمه (حداقل قطعی {MIN_FA}). هر بخش h2 باید ۲ تا ۴ پاراگراف مفصل و عملی داشته باشد. جمله‌ها را تکراری شروع نکن.
۲) فقط محصولات ردیفی؛ از باغ، تاکستان و گلخانه حرف نزن. نگو این محصول «محصول اصلی» محل است، مگر در واقعیت‌های تأییدشده آمده باشد.
۳) هرگز جعل نکن؛ هیچ بازه یا مقدار عددی (فاصله قطره‌چکان، فشار، دبی، درصد، ساعت، روز، مقدار آب و ...) ننویس و فقط ابعاد موجود در عنوان محصولات (مثل ۲۰ سانتی‌متر، ۱۰۰۰ متر) مجاز است: قیمت، تخفیف، عملکرد، آمار، تاریخ، جایزه، گواهینامه، نمایندگی/انبار/مرکز خدمات در تاجیکستان، ارسال رایگان یا محلی، تأیید یا حمایت دولت. هیچ عددی همراه واحد پول ننویس و از رئیس‌جمهور نام نبر.
۴) نکته‌ی تجاری: قیمت و شرایط خرید با تماس تلفنی یا فرم توافق می‌شود؛ محصول گارانتی دارد ولی خدمات پس از فروش و شرایط ارسال به تاجیکستان جداگانه توافق می‌شود. نشانگر [[[CONTACT_BOX]]] را دقیقاً یک بار در یک خط جدا بگذار (اسکریپت تلفن را جایگزین می‌کند).
۵) در بخش همکاری یک پاراگراف کوتاه (۲ تا ۳ جمله) هم‌روح این جمله ولی کاملاً بازنویسی‌شده بنویس: «{seed}». این پاراگراف باید لینک [[L1|متن طبیعی]] را داشته باشد. هیچ حرفی را به رئیس‌جمهور یا دولت نسبت نده.
۶) ساختار: مقدمه (محل + محصول + محصول زراعی) ← [[[IMAGE_1]]] ← h2 چرا/کی این محصول به این محصول زراعی می‌خورد ← h2 چگونه انتخاب کنیم (یک جدول کوچک معیارهای کلی، بدون شماره‌ی کاتالوگ نامطمئن) ← [[[IMAGE_2]]] ← h2 نصب و نگهداری (فهرست شماره‌دار) ← h2 صرفه‌جویی آب و روش کار در مزرعه (بدون داده‌ی محلی ساختگی) ← h2 همکاری (قانون ۵) ← [[[CONTACT_BOX]]] ← [[[IMAGE_3]]] ← پرسش‌های متداول: دقیقاً ۳ پرسش، هرکدام به شکل <details class="navar-faq"><summary><h3>پرسش</h3></summary><div><p>پاسخ</p></div></details> ← در پایان <h2>مطالب مرتبط</h2><ul> با لینک‌های مرتبط.
۷) لینک‌ها: هرگز URL یا تگ <a> ننویس. برای لینک فقط از نشانگر [[L<شماره>|متن لینک]] با شماره‌های همین فهرست استفاده کن. بین {A.MIN_LINKS} تا {A.MAX_LINKS} نشانگر متفاوت به‌کار ببر و [[L1|...]] اجباری است:
{ll}
۸) فقط JSON معتبر با کلیدهای html، excerpt (حداکثر ۱۶۰ نویسه)، meta_title (حداکثر ۶۰ نویسه)، meta_description (حداکثر ۱۵۵ نویسه)، focus_keyword (۲ تا ۴ کلمه) و image_alts (آرایه‌ی ۳ متن کوتاه برای توضیح تصویر).'''


def limit_links(body, mx):
    """Keep the pillar + the first (mx-1) distinct links; unwrap the rest (maghala2 keeps 4-7 links)."""
    order = []
    for m in re.finditer(r'<a\b[^>]*href=["\']([^"\']+)', body, re.I):
        u = A.urlnorm(m.group(1))
        if 'navar-abyari.ir' in u and u not in order: order.append(u)
    pil = A.urlnorm(TG_PILLAR)
    keep = ([pil] if pil in order else []) + [u for u in order if u != pil]
    keep = set(keep[:mx])
    def f(m):
        h = re.search(r'href=["\']([^"\']+)', m.group(1), re.I)
        return m.group(0) if (not h or A.urlnorm(h.group(1)) in keep or 'navar-abyari.ir' not in h.group(1)) else m.group(2)
    return re.sub(r'(<a\b[^>]*>)(.*?)</a>', lambda m: f(m) if False else (m.group(0) if (lambda h: (not h) or A.urlnorm(h.group(1)) in keep or 'navar-abyari.ir' not in h.group(1))(re.search(r'href=["\']([^"\']+)', m.group(1), re.I)) else m.group(2)), body, flags=re.S | re.I)


def ensure_markers(body):
    """Same idea as maghala2 ensure_image_markers: repair, don't reject."""
    for tag in ('[[[IMAGE_1]]]', '[[[IMAGE_2]]]', '[[[IMAGE_3]]]', '[[[CONTACT_BOX]]]'):
        n = body.count(tag)
        if n > 1:
            first = body.index(tag) + len(tag)
            body = body[:first] + body[first:].replace(tag, '')
    h2 = [m.start() for m in re.finditer(r'<h2\b', body)]
    def put(tag, pos):
        nonlocal body
        if tag not in body: body = body[:pos] + tag + body[pos:]
    if len(h2) >= 4:
        put('[[[IMAGE_1]]]', h2[0]); h2 = [m.start() for m in re.finditer(r'<h2\b', body)]
        put('[[[IMAGE_2]]]', h2[min(2, len(h2) - 1)]); h2 = [m.start() for m in re.finditer(r'<h2\b', body)]
    d = body.find('<details')
    if d > 0:
        put('[[[CONTACT_BOX]]]', d)
        put('[[[IMAGE_3]]]', body.find('<details'))
    return body


def validate_fa(obj, item, allowed):
    body = obj.get('html', ''); txt = plain(body); bad = []
    pf = I18N['places'][item['place']]['fa']
    if pwords(body) < MIN_FA: bad.append(f'words {pwords(body)} < {MIN_FA}')
    used = {A.urlnorm(u) for u in A.internal_links(body)}
    if not (A.MIN_LINKS <= len(used) <= A.MAX_LINKS): bad.append(f'links {len(used)} not in {A.MIN_LINKS}-{A.MAX_LINKS}')
    if used - {A.urlnorm(u) for u in allowed}: bad.append('link outside approved pool')
    if A.urlnorm(TG_PILLAR) not in used: bad.append('pillar link missing')
    for t in ('[[[IMAGE_1]]]', '[[[IMAGE_2]]]', '[[[IMAGE_3]]]', '[[[CONTACT_BOX]]]'):
        if body.count(t) != 1: bad.append(f'{t} count')
    if len(re.findall(r'<details\b', body)) != 3: bad.append('FAQ must be exactly 3 <details>')
    if re.search(r'<h1\b', body, re.I): bad.append('H1 not allowed')
    if len(re.findall(r'<h2\b', body, re.I)) < 4: bad.append('need >=4 h2')
    latin = [w for w in A.LATIN_WORD_RE.findall(txt) if w not in ('AFP', 'PE', 'LIF')]
    if latin: bad.append('Latin words: ' + ','.join(latin[:5]))
    if A.PRICE_RE.search(txt) or re.search(r'\d[\d\s.,٫٬]*\s*(تومان|ریال|دلار|سامانی|سومونی|روبل)', txt): bad.append('price-like text')
    for ph in I18N['forbidden_fa']:
        if ph in txt: bad.append('forbidden: ' + ph)
    if item['crop'] and I18N['crops'][item['crop']]['fa'] not in txt: bad.append('crop name missing')
    if pf not in txt: bad.append('place name missing')
    if item['place'] not in I18N['place_facts']:      # no verified numbers for this place -> no invented measurements
        t2 = txt.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٫٬', '0123456789.,'))
        if re.search(r'\d+\s*(?:[-–تا]|الی)\s*\d+', t2) or re.search(r'\d+\s*(?:بار|لیتر|درصد|%|٪|درجه|ساعت|دقیقه|روز|هفته|ماه|کیلو|تن|هکتار|متر مکعب|اتمسفر)', t2): bad.append('invented numbers/ranges (only numbers from product titles are allowed)')
    for k in ('excerpt', 'meta_title', 'meta_description', 'focus_keyword'):
        if not obj.get(k): bad.append('missing ' + k)
    if len(obj.get('image_alts', [])) != 3: bad.append('need 3 image_alts')
    return bad


def agnes_fa(prompt):
    last = None
    for k in range(1, 4):
        try:
            key = A.AGNES_KEYS[next(A._KEYS) % len(A.AGNES_KEYS)]
            data = A.fetch_json(A.AGNES_BASE + '/chat/completions', {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'User-Agent': 'navar-tj-ads-queue'},
                                {'model': A.AGNES_MODEL, 'messages': [{'role': 'system', 'content': 'تو سردبیر حرفه‌ای فارسی در حوزه آبیاری کشاورزی هستی. فقط JSON معتبر برگردان.'}, {'role': 'user', 'content': prompt}],
                                 'temperature': 0.5 if k == 1 else 0.3, 'max_tokens': 20000}, timeout=min(420, 240 + 60 * (k - 1)))
            return A.parse_object(data.get('choices', [{}])[0].get('message', {}).get('content', ''))
        except Exception as e:
            last = e; print(f'agnes retry {k}/3: {str(e)[:200]}', flush=True); time.sleep(min(20, 2 ** k))
    raise RuntimeError('Agnes failed: ' + str(last))


def mock_fa(item, links):
    ph = lambda i, t: f'[[L{i}|{t}]]'
    para = lambda n: '<p>' + ' '.join(['آبیاری قطره‌ای در مزرعه رودکی پنبه آب کشاورز نصب فشار فیلتر'] * n) + '</p>'
    h = f"<p>مقدمه {I18N['places'][item['place']]['fa']} {I18N['crops'].get(item['crop'], {'fa': ''})['fa']} {ph(1, 'همکاری')}</p>[[[IMAGE_1]]]"
    h += ''.join(f'<h2>بخش {i}</h2>' + para(40) + para(40) for i in range(1, 6)) + f"<p>{ph(2, 'تماس')} {ph(3, 'گارانتی')} {ph(4, 'قوانین')}</p>[[[CONTACT_BOX]]][[[IMAGE_2]]][[[IMAGE_3]]]"
    h += ''.join('<details class="navar-faq"><summary><h3>پرسش؟</h3></summary><div><p>پاسخ</p></div></details>' for _ in range(3))
    h += '<h2>مطالب مرتبط</h2><ul><li>' + ph(5, 'محصول') + '</li></ul>'
    return {'html': h, 'excerpt': 'خلاصه', 'meta_title': 'عنوان سئو', 'meta_description': 'توضیح', 'focus_keyword': 'نوار قطره‌ای', 'image_alts': ['تصویر یک', 'تصویر دو', 'تصویر سه']}


def make_source(item, place, products, mock=False):
    tt = titles_i18n(item); links = pool_for(item); allowed = [x['url'] for x in links]
    base = build_prompt_fa(item, place, products, links, tt); prompt = base; obj = None; hist = []
    for attempt in range(1, MAXTRY_SRC + 1):
        new = mock_fa(item, links) if mock else agnes_fa(prompt)
        if isinstance(new, dict) and new.get('html'): obj = new
        if obj is None: continue
        body = A.resolve_links(obj['html'], links)
        body = ensure_markers(limit_links(re.sub(r'<h1\b[^>]*>.*?</h1>', '', body, flags=re.S), A.MAX_LINKS))
        obj['html'] = body
        bad = validate_fa(obj, item, allowed)
        hist.append({'attempt': attempt, 'words': pwords(body), 'problems': bad})
        print(f"  source attempt {attempt}: {pwords(body)} words, problems={bad}", flush=True)
        if not bad: return obj, tt
        prompt = (base + '\n\nپیش‌نویس قبلی (لینک‌ها حل شده‌اند؛ بخش‌های خوب را نگه دار):\n' + body[:32000] + '\n\nکنترل کیفیت رد کرد: ' + '؛ '.join(bad) +
                  f'.\nکل JSON را دوباره و کامل برگردان. اگر تعداد کلمات کم است همه‌ی بخش‌ها را با جزئیات عملی گسترش بده تا به حدود {TARGET} کلمه برسد. نشانگرهای [[L<n>|...]] و [[[...]]] را حفظ کن.')
    DBG.mkdir(parents=True, exist_ok=True)
    (DBG / f"{item['id']}.json").write_text(json.dumps({'history': hist, 'last_html': obj['html'] if obj else ''}, ensure_ascii=False, indent=1), encoding='utf-8')
    raise RuntimeError('Persian source QA failed: ' + '; '.join(hist[-1]['problems']))


# ------------------------------------------------------------------ translation
def set_labels(item=None, place=None, lang=None):
    if not TQ: return
    extra = {}
    if item and place:
        fa = I18N['places'][item['place']]['fa']; zf = I18N['zone_label'][item['zone']]['fa']
        extra['tg-TJ'] = f" Names that must be rendered EXACTLY: {fa} = {place['name_tg']}; \"{zf}\" = \"{place['zone_label_tg']}\"."
        extra['ru-RU'] = f" Names that must be rendered EXACTLY: {fa} = {I18N['places'][item['place']]['ru']}; \"{zf}\" = \"{I18N['zone_label'][item['zone']]['ru']}\"."
    TQ.language_label = lambda lg: LANGS[lg]['label'] + '. ' + I18N['glossary'][lg] + extra.get(lg, '')
    if lang: TQ.MODEL = LANG_MODEL[lang]


def trim(s, n):
    s = str(s).strip()
    if len(s) <= n: return s
    cut = s[:n].rsplit(' ', 1)[0].rstrip(' ,;:-—')
    return cut or s[:n]


def translate_fields(obj, lang, mock=False):
    if mock:
        w = 'Матни санҷишӣ' if lang == 'tg-TJ' else 'Тестовый текст'
        return {'excerpt': w, 'meta_title': w, 'meta_description': w, 'focus_keyword': w, 'image_alts': [f'{w} {i}' for i in (1, 2, 3)]}
    src = {k: obj[k] for k in ('excerpt', 'meta_title', 'meta_description', 'focus_keyword', 'image_alts')}
    prompt = (f"Translate these Persian SEO fields into {TQ.language_label(lang)}. Return valid JSON only with the same keys "
              f"(excerpt <=160 chars, meta_title <=60 chars, meta_description <=155 chars, focus_keyword 2-4 words, image_alts = array of exactly 3 short texts). Keep AFP. No HTML.\n{json.dumps(src, ensure_ascii=False)}")
    last = None
    for k in range(3):
        try:
            r = TQ.call_chat([{'role': 'system', 'content': 'You are a precise SEO localization editor. Output valid JSON only.'}, {'role': 'user', 'content': prompt}], max_tokens=2500)
            if not isinstance(r.get('image_alts'), list) or len(r['image_alts']) != 3: raise ValueError('image_alts must have 3 items')
            for key in ('excerpt', 'meta_title', 'meta_description', 'focus_keyword'):
                if not r.get(key): raise ValueError('missing ' + key)
            r['meta_title'] = trim(r['meta_title'], 60); r['meta_description'] = trim(r['meta_description'], 155); r['excerpt'] = trim(r['excerpt'], 160)
            return r
        except Exception as e:
            last = e; print(f'fields attempt {k + 1} failed: {str(e)[:150]}', flush=True); time.sleep(4 * (k + 1))
    raise RuntimeError(f'field translation failed for {lang}: {last}')


def mock_translate_html(src, lang):
    w = 'Ин матни санҷишӣ барои ҷараёни кор аст ' if lang == 'tg-TJ' else 'Это тестовый текст для проверки процесса '
    return re.sub(r'>([^<>]*[\u0600-\u06ff][^<>]*)<', lambda m: '>' + (w * max(1, len(m.group(1)) // 40)) + '<', src)


def qc_translation(html_t, lang, src_html, minw):
    bad = []; txt = re.sub(r'\[\[\[[A-Z_0-9]+\]\]\]', ' ', plain(html_t))
    if TQ:
        a, b = TQ.counts(src_html), TQ.counts(html_t)
        for tag in ('h2', 'h3', 'ul', 'ol', 'li', 'a', 'table', 'tr', 'td', 'details', 'summary'):
            if a.get(tag, 0) != b.get(tag, 0): bad.append(f'HTML count {tag}: {a.get(tag, 0)}->{b.get(tag, 0)}')
    for t in ('[[[IMAGE_1]]]', '[[[IMAGE_2]]]', '[[[IMAGE_3]]]', '[[[CONTACT_BOX]]]'):
        if html_t.count(t) != 1: bad.append(f'{t} count')
    if A.ARABIC_RE.search(txt): bad.append('untranslated Persian/Arabic letters remain: ' + ''.join(sorted(set(A.ARABIC_RE.findall(txt))))[:20])
    rest = re.sub(r'\b(?:AFP|PE|LIF|layflat)\b', ' ', txt)
    latin = re.findall(r'[A-Za-z]+', rest)
    if latin: bad.append('Latin letters inside translated text (mixed-script garbage): ' + ','.join(latin[:6]))
    n = A.words(html_t)
    if n < minw: bad.append(f'words {n} < {minw}')
    if lang == 'tg-TJ' and A.RUSSIAN_ONLY.search(txt): bad.append('Russian-only letters/words in Tajik text')
    if lang == 'ru-RU':
        if TG_ONLY.search(txt): bad.append('Tajik-only letters in Russian text: ' + ''.join(sorted(set(TG_ONLY.findall(txt)))))
    for u in A.internal_links(src_html):
        want = RU_PILLAR if (lang == 'ru-RU' and A.urlnorm(u) == A.urlnorm(TG_PILLAR)) else u
        if A.urlnorm(want) not in {A.urlnorm(x) for x in A.internal_links(html_t)}: bad.append('link lost: ' + u[-30:])
    if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]', txt): bad.append('CJK characters in translation')
    if A.PRICE_RE.search(txt): bad.append('price-like text')
    return bad


def translate_post(obj, item, lang, tt, mock=False, place=None):
    set_labels(item, place, lang); minw = 100 if mock else MIN_TR; last = []
    for k in range(1, MAXTRY_TR + 1):
        html_t = mock_translate_html(obj['html'], lang) if mock else TQ.translate_html(obj['html'], lang)
        if lang == 'ru-RU': html_t = html_t.replace(TG_PILLAR, RU_PILLAR)
        last = qc_translation(html_t, lang, obj['html'] if lang == 'tg-TJ' else obj['html'], minw)
        print(f"  {lang} attempt {k}: {A.words(html_t)} words, problems={last}", flush=True)
        if not last: break
    else:
        DBG.mkdir(parents=True, exist_ok=True)
        (DBG / f"{item['id']}-{LANGS[lang]['suffix']}.html").write_text(html_t, encoding='utf-8')
        raise RuntimeError(f'{lang} translation QA failed: ' + '; '.join(last))
    f = translate_fields(obj, lang, mock)
    title = item['title'] if lang == 'tg-TJ' else tt['ru']
    slug = item['slug'] if lang == 'tg-TJ' else translit(tt['ru'])
    return {'lang': lang, 'title': title, 'slug': slug, 'html': html_t, **f}


RU_MAP = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a','b','v','g','d','e','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya']))
def translit(s):
    t = ''.join(RU_MAP.get(c, c) for c in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:80]


# ------------------------------------------------------------------ rendering + SQL
def contact_box(lang):
    if lang == 'tg-TJ': return A.contact_box()
    ph = A.cfg('products.json')['company']['phone_display']; c = I18N['contact_ru']
    return (f'<div class="navar-tj-contact"><p><strong>{c["label"]}</strong> <a href="tel:{ph.replace(" ", "")}">{ph}</a> · '
            f'<a href="{SITE}/tg-tj-tamos/">{c["contact"]}</a> · <a href="{SITE}/tg-tj-shakli-darhost/">{c["form"]}</a></p><p>{" ".join(c["statements"])}</p></div>')


def render(post, names):
    body = post['html'].replace('[[[CONTACT_BOX]]]', contact_box(post['lang']))
    urls = []
    for i, (n, alt) in enumerate(zip(names, post['image_alts']), 1):
        u = f'{SITE}/wp-content/uploads/{A.UPLOAD_DIR}/{n}'; urls.append(u)
        body = body.replace(f'[[[IMAGE_{i}]]]', f'<figure class="wp-block-image size-large"><img src="{u}" alt="{html.escape(alt, quote=True)}" loading="lazy"/><figcaption>{html.escape(alt)}</figcaption></figure>')
    return body, urls


T, M = A.TABLE, A.META
TERMS, TAX, REL = (T.replace('posts', x) for x in ('terms', 'term_taxonomy', 'term_relationships'))


def category_sql(var, slug, name):
    return [f"INSERT INTO `{TERMS}` (`name`,`slug`,`term_group`) SELECT '{esc(name)}','{slug}',0 FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM `{TERMS}` WHERE `slug`='{slug}');",
            f"SET @t := (SELECT `term_id` FROM `{TERMS}` WHERE `slug`='{slug}' ORDER BY `term_id` LIMIT 1);",
            f"INSERT INTO `{TAX}` (`term_id`,`taxonomy`,`description`,`parent`,`count`) SELECT @t,'category','',0,0 FROM DUAL WHERE @t IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{TAX}` WHERE `term_id`=@t AND `taxonomy`='category');",
            f"SET @tt := (SELECT `term_taxonomy_id` FROM `{TAX}` WHERE `term_id`=@t AND `taxonomy`='category' ORDER BY `term_taxonomy_id` LIMIT 1);",
            f"INSERT INTO `{REL}` (`object_id`,`term_taxonomy_id`,`term_order`) SELECT {var},@tt,0 FROM DUAL WHERE {var} IS NOT NULL AND @tt IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{REL}` WHERE `object_id`={var} AND `term_taxonomy_id`=@tt);",
            f"UPDATE `{TAX}` SET `count`=(SELECT COUNT(*) FROM `{REL}` WHERE `term_taxonomy_id`=@tt) WHERE `term_taxonomy_id`=@tt;"]


def sql_pair(item, posts, names):
    q = ['START TRANSACTION;']; rb = ['START TRANSACTION;']; first = True; thumbs = None
    for post in posts:
        lang = post['lang']; L = LANGS[lang]; v = '@p_' + L['suffix']
        body, urls = render(post, names)
        post['body'] = body
        q.append(A.ins_post(post['title'], body, post['excerpt'], post['slug'], 'publish', 'post'))
        q.append(f"SET {v} := (SELECT `ID` FROM `{T}` WHERE `post_name`='{esc(post['slug'])}' AND `post_type`='post' ORDER BY `ID` LIMIT 1);")
        q.append(f"SET @pid := {v};")
        meta = [('_rank_math_title', post['meta_title']), ('_rank_math_description', post['meta_description']), ('rank_math_focus_keyword', post['focus_keyword']),
                ('_navar_tj_ad', '1'), ('_navar_tj_lang', lang), ('_navar_tj_queue_id', item['id']), ('_navar_tj_place', item['place']), ('_navar_tj_place_name', item['place_tg']),
                ('_navar_tj_product', item['product']), ('_navar_tj_crop', item['crop'] or ''), ('_navar_tj_crop_evidence', item['crop_evidence']), ('_navar_tj_tier', item['tier'])]
        q += [A.ins_meta(v, k, val) for k, val in meta]
        q += category_sql(v, L['cat_slug'], L['cat_name'])
        if first:
            for i, (n, u) in enumerate(zip(names, urls), 1):
                alt = post['image_alts'][i - 1]; rel = f'{A.UPLOAD_DIR}/{n}'
                q.append(A.ins_attachment(alt, n.rsplit('.', 1)[0], u))
                q.append(f"SET @m{i} := (SELECT `ID` FROM `{T}` WHERE `guid`='{esc(u)}' AND `post_type`='attachment' ORDER BY `ID` LIMIT 1);")
                q.append(A.ins_meta(f'@m{i}', '_wp_attached_file', rel))
                q.append(A.ins_meta(f'@m{i}', '_wp_attachment_metadata', f'a:3:{{s:5:"width";i:1200;s:6:"height";i:675;s:4:"file";s:{len(rel.encode())}:"{rel}";}}'))
                q.append(A.ins_meta(f'@m{i}', '_wp_attachment_image_alt', alt))
            first = False
        q.append(f"INSERT INTO `{M}` (`post_id`,`meta_key`,`meta_value`) SELECT {v},'_thumbnail_id',@m1 FROM DUAL WHERE {v} IS NOT NULL AND @m1 IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{M}` WHERE `post_id`={v} AND `meta_key`='_thumbnail_id');")
    q.append('COMMIT;')
    for post in posts:
        L = LANGS[post['lang']]; v = '@p_' + L['suffix']
        rb += [f"SET {v} := (SELECT `ID` FROM `{T}` WHERE `post_name`='{esc(post['slug'])}' AND `post_type`='post' AND `ID` IN (SELECT `post_id` FROM `{M}` WHERE `meta_key`='_navar_tj_queue_id' AND `meta_value`='{esc(item['id'])}') ORDER BY `ID` LIMIT 1);",
               f"DELETE FROM `{REL}` WHERE `object_id`={v} AND {v} IS NOT NULL;"]
    first_var = '@p_' + LANGS[posts[0]['lang']]['suffix']
    rb += [f"DELETE FROM `{M}` WHERE `post_id` IN (SELECT `ID` FROM `{T}` WHERE `post_parent`={first_var} AND `post_type`='attachment') AND {first_var} IS NOT NULL;",
           f"DELETE FROM `{T}` WHERE `post_parent`={first_var} AND `post_type`='attachment' AND {first_var} IS NOT NULL;"]
    for post in posts:
        v = '@p_' + LANGS[post['lang']]['suffix']
        rb += [f"DELETE FROM `{M}` WHERE `post_id`={v} AND {v} IS NOT NULL;", f"DELETE FROM `{T}` WHERE `ID`={v} AND `post_type`='post' AND {v} IS NOT NULL;"]
    for L in LANGS.values():
        rb.append(f"UPDATE `{TAX}` SET `count`=(SELECT COUNT(*) FROM `{REL}` WHERE `term_taxonomy_id`=`{TAX}`.`term_taxonomy_id`) WHERE `term_id` IN (SELECT `term_id` FROM `{TERMS}` WHERE `slug`='{L['cat_slug']}');")
    rb.append('COMMIT;')
    return '\n'.join(q) + '\n', '\n'.join(rb) + '\n'


# ------------------------------------------------------------------ run
def produce(item, place, products, mock=False):
    print(f"== {item['id']}: {item['title']}", flush=True)
    src, tt = make_source(item, place, products, mock)
    posts = [translate_post(src, item, lang, tt, mock, place) for lang in LANGS]
    names, hashes = [], []
    for k in range(1, A.IMAGES_PER_POST + 1):
        n, h = A.generate_image(item, k, mock); names.append(n); hashes.append(h)
        if not mock: time.sleep(2)
    ins, rb = sql_pair(item, posts, names)
    (A.SQL / f"{item['id']}.sql").write_text(ins, encoding='utf-8'); (A.ROLLBACK / f"{item['id']}.sql").write_text(rb, encoding='utf-8')
    rec = {**item, 'title_fa': tt['fa'], 'source_fa': src, 'images': names, 'image_sha256': hashes,
           'posts': [{k: v for k, v in p.items() if k != 'html'} | {'url': f"{SITE}/{p['slug']}/"} for p in posts]}
    (A.ITEMS / f"{item['id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding='utf-8')
    return {'words_tg': A.words(posts[0]['body']), 'words_ru': A.words(posts[1]['body']), 'images': names}


def process(q, only_place=None, tier=None, limit=None, mock=False, only_id=None):
    place_cfg = {p['slug']: p for p in cfg('places.json')['places']}; products = cfg('products.json')
    i18n_titles = json.loads((ROOT / 'data/titles_i18n.json').read_text(encoding='utf-8'))
    cand = [x for x in q['items'] if x['status'] == 'pending' and x['attempts'] < A.MAX_ATTEMPTS and x['id'] in i18n_titles
            and (not only_id or x['id'] == only_id) and (not only_place or x['place'] == only_place) and (not tier or x['tier'] == tier)]
    batch = cand[: (limit or A.BATCH)]
    if not batch:
        A.write_status(q, 'complete'); print('nothing to do (items need Persian/Russian titles in data/titles_i18n.json)'); return
    for item in batch:
        item.update(status='processing', attempts=item['attempts'] + 1, started_at=A.now()); A.save(q)
        try:
            r = produce(item, place_cfg[item['place']], products, mock)
            item.update(status='completed', completed_at=A.now(), word_count=r['words_tg'], word_count_ru=r['words_ru'], images=r['images'], last_error='')
        except Exception as e:
            msg = str(e)[:900]; blocked = ('IMAGE_API_KEY' in msg or 'HTTP 401' in msg or 'HTTP 403' in msg)
            item.update(status='blocked_image_model' if blocked else 'failed', failed_at=A.now(), last_error=msg); print('FAILED:', msg, flush=True)
            A.save(q)
            if blocked: A.write_status(q, 'blocked_image_model'); raise
        A.save(q); A.write_status(q, 'processing')
    (A.OUT / 'create-all-completed.sql').write_text('-- Review before import. Posts are inserted as PUBLISHED.\nSET NAMES utf8mb4;\n' + '\n'.join(p.read_text(encoding='utf-8') for p in sorted(A.SQL.glob('*.sql'))), encoding='utf-8')
    (A.OUT / 'rollback-all-completed.sql').write_text('SET NAMES utf8mb4;\n' + '\n'.join(p.read_text(encoding='utf-8') for p in sorted(A.ROLLBACK.glob('*.sql'))), encoding='utf-8')
    A.write_status(q, 'ready')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mock', action='store_true'); ap.add_argument('--limit', type=int); ap.add_argument('--only-place'); ap.add_argument('--tier', choices=['A', 'B', 'C'])
    ap.add_argument('--only-id'); ap.add_argument('--redo', help='reset this item id to pending first')
    a = ap.parse_args()
    q = A.initialize(False)
    if a.redo:
        for x in q['items']:
            if x['id'] == a.redo: x.update(status='pending', attempts=0, last_error='')
        A.save(q)
    process(q, a.only_place, a.tier, a.limit, a.mock, a.only_id)


if __name__ == '__main__':
    main()
