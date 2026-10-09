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

SLUG_RU = json.loads((ROOT / 'config/i18n.json').read_text(encoding='utf-8'))['pillar']['ru_slug']
TITLE_RU = 'Производство и сотрудничество с сельским хозяйством Таджикистана'


def quote_ru(qid, text, label):
    q = Q[qid]; s = src[q['source']]
    return (f'<blockquote><p>«{text}»</p><p><small>Источник (оригинал на таджикском): <a href="{s["url"]}" rel="nofollow noopener" target="_blank">{label}</a>, {q["date"]}. Неофициальный перевод.</small></p></blockquote>')


BODY_RU = f'''<p>AFP — производитель капельной ленты, полиэтиленовых труб и армированных нитью плоскосворачиваемых рукавов (layflat) в городе Наджафабад (провинция Исфахан, Иран). На этой странице мы кратко рассказываем, что производим и как можем сотрудничать с фермерами и организациями аграрного сектора Таджикистана.</p>
<h2>Что мы производим</h2>
<ul>
<li><strong>Капельная лента</strong> — для рядковых культур: хлопка, овощей, дынь и арбузов. <a href="{SITE}/product/tg-tj-product-969/">Смотреть продукцию</a>.</li>
<li><strong>Полиэтиленовая труба</strong> — для магистральных и распределительных линий воды на поле.</li>
<li><strong>Армированный нитью плоскосворачиваемый рукав (layflat)</strong> — для подачи воды из канала или от насоса на поле. <a href="{SITE}/product/tg-tj-product-37848/">Смотреть продукцию</a>.</li>
</ul>
<p>Перед каждым заказом рекомендуем <a href="{SITE}/tg-tj-sanjishi-zamin/">оценить землю</a> и ознакомиться с <a href="{SITE}/tg-tj-sanjishhoi-sifat/">проверками качества продукции</a>.</p>
<h2>Почему вода и земля важны для Таджикистана</h2>
<p>По открытым данным, лишь около 28% территории Таджикистана занимают сельскохозяйственные земли, а сельское хозяйство страны зависит от орошения. В некоторых районах, например в Истаравшане и в бассейне Кызылсу–Яхсу возле Куляба, орошение не полностью покрывает потребность в воде. <small>(Источник: <a href="{src['S1']['url']}" rel="nofollow noopener" target="_blank">{html.escape(src['S1']['title'])}</a>.)</small></p>
<h2>Из официальных выступлений 2026 года</h2>
<p>В новогоднем (Навруз) обращении 2026 года и в выступлении 30 марта того же года рациональное использование воды и земли названо приоритетом:</p>
{quote_ru('nowruz-2026-water-land', 'Поэтому мы должны эффективно и рационально использовать все имеющиеся у нас ресурсы и возможности, в том числе каждую пядь земли и воду.', 'Поздравление Президента по случаю Навруза, 19.03.2026 (president.tj)')}
{quote_ru('mastchoh-2026-water', 'Подчёркиваю, что рациональное использование воды и каждой пяди земли является важным условием обеспечения развития национальной экономики, продовольственной безопасности страны и достойной жизни народа.', 'Выступление Президента в Мастчохе, 30.03.2026 (president.tj)')}
<p><em>Цитаты приведены для информации и не означают одобрения или поддержки продукции AFP со стороны государственных органов.</em></p>
<h2>Сотрудничество с AFP</h2>
<p>Учитывая приоритет развития сельского хозяйства и эффективного использования воды, мы готовы консультировать фермерские хозяйства, сельскохозяйственные предприятия, торговых партнёров и отраслевые организации по выбору ленты и труб. Цена, условия покупки и доставки в Таджикистан согласовываются отдельно при обращении. На продукцию распространяется гарантия (<a href="{SITE}/tg-tj-kafolat/">условия гарантии</a>); подробности о послепродажном обслуживании — на <a href="{SITE}/tg-tj-hizmatrasoni/">этой странице</a>.</p>
<p><strong>Контакты:</strong> <a href="tel:{ph.replace(' ', '')}">{ph}</a> · <a href="{SITE}/tg-tj-tamos/">страница контактов</a> · <a href="{SITE}/tg-tj-shakli-darhost/">форма заявки</a> · <a href="{SITE}/tj-rules/">правила покупки</a>.</p>'''


def sql(SLUG, TITLE, BODY, metas, status='publish'):
    t = '`ha_posts`'; m = '`ha_postmeta`'
    ins = (f"INSERT INTO {t} (`post_author`,`post_date`,`post_date_gmt`,`post_content`,`post_title`,`post_excerpt`,`post_status`,`comment_status`,`ping_status`,`post_name`,`post_modified`,`post_modified_gmt`,`post_parent`,`guid`,`menu_order`,`post_type`,`post_mime_type`,`comment_count`,`to_ping`,`pinged`,`post_content_filtered`) "
           f"SELECT 1,NOW(),UTC_TIMESTAMP(),'{esc(BODY)}','{esc(TITLE)}','','{status}','closed','closed','{SLUG}',NOW(),UTC_TIMESTAMP(),0,'{SITE}/{SLUG}/',0,'page','',0,'','','' FROM DUAL "
           f"WHERE NOT EXISTS (SELECT 1 FROM {t} WHERE `post_name`='{SLUG}' AND `post_type`='page');")
    out = ['START TRANSACTION;', ins, f"SET @pid := (SELECT `ID` FROM {t} WHERE `post_name`='{SLUG}' AND `post_type`='page' ORDER BY `ID` LIMIT 1);"]
    out += [f"INSERT INTO {m} (`post_id`,`meta_key`,`meta_value`) SELECT @pid,'{k}','{esc(v)}' FROM DUAL WHERE @pid IS NOT NULL AND NOT EXISTS (SELECT 1 FROM {m} WHERE `post_id`=@pid AND `meta_key`='{k}');" for k, v in metas]
    out.append('COMMIT;')
    rb = ['START TRANSACTION;', f"SET @pid := (SELECT `ID` FROM {t} WHERE `post_name`='{SLUG}' AND `post_type`='page' ORDER BY `ID` LIMIT 1);",
          f"DELETE FROM {m} WHERE `post_id`=@pid AND @pid IS NOT NULL;", f"DELETE FROM {t} WHERE `ID`=@pid AND `post_type`='page' AND @pid IS NOT NULL;", 'COMMIT;']
    return 'SET NAMES utf8mb4;\n-- Pillar page is inserted as PUBLISHED (ad posts link to it).\n' + '\n'.join(out) + '\n', 'SET NAMES utf8mb4;\n' + '\n'.join(rb) + '\n'


def main():
    (ROOT / 'wp').mkdir(exist_ok=True)
    tg_meta = [('_rank_math_title', 'Хати истеҳсолот ва ҳамкорӣ бо кишоварзии Тоҷикистон | AFP'), ('_rank_math_description', 'AFP — истеҳсолкунандаи лентаи обёрии қатрагӣ, қубури полиэтиленӣ ва қубури қатшавандаи риштадор. Шартҳои ҳамкорӣ бо деҳқонон ва ташкилотҳои Тоҷикистон.'),
               ('rank_math_focus_keyword', 'лентаи обёрии қатрагӣ Тоҷикистон'), ('_navar_tj_lang', 'tg-TJ')]
    ru_meta = [('_rank_math_title', 'Производство и сотрудничество с сельским хозяйством Таджикистана | AFP'), ('_rank_math_description', 'AFP — производитель капельной ленты, полиэтиленовых труб и армированных рукавов layflat. Условия сотрудничества с фермерами и организациями Таджикистана.'),
               ('rank_math_focus_keyword', 'капельная лента Таджикистан'), ('_navar_tj_lang', 'ru-RU')]
    (ROOT / 'wp/pillar-page.html').write_text(BODY, encoding='utf-8'); (ROOT / 'wp/pillar-page-ru.html').write_text(BODY_RU, encoding='utf-8')
    a, b = sql(SLUG, TITLE, BODY, tg_meta); c, d = sql(SLUG_RU, TITLE_RU, BODY_RU, ru_meta)
    # one file with both pages (tg + ru), one rollback
    (ROOT / 'wp/pillar-pages.sql').write_text(a + c.replace('SET NAMES utf8mb4;\n', ''), encoding='utf-8')
    (ROOT / 'wp/pillar-pages-ROLLBACK.sql').write_text(b + d.replace('SET NAMES utf8mb4;\n', ''), encoding='utf-8')
    print('pillar pages written (tg + ru)')


if __name__ == '__main__':
    main()
