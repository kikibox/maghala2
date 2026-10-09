#!/usr/bin/env python3
"""Smoke-test generated SQL on an in-memory SQLite copy of the two WP tables.

It is NOT a MySQL test (no MySQL here); it checks that the SQL is idempotent
(2nd run changes nothing), links post/attachments/meta correctly and that the
ROLLBACK removes everything. Always test on a DB copy before the live site.
"""
import re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/tj-ads'
STR = re.compile(r"'(?:[^'\\]|\\.|'')*'", re.S)


def conv(m):
    raw = m.group(0)[1:-1]
    raw = re.sub(r'\\(.)', lambda x: {'n': '\n', 'r': '\r', '0': '\0'}.get(x.group(1), x.group(1)), raw)
    return "'" + raw.replace("'", "''") + "'"


def split(sql):
    sql = STR.sub(conv, sql); res, cur, q = [], '', False
    for ch in sql:
        if ch == "'": q = not q
        if ch == ';' and not q: res.append(cur.strip()); cur = ''
        else: cur += ch
    return [r for r in (x.strip() for x in res + [cur]) if r]


def db_new():
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE ha_posts (ID INTEGER PRIMARY KEY AUTOINCREMENT, post_author, post_date, post_date_gmt, post_content, post_title, post_excerpt, post_status, comment_status, ping_status, post_name, post_modified, post_modified_gmt, post_parent, guid, menu_order, post_type, post_mime_type, comment_count, to_ping, pinged, post_content_filtered)')
    db.execute('CREATE TABLE ha_postmeta (meta_id INTEGER PRIMARY KEY AUTOINCREMENT, post_id, meta_key, meta_value)')
    db.execute('CREATE TABLE ha_terms (term_id INTEGER PRIMARY KEY AUTOINCREMENT, name, slug, term_group)')
    db.execute('CREATE TABLE ha_term_taxonomy (term_taxonomy_id INTEGER PRIMARY KEY AUTOINCREMENT, term_id, taxonomy, description, parent, count)')
    db.execute('CREATE TABLE ha_term_relationships (object_id, term_taxonomy_id, term_order)')
    # pre-existing site data that must survive untouched
    db.execute("INSERT INTO ha_terms (name, slug, term_group) VALUES ('Persian articles','maqalat',0)")
    db.execute("INSERT INTO ha_term_taxonomy (term_id, taxonomy, description, parent, count) VALUES (1,'category','',0,5)")
    return db


def run(db, sql):
    var = {}
    for st in split(sql):
        st = '\n'.join(l for l in st.split('\n') if not l.startswith('--')).strip()
        if not st or st.startswith('SET NAMES'): continue
        if st in ('START TRANSACTION', 'COMMIT'): continue
        st = st.replace('UTC_TIMESTAMP()', "datetime('now')").replace('NOW()', "datetime('now')").replace('FROM DUAL', '')
        m2 = re.match(r'SET @(\w+) := @(\w+)$', st)
        if m2: var[m2.group(1)] = var.get(m2.group(2)); continue
        m = re.match(r'SET @(\w+) := \((.*)\)$', st, re.S)
        if m:
            r = db.execute(subst(m.group(2), var)).fetchone(); var[m.group(1)] = r[0] if r else None; continue
        db.execute(subst(st, var))
    db.commit()


def subst(st, var):
    return re.sub(r'@(\w+)', lambda m: 'NULL' if var.get(m.group(1)) is None else str(var[m.group(1)]), st)


def snap(db):
    return tuple(db.execute(f'select count(*) from {t}').fetchone()[0] for t in ('ha_posts', 'ha_postmeta', 'ha_term_relationships')) + (db.execute("select count from ha_term_taxonomy where term_id=1").fetchone()[0],)


def main():
    files = sorted((OUT / 'sql').glob('*.sql'))
    if not files: sys.exit('no SQL files; run ads_queue.py first (use --mock)')
    db = db_new(); base = snap(db)
    for f in files: run(db, f.read_text(encoding='utf-8'))
    first = snap(db)
    for f in files: run(db, f.read_text(encoding='utf-8'))
    assert snap(db) == first, 'SQL is not idempotent'
    n = len(files)
    posts = db.execute("select count(*) from ha_posts where post_type='post' and post_status='publish'").fetchone()[0]
    atts = db.execute("select count(*) from ha_posts where post_type='attachment'").fetchone()[0]
    thumbs = db.execute("select count(*) from ha_postmeta where meta_key='_thumbnail_id' and meta_value in (select ID from ha_posts where post_type='attachment')").fetchone()[0]
    rels = db.execute("select count(*) from ha_term_relationships").fetchone()[0]
    cats = db.execute("select count(*) from ha_terms where slug like 'tajikistan-ads-%'").fetchone()[0]
    counts = [r[0] for r in db.execute("select count from ha_term_taxonomy where term_id>1")]
    st = db.execute("select distinct post_status from ha_posts where post_type='post'").fetchall()
    assert posts == 2 * n and atts == 3 * n and thumbs == 2 * n and rels == 2 * n and cats == 2, (posts, atts, thumbs, rels, cats)
    assert sorted(counts) == [n, n], counts
    for f in sorted((OUT / 'rollback').glob('*.sql')): run(db, f.read_text(encoding='utf-8'))
    assert snap(db) == base, ('rollback incomplete', snap(db))
    print(f'OK: {n} items = {posts} published posts (tg+ru), {atts} attachments, status={st}, idempotent, rollback clean')


if __name__ == '__main__':
    main()
