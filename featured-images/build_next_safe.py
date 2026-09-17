#!/usr/bin/env python3
from PIL import Image, ImageDraw
import build_next as job

def safe_source_image(source_id,title):
    try:
        return original(source_id,title)
    except Exception as exc:
        print(f'Warning: source image unavailable for {source_id}: {exc}; using deterministic agricultural fallback.')
        im=Image.new('RGB',(1200,675),(32,82,51)); d=ImageDraw.Draw(im)
        for y in range(675):
            t=y/674; d.line((0,y,1200,y),fill=(int(35+105*t),int(88+72*t),int(58+18*t)))
        for x in range(-200,1400,72): d.line((600,300,x,675),fill=(207,180,82),width=5)
        for x in range(60,1180,82):
            d.line((x,245,x+8,535),fill=(92,120,48),width=6)
            d.ellipse((x-5,230,x+22,275),fill=(195,168,66))
        return im,f'procedural:{title}',0

original=job.source_image
job.source_image=safe_source_image
job.main()
