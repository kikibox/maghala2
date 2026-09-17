#!/usr/bin/env python3
"""Cleanup generated HTML before SQL export."""
import re
IMAGE_MARKER_RE=re.compile(r'\[\[\[IMAGE_[1-5]\]\]\]')
LONG_TITLE_PREFIXES=(
    'راهنمای جامع انتخاب و خرید ',
    'راهنمای تخصصی انتخاب و خرید ',
    'راهنمای تخصصی خرید و نصب ',
    'راهنمای خرید و نصب ',
    'راهنمای فنی انتخاب ',
)

def clean_title(title, item):
    title=(title or '').strip()
    topic=item.get('topic')
    city=item.get('city','').strip()
    if topic=='layflat':
        base=f'خرید لوله نخی و تاشو در {city}'
    elif topic=='tape20':
        base=f'خرید نوار تیپ ۲۰ سانتی در {city}'
    else:
        base=title
    return base[:68].strip()

def cleanup_html(html):
    html=html or ''
    # IMAGE_1 is featured only; remove any leaked marker from visible post body.
    html=html.replace('[[[IMAGE_1]]]','')
    html=IMAGE_MARKER_RE.sub('', html)
    html=re.sub(r'<p>\s*</p>','',html)
    return html.strip()

def apply(obj,item):
    if not isinstance(obj,dict): return obj
    obj['title']=clean_title(obj.get('title',''),item)
    obj['meta_title']=clean_title(obj.get('meta_title') or obj.get('title',''),item)
    if obj.get('html'): obj['html']=cleanup_html(obj['html'])
    return obj
