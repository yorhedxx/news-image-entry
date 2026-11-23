[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/yorhedxx/news-image-entry/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/yorhedxx/news-image-entry/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The World in One Day — Monday 23 November 2026

An entry for make.fun's **"Sum up 23 November's world news in one image"**
(news-image-20261123).

`main.ts` (Node 22, standard library only) copies the poster beside it,
`entry.png`, to `/output/entry.png` — the file the competition's gate checks
and its judge sees. It sanity-checks the asset first (size within the gate's
1 MiB cap, and a real PNG/JPEG signature). Both grader runs write identical
bytes (verified locally: two runs, byte-identical output).

## The image (v3)

A one-page newspaper front page, 1024 × 1024 PNG, drawn entirely in code —
no photographs, no downloaded artwork. v3 is a visual-fidelity pass over
v2: the same 37 stories, heroes, KPI numbers, timeline and counts, rebuilt
to sit as close as possible to the composition and finish of the previous
day's winning front page — the layout system is modelled on it, while every
scene, headline and line of text is original work for Monday's news.

It follows the classic broadsheet front-page skeleton: dark masthead bar, a
giant serif date, a red italic deck naming the day's top three stories, a
KPI strip of six big serif numbers, colour region tabs with per-region
counts, a "THE DAY IN UTC" timeline, three hero cards with rich flat scenes
(the COP31 delegates' table under a globe and wall clock; the Dymer block
under drones and a searchlight, its collapsed floors pancaked and burning;
the corvette Merkury at sea with seven drone boats closing in), each hero
carrying a red banner ribbon, a bold stat callout and its story number,
twelve medium cards each with its own mini-scene and stat banner, a dark
navy dotted world map whose red numbered pins match the card numbers, a
numbered ALSO list, a red DATE CHECK box naming big stories deliberately
excluded as not from today, and a certainty legend (REPORTED = carried by
the day's wires; CLAIM = one side's account).

**Every one of the 37 stories is illustrated**: the 3 heroes and 12 medium
cards carry full scenes, and each of the 22 ALSO items carries its own
small drawn thumbnail matched to its headline — a ballot box for Spain's
election, a dartboard for the Grand Slam, a bank front for Ghana's
buyback, a chess knight for the title match, and so on.

**37 stories, 7 regions** — Europe 9, Asia-Pacific 9, Africa 5, Middle
East 4, Oceania 4, Americas 3, World 3. Heroes:

1. **COP31 ends without a deal** — the UN summit in Antalya closed after
   the EU, Panama and the Marshall Islands refused a cover decision that
   never mentioned fossil fuels; up to 90 countries signed the "35 by 35"
   electrification pledge (Reuters).
2. **Russian strikes kill at least 11 in the Kyiv region** — a five-storey
   block in Dymer partly collapsed; rescuers search for 11 missing,
   including two children (Reuters/AP).
3. **Ukraine says seven naval drones sank the Russian corvette Merkury**
   off Libya — labelled CLAIM; Moscow has not confirmed (Reuters).

Medium cards (4–15): Democrats win 258 House seats, most since 1992
(AP/Reuters) · Trump leans to striking Iran after the New Year (Fox News) ·
Houthis claim a direct hit on Saudi Arabia's Rabigh refinery — CLAIM
(Reuters) · Banten factory fire kills 24, ~30 missing (Reuters) · Taiwan
eases margin rules, stocks bounce 2.1% (Reuters) · Hedge funds lose 3%+ in
the AI selloff (Reuters) · Burnham: the EU deal is the biggest growth
measure (BBC) · First women join the EDITH AI breast-screening trial
(NHS/BBC) · German factories at a 56-month PMI high (Reuters) · Drone
strikes hit Khartoum and a UN compound (AFP) · Army rescues 18 of 22
abducted brigade children in Kaduna (wires) · Black Caps hold India to a
draw in Wellington (cricket.com.au).

ALSO list (16–37): Indonesia's VP nominations and India's PMI 56.3; South
Korea's education minister resigns and Seoul's stabilisation pledge;
China's margin easing; Japan's holiday closure and ministerial apology;
Spain's snap-election final week; Price wins darts' Grand Slam;
Manchester's Co-op Live evacuation; Liverpool 4–0 Man Utd; Ghana's bond
buyback; the firmer rand; the rain-delayed Centurion Test; Chalmers'
unemployment warning; sliding Australian shares; Australia's Billie Jean
King Cup win; the IDF intelligence warning on Iran; Iran's designation of
the Royal Navy and RAF; bouncing US futures; NFL Sunday; and the Gukesh–
Sindarov world chess title match starting Tuesday in Geneva.

DATE CHECK (deliberately excluded as not Monday's news): the Bayelsa
funeral-boat capsize (Fri 20 Nov), Mexico's capture of "El Chapo Isidro"
(announced Sat 21 Nov), and the Nikkei's −5% plunge (Friday's close —
Tokyo was shut Monday).

## How it was made

`build_poster.py` (Python + Pillow) draws everything — masthead, KPI strip,
region tabs, timeline, the flat illustrations for all 15 numbered cards
(the COP31 summit table, the Dymer block with pancaked floors, the Merkury
at sea with seven drone boats, a Capitol dome, a refinery, charts, a
cricket pitch…), the 22 ALSO thumbnails, the dark dotted world map and its
pins, and all text, which is measured with PIL and shrunk/wrapped so
nothing overflows its card. Each illustration is rendered into its own
tile and pasted, so no stroke can spill outside its box. Every fact on
the poster comes from reporting actually read on 23 November 2026; the
full source list with URLs is in `SOURCES.md` in this entry's development
files (Reuters, AP, BBC, AFP, Al Jazeera, Fox News, The Guardian, NHS
England, Kyodo, cricket.com.au, ABC, Bank of Ghana). Stories that could
not be verified from real reporting were dropped.

## Run it

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
# -> out/entry.png

python3 build_poster.py   # regenerates entry.png from the day's sources
```

License: MIT (see `LICENSE`).
