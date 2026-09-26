#!/usr/bin/env python3
"""Convert and rename article images to SEO-friendly WebP quality 60."""
from __future__ import annotations
import hashlib,json,re
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'article-content-queue';IMAGES=OUT/'images';ITEMS=OUT/'items'
QUALITY=60
TEXT_SUFFIXES={'.json','.sql','.md','.txt','.csv','.html','.xml'}
ROLE_SLUGS={1:'تصویر-شاخص',2:'کاربرد-عملی',3:'جزئیات-فنی'}


def slugify(value)->str:
    slug=re.sub(r'[^0-9A-Za-z\u0600-\u06FF-]+','-',str(value or '').lower())
    return (re.sub(r'-{2,}','-',slug).strip('-')[:140].strip('-') or 'article')


def seo_name(item,index:int)->str:
    base=slugify(item.get('slug') or item.get('focus') or item.get('title') or item.get('id'))
    return f"{base}-{ROLE_SLUGS.get(index,f'تصویر-{index}')}.webp"


def encode(source:Path)->bytes:
    with Image.open(source) as opened:
        image=opened.convert('RGB');buf=BytesIO()
        image.save(buf,'WEBP',quality=QUALITY,method=6)
        return buf.getvalue()


def main()->int:
    item_docs={};plans={}
    if ITEMS.exists():
        for path in sorted(ITEMS.glob('*.json')):
            try:data=json.loads(path.read_text(encoding='utf-8'))
            except Exception:continue
            item_docs[path]=data
            for index,record in enumerate(data.get('images',[]),1):
                if isinstance(record,dict) and record.get('name'):
                    plans[record['name']]=seo_name(data,index)
    # Convert and SEO-rename every planned image; also convert orphan legacy images.
    if IMAGES.exists():
        for source in sorted(IMAGES.iterdir()):
            if not source.is_file() or source.suffix.lower() not in {'.jpg','.jpeg','.png','.webp'}:continue
            plans.setdefault(source.name,source.with_suffix('.webp').name)
    mapping={};metadata={};before=after=converted=renamed=0
    for old,target_name in sorted(plans.items()):
        source=IMAGES/old
        if not source.exists():continue
        target=IMAGES/target_name
        needs_encode=source.suffix.lower()!='.webp'
        blob=encode(source) if needs_encode else source.read_bytes()
        before+=source.stat().st_size;after+=len(blob);converted+=int(needs_encode);renamed+=int(old!=target_name)
        if source!=target:target.write_bytes(blob);source.unlink()
        mapping[old]=target_name
        metadata[old]={'name':target_name,'sha256':hashlib.sha256(blob).hexdigest(),'mime':'image/webp','width':1200,'height':675}
    rewritten=0
    for path,data in item_docs.items():
        changed=False;hashes=[]
        for record in data.get('images',[]):
            if not isinstance(record,dict):continue
            old=record.get('name')
            if old in metadata:record.update(metadata[old]);changed=True
            if record.get('sha256'):hashes.append(record['sha256'])
        if changed:
            data['image_sha256']=hashes
            text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
            for old,new in mapping.items():text=text.replace(old,new)
            path.write_text(text,encoding='utf-8');rewritten+=1
    for path in OUT.rglob('*') if OUT.exists() else []:
        if path in item_docs or not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:continue
        try:text=path.read_text(encoding='utf-8')
        except UnicodeDecodeError:continue
        updated=text
        for old,new in mapping.items():updated=updated.replace(old,new)
        if mapping:updated=updated.replace("'image/jpeg'","'image/webp'").replace('"mime": "image/jpeg"','"mime": "image/webp"')
        if updated!=text:path.write_text(updated,encoding='utf-8');rewritten+=1
    report={'quality':QUALITY,'converted_images':converted,'seo_renamed_images':renamed,'source_bytes':before,'webp_bytes':after,'saved_percent':round((1-after/before)*100,2) if before else 0,'reference_files_rewritten':rewritten}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'image-compression-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False));return 0


if __name__=='__main__':raise SystemExit(main())
