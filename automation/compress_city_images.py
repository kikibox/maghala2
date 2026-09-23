#!/usr/bin/env python3
"""Measure or apply loss-controlled WebP compression for city images."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QUEUE_DIR = ROOT / "artifacts" / "city-content-queue"
IMAGE_DIR = QUEUE_DIR / "images"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
TEXT_SUFFIXES = {".json", ".sql", ".md", ".txt", ".csv", ".html", ".xml"}


def encode(path: Path, quality: int) -> bytes:
    with Image.open(path) as source:
        image = source.convert("RGB")
        output = BytesIO()
        image.save(output, format="WEBP", quality=quality, method=6)
        return output.getvalue()


def grouped_sources(paths: list[Path]) -> dict[Path, list[Path]]:
    groups: dict[Path, list[Path]] = defaultdict(list)
    for path in paths:
        groups[path.with_suffix(".webp")].append(path)
    return dict(groups)


def choose_source(candidates: list[Path]) -> Path:
    for suffix in (".png", ".jpg", ".jpeg", ".webp"):
        for path in candidates:
            if path.suffix.lower() == suffix:
                return path
    return candidates[0]


def rewrite_references(mapping: dict[str, str]) -> int:
    changed = 0
    for path in QUEUE_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = text
        for old, new in mapping.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--quality", type=int, default=60)
    parser.add_argument("--compare-quality", type=int, default=78)
    parser.add_argument(
        "--report",
        default="artifacts/city-content-queue/image-compression-report.json",
    )
    args = parser.parse_args()

    if not 40 <= args.quality <= 95:
        parser.error("quality must be between 40 and 95")

    paths = (
        sorted(
            path
            for path in IMAGE_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )
        if IMAGE_DIR.exists()
        else []
    )
    groups = grouped_sources(paths)
    rows: list[dict[str, object]] = []
    mapping: dict[str, str] = {}
    encoded_targets: dict[Path, bytes] = {}

    for target, candidates in sorted(groups.items()):
        source = choose_source(candidates)
        optimized = encode(source, args.quality)
        comparison = encode(source, args.compare_quality)
        encoded_targets[target] = optimized
        for candidate in candidates:
            mapping[candidate.name] = target.name
            rows.append(
                {
                    "file": str(candidate.relative_to(ROOT)),
                    "source_bytes": candidate.stat().st_size,
                    "quality": args.quality,
                    "quality_bytes": len(optimized),
                    "comparison_quality": args.compare_quality,
                    "comparison_bytes": len(comparison),
                    "output": str(target.relative_to(ROOT)),
                    "source_used": str(source.relative_to(ROOT)),
                }
            )

    rewritten = 0
    if args.apply:
        for target, data in encoded_targets.items():
            target.write_bytes(data)
        for path in paths:
            target = path.with_suffix(".webp")
            if path != target and path.exists():
                path.unlink()
        rewritten = rewrite_references(mapping)

    def total(key: str) -> int:
        return sum(int(row[key]) for row in rows)

    source_total = total("source_bytes")
    quality_total = sum(len(data) for data in encoded_targets.values())
    compare_total = sum(
        int(row["comparison_bytes"])
        for row in rows
        if row["file"] == row["source_used"]
    )
    report = {
        "mode": "apply" if args.apply else "dry-run",
        "image_count": len(paths),
        "unique_output_count": len(encoded_targets),
        "quality": args.quality,
        "comparison_quality": args.compare_quality,
        "source_bytes": source_total,
        "quality_bytes": quality_total,
        "comparison_bytes": compare_total,
        "quality_savings_percent": round(
            (1 - quality_total / source_total) * 100, 2
        )
        if source_total
        else 0,
        "comparison_savings_percent": round(
            (1 - compare_total / source_total) * 100, 2
        )
        if source_total
        else 0,
        "reference_files_rewritten": rewritten if args.apply else None,
        "images": rows,
    }
    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "images"},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
