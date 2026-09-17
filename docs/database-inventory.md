# Database inventory — 2026-09-13

## Source

- Archive: `navaraby_wp569.sql.zip`
- Extracted SQL size: 65,167,702 bytes
- SQL SHA-256: `9db246a43e78e7847684209ad53a0250733f7f4132c526294890015d40448d37`
- Archive SHA-256: `8ceef363a4f1c8ad4961c0eaf29558e48c132eae1770c8e382b12fc2e0a80a5c`
- MySQL: 8.0.32
- Encoding: utf8mb4
- Prefix: `ha_`

## Parsed core records

| Record | Count |
|---|---:|
| `ha_posts` rows | 2,410 |
| posts with metadata | 1,459 |
| terms | 300 |
| term-taxonomy rows | 300 |
| term relationships | 859 |

## Published content

| Type | Count |
|---|---:|
| Posts | 220 |
| Pages | 38 |
| FAQs | 42 |
| Products | 45 |

## Published post language inventory

| Language group | Existing posts |
|---|---:|
| Persian/base and uncategorized | 172 |
| Iraqi Arabic | 30 |
| Tajik | 18 |

The Iraqi Arabic total includes 13 older city/market articles under `iraq` plus 17 translated technical articles under `maqalat-al-ray`. Tajik currently has 18 technical translations. Pair mapping and missing-translation detection are the next phase.

## Safety

The full database dump is intentionally excluded from Git because it can contain users, configuration, sessions, orders, and secrets. Only sanitized analysis, scripts, article exports, translation manifests, and final checksums should be committed.