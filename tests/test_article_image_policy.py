import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import article_image_policy as policy


class ArticleImagePolicyTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "id": "prod-001",
            "title": "راهنمای خرید نوار تیپ 20 سانتی",
            "focus": "product buying guide",
            "city": "شیراز",
            "topic": "نوار تیپ",
            "vertical": "product",
        }

    def test_option_pools_have_at_least_seven_values(self):
        for values in (
            policy.CAMERAS, policy.BACKGROUNDS, policy.LIGHTING,
            policy.COMPOSITIONS, policy.SUBJECT_POSITIONS,
            policy.HORIZONS, policy.SOILS, policy.ROW_LAYOUTS,
        ):
            self.assertGreaterEqual(len(values), 7)

    def test_five_prompts_have_unique_controlled_variations(self):
        specs = [policy.variation_spec(self.item, i) for i in range(1, 6)]
        prompts = [policy.image_prompt(self.item, i) for i in range(1, 6)]
        self.assertEqual(len(set(prompts)), 5)
        for key in ("camera", "background", "lighting", "composition"):
            self.assertEqual(len({spec[key] for spec in specs}), 5, key)
        self.assertTrue(all("must never be visible" in prompt for prompt in prompts))
        self.assertIn("technical field scene", prompts[2])
        self.assertIn("technical field scene", prompts[3])
        self.assertIn("technical field scene", prompts[4])

    def test_product_reference_is_mandatory_only_for_product_views(self):
        self.assertTrue(policy.reference_images(self.item, 1))
        self.assertTrue(policy.reference_images(self.item, 2))
        self.assertEqual(policy.reference_images(self.item, 3), [])

    def test_ocr_accepts_only_approved_product_strings(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp:
            path = Path(temp.name)
            with patch.object(policy, "ocr_text", return_value="AFP DRIP Irrigation tape"):
                valid, _ = policy.validate_ocr(path, self.item, 1)
                self.assertTrue(valid)
            with patch.object(policy, "ocr_text", return_value="AFP FAKE 9999"):
                valid, _ = policy.validate_ocr(path, self.item, 1)
                self.assertFalse(valid)
            with patch.object(policy, "ocr_text", return_value=""):
                valid, _ = policy.validate_ocr(path, self.item, 1, hide_label=True)
                self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()