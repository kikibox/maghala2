import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

import content_layout_policy as policy


def sample_html():
    blocks = "".join(
        f"<p>بخش محتوایی شماره {i} درباره آبیاری و مدیریت مزرعه.</p>"
        for i in range(1, 25)
    )
    faq = (
        "<h2>پرسش‌های متداول</h2>"
        "<details><summary>سؤال اول</summary><p>پاسخ اول</p></details>"
        "<details><summary>سؤال دوم</summary><p>پاسخ دوم</p></details>"
        "<details><summary>سؤال سوم</summary><p>پاسخ سوم</p></details>"
    )
    return blocks + faq


def link_pool(size=190):
    return [
        {
            "title": f"راهنمای تخصصی آبیاری محصول {i}",
            "url": f"https://navar-abyari.ir/article-{i}/",
            "post_type": "post",
        }
        for i in range(size)
    ]


class ContentLayoutPolicyTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "id": "crop-001", "title": "راهنمای آبیاری گندم",
            "slug": "current-article", "focus": "گندم آبیاری",
            "city": "شیراز", "topic": "گندم", "vertical": "crop",
        }

    def test_selects_four_unique_links_from_190_deterministically(self):
        first = policy.select_internal_links(link_pool(), self.item, 4)
        second = policy.select_internal_links(link_pool(), self.item, 4)
        self.assertEqual(first, second)
        self.assertEqual(len({row["url"] for row in first}), 4)

    def test_two_articles_do_not_receive_the_same_links(self):
        other = {**self.item, "id": "crop-002", "title": "راهنمای آبیاری عدس", "topic": "عدس"}
        self.assertNotEqual(
            policy.select_internal_links(link_pool(), self.item, 4),
            policy.select_internal_links(link_pool(), other, 4),
        )

    def test_markers_and_links_are_distributed_before_unchanged_faq(self):
        raw = sample_html()
        original_faq = raw[policy.find_faq_start(raw):]
        body, selected = policy.apply_layout(raw, self.item, link_pool(), 4)
        faq_start = policy.find_faq_start(body)
        pre_faq, faq = body[:faq_start], body[faq_start:]
        self.assertEqual(faq, original_faq)
        self.assertNotIn("[[[IMAGE_1]]]", body)
        marker_positions = []
        for image_no in range(2, 6):
            marker = f"[[[IMAGE_{image_no}]]]"
            self.assertEqual(body.count(marker), 1)
            self.assertIn(marker, pre_faq)
            marker_positions.append(pre_faq.index(marker))
        regions = {int(position / max(len(pre_faq), 1) * 4) for position in marker_positions}
        self.assertGreaterEqual(len(regions), 3)
        self.assertEqual(pre_faq.lower().count("<a "), 4)
        self.assertNotIn("<a ", faq.lower())
        self.assertEqual(len({row["url"] for row in selected}), 4)
        anchor_positions = [match.start() for match in re.finditer(r"<a\b", pre_faq, re.I)]
        anchor_regions = {int(position / max(len(pre_faq), 1) * 4) for position in anchor_positions}
        self.assertGreaterEqual(len(anchor_regions), 3)
        # Every inserted marker/paragraph follows a complete top-level block.
        for token in [f"[[[IMAGE_{i}]]]" for i in range(2, 6)]:
            prefix = pre_faq[:pre_faq.index(token)].rstrip()
            self.assertRegex(prefix, r"</(?:p|ul|ol|table)>$")
        policy.validate_faq_tail(body)

    def test_model_links_and_old_markers_are_rebuilt(self):
        raw = sample_html().replace(
            "</p>", '<a href="https://evil.example/">جعلی</a>[[[IMAGE_99]]]</p>', 1
        )
        body, _ = policy.apply_layout(raw, self.item, link_pool(), 4)
        self.assertNotIn("evil.example", body)
        self.assertNotIn("IMAGE_99", body)
        self.assertEqual(len(re.findall(r"<a\b", body, re.I)), 4)


if __name__ == "__main__":
    unittest.main()