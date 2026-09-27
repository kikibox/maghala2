# Agnes concurrency benchmark

- Text model: `agnes-3.0-flash`
- Image model: `agnes-image-2.5-flash`
- Text keys detected: **8**
- Image keys detected: **8**
- Safe text concurrency: **16**
- Safe image concurrency: **16**

| Service | Concurrency | Success | Failure | Wall time |
|---|---:|---:|---:|---:|
| text | 8 | 8 | 0 | 105.803s |
| image | 8 | 8 | 0 | 26.673s |
| text | 12 | 12 | 0 | 4.806s |
| image | 12 | 12 | 0 | 20.211s |
| text | 16 | 16 | 0 | 14.741s |
| image | 16 | 16 | 0 | 27.142s |
