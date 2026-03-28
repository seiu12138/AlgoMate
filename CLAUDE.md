# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AlgoMate is an intelligent algorithm tutoring system built on **LangGraph + ReAct architecture**. It automatically analyzes algorithm problems, writes code, executes tests, and self-corrects errors.

## Core Architecture

### ReAct Agent Flow (LangGraph)

The agent follows a state machine workflow defined in `agent/react_agent.py`:

```
analyze → generate_test_cases → validate_test_cases → generate_code → execute_code → analyze_result
                                                                              ↓
                                                                         fix_code (loops back)
                                                                              ↓
                                                                           finish
```

**Key decision point**: `analyze_result` node determines next action:
- `"fix"` → fix_code node (iteration_count < max_iterations)
- `"reexecute"` → execute_code node (after test case correction)
- `"finish"` → end workflow (success or max iterations reached)

### State Management (`agent/state.py`)

`AgentState` is the central TypedDict that flows through all nodes:
- `messages`: LangChain message history (auto-merged with `operator.add`)
- `problem_analysis`: Structured JSON analysis of the problem
- `test_cases`: List of `TestCase` objects with input/expected/actual/passed
- `execution_history`: List of `ExecutionHistory` tracking all code iterations
- `iteration_count` / `max_iterations`: Controls retry loop
- `next_step`: Routing signal for conditional edges

### Node Implementation (`agent/nodes.py`)

Each node is a method in `AgentNodes` class that:
1. Takes `AgentState` as input
2. Calls LLM with prompt template from `prompts/`
3. Returns dict with updated state fields

Critical nodes:
- `analyze_result`: Parses execution results and decides if test cases are wrong vs code is wrong
- `validate_test_cases`: Self-validation step that verifies test case expected values before code generation
- `fix_code`: Receives execution history and error analysis to generate fixes

### Code Execution (`tools/code_executor.py`)

Two sandbox implementations:
- `SubprocessSandbox`: Default, uses subprocess with timeout/memory limits
- `DockerSandbox`: Optional, requires docker package

`CodeExecutor` returns `ExecutionResult` with:
- `success`, `stdout`, `stderr`, `exit_code`
- `error_type`: `'compile_error'`, `'runtime_error'`, `'timeout'`, `'memory_limit'`
- Execution time and memory usage metrics

### RAG System (`rag/`)

- `vector_stores.py`: ChromaDB wrapper with MD5-based deduplication
- `rag.py`: RAG service for algorithm knowledge Q&A
- Knowledge base files go in `data/knowledge_base/` (PDF/TXT)

## Configuration System

All configs are YAML files in `config/`:
- `model.yaml`: LLM and embedding model names (DashScope/OpenAI)
- `agent.yaml`: `max_iterations`, `code_execution_timeout`
- `chroma.yaml`: Vector DB collection name and path
- `splitter.yaml`: `chunk_size`, `chunk_overlap` for text splitting
- `storage.yaml`: Paths for MD5 cache and history

Loaded via `utils/config_handler.py` which exports `model_conf`, `agent_conf`, etc.

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (required)
export DASHSCOPE_API_KEY="your-key"  # Linux/macOS
set DASHSCOPE_API_KEY=your-key       # Windows
```

### Knowledge Base
```bash
# Warm up vector database (load PDFs/TXTs from data/knowledge_base/)
python scripts/warmup_knowledge_base.py

# Warm up with test query
python scripts/warmup_knowledge_base.py --test-query "动态规划"

# Skip test after warmup
python scripts/warmup_knowledge_base.py --no-test
```

### Running the System
```bash
# Launch web interface (Streamlit)
streamlit run algomate_web.py

# Run agent test script
python test_agent.py
```

### Testing Configuration
```bash
# Verify config loading
python -c "from utils.config_handler import load_all_configs; load_all_configs()"
```

## Important Notes

### Embedding Model Consistency
**CRITICAL**: If knowledge base was warmed up with `text-embedding-v4`, retrieval MUST use the same model. Dimension mismatch will cause ChromaDB errors. Check `config/model.yaml` before warmup.

### Prompt Templates
All prompts are in `prompts/*.txt` and loaded via `utils/prompts_loader.py`. When modifying agent behavior, edit these templates rather than hardcoding prompts in nodes.

### Language Support
Supported languages in `tools/code_executor.py`:
- `python`: Uses `python3` command
- `cpp`: Compiles with `g++`, runs binary
- `java`: Compiles with `javac`, runs with `java`

### Iteration Control
Default `max_iterations=5` in `agent/react_agent.py`. Agent will attempt up to 5 code fixes before giving up. Configurable per solve() call or via `config/agent.yaml`.

### Logging
Structured logging via `utils/logger_handler.py`:
- `log_node()`: Node execution flow
- `log_test()`: Test case details
- `log_code()`: Generated code
- Logs saved to `logs/` directory

## Web Interface (`algomate_web.py`)

Two modes:
1. **RAG Q&A Mode**: Query knowledge base for algorithm concepts
2. **Agent Solve Mode**: Input problem description, select language, watch agent solve in real-time

Uses `solve_stream()` for real-time progress display in Streamlit.
