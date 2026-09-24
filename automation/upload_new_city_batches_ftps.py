#!/usr/bin/env python3
"""Upload only new or changed, manifest-listed city ZIP batches over explicit FTPS."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from upload_city_batches_ftps import PACKAGES, connect

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "artifacts" / "city-content-queue" / "ftps-upload-state.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {"files": {}}
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"files": {}}
    except (OSError, json.JSONDecodeError):
        return {"files": {}}


def manifest_packages() -> list[Path]:
    manifest_path = PACKAGES / "manifest.json"
    if not manifest_path.exists():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid package manifest: {exc}") from exc
    paths = []
    for package in manifest.get("packages", []):
        name = package.get("zip") if isinstance(package, dict) else None
        if not name or Path(str(name)).name != str(name) or not str(name).endswith(".zip"):
            raise RuntimeError(f"Invalid package name in manifest: {name!r}")
        path = PACKAGES / str(name)
        if not path.is_file():
            raise RuntimeError(f"Package listed in manifest is missing: {path}")
        paths.append(path)
    return paths


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    packages = sorted(manifest_packages())
    state = load_state()
    tracked = state.setdefault("files", {})
    if not packages:
        print("No manifest-listed ZIP batches are currently available; nothing to upload.")
        return 0

    pending = []
    skipped = 0
    for path in packages:
        digest = sha256(path)
        size = path.stat().st_size
        previous = tracked.get(path.name, {})
        if previous.get("sha256") == digest and int(previous.get("size", -1)) == size:
            print(f"Already uploaded; skipped: {path.name}")
            skipped += 1
        else:
            pending.append((path, digest, size))

    if not pending:
        print(json.dumps({"uploaded": 0, "skipped": skipped, "checked": len(packages)}, ensure_ascii=False))
        return 0

    ftp = connect()
    uploaded = 0
    try:
        for path, digest, size in pending:
            with path.open("rb") as stream:
                ftp.storbinary(f"STOR {path.name}", stream, blocksize=1024 * 1024)
            remote_size = ftp.size(path.name)
            if remote_size != size:
                raise RuntimeError(
                    f"Size verification failed for {path.name}: local={size}, remote={remote_size}"
                )
            tracked[path.name] = {"sha256": digest, "size": size, "uploaded_at": now()}
            print(f"Uploaded and verified: {path.name} ({size} bytes)")
            uploaded += 1
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    state["last_run"] = {
        "uploaded": uploaded,
        "skipped": skipped,
        "checked": len(packages),
        "completed_at": now(),
    }
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(state["last_run"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
