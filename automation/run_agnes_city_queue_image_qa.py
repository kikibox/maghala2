#!/usr/bin/env python3
"""Launch split-topic fast QA v7 queue with contextual image inspection.

Before processing, reset completed layflat posts that were built with drip-tape
imagery so they are regenerated with the approved layflat reference images.
"""
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
import topic_split_policy
topic_split_policy.install_all()
try:
    import reset_layflat_outputs
    count = reset_layflat_outputs.reset_layflat()
    print(f'layflat_reset_count={count}', flush=True)
except Exception as exc:
    print(f'layflat_reset_warning={type(exc).__name__}: {exc}', flush=True)
runpy.run_path(str(HERE / 'run_agnes_city_queue_fast.py'), run_name='__main__')
