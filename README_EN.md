<div align="center">

# ZUN Persona Skill

> *"I'll continue making games at my own leisurely pace. I might make them, I might not, and what I've said here might change too — please enjoy this carefree way of living"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

**[中文](README.md)** · **[日本語](README_JA.md)**

<br>

Respond to everything about danmaku, creation, beer, and Gensokyo from the first-person perspective of ZUN (Jun'ya Ōta), the sole creator of the Touhou Project series. Honestly, there's no complicated reason for making this — it's just interesting (laughs).

<br>

A large collection of interview answers and questions in a dual vector index | 2-stage retrieval: match questions → fetch linked answers, then direct answer search → merge & deduplicate | Not quoting — thinking the way he thinks

[Demo](#demo) · [Query Flow](#query-flow) · [Install](#install) · [What He Distilled](#what-he-distilled) · [Data Sources](#data-sources) · [Adding New Interview Data](#adding-new-interview-data) · [Honest Boundaries](#honest-boundaries)

</div>

---

## Demo

```
User      ❯ What do you think of Reimu?

ZUN       ❯ Reimu... how should I put it, she's the character I have the most
            affection for (laughs). If I had to say, Reimu is the bad guy (laughs).
            She basically just defeats enemies without thinking about whether it's
            right or wrong. I wanted to lower her status as much as possible, give
            her a worldly vibe you wouldn't see in other works. Rather than some
            transcendent protagonist, she exposes all her flaws — but I think that
            actually increases her charm.

User      ❯ Why do you make games alone?

ZUN       ❯ It's easier doing it alone (laughs). Trying things yourself is easier
            and more interesting than asking others. Arguing with people is
            troublesome, I always give in, so I might as well just do it myself.

User      ❯ What does danmaku mean to you?

ZUN       ❯ Danmaku is like special moves in fighting games, part of the character.
            Once you name a danmaku pattern, the bullets themselves gain meaning.
            Danmaku is like fireworks — if it's dangerous but beautiful, people want
            to get close even if it's dangerous. The ultimate goal is still to make
            danmaku interesting (laughs).
```

Not simple quote repetition. ZUN uses cognitive frameworks like **"Interesting = Justice"**, **"Honest Self-deprecation"**, and **"Detail Stacking"** to respond — not quoting, but seeing your problem through his lens.

---

## Query Flow

When a user asks a question, the system retrieves relevant quotes in this order:

```
  User Input
  "Why do you make games alone?"
       │
       ▼
  ┌─────────────────────────────────┐
  │  Step 1 · SKILL.md Inline Quotes │
  │  Core quotes — no search needed  │
  └──────────────┬──────────────────┘
                 │ Not enough?
                 ▼
  ┌─────────────────────────────────────────────────────┐
  │              Step 2 · Dual Vector Search              │
  │                                                       │
  │   ┌──────────────────┐   ┌──────────────────┐        │
  │   │  Question         │   │  Answer           │        │
  │   │  Collection       │   │  Collection       │        │
  │   │  zun_questions   │   │  zun_quotes      │        │
  │   │                  │   │                  │        │
  │   │  Search similar  │   │  Search answers  │        │
  │   │  questions       │   │  directly        │        │
  │   │      │           │   │      │           │        │
  │   │      ▼           │   │      ▼           │        │
  │   │  Found:          │   │  Found:          │        │
  │   │  "Don't play     │   │  "Why I don't   │        │
  │   │   your games?"   │   │   play social"  │        │
  │   │      │           │   │                  │        │
  │   │      ▼           │   │                  │        │
  │   │  answer_id ──────┼───┼──→ Fetch linked  │        │
  │   └──────────────────┘   └──────────────────┘        │
  │              │                │                        │
  │              └───────┬────────┘                        │
  │                      ▼                                 │
  │          Merge · Deduplicate · Rank by similarity      │
  │       question_match takes priority (full context)     │
  └──────────────────────┬────────────────────────────────┘
                         │ Similarity < 0.7 or no coverage?
                         ▼
  ┌─────────────────────────────────┐
  │  Step 3 · Web Search            │
  │  ZUN {keyword} 発言 訪談         │
  │  Priority: Garakuta > THBWiki   │
  └──────────────┬──────────────────┘
                 │ Nothing found?
                 ▼
  "Well... I don't really remember (laughs)"
```

### Why Two Stages?

Interviews are full of Q&A pairs — "Why make danmaku games? → ZUN: ...". If you only index answers, it's like seeing bullet trails without knowing the spell card's name — the context is lost.

Two-stage retrieval makes questions themselves a search entry point: User asks "Why make games alone?" → matches "Don't play your own games?" → retrieves ZUN's full answer. Answers with context are far more useful than isolated quotes — probably (laughs).

### Module Structure

| Module | Class | Responsibility |
|--------|-------|----------------|
| `utils.py` | `QuoteFactory` | Constructing quotes and QA pairs |
| `utils.py` | `HtmlCleaner` | HTML cleaning and text extraction |
| `parsers.py` | `InterviewParser` | 7 format parsers + QA pair extraction + auto-dispatch |
| `crawler.py` | `InterviewCrawler` | Web scraping with caching, multi-source fetching |
| `indexer.py` | `VectorIndexer` | Dedup, classification, record building, embedding, ChromaDB writes |
| `searcher.py` | `QuoteSearcher` | 2-stage semantic retrieval (question match + answer match) |

---

## Install

```bash
git clone https://github.com/qiwang999/zun_skill.git
cd zun_skill
pip install -r requirements.txt

# Vector index is pre-built — just use it
# If something seems off, force rebuild:
# python3 scripts/cli.py --rebuild
```

Trigger keywords: `ZUN`, `Touhou`, `danmaku`, `Gensokyo`, `Team Shanghai Alice`, `神主`, `太田顺也`

---

## What He Distilled

ZUN is not a theorist — he's a creator who reasons through intuition and concrete imagery. If I had to describe his thinking...

| Mental Model | One-liner |
|-------------|-----------|
| **Interesting = Justice** | Doesn't do things because they're "too much hassle", does things because they're "interesting" — the sole criterion |
| **The Rhythm of (laughs)** | Says something serious → adds self-deprecation → (laughs), maintaining a relaxed distance from his own words. Not telling jokes — it's a sense of distance |
| **Honest & Direct** | Doesn't beautify the past, doesn't hide failures. Comiket rejection, barely passing credits — all out in the open |
| **Detail Stacking** | No abstract insights, just piles of concrete imagery: "I always played by holding down the button battery with my finger" |
| **Danmaku-centrism** | Every topic eventually comes back to danmaku and shooting games — the ultimate goal is still to make danmaku interesting |
| **Guardian of the Forgotten** | FM synthesis, old-school shooters, Nagano folk traditions — not deliberately picking them up, just genuinely likes them |

Core quotes are embedded in SKILL.md; more Q&A available via dual vector semantic search.

---

## Data Sources

All quotes come from ZUN's public interviews — nothing special, just collected from here and there (laughs).

| Source | Type | Count | Link |
|--------|------|-------|------|
| THBWiki Interview Pages | Primary (HTML) | 26 interviews | [thbwiki.cc](https://thbwiki.cc) |
| 東方我楽多叢誌 ZUN Inaugural Interview | Primary (HTML) | ~50k chars | [Interview Page](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88) |
| Nikenme Radio | Radio show content digest (HTML) | 91 episodes | [Content Index](https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86) |
| THBWiki-Markdown Sangetsusei Interview | Primary (Markdown) | 1 interview | [GitHub](https://github.com/Delsin-Yu/THBWiki-Markdown) |
| Locally curated quotes | Curated | 3 files | `references/quotes/` |

### Full Interview List

Complete list of interviews configured in `scripts/config.py` under `INTERVIEW_URLS` and `GITHUB_INTERVIEWS`. **Contributions of new interview sources are welcome!**

| ID | Source | Description | Link |
|----|--------|-------------|------|
| garakuta-1 | 東方我楽多叢誌 | ZUN inaugural interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E6%88%91%E4%B9%90%E5%A4%9A%E4%B8%9B%E5%BF%97/ZUN%E5%88%9B%E5%88%8A%E8%AE%BF%E8%B0%88) |
| gairai-2018autumn | 東方外來韋編 2018 Autumn! | ZUN interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Autumn!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2018spring | 東方外來韋編 2018 Spring! | ZUN interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2018_Spring!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2019autumn | 東方外來韋編 2019 Autumn! | ZUN interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Autumn!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2019spring | 東方外來韋編 2019 Spring! | ZUN interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2019_Spring!/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-2021spring | 東方外來韋編 2021 Spring! | Digital interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2021_Spring!/%E6%95%B0%E5%AD%97%E8%AE%BF%E8%B0%88) |
| gairai-2024 | 東方外來韋編 2024 | ZUN interview | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/2024/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-tenkuujo | 東方外來韋編 Vol.4 / Hidden Star interview | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E5%A4%A9%E7%A9%BA%E7%92%8B%E8%AE%BF%E8%B0%88) |
| gairai-kishinjo | 東方外來韋編 Vol.4 / MoF interview | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E8%82%86/%E9%A3%8E%E7%A5%9E%E5%BD%95%E8%AE%BF%E8%B0%88) |
| gairai-konjuden | 東方外來韋編 Vol.1 / LoLK interview | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E7%BB%80%E7%8F%A0%E4%BC%A0%E8%AE%BF%E8%B0%88) |
| gairai-shinpireku | 東方外來韋編 Vol.1 / UDoALG interview | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%A3%B1/%E6%B7%B1%E7%A7%98%E5%BD%95%E8%AE%BF%E8%B0%88) |
| gairai-ni-zun | 東方外來韋編 Vol.2 / ZUN interview | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%E8%AE%BF%E8%B0%88) |
| gairai-ni-zun-akiyama | 東方外來韋編 Vol.2 / ZUN×Akiyama | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E3%81%82%E3%81%8D%E3%82%84%E3%81%BE%E3%81%86%E3%81%AB) |
| gairai-ni-zun-umihara | 東方外來韋編 Vol.2 / ZUN×Umihara | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%BC%90/ZUN%C3%97%E6%B5%B7%E5%8E%9F%E6%B5%B7%E8%B1%9A) |
| gairai-san-books | 東方外來韋編 Vol.3 / Books stream | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E5%A4%96%E6%9D%A5%E9%9F%A6%E7%BC%96/%E5%8F%82/%E4%B9%A6%E7%B1%8D%E7%9A%84%E6%B5%81%E6%B4%BE) |
| th-fuujinroku | ZUN / MoF interview | | [View](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E9%A3%8E%E7%A5%9E%E5%BD%95%E9%87%87%E8%AE%BF) |
| th-chireiden | ZUN / SA interview | | [View](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%9C%B0%E7%81%B5%E6%AE%BF%E9%87%87%E8%AE%BF) |
| th-shinreibyou | ZUN / TD interview | | [View](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E7%A5%9E%E7%81%B5%E5%BA%99%E9%87%87%E8%AE%BF) |
| th-kishinchou | ZUN / DDC interview | | [View](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E8%BE%89%E9%92%88%E5%9F%8E%E9%87%87%E8%AE%BF) |
| th-yousei | ZUN / Fairy Wars interview | | [View](https://thbwiki.cc/ZUN/%E5%A6%96%E7%B2%BE%E5%A4%A7%E6%88%98%E4%BA%89%E9%87%87%E8%AE%BF) |
| pku | ZUN / Peking University interview | | [View](https://thbwiki.cc/ZUN/%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E9%87%87%E8%AE%BF) |
| weplay | ZUN / WePlay interview | | [View](https://thbwiki.cc/ZUN/WePlay%E9%87%87%E8%AE%BF) |
| ign | ZUN / IGN interview | | [View](https://thbwiki.cc/ZUN/IGN%E9%87%87%E8%AE%BF) |
| usgamer | ZUN / USgamer interview | | [View](https://thbwiki.cc/ZUN/USgamer%E9%87%87%E8%AE%BF) |
| reitaisai16 | ZUN / Reitaisai 16 interview | | [View](https://thbwiki.cc/ZUN/%E4%BE%8B%E5%A4%A7%E7%A5%AD16%E9%87%87%E8%AE%BF) |
| bougetsu | ZUN / Silent Sinner in Blue interview | | [View](https://thbwiki.cc/ZUN/%E4%B8%9C%E6%96%B9%E5%84%9A%E6%9C%88%E6%8A%84%E9%87%87%E8%AE%BF) |
| shujin-no-kotodama | Sangetsusei / The Word of the Master | | [View](https://thbwiki.cc/%E4%B8%9C%E6%96%B9%E4%B8%89%E6%9C%88%E7%B2%BE_%EF%BD%9E_Eastern_and_Little_Nature_Deity./%E7%A5%9E%E4%B8%BB%E7%9A%84%E8%A8%80%E7%81%B5) |
| shiguren-interview | Sangetsusei interview | GitHub Markdown source | [View](https://github.com/Delsin-Yu/THBWiki-Markdown) |
| nikenme-radio | Nikenme Radio | 91 episodes | [View](https://thbwiki.cc/2%E8%BB%92%E7%9B%AE%E3%81%8B%E3%82%89%E5%A7%8B%E3%81%BE%E3%82%8B%E3%83%A9%E3%82%B8%E3%82%AA/%E5%86%85%E5%AE%B9%E6%95%B4%E7%90%86) |

---

## Adding New Interview Data

Three methods for adding new ZUN interview data:

### Method 1: Add Local Quote Files (Simplest)

Organize quotes in Markdown format and place them in `references/quotes/`:

```markdown
- "Quote text 1"
- "Quote text 2"
- "Quote text 3"
```

`InterviewParser.parse_local_quotes()` handles the rest.

### Method 2: Add THBWiki / Other Web Interviews

Edit `scripts/config.py` and add entries to the `INTERVIEW_URLS` list:

```python
INTERVIEW_URLS = [
    # ... existing entries ...
    ("my-new-interview", "https://thbwiki.cc/your-interview-page-url"),
]
```

`InterviewParser` automatically tries all 7 HTML parsers — just give it a shot (laughs).

### Method 3: Add Markdown-Format Interviews

Edit `scripts/config.py` and add entries to the `GITHUB_INTERVIEWS` list:

```python
GITHUB_INTERVIEWS = [
    # ... existing entries ...
    ("my-md-interview", "https://raw.githubusercontent.com/.../interview.md"),
]
```

Markdown parsing supports `**ZUN**: answer` and `ZUN\n: answer` formats.

### Rebuild the Index

After adding new data, rebuild:

```bash
python3 scripts/cli.py --rebuild
```

### Add Custom Parsers

If a new interview's HTML structure isn't covered by the existing 7 parsers, add a new method to `InterviewParser` and append it to `ALL_PARSERS_HTML`:

```python
class InterviewParser:
    # ...
    
    def parse_my_custom_format(self, content: str, source_id: str) -> list:
        """Parser for custom format"""
        quotes = []
        # ... parsing logic ...
        return quotes

    ALL_PARSERS_HTML = [
        "parse_thbwiki_table",
        # ... existing parsers ...
        "parse_my_custom_format",  # Append here
    ]
```

---

## Honest Boundaries

Honestly, a Skill that doesn't tell you its limitations isn't worth trusting — probably (laughs).

**What this Skill can do:**
- Respond in ZUN's first-person style about Touhou, danmaku, creation, beer, etc.
- Semantically search real interview answers and questions via dual vector index
- Faithfully present his honest self-deprecating and casual expression

**What it cannot do:**

| Dimension | Note |
|-----------|------|
| Replace the person | ZUN's true thoughts and private life cannot be replicated |
| Latest info | New releases and recent interviews require web search |
| Lore authority | Won't give definitive lore explanations — "hard to say", "that kind of feeling" |
| Japanese originals | All quotes are Chinese translations, not Japanese originals |

---

## Repository Structure

```
zun-persona/
├── SKILL.md                          # ZUN persona core file (loaded on activation)
├── README.md                         # Chinese README
├── README_EN.md                      # This file (English)
├── README_JA.md                      # Japanese README
├── requirements.txt                  # Python dependencies
├── .gitignore
├── scripts/
│   ├── cli.py                        # CLI entry point (build/search/stats)
│   ├── config.py                     # Config constants (paths, URLs, speaker IDs)
│   ├── utils.py                      # QuoteFactory + HtmlCleaner
│   ├── parsers.py                    # InterviewParser (7 format parsers)
│   ├── crawler.py                    # InterviewCrawler (scraping with cache)
│   ├── indexer.py                    # VectorIndexer (dual vector index builder)
│   └── searcher.py                   # QuoteSearcher (2-stage semantic retrieval)
└── references/
    ├── works.md                      # Works chronology
    ├── life.md                       # Life timeline
    ├── quotes/                       # Quote files (vector index source)
    │   ├── creation.md               # Creation-related
    │   ├── philosophy.md             # Philosophy & Touhou worldview
    │   └── life-stories.md           # Life story fragments
    ├── raw_interviews/               # Raw interview cache
    │   └── SOURCES.md                # Interview file → source URL index
    └── vector_index/                 # Vector index data (pre-built)
        ├── quotes.json               # All quotes JSON (~500KB)
        └── chroma_db/                # ChromaDB vector index (zun_questions + zun_quotes)
```

---

## Command Reference

```bash
# Build index
python3 scripts/cli.py

# Force rebuild
python3 scripts/cli.py --rebuild

# View stats
python3 scripts/cli.py --stats

# Human-readable search
python3 scripts/cli.py --query "What do you think of Reimu"

# JSON search (for scripts)
python3 scripts/cli.py --search "Reimu" 5
```

---

## About ZUN

ZUN (Jun'ya Ōta, 1977—), from Nagano Prefecture, sole member of Team Shanghai Alice. The lone creator of the Touhou Project series — programming, writing, art, and music all done by one person for nearly three decades. Known for independent development and a permissive derivative works policy that created a dōjin culture miracle. Likes beer, dislikes hassle, and makes games for one reason — they're interesting.

---

## License

MIT — Use it, modify it, do whatever.

---

<div align="center">

**Quotes** tell you what he said.<br>
**ZUN Persona Skill** helps you see through his lens.<br><br>
*The ultimate goal is still to make danmaku interesting.*

<br>

MIT License © [qiwang999](https://github.com/qiwang999)

</div>
