#!/usr/bin/env python3
"""Ensure failed city/topic posts are not removed from the retry path."""
import json
from pathlib import Path

def reset_failed_for_retry(queue_path):
    queue_path = Path(queue_path)
    if not queue_path.exists():
        return 0
    q = json.loads(queue_path.read_text(encoding='utf-8'))
    changed = 0
    for item in q.get('items', []):
        if item.get('status') == 'failed':
            item['status'] = 'pending'
            item['needs_fix'] = True
            item['retry_policy'] = 'keep-in-queue-until-fixed'
            # Keep last_error for diagnosis, but remove transient timestamps so
            # the scheduler can pick it again.
            item.pop('failed_at', None)
            item.pop('started_at', None)
            changed += 1
    if changed:
        q['updated_at'] = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).replace(microsecond=0).isoformat()
        q['failed_posts_policy'] = 'do-not-drop; retry after diagnosis/fix'
        queue_path.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    return changed

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print('reset_failed_for_retry=', reset_failed_for_retry(root / 'artifacts/city-content-queue/queue.json'))
