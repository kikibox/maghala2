import os
import sys
import base64
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import article_content_queue as queue


class ArticleQueueTests(unittest.TestCase):
    def test_api_base_has_safe_fallback(self):
        self.assertTrue(queue.AGNES_BASE.startswith("https://"))
        self.assertNotEqual(queue.AGNES_BASE, "")

    def test_non_allowlisted_links_are_removed(self):
        allowed = "https://navar-abyari.ir/ok/"
        body = (
            f'<p><a href="{allowed}">مجاز</a> '
            '<a href="https://example.com/bad">غیرمجاز</a></p>'
        )
        cleaned = queue.sanitize_links(body, {allowed})
        self.assertIn(f'href="{allowed}"', cleaned)
        self.assertNotIn("example.com", cleaned)
        self.assertIn("غیرمجاز", cleaned)

    def test_missing_internal_links_are_added_deterministically(self):
        links = [
            {"title": f"مطلب {i}", "url": f"https://navar-abyari.ir/post-{i}/"}
            for i in range(1, 7)
        ]
        body = '<p><a href="https://navar-abyari.ir/post-1/">یک</a></p>'
        repaired = queue.ensure_minimum_internal_links(body, links)
        self.assertEqual(len(queue.internal_links(repaired)), queue.MIN_LINKS)
        self.assertIn("مطالب مرتبط", repaired)

    def test_failed_items_are_retried_first(self):
        old_batch, old_attempts = queue.BATCH, queue.MAX_ATTEMPTS
        queue.BATCH, queue.MAX_ATTEMPTS = 1, 4
        try:
            q = {"items": [
                {"id": "new", "status": "pending", "attempts": 0},
                {"id": "retry", "status": "failed", "attempts": 1, "failed_at": "2026-01-01"},
            ]}
            self.assertEqual(queue.select_batch(q)[0]["id"], "retry")
        finally:
            queue.BATCH, queue.MAX_ATTEMPTS = old_batch, old_attempts

    def test_image_response_is_normalized_to_optimized_16_by_9_webp(self):
        source = io.BytesIO()
        Image.effect_noise((1024, 768), 64).convert("RGB").save(source, "PNG")
        response = {"data": [{"b64_json": base64.b64encode(source.getvalue()).decode()}]}
        old_out, old_token = queue.OUT, queue.IMAGE_TOKEN
        with tempfile.TemporaryDirectory() as tmp:
            queue.OUT = Path(tmp)
            queue.IMAGE_TOKEN = "test"
            try:
                item = {"id": "crop-001", "title": "مقاله نوار تیپ", "slug": "راهنمای-کشت-گوجه-با-نوار-تیپ", "focus": "crop", "vertical": "crop"}
                with patch.object(queue, "fetch_json", return_value=response) as fetch_json:
                    record = queue.generate_image(item, 1)
                payload = fetch_json.call_args.args[2]
                self.assertEqual(payload["model"], "agnes-image-2.5-flash")
                self.assertEqual(len(payload["extra_body"]["image"]), 1)
                neutral = payload["extra_body"]["image"][0]
                self.assertTrue(neutral.startswith("data:image/png;base64,"))
                self.assertNotIn(queue.image_prompt_policy.DRIP_TAPE_ROLL_REFERENCE, neutral)
                prompt = queue.image_prompt(item, 1)
                self.assertIn("1000-meter", prompt)
                self.assertIn("10 to 20 percent", prompt)
                self.assertIn("75 to 85 percent", prompt)
                self.assertIn("not a reference image", prompt)
                output = Path(tmp) / "images" / record["name"]
                self.assertEqual(record["mime"], "image/webp")
                self.assertEqual(record["name"], "راهنمای-کشت-گوجه-با-نوار-تیپ-تصویر-شاخص.webp")
                self.assertEqual((record["width"], record["height"]), (1200, 675))
                with Image.open(output) as image:
                    self.assertEqual(image.size, (1200, 675))
                    self.assertEqual(image.format, "WEBP")
            finally:
                queue.OUT, queue.IMAGE_TOKEN = old_out, old_token

    def test_seo_image_names_are_descriptive_and_sanitized(self):
        item = {"id": "crop-001", "slug": "هزینه کشت گوجه / نوار تیپ"}
        self.assertEqual(
            queue.seo_image_name(item, 2),
            "هزینه-کشت-گوجه-نوار-تیپ-کاربرد-عملی.webp",
        )
        self.assertNotIn("crop-001", queue.seo_image_name(item, 2))

    def test_parallel_image_manager_preserves_role_order(self):
        import threading
        active = 0
        peak = 0
        lock = threading.Lock()
        def fake_generate(item, kind):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            import time
            time.sleep(0.03)
            with lock:
                active -= 1
            return {"name": f"{kind}.webp", "sha256": str(kind)}
        with patch.object(queue, "generate_image", side_effect=fake_generate):
            rows = queue.generate_images_parallel({"id": "crop-001"})
        self.assertEqual([row["name"] for row in rows], ["1.webp", "2.webp", "3.webp"])
        self.assertGreaterEqual(peak, 2)

    def test_product_label_text_is_exact_and_family_specific(self):
        tape = queue.image_prompt_policy.image_prompt(
            {"source_id": "crop-001", "title": "مقاله نوار تیپ"}, 1
        )
        layflat = queue.image_prompt_policy.image_prompt(
            {"source_id": "crop-001-layflat", "title": "مقاله لوله نخدار"}, 1
        )
        for required in ("AFP", "آبگسترفراپارسیان", "Drip Irrigation tape"):
            self.assertIn(required, tape)
        self.assertIn('never print "layflat"', tape)
        for required in ("AFP", "آبگسترفراپارسیان", 'lowercase "layflat"'):
            self.assertIn(required, layflat)
        self.assertIn('never print "Drip Irrigation tape"', layflat)

    def test_sql_is_publish_idempotent_and_rollback_is_marker_scoped(self):
        item = {
            "id": "crop-001", "title": "عنوان", "slug": "onvan",
            "focus": "focus", "vertical": "crop", "post_type": "post",
        }
        obj = {
            "title": "عنوان", "html": "[[[IMAGE_1]]][[[IMAGE_2]]][[[IMAGE_3]]]",
            "excerpt": "خلاصه", "meta_title": "متا",
            "meta_description": "شرح", "focus_keyword": "کلید",
        }
        images = [
            {"name": f"crop-001-{i}.png", "mime": "image/png", "width": 1536,
             "height": 1024, "sha256": "x"}
            for i in range(1, 4)
        ]
        sql, rollback, body = queue.sql_for(item, obj, images)
        self.assertIn("'publish'", sql)
        self.assertIn("_navar_queue_item_id", sql)
        self.assertIn("_navar_queue_image_id", sql)
        self.assertIn("'image/png'", sql)
        self.assertIn("_wp_attachment_metadata", sql)
        self.assertNotIn("WHERE post_name='onvan'", rollback)
        self.assertIn("_navar_queue_item_id", rollback)
        self.assertNotIn("[[[IMAGE_", body)


if __name__ == "__main__":
    unittest.main()