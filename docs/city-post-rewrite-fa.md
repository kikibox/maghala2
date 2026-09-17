# بازنویسی پست‌های شهری با Agnes

این اتوماسیون dump وردپرس را فقط می‌خواند و مستقیماً دیتابیس زنده را تغییر نمی‌دهد. خروجی شامل فهرست شباهت، SQL جایگزینی، SQL بازگشت و گزارش QA است.

## اجرا

1. فایل `navaraby_wp569.sql.gz` در `database/incoming/` آپلود شود؛ audit خودکار اجرا می‌شود.
2. artifact اجرای audit دانلود و `inventory.csv` بررسی شود.
3. از Actions، گردش‌کار **Rewrite city posts with Agnes** با `mode=rewrite` و `max_posts=3` اجرا شود.
4. خروجی روی staging نصب و بررسی شود.
5. پس از تأیید، اجرای کامل با `max_posts=0` انجام شود.

مدل و endpoint با سامانه فعلی ترجمه یکسان‌اند: `agnes-2.5-flash` و `https://apihub.agnes-ai.com/v1`. سکرت موجود `AGNES_API_KEY` استفاده می‌شود.

## ایمنی

URLها، شماره‌ها، shortcodeها، کامنت‌های Gutenberg و تگ‌های تصویر محافظت می‌شوند. خروجی کوتاه یا بسیار مشابه حداکثر سه بار بازتولید می‌شود. SQL اصلی فقط پس از تست staging و با نگهداری `rollback.sql` اجرا شود.
