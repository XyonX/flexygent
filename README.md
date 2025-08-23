# Flexygent: Flexible & Customizable AI Agent Framework

Flexygent is a modular, extensible framework for building custom AI agents with memory, tool use, and LLM integration. Designed for rapid prototyping and production-ready deployments, Flexygent lets you combine short-term and long-term memory, tool execution, and modern LLMs (via OpenRouter) in a single, easy-to-extend Python codebase.

## Features

- **FastAPI-powered API server** for chat and agent interaction
- **Short-term and long-term memory** (vector store via ChromaDB)
- **Pluggable tool registry** for agent tool use (add your own tools easily)
- **LLM integration** via OpenRouter-compatible API (supports OpenAI schema)
- **Async, production-ready code**
- **Easy configuration** with `.env` and config files
- **Example usage script** for quick testing and prototyping

## Quickstart

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file or edit `config/config.py` to set your API keys and configuration (e.g., OpenRouter key, ChromaDB path).

### 3. Run the API Server

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`.

### 4. Example Usage

See `example_usage.py` for a script that demonstrates agent memory, tool use, and LLM response.

## Project Structure

```
flexygent/
├── main.py                # FastAPI server entrypoint
├── example_usage.py       # Example script for agent usage
├── requirements.txt       # Python dependencies
├── config/                # Configuration files
├── memory/                # Short-term and long-term memory modules
├── tools/                 # Tool registry and custom tools
├── utils/                 # LLM client and utilities
├── chroma_data/           # ChromaDB vector store data
└── notes.txt              # Project notes
```

## API Overview

- **POST /chat**
  - Request: `{ "session_id": "string", "message": "string" }`
  - Response: `{ "reply": "string" }`

## Extending Flexygent

- **Add new tools:** Implement a tool and register it in `tools/tool_registry.py`.
- **Swap LLMs:** Change the model or provider in `utils/llm.py` or via config.
- **Customize memory:** Extend `ShortTermMemory` or `LongTermMemory` for new memory strategies.

## Requirements
- Python 3.8+
- See `requirements.txt` for dependencies

## License

MIT License. See `LICENSE` file.

---

*Flexygent is in active development. Contributions and feedback are welcome!*
