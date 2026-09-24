#!/usr/bin/env python3
"""Create immutable, upload-ready ZIP packages for completed city-content batches."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "city-content-queue"
PACKAGES = OUT / "packages"
BATCH_SIZE = max(1, int(os.getenv("PACKAGE_BATCH_SIZE", "50")))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_id(item: dict) -> str:
    return str(item.get("source_id"))


def load_json(path: Path, default: dict) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
    return value if isinstance(value, dict) else default


def previous_packages() -> dict[str, dict]:
    manifest = load_json(PACKAGES / "manifest.json", {})
    result = {}
    for package in manifest.get("packages", []):
        if isinstance(package, dict) and package.get("batch"):
            result[str(package["batch"])] = package
    return result


def ordered_completed(completed: list[dict], old_packages: dict[str, dict]) -> list[dict]:
    """Keep already packaged posts in their original immutable batches.

    New completions are appended after the locked package order.  This prevents
    a late timestamp or a queue re-sort from changing an existing ZIP.
    """
    by_id = {source_id(item): item for item in completed}
    locked = []
    seen = set()
    for package in old_packages.values():
        for post in package.get("posts", []):
            sid = str(post.get("source_id"))
            if sid in by_id and sid not in seen:
                locked.append(by_id[sid])
                seen.add(sid)
    remaining = [item for item in completed if source_id(item) not in seen]
    remaining.sort(key=lambda item: (item.get("completed_at", ""), source_id(item)))
    return locked + remaining


def healthy_existing_zip(path: Path, batch_name: str, expected: list[dict]) -> dict | None:
    """Return the embedded manifest only when an existing ZIP is complete."""
    expected_ids = {source_id(item) for item in expected}
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                return None
            names = set(archive.namelist())
            if "manifest.json" not in names:
                return None
            embedded = json.loads(archive.read("manifest.json").decode("utf-8"))
            actual_ids = {str(post.get("source_id")) for post in embedded.get("posts", [])}
            if (
                embedded.get("batch") != batch_name
                or int(embedded.get("post_count", 0)) != len(expected)
                or actual_ids != expected_ids
                or "sql/create-batch.sql" not in names
                or "sql/rollback-batch.sql" not in names
                or len([name for name in names if name.startswith("items/") and name.endswith(".json")]) < len(expected)
                or not any(name.startswith("images/") for name in names)
            ):
                return None
            embedded["zip"] = path.name
            embedded["zip_sha256"] = sha256(path)
            embedded["zip_bytes"] = path.stat().st_size
            return embedded
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile):
        return None


def build_package(batch: list[dict], batch_name: str) -> dict:
    work = PACKAGES / batch_name
    if work.exists():
        shutil.rmtree(work)
    (work / "sql").mkdir(parents=True)
    (work / "images").mkdir(parents=True)
    (work / "items").mkdir(parents=True)

    create_parts = [f"-- Upload-ready SQL for {BATCH_SIZE} completed generated posts"]
    rollback_parts = [f"-- Rollback SQL for this {BATCH_SIZE}-post package"]
    files = []
    posts = []
    missing = []

    for item in batch:
        sid = source_id(item)
        posts.append(
            {
                "source_id": sid,
                "city": item.get("city"),
                "province": item.get("province"),
                "topic": item.get("topic"),
                "slug": item.get("slug"),
                "completed_at": item.get("completed_at"),
                "word_count": item.get("word_count"),
            }
        )
        for src_dir, collector in (("sql", create_parts), ("rollback", rollback_parts)):
            src = OUT / src_dir / f"{sid}.sql"
            if src.exists():
                collector.append(f"\n-- {src_dir}: {sid}\n" + src.read_text(encoding="utf-8"))
            else:
                missing.append(str(src.relative_to(OUT)))

        item_json = OUT / "items" / f"{sid}.json"
        if not item_json.exists():
            missing.append(str(item_json.relative_to(OUT)))
            image_names = item.get("images") or []
        else:
            shutil.copy2(item_json, work / "items" / item_json.name)
            files.append(str(Path("items") / item_json.name))
            data = load_json(item_json, {})
            image_names = data.get("images") or item.get("images") or []

        for image in image_names:
            src = OUT / "images" / Path(str(image)).name
            if not src.exists():
                missing.append(str(src.relative_to(OUT)))
                continue
            shutil.copy2(src, work / "images" / src.name)
            files.append(str(Path("images") / src.name))

    if missing:
        raise RuntimeError("Cannot create healthy package; missing artifacts: " + ", ".join(sorted(set(missing))[:20]))

    (work / "sql" / "create-batch.sql").write_text("\n".join(create_parts) + "\n", encoding="utf-8")
    (work / "sql" / "rollback-batch.sql").write_text("\n".join(rollback_parts) + "\n", encoding="utf-8")
    files += ["sql/create-batch.sql", "sql/rollback-batch.sql"]
    manifest = {
        "batch": batch_name,
        "post_count": len(batch),
        "posts": posts,
        "files": sorted(set(files)),
    }
    (work / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = PACKAGES / f"{batch_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(work.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(work).as_posix())

    manifest["zip"] = zip_path.name
    manifest["zip_sha256"] = sha256(zip_path)
    manifest["zip_bytes"] = zip_path.stat().st_size
    return manifest


def main() -> None:
    queue_path = OUT / "queue.json"
    if not queue_path.exists():
        print("no queue.json; skipping packages")
        return

    queue = load_json(queue_path, {})
    completed = [item for item in queue.get("items", []) if item.get("status") == "completed"]
    completed.sort(key=lambda item: (item.get("completed_at", ""), source_id(item)))
    PACKAGES.mkdir(parents=True, exist_ok=True)
    old_packages = previous_packages()
    ordered = ordered_completed(completed, old_packages)

    package_manifest = []
    for batch_no, start in enumerate(range(0, len(ordered), BATCH_SIZE), 1):
        batch = ordered[start : start + BATCH_SIZE]
        if len(batch) < BATCH_SIZE:
            break
        batch_name = f"batch-{batch_no:03d}-posts-{start + 1:04d}-{start + len(batch):04d}"
        zip_path = PACKAGES / f"{batch_name}.zip"
        existing = healthy_existing_zip(zip_path, batch_name, batch) if zip_path.exists() else None
        if existing is not None:
            package_manifest.append(existing)
            print(f"Already packaged; preserved: {zip_path.name}")
        else:
            package_manifest.append(build_package(batch, batch_name))
            print(f"Created or repaired: {zip_path.name}")

    top_level = {
        "batch_size": BATCH_SIZE,
        "ready_batches": len(package_manifest),
        "packages": package_manifest,
    }
    (PACKAGES / "manifest.json").write_text(
        json.dumps(top_level, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"batch_size": BATCH_SIZE, "ready_batches": len(package_manifest), "package_dir": str(PACKAGES)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
