# جریان تولید (نسخهٔ فعلی)

1. عنوان تاجیکی تأییدشده + عنوان فارسی و روسی (`data/titles_i18n.json`) → مقالهٔ **فارسی** (فقط واسطه، منتشر نمی‌شود).
2. ترجمهٔ قطعه‌به‌قطعه با `translate_queue.py` (maghala2): تاجیکی با `agnes-2.5-flash`، روسی با `agnes-3.0-flash`؛ واژه‌نامهٔ ثابت و نام مکان‌ها؛ ترمیم خودکار قطعه‌های خراب.
3. سه تصویر مشترک برای هر دو زبان.
4. SQL + rollback: دو پست عادی `publish` در دسته‌های `tajikistan-ads-tg` و `tajikistan-ads-ru` (جدا از دسته‌های مقاله).
5. بستهٔ ZIP هر ۵۰ آیتم (۱۰۰ پست) با `create.sql`، `rollback.sql`، `pillar-pages.sql`، تصاویر، `manifest.csv` و `preview/`.

شروع اجرا: ویرایش `automation/tj-ads-trigger.txt` (only_id، redo، batch_size، only_place، tier). ورود به دارندهٔ لیست مقالات: `wp/navar-tj-ads-exclude.php` را به‌صورت mu-plugin نصب کنید تا پست‌های تبلیغاتی در لیست مقالات/صفحهٔ اصلی/فید نیایند.
