#!/usr/bin/env python3
"""Render a human-readable live dashboard for the city-content queue."""
import datetime as dt,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/city-content-queue'
status=json.loads((OUT/'status.json').read_text(encoding='utf-8'))
queue=json.loads((OUT/'queue.json').read_text(encoding='utf-8'))
items=queue.get('items',[])
completed=[x for x in items if x.get('status')=='completed']
failed=[x for x in items if x.get('status')=='failed']
processing=[x for x in items if x.get('status')=='processing']
total=max(1,int(status.get('total',len(items))))
done=int(status.get('completed',len(completed)))
percent=done*100/total
now=dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
packages_manifest=OUT/'packages'/'manifest.json'
package_lines=[]
batch_size=50
if packages_manifest.exists():
    try:
        pm=json.loads(packages_manifest.read_text(encoding='utf-8'))
        batch_size=int(pm.get('batch_size',50));package_lines.append(f'- بسته‌های {batch_size}تایی آماده: **{pm.get("ready_batches",0)}**')
        for pkg in pm.get('packages',[])[-10:]:
            package_lines.append(f'- [{pkg.get("zip")}]({{}}./packages/{pkg.get("zip")}) — {pkg.get("post_count")} پست — {pkg.get("zip_bytes",0)} بایت'.format(''))
    except Exception as exc:
        package_lines.append(f'- خطا در خواندن بسته‌ها: `{type(exc).__name__}`')
else:
    package_lines.append(f'- هنوز بسته {batch_size}تایی آماده نشده است.')
lines=['# وضعیت زنده صف تولید پست‌های شهری','', '> این صفحه پس از پردازش هر پست به‌روزرسانی می‌شود. برای دیدن مقدار تازه، صفحه را Refresh کنید.','', f'- آخرین بروزرسانی: `{now}`',f'- وضعیت صف: **{status.get("result","unknown")}**',f'- پیشرفت: **{done} از {total} ({percent:.2f}٪)**',f'- تکمیل‌شده: **{done}**',f'- در حال پردازش: **{status.get("processing",len(processing))}**',f'- در انتظار: **{status.get("pending",0)}**',f'- ناموفق: **{status.get("failed",len(failed))}**',f'- مسدودشده توسط مدل تصویر: **{status.get("blocked_image_model",0)}**',f'- مدل متن و بازبینی: `agnes-3.0-flash`',f'- مدل تصویر: `{status.get("image_model","agnes-image-2.0-flash")}`',f'- فاصله شروع پست بعدی: **۳۰ ثانیه**','', '## بسته‌های آماده آپلود',''] + package_lines + ['', '## آخرین پست‌های تکمیل‌شده','']
if completed:
 for item in sorted(completed,key=lambda x:x.get('completed_at',''),reverse=True)[:20]:
  lines.append(f'- **{item.get("city","—")}** — {item.get("province","—")} — `{item.get("topic","—")}` — {item.get("word_count","—")} کلمه — `{item.get("completed_at","—")}`')
else: lines.append('- هنوز پستی کنترل کیفیت را با موفقیت نگذرانده است.')
lines+=['','## خطاهای اخیر','']
if failed:
 for item in failed[:10]:lines.append(f'- **{item.get("city","—")}** — `{item.get("topic","—")}`: `{str(item.get("last_error","نامشخص"))[:300]}`')
else: lines.append('- خطای فعالی ثبت نشده است.')
lines+=['','## فایل‌های خروجی','','- [وضعیت ماشینی](./status.json)','- [صف کامل](./queue.json)','- [SQL تجمیعی انتشار](./create-all-completed.sql)','- [SQL تجمیعی بازگشت](./rollback-all-completed.sql)',f'- [پوشه بسته‌های {batch_size}تایی](./packages/)','']
(OUT/'STATUS.md').write_text('\n'.join(lines),encoding='utf-8')
