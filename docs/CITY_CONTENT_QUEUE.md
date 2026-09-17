# Missing-city content queue

This queue creates draft WordPress city posts that do not already exist in the SQL snapshot.

- Scope: all missing Iranian cities from a pinned `sajaddp/list-of-cities-in-Iran` dataset.
- Text: Agnes `agnes-2.5-flash`, minimum 1,050 Persian words, 4–7 approved internal links.
- Images: GitHub Models `openai/gpt-image-1`, one featured image and two inline images per post.
- Output: per-city JSON, PNG files, idempotent creation SQL, combined SQL, and rollback SQL.
- Safety: generated posts use `draft`; SQL must be reviewed before import. Existing titles/slugs are skipped.
- Batch: 3 posts per run; scheduled every two hours. Failed image-model calls stop the queue and record `blocked_image_model` with the API error.

The workflow uses the repository `GITHUB_TOKEN` with `models: read`. If GitHub Models does not permit image generation for this repository/account, select a replacement image provider before resuming.
