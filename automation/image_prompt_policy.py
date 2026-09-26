#!/usr/bin/env python3
"""Topic-first scenes plus exact, non-generated AFP product compositing."""
from collections import deque
from functools import lru_cache
from pathlib import Path
import base64,io
from PIL import Image,ImageFilter
ASSET_DIR=Path(__file__).with_name('assets')
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}

def product_family(item):
 item=item or {};sid=str(item.get('source_id') or '').lower();text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
 return 'layflat' if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')) else 'tape20'

SCENES={1:'wide editorial hero in which the article topic, crop, field condition or irrigation problem is the unmistakable main subject',2:'practical agricultural scene showing the article-specific selection, comparison, measurement or setup activity as the main subject',3:'technical field scene showing the article-specific irrigation detail, crop response, installation or maintenance action as the main subject'}

def reference_images(kind,item=None):return []

def image_prompt(item,kind):
 topic=str((item or {}).get('title') or (item or {}).get('topic') or (item or {}).get('focus') or 'the article topic')
 return ('Photorealistic 16:9 editorial agricultural photograph. '+f'Article topic: {topic}. Main scene: {SCENES.get(kind,SCENES[1])}. '
  'The article subject and real agricultural activity must dominate the frame. IMPORTANT: do not generate, draw or imitate any product package, irrigation roll, AFP logo, brand text, label, carton or layflat package. '
  'Leave clean naturally lit ground space in the lower-left corner for a later exact product overlay. No fake writing, product-shaped object, caption, watermark or collage. Natural daylight, believable Iranian farm environment and realistic perspective.')

def _is_background(pixel):
    r,g,b,a=pixel
    return a==0 or (r>=232 and g>=232 and b>=232 and max(r,g,b)-min(r,g,b)<=22)


@lru_cache(maxsize=2)
def _product_cutout(family):
    filename='afp-layflat.webp.b64' if family=='layflat' else 'afp-tape.webp.b64'
    blob=base64.b64decode((ASSET_DIR/filename).read_text(encoding='ascii'))
    image=Image.open(io.BytesIO(blob)).convert('RGBA');width,height=image.size;pixels=image.load()
    seen=bytearray(width*height);queue=deque()
    def add(x,y):
        idx=y*width+x
        if not seen[idx] and _is_background(pixels[x,y]):seen[idx]=1;queue.append((x,y))
    for x in range(width):add(x,0);add(x,height-1)
    for y in range(height):add(0,y);add(width-1,y)
    while queue:
        x,y=queue.popleft();r,g,b,a=pixels[x,y];pixels[x,y]=(r,g,b,0)
        if x:add(x-1,y)
        if x+1<width:add(x+1,y)
        if y:add(x,y-1)
        if y+1<height:add(x,y+1)
    alpha=image.getchannel('A');box=alpha.getbbox()
    if not box:raise RuntimeError('Exact product asset became empty after background removal')
    return image.crop(box)


def composite_product(scene,item,kind):
    """Overlay the untouched approved product asset; never redraw its shape/text."""
    canvas=scene.convert('RGBA');product=_product_cutout(product_family(item)).copy()
    target_width=max(170,int(canvas.width*0.19));target_height=max(1,round(product.height*target_width/product.width))
    product=product.resize((target_width,target_height),Image.Resampling.LANCZOS)
    margin=max(18,int(canvas.width*0.025));x=margin;y=canvas.height-product.height-max(14,int(canvas.height*0.025))
    alpha=product.getchannel('A')
    shadow_alpha=alpha.filter(ImageFilter.GaussianBlur(max(4,target_width//35))).point(lambda value:value*90//255)
    shadow=Image.new('RGBA',product.size,(0,0,0,0));shadow.putalpha(shadow_alpha)
    canvas.alpha_composite(shadow,(x+max(4,target_width//45),y+max(7,target_width//30)))
    canvas.alpha_composite(product,(x,y))
    return canvas.convert('RGB')


def install(backend):backend.SCENES=SCENES;backend.REFERENCE_IMAGES={};backend.image_prompt=image_prompt
