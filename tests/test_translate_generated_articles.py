import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import translate_generated_articles as translations


class GeneratedTranslationTests(unittest.TestCase):
    def sample_translation(self):
        return {
            "title": "Translated title",
            "slug": "shared-translation-slug",
            "html": "<p>Translated body</p>",
            "excerpt": "Excerpt",
            "meta_title": "Meta title",
            "meta_description": "Meta description",
            "focus_keyword": "Keyword",
        }

    def test_bounded_slug_preserves_utf8_and_wordpress_limit(self):
        slug = "نامک-" + ("بسیار-طولانی-" * 40)
        result = translations.bounded_slug(slug, "crop-001-en")
        self.assertLessEqual(len(result.encode("utf-8")), 200)
        self.assertTrue(result.endswith("-crop-001-en"))
        result.encode("utf-8")

    def test_existing_translation_json_repairs_missing_delivery_sql(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trans = root / "translations"
            sql = root / "translation-sql"
            rollback = root / "translation-rollback"
            folder = trans / "crop-001"
            folder.mkdir(parents=True)
            payload = self.sample_translation()
            (folder / "en-US.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            sources = [({"id": "crop-001", "slug": "source-slug"}, {})]
            with patch.object(translations, "TRANS", trans), patch.object(
                translations, "SQL", sql
            ), patch.object(translations, "ROLLBACK", rollback):
                repaired = translations.ensure_translation_artifacts(sources)

            self.assertEqual(repaired, 2)
            self.assertTrue((folder / "en-US.html").exists())
            create = (sql / "crop-001-en-US.sql").read_text(encoding="utf-8")
            self.assertIn("_navar_translation_queue_key", create)
            self.assertIn("_navar_translation_source_id", create)
            self.assertIn("SET @resolved_slug=", create)
            self.assertIn("crop-001-en", create)
            self.assertTrue((rollback / "crop-001-en-US.sql").exists())

    def test_slug_conflict_uses_deterministic_queue_specific_fallback(self):
        item = {"id": "crop-001", "slug": "source-slug"}
        create, _ = translations.build_sql(
            item, self.sample_translation(), "en-US"
        )
        self.assertIn("shared-translation-slug-crop-001-en", create)
        self.assertIn("@resolved_conflict", create)
        self.assertNotIn("@slug_conflict IS NULL,LAST_INSERT_ID()", create)


if __name__ == "__main__":
    unittest.main()