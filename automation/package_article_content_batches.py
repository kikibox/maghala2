#!/usr/bin/env python3
"""Build incremental, upload-ready 50-article ZIP packages."""
from __future__ import annotations
import hashlib, json, os, shutil, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "article-content-queue"
PACKAGES = OUT / "packages"
BATCH_SIZE = max(1, int(os.getenv("PACKAGE_BATCH_SIZE", "50")))
UPLOAD_SUBDIR = (os.getenv("ARTICLE_IMAGE_UPLOAD_SUBDIR") or "2026/09/navar-article-generated").strip("/")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    qpath = OUT / "queue.json"
    if not qpath.exists():
        print("no queue.json; skipping article packages")
        return 0
    queue = json.loads(qpath.read_text(encoding="utf-8"))
    completed = [x for x in queue.get("items", []) if x.get("status") == "completed"]
    completed.sort(key=lambda x: (x.get("completed_at", ""), str(x.get("id", ""))))
    PACKAGES.mkdir(parents=True, exist_ok=True)
    package_records = []
    for batch_no, start in enumerate(range(0, len(completed), BATCH_SIZE), 1):
        batch = completed[start:start + BATCH_SIZE]
        if len(batch) < BATCH_SIZE:
            continue
        name = f"batch-{batch_no:03d}-articles-{start+1:04d}-{start+len(batch):04d}"
        work = PACKAGES / name
        archive = PACKAGES / f"{name}.zip"
        if work.exists():
            shutil.rmtree(work)
        (work / "sql").mkdir(parents=True)
        (work / "items").mkdir(parents=True)
        image_root = work / "wp-content" / "uploads" / UPLOAD_SUBDIR
        image_root.mkdir(parents=True)
        create_parts = [f"-- Create {len(batch)} generated articles ({name})"]
        rollback_parts = [f"-- Roll back {len(batch)} generated articles ({name})"]
        posts = []
        files = []
        for item in batch:
            item_id = str(item.get("id"))
            posts.append({
                "id": item_id, "title": item.get("title"), "slug": item.get("slug"),
                "vertical": item.get("vertical"), "completed_at": item.get("completed_at"),
                "word_count": item.get("word_count"),
            })
            create_file = OUT / "sql" / f"{item_id}.sql"
            rollback_file = OUT / "rollback" / f"{item_id}.sql"
            if not create_file.exists() or not rollback_file.exists():
                raise RuntimeError(f"SQL pair missing for completed item {item_id}")
            create_parts.append(f"\n-- article: {item_id}\n" + create_file.read_text(encoding="utf-8"))
            rollback_parts.append(f"\n-- article: {item_id}\n" + rollback_file.read_text(encoding="utf-8"))
            item_file = OUT / "items" / f"{item_id}.json"
            if not item_file.exists():
                raise RuntimeError(f"Item JSON missing for completed item {item_id}")
            shutil.copy2(item_file, work / "items" / item_file.name)
            files.append(f"items/{item_file.name}")
            data = json.loads(item_file.read_text(encoding="utf-8"))
            for image in data.get("images", []):
                image_name = Path(image["name"] if isinstance(image, dict) else image).name
                source = OUT / "images" / image_name
                if not source.exists():
                    raise RuntimeError(f"Image missing for {item_id}: {image_name}")
                shutil.copy2(source, image_root / image_name)
                files.append(f"wp-content/uploads/{UPLOAD_SUBDIR}/{image_name}")
        (work / "sql" / "create-batch.sql").write_text("\n".join(create_parts) + "\n", encoding="utf-8")
        (work / "sql" / "rollback-batch.sql").write_text("\n".join(rollback_parts) + "\n", encoding="utf-8")
        files += ["sql/create-batch.sql", "sql/rollback-batch.sql"]
        readme = (
            "1) پوشه wp-content را در ریشه وردپرس آپلود کنید.\n"
            "2) سپس sql/create-batch.sql را در پایگاه داده وردپرس اجرا کنید.\n"
            "3) برای بازگشت، sql/rollback-batch.sql را اجرا کنید و تصاویر همان بسته را حذف کنید.\n"
            "4) پیش از اجرا از دیتابیس نسخه پشتیبان بگیرید.\n"
        )
        (work / "README-fa.txt").write_text(readme, encoding="utf-8")
        files.append("README-fa.txt")
        manifest = {"batch": name, "post_count": len(batch), "upload_subdir": UPLOAD_SUBDIR,
                    "posts": posts, "files": sorted(files)}
        (work / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in sorted(work.rglob("*")):
                if file.is_file():
                    zf.write(file, file.relative_to(work))
        manifest.update(zip=archive.name, zip_sha256=sha256(archive), zip_bytes=archive.stat().st_size)
        package_records.append(manifest)
    (PACKAGES / "manifest.json").write_text(json.dumps({
        "batch_size": BATCH_SIZE, "ready_batches": len(package_records), "packages": package_records,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"batch_size": BATCH_SIZE, "ready_batches": len(package_records)}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
