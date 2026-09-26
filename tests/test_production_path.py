import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProductionPathTests(unittest.TestCase):
    def test_single_workflow_runs_article_queue_directly(self):
        workflows = list((ROOT / ".github" / "workflows").glob("*.yml"))
        self.assertEqual([path.name for path in workflows], ["article-content-queue.yml"])
        workflow = workflows[0].read_text(encoding="utf-8")
        self.assertIn("python automation/article_content_queue.py", workflow)
        self.assertIn("tesseract-ocr-fas", workflow)

    def test_production_runner_imports_policies_without_runtime_monkey_patch(self):
        path = ROOT / "automation" / "article_content_queue.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertIn("content_layout_policy", imports)
        self.assertIn("article_image_policy", imports)
        source = path.read_text(encoding="utf-8")
        self.assertNotIn("run_agnes_city_queue", source)
        self.assertNotIn(".install(", source)


if __name__ == "__main__":
    unittest.main()