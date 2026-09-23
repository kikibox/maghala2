#!/usr/bin/env python3
"""Product-family routing and locked original-packaging image policy."""
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}

def product_family(item):
    item=item or {}; sid=str(item.get('source_id') or '').lower()
    text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
    if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')):
        return 'layflat'
    return 'tape20'

TAPE_SCENES={
  1:'wide field-first hero with exactly one intact white AFP cylindrical product carton resting naturally on bare soil beside crop rows',
  2:'low close product view of exactly one intact white AFP cylindrical product carton on the soil, with its blue band, central core and printed label panels visible',
  3:'technical but natural farm photograph of exactly one intact AFP drip-irrigation tape carton on soil, showing the original packaging rather than loose tape',
  4:'one intact AFP product carton beside a crop row, fully grounded on the soil with no exposed or unboxed tape',
  5:'clean agricultural advertising photograph of one intact original AFP drip-irrigation tape carton on realistic soil with crops in the background'
}
LAYFLAT_SCENES={
  1:'wide field-edge hero with exactly one intact original packaged black woven yarn-reinforced layflat hose roll resting naturally on compact agricultural soil',
  2:'low close product photograph of the same single intact packaged black woven layflat hose roll on the ground, showing its original wrap, weave and straps',
  3:'technical product photograph of the same single intact packaged layflat hose roll on a farm surface, with its original packaging preserved and no loose hose',
  4:'real agricultural field photograph of the same single intact packaged layflat hose roll placed beside a crop row, fully grounded and unopened',
  5:'clean selection and maintenance photograph of one intact original packaged layflat hose roll on a natural farm surface'
}
COMMON=(
 'Photorealistic full-scene product photograph, realistic scale, natural daylight, commercial agricultural photography, clean 16:9 composition. '
 'Use the supplied approved reference as a locked product-and-packaging identity reference, not as inspiration. Preserve the exact original packaging silhouette, printed label layout, logo placement, blue/white/black colors, straps, folds, central core and proportions. '
 'The product must remain intact, boxed or in its original retail packaging, resting on real soil with a believable contact shadow, perspective and scale. Never show the product loose, unboxed, unpacked, cut open, exposed, floating, cropped or composited. '
 'Do not invent, translate, redraw or hallucinate labels, numbers, specifications, phone numbers or logos. Use only the family-specific approved wording stated below. Keep all other label panels clean and aligned with the reference; no gibberish text, captions or watermark.')

def reference_images(kind,item=None):
    return [LAYFLAT_REFERENCE_PACKAGE] if product_family(item)=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]

def image_prompt(item,kind):
    family=product_family(item)
    if family=='layflat':
        product=(
          'Exactly one black woven yarn-reinforced collapsible layflat hose roll matching the supplied approved packaged reference. '
          'Keep its original cardboard/wrap packaging, folded geometry, weave, width, thickness, straps and visible label layout intact. '
          'The brand text must be exactly "AFP" and "آبگسترفراپارسیان". If a family marking is visible, it must read exactly lowercase "layflat"; never place "DRIP Irrigation tape" on this product. '
          'It must stay packaged and closed on the ground; it is not drip tape.')
        forbidden=('Never show a loose or unboxed hose, a drip-tape roll, a white AFP tape carton, a round rigid pipe, a second hose, '
                   'fitting, valve, filter, tool, person, hand, invented label or replacement packaging.')
        scene=LAYFLAT_SCENES.get(kind,LAYFLAT_SCENES[1])
    else:
        product=(
          'Exactly one original AFP 20-centimeter drip-irrigation tape product carton matching the supplied approved reference: a white cylindrical carton with the AFP logo, blue lower band, central cardboard core and side label panels. The front must show exactly these approved strings: "AFP", "آبگسترفراپارسیان" and "DRIP Irrigation tape". Preserve their spelling, capitalization and layout without inventing, translating or replacing the text. '
          'The tape itself must remain inside the carton; do not expose a loose black roll.')
        forbidden=('Never show a loose or unboxed black tape roll, a bare flat tape coil, a layflat/yarn hose, a round pipe, a second irrigation product, '
                   'fitting, valve, filter, tool, person, hand, invented label, fake text or a different carton.')
        scene=TAPE_SCENES.get(kind,TAPE_SCENES[1])
    return COMMON+' '+product+' Scene: '+scene+'. '+forbidden

def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
