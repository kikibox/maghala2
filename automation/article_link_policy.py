"""Fail-closed link selection for the Persian article producer.

No guessed slugs, prefix matching, redirects, or WordPress mutations.
The final HTML must corroborate an exact, indexable Persian canonical URL.
"""
from __future__ import annotations

import html
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

SITE = "https://navar-abyari.ir"
CONTENT_TYPES = frozenset({"post", "page", "product", "faq", "city"})
POLICY_VERSION = 1
MAX_BYTES = 2_000_000
CACHE_SECONDS = 900
_CACHE = {}
_LOCK = threading.Lock()
_ROBOTS_CACHE = None
_STOP = set("آبیاری نوار تیپ راهنمای جامع بررسی برای در از به با و یا که این آن یک کاربردی نکات".split())


def url_key(value):
    """Compare Unicode/percent-case equivalents, never fuzzy path prefixes."""
    try:
        p = urllib.parse.urlsplit(html.unescape(str(value)))
        if (p.scheme != "https" or p.netloc.lower() != "navar-abyari.ir"
                or p.query or p.fragment or "\\" in p.path
                or re.search(r"%(?![0-9a-fA-F]{2})", p.path)):
            return None
        path = urllib.parse.quote(p.path, safe="/%:@!$&'()*+,;=-._~")
        path = re.sub(r"%[0-9A-Fa-f]{2}", lambda m: m[0].lower(), path)
        return SITE + path
    except (ValueError, TypeError):
        return None


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.language = ""
        self.canonicals = []
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.language = a.get("lang", "").lower().replace("_", "-")
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        if tag == "meta" and a.get("name", "").lower() in {
            "robots", "googlebot", "googlebot-news"
        }:
            self.noindex |= bool(re.search(r"\b(noindex|none)\b", a.get("content", ""), re.I))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_page(url):
    req = urllib.request.Request(
        url_key(url),
        headers={"User-Agent": "navar-article-link-qa/1.0", "Accept": "text/html"},
    )
    with urllib.request.build_opener(_NoRedirect).open(req, timeout=15) as response:
        body = response.read(MAX_BYTES + 1)
        return {
            "status": response.status,
            "url": response.geturl(),
            "headers": dict(response.headers),
            "body": body,
        }


def verify_page(url, result):
    key = url_key(url)
    if not key or result.get("status") != 200 or url_key(result.get("url")) != key:
        return False
    headers = {k.lower(): str(v) for k, v in result.get("headers", {}).items()}
    if not headers.get("content-type", "").lower().startswith("text/html"):
        return False
    if re.search(r"\b(noindex|none)\b", headers.get("x-robots-tag", ""), re.I):
        return False
    body = result.get("body", b"")
    if isinstance(body, bytes):
        if len(body) > MAX_BYTES:
            return False
        body = body.decode("utf-8", "strict")
    if len(body.encode("utf-8")) > MAX_BYTES:
        return False
    page = _Page()
    page.feed(body)
    return (
        page.language in {"fa", "fa-ir"}
        and not page.noindex
        and len(page.canonicals) == 1
        and url_key(urllib.parse.urljoin(key, page.canonicals[0])) == key
    )


def robots_allows(url):
    """Treat unavailable/redirecting robots responses as unverified, not allowed."""
    global _ROBOTS_CACHE
    with _LOCK:
        cached = _ROBOTS_CACHE
    if not cached or time.monotonic() - cached[0] >= CACHE_SECONDS:
        try:
            request = urllib.request.Request(
                SITE + "/robots.txt", headers={"User-Agent": "navar-article-link-qa/1.0"}
            )
            with urllib.request.build_opener(_NoRedirect).open(request, timeout=15) as r:
                data = r.read(100_001)
                if r.status != 200 or len(data) > 100_000:
                    return False
                text = data.decode("utf-8-sig", "strict")
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(text.splitlines())
        except (OSError, ValueError, UnicodeError, urllib.error.URLError):
            return False
        cached = (time.monotonic(), parser)
        with _LOCK:
            _ROBOTS_CACHE = cached
    return cached[1].can_fetch("Googlebot", url_key(url))


def verified(url, fetcher=None):
    key = url_key(url)
    if not key:
        return False
    # Injected fetchers bypass the cache; unit tests never make network calls.
    if fetcher is None:
        with _LOCK:
            saved = _CACHE.get(key)
        if saved and time.monotonic() - saved[0] < CACHE_SECONDS:
            return saved[1]
    try:
        passed = verify_page(url, (fetcher or fetch_page)(url))
        if passed and fetcher is None:
            passed = robots_allows(url)
    except (OSError, ValueError, UnicodeError, urllib.error.URLError):
        passed = False
    if fetcher is None:
        with _LOCK:
            _CACHE[key] = (time.monotonic(), passed)
    return passed


def _tokens(value):
    text = re.sub(r"<[^>]+>", " ", html.unescape(str(value))).lower()
    text = text.replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    return set(re.findall(r"[a-z0-9\u0621-\u06ff]+", text)) - _STOP


def select_links(item, links, *, limit=12, probe_limit=60, fetcher=None):
    """Require topic overlap as well as a live, self-canonical Persian page."""
    topic = _tokens(str(item.get("title", "")) + " " + str(item.get("focus", "")))
    candidates = []
    for row in links:
        if row.get("post_type") not in CONTENT_TYPES:
            continue
        if row.get("status", "publish") != "publish":
            continue
        key = url_key(row.get("url"))
        overlap = len(topic & _tokens(row.get("title", "")))
        if key and overlap:
            candidates.append((-overlap, key, row))
    candidates.sort(key=lambda x: (x[0], x[1]))
    approved, seen, probes = [], set(), 0
    for _, key, row in candidates:
        if key in seen:
            continue
        seen.add(key)
        if probes >= probe_limit:
            break
        probes += 1
        if verified(row["url"], fetcher):
            approved.append({**row, "url": key})
        if len(approved) >= limit:
            break
    return approved