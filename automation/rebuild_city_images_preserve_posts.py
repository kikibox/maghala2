#!/usr/bin/env python3
"""Replace drifted AI product images with reference-locked product compositions.

The product itself is never redrawn: the approved product reference is cut out,
kept pixel-faithful, and placed on a clean varied background. This prevents AI
from turning the AFP packaged tape into a generic black ring or changing the
layflat package geometry.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import city_content_queue as base
import city_content_queue_cloudflare as backend

POLICY = "reference-locked-product-images-v17"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "city-content-queue"
MARKER = OUT / "image-rebuild-reference-locked-v17.json"
TAPE_REFERENCE = "https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp"
LAYFLAT_REFERENCE = "https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp"
CACHE = ROOT / ".reference-cache"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def reference_url(item: dict) -> str:
    return LAYFLAT_REFERENCE if item.get("topic") == "layflat" else TAPE_REFERENCE


def download_reference(url: str) -> Image.Image:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / hashlib.sha256(url.encode()).hexdigest()
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            path.write_bytes(response.read())
    return Image.open(path).convert("RGBA")


def cut_out_white_background(image: Image.Image) -> Image.Image:
    """Remove only border-connected white background; preserve white packaging."""
    image = image.copy().convert("RGBA")
    pixels = image.load()
    width, height = image.size
    seen: set[tuple[int, int]] = set()
    stack = [(x, 0) for x in range(width)] + [(x, height - 1) for x in range(width)]
    stack += [(0, y) for y in range(height)] + [(width - 1, y) for y in range(height)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or x < 0 or y < 0 or x >= width or y >= height:
            continue
        r, g, b, _ = pixels[x, y]
        if not (r > 225 and g > 225 and b > 225 and max(r, g, b) - min(r, g, b) < 18):
            continue
        seen.add((x, y))
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for x, y in seen:
        r, g, b, _ = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)
    bbox = image.getchannel("A").getbbox()
    return image.crop(bbox) if bbox else image


def background(kind: int, topic: str) -> Image.Image:
    width, height = 1200, 675
    palettes = [
        ((242, 246, 242), (210, 221, 207)),
        ((239, 244, 247), (218, 224, 215)),
        ((246, 242, 232), (214, 220, 199)),
        ((235, 241, 235), (201, 213, 194)),
        ((243, 239, 232), (211, 205, 187)),
    ]
    top, bottom = palettes[(kind - 1) % len(palettes)]
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    # Very subtle agricultural texture; never draw a competing product.
    soil_y = 470
    draw.rectangle((0, soil_y, width, height), fill=(165, 145, 111))
    for row in range(5):
        y = soil_y + 25 + row * 38 + (kind % 3) * 4
        draw.line((0, y, width, y - 35), fill=(181, 160, 124), width=3)
    if topic == "tape20":
        for x in range(40, width, 105):
            draw.ellipse((x, 180 + (x % 55), x + 18, 225 + (x % 55)), fill=(130, 165, 104))
    else:
        for x in range(50, width, 170):
            draw.ellipse((x, 160 + (x % 70), x + 30, 245 + (x % 70)), fill=(118, 151, 101))
    return image.filter(ImageFilter.GaussianBlur(1.2)).convert("RGBA")


def make_product_image(item: dict, kind: int) -> tuple[bytes, str]:
    topic = item.get("topic") or "tape20"
    foreground = cut_out_white_background(download_reference(reference_url(item)))
    canvas = background(kind, topic)
    width, height = canvas.size
    target_width = int(width * (0.70 if topic == "layflat" else 0.68 + (kind % 2) * 0.04))
    scale = min(target_width / foreground.width, (height * 0.62) / foreground.height)
    foreground = foreground.resize((max(1, int(foreground.width * scale)), max(1, int(foreground.height * scale))), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    cx = width // 2 + ((kind % 3) - 1) * 18
    cy = int(height * 0.69)
    shadow_draw.ellipse((cx - foreground.width // 2, cy - 28, cx + foreground.width // 2, cy + 35), fill=(0, 0, 0, 70))
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(22)))
    x = (width - foreground.width) // 2 + ((kind % 3) - 1) * 18
    y = int(height * 0.38) - foreground.height // 2 + ((kind % 2) * 10)
    canvas.alpha_composite(foreground, (x, y))
    output = io.BytesIO()
    canvas.convert("RGB").save(output, "JPEG", quality=95, optimize=True)
    final = backend.watermark(output.getvalue())
    if len(final) < 10000:
        raise RuntimeError("Reference-locked image is unexpectedly small")
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
        raise RuntimeError("Queue file is missing; refusing image cleanup")
    queue = json.loads(base.QUEUE.read_text(encoding="utf-8"))
    completed = [x for x in queue.get("items", []) if x.get("status") == "completed"]
    referenced_names: set[str] = set()
    item_data: dict[str, tuple[Path, dict, list[str]]] = {}
    for item in completed:
        sid = str(item.get("source_id"))
        item_path = OUT / "items" / f"{sid}.json"
        if not item_path.exists():
            continue
        data = json.loads(item_path.read_text(encoding="utf-8"))
        names = [Path(name).name for name in (data.get("images") or item.get("images") or [])]
        referenced_names.update(names)
        item_data[sid] = (item_path, data, names)

    deleted_unrelated = []
    images_dir = OUT / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    for path in images_dir.iterdir():
        if path.is_file() and path.name not in referenced_names:
            path.unlink(missing_ok=True)
            deleted_unrelated.append(path.name)

    rebuilt, skipped, failures = [], [], []
    for item in completed:
        sid = str(item.get("source_id"))
        record = item_data.get(sid)
        if not record:
            skipped.append({"source_id": sid, "reason": "item JSON missing"})
            continue
        item_path, data, names = record
        if len(names) != 5:
            skipped.append({"source_id": sid, "reason": f"expected 5 images, found {len(names)}"})
            continue
        try:
            for name in names:
                (images_dir / name).unlink(missing_ok=True)
            hashes = []
            for kind, name in enumerate(names, 1):
                blob, digest = make_product_image({**item, **data}, kind)
                (images_dir / name).write_bytes(blob)
                hashes.append(digest)
                time.sleep(0.15)
            stamp = now()
            data["image_sha256"] = hashes
            data["image_rebuild_policy"] = POLICY
            data["image_rebuilt_at"] = stamp
            data["image_generation_mode"] = "reference-locked-product-composite"
            item_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            rebuilt.append(sid)
            print(f"image_rebuilt source_id={sid}", flush=True)
        except Exception as exc:
            failures.append({"source_id": sid, "error": str(exc)[:1200]})
            print(f"image_rebuild_failed source_id={sid} error={exc}", flush=True)
            break

    summary = {
        "policy": POLICY,
        "completed": not failures and len(rebuilt) + len(skipped) == len(completed),
        "completed_at": now() if not failures else None,
        "completed_posts": len(rebuilt),
        "deleted_unrelated_images": deleted_unrelated,
        "skipped_posts": skipped,
        "failures": failures,
    }
    MARKER.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        raise RuntimeError(f"Reference-locked rebuild stopped after {len(rebuilt)} posts: {failures[0]['error']}")
    print(f"image_rebuild_completed posts={len(rebuilt)} deleted_unrelated={len(deleted_unrelated)} policy={POLICY}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
