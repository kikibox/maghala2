#!/usr/bin/env python3
"""Package completed ad posts into upload-ready zips (SQL + rollback + images + manifest).

Each zip: create.sql, rollback.sql, images/*.webp (upload to wp-content/uploads/2026/10/navar-tj-ads/), manifest.csv, preview/*.html.
Size per batch: PACKAGE_SIZE (default 25 posts) so phpMyAdmin imports stay small.
"""
import csv, json, os, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/tj-ads'
PKG = OUT / 'packages'
SIZE = int(os.getenv('PACKAGE_SIZE', '50'))   # items per ZIP (each item = 1 Tajik + 1 Russian post), same as maghala2 article packages


def main():
    PKG.mkdir(parents=True, exist_ok=True)
    done = sorted((OUT / 'items').glob('*.json'))
    rows = [json.loads(p.read_text(encoding='utf-8')) for p in done]
    rows.sort(key=lambda r: r['seq'])
    n = 0
    for i in range(0, len(rows), SIZE):
        chunk = rows[i:i + SIZE]
        name = PKG / f'tj-ads-batch-{i // SIZE + 1:03d}.zip'
        if name.exists() and name.stat().st_size and os.getenv('REBUILD') != '1':
            continue
        with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('create.sql', 'SET NAMES utf8mb4;\n' + '\n'.join((OUT / 'sql' / f"{r['id']}.sql").read_text(encoding='utf-8') for r in chunk))
            for extra in ('pillar-pages.sql', 'pillar-pages-ROLLBACK.sql'):
                if (ROOT / 'wp' / extra).exists(): z.write(ROOT / 'wp' / extra, extra)
            z.writestr('rollback.sql', 'SET NAMES utf8mb4;\n' + '\n'.join((OUT / 'rollback' / f"{r['id']}.sql").read_text(encoding='utf-8') for r in chunk))
            for r in chunk:
                for img in r['images']:
                    z.write(OUT / 'images' / img, f'images/{img}')
            import io
            buf = io.StringIO(); w = csv.writer(buf); w.writerow(['seq', 'id', 'lang', 'title', 'slug', 'url', 'place', 'product', 'crop', 'words'])
            for r in chunk:
                for p in r['posts']:
                    w.writerow([r['seq'], r['id'], p['lang'], p['title'], p['slug'], p['url'], r['place_en'], r['product'], r['crop_tg'], r.get('word_count', '')])
                    z.writestr(f"preview/{r['id']}-{p['lang']}.html", '<!doctype html><meta charset="utf-8"><body style="max-width:820px;margin:auto;font:16px/1.7 sans-serif"><h1>' + p['title'] + '</h1>' + p['body'].replace('/wp-content/uploads/2026/10/navar-tj-ads/', '../images/'))
            z.writestr('manifest.csv', '\ufeff' + buf.getvalue())
        n += 1
    print(f'{n} package(s) written to {PKG}')


if __name__ == '__main__':
    main()
