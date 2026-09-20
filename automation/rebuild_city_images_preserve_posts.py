#!/usr/bin/env python3
"""Rebuild images for completed city posts while preserving their text and SEO."""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

import city_content_queue as base
import city_content_queue_cloudflare as backend
import image_prompt_policy

POLICY = "reference-conditioned-product-images-v16"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "city-content-queue"
MARKER = OUT / "image-rebuild-reference-product-v16.json"
MODEL = os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.0-flash")
API = os.getenv("AGNES_API_BASE", "https://apihub.agnes-ai.com/v1").rstrip("/")
KEY = os.getenv("AGNES_API_KEY", "").strip()
image_prompt_policy.install(backend)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def prompt(item: dict, kind: int) -> str:
    return image_prompt_policy.image_prompt(item, kind)


def generate(item: dict, kind: int) -> tuple[bytes, str]:
    if not KEY:
        raise RuntimeError("AGNES_API_KEY is missing")
    payload = {
        "model": MODEL,
        "prompt": prompt(item, kind),
        "size": "1024x768",
        "return_base64": True,
        "extra_body": {
            "response_format": "b64_json",
            "image": image_prompt_policy.reference_images(kind, item),
        },
    }
    req = urllib.request.Request(
        API + "/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "navar-city-content-queue/15.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Agnes Image HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:1200]}") from exc
    row = (data.get("data") or [{}])[0]
    if row.get("b64_json"):
        blob = base64.b64decode(row["b64_json"])
    elif row.get("url"):
        with urllib.request.urlopen(row["url"], timeout=300) as response:
            blob = response.read()
    else:
        raise RuntimeError("Agnes image response has neither b64_json nor url")
    image = Image.open(io.BytesIO(blob)).convert("RGB")
    target = 16 / 9
    width, height = image.size
    if width / height > target:
        new_width = int(height * target)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    image = image.resize((1200, 675), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    image.save(buf, "JPEG", quality=93, optimize=True)
    final = backend.watermark(buf.getvalue())
    if len(final) < 10000:
        raise RuntimeError("Generated image is unexpectedly small")
    return final, hashlib.sha256(final).hexdigest()


def main() -> int:
    if MARKER.exists():
        try:
            old = json.loads(MARKER.read_text(encoding="utf-8"))
            if old.get("policy") == POLICY and old.get("completed") is True:
                print(f"image_rebuild=already_completed policy={POLICY}", flush=True)
                return 0
        except Exception:
            pass
    if not base.QUEUE.exists():
        raise RuntimeError("Queue file is missing; refusing image rebuild")
    queue = json.loads(base.QUEUE.read_text(encoding="utf-8"))
    completed = [x for x in queue.get("items", []) if x.get("status") == "completed"]
    rebuilt = []
    skipped = []
    failures = []
    for item in completed:
        sid = str(item.get("source_id"))
        item_path = OUT / "items" / f"{sid}.json"
        if not item_path.exists():
            skipped.append({"source_id": sid, "reason": "item JSON missing"})
            continue
        data = json.loads(item_path.read_text(encoding="utf-8"))
        names = list(data.get("images") or item.get("images") or [])
        if len(names) != 5:
            skipped.append({"source_id": sid, "reason": f"expected 5 images, found {len(names)}"})
            continue
        try:
            for name in names:
                (OUT / "images" / Path(name).name).unlink(missing_ok=True)
            hashes = []
            for kind, name in enumerate(names, 1):
                blob, digest = generate({**item, **data}, kind)
                (OUT / "images" / Path(name).name).write_bytes(blob)
                hashes.append(digest)
                time.sleep(2)
            stamp = now()
            data["image_sha256"] = hashes
            data["image_rebuild_policy"] = POLICY
            data["image_rebuilt_at"] = stamp
            item["image_sha256"] = hashes
            item["image_rebuild_policy"] = POLICY
            item["image_rebuilt_at"] = stamp
            item_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            rebuilt.append(sid)
            print(f"image_rebuilt source_id={sid}", flush=True)
        except Exception as exc:
            failures.append({"source_id": sid, "error": str(exc)[:1200]})
            print(f"image_rebuild_failed source_id={sid} error={exc}", flush=True)
            break
    # Do not rewrite queue.json here: the live content worker may be updating
    # pending items at the same time. The item JSON and image filenames are
    # sufficient for a safe image-only rebuild.
    summary = {
        "policy": POLICY,
        "completed": not failures and len(rebuilt) + len(skipped) == len(completed),
        "completed_at": now() if not failures else None,
        "completed_posts": len(rebuilt),
        "skipped_posts": skipped,
        "failures": failures,
    }
    MARKER.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        raise RuntimeError(f"Image rebuild stopped after {len(rebuilt)} posts: {failures[0]['error']}")
    print(f"image_rebuild_completed posts={len(rebuilt)} skipped={len(skipped)} policy={POLICY}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
