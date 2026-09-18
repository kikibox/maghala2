#!/usr/bin/env python3
"""Topic-aware image policy for product-accurate agricultural advertising."""
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_ROLL='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
LAYFLAT_REFERENCE_INSTALLED='https://navar-abyari.ir/wp-content/uploads/Gemini_Generated_Image_305tna305tna305t.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_roll':LAYFLAT_REFERENCE_ROLL,'layflat_installed':LAYFLAT_REFERENCE_INSTALLED}
TAPE_SCENES={
 1:'wide field-first hero with one black flat drip-tape roll lying naturally on bare soil beside crop rows',
 2:'close product view of one black flat drip-tape roll, slightly unwrapped on soil, showing flat layers and real emitter spacing',
 3:'technical product-only view of one drip-tape roll and its flat tape edge on farm soil, with no other irrigation hardware',
 4:'one drip-tape roll beside a crop row with a short flat section unwrapped on the soil, no pipe or tool crossing it',
 5:'clean advertising view of one drip-tape roll on realistic agricultural soil with crop rows in the background'
}
LAYFLAT_SCENES={
 1:'hero advertising photograph of exactly one black woven yarn-reinforced collapsible layflat hose roll resting naturally on bare farm soil',
 2:'close product photograph of exactly the same single black woven yarn-reinforced layflat hose roll, with its flattened wall, weave and coil clearly visible',
 3:'technical product photograph of exactly one continuous yarn-reinforced layflat hose on the ground, showing realistic wall thickness and scale',
 4:'single-product side view of exactly one yarn-reinforced layflat hose partly unrolled on soil, with a physically continuous body and natural gravity',
 5:'wide agricultural advertising photograph with exactly one yarn-reinforced layflat hose as the only product, resting on soil with a farm field behind it'
}
COMMON_RULES=('Photorealistic documentary agricultural advertising photograph in Iran, realistic scale, natural daylight, clean 16:9 composition. '
 'Respect the reference product dimensions, proportions, wall thickness, texture, coil diameter and physical material. '
 'No invented text, letters, digits, labels, captions, signs, logos, brands or generated watermarks; the pipeline adds the approved watermark afterward. '
 'Do not distort, merge, duplicate, float or clip the product.')
TAPE_RULES=('The product is thin, flat black 20-centimeter drip tape, not a round pipe, cable, garden hose or layflat hose. '
 'The roll must lie naturally on soil, never stand upright like a wheel, and must never contain, surround, wrap around, or be pierced by another object.')
LAYFLAT_RULES=('MANDATORY SINGLE-PRODUCT RULE: show exactly one yarn-reinforced black collapsible layflat hose, matching the approved لوله-نخی-2-اینچ-1 reference. '
 'Do not show any second hose, round pipe, drip tape, irrigation line, cable, fitting, valve, filter, coupler, box, package, tool, hand, person or other product. '
 'Nothing may cross, pass through, enter, wrap around, touch, intersect, merge with or be hidden inside the hose or its coil. '
 'The hose must be a physically continuous object resting on the ground with credible gravity, perspective, thickness and dimensions. '
 'If the reference contains genuine product markings, preserve their position and proportions only; never invent or hallucinate writing.')

def reference_images(kind,item=None):
    topic=(item or {}).get('topic') if isinstance(item,dict) else None
    return [LAYFLAT_REFERENCE_ROLL,LAYFLAT_REFERENCE_INSTALLED] if topic=='layflat' else [DRIP_TAPE_ROLL_REFERENCE]

def image_prompt(item,kind):
    topic=item.get('topic','tape20') if isinstance(item,dict) else 'tape20'
    if topic=='layflat':
        scene=LAYFLAT_SCENES.get(kind,LAYFLAT_SCENES[1])
        return COMMON_RULES+' '+LAYFLAT_RULES+' Scene: '+scene+'. Only bare soil, crop rows and distant natural field background may appear besides the single hose.'
    scene=TAPE_SCENES.get(kind,TAPE_SCENES[1])
    return COMMON_RULES+' '+TAPE_RULES+' Scene: '+scene+'. Use only the drip-tape product, soil and crop-field background; no other irrigation product.'

def install(backend):
    backend.SCENES={**TAPE_SCENES,**LAYFLAT_SCENES}
    backend.REFERENCE_IMAGES=REFERENCE_IMAGES
    backend.image_prompt=image_prompt
