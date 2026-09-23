#!/usr/bin/env python3
"""Run the resilient queue without dropping errored posts.

Policy: failed posts remain eligible for future retries. Do not fail-forward by
permanently skipping a city/topic after a small number of attempts; errors must
be surfaced and repaired, then retried.
"""
import os, runpy
from pathlib import Path
import city_content_queue as base

HERE = Path(__file__).resolve().parent

# Override workflow MAX_ATTEMPTS=2. A small attempt cap caused failed city posts
# to fall out of the retry selection. Keep items retryable across runs until the
# underlying prompt/code/model issue is fixed.
os.environ['MAX_ATTEMPTS'] = '9999'
base.MAX_ATTEMPTS = 9999

# Failed items must not block the queue. Retry them only during an explicit
# repair run with RETRY_FAILED=1; normal scheduled runs continue to the next
# pending item and preserve failures for diagnosis.
if os.getenv('RETRY_FAILED', '0') == '1':
    try:
        import keep_failed_in_queue
        reset_count = keep_failed_in_queue.reset_failed_for_retry(base.QUEUE)
        print(f'retry_failed_reset={reset_count}', flush=True)
    except Exception as exc:
        print(f'keep_failed_in_queue_warning={type(exc).__name__}: {exc}', flush=True)

runpy.run_path(str(HERE / 'run_agnes_city_queue_resilient.py'), run_name='__main__')
