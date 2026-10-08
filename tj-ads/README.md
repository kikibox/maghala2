# tj-ads — پست‌های تبلیغاتی تاجیکستان (سیریلیک)

> این پوشه در شاخه `feat/tajikistan-ads` مخزن `kikibox/maghala2` قرار دارد تا از Secrets و ماژول‌های همان مخزن (کلیدهای Agnes، `image_prompt_policy`، FTPS) استفاده کند. مخزن `kikibox/ads-for-tj` فقط نسخه‌ی اولیه است.

پیاده‌سازی خط تولید پست‌های تبلیغاتی برای **۵۰ مکان مهم تاجیکستان** روی سایت navar-abyari.ir، بر پایه‌ی قوانین `kikibox/maghala2`.

| مورد | تصمیم |
|---|---|
| زبان | تاجیکی با **خط سیریلیک**؛ نام مکان‌ها سیریلیک، slug لاتین. روسی فعلاً نه |
| محل انتشار | **CPT جدید `tajikistan`** (جدا از مقالات). آدرس: `/tajikistan/{slug}/` |
| وضعیت پست | `draft` تا بازبینی |
| محصولات | لنتای آبیاری قطره‌ای، قوبوری پلی‌اتیلنی، قوبوری قات‌شونده‌ی نخ‌دار (layflat) |
| محصولات زراعی | فقط کشت ردیفی؛ باغ/تاکستان/گلخانه خارج از محدوده |
| تعداد عنوان | **۷۲۴** (A: ۱۰ مکان×۲۵، B: ۲۲×۱۵، C: ۱۸×۸) — برای کاهش شباهت قالبی؛ قابل تغییر در `config/title_templates.json` |

## ساختار
```
config/   places.json  crops.json  products.json  sources.json  government_context.json  link_pool.json  title_templates.json
data/     titles.csv  (titles.json با build_titles.py ساخته می‌شود)   ← خروجی مرحله ۱
automation/   (کنار این پوشه، ماژول‌های maghala2 در ../automation استفاده می‌شوند)
  build_titles.py      تولید قطعی عنوان‌ها از config
  ads_queue.py         صف تولید: متن (Agnes) + ۳ تصویر (GitHub Models) + SQL و Rollback
  package_batches.py   بسته‌های zip قابل آپلود (۲۵ پست)
  build_pillar.py      صفحه‌ی ستونی «خط تولید و همکاری»
  test_sql_sqlite.py   تست SQL روی SQLite (نه MySQL)
wp/       navar-tajikistan-ads.php (افزونه CPT)  pillar-page.sql (+ROLLBACK)
docs/     RULES.md  DEPLOY-fa.md  SOURCES.md
(workflow در ریشه‌ی مخزن: .github/workflows/tj-ads-queue.yml)
```

## شروع سریع
1. افزونه `wp/navar-tajikistan-ads.php` را نصب/فعال کنید → تنظیمات → پیوندهای یکتا → ذخیره.
2. `wp/pillar-page.sql` را در phpMyAdmin اجرا کنید (صفحه‌ی ستونی به‌صورت پیش‌نویس)؛ بازبینی و انتشار.
3. Secrets همان maghala2 استفاده می‌شود (`AGNES_API_KEY..13`، `IMAGE_API_KEY`، `FTP_PASSWORD`). اجرا: فایل `automation/tj-ads-trigger.txt` را ویرایش و commit کنید (یا Actions → **tj-ads-queue** → Run workflow پس از merge به main). اول `batch_size=3` و `only_place=rudaki`.
4. سه نمونه را بازبینی کنید؛ سپس batch را بزرگ‌تر کنید. خروجی: artifact `tj-ads-packages` (zip شامل `create.sql`, `rollback.sql`, `images/`).

جزئیات: `docs/DEPLOY-fa.md`، قوانین: `docs/RULES.md`، منابع: `docs/SOURCES.md`.

> ⚠️ SQL فقط روی SQLite تست شده است (MySQL در دسترس نبود). قبل از اجرا روی سایت زنده، بکاپ بگیرید.
> ⚠️ متن‌های تاجیکی و عنوان‌ها باید توسط یک گویشور تاجیک بازبینی شوند.
