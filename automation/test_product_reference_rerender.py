#!/usr/bin/env python3
"""Generate two review samples using reference-conditioned 3D product rerendering."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(__file__).with_name("assets")
OUT = ROOT / "artifacts" / "product-rerender-test"
API = os.getenv("IMAGE_ENDPOINT") or os.getenv(
    "AGNES_API_BASE", "https://apihub.agnes-ai.com/v1"
).rstrip("/") + "/images/generations"
KEY = (os.getenv("IMAGE_API_KEY") or os.getenv("AGNES_API_KEY", "")).strip()
MODEL = os.getenv("IMAGE_MODEL") or os.getenv(
    "AGNES_IMAGE_MODEL", "agnes-image-2.5-flash"
)
PHONE_LABEL = "AFP | 09134922013"


CASES = {
    "tape": {
        "asset": "afp-tape.webp.b64",
        "text": 'The carton must keep the exact readable marks "AFP" and "Drip Irrigation Tape".',
        "shape": (
            "a wide cylindrical 1000-meter drip-tape roll inside its white-and-blue "
            "printed carton sleeve, with the same diameter-to-height ratio, central top hole, "
            "straight carton walls and blue lower band"
        ),
        "scene": "a real drip-irrigated row-crop field during installation",
    },
    "layflat": {
        "asset": "afp-layflat.webp.b64",
        "text": 'The package must keep the exact readable marks "AFP" and "layflat".',
        "shape": (
            "a low, wide black woven layflat hose coil held by the same folded printed "
            "cardboard top and bottom pieces and the same crossing black straps, preserving "
            "the center opening, coil thickness and package proportions"
        ),
        "scene": "a real farm water-transfer setup beside cultivated rows",
    },
    "layflat-bare": {
        "asset": "afp-layflat-bare.jpg.b64",
        "mime": "image/jpeg",
        "text": (
            "This unboxed hose has no carton label: do not add AFP, layflat, a logo "
            "or any invented writing to the black hose."
        ),
        "shape": (
            "one low wide coil of unboxed black woven layflat hose, preserving the "
            "flat concentric layers, short hollow cardboard center, woven diagonal "
            "surface texture, coil thickness and the small loose hose end"
        ),
        "scene": "a practical layflat-hose installation beside a farm water-transfer line",
    },
}


def prompt(case: dict) -> str:
    return (
        "Create one photorealistic 16:9 agricultural editorial photograph. The attached image "
        "is an identity and geometry reference for the product, not a flat layer to paste. "
        f"Reconstruct the product as a true three-dimensional object: {case['shape']}. "
        "Show it from a slightly different but physically plausible three-quarter camera angle, "
        "about 10 to 20 degrees away from the reference angle. Preserve the exact product family, "
        "silhouette, packaging construction, proportions, material, printed-panel layout and "
        "brand colors. Do not invent a new package and do not turn it into a pipe, wheel, box or "
        f"different roll. {case['text']} The setting is {case['scene']}. "
        "The agricultural activity and article context occupy 75 to 85 percent of the frame; "
        "the product is a secondary object occupying about 12 to 18 percent, positioned naturally "
        "on the lower third. It must share the scene's perspective, depth of field, color cast, "
        "contact shadow, reflected light and slight soil interaction. It may be subtly occluded by "
        "a few foreground soil particles or leaves. Absolutely no sticker look, hard cut-out edge, "
        "white halo, flat front-facing packshot, collage, floating object, duplicate product, "
        "caption, added logo or invented writing."
    )


def reference_data_url(filename: str) -> str:
    encoded = (ASSETS / filename).read_text(encoding="ascii").strip()
    mime = "image/jpeg" if filename.endswith(".jpg.b64") else "image/webp"
    return f"data:{mime};base64," + encoded


def add_phone_watermark(image: Image.Image) -> Image.Image:
    canvas = image.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 27)
    except OSError:
        font = ImageFont.load_default()
    box = draw.textbbox((0, 0), PHONE_LABEL, font=font)
    width, height = box[2] - box[0], box[3] - box[1]
    margin, pad_x, pad_y = 18, 16, 10
    x = canvas.width - width - margin - 2 * pad_x
    y = canvas.height - height - margin - 2 * pad_y
    draw.rounded_rectangle(
        (x, y, canvas.width - margin, canvas.height - margin),
        radius=8,
        fill=(0, 0, 0, 178),
    )
    draw.text((x + pad_x, y + pad_y - box[1]), PHONE_LABEL, font=font, fill="white")
    return Image.alpha_composite(canvas, overlay).convert("RGB")


def generate(name: str, case: dict) -> dict:
    payload = {
        "model": MODEL,
        "prompt": prompt(case),
        "size": "1024x768",
        "return_base64": True,
        "extra_body": {
            "response_format": "b64_json",
            "image": [reference_data_url(case["asset"])],
        },
    }
    last = None
    for attempt in range(1, 4):
        request = urllib.request.Request(
            API,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": "Bearer " + KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "navar-product-rerender-test/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                data = json.loads(response.read())
            row = (data.get("data") or [{}])[0]
            if row.get("b64_json"):
                blob = base64.b64decode(row["b64_json"])
            elif row.get("url"):
                with urllib.request.urlopen(row["url"], timeout=300) as response:
                    blob = response.read()
            else:
                raise RuntimeError("image response has neither b64_json nor url")
            image = Image.open(io.BytesIO(blob)).convert("RGB")
            width, height = image.size
            target = 16 / 9
            if width / height > target:
                new_width = int(height * target)
                left = (width - new_width) // 2
                image = image.crop((left, 0, left + new_width, height))
            else:
                new_height = int(width / target)
                top = (height - new_height) // 2
                image = image.crop((0, top, width, top + new_height))
            image = image.resize((1200, 675), Image.Resampling.LANCZOS)
            image = add_phone_watermark(image)
            output = io.BytesIO()
            image.save(output, "WEBP", quality=72, method=6)
            result = output.getvalue()
            path = OUT / f"{name}-reference-rerender.webp"
            path.write_bytes(result)
            return {
                "case": name,
                "file": path.name,
                "sha256": hashlib.sha256(result).hexdigest(),
                "bytes": len(result),
                "model": MODEL,
                "prompt": prompt(case),
            }
        except (Exception, urllib.error.HTTPError) as exc:
            last = exc
            print(f"sample={name} attempt={attempt}/3 error={exc}", flush=True)
            if attempt < 3:
                time.sleep(5 * attempt)
    raise RuntimeError(f"{name} sample failed: {last}") from last


def main() -> int:
    if not KEY:
        raise RuntimeError("IMAGE_API_KEY/AGNES_API_KEY is missing")
    OUT.mkdir(parents=True, exist_ok=True)
    records = [generate(name, case) for name, case in CASES.items()]
    (OUT / "manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(records, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())