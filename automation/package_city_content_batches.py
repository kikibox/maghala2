#!/usr/bin/env python3
"""Create upload-ready ZIP packages for every 5 completed city-content posts.

Each package contains:
- sql/create-batch.sql
- sql/rollback-batch.sql
- images/* for those posts
- items/*.json metadata
- manifest.json
"""
import json, shutil, zipfile, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts' / 'city-content-queue'
PACKAGES = OUT / 'packages'
BATCH_SIZE = 5

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
    manifest_all=[]
    for batch_no, start in enumerate(range(0, len(completed), BATCH_SIZE), 1):
        batch=completed[start:start+BATCH_SIZE]
        if len(batch) < BATCH_SIZE:
            continue
        batch_name=f'batch-{batch_no:03d}-posts-{start+1:04d}-{start+len(batch):04d}'
        work=PACKAGES / batch_name
        if work.exists(): shutil.rmtree(work)
        (work/'sql').mkdir(parents=True)
        (work/'images').mkdir(parents=True)
        (work/'items').mkdir(parents=True)
        create_parts=['-- Upload-ready SQL for 5 completed generated posts']
        rollback_parts=['-- Rollback SQL for this 5-post package']
        files=[]
        posts=[]
        for item in batch:
            sid=str(item.get('source_id'))
            posts.append({'source_id':sid,'city':item.get('city'),'province':item.get('province'),'topic':item.get('topic'),'slug':item.get('slug'),'completed_at':item.get('completed_at'),'word_count':item.get('word_count')})
            for src_dir,dst_dir,collector in [('sql','sql',create_parts),('rollback','sql',rollback_parts)]:
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
        zip_path=PACKAGES/f'{batch_name}.zip'
        if zip_path.exists(): zip_path.unlink()
        with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(work.rglob('*')):
                if p.is_file(): z.write(p, p.relative_to(work))
        man['zip']=zip_path.name; man['zip_sha256']=sha256(zip_path); man['zip_bytes']=zip_path.stat().st_size
        manifest_all.append(man)
    (PACKAGES/'manifest.json').write_text(json.dumps({'batch_size':BATCH_SIZE,'ready_batches':len(manifest_all),'packages':manifest_all}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ready_batches':len(manifest_all),'package_dir':str(PACKAGES)}, ensure_ascii=False))

if __name__=='__main__': main()
