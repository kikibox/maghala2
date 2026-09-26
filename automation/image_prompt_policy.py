#!/usr/bin/env python3
"""Topic-first scenes with reference-conditioned 3D AFP product rerendering."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ASSET_DIR=Path(__file__).with_name('assets')
PHONE_LABEL='AFP | 09134922013'
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}

def product_family(item):
 item=item or {};sid=str(item.get('source_id') or '').lower();text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
 return 'layflat' if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')) else 'tape20'

SCENES={1:'wide editorial hero in which the article topic, crop, field condition or irrigation problem is the unmistakable main subject',2:'practical agricultural scene showing the article-specific selection, comparison, measurement or setup activity as the main subject',3:'technical field scene showing the article-specific irrigation detail, crop response, installation or maintenance action as the main subject'}

def reference_images(kind,item=None):
 family=product_family(item)
 if family=='layflat':
  return [
   'data:image/webp;base64,'+(ASSET_DIR/'afp-layflat.webp.b64').read_text(encoding='ascii').strip(),
   'data:image/jpeg;base64,'+(ASSET_DIR/'afp-layflat-bare.jpg.b64').read_text(encoding='ascii').strip(),
  ]
 return ['data:image/webp;base64,'+(ASSET_DIR/'afp-tape.webp.b64').read_text(encoding='ascii').strip()]

def image_prompt(item,kind):
 topic=str((item or {}).get('title') or (item or {}).get('topic') or (item or {}).get('focus') or 'the article topic')
 family=product_family(item)
 if family=='layflat':
  shape=('exactly two related layflat-hose objects placed naturally beside each other: first, the packaged low wide black woven hose coil with the same folded printed cardboard pieces, crossing straps, center opening and package proportions; second, the unboxed black woven hose coil with flat concentric layers, short hollow cardboard center, diagonal surface texture and small loose hose end')
  exact=('Keep the packaged object marks "AFP" and "layflat" readable. The bare black coil has no carton, logo or writing. The two references are two separate objects in the same final scene, never alternatives and never fused into one object. Both coils must rest flat and horizontally, parallel to the soil; never stand either roll upright like a wheel.')
 else:
  shape='a wide cylindrical 1000-meter drip-tape roll in the same white-and-blue carton sleeve, with the same diameter-to-height ratio, central top hole, straight carton walls and blue lower band'
  exact='Keep the exact readable marks "AFP" and "Drip Irrigation Tape"; never change it into layflat hose.'
 return ('Create one photorealistic 16:9 agricultural editorial photograph. The attached image is an identity and geometry reference, not a flat layer to paste. '
  +f'Article topic: {topic}. Main scene: {SCENES.get(kind,SCENES[1])}. Reconstruct the product as a true three-dimensional object: {shape}. '
  'Show it from a slightly different but physically plausible three-quarter angle, about 10 to 20 degrees from the reference. Preserve the silhouette, packaging construction, proportions, material, printed-panel layout and brand colors. '
  +exact+' The agricultural activity and article subject must dominate at least 85 percent of the frame. The product is one small secondary object, off-center on the lower third, no more than 10 to 14 percent of frame width. '
  'Use a wide environmental composition; never make the product the hero or foreground focal point. Match scene perspective, depth of field, color cast, contact shadow, reflected light and slight soil interaction. '
  'Absolutely no sticker look, hard cut-out edge, white halo, flat front-facing packshot, collage, floating or duplicate product, caption, added logo or invented writing. Natural daylight and believable Iranian farm environment.')

def add_phone_watermark(image):
 canvas=image.convert('RGBA');overlay=Image.new('RGBA',canvas.size,(0,0,0,0));draw=ImageDraw.Draw(overlay)
 try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',27)
 except OSError:font=ImageFont.load_default()
 box=draw.textbbox((0,0),PHONE_LABEL,font=font);w,h=box[2]-box[0],box[3]-box[1];margin,padx,pady=18,16,10
 x=canvas.width-w-margin-2*padx;y=canvas.height-h-margin-2*pady
 draw.rounded_rectangle((x,y,canvas.width-margin,canvas.height-margin),radius=8,fill=(0,0,0,178))
 draw.text((x+padx,y+pady-box[1]),PHONE_LABEL,font=font,fill='white')
 return Image.alpha_composite(canvas,overlay).convert('RGB')

def install(backend):backend.SCENES=SCENES;backend.REFERENCE_IMAGES=REFERENCE_IMAGES;backend.image_prompt=image_prompt
