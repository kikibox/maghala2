#!/usr/bin/env python3
"""Independent useful-article content queue for navar-abyari.ir.

This module is INTENTIONALLY SEPARATE from automation/city_content_queue.py:
  - City queue: advertising posts about "دستگاه/نوار خرید در شهر X" (city verticals)
  - Article queue (this file): useful content articles about drip irrigation,
    crops, products, irrigation methods, and strategic topics.

Shared infrastructure (reused, not modified):
  - Agnes API client (same model, same base URL pattern)
  - Internal-link pool (same link_index refresh logic)
  - Reversible SQL output (same per-item + combined + rollback pattern)
  - 1050+ words / exactly 4 policy-selected internal links / 5 images

Output: artifacts/article-content-queue/
  queue.json, items/, sql/, rollback/, create-all-completed.sql
"""
import json, os, re, time, hashlib, struct, urllib.request, urllib.error, html, datetime as dt
from collections import Counter
from pathlib import Path
from agnes_json_client import call as agnes_json_call
import article_image_policy
import content_layout_policy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "article-content-queue"
ITEMS = OUT / "items"; SQL = OUT / "sql"; ROLLBACK = OUT / "rollback"
QUEUE = OUT / "queue.json"; STATUS = OUT / "status.json"
TOPICS_FILE = OUT / "topics.json"
CATALOG = ROOT / "data" / "article-catalog.json"

SITE = "https://navar-abyari.ir"
TABLE = "ha_posts"; META = "ha_postmeta"

# Agnes config (same as city queue)
AGNES_BASE = (os.getenv("AGNES_API_BASE") or "https://apihub.agnes-ai.com/v1").rstrip("/")
AGNES_KEY = os.getenv("AGNES_API_KEY", "").strip()
AGNES_MODEL = os.getenv("AGNES_MODEL") or "agnes-3.0-flash"

# Image config uses the same Agnes endpoint/key as the working city image
# implementation. The previous GitHub Models endpoint was incompatible with
# the Agnes image model name.
IMAGE_TOKEN = (os.getenv("IMAGE_API_KEY") or AGNES_KEY).strip()
IMAGE_MODEL = os.getenv("IMAGE_MODEL") or "agnes-image-2.0-flash"
IMAGE_ENDPOINT = os.getenv("IMAGE_ENDPOINT") or f"{AGNES_BASE}/images/generations"
UPLOAD_SUBDIR = (os.getenv("ARTICLE_IMAGE_UPLOAD_SUBDIR") or "2026/09/navar-article-generated").strip("/")
PUBLIC_UPLOAD_BASE = f"{SITE}/wp-content/uploads/{UPLOAD_SUBDIR}"

BATCH = max(1, int(os.getenv("BATCH_SIZE", "2")))
MIN_WORDS = int(os.getenv("MIN_WORDS", "1050"))
MIN_LINKS = int(os.getenv("MIN_INTERNAL_LINKS", "4"))
MAX_ATTEMPTS = max(1, int(os.getenv("MAX_ATTEMPTS", "4")))

# SQL needs term_taxonomy_id, not term_id. Keep the old variable as a
# backwards-compatible fallback for existing repository settings.
CATEGORY_TAXONOMY_ID = int(
    os.getenv("ARTICLE_CATEGORY_TAXONOMY_ID")
    or os.getenv("ARTICLE_CATEGORY_ID")
    or "35"
)

WORD_RE = re.compile(r"[\u0600-\u06ff\u200c]+|[A-Za-z]+")
HREF_RE = re.compile(r'<a\b[^>]*href=["\']([^"\']+)', re.I)


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def fetch_json(url, headers=None, payload=None, timeout=420):
    req = urllib.request.Request(
        url,
        data=(json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None),
        headers=headers or {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {url}: {e.read().decode('utf-8','replace')[:800]}")


def normalize(s):
    s = html.unescape(str(s or "")).replace("ي","ی").replace("ك","ک").replace("\u200c"," ")
    return re.sub(r"[^\u0600-\u06ff0-9]+","",s).lower()


def esc(s):
    return (s or "").replace("\\","\\\\").replace("'","\\'").replace("\0","\\0").replace("\n","\\n").replace("\r","\\r").replace("\x1a","\\Z")


def words(text):
    return len(WORD_RE.findall(re.sub(r'<[^>]+>',' ',text or '')))


def internal_links(text):
    from urllib.parse import urlparse
    found = set()
    for url in HREF_RE.findall(text or ""):
        host = (urlparse(url).hostname or "").lower()
        if host == "navar-abyari.ir" or host.endswith(".navar-abyari.ir"):
            found.add(url)
    return found


def sitemap_index():
    """Collect all healthy content URLs exposed by the site's sitemap indexes."""
    import urllib.parse as _up, json as _json, re as _re
    cache = OUT / "link-index-sitemap.json"
    if cache.exists():
        try:
            c = _json.loads(cache.read_text(encoding="utf-8"))
            if c.get("count", 0) > 0:
                return c["links"]
        except Exception:
            pass
    def read_url(url, timeout=60):
        req = urllib.request.Request(url, headers={"User-Agent": "navar-article-queue"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", "replace")

    sitemap_urls = set()
    for index_name in ("sitemap_index.xml", "wp-sitemap.xml"):
        try:
            for loc in _re.findall(r"<loc>(.*?)</loc>", read_url(f"{SITE}/{index_name}")):
                lowered = loc.lower()
                if any(token in lowered for token in (
                    "post-sitemap", "page-sitemap", "product-sitemap",
                    "wp-sitemap-posts-post", "wp-sitemap-posts-page",
                    "wp-sitemap-posts-product",
                )):
                    sitemap_urls.add(loc)
        except Exception:
            pass
    if not sitemap_urls:
        sitemap_urls = {f"{SITE}/post-sitemap1.xml", f"{SITE}/post-sitemap2.xml"}

    urls = set()
    for sitemap_url in sorted(sitemap_urls):
        try:
            urls.update(_re.findall(r"<loc>(.*?)</loc>", read_url(sitemap_url)))
        except Exception:
            pass
    if not urls:
        return []
    links = []
    for url in sorted(urls):
        path = _up.urlparse(url).path.strip("/")
        title = None
        try:
            slug = _up.unquote(path)
            req = urllib.request.Request(f"{SITE}/wp-json/wp/v2/posts?slug={_up.quote(slug)}&per_page=1",
                                         headers={"User-Agent":"navar-article-queue"})
            with urllib.request.urlopen(req, timeout=15) as r:
                rows = _json.loads(r.read().decode("utf-8","replace"))
                if rows:
                    t = rows[0].get("title")
                    if isinstance(t, dict):
                        title = t.get("raw") or None
                    elif isinstance(t, str) and t:
                        title = t
        except Exception:
            pass
        if not title:
            try:
                page = read_url(url, timeout=20)
                match = _re.search(r"<title[^>]*>(.*?)</title>", page, _re.I | _re.S)
                if match:
                    title = html.unescape(_re.sub(r"<[^>]+>", "", match.group(1)))
                    title = _re.split(r"\s+[|–—-]\s+", title, maxsplit=1)[0].strip()
            except Exception:
                pass
        if not title:
            # A URL without an authoritative title cannot provide trustworthy
            # anchor text, so it is excluded instead of inventing a label.
            continue
        links.append({"title": title, "url": url, "post_type": "post"})
    OUT.mkdir(parents=True, exist_ok=True)
    cache.write_text(_json.dumps({"count":len(links),"links":links}, ensure_ascii=False, indent=1), encoding="utf-8")
    return links


def rest_index():
    """Fully independent: pull existing posts from the live WordPress REST API.

    No dependency on the city queue, no DB dump. If the REST API is
    unreachable, returns an empty link list (the queue still initializes,
    just without a link pool — the content generator will use its fallback).
    """
    import urllib.request as _ur, json as _json
    names = set(); links = []
    page = 1
    per_page = 100
    while True:
        try:
            url = f"{SITE}/wp-json/wp/v2/posts?per_page={per_page}&page={page}&_fields=id,slug,title,type,status"
            req = _ur.Request(url, headers={"User-Agent": "navar-article-queue"})
            with _ur.urlopen(req, timeout=45) as r:
                rows = _json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
            break
        if not rows:
            break
        for row in rows:
            slug = (row.get("slug") or "").strip("/")
            status = row.get("status") or "publish"
            if status not in {"publish", "draft", "pending", "future", "private"}:
                continue
            title = row.get("title")
            if isinstance(title, dict):
                title = title.get("raw") or title.get("rendered") or slug
            else:
                title = title or slug
            pt = row.get("type") or "post"
            names.add(normalize(title)); names.add(normalize(slug))
            links.append({"title": title,
                         "url": f"{SITE}/{slug}/" if pt == "post" else f"{SITE}/{pt}/{slug}/",
                         "post_type": pt})
        # Pagination: stop if fewer rows than per_page
        if len(rows) < per_page:
            break
        page += 1
    return names, links


def write_status(q, result):
    c = Counter(x["status"] for x in q["items"])
    STATUS.write_text(json.dumps({
        "result": result, "updated_at": now(), "total": len(q["items"]),
        "pending": c["pending"], "processing": c["processing"],
        "completed": c["completed"], "failed": c["failed"],
        "blocked_image_model": c["blocked_image_model"],
        "image_model": IMAGE_MODEL, "batch_size": BATCH
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    # Live human-readable STATUS.md (mirrors the city queue format)
    STATUS_MD = OUT / "STATUS.md"
    total = len(q["items"])
    done = c["completed"]
    pct = (done / total * 100) if total else 0
    lines = [
        "# وضعیت زنده صف تولید مقالات مفید",
        "",
        "> این صفحه پس از پردازش هر مقاله به‌روزرسانی می‌شود. برای دیدن مقدار تازه، صفحه را Refresh کنید.",
        "",
        f"- آخرین بروزرسانی: `{now()}`",
        f"- وضعیت صف: **{result}**",
        f"- پیشرفت: **{done} از {total} ({pct:.2f}٪)**",
        f"- تکمیل‌شده: **{done}**",
        f"- در حال پردازش: **{c['processing']}**",
        f"- در انتظار: **{c['pending']}**",
        f"- ناموفق: **{c['failed']}**",
        f"- مسدود به‌دلیل مدل تصویر: **{c['blocked_image_model']}**",
        f"- مدل متن: `{AGNES_MODEL}`",
        f"- مدل تصویر: `{IMAGE_MODEL}`",
        f"- دستهٔ مقالات: **مقاله‌ها** (term_taxonomy {CATEGORY_TAXONOMY_ID})",
        "",
        "## دسته‌بندی عمودی",
        "",
    ]
    by_v = Counter(x.get("vertical", "?") for x in q["items"] if x["status"] == "completed")
    for v in sorted(by_v):
        lines.append(f"- {v}: {by_v[v]}")
    STATUS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def initialize(force=False):
    for p in (OUT, ITEMS, SQL, ROLLBACK):
        p.mkdir(parents=True, exist_ok=True)
    if QUEUE.exists() and not force:
        return json.loads(QUEUE.read_text(encoding="utf-8"))

    # Load topics from the pre-seeded topics.json (produced by topic_matrix.py)
    if not TOPICS_FILE.exists():
        raise RuntimeError(f"topics.json not found at {TOPICS_FILE}. Run topic_matrix.py first.")
    topics = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    topic_list = topics["topics"]

    # Load existing posts from the LIVE REST API to dedup (fully independent,
    # no dependency on the city queue or a DB dump).
    try:
        existing, links = rest_index()
        print(f"rest_index: {len(existing)} existing posts, {len(links)} links (live API)", flush=True)
    except Exception as e:
        existing = set(); links = []
        print(f"rest_index warning: {type(e).__name__}: {e} — proceeding with empty link pool", flush=True)

    # Build queue items from topics
    items = []
    for idx, t in enumerate(topic_list):
        norm_title = normalize(t["title"])
        # Skip if already exists in the live site
        if norm_title in existing:
            continue
        items.append({
            "id": t["id"],
            "title": t["title"],
            "slug": t["slug"],
            "focus": t["focus"],
            "vertical": t["vertical"],
            "category_id": CATEGORY_TAXONOMY_ID,
            "post_type": "post",
            "status": "pending",
            "attempts": 0
        })

    q = {
        "version": 1,
        "created_at": now(),
        "updated_at": now(),
        "source": "article-catalog.json + topics.json",
        "scope": "useful articles — separate from city queue",
        "text_model": AGNES_MODEL,
        "image_model": IMAGE_MODEL,
        "images_per_post": 5,
        "category_id": CATEGORY_TAXONOMY_ID,
        "rules": {"draft_only": False, "minimum_words": MIN_WORDS, "minimum_internal_links": MIN_LINKS},
        "items": items,
        "link_index": links
    }
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    write_status(q, "initialized")
    return q


def agnes(prompt):
    # Shared client handles fenced/double-encoded JSON and bounded retries.
    import sys
    return agnes_json_call(sys.modules[__name__], prompt, attempts=4)


def make_content(item, links):
    prompt = f'''برای مقاله مفید با موضوع "{item["title"]}" در حوزه آبیاری قطره‌ای و نوار تیپ، یک مقاله سئوشده و کاربردی بنویس. متن فارسی طبیعی، دست‌کم {MIN_WORDS} کلمه و بدون ادعای ساختگی درباره قیمت یا نمایندگی محلی باشد. ساختار HTML فقط با h2/h3/p/ul/ol/table/strong/details/summary باشد و H1 نداشته باشد. پیش از FAQ دست‌کم ۱۲ بلوک مستقل و طبیعی از نوع p، ul، ol یا table ایجاد کن. هیچ لینک، تگ a، تصویر یا marker تصویر نساز؛ سامانه بعداً آن‌ها را با سیاست قطعی درج می‌کند. FAQ باید آخرین بخش مقاله باشد، با یک h2 با عنوان پرسش‌های متداول شروع شود و سؤال‌ها را فقط با details/summary نگه دارد. پس از FAQ هیچ heading، جمع‌بندی یا محتوای تازه‌ای قرار نده. موضوعات: مقدمه، بخش‌های تخصصی مرتبط با {item["focus"]}، نکات عملی، جمع‌بندی و در انتها FAQ. فقط JSON معتبر با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.'''
    for _ in range(4):
        obj = agnes(prompt)
        try:
            body, selected = content_layout_policy.apply_layout(
                obj.get("html", ""), item, links, MIN_LINKS
            )
            used = internal_links(body)
            if words(body) < MIN_WORDS:
                raise ValueError(f"length {words(body)} below {MIN_WORDS}")
            if len(used) != MIN_LINKS:
                raise ValueError(f"internal link count {len(used)} != {MIN_LINKS}")
            if any(body.count(f"[[[IMAGE_{i}]]]") != 1 for i in range(2, 6)):
                raise ValueError("image marker count is invalid")
            content_layout_policy.validate_faq_tail(body)
            obj["html"] = body
            obj["selected_internal_links"] = selected
            return obj
        except Exception as exc:
            prompt += (
                "\nنسخه قبلی کنترل کیفیت را رد کرد: "
                + str(exc)[:240]
                + ". متن را کامل‌تر کن، FAQ را با details/summary فقط در انتها نگه دار و هیچ لینک یا marker نساز."
            )
    raise RuntimeError("Text QA failed after 4 attempts")


def _urlnorm(u):
    import urllib.parse as _up
    try:
        p = _up.urlparse(u)
        q = _up.quote(_up.unquote(p.path), safe="/")
        qs = _up.quote(_up.unquote(p.query), safe="=&") if p.query else ""
        return ("%s://%s%s" % ((p.scheme or "https"), p.netloc, q)) + (("?" + qs) if qs else "")
    except Exception:
        return u


def sanitize_links(html_text, allowed_urls):
    import re as _re
    allowed_norm = {_urlnorm(u) for u in allowed_urls}
    def _keep(match):
        tag = match.group(0)
        m = _re.search(r'href=["\']([^"\']+)', tag, _re.I)
        if not m:
            return tag
        href = m.group(1)
        if _urlnorm(href) in allowed_norm:
            return tag
        # Preserve visible text but strip every non-allowlisted destination.
        return _re.sub(r'</?a\b[^>]*>', '', tag)
    return _re.sub(r'<a\b[^>]*>.*?</a>', _keep, html_text, flags=_re.I | _re.S)


def image_info(blob):
    """Return extension, MIME type, width, and height for supported images."""
    if blob.startswith(b"\x89PNG\r\n\x1a\n") and len(blob) >= 24:
        width, height = struct.unpack(">II", blob[16:24])
        return ".png", "image/png", width, height
    if blob.startswith(b"\xff\xd8"):
        pos = 2
        while pos + 9 < len(blob):
            if blob[pos] != 0xFF:
                pos += 1
                continue
            marker = blob[pos + 1]
            pos += 2
            if marker in {0xD8, 0xD9}:
                continue
            if pos + 2 > len(blob):
                break
            length = int.from_bytes(blob[pos:pos + 2], "big")
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height = int.from_bytes(blob[pos + 3:pos + 5], "big")
                width = int.from_bytes(blob[pos + 5:pos + 7], "big")
                return ".jpg", "image/jpeg", width, height
            pos += max(length, 2)
    raise RuntimeError("Generated image format is unsupported or corrupt")


def generate_image(item, kind):
    import base64
    import io
    from PIL import Image
    if not IMAGE_TOKEN:
        raise RuntimeError("IMAGE_API_KEY/AGNES_API_KEY is missing")
    img_dir = OUT / "images"
    img_dir.mkdir(exist_ok=True)
    name = f"{item['id']}-{kind}.jpg"
    path = img_dir / name
    ocr_results = []
    # Three identity-preserving attempts, followed by one safe fallback where
    # labels/logos are deliberately not readable (maximum three regenerations).
    for attempt in range(1, 5):
        hide_label = attempt == 4
        references = article_image_policy.reference_images(item, kind)
        extra_body = {"response_format": "b64_json"}
        if references:
            extra_body["image"] = references
        data = fetch_json(
            IMAGE_ENDPOINT,
            {"Authorization": f"Bearer {IMAGE_TOKEN}", "Content-Type": "application/json",
             "Accept": "application/json", "User-Agent": "navar-article-queue"},
            {"model": IMAGE_MODEL,
             "prompt": article_image_policy.image_prompt(item, kind, hide_label=hide_label),
             "size": "1024x768", "return_base64": True, "extra_body": extra_body},
            600
        )
        row = data["data"][0]
        if row.get("b64_json"):
            source_blob = base64.b64decode(row["b64_json"])
        elif row.get("url"):
            with urllib.request.urlopen(row["url"], timeout=180) as r:
                source_blob = r.read()
        else:
            raise RuntimeError("Image response has neither b64_json nor url")
        if len(source_blob) < 10000:
            raise RuntimeError("Generated image is unexpectedly small")
        image = Image.open(io.BytesIO(source_blob)).convert("RGB")
        width, height = image.size
        target = 16 / 9
        if width / height > target:
            new_width = int(height * target)
            left = (width - new_width) // 2
            image = image.crop((left, 0, left + new_width, height))
        else:
            new_height = int(width / target)
            top = (height - new_height) // 2
            image = image.crop((0, top, width, top + new_height))
        image = image.resize((1200, 675), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=92, optimize=True)
        blob = buffer.getvalue()
        path.write_bytes(blob)
        valid, observed = article_image_policy.validate_ocr(
            path, item, kind, hide_label=hide_label
        )
        ocr_results.append({"attempt": attempt, "valid": valid, "text": observed[:300]})
        if valid:
            suffix, mime, width, height = image_info(blob)
            return {
                "name": name,
                "sha256": hashlib.sha256(blob).hexdigest(),
                "mime": mime,
                "width": width,
                "height": height,
                "variation": article_image_policy.variation_spec(item, kind),
                "ocr": ocr_results,
            }
        path.unlink(missing_ok=True)
    raise RuntimeError(f"Image OCR policy failed after 3 retries and safe fallback: {ocr_results}")


def _php_attachment_metadata(image):
    relative = f"{UPLOAD_SUBDIR}/{image['name']}"
    relative_len = len(relative.encode("utf-8"))
    return (
        f'a:3:{{s:5:"width";i:{int(image["width"])};'
        f's:6:"height";i:{int(image["height"])};'
        f's:4:"file";s:{relative_len}:"{relative}";}}'
    )


def sql_for(item, obj, images):
    title = obj["title"]; body = obj["html"]; urls = []
    for i, image in enumerate(images, 1):
        name = image["name"]
        url = f"{PUBLIC_UPLOAD_BASE}/{name}"
        urls.append(url)
        body = body.replace(
            f"[[[IMAGE_{i}]]]",
            f'<figure class="wp-block-image size-large"><img src="{url}" alt="{item["title"]} - تصویر {i}"/><figcaption>{item["focus"]}</figcaption></figure>'
        )
    pt = item["post_type"]; slug = item["slug"]
    queue_key = f"article-content-queue:{item['id']}"
    excerpt = obj.get("excerpt","")
    q = [
        "START TRANSACTION;",
        f"SET @queue_key='{esc(queue_key)}';",
        f"SET @post_id=(SELECT post_id FROM `{META}` WHERE meta_key='_navar_queue_item_id' AND meta_value=@queue_key LIMIT 1);",
        f"SET @slug_conflict=(SELECT ID FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}' AND (@post_id IS NULL OR ID<>@post_id) LIMIT 1);",
        f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(body)}','{esc(title)}','{esc(excerpt)}','publish','open','open','{esc(slug)}',NOW(),UTC_TIMESTAMP(),0,'',0,'{esc(pt)}','',0 WHERE @post_id IS NULL AND @slug_conflict IS NULL;",
        "SET @post_id=COALESCE(@post_id,IF(@slug_conflict IS NULL,LAST_INSERT_ID(),NULL));",
        # A conflict deliberately leaves @post_id NULL. Every later write is
        # guarded, so an unrelated post with the same slug is never modified.
        f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'_navar_queue_item_id',@queue_key WHERE @post_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@post_id AND meta_key='_navar_queue_item_id');",
        "SELECT IF(@post_id IS NULL,'SKIPPED: slug conflict','OK') AS navar_queue_result;",
        f"UPDATE `{TABLE}` SET post_content='{esc(body)}',post_title='{esc(title)}',post_excerpt='{esc(excerpt)}',post_status='publish',post_modified=NOW(),post_modified_gmt=UTC_TIMESTAMP() WHERE ID=@post_id;",
    ]
    for key, val in [
        ("_rank_math_title", obj.get("meta_title","")),
        ("_rank_math_description", obj.get("meta_description","")),
        ("rank_math_focus_keyword", obj.get("focus_keyword","")),
        ("_navar_article_vertical", item.get("vertical","")),
    ]:
        q.append(f"UPDATE `{META}` SET meta_value='{esc(val)}' WHERE post_id=@post_id AND meta_key='{esc(key)}';")
        q.append(f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'{esc(key)}','{esc(val)}' WHERE @post_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@post_id AND meta_key='{esc(key)}');")
    # Assign category
    q.append(
        f"INSERT INTO `ha_term_relationships` (`object_id`,`term_taxonomy_id`) "
        f"SELECT @post_id,{CATEGORY_TAXONOMY_ID} WHERE @post_id IS NOT NULL AND NOT EXISTS "
        f"(SELECT 1 FROM `ha_term_relationships` WHERE object_id=@post_id AND term_taxonomy_id={CATEGORY_TAXONOMY_ID});"
    )
    for idx, (image, url) in enumerate(zip(images, urls), 1):
        name = image["name"]
        image_key = f"{queue_key}:image:{idx}"
        attached_file = f"{UPLOAD_SUBDIR}/{name}"
        metadata = _php_attachment_metadata(image)
        q.append(
            f"SET @media_{idx}=(SELECT post_id FROM `{META}` WHERE meta_key='_navar_queue_image_id' AND meta_value='{esc(image_key)}' LIMIT 1); "
            f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) "
            f"SELECT 1,NOW(),UTC_TIMESTAMP(),'','{esc(item['title'])} - تصویر {idx}','','inherit','open','closed','{esc(name.rsplit('.',1)[0])}',NOW(),UTC_TIMESTAMP(),@post_id,'{esc(url)}',0,'attachment','{esc(image['mime'])}',0 WHERE @media_{idx} IS NULL AND @post_id IS NOT NULL; "
            f"SET @media_{idx}=IF(@post_id IS NULL,NULL,COALESCE(@media_{idx},LAST_INSERT_ID())); "
            f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @media_{idx},'_navar_queue_image_id','{esc(image_key)}' WHERE @media_{idx} IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@media_{idx} AND meta_key='_navar_queue_image_id'); "
            f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @media_{idx},'_wp_attached_file','{esc(attached_file)}' WHERE @media_{idx} IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@media_{idx} AND meta_key='_wp_attached_file'); "
            f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @media_{idx},'_wp_attachment_metadata','{esc(metadata)}' WHERE @media_{idx} IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@media_{idx} AND meta_key='_wp_attachment_metadata');"
        )
    q.append(f"UPDATE `{META}` SET meta_value=@media_1 WHERE post_id=@post_id AND meta_key='_thumbnail_id';")
    q.append(f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'_thumbnail_id',@media_1 WHERE @post_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@post_id AND meta_key='_thumbnail_id');")
    q.append("COMMIT;")
    rollback = (
        f"START TRANSACTION; SET @post_id=(SELECT post_id FROM `{META}` WHERE meta_key='_navar_queue_item_id' AND meta_value='{esc(queue_key)}' LIMIT 1); "
        f"DELETE pm FROM `{META}` pm JOIN `{TABLE}` p ON p.ID=pm.post_id WHERE p.post_parent=@post_id AND p.post_type='attachment'; "
        f"DELETE FROM `{TABLE}` WHERE post_parent=@post_id AND post_type='attachment'; "
        f"DELETE FROM `{META}` WHERE post_id=@post_id; "
        f"DELETE FROM `ha_term_relationships` WHERE object_id=@post_id; "
        f"DELETE FROM `{TABLE}` WHERE ID=@post_id; "
        f"COMMIT;\n"
    )
    return "\n".join(q) + "\n", rollback, body


def select_batch(q):
    """Retry failed work before starting new work, up to MAX_ATTEMPTS."""
    eligible = [
        x for x in q["items"]
        if x.get("status") in {"pending", "failed"}
        and int(x.get("attempts", 0)) < MAX_ATTEMPTS
    ]
    eligible.sort(key=lambda x: (x.get("status") != "failed", x.get("failed_at", ""), x["id"]))
    return eligible[:BATCH]


def process(q):
    # A killed runner may leave an item in processing. Make it retryable.
    for item in q["items"]:
        if item.get("status") == "processing":
            item.update(status="failed", failed_at=now(), last_error="Previous runner stopped while processing")

    if any(x["status"] == "blocked_image_model" for x in q["items"]):
        write_status(q, "blocked_image_model")
        raise RuntimeError(q.get("image_model_error", "Image model is blocked"))

    q["images_per_post"] = 5
    q.setdefault("rules", {})["layout_policy"] = "deterministic-v1"
    batch = select_batch(q)
    try:
        existing_urls = {l["url"] for l in q.get("link_index", [])}
        smlinks = [l for l in sitemap_index() if l["url"] not in existing_urls]
        if smlinks:
            q["link_index"] = q.get("link_index", []) + smlinks
    except Exception as e:
        print(f"sitemap_index warning: {type(e).__name__}: {e}", flush=True)

    if not batch:
        exhausted = any(x.get("status") == "failed" for x in q["items"])
        write_status(q, "attention_required" if exhausted else "complete")
        return

    for item in batch:
        item.update(status="processing", attempts=item["attempts"]+1, started_at=now())
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        stage = "text"
        try:
            obj = make_content(item, q["link_index"])
            stage = "image"
            images = []
            for kind in range(1, 6):
                images.append(generate_image(item, kind))
                time.sleep(2)
            # Publish media and the article through WordPress REST. Completion
            # is recorded only after WordPress confirms status=publish.
            stage = "wordpress_publish"
            from wordpress_publish_article import publish_article
            published = publish_article(item, obj, images)
            stage = "sql"
            insert, rollback, body = sql_for(item, obj, images)
            (SQL / f"{item['id']}.sql").write_text(insert, encoding="utf-8")
            (ROLLBACK / f"{item['id']}.sql").write_text(rollback, encoding="utf-8")
            (ITEMS / f"{item['id']}.json").write_text(
                json.dumps({**item, **obj, "html": published["html"], "images": images,
                            "wordpress": published},
                          ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            item.update(
                status="completed",
                completed_at=now(),
                word_count=words(body),
                images=[x["name"] for x in images],
                image_sha256=[x["sha256"] for x in images],
                wordpress_post_id=published["post_id"],
                wordpress_url=published.get("link"),
                last_error="",
            )
        except Exception as e:
            msg = str(e)[:900]
            permanent_codes = ("HTTP 400 ", "HTTP 401 ", "HTTP 403 ", "HTTP 404 ")
            blocked = stage == "image" and (
                "IMAGE_API_KEY/AGNES_API_KEY is missing" in msg
                or any(code in msg for code in permanent_codes)
            )
            item.update(status="blocked_image_model" if blocked else "failed",
                        failed_at=now(), last_error=msg, failed_stage=stage)
            if blocked:
                q["image_model_error"] = msg
                QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
                write_status(q, "blocked_image_model")
                raise
        q["updated_at"] = now()
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        write_status(q, "processing")

    (OUT / "create-all-completed.sql").write_text(
        "\n".join(["-- Review before importing. Generated articles are intentionally published."] +
                  [p.read_text(encoding="utf-8") for p in sorted(SQL.glob("*.sql"))]),
        encoding="utf-8"
    )
    (OUT / "rollback-all-completed.sql").write_text(
        "\n".join(p.read_text(encoding="utf-8") for p in sorted(ROLLBACK.glob("*.sql"))),
        encoding="utf-8"
    )
    exhausted = any(
        x.get("status") == "failed" and int(x.get("attempts", 0)) >= MAX_ATTEMPTS
        for x in q["items"]
    )
    write_status(q, "attention_required" if exhausted else "ready")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--init-only", action="store_true")
    ap.add_argument("--force-init", action="store_true")
    a = ap.parse_args()
    q = initialize(a.force_init)
    if not a.init_only:
        process(q)


if __name__ == "__main__":
    main()
