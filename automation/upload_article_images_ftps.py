#!/usr/bin/env python3
"""Upload generated article images to their public WordPress upload path."""
from __future__ import annotations

import os
from pathlib import Path

from upload_city_batches_ftps import connect

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "artifacts" / "article-content-queue" / "images"
UPLOAD_SUBDIR = (os.getenv("ARTICLE_IMAGE_UPLOAD_SUBDIR") or "2026/09/navar-article-generated").strip("/")
REMOTE_DIR = f"wp-content/uploads/{UPLOAD_SUBDIR}"


def ensure_remote_dir(ftp, path: str) -> None:
    ftp.cwd("/")
    for part in Path(path).parts:
        if part in {"", "/"}:
            continue
        try:
            ftp.cwd(part)
        except Exception:
            ftp.mkd(part)
            ftp.cwd(part)


def main() -> int:
    files = sorted(p for p in IMAGES.glob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg"})
    if not files:
        print("No newly generated article images; FTPS upload skipped.")
        return 0

    # connect() validates TLS/login using the existing FTPS configuration.
    # The workflow sets FTP_REMOTE_DIR=/, then this script creates/cwds to the
    # public WordPress upload directory.
    ftp = connect()
    try:
        ensure_remote_dir(ftp, REMOTE_DIR)
        for path in files:
            size = path.stat().st_size
            temp_name = f".{path.name}.uploading"
            with path.open("rb") as stream:
                ftp.storbinary(f"STOR {temp_name}", stream, blocksize=1024 * 1024)
            remote_size = ftp.size(temp_name)
            if remote_size != size:
                try:
                    ftp.delete(temp_name)
                finally:
                    raise RuntimeError(
                        f"Image size verification failed for {path.name}: local={size}, remote={remote_size}"
                    )
            try:
                ftp.delete(path.name)
            except Exception:
                pass
            ftp.rename(temp_name, path.name)
            print(f"Uploaded article image: {path.name} ({size} bytes)")
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())