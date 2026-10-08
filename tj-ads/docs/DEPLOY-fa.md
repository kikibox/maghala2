# راه‌اندازی و اجرا

## ۱) سمت وردپرس (یک‌بار)
1. `wp/navar-tajikistan-ads.php` → `wp-content/plugins/navar-tajikistan-ads/` → فعال‌سازی.
2. تنظیمات → پیوندهای یکتا → «ذخیره». آدرس‌ها: `/tajikistan/` و `/tajikistan/{slug}/`.
3. Rank Math → Titles & Meta → «Tajikistan Ads»: ایندکس + نقشه‌ی سایت (Sitemap) را روشن کنید (پس از تأیید نمونه‌ها).
4. phpMyAdmin: `wp/pillar-page.sql` (بکاپ بگیرید). Rollback: `wp/pillar-page-ROLLBACK.sql`.
5. افزونه‌ی `navar-seo-url-guard` و «Permalink Manager» مشکلی با CPT ندارند؛ فقط «Navar Multilingual Permalinks v3» را فعال نکنید.

## ۲) GitHub (maghala2، شاخه `feat/tajikistan-ads`)
- Secrets موجود استفاده می‌شوند: `AGNES_API_KEY`..`AGNES_API_KEY13` (چرخش کلید)، `IMAGE_API_KEY`، `FTP_PASSWORD`. Variables اختیاری: `AGNES_MODEL` (پیش‌فرض `agnes-3.0-flash`)، `IMAGE_MODEL`.
- تصاویر: همان مسیر maghala2 (`image_prompt_policy`: مرجع محصول AFP برای لنتا/layflat، قفل هویت گیاه، واترمارک تلفن، WebP 1200×675). برای قوبوری PE مرجع فرستاده نمی‌شود.
- شروع اجرا: `automation/tj-ads-trigger.txt` را ویرایش و commit کنید (`batch_size`, `only_place`, `tier`, `mock`, `upload`). دکمه‌ی Run workflow فقط وقتی دیده می‌شود که فایل workflow در main باشد.
- محلی: `python automation/ads_queue.py --mock --limit 3 && python automation/test_sql_sqlite.py`.
- `upload=true`: ZIPها با FTPS در ریشه‌ی FTP آپلود می‌شوند (مثل بسته‌های مقاله).

## ۳) انتشار هر بسته
1. artifact → `tj-ads-batch-NNN.zip`.
2. محتوای `images/` را در `wp-content/uploads/2026/10/navar-tj-ads/` آپلود کنید.
3. `create.sql` را در phpMyAdmin اجرا کنید → پست‌ها **draft** ساخته می‌شوند.
4. بازبینی (گویشور تاجیک) → انتشار. بازگشت: `rollback.sql`.

## ۴) پس از انتشار
Search Console: sitemap جدید CPT را ثبت کنید. همه‌ی پست‌های یک مکان را یک‌باره منتشر نکنید؛ روزانه تدریجی (مثلاً ۱۰–۲۰ پست) منتشر کنید.
