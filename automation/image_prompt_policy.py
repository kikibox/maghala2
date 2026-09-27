#!/usr/bin/env python3
"""Topic-first scenes with reference-conditioned 3D AFP product rerendering."""
import base64,hashlib,io,re
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

SCENES={
 1:'wide editorial hero in which the article topic, crop, field condition or irrigation problem is the unmistakable main subject',
 2:'unattended practical agricultural arrangement showing article-specific selection, comparison, measurement or setup evidence as the main subject; no person performs the activity',
 3:'empty technical field detail showing article-specific irrigation hardware, crop response, installation evidence or maintenance result as the main subject; no human action is shown',
}
ROLE_CAMERAS={
 1:['high-oblique 35mm crop-canopy view','eye-level 50mm side view across a dense crop block','elevated wide 40mm view with an asymmetric field edge','long-lens 85mm crop-layer view with no central vanishing point'],
 2:['near-overhead 55mm agronomic close view','high-oblique 70mm crop-and-soil detail','top-down technical view with no visible horizon','close lateral 85mm view across leaves, tape and wetting band'],
 3:['medium-height 50mm side view of irrigation hardware','three-quarter 65mm technical view across a header assembly','high-oblique 55mm view of manifold and adjacent crop bed','close 70mm hardware foreground with shallow crop context'],
}
ROLE_ENVIRONMENTS={
 1:['mature recognizable crop canopy filling most of the frame','asymmetric production block at the exact crop growth stage','dense crop bed beside a restrained field boundary','layered crop canopy with minimal bare soil and no vehicles'],
 2:['tight crop-leaf, soil and drip-line zone with no skyline','localized wetting band and root-zone evidence between recognizable plants','measured emitter placement among crop-specific leaves with no landscape background','crop-health detail area with irrigation evidence and no buildings'],
 3:['unattended irrigation header beside the named crop bed','filter, gauge and manifold zone at a field edge with no vehicle','flush-point and water-distribution detail beside the crop','clean pressure-control assembly with a short section of adjacent crop bed'],
}
LIGHTING=['soft blue-hour dawn light','bright overcast documentary light','warm late-afternoon side light','clean high-noon light with short realistic shadows','diffused post-cloud light with saturated crop color','backlit sunrise with restrained haze and no lens flare','cool morning light with warm soil tones']
ROLE_STORIES={
 1:['make crop identity and growth stage the visual story','make canopy density and uniform establishment the visual story','make crop vigor and field-block consistency the visual story'],
 2:['make leaf condition, tape placement and wetting evidence the visual story','make spacing and root-zone moisture evidence the visual story','make crop-specific agronomic detail the visual story'],
 3:['make filtration, pressure and connection hardware the visual story','make water-distribution control and clean system layout the visual story','make the unattended irrigation headworks the visual story'],
}
CROPS={
 'اسفناج':'spinach','عدس':'lentil','کنجد':'sesame','طالبی':'cantaloupe','اسپرس':'sainfoin',
 'کلزا':'canola (rapeseed)',
 'خیار':'cucumber','سیر':'garlic','باقلا':'fava bean','ذرت':'maize','یونجه':'alfalfa',
 'گندم':'wheat','سویا':'soybean','تره':'leek','سورگوم':'sorghum','زعفران':'saffron crocus',
 'نخود':'chickpea','شاهی':'garden cress','خربزه':'melon','ریحان':'basil','کاهو':'lettuce',
 'ملون':'melon','سبزی':'leafy vegetables','چغندر':'sugar beet','مرزه':'summer savory',
 'لپه':'yellow split-pea crop','گشنیز':'coriander','شبدر':'clover','ماش':'mung bean',
 'پاپریکا':'paprika pepper','موسیر':'Persian shallot','رزماری':'rosemary','تریتیکاله':'triticale',
 'چاودار':'rye',
}
CROP_VISUALS={
 'اسفناج':'spinach with dense low rosettes of smooth dark-green oval to arrow-shaped leaves; no flowers, pods, tall stalks or broad bean-like foliage',
 'عدس':'lentil plants as low fine-textured bushy legumes with many thin branching stems, small paired pinnate oval leaflets and small flat pods; absolutely no corn blades, sunflower heads, brassica flowers or large bean leaves',
 'کنجد':'upright sesame stems with narrow lance-shaped leaves and elongated seed capsules',
 'کلزا':'canola (rapeseed) as low bluish-green rosettes of broad lobed brassica leaves at establishment, or slender branching stems with small yellow four-petal flowers at bloom; absolutely no maize or corn blade leaves, tomato vines, cereal heads or generic tall grass',
 'طالبی':'cantaloupe vines with lobed leaves and restrained netted fruit still attached to the vine',
 'خیار':'cucumber vines with angular leaves, tendrils and small attached cucumbers',
 'سیر':'garlic rows with narrow flat blue-green leaves emerging in upright clusters',
 'باقلا':'fava bean plants with thick upright stems, broad paired leaflets and visible elongated pods',
 'ذرت':'maize with tall upright stalks and long blade leaves',
 'یونجه':'alfalfa with dense fine trifoliate leaflets and no large broad leaves',
 'گندم':'wheat with narrow leaves and mature compact grain heads',
 'سویا':'soybean with trifoliate leaves and fuzzy pods held close to branching stems',
 'زعفران':'saffron crocus with narrow grass-like leaves and sparse purple flowers',
 'نخود':'chickpea as low bushy plants with many tiny serrated leaflets and inflated pods',
 'شاهی':'garden cress as a dense low bed of small divided green leaves',
 'ریحان':'basil with opposite oval aromatic leaves on compact branching stems',
 'کاهو':'lettuce heads as low layered rosettes of broad crinkled leaves',
 'چغندر':'sugar beet with large low rosettes and thick reddish leaf stems',
 'گشنیز':'coriander with finely divided feathery leaves',
 'شبدر':'clover with unmistakable three-leaflet leaves in a dense low canopy',
 'ماش':'mung bean as compact legumes with trifoliate leaves and slender dark pods',
 'پاپریکا':'paprika pepper plants with narrow oval leaves and attached elongated red peppers',
 'موسیر':'Persian shallot with narrow strap-like leaves growing in clustered bulbs',
 'رزماری':'rosemary as woody low shrubs with many needle-like dark-green leaves',
 'چاودار':'rye with tall slender stems and long narrow grain heads',
}

def visual_brief(item,max_chars=650):
 item=item or {};parts=[]
 for key in ('title','focus','excerpt','meta_description','summary'):
  value=re.sub(r'<[^>]+>',' ',str(item.get(key) or ''))
  value=re.sub(r'\s+',' ',value).strip()
  if value and value not in parts:parts.append(value)
 brief=' | '.join(parts)
 return brief[:max_chars].rsplit(' ',1)[0] if len(brief)>max_chars else brief

def topic_visual_anchor(item):
 text=visual_brief(item).lower()
 rules=[
  (('بذر','seed'),'show article-specific seeds, a calibrated seed tray or clear row-spacing markers; the seed-rate story must be visually obvious'),
  (('آفت','بیماری','pest','disease'),'show article-specific crop leaves and non-graphic field symptoms with a clean monitoring card; no person applies treatment'),
  (('فاصله','spacing'),'show measured row and emitter spacing through visible field geometry and neutral measurement stakes'),
  (('هزینه','cost'),'show a clearly bounded production field block, irrigation header and measurable infrastructure; do not add money, text or decorative produce'),
  (('برداشت','عملکرد','yield','harvest'),'show the article-specific crop at its mature pre-harvest stage across the field; do not stage baskets or produce beside the AFP roll'),
  (('نگهداری','maintenance','گرفتگی','filter'),'show an unattended filter, pressure gauge, flush point or clean connection detail relevant to the article'),
  (('کاشت','planting'),'show the article-specific crop establishment stage, prepared rows and irrigation placement with no worker present'),
 ]
 for keys,anchor in rules:
  if any(key in text for key in keys):return anchor
 return 'derive one unmistakable visual anchor from the article title and summary; a generic empty field is not sufficient'

def named_crop(item):
 text=visual_brief(item)
 for fa,en in CROPS.items():
  if fa in text:return f'{fa} ({en})'
 return 'the exact named crop from the article title'

def crop_identity_spec(item):
 text=visual_brief(item)
 for fa,en in CROPS.items():
  if fa in text:
   return CROP_VISUALS.get(fa,f'{fa} ({en}) with botanically accurate leaves, stems, growth habit and harvest stage')
 return 'the exact named crop from the article title with botanically accurate, unmistakable morphology'

def role_directive(item,kind):
 crop=named_crop(item);identity=crop_identity_spec(item);text=visual_brief(item).lower()
 if kind==1:
  detail='show mature pre-harvest crop density and uniformity' if any(x in text for x in ('برداشت','عملکرد','yield','harvest')) else 'show the crop at the growth stage discussed by the article'
  return f'CROP-IDENTITY HERO: a high or eye-level wide editorial view of unmistakable {crop}; botanical identity: {identity}; {detail}. Do not use a low centered furrow composition. The crop species, not bare soil or the AFP roll, must dominate.'
 if kind==2:
  evidence='visible non-graphic leaf symptoms and crop-specific monitoring evidence' if any(x in text for x in ('آفت','بیماری','pest','disease')) else 'recognizable leaves or crowns, the drip line and the localized wetting band/root-zone evidence'
  if any(x in text for x in ('بذر','seed')): evidence='article-specific seeds, calibrated seed quantity and establishment spacing beside recognizable young plants'
  if any(x in text for x in ('فاصله','spacing')): evidence='clearly measured row and emitter spacing with neutral stakes and visible drip-line placement'
  return f'AGRONOMIC CLOSE EVIDENCE: an overhead or high-oblique close technical view of {crop} showing {evidence}. Botanical identity must visibly match: {identity}. No horizon, barn, tractor, landscape panorama or long symmetrical furrows. This must look categorically different from role 1.'
 return f'IRRIGATION-SYSTEM STORY: a medium side view centered on an unattended header, filter, pressure gauge, manifold or flush point and visible water-distribution evidence. The crop may be absent or visually neutral in this hardware role; if recognizable crop plants appear, they must not contradict {crop}. No open-field panorama, no centered vanishing-point furrows, no tractor and no repeated role-1 composition. The hardware narrative must be obvious while the AFP roll stays secondary.'

def role_topic_anchor(item,kind):
 text=visual_brief(item).lower();crop=named_crop(item)
 if kind==3:
  return f'show unattended filtration, pressure, manifold or flush-point evidence configured for {crop}; keep the crop as nearby context only, never as a field panorama'
 if kind==2 and any(x in text for x in ('برداشت','عملکرد','yield','harvest')):
  return f'show close evidence of {crop} canopy density, leaf quality, drip-line placement and uniform wetting as the yield story; no panorama'
 return topic_visual_anchor(item)

def visual_recipe(item,kind):
 identity='|'.join(str((item or {}).get(k) or '') for k in ('id','source_id','slug','title'))
 seed=int(hashlib.sha256((identity+'|creative-recipe-v3').encode('utf-8')).hexdigest()[:12],16);kind=max(1,min(3,int(kind)))
 cameras=ROLE_CAMERAS[kind];environments=ROLE_ENVIRONMENTS[kind];stories=ROLE_STORIES[kind]
 return {'camera':cameras[seed%len(cameras)],'environment':environments[(seed*3)%len(environments)],'lighting':LIGHTING[(seed*5+kind*3)%len(LIGHTING)],'story':stories[(seed*7)%len(stories)],'anchor':role_topic_anchor(item,kind),'token':hashlib.sha256(f'{identity}|{kind}|creative-v3'.encode('utf-8')).hexdigest()[:10]}

def visual_template(item,kind):
 r=visual_recipe(item,kind)
 return f"Mandatory role blueprint: {role_directive(item,kind)} Camera: {r['camera']}. Environment: {r['environment']}. Light: {r['lighting']}. Narrative: {r['story']}. Topic anchor: {r['anchor']}. If a generic recipe conflicts with the mandatory role blueprint, the role blueprint wins. Variation token {r['token']} is a seed only and must never be rendered."

def reference_images(kind,item=None):
 family=product_family(item)
 if family=='layflat':
  refs=[]
  for filename in ('afp-layflat.webp.b64','afp-layflat-bare.jpg.b64'):
   raw=base64.b64decode((ASSET_DIR/filename).read_text(encoding='ascii').strip())
   product=Image.open(io.BytesIO(raw)).convert('RGB')
   product.thumbnail((150,112),Image.Resampling.LANCZOS)
   canvas=Image.new('RGB',(1200,675),(238,238,235))
   canvas.paste(product,(90,675-product.height-55))
   buf=io.BytesIO();canvas.save(buf,'WEBP',quality=90,method=6)
   refs.append('data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii'))
  return refs
 raw=base64.b64decode((ASSET_DIR/'afp-tape.webp.b64').read_text(encoding='ascii').strip())
 product=Image.open(io.BytesIO(raw)).convert('RGB').resize((280,170),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(1200,675),(238,238,235));canvas.paste(product,(90,675-product.height-55))
 buf=io.BytesIO();canvas.save(buf,'WEBP',quality=90,method=6)
 return ['data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode('ascii')]

def image_prompt(item,kind):
 topic=str((item or {}).get('title') or (item or {}).get('topic') or (item or {}).get('focus') or 'the article topic')
 brief=visual_brief(item)
 summary_instruction=f'Article visual brief extracted from the post: {brief}. Every background must visibly express this brief rather than a generic farm. ' if brief else ''
 template=visual_template(item,kind)
 identity=crop_identity_spec(item)
 identity_lock=(
  f'BOTANICAL IDENTITY LOCK: prefer an unmistakable, accurate view of {identity}. Never substitute a visibly different crop species. If exact mature morphology cannot be rendered reliably, use botanically neutral prepared beds, tiny unidentifiable seedlings, irrigation evidence or soil/root-zone evidence instead of inventing a different crop. '
  if int(kind) in (1,2)
  else f'TECHNICAL ROLE CROP RULE: the hardware and water-distribution evidence are the subject. Crop plants may be absent or visually neutral; never show a clearly different identifiable crop from {named_crop(item)}. '
 )
 correction=str((item or {}).get('_image_qa_feedback') or '').strip()
 correction_instruction=f'Previous candidate was rejected by visual QA. Correct all of these issues: {correction}. ' if correction else ''
 if int(kind) in (1,2) and correction and any(term in correction.lower() for term in ('different species','crop mismatch','contradict','botanical','morphology','sunflower','tomato')):
  identity_lock=(
   f'BOTANICAL SAFE FALLBACK: the previous image invented a visibly wrong crop for {named_crop(item)}. '
   'Use a clean prepared bed with tiny botanically unidentifiable seedlings, drip-line placement and root-zone or spacing evidence. '
   'Do not render mature flowers, fruits, pods, grain heads or broad leaves that could identify another species. '
  )
 family=product_family(item)
 composition_contract={
  1:'FINAL COMPOSITION CONTRACT: use an elevated or eye-level wide crop-canopy editorial view. The crop block dominates; keep the product near a lower corner. Do not use a close low-angle product-on-furrow shot and do not make a barn the main background structure.',
  2:'FINAL COMPOSITION CONTRACT: use a near-overhead or high-oblique tight agronomic evidence view with no horizon, skyline, barn or landscape panorama. Show recognizable leaves or neutral seedlings, drip-line placement, wetting band, spacing or root-zone evidence around the product.',
  3:'FINAL COMPOSITION CONTRACT: use a medium side-view technical hardware story centered on an unattended filter, gauge, manifold, regulator or flush point. Crop all people, vehicles and horizon out of frame. Use only neutral soil or tiny unidentifiable seedlings around the hardware; do not show fruiting plants or a recognizable crop species. Do not repeat the role-1 crop panorama or the role-2 top-down detail.',
 }.get(int(kind),'')
 if family=='layflat':
  shape=('exactly two separate related layflat-hose objects placed naturally beside each other: first, the packaged low wide black woven hose coil with the same folded printed cardboard pieces, crossing straps, center opening and package proportions; second, the unboxed black woven layflat hose coil exactly like its reference, as a low flat horizontal coil made of many tight concentric layers with a short hollow brown cardboard center, visible diagonal woven fabric texture, realistic compressed thickness and one short loose hose end')
  exact=('Keep the packaged object marks "AFP" and "layflat" readable. The bare black coil has no carton, logo or writing. The two references are two separate objects in the same final scene, never alternatives and never fused into one object. Both coils must rest flat, horizontal and parallel to the soil. Never turn the bare coil into smooth round tubing, a tall cable spool, an upright wheel, a solid tire or a plastic pipe coil.')
  scale=('Use the approved 05-pair-far scale: the complete two-object group occupies approximately 12 to 15 percent of frame width, stays low on the soil and appears about four metres from the camera. Keep the pair off-center on the lower third.')
  people_rule=('NO PEOPLE in any image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette or distant human figure. Do not show a tractor, harvester, vehicle cabin, hand-held tool or human-associated activity unless machinery is essential to the article itself; default to an empty equipment-free scene. Show the article-specific field, crop, irrigation system and unattended equipment without any human presence.')
 else:
  shape='a wide low cylindrical 1000-meter drip-tape roll in the same white-and-blue carton sleeve; its visible diameter must be 1.6 to 1.8 times its visible height, with a central top hole, straight carton walls and blue lower band'
  exact=('Show exactly one commercial product object in the entire image: this AFP drip-tape carton roll. Keep the exact readable marks "AFP" and "Drip Irrigation Tape"; never change it into layflat hose. Absolutely no bottle, jar, canister, bucket, fertilizer container, pesticide container, second package, second roll, decorative produce, harvest basket or invented companion product anywhere in the frame.')
  scale=('Use the balanced scale-conditioned reference: the product occupies approximately 20 to 23 percent of frame width, stays low in real-world scale and remains off-center on the lower third.')
  people_rule=('NO PEOPLE in any drip-tape image: no farmer, worker, person, face, hand, arm, leg, body part, human silhouette or distant human figure. Do not show a tractor, harvester, vehicle cabin, hand-held tool or human-associated activity unless machinery is essential to the article itself; default to an empty equipment-free scene. Show the article-specific field, crop, irrigation system and unattended equipment without any human presence.')
 return ('Create one photorealistic 16:9 agricultural editorial photograph. The attached image is an identity and geometry reference, not a flat layer to paste. '
  +f'Article topic: {topic}. {summary_instruction}{correction_instruction}{identity_lock}Main scene: {SCENES.get(kind,SCENES[1])}. Selected visual template: {template}. This recipe is one member of a deterministic creative set. Follow every camera, environment, light, narrative and topic-anchor instruction. The three sibling images must look like different editorial assignments, not alternate crops of one scene. The background, physical evidence and equipment must be specifically derived from the article topic and summary and remain the main subject. The farm must look temporarily empty before photography; nobody is performing any task. {people_rule} Reconstruct the product as a true three-dimensional object: {shape}. '
  'Show it from a slightly different but physically plausible three-quarter angle, about 10 to 20 degrees from the reference. Preserve the silhouette, packaging construction, proportions, material, printed-panel layout and brand colors. '
  +exact+' '+scale+' Enforce believable real-world scale. A drip-tape carton roll is roughly 40 to 55 cm across and 20 to 30 cm high; each layflat coil is roughly 45 to 65 cm across and 15 to 25 cm high. People must not appear. Every roll must remain clearly below knee height as implied by normal real-world scale and must never look waist-high, table-sized or large enough for a person to lean on. '
  +composition_contract+' The article subject is the hero and the product is a secondary prop. Do not add any extra package, roll, bottle, jar, canister, bucket, container, advertisement or invented product. Reject forced-perspective enlargement, giant packaging and any crop that cuts through the product. Match scene perspective, depth of field, color cast, contact shadow, reflected light and slight soil interaction. '
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
