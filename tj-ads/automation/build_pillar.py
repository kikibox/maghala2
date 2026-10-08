#!/usr/bin/env python3
"""Build the pillar page ("production line + cooperation") as HTML + reversible SQL (draft).

Quotes are taken verbatim from config/government_context.json (each verified against president.tj).
Outputs: wp/pillar-page.html, wp/pillar-page.sql, wp/pillar-page-ROLLBACK.sql
"""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cfg = lambda n: json.loads((ROOT / 'config' / n).read_text(encoding='utf-8'))
gov, src, prod, pool = cfg('government_context.json'), cfg('sources.json')['sources'], cfg('products.json'), cfg('link_pool.json')
Q = {q['id']: q for q in gov['quotes']}
SLUG = gov['pillar_page_slug']
TITLE = pool['pillar']['title']
SITE = 'https://navar-abyari.ir'
ph = prod['company']['phone_display']
esc = lambda s: str(s).replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')


def quote(qid):
    q = Q[qid]; s = src[q['source']]
    return (f'<blockquote><p>«{html.escape(q["text_tg"])}»</p><p><small>Сарчашма: <a href="{s["url"]}" rel="nofollow noopener" target="_blank">{html.escape(s["title"])}</a>, {q["date"]}.</small></p></blockquote>')


BODY = f'''<p>AFP — ширкати истеҳсолкунандаи лентаи обёрии қатрагӣ, қубури полиэтиленӣ ва қубури қатшавандаи риштадор дар шаҳри Наҷафобод (вилояти Исфаҳон, Эрон). Дар ин саҳифа мо мухтасар нишон медиҳем, ки чӣ истеҳсол мекунем ва чӣ гуна бо деҳқонон ва ташкилотҳои соҳаи кишоварзии Тоҷикистон ҳамкорӣ карда метавонем.</p>
<h2>Хати истеҳсолот</h2>
<ul>
<li><strong>Лентаи обёрии қатрагӣ</strong> — барои зироатҳои қаторӣ: пахта, сабзавот, харбуза ва тарбуз. <a href="{SITE}/product/tg-tj-product-969/">Маҳсулотро бинед</a>.</li>
<li><strong>Қубури полиэтиленӣ</strong> — барои хатҳои асосӣ ва тақсимкунандаи об дар киштзор.</li>
<li><strong>Қубури қатшавандаи риштадор</strong> — барои интиқоли об аз канал ё насос ба киштзор. <a href="{SITE}/product/tg-tj-product-37848/">Маҳсулотро бинед</a>.</li>
</ul>
<p>Пеш аз ҳар фармоиш мо тавсия медиҳем, ки <a href="{SITE}/tg-tj-sanjishi-zamin/">замини кишоварзӣ санҷида шавад</a> ва <a href="{SITE}/tg-tj-sanjishhoi-sifat/">санҷишҳои сифати маҳсулот</a> дида шаванд.</p>
<h2>Чаро об ва замин барои Тоҷикистон муҳим аст</h2>
<p>Мувофиқи маълумоти ошкоро, танҳо тақрибан 28% хоки Тоҷикистон замини кишоварзӣ аст ва кишоварзии кишвар ба обёрӣ вобаста аст. Дар баъзе минтақаҳо, масалан дар Истаравшан ва ҳавзаи Қизилсув–Яхсу дар атрофи Кӯлоб, обёришавӣ талаботро пурра қонеъ намекунад. <small>(Сарчашма: <a href="{src['S1']['url']}" rel="nofollow noopener" target="_blank">{html.escape(src['S1']['title'])}</a>.)</small></p>
<h2>Аз суханони расмии соли 2026</h2>
<p>Дар паёми Наврӯзии соли 2026 ва суханронии 30 марти ҳамон сол масъалаи истифодаи оқилонаи об ва замин ҳамчун афзалият зикр шудааст:</p>
{quote('nowruz-2026-water-land')}
{quote('mastchoh-2026-water')}
<p><em>Иқтибосҳо барои иттилоъ оварда шудаанд ва маънои тасдиқ ё дастгирии маҳсулоти AFP-ро аз ҷониби мақомоти давлатӣ надоранд.</em></p>
<h2>Ҳамкорӣ бо AFP</h2>
<p>Бо дарназардошти афзалияти рушди кишоварзӣ ва истифодаи самараноки об, мо омодаем бо хоҷагиҳои деҳқонӣ, корхонаҳои кишоварзӣ, шарикони тиҷоратӣ ва ташкилотҳои соҳа оид ба интихоби лента ва қубур машварат кунем. Нарх, шартҳои харид ва расонидани маҳсулот ба Тоҷикистон ҳангоми тамос алоҳида мувофиқа мешаванд. Маҳсулот кафолат дорад (<a href="{SITE}/tg-tj-kafolat/">шартҳои кафолат</a>); тафсилоти хизмати баъдифурӯшро дар <a href="{SITE}/tg-tj-hizmatrasoni/">ин саҳифа</a> бинед.</p>
<p><strong>Тамос:</strong> <a href="tel:{ph.replace(' ', '')}">{ph}</a> · <a href="{SITE}/tg-tj-tamos/">саҳифаи тамос</a> · <a href="{SITE}/tg-tj-shakli-darhost/">шакли дархост</a> · <a href="{SITE}/tj-rules/">қоидаҳои харид</a>.</p>'''


def sql():
    t = '`ha_posts`'; m = '`ha_postmeta`'
    ins = (f"INSERT INTO {t} (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`,`to_ping`,`pinged`,`post_content_filtered`) "
           f"SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(BODY)}','{esc(TITLE)}','','draft','closed','closed','{SLUG}',NOW(),UTC_TIMESTAMP(),0,'{SITE}/{SLUG}/',0,'page','',0,'','','' FROM DUAL "
           f"WHERE NOT EXISTS (SELECT 1 FROM {t} WHERE `post_name`='{SLUG}' AND `post_type`='page');")
    metas = [('_rank_math_title', 'Хати истеҳсолот ва ҳамкорӣ бо кишоварзии Тоҷикистон | AFP'), ('_rank_math_description', 'AFP — истеҳсолкунандаи лентаи обёрии қатрагӣ, қубури полиэтиленӣ ва қубури қатшавандаи риштадор. Шартҳои ҳамкорӣ бо деҳқонон ва ташкилотҳои Тоҷикистон.'),
             ('rank_math_focus_keyword', 'лентаи обёрии қатрагӣ Тоҷикистон'), ('_navar_translation_language', 'tg-TJ')]
    out = ['START TRANSACTION;', ins, f"SET @pid := (SELECT `ID` FROM {t} WHERE `post_name`='{SLUG}' AND `post_type`='page' ORDER BY `ID` LIMIT 1);"]
    out += [f"INSERT INTO {m} (`post_id`,`meta_key`,`meta_value`) SELECT @pid,'{k}','{esc(v)}' FROM DUAL WHERE @pid IS NOT NULL AND NOT EXISTS (SELECT 1 FROM {m} WHERE `post_id`=@pid AND `meta_key`='{k}');" for k, v in metas]
    out.append('COMMIT;')
    rb = ['START TRANSACTION;', f"SET @pid := (SELECT `ID` FROM {t} WHERE `post_name`='{SLUG}' AND `post_type`='page' ORDER BY `ID` LIMIT 1);",
          f"DELETE FROM {m} WHERE `post_id`=@pid AND @pid IS NOT NULL;", f"DELETE FROM {t} WHERE `ID`=@pid AND `post_type`='page' AND @pid IS NOT NULL;", 'COMMIT;']
    return 'SET NAMES utf8mb4;\n-- Pillar page is inserted as DRAFT: review, then Publish.\n' + '\n'.join(out) + '\n', 'SET NAMES utf8mb4;\n' + '\n'.join(rb) + '\n'


def main():
    (ROOT / 'wp').mkdir(exist_ok=True)
    (ROOT / 'wp/pillar-page.html').write_text(BODY, encoding='utf-8')
    a, b = sql()
    (ROOT / 'wp/pillar-page.sql').write_text(a, encoding='utf-8'); (ROOT / 'wp/pillar-page-ROLLBACK.sql').write_text(b, encoding='utf-8')
    print('pillar page written')


if __name__ == '__main__':
    main()
