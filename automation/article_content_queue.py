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
  - 1050+ words / 4-7 internal links / 3 image markers (same QA gate)

Output: artifacts/article-content-queue/
  queue.json, items/, sql/, rollback/, create-all-completed.sql
"""
import json, os, re, time, hashlib, struct, urllib.request, urllib.error, html, datetime as dt
from collections import Counter
from pathlib import Path
from agnes_json_client import call as agnes_json_call

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
    """Same as city queue: resolve sitemap posts + use link-index cache."""
    import urllib.parse as _up, json as _json, re as _re
    cache = OUT / "link-index-sitemap.json"
    if cache.exists():
        try:
            c = _json.loads(cache.read_text(encoding="utf-8"))
            if c.get("count", 0) > 0:
                return c["links"]
        except Exception:
            pass
    urls = set()
    for sm in ("post-sitemap1.xml", "post-sitemap2.xml"):
        try:
            req = urllib.request.Request(f"{SITE}/{sm}", headers={"User-Agent":"navar-article-queue"})
            with urllib.request.urlopen(req, timeout=60) as r:
                urls.update(_re.findall(r"<loc>(.*?)</loc>", r.read().decode("utf-8","replace")))
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
            title = path.replace("%","").replace("-"," ").strip() or "مقاله"
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
        "images_per_post": 3,
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
    CONTENT_TYPES = {"post", "page", "product", "faq"}
    approved = [x for x in links if (x.get("post_type") in CONTENT_TYPES or
              (x.get("post_type") not in {"acf-field","acf-field-group","nav_menu_item","oembed_cache","rank_math_schema","wp_global_styles","elementor_library","custom_css","gp_elements","wpcf7_contact_form","customize_changeset","gp_font"}))]
    if len(approved) > 12:
        import random
        random.Random(item["id"]).shuffle(approved)
        approved = approved[:12]
    if len(approved) < MIN_LINKS:
        raise RuntimeError(f"Text QA cannot run: only {len(approved)} approved internal links available")
    link_lines = "\n".join(f"- {x['title']} | {x['url']}" for x in approved)
    target_words = max(MIN_WORDS + 250, 1300)
    prompt = f'''برای مقاله مفید با موضوع "{item["title"]}" در حوزه آبیاری قطره‌ای و نوار تیپ، یک مقاله سئوشده و کاربردی بنویس. متن فارسی طبیعی، دست‌کم {target_words} کلمه، بدون ادعای ساختگی درباره قیمت یا نمایندگی محلی. ساختار HTML فقط با h2/h3/p/ul/ol/table/strong/a باشد و H1 نداشته باشد. موضوعات: مقدمه، بخش‌های تخصصی مرتبط با {item["focus"]}، نکات عملی، FAQ و جمع‌بندی. حداقل {MIN_LINKS} و حداکثر ۷ لینک داخلی فقط از فهرست زیر استفاده کن. سه نشانگر دقیق [[[IMAGE_1]]], [[[IMAGE_2]]], [[[IMAGE_3]]] را هرکدام یک‌بار و بین بخش‌های مناسب بگذار. JSON با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.
لینک‌های مجاز:
{link_lines}'''
    obj = None
    last_errors = []
    allowed = {x["url"] for x in approved}
    for attempt in range(1, 5):
        if attempt == 1:
            obj = agnes(prompt)
        else:
            repair_prompt = f'''نسخه زیر در کنترل کیفیت رد شده است. همان مقاله را ویرایش کن و کوتاه یا از نو بازنویسی نکن. خطاهای دقیق: {'; '.join(last_errors)}. متن را به دست‌کم {target_words} کلمه برسان، فقط {MIN_LINKS} تا ۷ لینک از فهرست مجاز نگه دار و هر سه نشانگر تصویر را دقیقاً یک‌بار حفظ کن. فقط JSON معتبر با همان شش کلید برگردان.
لینک‌های مجاز:
{link_lines}
نسخه قبلی:
{json.dumps(obj, ensure_ascii=False)}'''
            obj = agnes(repair_prompt)
        if not isinstance(obj, dict):
            last_errors = ["response is not a JSON object"]
            continue
        body = sanitize_links(obj.get("html", ""), allowed)
        used = internal_links(body)
        errors = []
        word_count = words(body)
        if word_count < MIN_WORDS:
            errors.append(f"word count {word_count} below {MIN_WORDS}")
        if not (MIN_LINKS <= len(used) <= 7):
            errors.append(f"internal link count {len(used)} outside {MIN_LINKS}-7")
        if used - allowed:
            errors.append("unapproved internal links remain")
        for i in range(1, 4):
            marker_count = body.count(f"[[[IMAGE_{i}]]]")
            if marker_count != 1:
                errors.append(f"IMAGE_{i} marker count is {marker_count}, expected 1")
        for key in ("title", "meta_title", "meta_description", "focus_keyword", "excerpt", "html"):
            if not obj.get(key):
                errors.append(f"missing {key}")
        if not errors:
            obj["html"] = body
            return obj
        obj["html"] = body
        last_errors = errors
    raise RuntimeError("Text QA failed after 4 attempts: " + "; ".join(last_errors))


def image_prompt(item, kind):
    scenes = {
        1: "wide hero view of a modern agricultural field with drip irrigation system clearly visible",
        2: "close technical view of drip irrigation components, filter, and regulator in a clean farm setting",
        3: "farmer hands inspecting drip tape rows, no identifiable face"
    }
    vertical_desc = {
        "crop": f"showing {item.get('focus','crop')} field context",
        "product": "showing drip tape and pipe products on a clean white background",
        "strategic": "showing a well-designed drip irrigation system layout",
        "irrigation": "showing an irrigation method in a farm field",
        "xref": "showing drip irrigation in a crop field with visible drip tape lines"
    }
    v = vertical_desc.get(item.get("vertical",""), "showing a drip irrigation farm")
    return f"Photorealistic editorial agriculture image, {scenes[kind]}, {v}, natural light, no text, no logo, no watermark, no labels, 16:9 composition"


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
    data = fetch_json(
        IMAGE_ENDPOINT,
        {"Authorization": f"Bearer {IMAGE_TOKEN}", "Content-Type": "application/json",
         "Accept": "application/json", "User-Agent": "navar-article-queue"},
        {"model": IMAGE_MODEL, "prompt": image_prompt(item, kind),
         "size": "1024x768", "return_base64": True,
         "extra_body": {"response_format": "b64_json"}},
        600
    )
    row = data["data"][0]
    if row.get("b64_json"):
        blob = base64.b64decode(row["b64_json"])
    elif row.get("url"):
        with urllib.request.urlopen(row["url"], timeout=180) as r:
            blob = r.read()
    else:
        raise RuntimeError("Image response has neither b64_json nor url")
    if len(blob) < 10000:
        raise RuntimeError("Generated image is unexpectedly small")
    # Normalize every provider response to a real 16:9 JPEG so the extension,
    # MIME type, dimensions, SQL metadata, and public file all agree.
    image = Image.open(io.BytesIO(blob)).convert("RGB")
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
    suffix, mime, width, height = image_info(blob)
    img_dir = OUT / "images"
    img_dir.mkdir(exist_ok=True)
    name = f"{item['id']}-{kind}{suffix}"
    (img_dir / name).write_bytes(blob)
    return {
        "name": name,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "mime": mime,
        "width": width,
        "height": height,
    }


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

    batch_errors = []
    for item in batch:
        item.update(status="processing", attempts=item["attempts"]+1, started_at=now())
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        stage = "text"
        try:
            obj = make_content(item, q["link_index"])
            stage = "image"
            images = []
            for kind in range(1, 4):
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
            batch_errors.append(f"{item['id']} ({stage}): {msg}")
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
    if batch_errors:
        raise RuntimeError("Queue item failed: " + " | ".join(batch_errors))


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
