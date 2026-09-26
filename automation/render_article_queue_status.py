#!/usr/bin/env python3
import json
import article_content_queue as queue
from translate_generated_articles import status_payload

state = json.loads(queue.QUEUE.read_text(encoding="utf-8"))
translation = status_payload()
result = "translations_pending" if translation["articles_missing_any_translation"] else "ready"
queue.write_status(state, result)