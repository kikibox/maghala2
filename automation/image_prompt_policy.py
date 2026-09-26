#!/usr/bin/env python3
"""Topic-first image policy with a mandatory secondary AFP product object."""
DRIP_TAPE_ROLL_REFERENCE='https://navar-abyari.ir/wp-content/uploads/%D9%86%D9%88%D8%A7%D8%B1-%D8%A2%D8%A8%DB%8C%D8%A7%D8%B1%DB%8C-1.webp'
LAYFLAT_REFERENCE_PACKAGE='https://navar-abyari.ir/wp-content/uploads/%D9%84%D9%88%D9%84%D9%87-%D9%86%D8%AE%DB%8C-2-%D8%A7%DB%8C%D9%86%DA%86-1.webp'
REFERENCE_IMAGES={'drip_tape_roll':DRIP_TAPE_ROLL_REFERENCE,'layflat_package':LAYFLAT_REFERENCE_PACKAGE}


def product_family(item):
    item=item or {}; sid=str(item.get('source_id') or '').lower()
    text=' '.join(str(item.get(k) or '') for k in ('topic','topic_title','topic_focus','title','slug','source_id'))
    if sid.endswith('-layflat') or any(x in text.lower() for x in ('layflat','لوله نخی','لوله تاشو','looleh nakhi','looleh-nakhi')):
        return 'layflat'
    return 'tape20'


SCENES={
  1:'wide editorial hero in which the article topic, crop, field condition or irrigation problem is the unmistakable main subject',
  2:'practical agricultural scene showing the article-specific selection, comparison, measurement or setup activity as the main subject',
  3:'technical field scene showing the article-specific irrigation detail, crop response, installation or maintenance action as the main subject',
}


def reference_images(kind,item=None):
    """Kept for compatibility only; generation must not pass these as model references."""
    return []


def image_prompt(item,kind):
    family=product_family(item)
    topic=str((item or {}).get('title') or (item or {}).get('topic') or (item or {}).get('focus') or 'the article topic')
    if family=='layflat':
        product=(
          'Include exactly one recognizable AFP black woven yarn-reinforced layflat-hose roll in its intact package as a small secondary prop. '
          'The only printed package text permitted and required is exactly "AFP", "آبگسترفراپارسیان" and lowercase "layflat"; never print "Drip Irrigation tape" on this product. '
          'It must occupy about 10 to 20 percent of the frame, sit naturally at the side or in the midground, and never become the focal point.')
    else:
        product=(
          'Include exactly one recognizable AFP 1000-meter drip-irrigation tape roll/carton as a small secondary prop: white cylindrical body, blue lower band and central core. '
          'The only printed package text permitted and required is exactly "AFP", "آبگسترفراپارسیان" and "Drip Irrigation tape" with this exact capitalization; never print "layflat" on this product. '
          'It must occupy about 10 to 20 percent of the frame, sit naturally at the side or in the midground, and never become the focal point.')
    return (
      'Photorealistic 16:9 editorial agricultural photograph. '
      f'Article topic: {topic}. Main scene: {SCENES.get(kind,SCENES[1])}. '
      'Devote roughly 75 to 85 percent of the visual emphasis to the article topic and its real agricultural context. '
      +product+' The product is mandatory but must look like an incidental real object in the scene, not a reference image, hero product, advertisement or product-only shot. '
      'Do not use a close-up product composition, centered package, studio background, oversized package, duplicate product, floating object, collage, caption, watermark, invented specifications, extra words, numbers, phone numbers or gibberish label text. '
      'Natural daylight, believable Iranian farm environment, realistic scale, perspective, contact shadows, soil, crops and irrigation equipment.')


def install(backend):
    backend.SCENES=SCENES
    backend.REFERENCE_IMAGES={}
    backend.image_prompt=image_prompt
