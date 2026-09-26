=== Navar Multilingual Permalinks ===
Requires at least: 5.8
Requires PHP: 7.4
Stable tag: 2.0.0
License: GPLv2 or later

Four-language routing for navar-abyari.ir with direct legacy redirects and hreflang links.

== URL rules ==

* Persian posts: /post-slug/
* Iraqi Arabic posts in category slug iraq: /iraq/post-slug/
* Tajik posts in category slug tj, tajik, or tajikistan: /tj/post-slug/
* English posts in category slug en or english: /en/post-slug/
* Legacy /iq/post-slug/ redirects directly to /iraq/post-slug/.
* Former and incorrectly prefixed URLs redirect with HTTP 301.
* Canonical, sitemap, archive, menu, and other WordPress-generated post links use the new URL.
* No post content or slug is changed in the database.

== Language context ==

* Persian: lang=fa-IR and RTL (WordPress default)
* Iraqi Arabic: lang=ar-IQ and RTL
* Tajik: lang=tg-TJ and LTR
* English: lang=en-US and LTR
* Adds body classes navar-lang-fa, navar-lang-iraq, or navar-lang-tj.
* Exposes navar_current_language() for child-theme templates.

== Installation / upgrade ==

1. Replace version 1.x with this ZIP; do not keep both versions active.
2. Activate the plugin.
3. Confirm category slugs: iraq for Iraqi Arabic, and preferably tj for Tajik.
4. Visit Settings > Permalinks and click Save Changes once.
5. Clear WordPress, server, and CDN caches.

== Important ==

This plugin provides routing and language context. Separate translated posts, menus, and page content are still required for a complete multilingual site.
Do not create page hierarchies that occupy /iraq/post-slug/ or /tj/post-slug/.
