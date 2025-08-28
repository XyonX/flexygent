from __future__ import annotations
import os

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from src.tools import load_builtin_tools, registry
from src.tools.rag import index as _index  # noqa: F401  (ensure tool registers)
from src.tools.rag import query as _query  # noqa: F401
from src.agents.rag_agent import RAGAgent
from src.llm.openrouter_provider import OpenRouterProvider
from src.utils.config_loader import load_config, get_openrouter_cfg


def main():
    load_builtin_tools()

    cfg = load_config(["config/default.yaml"])
    or_cfg = get_openrouter_cfg(cfg)
    llm = OpenRouterProvider.from_config(or_cfg)

    # 1) Build/update the local index from some files (docs and code as example)
    idx_dir = ".rag_index"
    index_tool = registry.get_tool("rag.index")
    res = index_tool({
        "index_dir": idx_dir,
        "paths": ["README.md", "architecture.md", "src/**/*.py"],
        "file_extensions": [".md", ".py", ".txt"],
        "max_files": 500,
        "chunk_size": 800,
        "chunk_overlap": 100,
    })
    # Execute sync wrapper
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        res = asyncio.run(res)
    print(f"Indexed chunks: {res.added_chunks} from files: {res.total_files} -> {res.index_dir}")

    # 2) Ask a RAG-grounded question
    agent = RAGAgent(
        name="ragger",
        config={"index_dir": idx_dir, "top_k": 5},
        llm=llm,
        tools=[registry.get_tool("rag.query")],
    )
    question = "How does tool registration and discovery work in this project?"
    out = agent.process_task(question)
    print("\n=== Answer ===\n", out["answer"])


if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY not set; LLM calls will fail.")
    main()