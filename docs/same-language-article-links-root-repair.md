# Same-language article links: bounded root repair

## Scope and result

This is an operational remediation, not a whole-site SEO certification. A live, bounded cohort of 100 published posts (20 Persian source families and their four translations) was examined. The published-post identity index was read from the live database; URL candidates came from WordPress REST `link`, and exact translation identity came from stored relationships rather than guessed slugs.

- **46 articles repaired in stored `post_content`**: 17 Persian, 12 English, 6 Arabic, 10 Russian and 1 Tajik.
- **153 distinct-per-article contextual links**, generally 3–4 per article in this cohort, pointing to **141 verified destinations**. Selection was crop-specific and diversified across spacing, planting, cost, maintenance and crop-yield follow-ups. Links were spread through substantive paragraphs rather than collected in a random multilingual footer.
- 213 previous article anchors replaced or unwrapped; 20 generated related-link lists removed. This number does not assert that every previous anchor was broken.
- Every selected destination independently passed direct HTTP 200, exact self-canonical, public language, post identity, robots permission, noindex exclusion and crop-identity checks in its body.
- All 46 resulting body SHA-256 hashes were checked by a fresh database query. All public pages were fetched after WP Rocket cache purge; the exact number, URLs and labels of the contextual links were verified inside the actual theme's `article > .prose` content container, with no extra old article links remaining there.
- Publication dates, titles, slugs, products and prices were not modified. Modification times record the actual edit, with Asia/Tehran local time UTC+03:30.

## Root causes and code changes

The structure-preserving translator translated anchor text while copying original `href` attributes unchanged. That can produce localized text leading to another language. Generic lexical overlap in source candidate selection could also admit articles about a different crop.

`automation/translation_link_policy.py` now validates clean exact internal URLs and resolves an existing cross-language destination only through one live, reciprocal hreflang sibling. It verifies the destination's public language, canonical, status, indexability and crawlability; missing or ambiguous siblings fail closed. No language prefixes or slug variants are invented. It also checks descriptive anchor/title overlap, duplicate destinations, readable anchor text and word-count-dependent link bounds. These bounds are editorial safeguards, not a claimed Google link-count requirement.

The gate is applied to new translation output, rebuilding cached translation artifacts, the original translation SQL builder (including Russian), Persian SQL generation, and direct WordPress publishing **before remote mutations or media upload**. Source candidate selection now requires the same known crop rather than generic word overlap when a crop is unambiguously identified.

A deliberately bounded, reviewed crop vocabulary checks identity across title and body. Known contradictions, such as sainfoin being described as coffee or muskmelon as pumpkin, require editorial review in both original and translated material. This is not a universal factual validator.

The implementation is in the original producers/publishers, not a front-end output filter or an additional wrapper plugin. The code introduces no new redirects.

## Validation and limitations

- **70 offline regression tests passed locally**, covering prior queue/publisher behavior and the new policy. The new dedicated workflow repeats these tests without production credentials.
- **54 of the examined 100 posts remain deferred**: topic identity, source-content contradictions or insufficient corroborated target candidates need editorial review. Deferred pages were not rewritten or unpublished automatically.
- Root checks can intentionally block a new publication/package rebuild until its underlying content/links are corrected; errors are not replaced with arbitrary links just to reach a quota.
- Historical SQL/ZIP packages already stored or downloaded were not regenerated or certified by this work; do not reimport them as though they passed the new gate.
- The rest of the site's link graph, orphan pages, incoming-link distribution and wider content accuracy remain to be audited. This change does not claim GSC indexing or whole-site internal SEO is solved.

Raw database bodies, guarded repair/rollback SQL, authentication/session URLs and private evidence remain in the private backup and are not included in this public document.
