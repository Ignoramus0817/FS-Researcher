#!/usr/bin/env python3
"""
Minimal runnable entrypoint:
- Runs two agents: Stage 1 (knowledge base building) and Stage 2 (report writing)
- Prints intermediate logs (assistant output + tool call/return previews)

Examples:
1) From the repository root:
   python -m research_agent_minimal.main --topic "your research topic" --workspace ./workspace_demo

2) If you copy the `research_agent_minimal` folder elsewhere, run from its parent directory:
   python -m research_agent_minimal.main --topic "your research topic"
"""

import argparse
import logging

from .agent import run_research_task
from .config import DEFAULT_WORKSPACE, STAGE1_MAX_ROUNDS, STAGE2_MAX_ROUNDS


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Agent Minimal Runner")
    parser.add_argument("--topic", type=str, required=True, help="Research topic / prompt")
    parser.add_argument(
        "--workspace",
        type=str,
        default=DEFAULT_WORKSPACE,
        help="Workspace output directory (default: ./workspace)",
    )
    parser.add_argument(
        "--stage1_rounds",
        type=int,
        default=STAGE1_MAX_ROUNDS,
        help="Max rounds for Stage 1",
    )
    parser.add_argument(
        "--stage2_rounds",
        type=int,
        default=STAGE2_MAX_ROUNDS,
        help="Max rounds for Stage 2",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    _setup_logging(args.verbose)

    run_research_task(
        topic=args.topic,
        workspace_dir=args.workspace,
        stage1_rounds=args.stage1_rounds,
        stage2_rounds=args.stage2_rounds,
    )


if __name__ == "__main__":
    main()


