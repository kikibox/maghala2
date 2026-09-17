#!/usr/bin/env python3
"""Ground local claims and deterministically clean common QA failures."""
import json,re
DISTANCE_RE=re.compile(r'(?:فاصله(?:‌|\s|-)*(?:قطره(?:‌|\s|-)*چکان(?:‌|\s|-)*ها?)?|قطره(?:‌|\s|-)*چکان).{0,55}?(?:۵|5|۱۰|10|۱۵|15|۲۵|25|۳۰|30)\s*(?:سانتی(?:‌|\s|-)*متر|سانت)',re.I)
CLAIM_TERMS=('اقلیم','آب و هوا','آب‌وهوا','خاک','رسوب','شوری','حاصلخیز','دشت','زعفران','صیفی','گندم','جو')
SPECULATION_TERMS=('احتمال','احتمالاً','محتمل','ممکن است','به نظر می‌رسد','شاید')
PRICE_CLAIMS=('قیمت جهانی پلاستیک','نوسانات ارز','بهترین زمان نصب','اواخر پاییز یا اوایل بهار')
LATIN_RE=re.compile(r'\b[A-Za-z]{3,}\b')
P_RE=re.compile(r'<p\b[^>]*>.*?</p>',re.I|re.S)
TAG_SPLIT_RE=re.compile(r'(<[^>]+>)')
LATIN_MAP={'PVC':'پلی‌اتیلن','Flushing':'شست‌وشوی خط','Radius':'شعاع','Wetting':'خیس‌شدگی','adherence':'پایبندی','Ingestion':'جذب','Root':'ریشه','Zone':'ناحیه','Eto':'تبخیر و تعرق مرجع'}
def _visible(text):return re.sub(r'<[^>]+>',' ',text or '')
def _clean_text_nodes(html):
 parts=TAG_SPLIT_RE.split(html or '')
 for i in range(0,len(parts),2):
  text=parts[i]
  for old,new in LATIN_MAP.items():text=re.sub(r'\b'+re.escape(old)+r'\b',new,text,flags=re.I)
  text=LATIN_RE.sub(lambda m:m.group(0) if m.group(0).upper() in {'FAQ','AFP'} else '',text)
  text=DISTANCE_RE.sub('فاصله قطره‌چکان ۲۰ سانتی‌متر',text)
  for phrase in PRICE_CLAIMS:text=text.replace(phrase,'شرایط روز و مشخصات فنی قابل بررسی')
  parts[i]=re.sub(r' {2,}',' ',text)
 return ''.join(parts)
def sanitize_html(html,item,research):
 html=_clean_text_nodes(html)
 if research.get('status')=='insufficient_evidence':
  names=(item.get('city',''),item.get('county',''))
  def fix_paragraph(match):
   block=match.group(0);text=_visible(block)
   if any(name and name in text for name in names) and (any(term in text for term in CLAIM_TERMS) or any(term in text for term in SPECULATION_TERMS)):
    return '<p>برای انتخاب و طراحی سامانه، شرایط واقعی خاک، کیفیت آب، دبی منبع، شیب زمین و نوع کشت باید با آزمایش و بازدید مزرعه بررسی شود و نباید ویژگی محلی تأییدنشده را مبنای خرید قرار داد.</p>'
   return block
  html=P_RE.sub(fix_paragraph,html)
 for number in range(2,6):
  marker=f'[[[IMAGE_{number}]]]';html=html.replace(marker,'')+'\n'+marker
 return html
def rewrite_grounded(obj,item,research,agnes_call,minimum_words):
 prompt=f'''مقاله زیر را یک بار به‌عنوان حقیقت‌سنج نسخه ۷ اصلاح کن و فقط JSON معتبر با کلیدهای title, meta_title, meta_description, focus_keyword, excerpt, html برگردان. طول حداقل {minimum_words} کلمه و چهار نشانگر تصویر را حفظ کن. ادعای محلی فقط با شاهد تحقیق و scope صحیح مجاز است؛ اگر تحقیق insufficient_evidence است هیچ اقلیم، خاک، آب، رسوب، شوری یا محصولی را به شهر نسبت نده. فقط فاصله قطره‌چکان ۲۰ سانتی‌متر مجاز است. واژه لاتین، PVC، ادعای قیمت و بهترین فصل نصب را حذف کن. لینک HTML نساز. تحقیق: {json.dumps(research,ensure_ascii=False)} مقاله: {json.dumps(obj,ensure_ascii=False)}'''
 result=agnes_call(prompt)
 if not isinstance(result,dict):raise RuntimeError('Grounding review did not return a JSON object')
 result['html']=sanitize_html(result.get('html',''),item,research);result['city_research']=research
 return result
def validate_grounding(obj,item,research):
 visible=_visible(obj.get('html',''));errors=[]
 if DISTANCE_RE.search(visible):errors.append('non-20cm emitter spacing claim')
 bad=sorted({x for x in LATIN_RE.findall(visible) if x.upper() not in {'FAQ','AFP'}})
 if bad:errors.append('unexpected Latin after cleanup: '+', '.join(bad[:8]))
 if research.get('status')=='insufficient_evidence':
  sentences=re.split(r'[.!؟\n]+',visible);names=(item.get('city',''),item.get('county',''))
  if any(any(name and name in sentence for name in names) and any(term in sentence for term in CLAIM_TERMS) for sentence in sentences):errors.append('unsupported local agricultural claim')
 if '۲۰ سانتی' not in visible and '20 سانتی' not in visible:errors.append('20cm product focus missing')
 return errors
