"""
Configuration for Research Agent Minimal
All configurations are read from environment variables or this file
"""
import os

# =============================================================================
# LLM Configuration
# =============================================================================

# OpenAI-compatible API configuration
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5")

# Token limits
MAX_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", "128000"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "16384"))

# =============================================================================
# Tool Configuration
# =============================================================================

# Jina AI Reader API key (for read_webpage)
# Get your free API key at: https://jina.ai/reader/
JINA_API_KEY = os.getenv("JINA_API_KEY", "")

# Google SERP API key (for search_web)
# Get your API key at: https://serper.dev/
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# =============================================================================
# Agent Configuration
# =============================================================================

# Maximum rounds for each stage
STAGE1_MAX_ROUNDS = int(os.getenv("STAGE1_MAX_ROUNDS", "3"))
STAGE2_MAX_ROUNDS = int(os.getenv("STAGE2_MAX_ROUNDS", "100"))

# Workspace configuration
DEFAULT_WORKSPACE = os.getenv("DEFAULT_WORKSPACE", "./workspace")

