# Article producer: canonical-link prevention

## Confirmed origin and limits

The live post metadata for post 509608 identifies
`article-content-queue:xref-002`. Its source item is in this repository,
not the older `maghalat` translation repository. The original raw Persian
slug in that item differs from the current WordPress-encoded, shortened
database slug. Do not infer a destination from a shared slug prefix:
multiple real articles share long prefixes.

The producer already contains an earlier `wp_post_name()` SQL encoding fix.
This change does not claim to introduce that earlier repair or cure every
historical URL. It addresses remaining internal-link selection defects:

- REST discovery constructed URLs from slugs rather than the returned `link`.
- A negative list admitted unknown content types.
- Sitemap caches never expired.
- Random link selection checked neither the live response nor language,
  canonical, noindex, crawl permission, or topical overlap.

## New generation behavior

- Use the exact WordPress REST `link` for published posts. Never reconstruct
  it, infer a path prefix, or fall back to a guessed slug.
- Expire and version the sitemap candidate cache after six hours.
- Only permit the explicit content-type allowlist.
- Rank candidates by lexical topic overlap; this is a basic relevance
  safeguard, not an editorial relevance or factual-quality guarantee.
- Before supplying a link to the model, require direct HTTP 200 HTML,
  Persian `lang`, exactly one matching canonical, no HTML/header noindex,
  and permission under the fetched robots rules for Googlebot.
- Reject redirects, unavailable destinations, unknown languages, queries,
  fragments, foreign hosts and ambiguous canonicals. Do not rewrite them
  to a guessed substitute.
- Stop before generation if fewer than the required verified links remain.
  No filler links are added to conceal a failed gate.
- Cache verification for 15 minutes per runner. Fetch failures fail closed.

The helper is called by the original article producer; it is not a new
WordPress plugin or an output-time wrapper. The generation trigger file,
artifact state, existing SQL bundles and live database are not modified.

## Verification

Local tests: 23 pre-existing article queue tests plus 17 new regression tests
pass; the three existing WordPress publisher tests pass separately.
All model/network operations in unit tests are mocked. A separate read-only
live check rejected all six examined legacy URLs and accepted all six
current canonical URLs (post IDs 509608, 509604, 509560, 509600, 509104,
510816). This confirms the link gate, not the agronomic quality of those
articles or Google's eventual indexing decisions.

## Still separate work

- Inspect old packages and source artifacts before any re-import; they do not
  automatically become safe because the producer has changed.
- Repair existing stored links at their original source, with a fresh backup
  and exact before/after checks.
- For legacy URLs with independently confirmed identity, use exact historical
  compatibility redirects only after checking the current destination.
- Translation link localization and factual review of existing generated
  articles remain separate tasks. This Persian gate does not certify them.
- Recheck public HTML after cache invalidation and only then request appropriate
  Search Console validation. No blanket validation or indexing guarantee.
## Deployed historical compatibility repair

After committing and testing the producer change, six exact legacy article
redirects were deployed in the site's existing native `.htaccess`, outside the
WordPress-managed block. No plugin was added, no canonical slug was changed,
and no database content or publication date was rewritten. The original
configuration was backed up privately; it is not included in this repository.

Identity was checked against the article queue metadata and the exact
`wp_post_name()` result, not a shared prefix. Live verification for each of
509608, 509604, 509560, 509600, 509104 and 510816 confirmed:

- GET: exactly one 301, then the intended HTTP 200 page.
- HEAD: 301.
- Target directly: HTTP 200 with zero redirects.
- Target canonical: exact intended URL; HTML language: fa-IR.

Homepage and a Tajik product category remained direct HTTP 200. An unrelated
nonexistent control remained HTTP 404. The new rules are exact-path,
domain-bound, GET/HEAD-only and empty-query-only; existing server rules were
preserved byte-for-byte. Offline checks included 18 near-match negatives.

The GitHub regression run for commit
`41f904807d73f3b3606a02b5d84bc517f1ffbe1b` completed successfully:
https://github.com/kikibox/maghala2/actions/runs/39055760231

Six entries from the previously confirmed 106-URL live-404 review cohort are
now repaired. The other 100 entries have not been certified as fixed or
retested as a complete cohort in this step. Google reports can lag behind
live behavior. No blanket Search Console validation was requested.
