from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry
from ...rag.embedding import EmbeddingProvider
from ...rag.vector_store import LocalNumpyVectorStore, SearchResult


class RagQueryInput(BaseModel):
    index_dir: str = Field(..., description="Directory path to the local vector index")
    query: str = Field(..., description="User question or search query")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")
    model_name: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="Embedding model name")


class RetrievedChunk(BaseModel):
    text: str = Field(..., description="Retrieved text chunk")
    score: float = Field(..., description="Cosine similarity score")


class RagQueryOutput(BaseModel):
    query: str = Field(..., description="Original query")
    top_k: int = Field(..., description="Number of chunks returned")
    chunks: List[RetrievedChunk] = Field(default_factory=list, description="Retrieved chunks ordered by relevance")
    context: str = Field(..., description="Concatenated context string (for prompting)")


class RagQueryTool(BaseTool[RagQueryInput, RagQueryOutput]):
    name = "rag.query"
    description = "Query a local vector index and return the most relevant chunks."
    input_model = RagQueryInput
    output_model = RagQueryOutput

    requires_network = False
    requires_filesystem = True
    timeout_seconds = 20.0
    max_concurrency = 8
    tags = frozenset({"rag", "retrieve", "local"})

    async def execute(self, params: RagQueryInput, *, context: Optional[dict] = None) -> RagQueryOutput:
        embedder = EmbeddingProvider(model_name=params.model_name)
        q_emb = embedder.embed_query(params.query)

        store = LocalNumpyVectorStore(params.index_dir)
        results: List[SearchResult] = store.search(q_emb, top_k=params.top_k)

        chunks = [RetrievedChunk(text=r.text, score=r.score) for r in results]
        context = "\n\n---\n\n".join([r.text for r in results])

        return RagQueryOutput(
            query=params.query,
            top_k=params.top_k,
            chunks=chunks,
            context=context,
        )


# Register
registry.register_tool(RagQueryTool())