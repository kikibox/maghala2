#!/usr/bin/env python3
"""Rebuild completed city images with full-scene reference-conditioned generation.

No cut-out/composite is used. The image model receives the approved product
reference and must render the complete product photograph in a real field scene.
Policy note: this file intentionally preserves existing post image filenames.
"""
from __future__ import annotations
import base64, datetime as dt, hashlib, io, json, os, time, urllib.error, urllib.request
from pathlib import Path
from PIL import Image
import city_content_queue as base
import city_content_queue_cloudflare as backend
import image_prompt_policy

POLICY = "reference-conditioned-full-scene-v19"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "city-content-queue"
MARKER = OUT / "image-rebuild-reference-full-scene-v19.json"
MODEL = os.getenv("AGNES_IMAGE_MODEL", "agnes-image-2.0-flash")
API = os.getenv("AGNES_API_BASE", "https://apihub.agnes-ai.com/v1").rstrip("/")
KEY = os.getenv("AGNES_API_KEY", "").strip()
image_prompt_policy.install(backend)


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def full_scene_prompt(item: dict, kind: int) -> str:
    family = image_prompt_policy.product_family(item)
    city = item.get("city", "")
    province = item.get("province", "")
    roles = {
        1: "wide hero photograph with the product clearly visible on the soil and the crop rows providing context",
        2: "closer product photograph from a low natural camera angle, showing real contact with the soil",
        3: "technical but natural field photograph with the product resting on the ground and its material clearly visible",
        4: "field-use photograph showing the product placed naturally beside a crop row, without hands or extra equipment",
        5: "clean maintenance and selection photograph in a real agricultural setting, with the product grounded and fully visible",
    }
    if family == "layflat":
        product = (
            "The subject is exactly one black woven yarn-reinforced collapsible layflat hose roll matching the supplied "
            "approved packaged reference: same folded/rolled geometry, weave, width, thickness, straps and packaging. "
            "It must be a layflat/yarn hose product, never drip tape. Keep the single packaged roll intact on the ground."
        )
        forbidden = "No drip-tape roll, no white AFP tape cylinder, no round rigid pipe, no second hose, no fittings, valves, filters, tools, boxes, people, hands or invented labels."
    else:
        product = (
            "The subject is exactly one AFP 20-centimeter flat drip-irrigation tape roll matching the supplied approved "
            "reference: thin flat black tape layers and the same roll geometry. It must lie naturally on soil, not stand "
            "upright like a wheel and not become a round pipe or layflat hose."
        )
        forbidden = "No layflat/yarn hose, no white packaged cylinder, no round pipe, no second irrigation product, no fittings, valves, filters, tools, people, hands or invented labels."
    return (
        "Generate the complete final photorealistic product photograph from scratch using the supplied reference image "
        "only for product identity and shape control. Do not paste, cut out, collage, overlay or composite the reference; "
        "the product must be rendered as part of the same scene with matching perspective, light, soil contact, natural "
        "shadow and slight realistic dirt interaction. Real agricultural field in Iran, plausible crop rows and soil, "
        f"no landmark claim, city context {city}, {province}. {product} {roles.get(kind, roles[1])}. {forbidden} "
        "No generated text, captions, watermark, logo changes or fake writing. Natural commercial photography, 16:9."
    )


def generate_raw(item: dict, kind: int) -> tuple[str, str]:
    if not KEY:
        raise RuntimeError("AGNES_API_KEY is missing")
    refs = image_prompt_policy.reference_images(kind, item)
    payload = {
        "model": MODEL,
        "prompt": full_scene_prompt(item, kind),
        "size": "1024x768",
        "return_base64": True,
        "extra_body": {"response_format": "b64_json", "image": refs},
    }
    req = urllib.request.Request(
        API + "/images/generations", data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "navar-city-content-queue/19.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            data = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Agnes Image HTTP {exc.code}: {exc.read().decode('utf-8','replace')[:1200]}") from exc
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
        new_width = int(height * target); left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target); top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    image = image.resize((1200, 675), Image.Resampling.LANCZOS)
    output = io.BytesIO(); image.save(output, "JPEG", quality=93, optimize=True)
    blob = backend.watermark(output.getvalue())
    if len(blob) < 10000: raise RuntimeError("Generated image is unexpectedly small")
    name = f"{item['source_id']}-{kind}.jpg"
    (base.IMAGES / name).write_bytes(blob)
    return name, hashlib.sha256(blob).hexdigest()


def main() -> int:
    if MARKER.exists():
        try:
            old = json.loads(MARKER.read_text(encoding="utf-8"))
            if old.get("policy") == POLICY and old.get("completed") is True:
                print(f"image_rebuild=already_completed policy={POLICY}", flush=True); return 0
        except Exception: pass
    if not base.QUEUE.exists(): raise RuntimeError("Queue file is missing; refusing image cleanup")
    queue = json.loads(base.QUEUE.read_text(encoding="utf-8"))
    completed = [x for x in queue.get("items", []) if x.get("status") == "completed"]
    referenced: set[str] = set(); records = {}
    for item in completed:
        sid = str(item.get("source_id")); path = OUT / "items" / f"{sid}.json"
        if not path.exists(): continue
        data = json.loads(path.read_text(encoding="utf-8")); names = [Path(x).name for x in (data.get("images") or item.get("images") or [])]
        referenced.update(names); records[sid] = (path, data, names)
    deleted = []
    base.IMAGES.mkdir(parents=True, exist_ok=True)
    for path in base.IMAGES.iterdir():
        if path.is_file() and path.name not in referenced:
            path.unlink(missing_ok=True); deleted.append(path.name)
    rebuilt, skipped, failures = [], [], []
    for item in completed:
        sid = str(item.get("source_id")); record = records.get(sid)
        if not record:
            skipped.append({"source_id": sid, "reason": "item JSON missing"}); continue
        path, data, names = record
        if len(names) != 5:
            skipped.append({"source_id": sid, "reason": f"expected 5 images, found {len(names)}"}); continue
        enriched = {**item, **data}; family = image_prompt_policy.product_family(enriched)
        try:
            generated = []; hashes = []
            for kind in range(1, 6):
                generated_name, digest = generate_raw(enriched, kind)
                generated.append(generated_name); hashes.append(digest); time.sleep(1)
            # Keep the existing filenames because post HTML and SQL already reference them.
            for generated_name, old_name in zip(generated, names):
                source = base.IMAGES / generated_name
                target = base.IMAGES / old_name
                target.unlink(missing_ok=True)
                source.replace(target)
            stamp = now(); data["image_sha256"] = hashes; data["image_rebuild_policy"] = POLICY
            data["image_rebuilt_at"] = stamp; data["image_generation_mode"] = "reference-conditioned-full-scene"
            data["product_family"] = family; path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            rebuilt.append(sid); print(f"image_rebuilt source_id={sid} family={family}", flush=True)
        except Exception as exc:
            failures.append({"source_id": sid, "family": family, "error": str(exc)[:1200]})
            print(f"image_rebuild_failed source_id={sid} family={family} error={exc}", flush=True); break
    summary = {"policy": POLICY, "completed": not failures and len(rebuilt)+len(skipped)==len(completed), "completed_at": now() if not failures else None, "completed_posts": len(rebuilt), "deleted_unrelated_images": deleted, "skipped_posts": skipped, "failures": failures}
    MARKER.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures: raise RuntimeError(f"Full-scene rebuild stopped after {len(rebuilt)} posts: {failures[0]['error']}")
    print(f"image_rebuild_completed posts={len(rebuilt)} deleted_unrelated={len(deleted)} policy={POLICY}", flush=True)
    return 0

if __name__ == "__main__": raise SystemExit(main())
