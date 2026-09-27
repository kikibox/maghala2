# Agnes concurrency benchmark

- Text model: `agnes-3.0-flash`
- Image model: `agnes-image-2.5-flash`
- Text keys detected: **8**
- Image keys detected: **8**
- Safe text concurrency: **32**
- Safe image concurrency: **32**

| Service | Concurrency | Success | Failure | Wall time |
|---|---:|---:|---:|---:|
| text | 20 | 20 | 0 | 28.468s |
| image | 20 | 20 | 0 | 27.257s |
| text | 24 | 24 | 0 | 6.176s |
| image | 24 | 24 | 0 | 26.451s |
| text | 32 | 32 | 0 | 5.207s |
| image | 32 | 32 | 0 | 49.66s |
