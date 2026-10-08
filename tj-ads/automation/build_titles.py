#!/usr/bin/env python3
"""Build the deterministic list of ad titles (stage 1) from config/*.json.

Output: data/titles.json (+ data/titles.csv). Re-running gives the same result.
Rules: unique (place, product, template, crop); no repeated title; crops only from
config/crops.json that have a source for the place zone; no prices/claims in titles.
"""
import csv, json, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'config'
DATA = ROOT / 'data'

TRANSLIT = {'ҷ': 'j', 'қ': 'q', 'ғ': 'gh', 'ӣ': 'i', 'ӯ': 'u', 'ҳ': 'h', 'ъ': '', 'ё': 'yo', 'ю': 'yu', 'я': 'ya', 'ч': 'ch', 'ш': 'sh', 'ж': 'zh', 'х': 'kh'}


def load(name):
    return json.loads((CFG / name).read_text(encoding='utf-8'))


def loc_phrase(p):
    prefix = 'шаҳри' if p['kind'] == 'city' else 'ноҳияи'
    return f"{prefix} {p['name_tg']}"


def product_plan(n, share):
    plan = {k: int(round(n * v)) for k, v in share.items()}
    # fix rounding so the total is exactly n (tape absorbs the difference)
    plan['tape'] += n - sum(plan.values())
    return plan


def build():
    places = load('places.json')['places']
    crops = {c['id']: c for c in load('crops.json')['crops']}
    tpl = load('title_templates.json')
    out, seen = [], set()
    for p in places:
        n = tpl['tier_counts'][p['tier']]
        plan = product_plan(n, tpl['product_share'])
        rng = random.Random(p['slug'])
        crop_ids = [c['crop'] for c in p['crops']]
        usage = {c: 0 for c in crop_ids}
        picks = []
        for product, count in plan.items():
            combos = [(t, c) for t in tpl['templates'][product] for c in (crop_ids if t['crop'] else [None])]
            rng.shuffle(combos)
            # spread over crops: prefer least-used crops, then template variety
            chosen, used_tpl = [], {}
            for _ in range(count):
                best = min(combos, key=lambda tc: ((usage.get(tc[1], 0) if tc[1] else 0.5), used_tpl.get(tc[0]['key'], 0), crop_ids.index(tc[1]) if tc[1] else 99))
                combos.remove(best)
                chosen.append(best)
                used_tpl[best[0]['key']] = used_tpl.get(best[0]['key'], 0) + 1
                if best[1]:
                    usage[best[1]] += 1
            picks += [(product, t, c) for t, c in chosen]
        rng.shuffle(picks)
        for i, (product, t, c) in enumerate(picks, 1):
            crop_name = crops[c]['name_tg'] if c else ''
            title = re.sub(r'\s+', ' ', t['t'].format(c=crop_name, loc='дар ' + loc_phrase(p), pl=loc_phrase(p))).strip()
            assert title not in seen, title
            seen.add(title)
            slug = '-'.join(x for x in [p['slug'], c or 'umumi', {'tape': 'lenta', 'pipe': 'pe-qubur', 'layflat': 'layflat'}[product], t['key']] if x)
            out.append({
                'id': f"{p['slug']}-{i:02d}", 'seq': len(out) + 1, 'place': p['slug'], 'place_tg': p['name_tg'], 'place_en': p['name_en'],
                'kind': p['kind'], 'region': p['region_en'], 'zone': p['zone'], 'tier': p['tier'],
                'product': product, 'crop': c, 'crop_tg': crop_name, 'crop_evidence': next((x['evidence'] for x in p['crops'] if x['crop'] == c), ''),
                'template': t['key'], 'title': title, 'slug': slug, 'status': 'pending', 'attempts': 0,
            })
    return out


def main():
    rows = build()
    DATA.mkdir(exist_ok=True)
    (DATA / 'titles.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    with open(DATA / 'titles.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['seq', 'id', 'place_tg', 'place_en', 'region', 'tier', 'product', 'crop_tg', 'crop_evidence', 'title', 'slug'], extrasaction='ignore')
        w.writeheader(); w.writerows(rows)
    print(f'{len(rows)} titles, {len({r["place"] for r in rows})} places')


if __name__ == '__main__':
    main()
