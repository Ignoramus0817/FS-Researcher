"""
Agent implementation for Research Agent Minimal
A simple ReAct-style agent with tool use
"""
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import openai

# Compatibility:
# - Supports `python -m research_agent_minimal.main` (package-relative imports)
# - Also supports running after the folder is copied elsewhere (fallback absolute imports)
try:
    from .config import (
        LLM_API_KEY,
        LLM_API_BASE,
        LLM_MODEL,
        MAX_OUTPUT_TOKENS,
    )
    from .tools import (
        FileTools,
        WebSearchTool,
        WebPageReaderTool,
        normalize_url,
        TOOL_DEFINITIONS_STAGE1,
        TOOL_DEFINITIONS_STAGE2,
    )
    from .prompts import get_system_prompt_stage1, get_system_prompt_stage2
except Exception:  # pragma: no cover
    from config import (  # type: ignore
        LLM_API_KEY,
        LLM_API_BASE,
        LLM_MODEL,
        MAX_OUTPUT_TOKENS,
    )
    from tools import (  # type: ignore
        FileTools,
        WebSearchTool,
        WebPageReaderTool,
        normalize_url,
        TOOL_DEFINITIONS_STAGE1,
        TOOL_DEFINITIONS_STAGE2,
    )
    from prompts import get_system_prompt_stage1, get_system_prompt_stage2  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Tool Executor
# =============================================================================

class ToolExecutor:
    """Executes tools and manages workspace state."""
    
    def __init__(self, workspace_dir: str):
        self.fs = FileTools(workspace_dir)
        self.web_search = WebSearchTool()
        self.web_reader = WebPageReaderTool()
        self.workspace_dir = workspace_dir
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool and return the result."""
        try:
            if tool_name == "search_web":
                return self._execute_search_web(arguments)
            elif tool_name == "read_webpage":
                return self._execute_read_webpage(arguments)
            elif tool_name == "fs_read_file":
                return self._execute_fs_read_file(arguments)
            elif tool_name == "fs_insert_after":
                return self._execute_fs_insert_after(arguments)
            elif tool_name == "fs_delete_lines":
                return self._execute_fs_delete_lines(arguments)
            elif tool_name == "fs_replace_lines":
                return self._execute_fs_replace_lines(arguments)
            elif tool_name == "fs_ls":
                return self._execute_fs_ls(arguments)
            elif tool_name == "fs_grep":
                return self._execute_fs_grep(arguments)
            else:
                return f"<error>Unknown tool: {tool_name}</error>"
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return f"<error>{str(e)}</error>"
    
    def _execute_search_web(self, arguments: Dict[str, Any]) -> str:
        query = arguments.get("query", "")
        results = self.web_search(query)
        
        if not results:
            return f"<error>No search results found for query: {query}</error>"
        
        # Format results
        lines = [f"<search_results query=\"{query}\">"]
        for i, r in enumerate(results, 1):
            lines.append(f"  <result index=\"{i}\">")
            lines.append(f"    <title>{r.get('title', '')}</title>")
            lines.append(f"    <url>{r.get('url', '')}</url>")
            lines.append(f"    <summary>{r.get('summary', '')}</summary>")
            lines.append(f"  </result>")
        lines.append("</search_results>")
        
        return "\n".join(lines)
    
    def _execute_read_webpage(self, arguments: Dict[str, Any]) -> str:
        url = arguments.get("url", "")
        page_idx = int(arguments.get("page_idx", 1) or 1)
        archive = arguments.get("archive", True)
        
        normalized_url = normalize_url(url)
        result = self.web_reader(normalized_url)
        
        if not result or not result.get('content'):
            return f"<error>Failed to read webpage: {url}</error>"
        
        content = result.get('content', '')
        title = result.get('title', '')

        # chunking / paging (by characters, deterministic)
        chunk_size = 12000
        total_chars = len(content)
        total_pages = max(1, (total_chars + chunk_size - 1) // chunk_size)
        page_idx = max(1, min(page_idx, total_pages))
        start = (page_idx - 1) * chunk_size
        end = min(total_chars, start + chunk_size)
        page_content = content[start:end]

        # Archive raw source (optional, no summarization)
        archive_status = "Archive skipped"
        archive_path = ""
        if bool(archive):
            import hashlib
            import re
            from pathlib import Path

            # Stable filename: try to use a slug from title; fallback to hash(url)
            def _slugify(s: str) -> str:
                s = (s or "").strip().lower()
                s = re.sub(r"\s+", "-", s)
                s = re.sub(r"[^a-z0-9._-]+", "-", s)
                s = re.sub(r"-{2,}", "-", s).strip("-")
                return s[:80] if s else ""

            slug = _slugify(title)
            if not slug:
                slug = hashlib.md5(normalized_url.encode()).hexdigest()[:12]

            archive_path = f"knowledge_base/sources/{slug}.md"
            try:
                abs_path = Path(self.fs.root_dir) / archive_path
                if not abs_path.exists():
                    archived_content = f"---\nurl: {normalized_url}\ntitle: {title}\n---\n\n{content}"
                    self.fs.insert_after(path=archive_path, text=archived_content, after_line=None)
                archive_status = f"Source archived to ./{archive_path}"
            except Exception as e:
                archive_status = f"Archive failed: {str(e)}"

        return f"""<webpage>
<url>{url}</url>
<title>{title}</title>
<page_idx>{page_idx}</page_idx>
<total_pages>{total_pages}</total_pages>
<content>
{page_content}
</content>
<archive_status>{archive_status}</archive_status>
</webpage>"""
    
    def _execute_fs_read_file(self, arguments: Dict[str, Any]) -> str:
        path = arguments.get("path", "")
        page = arguments.get("page", 1)
        page_size = arguments.get("page_size", 50)
        return self.fs.read_file(path, page, page_size)
    
    def _execute_fs_insert_after(self, arguments: Dict[str, Any]) -> str:
        path = arguments.get("path", "")
        text = arguments.get("text", "")
        after_line = arguments.get("after_line")
        result = self.fs.insert_after(path, text, after_line)
        # Add warning about file modification
        warning = f"WARNING: {path} has been modified. Read it before next time you edit it.\n"
        return f"<observation>\n{warning}{result}\n</observation>"
    
    def _execute_fs_delete_lines(self, arguments: Dict[str, Any]) -> str:
        path = arguments.get("path", "")
        start_line = arguments.get("start_line", 1)
        end_line = arguments.get("end_line", 1)
        result = self.fs.delete_lines(path, start_line, end_line)
        warning = f"WARNING: {path} has been modified. Read it before next time you edit it.\n"
        return f"<observation>\n{warning}{result}\n</observation>"
    
    def _execute_fs_replace_lines(self, arguments: Dict[str, Any]) -> str:
        path = arguments.get("path", "")
        text = arguments.get("text", "")
        start_line = arguments.get("start_line", 1)
        end_line = arguments.get("end_line", 1)
        result = self.fs.replace_lines(path, text, start_line, end_line)
        warning = f"WARNING: {path} has been modified. Read it before next time you edit it.\n"
        return f"<observation>\n{warning}{result}\n</observation>"
    
    def _execute_fs_ls(self, arguments: Dict[str, Any]) -> str:
        path = arguments.get("path")
        recursive = arguments.get("recursive", False)
        max_depth = arguments.get("max_depth", 2)
        return f"<observation>\n{self.fs.ls(path, recursive, max_depth)}\n</observation>"
    
    def _execute_fs_grep(self, arguments: Dict[str, Any]) -> str:
        keyword = arguments.get("keyword", "")
        path = arguments.get("path", "")
        return f"<observation>\n{self.fs.grep(keyword, path)}\n</observation>"


# =============================================================================
# Agent
# =============================================================================

@dataclass
class AgentMessage:
    """Represents a message in the conversation."""
    role: str
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


class ResearchAgent:
    """
    A simple ReAct-style agent for research tasks.
    """
    
    def __init__(
        self,
        workspace_dir: str,
        stage: int = 1,
        max_iterations: int = 50,
    ):
        self.workspace_dir = workspace_dir
        self.stage = stage
        self.max_iterations = max_iterations
        
        # Initialize components
        self.tool_executor = ToolExecutor(workspace_dir)
        self.client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)
        
        # Get prompts and tools based on stage
        if stage == 1:
            self.system_prompt = get_system_prompt_stage1()
            self.tool_definitions = TOOL_DEFINITIONS_STAGE1
        else:
            self.system_prompt = get_system_prompt_stage2()
            self.tool_definitions = TOOL_DEFINITIONS_STAGE2
        
        # Conversation history
        self.messages: List[Dict[str, Any]] = []
    
    def run(self, user_query: str) -> str:
        """
        Run the agent with the given user query.
        Returns the final response.
        """
        # Initialize messages
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"<user_task>\n{user_query}\n</user_task>"}
        ]
        
        iteration = 0
        final_response = ""
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"[Iteration {iteration}]")
            
            # Call LLM
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=self.messages,
                    tools=[{"type": "function", "function": t} for t in self.tool_definitions],
                    tool_choice="auto",
                    max_tokens=MAX_OUTPUT_TOKENS,
                    temperature=0.7,
                )
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                break
            
            message = response.choices[0].message
            
            # Log the response
            if message.content:
                logger.info(f"[Assistant]: {message.content[:500]}...")
                print(f"\n[ASSISTANT]\n{message.content}")
            
            # Check if there are tool calls
            if message.tool_calls:
                # Add assistant message with tool calls
                self.messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    logger.info(f"[Tool Call] {tool_name}: {arguments}")
                    print(f"\n[TOOL] {tool_name}")
                    print(f"  Arguments: {json.dumps(arguments, ensure_ascii=False)[:200]}")
                    
                    # Execute tool
                    result = self.tool_executor.execute(tool_name, arguments)
                    
                    print(f"  Result: {result[:300]}...")
                    
                    # Add tool result to messages
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
            else:
                # No tool calls, this is the final response
                final_response = message.content or ""
                break
            # We intentionally do not rely on finish_reason:
            # if there are no tool_calls, we treat it as the final answer and stop.
        
        return final_response


# =============================================================================
# Simple Runner
# =============================================================================

def run_research_task(
    topic: str,
    workspace_dir: str,
    stage1_rounds: int = 3,
    stage2_rounds: int = 100,
) -> None:
    """
    Run a complete research task with both stages.
    
    Args:
        topic: The research topic
        workspace_dir: Directory for the workspace
        stage1_rounds: Maximum rounds for knowledge base building
        stage2_rounds: Maximum rounds for report writing
    """
    import os
    from pathlib import Path
    
    # Create workspace directory
    Path(workspace_dir).mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print(f"RESEARCH TOPIC: {topic}")
    print(f"WORKSPACE: {workspace_dir}")
    print("=" * 60)
    
    # Stage 1: Knowledge Base Building
    print("\n" + "=" * 60)
    print("STAGE 1: KNOWLEDGE BASE BUILDING")
    print("=" * 60)
    
    for round_num in range(1, stage1_rounds + 1):
        print(f"\n--- Round {round_num}/{stage1_rounds} ---")
        
        query = f"""Topic: {topic}

Current Round: {round_num} / Total Budget: {stage1_rounds}
Inspect your workspace status and begin knowledge base building.
Use the same language with the topic (except for filenames which should be in English)."""
        
        if round_num == stage1_rounds:
            query += " This is the final Round, do not add new todos, just finish all existing ones in this round."
        
        agent = ResearchAgent(workspace_dir, stage=1)
        
        try:
            agent.run(query)
        except Exception as e:
            logger.error(f"Stage 1 Round {round_num} failed: {e}")
        
        # Check if complete
        kb_log_path = Path(workspace_dir) / "kb_log.md"
        if kb_log_path.exists():
            with open(kb_log_path, "r", encoding="utf-8") as f:
                if "[ALL COMPLETE]" in f.read():
                    print("\n[Stage 1 Complete]")
                    break
    
    # Stage 2: Report Writing
    print("\n" + "=" * 60)
    print("STAGE 2: REPORT WRITING")
    print("=" * 60)
    
    for round_num in range(1, stage2_rounds + 1):
        print(f"\n--- Round {round_num}/{stage2_rounds} ---")
        
        query = f"""Topic: {topic}

Current Round: {round_num}.
Inspect your workspace status and begin report writing.
Use the same language with the topic.
ATTENTION: Place all citations in Reference section at the end of the report file. DO NOT list citations seperately for each section. Citations to the same file should come with the same citation index.
Key Takeaways should be brief and no citation is needed in key takeaways."""
        
        agent = ResearchAgent(workspace_dir, stage=2)
        
        try:
            agent.run(query)
        except Exception as e:
            logger.error(f"Stage 2 Round {round_num} failed: {e}")
        
        # Check if complete
        report_log_path = Path(workspace_dir) / "report_log.md"
        if report_log_path.exists():
            with open(report_log_path, "r", encoding="utf-8") as f:
                if "[ALL COMPLETE]" in f.read():
                    print("\n[Stage 2 Complete]")
                    break
    
    print("\n" + "=" * 60)
    print("RESEARCH TASK COMPLETE")
    print("=" * 60)
    print(f"Report saved to: {workspace_dir}/report.md")

