#!/usr/bin/env python3
"""Translate completed article-queue items before allowing new Persian articles."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path

import translate_queue as translator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "article-content-queue"
ITEMS = OUT / "items"
QUEUE = OUT / "queue.json"
TRANS = OUT / "translations"
SQL = OUT / "translation-sql"
ROLLBACK = OUT / "translation-rollback"
STATUS = OUT / "translation-status.json"
LANGUAGES = ("ar-IQ", "tg-TJ", "en-US")
PREFIX = {"ar-IQ": "iraq", "tg-TJ": "tj", "en-US": "en"}
BATCH = max(1, int(os.getenv("GENERATED_TRANSLATION_BATCH_SIZE", "2")))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def esc(value) -> str:
    return str(value or "").replace("\\", "\\\\").replace("'", "\\'").replace("\0", "\\0").replace("\n", "\\n").replace("\r", "\\r")


def completed_sources():
    if not QUEUE.exists():
        return []
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    rows = []
    for item in queue.get("items", []):
        if item.get("status") != "completed":
            continue
        item_id = str(item.get("id") or "")
        path = ITEMS / f"{item_id}.json"
        if not item_id or not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append((item, data))
    rows.sort(key=lambda pair: pair[0].get("completed_at", ""))
    return rows


def missing_languages(item_id: str):
    folder = TRANS / item_id
    return [lang for lang in LANGUAGES if not (folder / f"{lang}.json").exists()]


def translate_small_text(text: str, lang: str) -> str:
    if not text:
        return ""
    return translator.translate_segment_batch([{"id": 0, "text": text}], lang)[0]


def build_sql(item: dict, translated: dict, lang: str) -> tuple[str, str]:
    item_id = str(item["id"])
    key = f"article-translation:{item_id}:{lang}"
    source_key = f"article-content-queue:{item_id}"
    slug = translated["slug"]
    category_slug = PREFIX[lang]
    body = translated["html"]
    lines = [
        "START TRANSACTION;",
        f"SET @source_post_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_queue_item_id' AND meta_value='{esc(source_key)}' LIMIT 1);",
        f"SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='{esc(key)}' LIMIT 1);",
        f"SET @slug_conflict=(SELECT ID FROM `ha_posts` WHERE post_name='{esc(slug)}' AND post_type='post' AND (@translation_id IS NULL OR ID<>@translation_id) LIMIT 1);",
        f"INSERT INTO `ha_posts` (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`) SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(body)}','{esc(translated['title'])}','{esc(translated.get('excerpt',''))}','publish','closed','closed','{esc(slug)}',NOW(),UTC_TIMESTAMP(),0,'',0,'post','',0 WHERE @source_post_id IS NOT NULL AND @translation_id IS NULL AND @slug_conflict IS NULL;",
        "SET @translation_id=COALESCE(@translation_id,IF(@source_post_id IS NOT NULL AND @slug_conflict IS NULL,LAST_INSERT_ID(),NULL));",
    ]
    metadata = [
        ("_navar_translation_queue_key", key),
        ("_navar_translation_source_id", "@source_post_id"),
        ("_navar_translation_language", lang),
        ("_rank_math_title", translated.get("meta_title", "")),
        ("_rank_math_description", translated.get("meta_description", "")),
        ("rank_math_focus_keyword", translated.get("focus_keyword", "")),
    ]
    for meta_key, value in metadata:
        sql_value = value if value == "@source_post_id" else f"'{esc(value)}'"
        lines.append(
            f"INSERT INTO `ha_postmeta` (`post_id`,`meta_key`,`meta_value`) SELECT @translation_id,'{esc(meta_key)}',{sql_value} WHERE @translation_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `ha_postmeta` WHERE post_id=@translation_id AND meta_key='{esc(meta_key)}');"
        )
    lines += [
        f"INSERT INTO `ha_term_relationships` (`object_id`,`term_taxonomy_id`,`term_order`) SELECT @translation_id,tt.term_taxonomy_id,0 FROM `ha_term_taxonomy` tt JOIN `ha_terms` t ON t.term_id=tt.term_id WHERE @translation_id IS NOT NULL AND tt.taxonomy='category' AND t.slug='{esc(category_slug)}' AND NOT EXISTS (SELECT 1 FROM `ha_term_relationships` r WHERE r.object_id=@translation_id AND r.term_taxonomy_id=tt.term_taxonomy_id) LIMIT 1;",
        "COMMIT;",
    ]
    rollback = (
        "START TRANSACTION; "
        f"SET @translation_id=(SELECT post_id FROM `ha_postmeta` WHERE meta_key='_navar_translation_queue_key' AND meta_value='{esc(key)}' LIMIT 1); "
        "DELETE FROM `ha_term_relationships` WHERE object_id=@translation_id; "
        "DELETE FROM `ha_postmeta` WHERE post_id=@translation_id; "
        "DELETE FROM `ha_posts` WHERE ID=@translation_id; COMMIT;\n"
    )
    return "\n".join(lines) + "\n", rollback


def rebuild_combined_sql():
    files = sorted(SQL.glob("*.sql")) if SQL.exists() else []
    (OUT / "create-all-translations.sql").write_text(
        "-- Generated article translations: Arabic, Tajik and English.\nSET NAMES utf8mb4;\n\n"
        + "\n".join(path.read_text(encoding="utf-8") for path in files),
        encoding="utf-8",
    )
    rollback_files = sorted(ROLLBACK.glob("*.sql"), reverse=True) if ROLLBACK.exists() else []
    (OUT / "rollback-all-translations.sql").write_text(
        "-- Roll back generated article translations.\nSET NAMES utf8mb4;\n\n"
        + "\n".join(path.read_text(encoding="utf-8") for path in rollback_files),
        encoding="utf-8",
    )


def status_payload():
    sources = completed_sources()
    per_language = {}
    for lang in LANGUAGES:
        complete = sum((TRANS / str(item["id"]) / f"{lang}.json").exists() for item, _ in sources)
        per_language[lang] = {"completed": complete, "pending": len(sources) - complete}
    backlog_sources = sum(bool(missing_languages(str(item["id"]))) for item, _ in sources)
    image_marker = OUT / "image-rebuild-reference-rerender-3d-v3.json"
    image_data = {}
    if image_marker.exists():
        try:
            image_data = json.loads(image_marker.read_text(encoding="utf-8"))
        except Exception:
            image_data = {}
    payload = {
        "updated_at": now(),
        "source_articles_completed": len(sources),
        "languages": per_language,
        "total_translation_units": len(sources) * len(LANGUAGES),
        "completed_translation_units": sum(row["completed"] for row in per_language.values()),
        "pending_translation_units": sum(row["pending"] for row in per_language.values()),
        "articles_missing_any_translation": backlog_sources,
        "persian_queue_paused": backlog_sources > 0,
        "images": {
            "policy": image_data.get("policy"),
            "completed": bool(image_data.get("completed")),
            "failures": len(image_data.get("failures", [])),
            "total_candidates": image_data.get("total_candidates", len(sources)),
        },
    }
    package_manifest = OUT / "translation-packages" / "manifest.json"
    package_data = {"batch_size": 50, "ready_batches": 0, "packages": []}
    if package_manifest.exists():
        try:
            package_data.update(json.loads(package_manifest.read_text(encoding="utf-8")))
        except Exception:
            pass
    payload["packages"] = package_data
    STATUS.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-backlog", action="store_true")
    args = parser.parse_args()
    initial = status_payload()
    if args.check_backlog:
        print(initial["articles_missing_any_translation"])
        return 2 if initial["articles_missing_any_translation"] else 0
    if not translator.TOKEN:
        raise RuntimeError("AGNES_API_KEY is empty")
    TRANS.mkdir(parents=True, exist_ok=True);SQL.mkdir(parents=True, exist_ok=True);ROLLBACK.mkdir(parents=True, exist_ok=True)
    processed_sources = 0
    for item, data in completed_sources():
        item_id = str(item["id"])
        missing = missing_languages(item_id)
        if not missing:
            continue
        source = {
            "id": item_id,
            "title": data.get("title") or item.get("title"),
            "slug": item.get("slug", ""),
            "date": item.get("completed_at", ""),
            "content": data.get("html", ""),
        }
        folder = TRANS / item_id;folder.mkdir(parents=True, exist_ok=True)
        for lang in missing:
            result = translator.translate_validated(source, lang)
            result["excerpt"] = translate_small_text(data.get("excerpt", ""), lang)
            result["focus_keyword"] = result["title"]
            result["meta_title"] = result.pop("seo_title")
            result["meta_description"] = result.pop("seo_description")
            result.update({
                "source_id": item_id,
                "language": lang,
                "source_title": source["title"],
                "source_slug": source["slug"],
                "validated": True,
                "provider": "Agnes AI",
                "model": translator.MODEL,
            })
            (folder / f"{lang}.html").write_text(result["html"], encoding="utf-8")
            (folder / f"{lang}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            create_sql, rollback_sql = build_sql(item, result, lang)
            (SQL / f"{item_id}-{lang}.sql").write_text(create_sql, encoding="utf-8")
            (ROLLBACK / f"{item_id}-{lang}.sql").write_text(rollback_sql, encoding="utf-8")
            print(f"generated_translation source={item_id} language={lang}", flush=True)
        processed_sources += 1
        if processed_sources >= BATCH:
            break
    rebuild_combined_sql()
    final = status_payload()
    print(json.dumps(final, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())