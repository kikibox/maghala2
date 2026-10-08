#!/usr/bin/env python3
"""Upload new/changed tj-ads batch ZIPs to the site FTP home over explicit FTPS (same connect() as maghala2)."""
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT.parent / 'automation'))
from upload_city_batches_ftps import connect  # maghala2

PKG = ROOT / 'artifacts/tj-ads/packages'
STATE = ROOT / 'artifacts/tj-ads/ftps-upload-state.json'


def main():
    try: state = json.loads(STATE.read_text(encoding='utf-8'))
    except Exception: state = {'files': {}}
    tracked = state.setdefault('files', {})
    pending = []
    for z in sorted(PKG.glob('*.zip')):
        d = hashlib.sha256(z.read_bytes()).hexdigest()
        if tracked.get(z.name, {}).get('sha256') != d: pending.append((z, d))
    if not pending:
        print('nothing to upload'); return
    ftp = connect()
    try:
        for z, d in pending:
            tmp = f'.{z.name}.uploading'
            with z.open('rb') as f: ftp.storbinary(f'STOR {tmp}', f, blocksize=1 << 20)
            if ftp.size(tmp) != z.stat().st_size:
                ftp.delete(tmp); raise RuntimeError('size mismatch ' + z.name)
            try: ftp.delete(z.name)
            except Exception: pass
            ftp.rename(tmp, z.name)
            tracked[z.name] = {'sha256': d, 'size': z.stat().st_size, 'uploaded_at': datetime.now(timezone.utc).isoformat()}
            print('uploaded', z.name)
    finally:
        try: ftp.quit()
        except Exception: ftp.close()
    STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
