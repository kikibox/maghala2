#!/usr/bin/env python3
"""Create upload-ready ZIP packages for every completed city-content batch."""
import json, shutil, zipfile, hashlib, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'city-content-queue'
PACKAGES = OUT / 'packages'
BATCH_SIZE = max(1, int(os.getenv('PACKAGE_BATCH_SIZE', '50')))

def sha256(path):
    h=hashlib.sha256(); h.update(Path(path).read_bytes()); return h.hexdigest()

def main():
    qpath = OUT / 'queue.json'
    if not qpath.exists():
        print('no queue.json; skipping packages')
        return
    q=json.loads(qpath.read_text(encoding='utf-8'))
    completed=[x for x in q.get('items',[]) if x.get('status')=='completed']
    completed.sort(key=lambda x: (x.get('completed_at',''), str(x.get('source_id',''))))
    PACKAGES.mkdir(parents=True, exist_ok=True)
    # Incremental packaging: never wipe existing batch archives. An untouched
    # batch keeps its previous .zip and .sha256 so the FTPS upload step can
    # skip it, and git does not re-commit unchanged 20 MB artifacts. Only
    # batches whose post membership or per-post source files changed are
    # (re)built in place.
    manifest_all=[]
    for batch_no, start in enumerate(range(0, len(completed), BATCH_SIZE), 1):
        batch=completed[start:start+BATCH_SIZE]
        if len(batch) < BATCH_SIZE:
            continue
        batch_name=f'batch-{batch_no:03d}-posts-{start+1:04d}-{start+len(batch):04d}'
        work=PACKAGES / batch_name
        zip_path=PACKAGES/f'{batch_name}.zip'
        # Decide whether this batch actually changed. A batch is rebuilt only
        # if one of its source files (sql/items/images) differs from what is
        # already inside the existing zip. Unchanged batches keep their current
        # zip + manifest so they are never re-uploaded or re-committed.
        existing_zip=zip_path
        rebuild=True
        if existing_zip.exists():
            try:
                with zipfile.ZipFile(existing_zip) as zf:
                    have=set(zf.namelist())
                    # collect the file set this batch would produce now
                    want=set()
                    for it in batch:
                        sid=str(it.get('source_id'))
                        if (OUT/'sql'/f'{sid}.sql').exists():
                            want.add('sql/create-batch.sql')
                        if (OUT/'rollback'/f'{sid}.sql').exists():
                            want.add('sql/rollback-batch.sql')
                        if (OUT/'items'/f'{sid}.json').exists():
                            want.add(f'items/{sid}.json')
                        # image names as the previous run would have stored them
                        ij=OUT/'items'/f'{sid}.json'
                        img_names=it.get('images') or []
                        if ij.exists():
                            try:
                                img_names=(json.loads(ij.read_text(encoding='utf-8')).get('images') or it.get('images') or [])
                            except Exception:
                                img_names=it.get('images') or []
                        for img in img_names:
                            if (OUT/'images'/Path(img).name).exists():
                                want.add(f'images/{Path(img).name}')
                    have_norm={n.replace('\\','/') for n in have}
                    # same membership means the zip already contains exactly the
                    # files this batch would produce -> skip rebuild
                    rebuild = not (want <= have_norm)
            except Exception:
                rebuild=True
        if rebuild:
            if work.exists(): shutil.rmtree(work)
            (work/'sql').mkdir(parents=True)
            (work/'images').mkdir(parents=True)
            (work/'items').mkdir(parents=True)
            create_parts=[f'-- Upload-ready SQL for {BATCH_SIZE} completed generated posts']
            rollback_parts=[f'-- Rollback SQL for this {BATCH_SIZE}-post package']
            files=[]
            posts=[]
            for item in batch:
                sid=str(item.get('source_id'))
                posts.append({'source_id':sid,'city':item.get('city'),'province':item.get('province'),'topic':item.get('topic'),'slug':item.get('slug'),'completed_at':item.get('completed_at'),'word_count':item.get('word_count')})
                for src_dir,collector in [('sql',create_parts),('rollback',rollback_parts)]:
                    src=OUT/src_dir/f'{sid}.sql'
                    if src.exists():
                        collector.append(f'\n-- {src_dir}: {sid}\n'+src.read_text(encoding='utf-8'))
                item_json=OUT/'items'/f'{sid}.json'
                if item_json.exists():
                    shutil.copy2(item_json, work/'items'/item_json.name); files.append(str(Path('items')/item_json.name))
                    try:
                        data=json.loads(item_json.read_text(encoding='utf-8'))
                        image_names=data.get('images') or item.get('images') or []
                    except Exception:
                        image_names=item.get('images') or []
                else:
                    image_names=item.get('images') or []
                for img in image_names:
                    src=OUT/'images'/Path(img).name
                    if src.exists():
                        shutil.copy2(src, work/'images'/src.name); files.append(str(Path('images')/src.name))
            (work/'sql'/'create-batch.sql').write_text('\n'.join(create_parts)+'\n', encoding='utf-8')
            (work/'sql'/'rollback-batch.sql').write_text('\n'.join(rollback_parts)+'\n', encoding='utf-8')
            files += ['sql/create-batch.sql','sql/rollback-batch.sql']
            man={'batch':batch_name,'post_count':len(batch),'posts':posts,'files':sorted(set(files))}
            (work/'manifest.json').write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding='utf-8')
            with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
                for p in sorted(work.rglob('*')):
                    if p.is_file(): z.write(p, p.relative_to(work))
            man['zip']=zip_path.name; man['zip_sha256']=sha256(zip_path); man['zip_bytes']=zip_path.stat().st_size
            manifest_all.append(man)
        else:
            # Keep the existing zip; preserve the previously recorded manifest
            # entry so STATUS.md and the upload dedup stay consistent.
            man={'batch':batch_name,'post_count':len(batch),
                 'zip':zip_path.name,'zip_sha256':sha256(zip_path),'zip_bytes':zip_path.stat().st_size}
            manifest_all.append(man)
    (PACKAGES/'manifest.json').write_text(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(manifest_all),'packages':manifest_all}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(manifest_all),'package_dir':str(PACKAGES)}, ensure_ascii=False))

if __name__=='__main__': main()
