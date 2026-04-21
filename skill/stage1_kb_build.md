# Stage 1 — Knowledge Base Building (full convention)

This file is the authoritative spec for Stage 1. SKILL.md gives the high-level flow; here we fix the exact file schemas, citation syntax, and edge cases.

## Task statement

Perform exhaustive information gathering to construct a broad, structured, self-explanatory knowledge base about the user-provided topic. Act as a digital archivist and librarian. **The deliverable is the populated `knowledge_base/` directory, not an answer.** The report comes later in Stage 2.

## Round 1 — bootstrap

At round 1, you start from an empty workspace. Do these in order:

1. **Create `kb_log.md`** with a single line `# Round 1`.
2. **Create `index.md`** with the three mandatory sections below (Topic Deconstruction, Target Hierarchy, TODOs). It is OK for the hierarchy to be a rough draft — you will refine it each round.
3. **Fan out searches.** Issue **at least 4 `jina_search.sh` calls in parallel** (typical 4–6) using complementary queries:
   - Synonyms / aliases / local-language equivalents for the topic.
   - Sub-questions from the deconstruction.
   - Queries biased toward authoritative sources (e.g., append `site:gov.cn`, `官方`, `白皮书`, `annual report`, `filing`, `官方数据`, language of the topic).
   - If the topic is regional, query in the local language and in English.
4. **Fan out reads.** From the search results, pick the most promising URLs and issue **at least 6 `jina_read.sh` calls in parallel in round 1** (typical 8–12), then keep fanning out in subsequent batches within the same round until you have added **at least 8 distinct new archives to `knowledge_base/sources/` by the end of round 1**. Prefer:
   - Official / primary sources (company IR, government statistics, standards bodies).
   - Academic papers and survey articles.
   - Reputable industry publications and analyst reports.
   - Avoid paywalled pages that return empty content and social-media home pages.
5. **Write evidence notes** under `knowledge_base/<hierarchy>/<descriptive_name>.md`, one per coherent chunk of distilled evidence. Each note cites one or more files under `knowledge_base/sources/` (the slug passed to `jina_read.sh`).
6. **Append a round summary** to `kb_log.md` describing new URLs archived, notes created, TODO status updates, and any gaps observed. Do NOT mark `[ALL COMPLETE]` yet — run the self-check first.
7. **Run the Stage 1 self-check** (see `checklists.md`). Record answers in `kb_log.md` under a `## Self-check for Round 1` header. If all six questions pass, append the exit marker `[ALL COMPLETE]` on its own line. Otherwise convert failed items into `[TODO]` entries in `index.md` for the next round.

## Round 2+ — refine and deepen

1. Read `index.md` and `kb_log.md` in full.
2. Identify items with status `[TODO]` or `[IN-PROGRESS]`. If the last self-check flagged missing regional breakdowns, weak sources, vague notes, etc., list those as explicit targets for this round.
3. If new findings demand it, update the Target Hierarchy (add/split nodes, keep existing ones; never silently delete). Update wording of TODOs in place rather than creating a new "Round 2 TODOs" section.
4. Fan out searches and reads as in round 1, focused on the gap list. Each round after round 1 must add **at least 5 new archives** to `knowledge_base/sources/` unless Jina returns HTTP 429 / rate-limit errors; otherwise the round is considered insufficient and must continue.
5. Revise or extend evidence notes. When correcting a wrong note, keep the original with a `[SUPERSEDED]` marker and a link to the replacement file.
6. Append `# Round N` + round summary + self-check to `kb_log.md`.
7. Continue until the self-check passes AND the total archive count meets the Quality-bar floor in `SKILL.md` (≥ 20 for typical topics, 25–35 for broad ones).

Plan for **≥ 2 rounds**; **3 rounds** is typical. Do not force `[ALL COMPLETE]` just because a round budget is exhausted — if important gaps remain, leave them as explicit `[TODO]` and keep going.

## Depth-over-thrift (no budget-saving)

The skill is intentionally not cost-optimized. Unless a Jina call returns HTTP 429 or an explicit rate-limit message, treat the token budget as unconstrained:

- Never stop fanning out "because it's probably enough" — stop only when the self-check is a clean pass on all six questions AND the archive floor is met.
- Never collapse 2–5 parallel searches down to 1 for speed; parallelism is the whole point.
- If a batch of reads returns mostly empty or low-quality pages, immediately issue another batch with different queries rather than waiting for the next round.
- If the topic is cross-disciplinary (e.g., piezo isolation = mechatronics + control + manufacturing + quality management), ensure every sub-discipline has **≥ 3 dedicated sources** before declaring Stage 1 complete, even if that pushes the archive well past 30 files.

## `index.md` schema

`index.md` has exactly three mandatory sections, in this order.

### 1. Topic Deconstruction & Key Questions

Break the topic into problem-driven sub-topics. Prefer **questions** and **hypotheses** over noun labels. For each sub-topic list:

- Specific data needed (numbers, dates, names, ratios).
- Known debates / conflicts (e.g., "Market size — McKinsey vs BCG estimates").
- Information gaps (what is NOT yet known).

### 2. Target Hierarchy

An ASCII tree of the planned `knowledge_base/` structure. Each directory and leaf file gets a **one-sentence purpose comment** in parentheses. Two kinds of branching:

- **Breadth:** angles, stakeholders, organizations, data sources.
- **Depth:** problem-driven paths (e.g., `pressures_and_challenges/housing_burden.md`) — not just entity-level classification.

Every leaf is a concrete evidence note, never an abstract direction. Example:

```
workspace_root/
├── knowledge_base/
│   ├── sources/                         (raw archives, auto-managed)
│   └── market_landscape/                (market size, players, dynamics)
│       ├── market_size_2024.md          (market size estimates, growth rates)
│       ├── key_players_overview.md      (top 10 players by revenue)
│       └── regional_breakdown/
│           ├── china_market.md          (China-specific sizing and growth)
│           └── us_market.md             (US-specific sizing and growth)
```

Forbidden filenames: `notes.md`, `misc.md`, `source_1.md`, `temp.md`, `foo.md`.

### 3. TODOs

A flat, detailed checklist. Each item has exactly one status: `[TODO]`, `[IN-PROGRESS]`, or `[COMPLETE]`. Tie each to a concrete hierarchy node. Examples:

```
- [TODO] Populate market_landscape/market_size_2024.md with at least two independent 2024 estimates.
- [IN-PROGRESS] Collect regulatory timeline for regional_breakdown/china_market.md (have 2022, need 2023+2024).
- [COMPLETE] Archive the company's 2024 annual report.
```

It is normal for the TODO list to grow as you learn. Add new items when new sub-questions emerge.

## `knowledge_base/sources/` — the raw archive

**Written only by `scripts/jina_read.sh`.** Do not hand-edit. Each file has this shape:

```
---
url: <canonical url>
title: <page title, if any>
fetched_at: <ISO-8601 timestamp>
---

<full markdown body returned by Jina Reader>
```

Slug naming: lowercase, hyphen-separated, topic-reflective, no dates unless the page is version-specific. Examples: `tesla-q3-2024-earnings`, `nbs-china-income-quintiles-2024`, `mckinsey-china-consumer-2024`.

If a URL fails to fetch (empty content, timeout), DO NOT write a placeholder file. Log the URL + failure reason in `kb_log.md` and pick a different source.

## Evidence notes — the "meat"

Evidence notes live under `knowledge_base/<hierarchy>/*.md` and are the primary building blocks for the report. Content requirements:

- **Key data & statistics** — copy relevant tables and numbers exactly.
- **Direct quotes** — preserve important statements verbatim from experts, officials, or primary documents.
- **Arguments & counter-arguments** — record the core reasoning, not just the topic.
- **Methodologies** — note how a conclusion was reached (sample size, assumptions).
- **Comparisons** — if the source compares A vs B, keep the comparison details intact.

Avoid vague summaries. If you find yourself writing "this source discusses X", fetch again and extract specifics.

### Citation format inside notes

Use bracketed indices that resolve to a `References` block at the end of the note. The reference target is a relative workspace path to a file under `knowledge_base/sources/`. Tag document type and reliability.

```
China's urban disposable income per capita reached 54,188 yuan in 2024, up 4.4% YoY [1].
Household asset surveys show real estate accounts for ~67% of urban household assets [2], a figure McKinsey puts slightly lower at ~59% [3].

## References
[1] /knowledge_base/sources/nbs-china-income-2024.md
    - Type: Official Statistics
    - Reliability: High
[2] /knowledge_base/sources/pboc-household-assets-2019.md
    - Type: Central Bank Survey
    - Reliability: High (note: 2019 data; cross-validate with [3])
[3] /knowledge_base/sources/mckinsey-china-consumer-2024.md
    - Type: Industry Report
    - Reliability: Medium
```

Reliability guidance:

- **High** — official / primary sources, standards bodies, peer-reviewed papers, audited filings.
- **Medium** — reputable industry/analyst reports, mainstream news with named reporters.
- **Low** — blogs, forums, social media. Always cross-validate and tag as such; prefer not to rely on Low sources alone.

## Source selection and freshness

- **Source priority:** Official/primary > top-tier publishers/academic > reputable industry > aggregators/blogs.
- **QDF (Query Deserves Freshness):**
  - Breaking news / events: ≤ 72 hours.
  - Product / docs / pricing: ≤ 6–12 months.
  - Surveys / benchmarks: ≤ 18 months unless explicitly historical.
- **Cross-check** dates (event vs publication), definitions, and metrics. Never report predictions as facts.

## Failure modes to avoid

- Writing an evidence note with no citation, or citing a source you haven't archived.
- Reading only the first page of search results — low recall causes one-sided reports.
- Stopping at search snippets without archiving full pages — snippets miss numbers and context.
- Creating placeholder files for unreachable URLs.
- Running searches sequentially instead of in parallel — slows the round 5–10x with no benefit.
- Marking `[ALL COMPLETE]` while any self-check question still has a "no" answer.
- Filenames like `notes.md`, `source_1.md`, `other.md`.

## Stage 1 self-check (runs at the end of every round)

Answer all seven in `kb_log.md` under `## Self-check for Round N`:

1. **Tasks complete** — is every `[TODO]` in `index.md` now `[COMPLETE]`?
2. **Hierarchy match** — does the `knowledge_base/` directory exactly mirror the Target Hierarchy in `index.md`?
3. **No placeholders** — are all filenames self-explaining and specific?
4. **Full traceability** — does every evidence note cite its source file(s) under `knowledge_base/sources/`?
5. **Exhaustive coverage** — can you think of a reasonable question about the topic the KB cannot answer? Any missing regional / temporal / stakeholder-specific angles? Any claims supported by only 1–2 weak sources?
6. **Information density** — open a random note. Does it contain specific data/facts, or just vague summaries? If vague, fetch again and extract details.
7. **Archive floor met** — does `ls knowledge_base/sources/ | wc -l` return **≥ 20 for a typical topic** or **≥ 25 for broad / multi-aspect prompts**? If not, list what sub-topics still lack ≥ 3 dedicated sources and carry them into next round.

Only when all seven are a clean "yes" do you append `[ALL COMPLETE]` to `kb_log.md` and move to Stage 2. A "no" on question 7 is never waived for budget reasons — add another round.
