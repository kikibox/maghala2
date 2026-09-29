#!/usr/bin/env python3
import json
import article_content_queue as queue
from translate_generated_articles import status_payload

state = json.loads(queue.QUEUE.read_text(encoding="utf-8"))
translation = status_payload()
if translation["articles_missing_any_translation"]:
    result = "translations_pending"
elif any(item.get("status") == "processing" for item in state.get("items", [])):
    result = "processing"
elif queue.select_batch(state):
    result = "ready"
elif any(item.get("status") == "failed" for item in state.get("items", [])):
    result = "attention_required"
else:
    result = "complete"
queue.write_status(state, result)