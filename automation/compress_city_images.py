#!/usr/bin/env python3
"""Measure or apply WebP compression for generated city images."""
from __future__ import annotations

import argparse
import json
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "artifacts" / "city-content-queue" / "images"

def encode(path: Path, quality: int) -> bytes:
    with Image.open(path) as source:
        image = source.convert("RGB")
        output = BytesIO()
        image.save(output, format="WEBP", quality=quality, method=6)
        return output.getvalue()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--quality", type=int, default=78)
    parser.add_argument("--compare-quality", type=int, default=88)
    parser.add_argument("--report", default="artifacts/city-content-queue/image-compression-test.json")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("choose --dry-run or --apply")
    if not 40 <= args.quality <= 95:
        parser.error("quality must be between 40 and 95")

    paths = sorted(p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}) if IMAGE_DIR.exists() else []
    rows = []
    for path in paths:
        original = path.stat().st_size
        optimized = encode(path, args.quality)
        comparison = encode(path, args.compare_quality)
        target = path.with_suffix(".webp")
        if args.apply:
            target.write_bytes(optimized)
            if target != path:
                path.unlink()
        rows.append({
            "file": str(path.relative_to(ROOT)),
            "original_bytes": original,
            "quality": args.quality,
            "quality_bytes": len(optimized),
            "comparison_quality": args.compare_quality,
            "comparison_bytes": len(comparison),
            "output": str(target.relative_to(ROOT)),
        })

    def total(key):
        return sum(int(row[key]) for row in rows)

    original_total = total("original_bytes")
    quality_total = total("quality_bytes")
    compare_total = total("comparison_bytes")
    report = {
        "mode": "apply" if args.apply else "dry-run",
        "image_count": len(rows),
        "quality": args.quality,
        "comparison_quality": args.compare_quality,
        "original_bytes": original_total,
        "quality_bytes": quality_total,
        "comparison_bytes": compare_total,
        "quality_savings_percent": round((1 - quality_total / original_total) * 100, 2) if original_total else 0,
        "comparison_savings_percent": round((1 - compare_total / original_total) * 100, 2) if original_total else 0,
        "images": rows,
    }
    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "images"}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
