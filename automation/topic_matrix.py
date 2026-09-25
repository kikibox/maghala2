#!/usr/bin/env python3
"""Generate exactly 1150 pre-seeded useful-article topics for navar-abyari.ir.

DATA SOURCE: data/article-catalog.json — real crops (49), real products (14),
real FAQs, real strategic topics, all extracted from the live DB dump
(navaraby_wp569.sql.gz). No invented crop names.

This module ONLY produces the article topic queue. It is intentionally
SEPARATE from automation/city_content_queue.py (city advertising posts).
The two systems share no files and no queue directory.

V3 — deterministic seed, target = 1150.
Output: artifacts/article-content-queue/topics.json
"""
import json, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "article-catalog.json"
OUT_FILE = ROOT / "artifacts" / "article-content-queue" / "topics.json"

TARGET = 1150
SEED = 2026

cat = json.loads(CATALOG.read_text(encoding="utf-8"))
crops = cat["crops"]
crop_templates = cat["crop_templates"]
products = cat["products"]
product_templates = cat["product_templates"]
irrigation_methods = cat["irrigation_methods"]
strategic_topics = cat["strategic_topics"]

def slugify(title):
    s = title.lower().replace("ي","ی").replace("ك","ک").replace("‌","")
    s = re.sub(r"[^a-z0-9؀-ۿ]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")

topics = []
def add(pid, title, focus, vertical):
    topics.append({
        "id": pid, "title": title, "slug": slugify(title),
        "focus": focus, "category": "مقاله‌ها", "post_type": "post",
        "vertical": vertical, "status": "pending", "attempts": 0
    })

rng = random.Random(SEED)

# ---------- A) Crop × template (all 343 real combos) ----------
crop_combos = [(c, t) for c in crops for t in crop_templates]
rng.shuffle(crop_combos)
for i, (crop, tmpl) in enumerate(crop_combos, start=1):
    add(f"crop-{i:03d}", tmpl["title"].format(crop=crop),
        f"{tmpl['focus']} {crop}", "crop")

# ---------- B) Product × template (all 112 real combos) ----------
prod_combos = [(p, t) for p in products for t in product_templates]
rng.shuffle(prod_combos)
for i, (prod, tmpl) in enumerate(prod_combos, start=1):
    add(f"prod-{i:03d}", tmpl["title"].format(product=prod),
        f"{tmpl['focus']} {prod}", "product")

# ---------- C) Strategic topics (all 33) ----------
for i, t in enumerate(strategic_topics, start=1):
    add(f"strat-{i:03d}", t, "strategic irrigation guide", "strategic")

# ---------- D) Irrigation-method deep guides (all 12) ----------
for i, m in enumerate(irrigation_methods, start=1):
    add(f"irr-{i:02d}", f"راهنمای جامع {m}", f"{m} comprehensive guide", "irrigation")

# ---------- E) Crop × irrigation-method cross, DEEP (filler to reach target) ----------
# "آبیاری {method} در کشت {crop}" — real method × real crop × real angle,
# deduped by slug. 16 extended methods × 4 crops-angles.
methods_extended = list(irrigation_methods) + [
    "آبیاری قطره‌ای با نوار تیپ", "آبیاری قطره‌ای با قطره‌چکان",
    "آبیاری بارانی با رانش", "آبیاری هوشمند"
]
xref_angles = [
    "نکات کلیدی","هزینه بهینه","هزینه در مزرعه","کاربردها","مزایا",
    "راهنمای جامع","مقایسه","چالش‌ها","پیش‌نیازها"
]
cross_combos = [(c, m, a) for c in crops for m in methods_extended for a in xref_angles]
rng.shuffle(cross_combos)
i = 0
for crop, method, angle in cross_combos:
    if len(topics) >= TARGET:
        break
    i += 1
    add(f"xref-{i:03d}",
        f"{method} در کشت {crop}: {angle}",
        f"{method} {crop} {angle}",
        "xref")

# ---------- Deduplicate by slug, trim to target ----------
seen = set()
unique = []
for t in topics:
    if t["slug"] not in seen:
        seen.add(t["slug"])
        unique.append(t)
    if len(unique) >= TARGET:
        break

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
output = {
    "version": 3,
    "seed": SEED,
    "target_total": TARGET,
    "total": len(unique),
    "category": "مقاله‌ها",
    "post_type": "post",
    "data_source": str(CATALOG.relative_to(ROOT)),
    "note": "useful articles only — SEPARATE from city advertising queue",
    "topics": unique
}
OUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

from collections import Counter
vc = Counter(t["vertical"] for t in unique)
print(f"Total topics: {len(unique)} (target {TARGET})")
print("By vertical:", dict(vc))
print(f"Saved to {OUT_FILE}")
