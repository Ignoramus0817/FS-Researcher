---
name: deep-research
description: Produce a comprehensive, well-cited, long-form research report on any topic by running a two-stage, file-based research workflow (build a structured knowledge base, then write a section-by-section report) backed by Jina AI web search and webpage reading. Use when the user asks for "deep research", "research report", "调研报告", "深度研究", when they provide a research topic/question that requires up-to-date web evidence and a multi-section written deliverable, or when they want an output comparable to Perplexity / GPT Deep Research / Gemini Deep Research.
---

# Deep Research (File-Based, Two-Stage)

This skill turns the host CLI agent (Cursor, Claude Code, etc.) into a deep-research agent that:

1. **Stage 1 — Knowledge Base Building.** Exhaustively gathers, archives, and distills web evidence into a structured `knowledge_base/` directory tree, tracked by an `index.md` master file. Runs for multiple rounds with a self-check loop.
2. **Stage 2 — Report Writing.** Drafts `report.md` one top-level section per round from an outline (`report_outline.md`), placing all citations in a single reference list at the end.

The goal is an information-dense, well-structured, fully-cited report whose evidence coverage is **at least as broad and deep** as what a dedicated agent harness would produce. Shortcuts (one-shot reports, shallow searches, fabricated citations) are forbidden — this skill is explicitly optimized for completeness and traceability over speed.

## When to use this skill

Apply this skill when the user asks for any of the following:

- A research report, industry analysis, competitive analysis, market study, policy brief, literature review, topic explainer, or "deep research" on a subject.
- A multi-section written output that must be supported by real web sources, with citations.
- A workspace-style task where context (notes, sources, drafts) must persist across rounds.

Do NOT use this skill for short Q&A, single-link summaries, coding tasks, or tasks where the user clearly expects a quick conversational answer.

## Prerequisites

- **Jina AI API key.** This skill uses Jina AI as the sole web search and webpage reading backend. Before running, ensure `JINA_API_KEY` is set in the environment. If it is not set, stop and ask the user to export it:

```bash
export JINA_API_KEY="jina_xxxxxxxxxxxxxxxxxxxxxxxx"
```

Rate limits are higher with an API key; without one the scripts still work but Jina will throttle to ~20 RPM.

- **File tools.** The skill relies on the host CLI agent's built-in file tools (read / write / edit / list / grep / glob). It does NOT ship file tools of its own.

- **Shell access.** Required for invoking the Jina helper scripts (`scripts/jina_search.sh`, `scripts/jina_read.sh`).

## Workspace layout (single source of truth)

Unless the user specifies otherwise, treat the current working directory as the research workspace. All artifacts are created at workspace root:

```
<workspace>/
├── index.md              # Stage 1 master index (topic breakdown + hierarchy + TODOs)
├── kb_log.md             # Stage 1 round-by-round log and self-check results
├── knowledge_base/
│   ├── sources/          # Archived full-text of every webpage ever read (raw evidence)
│   │   ├── <slug>.md
│   │   └── ...
│   └── <hierarchy>/      # Evidence notes organized by the Target Hierarchy in index.md
│       └── ...
├── report_outline.md     # Stage 2 outline with per-section status [TODO|IN-PROGRESS|COMPLETE]
├── report.md             # Stage 2 final report
└── report_log.md         # Stage 2 round log and self-check results
```

**Invariants** (treat these as hard rules):

- Every file under `knowledge_base/sources/` is the raw archive of exactly one webpage (written only by `jina_read.sh`). Never hand-edit files in this directory.
- Every evidence note under `knowledge_base/<hierarchy>/` cites one or more files in `knowledge_base/sources/` using relative paths.
- `report.md` only cites files in `knowledge_base/sources/` — never the evidence notes.
- Filenames are self-explaining. Forbidden: `notes.md`, `source_1.md`, `misc.md`, `tmp.md`.

## Tools at a glance

| Tool | How to call | Purpose |
|---|---|---|
| `scripts/jina_search.sh "<query>"` | shell | Search the web via Jina `s.jina.ai`. Returns top results (URL + title + content) as JSON. |
| `scripts/jina_read.sh "<url>" "<slug>"` | shell | Fetch full page via Jina `r.jina.ai`, save to `knowledge_base/sources/<slug>.md` with YAML frontmatter, and echo the full text to stdout. |
| Host agent file tools | built-in | `ls`, `read_file`, `write`, `edit`, `grep`, `glob` against the workspace. |

Both scripts read `JINA_API_KEY` from the environment. See `scripts/` for full contracts.

## The two-stage workflow

### At every round — orient first

Before taking any action in either stage:

1. List the workspace (top-level + `knowledge_base/` recursively, 2 levels).
2. If `index.md`, `kb_log.md`, `report_outline.md`, or `report.md` already exist, **read them in full**.
3. Decide which stage you are in:
   - No `index.md` → start Stage 1 round 1.
   - `index.md` exists but `kb_log.md` does NOT contain a line `[ALL COMPLETE]` → continue Stage 1.
   - `kb_log.md` contains `[ALL COMPLETE]` but `report_log.md` does not → Stage 2.
   - `report_log.md` contains `[ALL COMPLETE]` → the task is already done; confirm with the user before doing anything else.
4. Append `# Round N` header to the relevant log file (`kb_log.md` or `report_log.md`). `N` starts at 1 and increments each round.

### Stage 1 — Knowledge Base Building

**Objective:** build a broad, structured, self-explanatory knowledge base that alone could answer any reasonable question about the topic. The product is the populated `knowledge_base/` directory, NOT a narrative answer.

Round 1:

1. Create `index.md` with three sections: **Topic Deconstruction & Key Questions**, **Target Hierarchy** (a planned directory tree with one-sentence purpose for each node), and **TODOs** (granular `[TODO]` items, each tied to a concrete hierarchy node).
2. Fan out: run **2–5 `jina_search.sh` calls in parallel**, then **2–5 `jina_read.sh` calls in parallel** on the most promising URLs. Do not stop at search snippets — always archive the full page.
3. For each archived source, create or update an evidence note under `knowledge_base/<hierarchy>/<descriptive_name>.md` that distills facts, data, quotes, arguments, and methodologies, each cited to its source file. Evidence notes are the "meat"; `sources/` is the raw material.
4. Append a round summary to `kb_log.md` listing new URLs archived, notes created, and TODO status changes.

Round 2+:

1. Read `index.md` and `kb_log.md`. Focus on items still marked `[TODO]` or `[IN-PROGRESS]`, plus any gaps surfaced by the last round's self-check.
2. Reorganize the Target Hierarchy if new findings demand it (add new nodes, split overstuffed ones). Never silently delete prior entries — mark them superseded.
3. Continue fan-out searches and archives until the self-check (below) passes.

**Stage 1 exit criteria.** At the end of each round, answer the six self-check questions in `checklists.md`. When and only when all pass, append a line `[ALL COMPLETE]` to `kb_log.md` and proceed to Stage 2. Plan for at least **2 rounds**, expect **3 rounds** for most topics, and do not cap yourself artificially.

Read `stage1_kb_build.md` for the full convention (file format of `index.md`, citation syntax, source reliability tagging, archiving rules, edge cases).

### Stage 2 — Report Writing

**Objective:** produce `report.md`, a long-form, paragraph-first, fully-cited report.

Round 1 (outline only):

1. Read `index.md` and skim `knowledge_base/`.
2. Create `report_outline.md` with all top-level sections, each entry carrying `Key Question`, `Content`, and `Status: [TODO]`. The outline MUST include a `Key Takeaways` section (section 0) and a numbered set of main-body sections.
3. **Do not write any `report.md` content in round 1.** Stop after the outline.

Round 2+ (one H2 section per round):

1. Pick the first section in `report_outline.md` with status `[TODO]` or `[IN-PROGRESS]`.
2. Read `report_log.md` for any prior self-check failures on this section, then read the relevant knowledge base notes and sources.
3. Draft or revise that single H2 section in `report.md`. Append it; do not rewrite existing sections. Use H3 subsections where helpful.
4. Place every citation inline as `[N]` right after the claim it supports. Maintain a single `# References` section at the end of `report.md`, citing only files under `knowledge_base/sources/`. Merge duplicate citations to the same file under one index.
5. Run the section-level self-check (see `checklists.md`). Record the Q&A in `report_log.md` under `## Self-check for Section <n> ...`. Update the section's status in `report_outline.md` to `[COMPLETE]` (pass) or `[IN-PROGRESS]` (fail).
6. **Stop the round.** Do not start another section in the same round.

Final round (report-level audit): once every outline section is `[COMPLETE]`, read `report.md` top-to-bottom and run the report-level self-check. On pass, append `[ALL COMPLETE]` to `report_log.md` and stop. On fail, fix format issues directly and flip content-flawed sections back to `[IN-PROGRESS]` for another pass.

Read `stage2_report_writing.md` for the full convention (outline schema, report format rules, citation format, paragraph-first style guide, tables/bullets policy).

## Global principles (apply in both stages)

1. **Parallelism is mandatory.** Whenever you need more than one piece of evidence, issue search and read calls concurrently in the same tool batch. A "single search at a time" pattern is a quality failure.
2. **Archive first, summarize second.** Never distill information you have not first saved to `knowledge_base/sources/`. If a page is unreachable via Jina, log the URL in `kb_log.md` and move on — do not fabricate content.
3. **Read before edit.** Re-read a file with line numbers immediately before any line-range edit to avoid clobbering.
4. **Additive over destructive.** Prefer appending, splitting, or versioning to rewriting. When you must correct a wrong note, keep the original with a `[SUPERSEDED]` tag and link to the replacement.
5. **Match the topic's language.** If the user's topic is in Chinese, write `index.md`, notes, outline, and report in Chinese; keep filenames in lowercase English hyphen-separated slugs. Do NOT mix languages in the same section (e.g., Chinese Key Takeaways with English body) — pick one and use it consistently across headings, prose, and tables.
6. **Cite or kill.** Any concrete claim, number, name, date, or quote in an evidence note or in `report.md` must carry a citation. Uncited background sentences in the report are acceptable only for connective prose.
7. **Depth-over-thrift.** Do NOT throttle search/read calls to save Jina tokens. The only legitimate reason to stop fanning out in a round is (a) an explicit HTTP 429 / rate-limit error returned by `scripts/jina_search.sh` or `scripts/jina_read.sh`, or (b) the round's self-check is already a clean pass on every one of the six Stage-1 questions. "It probably has enough coverage" is NOT a valid stop condition. When in doubt, fan out one more batch. Design queries deliberately (2–4 complementary phrasings, mix languages when regional) but never trim the *number* of rounds, sources, or parallel reads to conserve budget.

## Quality bar (what "comparable to a dedicated harness" means)

The finished `report.md` should meet all of the following. These are **hard gates**, not soft targets — falling short of any one triggers another Stage-1 or Stage-2 round, never a shipped report.

- **Sources (hard floor):** at least **20 distinct files** under `knowledge_base/sources/` for a typical topic, **25–35** for broad / multi-aspect prompts. Counting rule: each file must be the archive of a *different* URL that actually contributes at least one cited claim to the report. Duplicates, near-duplicates of the same source, or archive files that are never cited do not count. Mix official, academic, industry, and reputable news; target at least 40 % High-reliability sources (see stage1_kb_build.md).
- **Length & structure:** typically 8–12 top-level sections plus Key Takeaways and References. **Paragraph-first**: every section opens with 1–3 narrative paragraphs of prose before any table or bullet list, and the section's overall ratio of prose to list must be ≥ 2:1 by line count. Tables are used for side-by-side comparisons and always carry a one-line caption. No orphan bullet lists pretending to be analysis.
- **Reader-friendly tone:** write for a smart, non-specialist reader. Every acronym is spelled out on first use; every piece of jargon is defined in 1–2 plain sentences before it is used as a noun; every number is framed by a sentence of interpretation ("what this means"), not dumped as a bare figure. Sections read like explanatory essays, not spec sheets.
- **Traceability (hard gate):** **every** number, date, name, quote, and non-trivial claim in `report.md` carries a `[N]` citation placed immediately after the claim. `[N]` resolves to a single `# References` block at the end of the file. Each entry in `# References` points to a file under `knowledge_base/sources/` — **never** to an evidence note, subfolder, or workspace-relative prose path. See `stage2_report_writing.md` §Citation rules for the exact format and the forbidden patterns.
- **Coverage:** every requirement explicitly stated in the user prompt is addressed in the report. Regional, temporal, and sub-topic breakdowns called for by the prompt must be present.
- **Honesty:** conflicts between sources are called out, not flattened; weak sources are cross-validated or labeled as such.

If any check fails, loop another round — do not ship early. The skill is optimized for completeness and auditability, not speed or token cost.

## Reference files

- `stage1_kb_build.md` — full Stage 1 convention, `index.md` schema, archiving and citation rules.
- `stage2_report_writing.md` — full Stage 2 convention, outline schema, report format and style rules.
- `checklists.md` — the six-question Stage 1 self-check and the section/report-level Stage 2 self-checks.
- `scripts/jina_search.sh`, `scripts/jina_read.sh` — Jina AI wrappers and their contracts.
