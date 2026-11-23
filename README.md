[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/cryptotainment/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/cryptotainment/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# The World in One Day — Tuesday 24 November 2026

A program that draws one front page summing up Tuesday 24 November 2026's
world news and writes it to `/output/entry.png` (1024x1024 PNG, under 1 MiB,
deterministic).

`main.py` is Python 3.13 standard library only: it carries its own PNG
encoder and a hand-drawn 5x7 bitmap font, and draws the whole page itself —
masthead, lead story with a market chart, and six more stories with
pictograms. No network, no external files, no dependencies.

## The seven stories

1. **Nvidia reinstates CEO Jensen Huang** — Trump says he made the deal as
   the chipmaker brings back its co-founder after his affair with an alleged
   spy; shares surge and Congress objects. (BBC / Reuters)
2. **Ukraine sinks Russian warship off Libya** — seven sea drones sank the
   corvette Merkury in Benghazi and hit the cargo ship Angara. (BBC / AP)
3. **North Korea may shut Swiss office in Pyongyang** — Pyongyang condemned
   Swiss sanctions on a children's camp linked to Russia. (Reuters / KCNA)
4. **CrowdStrike buys Zscaler in a $44bn deal** — all-stock takeover as cyber
   threats mount. (Reuters)
5. **Iran flogs singer who sang without hijab** — her lawyers confirmed the
   flogging. (BBC)
6. **US weighs training Syrian troops** — demining training, the first such
   mission since 2024. (Reuters)
7. **Gaza now a toxic wasteland, Oxfam says** — Israeli attacks poisoned its
   water, soil and air. (BBC)

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs write byte-identical output (verified: sha256
`5c1b40db1a664cc4cc3e4cfc663455f3b4cf50eaec643e0a020436458e1d843f`,
19,594 bytes).
