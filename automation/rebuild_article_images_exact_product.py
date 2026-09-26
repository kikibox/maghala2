#!/usr/bin/env python3
"""Gradually rebuild completed article images with the approved AFP product policy."""
from __future__ import annotations

import datetime as dt
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import article_content_queue as queue

POLICY = "reference-rerender-3d-v5-approved-scales-topic-first"
MODE = "reference-conditioned-3d-rerender-approved-scales-topic-first"
MARKER = queue.OUT / "image-rebuild-reference-rerender-3d-v5-approved-scales-topic-first.json"
WORKERS = min(2, max(1, int(os.getenv("IMAGE_WORKERS", "2"))))
POST_LIMIT = max(1, int(os.getenv("IMAGE_REBUILD_POST_LIMIT", "4")))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def write_marker(rebuilt, skipped, failures, total, remaining, completed=False):
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(
        json.dumps(
            {
                "policy": POLICY,
                "mode": MODE,
                "completed": bool(completed and not failures and remaining == 0),
                "completed_at": now() if completed and not failures and remaining == 0 else None,
                "total_candidates": total,
                "remaining_candidates": remaining,
                "rebuilt_posts": sorted(rebuilt),
                "skipped": skipped,
                "failures": failures,
                "last_progress_at": now(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

def current_policy_ids(completed):
    current = []
    for item in completed:
        item_id = str(item.get("id") or item.get("source_id") or "")
        path = queue.ITEMS / f"{item_id}.json"
        if not item_id or not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("image_rebuild_policy") == POLICY:
            current.append(item_id)
    return sorted(current)


def main() -> int:
    if not queue.QUEUE.exists():
        print("exact_product_rebuild=no_queue")
        return 0
    state = json.loads(queue.QUEUE.read_text(encoding="utf-8"))
    completed = [x for x in state.get("items", []) if x.get("status") == "completed"]
    records, skipped = {}, []
    for item in completed:
        item_id = str(item.get("id") or item.get("source_id") or "")
        path = queue.ITEMS / f"{item_id}.json"
        if not item_id or not path.exists():
            skipped.append({"id": item_id, "reason": "item JSON missing"})
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("image_rebuild_policy") == POLICY:
            continue
        records[item_id] = (item, path, data)

    pending_total = len(records)
    if not records:
        current = current_policy_ids(completed)
        remaining = max(0, len(completed) - len(current))
        write_marker(current, skipped, [], len(completed), remaining, completed=True)
        print("exact_product_rebuild=already_current")
        return 0

    selected_ids = list(records)[:POST_LIMIT]
    records = {item_id: records[item_id] for item_id in selected_ids}
    results = {item_id: {} for item_id in records}
    failures = []
    with ThreadPoolExecutor(max_workers=WORKERS, thread_name_prefix="exact-product") as pool:
        futures = {}
        for item_id, (item, _, data) in records.items():
            enriched = {**item, **data}
            for kind in range(1, 4):
                futures[pool.submit(queue.generate_image, enriched, kind)] = (item_id, kind)
        for future in as_completed(futures):
            item_id, kind = futures[future]
            try:
                results[item_id][kind] = future.result()
            except Exception as exc:
                failures.append({"id": item_id, "kind": kind, "error": str(exc)[:1200]})

    failed_ids = {x["id"] for x in failures}
    rebuilt, stamp = [], now()
    for item_id, (item, path, data) in records.items():
        if item_id in failed_ids or len(results[item_id]) != 3:
            continue
        images = [results[item_id][kind] for kind in range(1, 4)]
        names = [x["name"] for x in images]
        hashes = [x["sha256"] for x in images]
        data.update(
            images=images,
            image_sha256=hashes,
            image_generation_mode=MODE,
            image_rebuild_policy=POLICY,
            image_rebuilt_at=stamp,
        )
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        item.update(
            images=names,
            image_sha256=hashes,
            image_generation_mode=MODE,
            image_rebuild_policy=POLICY,
            image_rebuilt_at=stamp,
        )
        rebuilt.append(item_id)

    state["updated_at"] = now()
    queue.QUEUE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    current = current_policy_ids(completed)
    remaining = max(0, len(completed) - len(current))
    write_marker(current, skipped, failures, len(completed), remaining, completed=True)
    print(
        f"exact_product_rebuild rebuilt={len(rebuilt)} remaining={remaining} failures={len(failures)} "
        f"workers={WORKERS} post_limit={POST_LIMIT} policy={POLICY}",
        flush=True,
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
