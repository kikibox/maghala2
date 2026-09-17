#!/usr/bin/env python3
"""Patch generated WordPress SQL so imported posts open directly without manual update.

Direct SQL import bypasses WordPress save hooks. The admin 'View' link may resolve to
front page until a post is opened and updated once. This post-process adds the
important permalink fields explicitly and rewrites existing SQL artifacts.
"""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'city-content-queue'
SITE='https://navar-abyari.ir'

def permalink_sql(match):
    slug=match.group('slug')
    pt=match.group('pt')
    return match.group(0)+f"\nUPDATE `ha_posts` SET `guid`='{SITE}/{pt}/{slug}/', `post_modified`=NOW(), `post_modified_gmt`=UTC_TIMESTAMP() WHERE `ID`=@post_id;"

POST_RE=re.compile(r"SET @post_id=COALESCE\(@existing_post,LAST_INSERT_ID\(\)\);(?P<body>.*?)INSERT INTO `ha_postmeta`", re.S)
SLUG_RE=re.compile(r"`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`.*?'(?P<slug>[^']+)',NOW\(\),UTC_TIMESTAMP\(\),0,'',0,'(?P<pt>[^']+)'", re.S)

def patch_text(text):
    def one(section):
        s=section.group(0)
        if 'UPDATE `ha_posts` SET `guid`=' in s:
            return s
        m=SLUG_RE.search(s)
        if not m:
            return s
        return s.replace('SET @post_id=COALESCE(@existing_post,LAST_INSERT_ID());', permalink_sql(m), 1)
    return POST_RE.sub(one, text)

def main():
    targets=[]
    targets += list((OUT/'sql').glob('*.sql')) if (OUT/'sql').exists() else []
    for name in ['create-all-completed.sql']:
        p=OUT/name
        if p.exists(): targets.append(p)
    changed=0
    for p in targets:
        old=p.read_text(encoding='utf-8')
        new=patch_text(old)
        if new!=old:
            p.write_text(new,encoding='utf-8'); changed+=1
    print(f'permalink_sql_patched={changed}')
if __name__=='__main__': main()
