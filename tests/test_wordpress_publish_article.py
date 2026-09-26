import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import wordpress_publish_article as wp


class WordPressPublisherTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "id": "crop-001",
            "title": "عنوان مقاله",
            "slug": "onvan-maghale",
            "focus": "آبیاری",
            "category_id": 35,
        }
        self.obj = {
            "title": "عنوان مقاله",
            "excerpt": "خلاصه",
            "html": "<p>متن</p>[[[IMAGE_1]]][[[IMAGE_2]]][[[IMAGE_3]]]",
        }
        self.images = [{"name": f"crop-001-{i}.jpg"} for i in range(1, 4)]
        self.media = [
            {"id": i, "source_url": f"https://example.test/image-{i}.jpg"}
            for i in range(1, 4)
        ]

    @patch.object(wp, "request_json")
    def test_verify_category_requires_exact_target(self, request_json):
        request_json.return_value = {"id": 35, "name": "مقاله‌ها", "slug": "مقاله-ها"}
        self.assertEqual(wp.verify_category(35)["id"], 35)
        request_json.return_value = {"id": 36}
        with self.assertRaises(RuntimeError):
            wp.verify_category(35)

    def test_render_html_replaces_every_marker(self):
        body = wp.render_html(self.item, self.obj, self.media)
        self.assertNotIn("[[[IMAGE_", body)
        self.assertEqual(body.count("<figure"), 3)
        self.assertIn("image-1.jpg", body)

    @patch.object(wp, "verify_publish_target")
    @patch.object(wp, "upload_media")
    @patch.object(wp, "find_post")
    @patch.object(wp, "request_json")
    def test_publish_updates_existing_slug_idempotently(
        self, request_json, find_post, upload_media, verify_publish_target
    ):
        upload_media.side_effect = self.media
        find_post.return_value = {"id": 99, "slug": self.item["slug"]}
        request_json.return_value = {
            "id": 99, "status": "publish", "link": "https://example.test/onvan-maghale/"
        }
        result = wp.publish_article(self.item, self.obj, self.images)
        self.assertEqual(result["post_id"], 99)
        self.assertEqual(result["status"], "publish")
        self.assertEqual(request_json.call_args.args[:2], ("POST", "/posts/99"))
        payload = request_json.call_args.kwargs["payload"]
        self.assertEqual(payload["featured_media"], 1)
        self.assertEqual(payload["categories"], [35])
        self.assertEqual(payload["status"], "publish")


if __name__ == "__main__":
    unittest.main()