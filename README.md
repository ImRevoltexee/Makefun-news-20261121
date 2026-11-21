[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/ImRevoltexee/Makefun-news-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard)
[![reward](https://make.fun/badge/news-image-20261121/ImRevoltexee/Makefun-news-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# 21 November 2026 — The World in One Day

Entry for the [make.fun](https://make.fun) bounty
[news-image-20261121](https://make.fun/bounty/news-image-20261121):
one image summing up the world's news of Saturday 21 November 2026.

## The image

A newspaper-style infographic (1024×1024, drawn with code, no AI image
generator): a masthead naming the day, six stories, and an "ALSO TODAY"
strip.

- **Conflict** — Russian missiles land in Poland: 400+ drones and 110
  missiles hit Ukraine overnight; two missiles and a drone came down in
  Poland, which PM Tusk calls a deliberate provocation.
- **Economy** — AI sell-off drags the S&P into correction: US stocks fell
  about 3.7% as AI and chip shares plunged.
- **Justice** — World court: Myanmar committed genocide. The ICJ ruled
  Myanmar's forces committed state-sponsored genocide against the
  Rohingya — a first for the court.
- **Disaster** — Magnitude 6.8 quake shakes Peru: the tremor struck the
  Junín region and rattled Lima, 320 km away; no casualties reported.
- **Climate** — COP31 talks spill into overtime: fossil-fuel language was
  stripped from the draft deal in Antalya.
- **Health** — Cancer pill makes tumours vanish: daraxonrasib plus chemo
  made tumours undetectable in 1 in 12 patients in a pancreatic cancer
  trial.

Also today: Trump, Xi and Putin end their first trilateral summit with a
joint vow against nuclear war; the UK and EU sign deals on food trade,
carbon markets and youth mobility; New York's mayor sets 2032 as the new
date to close the Rikers Island jail complex.

Sources: Reuters, OneTurn, CNN, WSJ, NY Post, ecancer, OncLive, UN News,
AP, The Daily Short.

## How it works

- `draw.py` — draws `entry.png` from scratch with Pillow (deterministic:
  no network, no randomness, no timestamps). Run it to regenerate the image:
  `python3 draw.py`
- `main.py` — the entry point (Python 3.13, standard library only). It
  copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`)
  and validates the file first (PNG or JPEG, at most 1 MiB, at most
  1024×1024, copied bytes hash-checked). It parses PNG dimensions from
  the IHDR chunk and JPEG dimensions from the Start-Of-Frame marker, so
  either format is accepted.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
