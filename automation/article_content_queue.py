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
import json, os, re, time, hashlib, urllib.request, urllib.error, html, datetime as dt
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "article-content-queue"
ITEMS = OUT / "items"; SQL = OUT / "sql"; ROLLBACK = OUT / "rollback"
QUEUE = OUT / "queue.json"; STATUS = OUT / "status.json"
TOPICS_FILE = OUT / "topics.json"
CATALOG = ROOT / "data" / "article-catalog.json"

SITE = "https://navar-abyari.ir"
TABLE = "ha_posts"; META = "ha_postmeta"

# Agnes config (same as city queue)
AGNES_BASE = os.getenv("AGNES_API_BASE", "https://apihub.agnes-ai.com/v1").rstrip("/")
AGNES_KEY = os.getenv("AGNES_API_KEY", "").strip()
AGNES_MODEL = os.getenv("AGNES_MODEL", "agnes-3.0-flash")

# Image config (same as city queue — agnes-image-2.0-flash)
IMAGE_TOKEN = (os.getenv("GITHUB_MODELS_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "agnes-image-2.0-flash")
IMAGE_ENDPOINT = os.getenv("IMAGE_ENDPOINT", "https://models.github.ai/inference/images/generations")

BATCH = max(1, int(os.getenv("BATCH_SIZE", "2")))
MIN_WORDS = int(os.getenv("MIN_WORDS", "1050"))
MIN_LINKS = int(os.getenv("MIN_INTERNAL_LINKS", "4"))
MAX_ATTEMPTS = max(1, int(os.getenv("MAX_ATTEMPTS", "4")))

# Category term for article posts (from live WP dump: term_id=35)
CATEGORY_TERM_ID = int(os.getenv("ARTICLE_CATEGORY_ID", "35"))

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
    return {u for u in HREF_RE.findall(text or '') if 'navar-abyari.ir' in u}


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


def existing_index(posts):
    names = set(); links = []
    for p in posts:
        if p.get("post_status") not in {"publish","draft","pending","future","private"}:
            continue
        title = re.sub(r"^(خرید|قیمت|فروش)\s+","",p.get("post_title") or "")
        names |= {normalize(title), normalize(p.get("post_name") or "")}
        slug = (p.get("post_name") or "").strip("/")
        if slug:
            pt = p.get("post_type") or "post"
            links.append({"title": p.get("post_title") or slug,
                          "url": f"{SITE}/{slug}/" if pt == "post" else f"{SITE}/{pt}/{slug}/",
                          "post_type": pt})


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
            url = f"{SITE}/wp-json/wp/v2/posts?per_page={per_page}&page={page}&_fields=id,slug,title,post_type,post_status"
            req = _ur.Request(url, headers={"User-Agent": "navar-article-queue"})
            with _ur.urlopen(req, timeout=45) as r:
                rows = _json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
            break
        if not rows:
            break
        for row in rows:
            slug = (row.get("slug") or "").strip("/")
            status = row.get("post_status") or "publish"
            if status not in {"publish", "draft", "pending", "future", "private"}:
                continue
            title = row.get("title")
            if isinstance(title, dict):
                title = title.get("raw") or title.get("rendered") or slug
            else:
                title = title or slug
            pt = row.get("post_type") or "post"
            names.add(normalize(title)); names.add(normalize(slug))
            links.append({"title": title,
                         "url": f"{SITE}/{slug}/" if pt == "post" else f"{SITE}/{pt}/{slug}/",
                         "post_type": pt})
        # Pagination: stop if fewer rows than per_page
        if len(rows) < per_page:
            break
        page += 1
    return names, links
    return names, links


def write_status(q, result):
    c = Counter(x["status"] for x in q["items"])
    STATUS.write_text(json.dumps({
        "result": result, "updated_at": now(), "total": len(q["items"]),
        "pending": c["pending"], "processing": c["processing"],
        "completed": c["completed"], "failed": c["failed"],
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
        f"- مدل متن: `{AGNES_MODEL}`",
        f"- مدل تصویر: `{IMAGE_MODEL}`",
        f"- دستهٔ مقالات: **مقاله‌ها** (term {CATEGORY_TERM_ID})",
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
            "category_id": CATEGORY_TERM_ID,
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
        "category_id": CATEGORY_TERM_ID,
        "rules": {"draft_only": True, "minimum_words": MIN_WORDS, "minimum_internal_links": MIN_LINKS},
        "items": items,
        "link_index": links
    }
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
    write_status(q, "initialized")
    return q


def agnes(prompt):
    if not AGNES_KEY:
        raise RuntimeError("AGNES_API_KEY is missing")
    data = fetch_json(
        AGNES_BASE + "/chat/completions",
        {"Authorization": f"Bearer {AGNES_KEY}", "Content-Type": "application/json",
         "User-Agent": "navar-article-queue"},
        {"model": AGNES_MODEL,
         "messages": [
            {"role": "system", "content": "شما نویسنده ارشد فارسی در حوزه آبیاری کشاورزی هستید. فقط JSON معتبر برگردانید."},
            {"role": "user", "content": prompt}
         ],
         "temperature": 0.66,
         "max_tokens": 20000
    })
    raw = data["choices"][0]["message"]["content"].strip()
    return json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw))


def make_content(item, links):
    CONTENT_TYPES = {"post", "page", "product", "faq"}
    approved = [x for x in links if (x.get("post_type") in CONTENT_TYPES or
              (x.get("post_type") not in {"acf-field","acf-field-group","nav_menu_item","oembed_cache","rank_math_schema","wp_global_styles","elementor_library","custom_css","gp_elements","wpcf7_contact_form","customize_changeset","gp_font"}))]
    if len(approved) > 12:
        import random
        random.Random(item["id"]).shuffle(approved)
        approved = approved[:12]
    link_lines = "\n".join(f"- {x['title']} | {x['url']}" for x in approved)
    prompt = f'''برای مقاله مفید با موضوع "{item["title"]}" در حوزه آبیاری قطره‌ای و نوار تیپ، یک مقاله سئوشده و کاربردی بنویس. متن فارسی طبیعی، دست‌کم {MIN_WORDS} کلمه، بدون ادعای ساختگی درباره قیمت یا نمایندگی محلی. ساختار HTML فقط با h2/h3/p/ul/ol/table/strong/a باشد و H1 نداشته باشد. موضوعات: مقدمه، بخش‌های تخصصی مرتبط با {item["focus"]}، نکات عملی، FAQ و جمع‌بندی. حداقل {MIN_LINKS} و حداکثر ۷ لینک داخلی فقط از فهرست زیر استفاده کن. سه نشانگر دقیق [[[IMAGE_1]]], [[[IMAGE_2]]], [[[IMAGE_3]]] را هرکدام یک‌بار و بین بخش‌های مناسب بگذار. JSON با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان.
لینک‌های مجاز:
{link_lines}'''
    for _ in range(4):
        obj = agnes(prompt)
        body = obj.get("html","")
        allowed = {x["url"] for x in approved}
        body = sanitize_links(body, allowed)
        used = internal_links(body)
        if words(body) >= MIN_WORDS and MIN_LINKS <= len(used) <= 7 and \
           all(body.count(f"[[[IMAGE_{i}]]]") == 1 for i in range(1,4)) and not (used - allowed):
            return obj
        prompt += "\nنسخه قبلی کنترل کیفیت را رد کرد؛ طول، لینک‌ها یا نشانگرهای تصویر را دقیق اصلاح کن."
    raise RuntimeError("Text QA failed after 4 attempts")


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
        if _urlnorm(href) in allowed_norm or 'navar-abyari.ir' not in href:
            return tag
        return _re.sub(r'</?a\b[^>]*>', '', tag)
    return _re.sub(r'<a\b[^>]*>.*?</a>', _keep, html_text, flags=_re.I | _re.S)


def generate_image(item, kind):
    import base64
    if not IMAGE_TOKEN:
        raise RuntimeError("GITHUB_MODELS_TOKEN/GITHUB_TOKEN is missing")
    data = fetch_json(
        IMAGE_ENDPOINT,
        {"Authorization": f"Bearer {IMAGE_TOKEN}", "Content-Type": "application/json",
         "Accept": "application/json", "User-Agent": "navar-article-queue"},
        {"model": IMAGE_MODEL, "prompt": image_prompt(item, kind),
         "size": "1536x1024", "quality": "medium", "n": 1},
        300
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
    img_dir = OUT / "images"
    img_dir.mkdir(exist_ok=True)
    name = f"{item['id']}-{kind}.png"
    (img_dir / name).write_bytes(blob)
    return name, hashlib.sha256(blob).hexdigest()


def sql_for(item, obj, image_names):
    title = obj["title"]; body = obj["html"]; urls = []
    for i, name in enumerate(image_names, 1):
        url = f"{SITE}/wp-content/uploads/2026/09/navar-article-generated/{name}"
        urls.append(url)
        body = body.replace(
            f"[[[IMAGE_{i}]]]",
            f'<figure class="wp-block-image size-large"><img src="{url}" alt="{item["title"]} - تصویر {i}"/><figcaption>{item["focus"]}</figcaption></figure>'
        )
    pt = item["post_type"]; slug = item["slug"]
    excerpt = obj.get("excerpt","")
    q = [
        "START TRANSACTION;",
        f"SET @existing_post=(SELECT ID FROM `{TABLE}` WHERE `post_name`='{esc(slug)}' OR (`post_type`='{esc(pt)}' AND `post_title`='{esc(title)}') LIMIT 1);",
        f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(body)}','{esc(title)}','{esc(excerpt)}','publish','open','open','{esc(slug)}',NOW(),UTC_TIMESTAMP(),0,'',0,'{esc(pt)}','',0 WHERE @existing_post IS NULL;",
        "SET @post_id=COALESCE(@existing_post,LAST_INSERT_ID());"
    ]
    for key, val in [
        ("_rank_math_title", obj.get("meta_title","")),
        ("_rank_math_description", obj.get("meta_description","")),
        ("rank_math_focus_keyword", obj.get("focus_keyword","")),
        ("_navar_article_vertical", item.get("vertical","")),
    ]:
        q.append(f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) SELECT @post_id,'{esc(key)}','{esc(val)}' WHERE NOT EXISTS (SELECT 1 FROM `{META}` WHERE post_id=@post_id AND meta_key='{esc(key)}');")
    # Assign category
    q.append(
        f"INSERT INTO `ha_term_relationships` (`object_id`,`term_taxonomy_id`) "
        f"SELECT @post_id,{CATEGORY_TERM_ID} WHERE NOT EXISTS "
        f"(SELECT 1 FROM `ha_term_relationships` WHERE object_id=@post_id AND term_taxonomy_id={CATEGORY_TERM_ID});"
    )
    for idx, (name, url) in enumerate(zip(image_names, urls), 1):
        q.append(
            f"INSERT INTO `{TABLE}` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) "
            f"VALUES (1,NOW(),UTC_TIMESTAMP(),'','{esc(item['title'])} - تصویر {idx}','','inherit','open','closed','{esc(name.rsplit('.',1)[0])}',NOW(),UTC_TIMESTAMP(),@post_id,'{esc(url)}',0,'attachment','image/webp',0); "
            f"SET @media_{idx}=LAST_INSERT_ID(); "
            f"INSERT INTO `{META}` (`post_id`,`meta_key`,`meta_value`) VALUES (@media_{idx},'_wp_attached_file','2026/09/navar-article-generated/{esc(name)}');"
        )
    q.append("INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) VALUES (@post_id,'_thumbnail_id',@media_1);")
    q.append("COMMIT;")
    rollback = (
        f"START TRANSACTION; "
        f"DELETE pm FROM `{META}` pm JOIN `{TABLE}` p ON p.ID=pm.post_id WHERE p.post_parent=(SELECT ID FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}' LIMIT 1) AND p.post_type='attachment'; "
        f"DELETE FROM `{TABLE}` WHERE post_parent=(SELECT ID FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}' LIMIT 1) AND post_type='attachment'; "
        f"DELETE pm FROM `{META}` pm JOIN `{TABLE}` p ON p.ID=pm.post_id WHERE p.post_name='{esc(slug)}' AND post_type='{esc(pt)}'; "
        f"DELETE FROM `ha_term_relationships` WHERE object_id=(SELECT ID FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}' LIMIT 1); "
        f"DELETE FROM `{TABLE}` WHERE post_name='{esc(slug)}' AND post_type='{esc(pt)}'; "
        f"COMMIT;\n"
    )
    return "\n".join(q) + "\n", rollback, body


def process(q):
    if any(x["status"] == "blocked_image_model" for x in q["items"]):
        write_status(q, "blocked_image_model")
        raise RuntimeError(q.get("image_model_error", "Image model is blocked"))

    batch = [x for x in q["items"] if x["status"] == "pending" and x["attempts"] < MAX_ATTEMPTS][:BATCH]
    try:
        existing_urls = {l["url"] for l in q.get("link_index", [])}
        smlinks = [l for l in sitemap_index() if l["url"] not in existing_urls]
        if smlinks:
            q["link_index"] = q.get("link_index", []) + smlinks
    except Exception as e:
        print(f"sitemap_index warning: {type(e).__name__}: {e}", flush=True)

    if not batch:
        write_status(q, "complete")
        return

    for item in batch:
        item.update(status="processing", attempts=item["attempts"]+1, started_at=now())
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            obj = make_content(item, q["link_index"])
            names = []; hashes = []
            for kind in range(1, 4):
                name, digest = generate_image(item, kind)
                names.append(name); hashes.append(digest)
                time.sleep(2)
            insert, rollback, body = sql_for(item, obj, names)
            (SQL / f"{item['id']}.sql").write_text(insert, encoding="utf-8")
            (ROLLBACK / f"{item['id']}.sql").write_text(rollback, encoding="utf-8")
            (ITEMS / f"{item['id']}.json").write_text(
                json.dumps({**item, **obj, "html": body, "images": names, "image_sha256": hashes},
                          ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            item.update(status="completed", completed_at=now(), word_count=words(body), images=names, last_error="")
        except Exception as e:
            msg = str(e)[:900]
            blocked = ("models.github.ai" in msg or "Image response" in msg or
                      "GITHUB_MODELS_TOKEN" in msg or "HTTP 4" in msg)
            item.update(status="blocked_image_model" if blocked else "failed",
                        failed_at=now(), last_error=msg)
            if blocked:
                q["image_model_error"] = msg
                QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
                write_status(q, "blocked_image_model")
                raise
        q["updated_at"] = now()
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
        write_status(q, "processing")

    (OUT / "create-all-completed.sql").write_text(
        "\n".join(["-- Review before importing. Generated articles will be published."] +
                  [p.read_text(encoding="utf-8") for p in sorted(SQL.glob("*.sql"))]),
        encoding="utf-8"
    )
    (OUT / "rollback-all-completed.sql").write_text(
        "\n".join(p.read_text(encoding="utf-8") for p in sorted(ROLLBACK.glob("*.sql"))),
        encoding="utf-8"
    )
    write_status(q, "ready")


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
