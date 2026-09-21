#!/usr/bin/env python3
"""Product-family routing and reference-conditioned full-scene image policy."""
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}

def product_family(item):
    item=item or {}; sid=str(item.get('source_id') or '').lower()
    text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
    if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')):
        return 'layflat'
    return 'tape20'

TAPE_SCENES={1:'wide field-first hero with one thin flat black drip-tape roll lying naturally on bare soil beside crop rows',2:'low close product view of one thin flat black drip-tape roll resting on soil with its flat layers visible',3:'technical but natural farm photograph of one flat drip-tape roll on soil, with no other irrigation hardware',4:'one flat drip-tape roll beside a crop row with a short flat section naturally resting on the ground',5:'clean agricultural advertising photograph of one flat drip-tape roll on realistic soil with crops in the background'}
LAYFLAT_SCENES={1:'wide field-edge hero with one packaged black woven layflat hose roll resting naturally on compact agricultural soil',2:'low close product photograph of the same single packaged black woven layflat hose roll on the ground, showing its weave and straps',3:'technical product photograph of the same single packaged layflat hose roll on a farm surface, no other equipment',4:'real agricultural field photograph of the same single packaged layflat hose roll placed beside a crop row, fully grounded',5:'clean selection and maintenance photograph of the same single packaged layflat hose roll on a natural farm surface'}
COMMON=('Photorealistic full-scene product photograph, realistic scale, natural daylight, commercial agricultural photography, clean 16:9 composition. '
 'Use the supplied reference only to preserve the product identity and physical shape. Generate the entire scene as one photograph; do not paste, cut out, collage, overlay, float or composite the reference. '
 'The product must have a believable contact shadow, perspective, scale and contact with soil. No generated text, fake writing, captions or watermark.')

def reference_images(kind,item=None):
    return [LAYFLAT_REFERENCE_PACKAGE] if product_family(item)=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]

def image_prompt(item,kind):
    family=product_family(item)
    if family=='layflat':
        product=('Exactly one black woven yarn-reinforced collapsible layflat hose roll matching the supplied approved packaged reference: preserve its folded/rolled geometry, weave, width, thickness, straps and packaging. '
                 'Keep the single packaged roll intact and resting on the ground. It is not drip tape.')
        forbidden='Never show a drip-tape roll, white AFP tape cylinder, round rigid pipe, second hose, fitting, valve, filter, tool, box, person, hand or invented label.'
        scene=LAYFLAT_SCENES.get(kind,LAYFLAT_SCENES[1])
    else:
        product=('Exactly one AFP 20-centimeter thin flat black drip-irrigation tape roll matching the supplied approved reference: preserve its flat layers and roll geometry. '
                 'It lies naturally on soil and is not a round pipe or layflat hose.')
        forbidden='Never show a layflat/yarn hose, white packaged cylinder, round pipe, second irrigation product, fitting, valve, filter, tool, person, hand or invented label.'
        scene=TAPE_SCENES.get(kind,TAPE_SCENES[1])
    return COMMON+' '+product+' Scene: '+scene+'. '+forbidden

def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
