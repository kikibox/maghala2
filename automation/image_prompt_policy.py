#!/usr/bin/env python3
"""Topic-first scenes with reference-conditioned 3D AFP product rerendering."""
import base64,hashlib,io
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
VISUAL_TEMPLATES=[
 'wide environmental view with long crop-row leading lines, a low horizon and the product on a lower corner',
 'high-oblique technical view emphasizing bed geometry, irrigation spacing and a small off-center product',
 'ground-level side view across the crop canopy with shallow depth of field and the product in the lower opposite third',
 'wide irrigation-infrastructure view featuring an unattended pump, filter or manifold in the middle distance',
 'orchard-edge composition with diagonal tree rows, textured soil and generous negative space',
 'greenhouse-edge composition with cultivated beds visible through the structure and no staged activity',
 'clean overhead-leaning field-detail composition showing tape placement, wetting pattern or soil texture',
 'mature-crop landscape with layered foreground, midground and distant hills under soft daylight',
 'recently prepared seedbed with parallel furrows, restrained equipment in the distance and asymmetric framing',
]

def visual_template(item,kind):
 identity='|'.join(str((item or {}).get(k) or '') for k in ('id','source_id','slug','title'))
 seed=int(hashlib.sha256(identity.encode('utf-8')).hexdigest()[:10],16)
 return VISUAL_TEMPLATES[(seed+(int(kind)-1)*5)%len(VISUAL_TEMPLATES)]

def reference_images(kind,item=None):
 family=product_family(item)
 if family=='layflat':
  return [
   'data:image/webp;base64,'+(ASSET_DIR/'afp-layflat.webp.b64').read_text(encoding='ascii').strip(),
   'data:image/jpeg;base64,'+(ASSET_DIR/'afp-layflat-bare.jpg.b64').read_text(encoding='ascii').strip(),
  ]
 raw=base64.b64decode((ASSET_DIR/'afp-tape.webp.b64').read_text(encoding='ascii').strip())
 product=Image.open(io.BytesIO(raw)).convert('RGB').resize((280,170),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(1200,675),(238,238,235));canvas.paste(product,(90,675-product.height-55))
 buf=io.BytesIO();canvas.save(buf,'WEBP',quality=90,method=6)
 return ['data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')]

def image_prompt(item,kind):
 topic=str((item or {}).get('title') or (item or {}).get('topic') or (item or {}).get('focus') or 'the article topic')
 summary=str((item or {}).get('excerpt') or (item or {}).get('meta_description') or (item or {}).get('summary') or '').strip()
 summary_instruction=f'Article summary for visual grounding: {summary}. ' if summary else ''
 template=visual_template(item,kind)
 correction=str((item or {}).get('_image_qa_feedback') or '').strip()
 correction_instruction=f'Previous candidate was rejected by visual QA. Correct all of these issues: {correction}. ' if correction else ''
 family=product_family(item)
 if family=='layflat':
  shape=('exactly two separate related layflat-hose objects placed naturally beside each other: first, the packaged low wide black woven hose coil with the same folded printed cardboard pieces, crossing straps, center opening and package proportions; second, the unboxed black woven layflat hose coil exactly like its reference, as a low flat horizontal coil made of many tight concentric layers with a short hollow brown cardboard center, visible diagonal woven fabric texture, realistic compressed thickness and one short loose hose end')
  exact=('Keep the packaged object marks "AFP" and "layflat" readable. The bare black coil has no carton, logo or writing. The two references are two separate objects in the same final scene, never alternatives and never fused into one object. Both coils must rest flat, horizontal and parallel to the soil. Never turn the bare coil into smooth round tubing, a tall cable spool, an upright wheel, a solid tire or a plastic pipe coil.')
  scale=('Use the approved 05-pair-far scale: the complete two-object group occupies approximately 12 to 15 percent of frame width, stays low on the soil and appears about four metres from the camera. Keep the pair off-center on the lower third.')
  people_rule=('NO PEOPLE in any image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette or distant human figure. Show the article-specific field, crop, irrigation system and unattended equipment without any human presence.')
 else:
  shape='a wide low cylindrical 1000-meter drip-tape roll in the same white-and-blue carton sleeve; its visible diameter must be 1.6 to 1.8 times its visible height, with a central top hole, straight carton walls and blue lower band'
  exact=('Show exactly one commercial product object in the entire image: this AFP drip-tape carton roll. Keep the exact readable marks "AFP" and "Drip Irrigation Tape"; never change it into layflat hose. Absolutely no bottle, jar, canister, bucket, fertilizer container, pesticide container, second package, second roll or invented companion product anywhere in the frame.')
  scale=('Use the balanced scale-conditioned reference: the product occupies approximately 19 to 22 percent of frame width, stays low in real-world scale and remains off-center on the lower third.')
  people_rule=('NO PEOPLE in any drip-tape image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette or distant human figure. Show the article-specific field, crop, irrigation system and unattended equipment without any human presence.')
 return ('Create one photorealistic 16:9 agricultural editorial photograph. The attached image is an identity and geometry reference, not a flat layer to paste. '
  +f'Article topic: {topic}. {summary_instruction}{correction_instruction}Main scene: {SCENES.get(kind,SCENES[1])}. Selected visual template: {template}. The template is chosen from a deterministic shuffled pool; follow its camera, background and composition rather than repeating a standard field shot. The background, activity and equipment must be specifically derived from the article topic and summary and remain the main subject. {people_rule} Reconstruct the product as a true three-dimensional object: {shape}. '
  'Show it from a slightly different but physically plausible three-quarter angle, about 10 to 20 degrees from the reference. Preserve the silhouette, packaging construction, proportions, material, printed-panel layout and brand colors. '
  +exact+' '+scale+' Enforce believable real-world scale. A drip-tape carton roll is roughly 40 to 55 cm across and 20 to 30 cm high; each layflat coil is roughly 45 to 65 cm across and 15 to 25 cm high. If people appear, every roll must remain clearly below knee height and must never look waist-high, table-sized or large enough for a person to lean on. '
  'Use a wide environmental composition with substantial context around the products; the article subject is the hero and the product is a secondary prop. Do not add any extra package, roll, bottle, jar, canister, bucket, container, advertisement or invented product. Reject forced-perspective enlargement, giant packaging and any crop that cuts through the product. Match scene perspective, depth of field, color cast, contact shadow, reflected light and slight soil interaction. '
  'Absolutely no sticker look, hard cut-out edge, white halo, flat front-facing packshot, collage, floating or duplicate product, caption, headline, added logo or invented writing anywhere outside the authentic package print and required phone watermark. Natural daylight and believable Iranian farm environment.')

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
