#!/usr/bin/env python3
"""Topic-aware image policy with one approved reference per product."""
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}
TAPE_SCENES={1:'wide field-first hero with one black flat drip-tape roll lying naturally on bare soil beside crop rows',2:'close product view of one black flat drip-tape roll, slightly unwrapped on soil, showing flat layers and real emitter spacing',3:'technical product-only view of one drip-tape roll and its flat tape edge on farm soil, with no other irrigation hardware',4:'one drip-tape roll beside a crop row with a short flat section unwrapped on the soil, no pipe or tool crossing it',5:'clean advertising view of one drip-tape roll on realistic agricultural soil with crop rows in the background'}
LAYFLAT_SCENE='the exact single packaged black woven yarn-reinforced collapsible layflat hose roll from the approved product reference, fully visible as one packaged product on a simple neutral agricultural surface'
COMMON_RULES=('Photorealistic product photograph, realistic scale, natural daylight, clean 16:9 composition. '
 'Respect the reference product dimensions, proportions, wall thickness, texture, coil diameter, packaging straps and physical material. '
 'No invented text, letters, digits, labels, captions, signs, logos, brands or generated watermarks; the pipeline adds the approved watermark afterward. '
 'Do not distort, merge, duplicate, float or clip the product.')
TAPE_RULES=('The product is thin, flat black 20-centimeter drip tape, not a round pipe, cable, garden hose or layflat hose. '
 'The roll must lie naturally on soil, never stand upright like a wheel, and must never contain, surround, wrap around, or be pierced by another object.')
LAYFLAT_RULES=('MANDATORY SINGLE-REFERENCE RULE: use only the one approved packaged layflat-hose reference image. '
 'For every layflat image role, show only that same type of single packaged black woven yarn-reinforced collapsible hose roll; do not unwrap it, install it, show it being held, or invent a second scene. '
 'Do not use the removed hand-held/installed reference. Do not show any second hose, round pipe, drip tape, irrigation line, cable, fitting, valve, filter, coupler, box, tool, hand, person or other product. '
 'Nothing may cross, pass through, enter, wrap around, touch, intersect, merge with or be hidden inside the packaged roll. '
 'Preserve the package size, coil proportions, weave, straps and any genuine product marking visible in the approved reference; never hallucinate writing.')

def reference_images(kind,item=None):
    topic=(item or {}).get('topic') if isinstance(item,dict) else None
    return [LAYFLAT_REFERENCE_PACKAGE] if topic=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]

def image_prompt(item,kind):
    topic=item.get('topic','tape20') if isinstance(item,dict) else 'tape20'
    if topic=='layflat':
        return COMMON_RULES+' '+LAYFLAT_RULES+' Scene: '+LAYFLAT_SCENE+'. Only the single packaged hose roll, its real packaging/straps and a simple natural background may appear.'
    scene=TAPE_SCENES.get(kind,TAPE_SCENES[1])
    return COMMON_RULES+' '+TAPE_RULES+' Scene: '+scene+'. Use only the drip-tape product, soil and crop-field background; no other irrigation product.'

def install(backend):
    backend.SCENES={**TAPE_SCENES,**{1:LAYFLAT_SCENE,2:LAYFLAT_SCENE,3:LAYFLAT_SCENE,4:LAYFLAT_SCENE,5:LAYFLAT_SCENE}}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
