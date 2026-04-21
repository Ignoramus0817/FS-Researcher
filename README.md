## FS-Researcher
This is the code repo for paper [FS-Researcher](https://arxiv.org/abs/2602.01566) (accepted by ACL 2026).

> **Recommended: use the [`skill/`](./skill) directory.** The `skill/` folder packages the FS-Researcher workflow as a ready-to-use [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills) that can be loaded directly by agent harnesses such as Claude Code, Cursor CLI, etc. It produces the highest-quality reports and is the preferred entry point for most users. The standalone Python implementation below is kept as a minimal reference.

### Project layout

- `skill/`: **(recommended)** Agent Skill package (`SKILL.md`, stage playbooks, checklists, helper scripts) — plug into any skill-compatible agent harness to run the full two-stage deep-research workflow.
- `main.py`: CLI entrypoint (runs two agents: Stage 1 + Stage 2)
- `agent.py`: minimal ReAct-style agent + tool executor
- `tools.py`: tools including `search_web` (Google Serper), `read_webpage` (Jina AI Reader), and `FileTools` (local filesystem utilities)
- `prompts.py`: system prompts for Stage 1 / Stage 2
- `config.py`: local config (reads from environment variables first)
- `requirements.txt`: minimal dependencies

### Recommended usage: load as a skill

Point your agent harness (Claude Code, Cursor CLI, or any skill-compatible client) at the `skill/` directory and invoke it with a research topic. See [`skill/SKILL.md`](./skill/SKILL.md) for prerequisites (Jina AI API key) and the full workflow specification.

### Installation (standalone Python implementation)

Create a virtual environment if you prefer, then:

```bash
pip install -r research_agent/requirements.txt
```

### Configuration (environment variables)

- **OpenAI-compatible API**
  - `OPENAI_API_KEY`: required
  - `OPENAI_API_BASE`: optional, defaults to `https://api.openai.com/v1`
  - `LLM_MODEL`: optional, defaults to `gpt-5`

- **Tools**
  - `SERPER_API_KEY`: Google Serper key (used by `search_web`)
  - `JINA_API_KEY`: Jina Reader key (used by `read_webpage`, optional)

### Run

From the repository root:

```bash
python -m research_agent.main --topic "your research topic" --workspace ./workspace_demo
```

You can also copy the entire `research_agent/` folder into another project and run it from its parent directory:

```bash
python -m research_agent.main --topic "your research topic"
```

