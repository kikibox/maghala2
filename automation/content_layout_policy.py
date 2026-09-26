#!/usr/bin/env python3
"""Deterministic article layout and internal-link policy.

This module owns placement only. It never calls a model and never mutates
completed queue items.
"""
from __future__ import annotations

import hashlib
import html
import random
import re
import urllib.parse

BLOCK_END_RE = re.compile(r"</(?:p|ul|ol|table)>", re.I)
ANCHOR_RE = re.compile(r"<a\b[^>]*>(.*?)</a>", re.I | re.S)
MARKER_RE = re.compile(r"\[\[\[IMAGE_\d+\]\]\]")
HEADING_RE = re.compile(r"<h([2-4])\b[^>]*>(.*?)</h\1>", re.I | re.S)
DETAILS_RE = re.compile(r"<details\b", re.I)
TAG_RE = re.compile(r"<[^>]+>")
TOKEN_RE = re.compile(r"[\u0600-\u06ff\u200cA-Za-z0-9]+")

FAQ_TERMS = (
    "faq",
    "پرسش‌های متداول",
    "پرسش های متداول",
    "سوالات متداول",
    "سؤالات متداول",
)
SYSTEM_POST_TYPES = {
    "acf-field", "acf-field-group", "nav_menu_item", "oembed_cache",
    "rank_math_schema", "wp_global_styles", "elementor_library",
    "custom_css", "gp_elements", "wpcf7_contact_form",
    "customize_changeset", "gp_font", "attachment",
}
UTILITY_TERMS = {
    "contact", "contact-us", "about", "privacy", "privacy-policy", "terms",
    "rules", "law", "cart", "checkout", "account", "login", "register",
    "feed", "sitemap", "wp-json", "wp-admin", "tag", "author", "page",
    "تماس", "درباره", "حریم-خصوصی", "قوانین", "سبد", "حساب", "ورود",
}
LINK_SENTENCES = (
    'برای تکمیل این بخش، راهنمای <a href="{url}">{title}</a> را نیز ببینید.',
    'مطالعه مطلب <a href="{url}">{title}</a> جزئیات بیشتری در اختیارتان می‌گذارد.',
    'در همین زمینه، مقاله <a href="{url}">{title}</a> نیز پیشنهاد می‌شود.',
    'برای بررسی دقیق‌تر، می‌توانید مطلب <a href="{url}">{title}</a> را مطالعه کنید.',
    'راهنمای <a href="{url}">{title}</a> نکات مکملی درباره این موضوع ارائه می‌دهد.',
    'اگر به جزئیات اجرایی نیاز دارید، مقاله <a href="{url}">{title}</a> مفید است.',
    'در ادامه این بحث، مطالعه <a href="{url}">{title}</a> توصیه می‌شود.',
    'برای مقایسه و تصمیم‌گیری بهتر، مطلب <a href="{url}">{title}</a> را ببینید.',
)


def stable_seed(item: dict, namespace: str = "layout") -> int:
    material = "|".join(str(item.get(k) or "") for k in (
        "id", "title", "focus", "city", "topic", "topic_title", "vertical"
    ))
    digest = hashlib.sha256(f"{namespace}|{material}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _plain(value) -> str:
    return html.unescape(TAG_RE.sub(" ", str(value or ""))).strip()


def _tokens(value) -> set[str]:
    return {x.lower().replace("ي", "ی").replace("ك", "ک") for x in TOKEN_RE.findall(_plain(value)) if len(x) > 2}


def _canonical_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.quote(urllib.parse.unquote(parsed.path), safe="/").rstrip("/") + "/"
    return urllib.parse.urlunparse(((parsed.scheme or "https").lower(), parsed.netloc.lower(), path, "", "", ""))


def clean_link_pool(rows: list[dict], item: dict, site_host: str = "navar-abyari.ir") -> list[dict]:
    current_slug = str(item.get("slug") or "").strip("/").lower()
    current_title = _plain(item.get("title")).lower()
    unique = {}
    for row in rows or []:
        if row.get("post_type") in SYSTEM_POST_TYPES:
            continue
        url = str(row.get("url") or "").strip()
        title = _plain(row.get("title"))
        if not url or not title:
            continue
        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        if host != site_host and not host.endswith("." + site_host):
            continue
        decoded_path = urllib.parse.unquote(parsed.path).strip("/").lower()
        segments = {x for x in re.split(r"[/_-]+", decoded_path) if x}
        lowered = f"{decoded_path} {title.lower()}"
        if segments & UTILITY_TERMS or any(f"/{term}/" in f"/{decoded_path}/" for term in UTILITY_TERMS):
            continue
        if decoded_path == current_slug or title.lower() == current_title:
            continue
        canonical = _canonical_url(url)
        unique.setdefault(canonical, {"title": title, "url": canonical, "post_type": row.get("post_type", "post")})
    return sorted(unique.values(), key=lambda row: row["url"])


def select_internal_links(rows: list[dict], item: dict, count: int = 4) -> list[dict]:
    pool = clean_link_pool(rows, item)
    if len(pool) < count:
        raise ValueError(f"healthy internal-link pool has {len(pool)} URLs; {count} required")
    query_tokens = _tokens(" ".join(str(item.get(k) or "") for k in (
        "title", "focus", "city", "topic", "topic_title", "vertical"
    )))
    ranked = []
    for row in pool:
        overlap = len(query_tokens & _tokens(row["title"]))
        tie = hashlib.sha256(f"{stable_seed(item, 'links')}|{row['url']}".encode()).hexdigest()
        ranked.append((overlap, tie, row))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    related = [row for score, _, row in ranked if score > 0][:2]
    chosen_urls = {row["url"] for row in related}
    remainder = [row for _, _, row in ranked if row["url"] not in chosen_urls]
    rng = random.Random(stable_seed(item, "link-random"))
    rng.shuffle(remainder)
    selected = related + remainder[:count - len(related)]
    if len(selected) < count:
        raise ValueError("could not select enough unique internal links")
    return selected[:count]


def strip_model_links_and_markers(raw_html: str) -> str:
    body = ANCHOR_RE.sub(lambda match: match.group(1), raw_html or "")
    return MARKER_RE.sub("", body)


def find_faq_start(body: str) -> int:
    for match in HEADING_RE.finditer(body):
        title = _plain(match.group(2)).lower()
        if any(term in title for term in FAQ_TERMS):
            return match.start()
    details = DETAILS_RE.search(body)
    if details:
        return details.start()
    raise ValueError("FAQ section was not found")


def _safe_points(pre_faq: str) -> list[int]:
    return [match.end() for match in BLOCK_END_RE.finditer(pre_faq)]


def _point_for_ratio(points: list[int], ratio: float, used: set[int]) -> int:
    if not points:
        return 0
    target = int(round((len(points) - 1) * ratio))
    candidates = sorted(range(len(points)), key=lambda i: (abs(i - target), i))
    for index in candidates:
        point = points[index]
        if point not in used:
            used.add(point)
            return point
    return points[-1]


def _insert_events(pre_faq: str, events: list[tuple[int, str]]) -> str:
    for point, fragment in sorted(events, key=lambda event: event[0], reverse=True):
        pre_faq = pre_faq[:point] + "\n" + fragment + "\n" + pre_faq[point:]
    return pre_faq


def validate_faq_tail(body: str) -> None:
    faq_start = find_faq_start(body)
    tail = body[faq_start:]
    headings = list(HEADING_RE.finditer(tail))
    if len(headings) > 1:
        raise ValueError("content heading found after FAQ started")
    if "<details" not in tail.lower() or "<summary" not in tail.lower():
        raise ValueError("FAQ details/summary structure is missing")
    if any(f"[[[IMAGE_{i}]]]" in tail for i in range(2, 6)):
        raise ValueError("image marker appears inside or after FAQ")
    if "<a " in tail.lower():
        raise ValueError("internal link appears inside or after FAQ")


def apply_layout(raw_html: str, item: dict, link_pool: list[dict], link_count: int = 4):
    body = strip_model_links_and_markers(raw_html)
    faq_start = find_faq_start(body)
    pre_faq, faq_tail = body[:faq_start], body[faq_start:]
    points = _safe_points(pre_faq)
    if not points:
        # Safe, valid top-level fallback immediately before FAQ.
        pre_faq = pre_faq + "<p></p>"
        points = _safe_points(pre_faq)

    selected = select_internal_links(link_pool, item, link_count)
    used_points = set()
    events = []
    for image_no, ratio in zip(range(2, 6), (0.16, 0.37, 0.58, 0.79)):
        point = _point_for_ratio(points, ratio, used_points)
        events.append((point, f"[[[IMAGE_{image_no}]]]"))

    sentence_rng = random.Random(stable_seed(item, "link-sentences"))
    templates = list(LINK_SENTENCES)
    sentence_rng.shuffle(templates)
    link_points = set()
    for link, ratio, template in zip(selected, (0.25, 0.46, 0.67, 0.88), templates):
        point = _point_for_ratio(points, ratio, link_points)
        sentence = template.format(url=html.escape(link["url"], quote=True), title=html.escape(link["title"]))
        events.append((point, f"<p>{sentence}</p>"))

    laid_out = _insert_events(pre_faq, events) + faq_tail
    if "[[[IMAGE_1]]]" in laid_out:
        raise ValueError("featured image marker must not appear in article body")
    for image_no in range(2, 6):
        if laid_out.count(f"[[[IMAGE_{image_no}]]]") != 1:
            raise ValueError(f"IMAGE_{image_no} marker count is not one")
    validate_faq_tail(laid_out)
    return laid_out, selected
