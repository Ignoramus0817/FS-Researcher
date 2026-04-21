# Self-check Checklists

Copy these blocks verbatim into `kb_log.md` or `report_log.md` at the end of each round. Answer each question with a clear **Yes / No + one-line justification**. A checklist only "passes" when every answer is Yes.

---

## Stage 1 — end-of-round self-check

Copy into `kb_log.md` under `## Self-check for Round <N>`.

```
1. Tasks complete — is every `[TODO]` in `index.md` now `[COMPLETE]`?
   Answer:

2. Hierarchy match — does the `knowledge_base/` directory exactly mirror the Target Hierarchy in `index.md`?
   Answer:

3. No placeholders — are all filenames self-explaining and specific (no `notes.md`, `source_1.md`, `misc.md`, etc.)?
   Answer:

4. Full traceability — does every evidence note cite its source file(s) under `knowledge_base/sources/` using relative paths?
   Answer:

5. Exhaustive coverage — can you think of a reasonable question about the topic the KB cannot answer? Any missing regional / temporal / stakeholder-specific angles? Any claims supported by only 1–2 weak sources?
   Answer:

6. Information density — open a random evidence note. Does it contain specific data, numbers, quotes, and methodologies, or only vague summaries?
   Answer:

7. Archive floor met — does `knowledge_base/sources/` contain ≥ 20 distinct, cited archives (≥ 25 for broad / multi-aspect topics), and does every sub-topic in the Target Hierarchy have ≥ 3 dedicated sources?
   Answer:
```

**Pass:** append `[ALL COMPLETE]` to `kb_log.md` and move to Stage 2.
**Fail:** convert each "No" into one or more concrete `[TODO]` items in `index.md`, then plan another round. A "No" on Q7 is never waived for budget reasons; if Jina is not returning HTTP 429, keep fanning out.

---

## Stage 2 — section-level self-check

Copy into `report_log.md` under `## Self-check for Section <N> — <title>` at the end of each section-writing round.

```
Content
1. Is the section's Key Question actually answered? Is the outlined Content covered end-to-end?
   Answer:

2. Does each fact group carry a clear "so what" interpretation, rather than being a bare listing?
   Answer:

Formatting & style
3. Does the section open with 1–3 paragraphs of prose before any table or bullet list?
   Answer:

4. Is the section's prose-to-list ratio ≥ 2:1 by line count (Key Takeaways exempt), and is every table both preceded by a one-line caption and followed by ≥ 1 paragraph of interpretation?
   Answer:

5. Is the language clear, with jargon defined and abbreviations spelled out on first use?
   Answer:

6. Are markdown headings, blank lines, and indents correct? No duplicate titles or stray artifacts?
   Answer:

Traceability (hard gates — any "No" here must be fixed in-place before marking the section [COMPLETE])
7. Does every concrete claim (numbers, names, dates, quotes) carry a `[N]` citation placed immediately after the claim?
   Answer:

8. Does the section contain ZERO inline relative-path citations (e.g., `` `knowledge_base/sources/x.md` ``, `` `../sources/x.md#L12` ``, or bare URLs used as citations)?
   Answer:

9. Is every `[N]` used in the section already present in the single `# References` block at the end of `report.md`, and does every one of those entries point to a file under `knowledge_base/sources/` (NOT to an evidence note under `knowledge_base/<hierarchy>/`)?
   Answer:

10. Does every `[N]` resolve to an archive file that actually exists (verify by listing `knowledge_base/sources/`)?
    Answer:
```

**Pass:** flip the section status in `report_outline.md` to `[COMPLETE]`, stop the round.
**Fail on any Content / Formatting question:** flip to `[IN-PROGRESS]` with a one-line note on what to fix. Continue into another round to revise this section.
**Fail on any Traceability question (7–10):** do NOT leave the section as-is. Fix the citation format in-place in the same round (replace inline paths with `[N]`, re-thread evidence-note references to the underlying sources, remove orphans, add missing entries to `# References`). Only after the four Traceability questions all pass may the section be marked `[COMPLETE]`.

---

## Stage 2 — report-level self-check

Copy into `report_log.md` under `## Report-level Self-check` once every outline section is `[COMPLETE]`.

```
Integrity
1. Does `report.md` exist and is non-empty? Does it contain Key Takeaways, Main Body, and References?
   Answer:

2. Do all sections listed in `report_outline.md` appear in `report.md`, in the same order?
   Answer:

3. Are markdown headings, blank lines, indents, and numbering consistent throughout?
   Answer:

Coverage
4. Listing every requirement and question in the user prompt, is each one addressed somewhere in the report?
   Answer:

5. If the prompt implies a time-horizon / roadmap / forecast view, is there one with clear, unambiguous steps?
   Answer:

6. Are all regional / stakeholder / sub-topic breakdowns implied by the prompt present?
   Answer:

Format & citations (hard gates)
7. Is `# References` a single flat numbered block at the end of the file (no per-section reference lists, no thematic sub-groupings like "**Company filings**" or "**行业排名**")?
   Answer:

8. Does each source appear only once in `# References` (duplicate citations merged to the same index)?
   Answer:

9. Do ALL reference targets resolve to files that actually exist under `knowledge_base/sources/`, and does NONE of them point to an evidence note at `knowledge_base/<hierarchy>/`?
   Answer:

10. Grep the whole body of `report.md` for the strings `knowledge_base/sources/`, `../sources/`, and backtick-delimited `.md` paths — is the count zero (i.e., no inline-path citations leaked from Stage 1)?
    Answer:

11. Does `report.md` language match the user's prompt language consistently across all sections (no Chinese Key Takeaways over an English body, or vice versa)?
    Answer:

Depth
12. Is the total count of archives in `knowledge_base/sources/` at least 20 (25 for broad / multi-aspect prompts), and are all of them cited at least once in `report.md`?
    Answer:
```

**Pass:** fix any small formatting issues directly, append `[ALL COMPLETE]` to `report_log.md`, stop.
**Fail on Integrity / Coverage / Depth:** fix formatting issues directly. Flip content-flawed sections back to `[IN-PROGRESS]` in `report_outline.md` with a one-line note per flaw. Continue into another Stage 2 round. A "No" on Q12 also requires going back to Stage 1 for another round of archiving.
**Fail on Format & citations (7–11):** these are hard gates. Fix them in-place in the same round — do not ship the report until every one reads Yes.
