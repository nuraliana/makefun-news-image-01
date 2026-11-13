# The World in One Day — 13 November 2026

Entry for the make.fun bounty [news-image-01](https://make.fun/bounty/news-image-01):
one 1024×1024 newspaper-front-page image summing up Friday, 13 November
2026 in six verified stories — NVIDIA's chief resigns, the global Microsoft
365 outage, Europe joining the Ukraine talks, tankers hit in the Strait of
Hormuz, the strike on Nasser hospital in Gaza, and England beating Croatia.

The image is drawn deterministically with Python + PIL (`render.py`, no
network, no randomness). To redraw it from scratch, run `python3 render.py`.
`main.py` copies the finished `entry.png` to the output directory.

## Run locally

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (1024×1024 PNG).

## Referral

Made with [make.fun](https://make.fun/r/ctnjhg8e).
