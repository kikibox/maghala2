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

    def test_link_variants_are_canonicalized_and_markers_repaired(self):
        canonical = "https://navar-abyari.ir/%D9%86%D9%88%D8%A7%D8%B1/"
        variant = "https://navar-abyari.ir/نوار/"
        body = f'<p><a href="{variant}">لینک</a></p><p>دو</p><p>سه</p><p>چهار</p>'
        cleaned = queue.sanitize_links(body, {canonical})
        self.assertIn(f'href="{canonical}"', cleaned)
        repaired = queue.ensure_image_markers(cleaned)
        for i in range(1, 4):
            self.assertEqual(repaired.count(f"[[[IMAGE_{i}]]]"), 1)

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
                approved = {
                    "pass": True,
                    "score": 100,
                    "reasons": ["unit-test fixture"],
                    "correction_prompt": "",
                }
                with patch.object(queue, "fetch_json", return_value=response) as fetch_json, \
                     patch.object(queue.image_quality_gate, "review_image", return_value=approved):
                    record = queue.generate_image(item, 1)
                payload = fetch_json.call_args.args[2]
                self.assertEqual(payload["model"], "agnes-image-2.5-flash")
                self.assertEqual(len(payload["extra_body"]["image"]), 1)
                neutral = payload["extra_body"]["image"][0]
                self.assertTrue(neutral.startswith("data:image/webp;base64,"))
                prompt = queue.image_prompt(item, 1)
                self.assertIn("true three-dimensional object", prompt)
                self.assertIn("20 to 23 percent of frame width", prompt)
                self.assertIn("below knee height", prompt)
                self.assertIn("Drip Irrigation Tape", prompt)
                output = Path(tmp) / "images" / record["name"]
                self.assertEqual(record["mime"], "image/webp")
                self.assertEqual(record["name"], "راهنمای-کشت-گوجه-با-نوار-تیپ-تصویر-شاخص.webp")
                self.assertEqual((record["width"], record["height"]), (1200, 675))
                with Image.open(output) as image:
                    self.assertEqual(image.size, (1200, 675))
                    self.assertEqual(image.format, "WEBP")
            finally:
                queue.OUT, queue.IMAGE_TOKEN = old_out, old_token

    def test_image_gate_metric_feedback_is_directional_and_tolerates_estimation_noise(self):
        ok, issues = queue.image_quality_gate._metric_check(
            "tape20",
            {"product_width_percent": 22, "product_height_percent": 25, "product_x_center_percent": 48},
        )
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        ok, issues = queue.image_quality_gate._metric_check(
            "tape20",
            {"product_width_percent": 18, "product_height_percent": 24, "product_x_center_percent": 50},
        )
        self.assertFalse(ok)
        self.assertTrue(any("Enlarge" in issue for issue in issues))
        self.assertFalse(any("do not center" in issue for issue in issues))

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
            output = Path(item["_image_output_dir"]) / f"{kind}.webp"
            output.write_bytes(f"candidate-{kind}".encode())
            with lock:
                active -= 1
            return {"name": f"{kind}.webp", "sha256": str(kind)}
        approved_set = {"pass": True, "score": 95, "duplicate_roles": [], "reasons": [], "correction_prompt": ""}
        old_out = queue.OUT
        with tempfile.TemporaryDirectory() as tmp:
            queue.OUT = Path(tmp)
            try:
                with patch.object(queue, "generate_image", side_effect=fake_generate), \
                     patch.object(queue.image_quality_gate, "review_image_set", return_value=approved_set):
                    rows = queue.generate_images_parallel({"id": "crop-001"})
            finally:
                queue.OUT = old_out
        self.assertEqual([row["name"] for row in rows], ["1.webp", "2.webp", "3.webp"])
        self.assertGreaterEqual(peak, 2)

    def test_visual_brief_extracts_post_summary_for_image_grounding(self):
        item = {"title": "مقدار بذر رزماری", "focus": "seed rate", "excerpt": "<p>محاسبه بذر، فاصله ردیف و آبیاری رزماری</p>", "meta_description": "راهنمای مزرعه"}
        brief = queue.image_prompt_policy.visual_brief(item)
        self.assertIn("رزماری", brief)
        self.assertIn("فاصله ردیف", brief)
        self.assertNotIn("<p>", brief)
        prompt = queue.image_prompt_policy.image_prompt(item, 1)
        self.assertIn("Article visual brief extracted from the post", prompt)
        self.assertIn("Every background must visibly express this brief", prompt)

    def test_creative_recipes_are_distinct_and_seed_topic_grounded(self):
        item = {"id": "crop-seed", "title": "مقدار بذر رزماری در هکتار", "excerpt": "محاسبه بذر و فاصله ردیف"}
        recipes = [queue.image_prompt_policy.visual_recipe(item, kind) for kind in (1, 2, 3)]
        self.assertEqual(len({row["camera"] for row in recipes}), 3)
        self.assertEqual(len({row["environment"] for row in recipes}), 3)
        self.assertIn("seed", recipes[0]["anchor"])
        self.assertIn("seed", recipes[1]["anchor"])
        self.assertIn("filtration", recipes[2]["anchor"])
        self.assertTrue(recipes[1]["camera"].startswith(("near-overhead", "high-oblique", "top-down", "close lateral")))
        self.assertTrue(any(word in recipes[2]["environment"] for word in ("irrigation", "filter", "flush", "pressure")))
        prompts = [queue.image_prompt_policy.image_prompt(item, kind) for kind in (1, 2, 3)]
        self.assertEqual(len(set(prompts)), 3)
        self.assertTrue(all("different editorial assignments" in prompt for prompt in prompts))
        self.assertIn("no person performs the activity", prompts[1])
        self.assertIn("People must not appear", prompts[0])
        self.assertNotIn("If people appear", prompts[0])

    def test_role_blueprints_force_crop_identity_and_distinct_compositions(self):
        item = {"id": "crop-spinach", "title": "میزان برداشت اسفناج در هکتار", "excerpt": "افزایش عملکرد با نوار تیپ"}
        self.assertEqual(queue.image_prompt_policy.named_crop(item), "اسفناج (spinach)")
        roles = [queue.image_prompt_policy.role_directive(item, kind) for kind in (1, 2, 3)]
        self.assertIn("CROP-IDENTITY HERO", roles[0])
        self.assertIn("AGRONOMIC CLOSE EVIDENCE", roles[1])
        self.assertIn("No horizon", roles[1])
        self.assertIn("IRRIGATION-SYSTEM STORY", roles[2])
        self.assertIn("no centered vanishing-point furrows", roles[2])
        self.assertEqual(len(set(roles)), 3)
        self.assertIn("dense low rosettes", queue.image_prompt_policy.crop_identity_spec(item))
        prompt = queue.image_prompt_policy.image_prompt(item, 1)
        self.assertIn("BOTANICAL IDENTITY LOCK", prompt)
        self.assertIn("dense low rosettes", prompt)

    def test_full_rebuild_uses_three_image_set_gate(self):
        rebuild = (ROOT / "automation" / "rebuild_article_images_exact_product.py").read_text(encoding="utf-8")
        self.assertIn("queue.generate_images_parallel", rebuild)
        self.assertNotIn("pool.submit(queue.generate_image", rebuild)

    def test_set_gate_regenerates_only_duplicate_role(self):
        calls = []
        def fake_generate(item, kind):
            calls.append(kind)
            output = Path(item["_image_output_dir"]) / f"{kind}.webp"
            output.write_bytes(f"candidate-{kind}-{len(calls)}".encode())
            return {"name": f"{kind}.webp", "sha256": f"hash-{kind}"}
        reviews = [
            {"pass": False, "score": 60, "duplicate_roles": [2], "reasons": ["role 2 repeats role 1"], "correction_prompt": "change camera and environment"},
            {"pass": True, "score": 92, "duplicate_roles": [], "reasons": [], "correction_prompt": ""},
        ]
        old_out = queue.OUT
        with tempfile.TemporaryDirectory() as tmp:
            queue.OUT = Path(tmp)
            (queue.OUT / "images").mkdir(parents=True)
            try:
                with patch.object(queue, "generate_image", side_effect=fake_generate), \
                     patch.object(queue.image_quality_gate, "review_image_set", side_effect=reviews):
                    rows = queue.generate_images_parallel({"id": "crop-diverse"})
            finally:
                queue.OUT = old_out
        self.assertEqual([row["name"] for row in rows], ["1.webp", "2.webp", "3.webp"])
        self.assertEqual(calls.count(1), 1)
        self.assertEqual(calls.count(2), 2)
        self.assertEqual(calls.count(3), 1)

    def test_failed_image_set_keeps_previously_published_images_untouched(self):
        old_out = queue.OUT
        rejected = {
            "pass": False,
            "score": 20,
            "duplicate_roles": [1, 2, 3],
            "reasons": ["wrong crop and duplicate composition"],
            "correction_prompt": "use the exact crop and three distinct scenes",
        }
        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            os.environ, {"IMAGE_SET_QA_ATTEMPTS": "1"}
        ):
            queue.OUT = Path(tmp)
            final_images = queue.OUT / "images"
            final_images.mkdir(parents=True)
            original = {}
            for kind in (1, 2, 3):
                name = queue.seo_image_name({"id": "crop-safe", "slug": "crop-safe"}, kind)
                original[name] = f"published-{kind}".encode()
                (final_images / name).write_bytes(original[name])

            def fake_generate(item, kind):
                name = queue.seo_image_name(item, kind)
                (Path(item["_image_output_dir"]) / name).write_bytes(
                    f"rejected-candidate-{kind}".encode()
                )
                return {"name": name, "sha256": f"candidate-{kind}"}

            try:
                with patch.object(queue, "generate_image", side_effect=fake_generate), \
                     patch.object(queue.image_quality_gate, "review_image_set", return_value=rejected):
                    with self.assertRaises(RuntimeError):
                        queue.generate_images_parallel({"id": "crop-safe", "slug": "crop-safe"})
                for name, expected in original.items():
                    self.assertEqual((final_images / name).read_bytes(), expected)
                self.assertFalse(any(queue.OUT.glob(".image-staging-*")))
            finally:
                queue.OUT = old_out

    def test_product_uses_family_specific_reference_and_3d_rerender_prompt(self):
        tape = queue.image_prompt_policy.image_prompt(
            {"source_id": "crop-001", "title": "مقاله نوار تیپ"}, 1
        )
        layflat = queue.image_prompt_policy.image_prompt(
            {"source_id": "crop-001-layflat", "title": "مقاله لوله نخدار"}, 1
        )
        self.assertIn("Drip Irrigation Tape", tape)
        self.assertIn('"layflat"', layflat)
        self.assertIn("20 to 23 percent of frame width", tape)
        self.assertIn("12 to 15 percent of frame width", layflat)
        self.assertIn("no sticker look", tape)
        tape_ref = queue.image_prompt_policy.reference_images(
            1, {"source_id": "crop-001"}
        )[0]
        layflat_refs = queue.image_prompt_policy.reference_images(
            1, {"source_id": "crop-001-layflat"}
        )
        self.assertTrue(tape_ref.startswith("data:image/webp;base64,"))
        self.assertEqual(len(layflat_refs), 2)
        self.assertTrue(layflat_refs[0].startswith("data:image/webp;base64,"))
        self.assertTrue(layflat_refs[1].startswith("data:image/jpeg;base64,"))
        self.assertNotEqual(tape_ref, layflat_refs[0])
        self.assertNotEqual(layflat_refs[0], layflat_refs[1])

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