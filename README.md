## FS-Researcher
This is the code repo for paper FS-Researcher (currently a minimal implementation, performance not guaranteed, complete code coming soon).

### Project layout

- `main.py`: CLI entrypoint (runs two agents: Stage 1 + Stage 2)
- `agent.py`: minimal ReAct-style agent + tool executor
- `tools.py`: tools including `search_web` (Google Serper), `read_webpage` (Jina AI Reader), and `FileTools` (local filesystem utilities)
- `prompts.py`: system prompts for Stage 1 / Stage 2
- `config.py`: local config (reads from environment variables first)
- `requirements.txt`: minimal dependencies

### Installation

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

