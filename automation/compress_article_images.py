#!/usr/bin/env python3
"""Convert legacy article queue images to optimized WebP quality 60."""
from __future__ import annotations
import hashlib,json
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'article-content-queue'
IMAGES=OUT/'images'
QUALITY=60
TEXT_SUFFIXES={'.json','.sql','.md','.txt','.csv','.html','.xml'}


def encode(source:Path)->bytes:
    with Image.open(source) as opened:
        image=opened.convert('RGB');buf=BytesIO()
        image.save(buf,'WEBP',quality=QUALITY,method=6)
        return buf.getvalue()


def main()->int:
    sources=sorted(p for p in IMAGES.glob('*') if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png'}) if IMAGES.exists() else []
    mapping={};metadata={};before=after=0
    for source in sources:
        blob=encode(source);target=source.with_suffix('.webp')
        target.write_bytes(blob);before+=source.stat().st_size;after+=len(blob)
        mapping[source.name]=target.name
        metadata[source.name]={'name':target.name,'sha256':hashlib.sha256(blob).hexdigest(),'mime':'image/webp','width':1200,'height':675}
        source.unlink()
    rewritten=0
    for path in OUT.rglob('*') if OUT.exists() else []:
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:continue
        if path.parent==OUT/'items' and path.suffix.lower()=='.json':
            try:data=json.loads(path.read_text(encoding='utf-8'))
            except Exception:data=None
            if isinstance(data,dict):
                changed=False;new_hashes=[]
                for record in data.get('images',[]):
                    if not isinstance(record,dict):continue
                    old=record.get('name')
                    if old in metadata:record.update(metadata[old]);changed=True
                    if record.get('sha256'):new_hashes.append(record['sha256'])
                if changed:
                    data['image_sha256']=new_hashes
                    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
                    for old,new in mapping.items():text=text.replace(old,new)
                    path.write_text(text,encoding='utf-8');rewritten+=1;continue
        try:text=path.read_text(encoding='utf-8')
        except UnicodeDecodeError:continue
        updated=text
        for old,new in mapping.items():updated=updated.replace(old,new)
        if mapping:updated=updated.replace("'image/jpeg'","'image/webp'").replace('"mime": "image/jpeg"','"mime": "image/webp"')
        if updated!=text:path.write_text(updated,encoding='utf-8');rewritten+=1
    report={'quality':QUALITY,'converted_images':len(sources),'source_bytes':before,'webp_bytes':after,'saved_percent':round((1-after/before)*100,2) if before else 0,'reference_files_rewritten':rewritten}
    (OUT/'image-compression-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    return 0


if __name__=='__main__':raise SystemExit(main())
