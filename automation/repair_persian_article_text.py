#!/usr/bin/env python3
"""Deterministically repair legacy Persian article tails and delivery SQL."""
from __future__ import annotations

import json

import article_content_queue as queue


def repair_all() -> int:
    if not queue.QUEUE.exists():
        return 0
    state = json.loads(queue.QUEUE.read_text(encoding="utf-8"))
    repaired = 0
    for item in state.get("items", []):
        if item.get("status") != "completed":
            continue
        item_path = queue.ITEMS / f"{item['id']}.json"
        if not item_path.exists():
            continue
        data = json.loads(item_path.read_text(encoding="utf-8"))
        old_html = data.get("html", "")
        new_html = queue.cleanup_persian_html(old_html)
        if new_html == old_html:
            continue
        data["html"] = new_html
        create, rollback, rendered = queue.sql_for(item, data, data.get("images", []))
        data["html"] = rendered
        data["word_count"] = queue.words(rendered)
        item_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        (queue.SQL / f"{item['id']}.sql").write_text(create, encoding="utf-8")
        (queue.ROLLBACK / f"{item['id']}.sql").write_text(rollback, encoding="utf-8")
        repaired += 1
    print(f"persian_text_repaired={repaired}")
    return repaired


if __name__ == "__main__":
    repair_all()
