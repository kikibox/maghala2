#!/usr/bin/env python3
"""Deterministic five-image variation and product-identity policy."""
from __future__ import annotations

import hashlib
import random
import re
import subprocess
from difflib import SequenceMatcher
from pathlib import Path

DRIP_TAPE_REFERENCE = "https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp"
LAYFLAT_REFERENCE = "https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp"

CAMERAS = (
    "eye-level wide view from the front-left at standing height",
    "low ground-level three-quarter view from the right",
    "high oblique view from approximately three meters",
    "long-lens lateral view at crop-canopy height",
    "close waist-height diagonal view with shallow perspective",
    "rear three-quarter field view at chest height",
    "top-down near-vertical technical view",
)
BACKGROUNDS = (
    "open row-crop field with distant windbreak trees",
    "compact farm service lane beside cultivated rows",
    "greenhouse edge with diffuse structure in the distance",
    "dry semi-arid field margin with sparse native vegetation",
    "irrigation head-unit area beside a working field",
    "orchard aisle with ordered tree rows",
    "freshly prepared seedbed with no buildings visible",
)
LIGHTING = (
    "cool early-morning side light",
    "soft overcast midday light",
    "warm late-afternoon backlight",
    "bright high-noon light softened by thin cloud",
    "golden-hour cross light from camera-left",
    "blue-hour ambient light with subtle practical farm lighting",
    "post-rain diffused daylight with gentle reflections",
)
COMPOSITIONS = (
    "rule-of-thirds composition with strong leading crop rows",
    "center-weighted technical composition with balanced negative space",
    "asymmetric diagonal composition with the subject in the lower-left",
    "layered foreground-midground-background composition",
    "wide environmental composition with the subject in the right third",
    "tight editorial composition framed by crop leaves",
    "S-curve composition following the irrigation line",
)
SUBJECT_POSITIONS = (
    "lower-left third", "lower-right third", "center foreground",
    "right-middle third", "left-middle third", "center midground",
    "upper-right intersection",
)
HORIZONS = (
    "low horizon", "high horizon", "level mid-frame horizon",
    "slightly rising left-to-right horizon", "slightly falling left-to-right horizon",
    "horizon hidden by crop canopy", "distant horizon compressed by a long lens",
)
SOILS = (
    "fine dry loam", "dark moist loam", "light sandy soil",
    "reddish clay-loam", "mulched cultivated soil", "gravelly farm soil",
    "freshly irrigated textured soil",
)
ROW_LAYOUTS = (
    "parallel straight rows", "diagonal converging rows", "curved contour rows",
    "wide raised beds", "narrow paired rows", "orchard grid rows",
    "alternating planted and service rows",
)
ROLES = {
    1: "featured hero and overall field context",
    2: "close product or material detail",
    3: "technical scene showing filters, regulators, valves or irrigation equipment in context",
    4: "real installation or active use in the field",
    5: "maintenance, inspection or connection check in the field",
}
APPROVED = {
    "tape20": ("AFP", "آبگسترفراپارسیان", "DRIP Irrigation tape"),
    "layflat": ("AFP", "آبگسترفراپارسیان", "layflat"),
}
TOKEN_RE = re.compile(r"[\u0600-\u06ffA-Za-z0-9]+")


def stable_seed(item: dict, namespace: str = "image") -> int:
    material = "|".join(str(item.get(k) or "") for k in (
        "id", "city", "title", "topic", "topic_title", "focus", "vertical"
    ))
    digest = hashlib.sha256(f"{namespace}|{material}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _choice(options, item, kind, namespace):
    values = list(options)
    random.Random(stable_seed(item, namespace)).shuffle(values)
    return values[(kind - 1) % len(values)]


def product_family(item: dict) -> str:
    text = " ".join(str(item.get(k) or "") for k in ("title", "focus", "topic", "slug")).lower()
    if any(value in text for value in ("layflat", "لوله نخی", "لوله نخ", "لوله تاشو")):
        return "layflat"
    return "tape20"


def product_centered(item: dict, kind: int) -> bool:
    text = " ".join(str(item.get(k) or "") for k in ("title", "focus", "vertical")).lower()
    product_topic = item.get("vertical") == "product" or any(
        value in text for value in ("نوار تیپ", "لوله نخی", "لوله نخ", "لوله تاشو", "drip tape", "layflat")
    )
    return bool(product_topic and kind in (1, 2))


def variation_spec(item: dict, kind: int) -> dict:
    if kind not in ROLES:
        raise ValueError(f"unsupported image number: {kind}")
    token = hashlib.sha256(f"{stable_seed(item)}|{kind}".encode()).hexdigest()[:16]
    return {
        "kind": kind,
        "role": ROLES[kind],
        "camera": _choice(CAMERAS, item, kind, "camera"),
        "background": _choice(BACKGROUNDS, item, kind, "background"),
        "lighting": _choice(LIGHTING, item, kind, "lighting"),
        "composition": _choice(COMPOSITIONS, item, kind, "composition"),
        "subject_position": _choice(SUBJECT_POSITIONS, item, kind, "position"),
        "horizon": _choice(HORIZONS, item, kind, "horizon"),
        "soil": _choice(SOILS, item, kind, "soil"),
        "row_layout": _choice(ROW_LAYOUTS, item, kind, "rows"),
        "variation_token": token,
    }


def reference_images(item: dict, kind: int) -> list[str]:
    if not product_centered(item, kind):
        return []
    return [LAYFLAT_REFERENCE if product_family(item) == "layflat" else DRIP_TAPE_REFERENCE]


def image_prompt(item: dict, kind: int, hide_label: bool = False) -> str:
    spec = variation_spec(item, kind)
    family = product_family(item)
    identity = ""
    if product_centered(item, kind):
        allowed = ", ".join(f'"{value}"' for value in APPROVED[family])
        if hide_label:
            identity = (
                "Use the supplied reference to preserve the exact package shape, colors, core, straps, folds, "
                "logo position and label-panel geometry, but turn the readable label away from camera or keep it "
                "small and softly out of focus. No text or logo may be readable."
            )
        else:
            identity = (
                "The supplied product reference is mandatory and identity-locked. Preserve exact packaging shape, "
                "colors, central core, straps, folds, logo and label-panel positions. Do not redesign or translate "
                f"the label. The only permitted readable strings are {allowed}."
            )
    elif kind >= 3:
        identity = (
            "This is a technical field scene, not a package portrait. Keep retail packaging outside the frame or "
            "small and defocused in the background. Show real equipment, installation or maintenance appropriate "
            "to the image role."
        )

    return (
        "Photorealistic single-frame agricultural editorial photograph, clean 16:9 landscape, realistic scale. "
        f"Image role: {spec['role']}. Camera: {spec['camera']}. Subject position: {spec['subject_position']}. "
        f"Composition: {spec['composition']}. Lighting/time: {spec['lighting']}. Background/environment: "
        f"{spec['background']}. Horizon: {spec['horizon']}. Soil texture: {spec['soil']}. Crop-row layout: "
        f"{spec['row_layout']}. {identity} "
        "Exactly one coherent scene; no duplicate product, no floating object, no collage, no invented logo, "
        "no fake text, no gibberish, no watermark and no caption. "
        f"Variation token for deterministic generation only: {spec['variation_token']}. "
        "The variation token is metadata and must never be visible in the image."
    )


def ocr_text(path: Path) -> str:
    result = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", "fas+eng"],
        capture_output=True, text=True, timeout=90, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"OCR failed: {result.stderr[:300]}")
    return " ".join(result.stdout.split())


def _normalized_tokens(value: str) -> set[str]:
    return {
        token.lower().replace("ي", "ی").replace("ك", "ک")
        for token in TOKEN_RE.findall(value or "") if len(token) >= 3
    }


def validate_ocr(path: Path, item: dict, kind: int, hide_label: bool = False) -> tuple[bool, str]:
    observed_text = ocr_text(path)
    observed = _normalized_tokens(observed_text)
    family = product_family(item)
    allowed = _normalized_tokens(" ".join(APPROVED[family]))
    if hide_label or not product_centered(item, kind):
        return (not observed, observed_text)
    if not observed:
        return False, observed_text
    matched = {
        token for token in observed
        if any(SequenceMatcher(None, token, allowed_token).ratio() >= 0.76 for allowed_token in allowed)
    }
    suspicious = observed - matched
    return bool(matched) and not suspicious, observed_text
