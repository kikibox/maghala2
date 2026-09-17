#!/usr/bin/env python3
"""FAQ policy for generated city posts: 3 collapsible details items at end."""
import re
FAQ_HEADING_RE=re.compile(r'<h3[^>]*>\s*(?:پرسش|سوال|سؤالات|سوالات).*?(?:متداول|FAQ).*?</h3>',re.I|re.S)
DETAILS_RE=re.compile(r'<details\b[^>]*>\s*<summary\b[^>]*>.*?</summary>.*?</details>',re.I|re.S)
TAIL_SECTION_RE=re.compile(r'(<h3[^>]*>\s*(?:پرسش|سوال|سؤالات|سوالات).*?(?:متداول|FAQ).*?</h3>.*?)(?=<h2|<h3|$)',re.I|re.S)

def faq_count(html):
    sections=list(TAIL_SECTION_RE.finditer(html or ''))
    if not sections:
        return 0
    return len(DETAILS_RE.findall(sections[-1].group(1)))

def has_faq_at_end(html):
    html=html or ''
    sections=list(TAIL_SECTION_RE.finditer(html))
    if not sections:
        return False
    last=sections[-1]
    if faq_count(last.group(1)) != 3:
        return False
    after=html[last.end():]
    return after.count('<h2')==0 and after.count('<h3')==0

# Backward-compatible name used by older patched runner code.
def has_five_faq_at_end(html):
    return has_faq_at_end(html)

def instruction():
    return ('در انتهای مقاله، قبل از بخش لینک‌های مرتبط، ابتدا یک جمله دعوت به تماس واتساپ بیاور: '
            '<p>برای دریافت مشاوره یا سفارش محصول، از طریق <a href="https://wa.me/989134922013">واتساپ با ما در ارتباط باشید</a>.</p> '
            'سپس عنوان سوالات متداول را با ساختار <h3 id="faq">پرسش‌های متداول درباره [موضوع] در [شهر]</h3> بنویس. '
            'بعد از آن دقیقاً ۳ پرسش و پاسخ تاشو بساز؛ هر مورد باید با ساختار <details><summary>متن سوال؟</summary>متن پاسخ کامل و کاربردی<br><br></details> باشد. '
            'از ساختار h2 برای FAQ استفاده نکن. برای سوالات از <h3> جداگانه استفاده نکن؛ فقط summary داخل details باشد. '
            'پرسش‌ها باید مرتبط با همان شهر و همان موضوع پست باشند؛ برای topic=layflat درباره لوله نخی/تاشو، و برای topic=tape20 درباره رول نوار تیپ ۲۰ سانتی باشد. '
            'تعداد سوالات دقیقاً ۳ عدد باشد، نه بیشتر و نه کمتر. بعد از FAQ هیچ بخش محتوایی جدید با h2 یا h3 اضافه نکن.')
