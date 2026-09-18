#!/usr/bin/env python3
"""Upload generated ZIP batches to the WordPress host over explicit FTPS."""
from __future__ import annotations

import argparse
import os
import ssl
import sys
from ftplib import FTP_TLS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "artifacts" / "city-content-queue" / "packages"


def env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"{name} is missing")
    return value or ""


def connect() -> FTP_TLS:
    host = env("FTP_HOST", required=True)
    user = env("FTP_USER", required=True)
    password = env("FTP_PASSWORD", required=True)
    port = int(env("FTP_PORT", "21"))
    remote_dir = env("FTP_REMOTE_DIR", required=True)
    verify_tls = env("FTP_TLS_VERIFY", "false").lower() in {"1", "true", "yes"}

    if verify_tls:
        context = ssl.create_default_context()
    else:
        # TLS encryption remains enabled, but certificate chain and hostname
        # verification are intentionally disabled for this hosting endpoint.
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        print("WARNING: FTPS certificate verification is disabled")

    ftp = FTP_TLS(context=context, timeout=90)
    ftp.connect(host, port)
    ftp.auth()          # explicit FTPS negotiation on port 21
    ftp.prot_p()        # encrypt the data channel as well
    ftp.login(user=user, passwd=password)
    ftp.voidcmd("TYPE I")
    ftp.cwd(remote_dir)
    print(f"Connected with explicit FTPS: {host}:{port}")
    print(f"Remote directory: {remote_dir}")
    return ftp


def upload(test_only: bool) -> int:
    files = sorted(PACKAGES.glob("*.zip"))
    if test_only:
        if not files:
            raise RuntimeError(f"No ZIP batch found in {PACKAGES}")
        files = files[:1]
    elif not files:
        print("No ZIP batches are currently available; nothing to upload.")
        return 0

    ftp = connect()
    try:
        for path in files:
            size = path.stat().st_size
            with path.open("rb") as stream:
                ftp.storbinary(f"STOR {path.name}", stream, blocksize=1024 * 1024)
            remote_size = ftp.size(path.name)
            if remote_size != size:
                raise RuntimeError(
                    f"Size verification failed for {path.name}: local={size}, remote={remote_size}"
                )
            print(f"Uploaded and verified: {path.name} ({size} bytes)")
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="upload only the first ZIP")
    parser.add_argument("--all", action="store_true", help="upload all ZIP batches")
    args = parser.parse_args()
    try:
        return upload(test_only=args.test)
    except Exception as exc:
        print(f"FTPS upload failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
