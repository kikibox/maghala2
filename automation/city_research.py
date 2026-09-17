#!/usr/bin/env python3
"""Fast, cached, evidence-aware agricultural research for each city post."""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

WIKI_API = "https://fa.wikipedia.org/w/api.php"
USER_AGENT = "navar-city-content-queue/4.0 (city research; https://navar-abyari.ir)"
MAX_SOURCE_CHARS = 5000


def _fetch(params, timeout=45):
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _search(query, limit=3):
    data = _fetch({"action": "query", "list": "search", "srsearch": query, "srlimit": limit, "format": "json", "utf8": 1})
    return [row.get("title", "") for row in data.get("query", {}).get("search", []) if row.get("title")]


def _pages(titles):
    if not titles:
        return []
    data = _fetch({"action": "query", "prop": "extracts|info", "inprop": "url", "explaintext": 1, "redirects": 1, "titles": "|".join(titles[:10]), "format": "json", "utf8": 1})
    rows = []
    for page in data.get("query", {}).get("pages", {}).values():
        text = re.sub(r"\s+", " ", page.get("extract", "")).strip()
        if text:
            rows.append({"title": page.get("title", ""), "url": page.get("fullurl", ""), "text": text[:MAX_SOURCE_CHARS]})
    return rows


def _collect_sources(item):
    exact = [item["city"], f"شهرستان {item['county']}", f"استان {item['province']}"]
    queries = [f"{item['city']} کشاورزی محصولات زراعی", f"{item['county']} کشاورزی", f"{item['province']} محصولات کشاورزی"]
    titles = exact[:]
    for query in queries:
        try:
            titles.extend(_search(query, 3))
        except Exception:
            continue
    unique = []
    seen = set()
    for title in titles:
        key = title.strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(key)
    try:
        return _pages(unique)
    except Exception:
        return []


def _fallback(item, sources, error=""):
    return {"status": "insufficient_evidence", "city": item["city"], "county": item["county"], "province": item["province"], "summary": "برای ادعای دقیق درباره محصولات زراعی این شهر، شواهد عمومی کافی پیدا نشد؛ مقاله باید بر نیازسنجی واقعی مزرعه تکیه کند.", "agricultural_products": [], "climate_water_notes": [], "irrigation_implications": ["نوع کشت، بافت خاک، شیب، کیفیت آب و دبی منبع پیش از انتخاب نوار تیپ بررسی شود."], "sources": [{"title": x["title"], "url": x["url"]} for x in sources if x.get("url")], "error": error[:300]}


def research_city(item, agnes_call, output_dir):
    """Return cached research; use only evidence included in fetched public sources."""
    research_dir = Path(output_dir) / "research"
    research_dir.mkdir(parents=True, exist_ok=True)
    cache = research_dir / f"{item['source_id']}.json"
    if cache.exists():
        try:
            saved = json.loads(cache.read_text(encoding="utf-8"))
            if saved.get("research_version") == 1:
                return saved
        except Exception:
            pass
    sources = _collect_sources(item)
    if not sources:
        result = _fallback(item, sources, "No usable public source extract")
    else:
        evidence = "\n\n".join(f"SOURCE {i+1}: {x['title']}\nURL: {x['url']}\nTEXT: {x['text']}" for i, x in enumerate(sources))
        prompt = f'''به‌عنوان پژوهشگر محتاط کشاورزی، برای آماده‌سازی مقاله نوار آبیاری درباره شهر {item['city']}، شهرستان {item['county']}، استان {item['province']} فقط از شواهد عمومی زیر یک تحقیق سریع استخراج کن. هیچ محصول، اقلیم، بحران آب، سطح زیر کشت یا ویژگی محلی را حدس نزن. محصول زراعی را فقط وقتی ذکر کن که متن منبع صریحاً از آن پشتیبانی کند. اگر شاهد مربوط به شهرستان یا استان است، scope را همان county یا province بگذار و آن را به شهر نسبت قطعی نده. توصیه آبیاری باید مشروط و فنی باشد. فقط JSON معتبر با کلیدهای status، summary، agricultural_products، climate_water_notes، irrigation_implications برگردان. agricultural_products آرایه‌ای از اشیای name، scope، evidence، confidence باشد و confidence فقط high یا medium باشد. climate_water_notes نیز آرایه‌ای از اشیای note، scope، evidence، confidence باشد. وضعیت فقط grounded یا insufficient_evidence باشد.\n\n{evidence}'''
        try:
            obj = agnes_call(prompt)
            if not isinstance(obj, dict):
                raise ValueError("Research response is not an object")
            obj["sources"] = [{"title": x["title"], "url": x["url"]} for x in sources if x.get("url")]
            result = obj
        except Exception as exc:
            result = _fallback(item, sources, str(exc))
    result.update({"research_version": 1, "city": item["city"], "county": item["county"], "province": item["province"]})
    cache.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def prompt_context(result):
    """Compact JSON context for the writer; explicitly marks evidence boundaries."""
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))
