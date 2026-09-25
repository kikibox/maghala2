#!/usr/bin/env python3
"""Write .new-batch-signal when a NEW 50-post batch was packaged in this run.

The FTPS upload workflow triggers on push of this signal file, so it fires
exactly when a new batch zip is committed - not on every single-post commit.
The signal lists the batch names whose ZIPs are not yet recorded in
ftps-upload-state.json.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "city-content-queue"
MANIFEST = OUT / "packages" / "manifest.json"
STATE = OUT / "ftps-upload-state.json"
SIGNAL = OUT / ".new-batch-signal"


def main() -> int:
    if not MANIFEST.exists():
        SIGNAL.unlink(missing_ok=True)
        print("No packages/manifest.json yet; .new-batch-signal cleared")
        return 0
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    new_batches = {p.get("batch") for p in manifest.get("packages", []) if p.get("batch")}
    already = set()
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
            already = {name.rsplit(".zip", 1)[0] for name in state.get("files", {}).keys()}
        except Exception:
            already = set()
    truly_new = sorted(b for b in new_batches if b not in already)
    if truly_new:
        SIGNAL.write_text("\n".join(truly_new) + "\n", encoding="utf-8")
        print(f"New batch(es) ready: {truly_new} - wrote {SIGNAL.name}")
    else:
        SIGNAL.unlink(missing_ok=True)
        print("No new batch this run; .new-batch-signal cleared")
    return 0


if __name__ == "__main__":
    sys.exit(main())
