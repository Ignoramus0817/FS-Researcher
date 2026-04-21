# Stage 2 — Report Writing (full convention)

This file is the authoritative spec for Stage 2. SKILL.md gives the high-level flow; here we fix the outline schema, report format, citation format, and style rules.

## Task statement

Using the knowledge base produced in Stage 1, write a comprehensive, insightful, well-supported, and easy-to-follow research report in `report.md`. Every substantive claim must be traceable to a source file under `knowledge_base/sources/`. You work **one top-level section per round** — this is a hard constraint that prevents the single-round-dump failure mode.

## Round 1 — outline only

1. Read `index.md` and skim `knowledge_base/` (both the hierarchy and at least a sample of notes) to understand what evidence you actually have.
2. Create `report_outline.md` following the schema below. The outline MUST include a `Key Takeaways` section (section 0) and typically 6–12 numbered main-body sections that together cover every requirement in the user prompt.
3. Create `report_log.md` with a single line `# Round 1` plus a note that the outline was created.
4. **Do NOT create `report.md` in round 1. Do NOT write any section text.** Stop after the outline.

## Round 2+ — one H2 section per round

Each round writes exactly one top-level `##` section.

1. Read `report_outline.md`. Pick the **first** section whose status is `[TODO]` or `[IN-PROGRESS]`.
2. Read `report_log.md` for any prior self-check failures on this section.
3. Read `index.md` to locate the relevant parts of the KB, then open the specific notes and sources you need.
4. Draft or revise the section in `report.md`:
   - Append new content with your agent's edit tool, anchored to the end of the file. Do NOT rewrite existing sections in the same round.
   - If `report.md` does not yet exist, create it with `# <Report Title>` as line 1, then your first section.
   - Finish the whole H2 section in one round. Use H3 subsections where appropriate, but avoid H4+.
5. Maintain a single `# References` section at the end of `report.md`. Every `[N]` in the body resolves to exactly one entry pointing to a file under `knowledge_base/sources/`. Merge duplicates — one source = one index.
6. Run the section-level self-check (see `checklists.md`). Write the Q&A to `report_log.md` under `## Self-check for Section <n> - <title>`. Flip the section status in `report_outline.md` to `[COMPLETE]` (all pass) or `[IN-PROGRESS]` (any fail, keep notes on what's missing).
7. **Stop the round immediately.** Do not start another section even if you "feel" you have capacity. Leaving sections for future rounds is the correct behavior.

## Final round — report-level audit

When every section in `report_outline.md` is `[COMPLETE]`:

1. Read the full `report.md` end-to-end.
2. Run the report-level self-check (see `checklists.md`). Write the Q&A to `report_log.md` under `## Report-level Self-check`.
3. **On pass:** directly fix any small format issues you spotted (stray blank lines, duplicated titles, heading level mistakes, misnumbered references). Then append a line `[ALL COMPLETE]` to `report_log.md` and stop.
4. **On fail:** fix format issues in `report.md` directly. For any section with content issues, flip its status in `report_outline.md` to `[IN-PROGRESS]` with a one-line note on what to fix, and continue into another Stage 2 round.

## `report_outline.md` schema

One block per section, in order. Each block has exactly four fields:

```
## <N>. <Section Title>
- **Key Question**: <the single most important question this section answers>
- **Content**: <1–3 sentences describing what will be in the section, concretely>
- **Status**: [TODO]
```

Required sections:

- `## 0. Key Takeaways` (section 0) — always present.
- Main-body sections numbered starting at 1, covering every requirement in the user prompt. Pull structure cues directly from the prompt — if the user asks for comparison across regions, have a regional section; if they ask for a forecast, have a forecast section; etc.
- Optional concluding sections (e.g., Risks & Outlook, Recommendations) as the prompt suggests.

The outline is the **single source of truth** for report structure. If you discover mid-report that a new section is needed, add it to `report_outline.md` first (as `[TODO]`) and write it in a later round.

Status options:

- `[TODO]` — not drafted.
- `[IN-PROGRESS]` — partially drafted, or drafted but failed self-check.
- `[COMPLETE]` — drafted and passed section-level self-check.

## `report.md` format

### Overall structure

```
# <Report Title>

## 0. Key Takeaways
<paragraph-first takeaways, optionally with bold highlights>

## 1. <First Main Section>
<paragraphs + tables + citations>

### 1.1 <Optional subsection>
...

## 2. <Second Main Section>
...

## <N>. <Last Main Section>
...

# References
[1] /knowledge_base/sources/<slug-1>.md
[2] /knowledge_base/sources/<slug-2>.md
...
```

### Markdown rules

- Hierarchical numbering on titles: `## 1.`, `### 1.1`, `### 1.2`, `## 2.`, etc.
- Use `##` for top-level sections, `###` for subsections. Avoid `####` and deeper.
- Two blank lines between top-level sections, one blank line between paragraphs.
- No stray headings, duplicate titles, or nested code fences.

### Citation rules — mandatory `[N]` format

This is the single most common source of skill failures. Read it carefully.

**Required format.** Inline citations use bracketed integer indices, `[1]`, `[2]`, `[12]`, placed **immediately after the specific claim**, never at the end of a paragraph. If one sentence draws from two sources, write `[1][2]`. Example:

> China's urban disposable income per capita reached 54,188 yuan in 2024, up 4.4 % YoY [1]. An independent household survey places the real-estate share of urban household assets near 67 % [2], a figure McKinsey revises down to 59 % [3].

The `# References` block sits as the **single last block** of `report.md`. Each entry is of the form:

```
# References

[1] knowledge_base/sources/nbs-china-income-2024.md
[2] knowledge_base/sources/pboc-household-assets-2019.md
[3] knowledge_base/sources/mckinsey-china-consumer-2024.md
```

Deduplicate: if two claims cite the same file, both use the same index; the file appears once in References, in order of first use.

**Forbidden citation patterns.** Any occurrence of these in `report.md` is a skill violation and must be fixed before marking the section `[COMPLETE]`:

1. **Inline relative paths** — e.g., ``... NBV grew 29.3 % `knowledge_base/sources/dfcfw-pingan-2024-annual-review.md#L93` `` or ``... see ../sources/x.md``. Inline paths are the Stage-1 evidence-note convention; they never appear in `report.md`. Replace with `[N]` pointing to the file.
2. **Citing evidence notes** — e.g., `[4] knowledge_base/comparative_analysis/financing_comparison.md` or `[5] knowledge_base/company_profiles/ping_an/...`. Evidence notes live under `knowledge_base/<hierarchy>/` and are internal scratch. Re-thread the citation to the underlying `sources/` file(s) the evidence note itself cites.
3. **Per-section reference lists** — all references live in one `# References` block at the end, never under each section.
4. **Bare URLs or prose citations** — e.g., `(Reuters, 2024)` or `https://example.com/...`. If the page is worth citing, it must already be archived in `knowledge_base/sources/` with its own slug file; cite that slug file via `[N]`.
5. **Dangling indices** — every `[N]` appearing in the body must have a matching entry in `# References`, and every entry in `# References` must be cited at least once in the body.

If any forbidden pattern is present, the section-level self-check (see `checklists.md`) fails automatically; the agent must fix the citations in-place before moving on to the next section.

### Style — narrative-first, reader-friendly writing

The report is explicitly optimized to read like a well-written explanatory essay, not a spec sheet. Every H2 section must obey the following:

- **Open with narrative, not a table.** Every H2 section begins with **1–3 paragraphs of prose** (roughly 120–300 words) that: (a) orient the reader to what the section is about and why it matters for the user's prompt, (b) preview the shape of the argument, (c) introduce any term of art that will be used. Only after this narrative opening may a table or bulleted list appear.
- **Paragraphs do the analytic work.** Analysis, argument, comparison, and "so what" live in prose. A section consisting mostly of tables or bullets with a thin layer of prose between them is a failure.
- **Tables complement, not replace, prose.** Tables are reserved for side-by-side comparisons, structured numeric data, or before/after contrasts. Every table has a one-line caption on the line above. Every table is followed by **at least one paragraph** interpreting what the numbers mean in plain language.
- **Bullet points** are reserved for short enumerable lists (pros/cons, options, roadmap steps). Cap bullets at 6 items and 2 levels of nesting; if you need more, restructure as a paragraph or table.
- **Section ratio.** Within each H2, the line count of prose paragraphs must be **≥ 2× the line count of tables + bullet lists combined**. Key Takeaways is the only allowed exception (it may be bullet-heavy, but must open with one short paragraph).

### Style — clarity, rigor, and accessibility

- Write for a smart, non-specialist reader. Define any jargon in 1–2 plain sentences on first use. Spell out acronyms on first use (e.g., "Filtered-x Least-Mean-Squares (FxLMS)").
- Frame every number with meaning. Do not write bare values like "158 mA peak at 35 Hz [7]" — write "driving the 5-µF stack to 150 V peak-to-peak at 35 Hz demands 158 mA of peak current [7], which is why amplifier sizing scales with actuator capacitance and not just voltage."
- **Present original data first.** When comparing ("Brand A has better margins than Brand B"), give the actual margin values before the comparative claim.
- Call out conflicts between sources rather than flattening them. Phrase disagreements explicitly ("McKinsey estimates 4 million [7]; Hurun reports 1.6 million [8]; the gap stems from differing asset thresholds.").
- Use signposting prose ("Having established the hardware floor, we now turn to…", "The picture changes once thermal drift is accounted for…") to stitch sections together.
- Avoid long noun chains, unexplained acronyms, and list-of-specs-without-story writing.
- Do not fabricate numbers to fill gaps. If the KB lacks data, either launch another Stage 1 round or flag the gap in the section explicitly.

## Common failure modes and how to avoid them

- **Single-round dump.** Writing all sections in one round always lowers quality — the model rushes, citations get sloppy, and self-check becomes perfunctory. Enforce the one-section-per-round rule unconditionally, even if the section is short.
- **Inline-path citations leaking from Stage 1.** Patterns like ``... reached 14.8 % `knowledge_base/sources/aerotech-piezo-tutorial.md#L53` `` are the Stage-1 evidence-note convention and are forbidden in `report.md`. Convert every such inline path to a `[N]` index with a matching entry in the final `# References` block. Grep the report for the strings `knowledge_base/sources/`, `../sources/`, and backtick-delimited `.md` paths before closing any section — every hit must be replaced.
- **Citing evidence notes instead of sources.** If you find `[N] /knowledge_base/market_landscape/xyz.md` or similar in References, that's a bug. Open the evidence note, find the underlying `sources/*.md` it cites, and thread the `[N]` to those sources directly. The final References block must contain zero paths outside `knowledge_base/sources/`.
- **Dangling references / orphan entries.** Every `[N]` in the body must appear in `# References`, and every entry in `# References` must be cited at least once. Grep for `\[\d+\]` and cross-check both directions before declaring a section complete.
- **Thematic reference grouping.** The References block must be a flat `[1]…[N]` numbered list. Any variant that groups sources under sub-headings ("**行业排名**", "**公司财报**", "**信用评级**", etc.) is a violation; flatten them into a single numbered list in order of first use.
- **Shadow outlines.** Keep `report_outline.md` and `report.md` in sync. If you rename or merge sections in `report.md`, update the outline immediately.
- **Silent destructive edits.** Prefer append-based edits over range-replace. If you must replace an existing block, re-read the file first so line numbers are correct, and keep the edit narrow.
- **Cramming everything into Key Takeaways.** Takeaways summarize 4–8 highest-priority findings. Full reasoning and numbers belong in the main body.
- **Language mixing.** Pick Chinese or English (matching the user's prompt) and use it consistently across section headings, prose, tables, and Key Takeaways. Do not write a Chinese Key Takeaways section on top of an English body, or vice versa.

## Section-level self-check

Before marking a section `[COMPLETE]`, answer in `report_log.md`. **If any answer is "No", the section status flips to `[IN-PROGRESS]` and must be fixed in the next round (or in-place, for format issues) before the agent can move on.**

**Content**
- Is the section's Key Question actually answered? Is the outlined Content covered?
- Does the section explain the "so what" for each fact, rather than just listing facts?

**Formatting & style**
- Does the section open with 1–3 paragraphs of prose (not a table or bullet list)?
- Is the prose-to-list ratio within the section ≥ 2:1 by line count (Key Takeaways exempt)?
- Is every table preceded by a one-line caption and followed by at least one paragraph of interpretation?
- Is the language clear, jargon defined, abbreviations spelled out on first use?
- Are heading levels, blank lines, and list indents correct?

**Traceability (hard gates — any "No" auto-fails the section)**
- Does every concrete claim (numbers, names, dates, quotes) carry a `[N]` citation placed immediately after the claim?
- Does the section contain **zero** inline relative paths like `` `knowledge_base/sources/x.md` `` or `` `../sources/x.md` `` used as citations?
- Is every `[N]` in the section present in the single `# References` block, pointing to a file under `knowledge_base/sources/...` (and not to an evidence note at `knowledge_base/<hierarchy>/...`)?
- Do all `[N]` indices in the section resolve to an archive file that actually exists (verify by listing `knowledge_base/sources/`)?

## Report-level self-check

**Integrity**
- Does `report.md` exist and is non-empty? Does it contain Key Takeaways, Main Body, and References?
- Do all sections listed in `report_outline.md` appear in `report.md`, in the same order?
- Are markdown headings, blank lines, and indents correct throughout?

**Coverage**
- List every requirement and question from the user prompt. Is each addressed somewhere in the report?
- If the prompt implies a time-horizon / roadmap view, is there one with clear, unambiguous steps?
- Regional / stakeholder / sub-topic breakdowns implied by the prompt — are they present?

**Format**
- Is `# References` a single block at the end of the file? No per-section reference lists?
- Is each source cited only once in `# References` (no duplicate entries)?
- Do all reference targets resolve to files that actually exist under `knowledge_base/sources/`?
