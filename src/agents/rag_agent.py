from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, LLMProvider, MemoryStore
from ..tools.base_tool import BaseTool
from ..tools.registry import registry


class RAGAgent(BaseAgent):
    """
    Retrieval-Augmented Generation agent:
      - Retrieves relevant context via rag.query
      - Crafts a prompt with the retrieved context
      - Calls the LLM to answer grounded in that context
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        llm: Optional[LLMProvider] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[MemoryStore] = None,
    ) -> None:
        super().__init__(name=name, config=config, llm=llm, tools=tools, memory=memory)
        # Ensure RAG tools are available
        wanted = ["rag.query"]
        for n in wanted:
            if not any(getattr(t, "name", "") == n for t in self.tools):
                if registry.has_tool(n):
                    self.tools.append(registry.get_tool(n))
        self._tool_by_name: Dict[str, BaseTool] = {t.name: t for t in self.tools}

    def process_task(self, task: str) -> Any:
        # Retrieve context
        index_dir = str(self.config.get("index_dir") or ".rag_index")
        top_k = int(self.config.get("top_k", 5))
        model_name = str(self.config.get("embed_model", "sentence-transformers/all-MiniLM-L6-v2"))

        rag_query = self._require_tool("rag.query")
        out = self._run_tool(
            rag_query,
            {
                "index_dir": index_dir,
                "query": task,
                "top_k": top_k,
                "model_name": model_name,
            },
        )

        # Compose prompt
        prompt = self._build_prompt(task, out.context)
        answer = self.llm.send_message(prompt) if self.llm else f"[No LLM configured]\n{prompt}"

        self.update_memory("last_rag", {"query": task, "chunks": [c.text for c in out.chunks], "answer": answer})
        return {"agent": self.name, "query": task, "answer": answer, "top_k": top_k, "index_dir": index_dir}

    def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        tool = self._require_tool(tool_name)
        return self._run_tool(tool, payload)

    # Helpers ------------------------------------------------------------------

    def _require_tool(self, name: str) -> BaseTool:
        tool = self._tool_by_name.get(name)
        if tool is None:
            if registry.has_tool(name):
                tool = registry.get_tool(name)
                self._tool_by_name[name] = tool
            else:
                raise ValueError(f"Tool '{name}' not available to agent '{self.name}'.")
        return tool

    def _run_tool(self, tool: BaseTool, payload: Dict[str, Any]):
        # Sync wrapper (BaseAgent currently sync)
        import asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(tool(payload))
        return loop.run_until_complete(tool(payload))

    def _build_prompt(self, question: str, context: str) -> str:
        return (
            "You are a helpful assistant. Use the provided context to answer the question.\n"
            "If the answer is not in the context, say you don't know.\n\n"
            f"Question:\n{question}\n\n"
            f"Context:\n{context}\n\n"
            "Answer:"
        )