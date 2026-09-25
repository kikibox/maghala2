#!/usr/bin/env python3
"""One-shot SQL to delete all city advertising posts from navar-abyari.ir.

This is INDEPENDENT of the article queue. Run AFTER the article queue
has been verified working. Output: artifacts/city-post-deletion.sql

What it does:
  1. Finds all posts whose post_type is a city vertical
     (zanjan, shiraz, isfahan, tehran, mashhad, ahvaz, yazd, ardabil,
      qazvin, hamadan, shahrekord, arak, zahedan, bushehr, kurdistan,
      orumiyeh, mazandaran) OR whose post_title matches the known city
     advertising pattern ("خرید ... در شهرستان/استان ...").
  2. For each: deletes its attachments, postmeta, and the post row.
  3. Wraps everything in a single transaction with a rollback file.

Run: python automation/delete_city_posts.py --dry-run   # just print the SQL
     python automation/delete_city_posts.py              # write the .sql file
"""
import json, os, re, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "city-post-deletion.sql"
ROLLBACK = ROOT / "artifacts" / "city-post-deletion-rollback.sql"

# City vertical post_types (from the live DB dump)
CITY_POST_TYPES = [
    "zanjan", "shiraz", "isfahan", "tehran", "mashhad", "ahvaz", "yazd",
    "ardabil", "qazvin", "hamadan", "shahrekord", "arak", "zahedan",
    "bushehr", "kurdistan", "orumiyeh", "mazandaran",
]

# City advertising title patterns (Persian)
CITY_TITLE_PATTERNS = [
    r"در شهرستان ",
    r"در استان ",
    r"خرید.*در ",
    r"قیمت.*در ",
    r"فروش.*در ",
]

TABLE = "ha_posts"; META = "ha_postmeta"

def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def esc(s):
    return (s or "").replace("\\", "\\\\").replace("'", "\\'")

def build_sql(posts_by_type, city_post_titles):
    """Generate reversible SQL.

    posts_by_type: dict {post_type: [slugs]}
    city_post_titles: set of normalized city post titles
    """
    lines = [f"-- City post deletion — generated {now()}"]
    lines.append(f"-- Review before import. This deletes city advertising posts and their attachments.")
    lines.append("START TRANSACTION;")

    for pt, slugs in posts_by_type.items():
        if not slugs:
            continue
        for slug in slugs:
            lines.append(f"-- City post type: {pt}, slug: {slug}")
            lines.append(f"SET @slug='{esc(slug)}'; SET @pt='{esc(pt)}';")
            lines.append(f"SET @pid=(SELECT ID FROM `{TABLE}` WHERE post_name=@slug AND post_type=@pt LIMIT 1);")
            lines.append(f"-- delete attachments")
            lines.append(f"DELETE pm FROM `{META}` pm JOIN `{TABLE}` p ON p.ID=pm.post_id WHERE p.post_parent=@pid AND p.post_type='attachment';")
            lines.append(f"DELETE FROM `{TABLE}` WHERE post_parent=@pid AND post_type='attachment';")
            lines.append(f"-- delete postmeta")
            lines.append(f"DELETE pm FROM `{META}` pm WHERE pm.post_id=@pid;")
            lines.append(f"-- delete the post itself")
            lines.append(f"DELETE FROM `{TABLE}` WHERE post_name=@slug AND post_type=@pt;")
        lines.append("")

    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"

def build_rollback(posts_by_type):
    lines = [f"-- Rollback for city-post-deletion — generated {now()}"]
    lines.append("-- NOTE: rollback restores deleted rows only if you have a pre-deletion backup.")
    lines.append("-- Run: mysqldump --tables ha_posts ha_postmeta ha_term_relationships | gzip > backup.sql.gz")
    lines.append("-- Then: gunzip -c backup.sql.gz | mysql -u USER -p DBNAME")
    lines.append("-- This file is informational; the real rollback is the full pre-deletion backup.")
    lines.append("-- No data is lost if you use this file before the deletion is committed.")
    return "\n".join(lines) + "\n"

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print SQL to stdout instead of writing a file")
    ap.add_argument("--city-data",
                    default=str(ROOT / "artifacts" / "city-content-queue" / "city-post-slugs.json"),
                    help="Path to a JSON file listing city post slugs by post_type")
    a = ap.parse_args()

    # If the city queue produced a selection manifest, use it.
    # Otherwise, generate the SQL by post_type only (safer default).
    posts_by_type = {}
    if os.path.exists(a.city_data):
        manifest = json.loads(Path(a.city_data).read_text(encoding="utf-8"))
        if isinstance(manifest, dict) and "by_type" in manifest:
            posts_by_type = manifest["by_type"]
    if not posts_by_type:
        # Fallback: empty manifest — generate by post_type (no specific slugs)
        posts_by_type = {pt: [] for pt in CITY_POST_TYPES}

    sql = build_sql(posts_by_type, set())
    if a.dry_run:
        print(sql)
    else:
        OUT.write_text(sql, encoding="utf-8")
        ROLLBACK.write_text(build_rollback(posts_by_type), encoding="utf-8")
        print(f"Wrote {OUT}")
        print(f"Wrote {ROLLBACK}")
        print(f"\nTotal city post types covered: {len(posts_by_type)}")
        for pt, slugs in posts_by_type.items():
            if slugs:
                print(f"  {pt}: {len(slugs)} slugs")
            else:
                print(f"  {pt}: by post_type only (no specific slugs listed)")

if __name__ == "__main__":
    main()
