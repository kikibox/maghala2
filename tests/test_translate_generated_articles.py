import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import translate_generated_articles as translations
import package_article_content_batches as article_packages


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
        self.assertIn("_navar_inherited_thumbnail", create)
        self.assertIn("'_thumbnail_id'", create)
        self.assertIn("source_thumb.post_id=@source_post_id", create)
        self.assertNotIn("@slug_conflict IS NULL,LAST_INSERT_ID()", create)

    def test_changed_generator_refreshes_existing_sql_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            trans = root / "translations"
            sql = root / "translation-sql"
            rollback = root / "translation-rollback"
            folder = trans / "crop-001"
            folder.mkdir(parents=True)
            sql.mkdir()
            rollback.mkdir()
            payload = self.sample_translation()
            (folder / "en-US.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            (folder / "en-US.html").write_text(
                payload["html"], encoding="utf-8"
            )
            (sql / "crop-001-en-US.sql").write_text(
                "-- stale", encoding="utf-8"
            )
            (rollback / "crop-001-en-US.sql").write_text(
                "-- stale", encoding="utf-8"
            )
            sources = [({"id": "crop-001", "slug": "source-slug"}, {})]
            with patch.object(translations, "TRANS", trans), patch.object(
                translations, "SQL", sql
            ), patch.object(translations, "ROLLBACK", rollback):
                repaired = translations.ensure_translation_artifacts(sources)
            self.assertEqual(repaired, 1)
            refreshed = (sql / "crop-001-en-US.sql").read_text(
                encoding="utf-8"
            )
            self.assertIn("_navar_inherited_thumbnail", refreshed)

    def test_legacy_article_sql_is_normalized_before_packaging(self):
        legacy = (
            "SET NAMES utf8mb4;\n"
            "SET @post_id=(SELECT post_id FROM `ha_postmeta` "
            "WHERE meta_value=@queue_key LIMIT 1);"
        )
        fixed = article_packages.normalize_sql(legacy)
        self.assertNotIn("SET NAMES utf8mb4;", fixed)
        self.assertNotIn("meta_value=@queue_key", fixed)
        self.assertIn(
            "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_520_ci;", fixed
        )
        self.assertIn(
            "meta_value COLLATE utf8mb4_unicode_520_ci = "
            "@queue_key COLLATE utf8mb4_unicode_520_ci",
            fixed,
        )

    def test_combined_translation_sql_sets_legacy_database_collation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sql = root / "translation-sql"
            rollback = root / "translation-rollback"
            sql.mkdir()
            rollback.mkdir()
            (sql / "one.sql").write_text("SELECT 1;", encoding="utf-8")
            (rollback / "one.sql").write_text("SELECT 2;", encoding="utf-8")
            with patch.object(translations, "OUT", root), patch.object(
                translations, "SQL", sql
            ), patch.object(translations, "ROLLBACK", rollback):
                translations.rebuild_combined_sql()
            for name in (
                "create-all-translations.sql",
                "rollback-all-translations.sql",
            ):
                content = (root / name).read_text(encoding="utf-8")
                self.assertIn(
                    "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_520_ci;",
                    content,
                )
                self.assertIn(
                    "SET collation_connection = 'utf8mb4_unicode_520_ci';",
                    content,
                )
                self.assertNotIn("SET NAMES utf8mb4;\n", content)

    def test_article_package_contains_source_and_three_translations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "article-content-queue"
            packages = out / "packages"
            trans = out / "translations"
            trans_sql = out / "translation-sql"
            trans_rollback = out / "translation-rollback"
            for path in (
                out / "sql",
                out / "rollback",
                out / "items",
                out / "images",
                packages,
                trans_sql,
                trans_rollback,
            ):
                path.mkdir(parents=True, exist_ok=True)
            key = "crop-001"
            (out / "sql" / f"{key}.sql").write_text(
                "START TRANSACTION; COMMIT;", encoding="utf-8"
            )
            (out / "rollback" / f"{key}.sql").write_text(
                "START TRANSACTION; COMMIT;", encoding="utf-8"
            )
            (out / "items" / f"{key}.json").write_text(
                json.dumps({"images": []}), encoding="utf-8"
            )
            for lang in article_packages.LANGUAGES:
                folder = trans / key
                folder.mkdir(parents=True, exist_ok=True)
                (folder / f"{lang}.html").write_text("<p>x</p>", encoding="utf-8")
                (folder / f"{lang}.json").write_text("{}", encoding="utf-8")
                queue_key = f"article-translation:{key}:{lang}"
                (trans_sql / f"{key}-{lang}.sql").write_text(
                    f"SELECT '{queue_key}';", encoding="utf-8"
                )
                (trans_rollback / f"{key}-{lang}.sql").write_text(
                    "SELECT 1;", encoding="utf-8"
                )
            item = {
                "id": key,
                "title": "Source",
                "slug": "source",
                "vertical": "crop",
            }
            with patch.object(article_packages, "OUT", out), patch.object(
                article_packages, "PACKAGES", packages
            ), patch.object(article_packages, "TRANS", trans), patch.object(
                article_packages, "TRANS_SQL", trans_sql
            ), patch.object(
                article_packages, "TRANS_ROLLBACK", trans_rollback
            ):
                manifest = article_packages.build([item], "unit-batch")
            self.assertEqual(manifest["source_post_count"], 1)
            self.assertEqual(manifest["translation_post_count"], 3)
            self.assertEqual(manifest["total_post_count"], 4)
            archive = packages / "unit-batch.zip"
            with zipfile.ZipFile(archive) as zipped:
                names = set(zipped.namelist())
                sql = zipped.read("sql/create-unit-batch.sql").decode("utf-8")
            self.assertEqual(
                len([name for name in names if name.endswith(".json") and name.startswith("translations/")]),
                3,
            )
            for lang in article_packages.LANGUAGES:
                self.assertIn(f"article-translation:{key}:{lang}", sql)


if __name__ == "__main__":
    unittest.main()