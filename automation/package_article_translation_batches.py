#!/usr/bin/env python3
"""Package complete multilingual translations in 50-source-article batches."""
from __future__ import annotations

import hashlib
import json
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "article-content-queue"
QUEUE = OUT / "queue.json"
TRANS = OUT / "translations"
SQL = OUT / "translation-sql"
ROLLBACK = OUT / "translation-rollback"
PACKAGES = OUT / "translation-packages"
LANGUAGES = ("ar-IQ", "tg-TJ", "en-US")
BATCH_SIZE = max(1, int(os.getenv("TRANSLATION_PACKAGE_BATCH_SIZE", "50")))


def main() -> int:
    if not QUEUE.exists():
        return 0
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    completed = [x for x in queue.get("items", []) if x.get("status") == "completed"]
    completed.sort(key=lambda x: x.get("completed_at", ""))
    PACKAGES.mkdir(parents=True, exist_ok=True)
    manifest = {"batch_size": BATCH_SIZE, "ready_batches": 0, "packages": []}
    full_batches = len(completed) // BATCH_SIZE
    for batch_index in range(full_batches):
        rows = completed[batch_index * BATCH_SIZE:(batch_index + 1) * BATCH_SIZE]
        files = []
        complete = True
        for item in rows:
            item_id = str(item["id"])
            for lang in LANGUAGES:
                required = [
                    TRANS / item_id / f"{lang}.html",
                    TRANS / item_id / f"{lang}.json",
                    SQL / f"{item_id}-{lang}.sql",
                    ROLLBACK / f"{item_id}-{lang}.sql",
                ]
                if not all(path.exists() for path in required):
                    complete = False
                    break
                files.extend(required)
            if not complete:
                break
        if not complete:
            continue
        start = batch_index * BATCH_SIZE + 1
        end = start + BATCH_SIZE - 1
        name = f"translation-batch-{batch_index + 1:03d}-sources-{start:04d}-{end:04d}.zip"
        target = PACKAGES / name
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            package_manifest = {
                "batch": batch_index + 1,
                "source_article_count": len(rows),
                "translation_post_count": len(rows) * len(LANGUAGES),
                "languages": list(LANGUAGES),
                "source_ids": [str(x["id"]) for x in rows],
            }
            archive.writestr("manifest.json", json.dumps(package_manifest, ensure_ascii=False, indent=2))
            for path in files:
                archive.write(path, path.relative_to(OUT))
        blob = target.read_bytes()
        manifest["packages"].append({
            "zip": name,
            "source_article_count": len(rows),
            "translation_post_count": len(rows) * len(LANGUAGES),
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
        })
    manifest["ready_batches"] = len(manifest["packages"])
    (PACKAGES / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())