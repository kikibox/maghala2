"""Resolve article links through reciprocal live hreflang, never guessed slugs.

This is a publication gate, not a front-end filter. Missing/unverified siblings
and insufficient unique links require editorial repair; no arbitrary substitutes.
"""
from __future__ import annotations
import html
import math
import re
import threading
import time
import urllib.parse
from html.parser import HTMLParser
import article_link_policy as policy

LANGUAGES = frozenset({'fa-IR', 'ar-IQ', 'tg-TJ', 'en-US', 'ru-RU'})
POLICY_VERSION = 1
_PAGE_CACHE = {}
_PAGE_LOCK = threading.Lock()
ANCHOR = re.compile(r'<a\b[^>]*>.*?</a\s*>', re.I | re.S)
HREF = re.compile(r'''(?<![\w:-])href\s*=\s*(["'])(.*?)\1''', re.I | re.S)
HEX = re.compile(r'\b(?:[0-9a-f]{2}){6,}\b', re.I)
# Deliberately bounded, reviewed vocabulary. Unknown crops are not claimed verified.
CROPS = {'اسپرس': {'en-US': ['sainfoin'], 'ar-IQ': ['الإسبارس', 'الاسبريس العلفي'], 'ru-RU': ['эспарцет'], 'tg-TJ': ['эспарцет']}, 'جعفری': {'en-US': ['parsley'], 'ar-IQ': ['بقدونس'], 'ru-RU': ['петруш'], 'tg-TJ': ['ҷаъфар', 'ҷаъфарӣ']}, 'طالبی': {'en-US': ['muskmelon', 'cantaloupe', 'melon'], 'ar-IQ': ['شمام'], 'ru-RU': ['дын'], 'tg-TJ': ['харбуза']}, 'کلزا': {'en-US': ['rapeseed', 'canola'], 'ar-IQ': ['كانولا', 'اللفت الزيتي'], 'ru-RU': ['рапс'], 'tg-TJ': ['рапс']}, 'تره': {'en-US': ['leek'], 'ar-IQ': ['كراث'], 'ru-RU': ['порей'], 'tg-TJ': ['пиёзи сабз']}, 'سبزی': {'en-US': ['vegetable'], 'ar-IQ': ['خضر', 'خضرا'], 'ru-RU': ['овощ'], 'tg-TJ': ['сабзавот']}, 'شنبلیله': {'en-US': ['fenugreek'], 'ar-IQ': ['حلبة'], 'ru-RU': ['пажитник'], 'tg-TJ': ['шамбала']}, 'کینوا': {'en-US': ['quinoa'], 'ar-IQ': ['كينوا'], 'ru-RU': ['киноа'], 'tg-TJ': ['кинва', 'киноа']}, 'بادمجان': {'en-US': ['eggplant', 'aubergine'], 'ar-IQ': ['باذنجان'], 'ru-RU': ['баклажан'], 'tg-TJ': ['бодинҷон']}, 'پنبه': {'en-US': ['cotton'], 'ar-IQ': ['قطن'], 'ru-RU': ['хлоп'], 'tg-TJ': ['пахта']}, 'شوید': {'en-US': ['dill'], 'ar-IQ': ['شبت'], 'ru-RU': ['укроп'], 'tg-TJ': ['шибит']}, 'کاهو': {'en-US': ['lettuce'], 'ar-IQ': ['خس'], 'ru-RU': ['салат'], 'tg-TJ': ['коҳу']}, 'ریحان': {'en-US': ['basil'], 'ar-IQ': ['ريحان'], 'ru-RU': ['базилик'], 'tg-TJ': ['райҳон']}, 'یونجه': {'en-US': ['alfalfa', 'lucerne'], 'ar-IQ': ['برسيم', 'فصة'], 'ru-RU': ['люцерн'], 'tg-TJ': ['юнучқа', 'люцерн']}, 'گلرنگ': {'en-US': ['safflower'], 'ar-IQ': ['عصفر'], 'ru-RU': ['сафлор'], 'tg-TJ': ['сафлор']}, 'مارچوبه': {'en-US': ['asparagus'], 'ar-IQ': ['هليون'], 'ru-RU': ['спарж'], 'tg-TJ': ['сарсабил']}, 'مرزه': {'en-US': ['savory', 'savoury'], 'ar-IQ': ['سعتر', 'ندغ'], 'ru-RU': ['чабер'], 'tg-TJ': ['чабер']}, 'خربزه': {'en-US': ['melon'], 'ar-IQ': ['بطيخ', 'شمام'], 'ru-RU': ['дын'], 'tg-TJ': ['харбуза']}}

class LinkPolicyError(ValueError):
    pass

class Page(policy._Page):
    def __init__(self):
        super().__init__()
        self.alternates = {}
        self.title_parts = []
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        a = dict(attrs)
        if tag == 'title': self.in_title = True
        if tag == 'link' and 'alternate' in a.get('rel', '').lower().split() and a.get('hreflang'):
            lang = a['hreflang'].lower().replace('_', '-')
            self.alternates.setdefault(lang, []).append(a.get('href', ''))
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
    def handle_data(self, text):
        if self.in_title: self.title_parts.append(text)


def normalize_text(value):
    return html.unescape(re.sub(r'<[^>]+>', ' ', str(value))).lower().replace('ي', 'ی').replace('ك', 'ک').replace('\u200c', ' ')


def crop_for_title(title):
    text = normalize_text(title)
    hits = [crop for crop in CROPS if re.search(r'(?<!\w)' + re.escape(crop) + r'(?!\w)', text)]
    return hits[0] if len(hits) == 1 else None


def validate_crop(source_title, title, body, language):
    crop = crop_for_title(source_title)
    if not crop:
        return
    contradictions = {
        'اسپرس': r'coffea|espresso|coffee|قهوه|تولید چای',
        'طالبی': r'\bpumpkin\b|cucurbita\s+pepo',
        'گلرنگ': r'grazing or understory cropping',
    }
    if crop in contradictions and re.search(contradictions[crop], normalize_text(title + ' ' + body), re.I):
        raise LinkPolicyError('Source/product identity contradiction requires editorial review: ' + crop)
    aliases = [crop] if language == 'fa-IR' else CROPS[crop].get(language, [])
    if not aliases or not all(any(normalize_text(a) in normalize_text(value) for a in aliases) for value in (title, body)):
        raise LinkPolicyError('Crop identity needs editorial review before publication: ' + crop)


_ANCHOR_STOP = set("آبیاری نوار تیپ قطره ای راهنمای جامع کاربردی مقاله مطالب مرتبط مطالعه تکمیلی و در به با از برای ها های irrigation drip tape article related guide practical complete comprehensive and the in of for a an to navar abyari ری الري بالتنقیط شریط دلیل شامل مقالة ذات صلة من فی و على для и в по на статья статьи руководство орошение капельное системы навор обёрӣ ва дар мақола роҳнамо".split())


def anchor_tokens(value):
    return set(re.findall(r'\w+', normalize_text(value))) - _ANCHOR_STOP


def count_bounds(body):
    words = len(re.findall(r'\w+', normalize_text(body)))
    minimum = 3 if words >= 900 else 2 if words >= 400 else 1
    maximum = min(7, max(minimum, math.ceil(words / 200)))
    return minimum, maximum


def _checked_page(url, language=None, fetcher=None):
    key = policy.url_key(url)
    if not key: raise LinkPolicyError('Unsafe or non-canonical internal URL')
    result = (fetcher or policy.fetch_page)(key)
    headers = {k.lower(): str(v) for k, v in result.get('headers', {}).items()}
    if result.get('status') != 200 or policy.url_key(result.get('url')) != key:
        raise LinkPolicyError('Internal destination must respond directly with 200')
    if not headers.get('content-type', '').lower().startswith('text/html') or re.search(r'\b(noindex|none)\b', headers.get('x-robots-tag', ''), re.I):
        raise LinkPolicyError('Destination is not indexable HTML')
    body = result.get('body', b'')
    if isinstance(body, bytes): body = body.decode('utf-8', 'strict')
    if len(body.encode('utf-8')) > policy.MAX_BYTES: raise LinkPolicyError('Page exceeds verification budget')
    page = Page(); page.feed(body)
    if page.noindex or len(page.canonicals) != 1 or policy.url_key(urllib.parse.urljoin(key, page.canonicals[0])) != key:
        raise LinkPolicyError('Destination must have one exact self-canonical')
    if language and page.language != language.lower():
        raise LinkPolicyError('Destination language does not match article')
    if fetcher is None and not policy.robots_allows(key):
        raise LinkPolicyError('Destination is not verified crawlable')
    return page


def checked_page(url, language=None, fetcher=None):
    key = policy.url_key(url)
    if fetcher is None:
        with _PAGE_LOCK:
            saved = _PAGE_CACHE.get(key)
        if saved and time.monotonic() - saved[0] < policy.CACHE_SECONDS:
            page = saved[1]
            if language and page.language != language.lower():
                raise LinkPolicyError('Destination language does not match article')
            return page
    page = _checked_page(url, language, fetcher)
    if fetcher is None:
        with _PAGE_LOCK:
            _PAGE_CACHE[key] = (time.monotonic(), page)
    return page


def localize_links(body, language, *, source_title='', title='', fetcher=None):
    """Keep translated prose/anchors; replace only verified href attribute values.

    Existing count checks in the translator still validate the original structure.
    Here duplicates, hex anchors, guessed/missing siblings, loops and language
    mismatches fail closed, including when rebuilding old SQL packages.
    """
    if language not in LANGUAGES: raise LinkPolicyError('Unsupported article language')
    validate_crop(source_title, title, body, language)
    seen = set(); edits = []; pages = {}
    def load(url, lang=None):
        key = policy.url_key(url)
        if key not in pages: pages[key] = checked_page(url, fetcher=fetcher)
        page = pages[key]
        if lang and page.language != lang.lower(): raise LinkPolicyError('Destination language does not match article')
        return page
    for match in ANCHOR.finditer(body):
        anchor = match.group(); href = HREF.search(anchor)
        if not href: continue
        raw = html.unescape(href.group(2)); parsed = urllib.parse.urlsplit(raw)
        if raw.startswith('#') or parsed.scheme in {'mailto','tel'}: continue
        if parsed.hostname and parsed.hostname.lower() not in {'navar-abyari.ir','www.navar-abyari.ir'}: continue
        url = policy.url_key(urllib.parse.urljoin(policy.SITE+'/', raw))
        if not url: raise LinkPolicyError('Internal article href is not an exact clean HTTPS URL')
        if re.search(r'^/(acf-field|nav_menu_item|rank_math_schema)/', urllib.parse.urlsplit(url).path, re.I):
            raise LinkPolicyError('Technical objects cannot be article destinations')
        label = normalize_text(anchor)
        if not label.strip() or HEX.search(label): raise LinkPolicyError('Internal anchor needs readable localized text')
        original = load(url)
        destination = url
        if original.language != language.lower():
            candidates = original.alternates.get(language.lower(), [])
            if len(candidates) != 1: raise LinkPolicyError('Missing or ambiguous exact hreflang sibling')
            destination = policy.url_key(candidates[0])
            if not destination: raise LinkPolicyError('Unsafe hreflang sibling')
            sibling = load(destination, language)
            reciprocal = sibling.alternates.get(original.language, [])
            if len(reciprocal) != 1 or policy.url_key(reciprocal[0]) != url:
                raise LinkPolicyError('Hreflang sibling is not reciprocal')
        else:
            load(destination, language)
        final_page = load(destination, language)
        if not anchor_tokens(label) & anchor_tokens(' '.join(final_page.title_parts)):
            raise LinkPolicyError('Anchor label does not corroborate the destination title')
        if title and normalize_text(title).strip() == normalize_text(' '.join(final_page.title_parts)).strip():
            raise LinkPolicyError('Possible self-link requires exact identity review')
        if destination in seen: raise LinkPolicyError('Repeated internal destination needs editorial consolidation')
        seen.add(destination)
        edits.append((match.start()+href.start(2), match.start()+href.end(2), html.escape(destination, quote=True)))
    low, high = count_bounds(body)
    if not low <= len(seen) <= high:
        raise LinkPolicyError(f'Internal link count needs editorial review: {len(seen)}, expected {low}..{high}')
    for begin, end, value in reversed(edits): body = body[:begin]+value+body[end:]
    return body
