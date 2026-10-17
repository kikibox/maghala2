import io
import json
import sys
import tempfile
import time
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation"))
import article_link_policy as policy
import article_content_queue as queue

URL = policy.SITE + "/basil/"


def page(url=URL, lang="fa-IR", canonical=None, extra="", headers=None, status=200):
    return {
        "status": status,
        "url": url,
        "headers": headers or {"Content-Type": "text/html; charset=UTF-8"},
        "body": (
            f'<html lang="{lang}"><head><link rel="canonical" '
            f'href="{canonical or url}">{extra}</head><body>متن</body></html>'
        ).encode(),
    }


class ArticleLinkPolicyTests(unittest.TestCase):
    def test_valid_page(self):
        self.assertTrue(policy.verify_page(URL, page()))

    def test_percent_case_and_unicode_equivalence(self):
        self.assertEqual(
            policy.url_key(policy.SITE + "/ریحان/"),
            policy.url_key(policy.SITE + "/%D8%B1%DB%8C%D8%AD%D8%A7%D9%86/"),
        )

    def test_prefixes_and_escaped_path_separators_are_not_equivalent(self):
        self.assertNotEqual(policy.url_key(URL), policy.url_key(URL + "long/"))
        self.assertNotEqual(policy.url_key(policy.SITE + "/a%2fb/"),
                            policy.url_key(policy.SITE + "/a/b/"))

    def test_unsafe_or_variant_urls_rejected(self):
        for url in [
            "https://navar-abyari.ir.evil.test/basil/",
            "http://navar-abyari.ir/basil/", URL + "?navar_lang=tj", URL + "#x",
            "https://user@navar-abyari.ir/basil/", policy.SITE + "/bad%xy/",
        ]:
            with self.subTest(url=url):
                self.assertIsNone(policy.url_key(url))

    def test_redirect_or_non_200_rejected(self):
        for status in (301, 302, 403, 404, 429, 500):
            self.assertFalse(policy.verify_page(URL, page(status=status)))
        self.assertFalse(policy.verify_page(URL, page(url=URL + "else/")))

    def test_other_language_rejected(self):
        for lang in ("ar-IQ", "tg-TJ", "en-US", "ru-RU", ""):
            self.assertFalse(policy.verify_page(URL, page(lang=lang)))

    def test_noindex_and_none_rejected(self):
        for name in ("robots", "googlebot"):
            for value in ("noindex, follow", "none"):
                self.assertFalse(policy.verify_page(URL, page(
                    extra=f'<meta name="{name}" content="{value}">'
                )))
        self.assertFalse(policy.verify_page(URL, page(headers={
            "Content-Type": "text/html", "X-Robots-Tag": "googlebot: noindex"
        })))

    def test_missing_duplicate_foreign_or_different_canonical_rejected(self):
        for canonical in ("https://example.test/", URL + "wrong/"):
            self.assertFalse(policy.verify_page(URL, page(canonical=canonical)))
        self.assertFalse(policy.verify_page(URL, page(extra=f'<link rel="canonical" href="{URL}">')))
        p = page()
        p["body"] = b'<html lang="fa-IR"><body>no canonical</body></html>'
        self.assertFalse(policy.verify_page(URL, p))

    def test_relative_canonical_allowed(self):
        self.assertTrue(policy.verify_page(URL, page(canonical="/basil/")))

    def test_non_html_or_truncated_response_rejected(self):
        self.assertFalse(policy.verify_page(URL, page(headers={"Content-Type": "application/xml"})))
        p = page()
        p["body"] = b"x" * (policy.MAX_BYTES + 1)
        self.assertFalse(policy.verify_page(URL, p))

    def test_timeout_fails_closed(self):
        with patch.object(policy, "fetch_page", side_effect=TimeoutError):
            policy._CACHE.clear()
            self.assertFalse(policy.verified(URL))

    def test_selection_strict_types_status_language_relevance_and_dedup(self):
        def row(n, **kw):
            return {"url": policy.SITE + "/" + n + "/", "title": "ریحان",
                    "post_type": "post", **kw}
        rows = [
            row("unknown", post_type="new_unregistered_type"), row("acf", post_type="acf-field"),
            row("draft", status="draft"), row("unrelated", title="خرید قطعه دستگاه"),
            row("bad-language"), row("ok"), row("ok"),
        ]
        called = []
        def fetch(url):
            called.append(url)
            return page(url=url, lang="en-US" if "bad-language" in url else "fa-IR")
        selected = policy.select_links({"title": "آبیاری ریحان"}, rows, fetcher=fetch)
        self.assertEqual([r["url"] for r in selected], [policy.SITE + "/ok/"])
        self.assertEqual(len(called), 2)

    def test_probe_budget(self):
        rows = [{"url": policy.SITE + f"/{i}/", "title": "ریحان", "post_type": "post"}
                for i in range(20)]
        called = []
        def fetch(url):
            called.append(url)
            return page(url=url, status=404)
        self.assertEqual(policy.select_links({"title": "ریحان"}, rows,
                                            fetcher=fetch, probe_limit=3), [])
        self.assertEqual(len(called), 3)

    def test_robots_disallow_and_fetch_failure(self):
        import urllib.robotparser
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(["User-agent: *", "Disallow: /basil/"])
        with patch.object(policy, "_ROBOTS_CACHE", (time.monotonic(), rp)):
            self.assertFalse(policy.robots_allows(URL))
            self.assertTrue(policy.robots_allows(policy.SITE + "/other/"))
        with patch.object(policy, "_ROBOTS_CACHE", None), \
             patch.object(policy.urllib.request, "build_opener", side_effect=TimeoutError):
            self.assertFalse(policy.robots_allows(URL))

    def test_generation_stops_before_model_when_no_verified_pool(self):
        with patch.object(policy, "select_links", return_value=[]), \
             patch.object(queue, "agnes") as model:
            with self.assertRaisesRegex(RuntimeError, "approved internal links"):
                queue.make_content({"title": "ریحان", "focus": "ریحان"}, [])
            model.assert_not_called()

    def test_rest_uses_authoritative_link_not_slug(self):
        rows = [
            {"id": 1, "slug": "full-old-slug", "link": URL, "title": {"rendered": "ریحان"},
             "type": "post", "status": "publish"},
            {"id": 2, "slug": "draft", "link": URL, "title": "پیش نویس",
             "type": "post", "status": "draft"},
            {"id": 3, "slug": "missing", "title": "بدون پیوند", "type": "post", "status": "publish"},
        ]
        with patch.object(queue.urllib.request, "urlopen",
                          return_value=io.BytesIO(json.dumps(rows).encode())):
            _, links = queue.rest_index()
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["url"], URL)
        self.assertNotIn("full-old-slug", links[0]["url"])

    def test_old_unversioned_sitemap_cache_not_trusted(self):
        with tempfile.TemporaryDirectory() as d, patch.object(queue, "OUT", Path(d)), \
             patch.object(queue.urllib.request, "urlopen", side_effect=TimeoutError):
            (Path(d) / "link-index-sitemap.json").write_text(json.dumps({
                "count": 1, "links": [{"url": URL}]
            }))
            self.assertEqual(queue.sitemap_index(), [])


if __name__ == "__main__":
    unittest.main()