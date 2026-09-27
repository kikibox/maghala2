# Agnes concurrency benchmark

- Text model: `agnes-3.0-flash`
- Image model: `agnes-image-2.5-flash`
- Text keys detected: **8**
- Image keys detected: **8**
- Safe text concurrency: **48**
- Safe image concurrency: **64**

| Service | Concurrency | Success | Failure | Wall time |
|---|---:|---:|---:|---:|
| text | 40 | 40 | 0 | 5.158s |
| image | 40 | 40 | 0 | 60.016s |
| text | 48 | 48 | 0 | 7.244s |
| image | 48 | 48 | 0 | 33.72s |
| text | 64 | 40 | 24 | 9.289s |
| image | 64 | 64 | 0 | 63.612s |
