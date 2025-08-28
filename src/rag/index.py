from __future__ import annotations

import glob
import os
from typing import List, Optional

from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry
from ...rag.embedding import EmbeddingProvider
from ...rag.vector_store import LocalNumpyVectorStore
from ...rag.chunking import split_text


class RagIndexInput(BaseModel):
    index_dir: str = Field(..., description="Directory path for the local vector index")
    texts: Optional[List[str]] = Field(None, description="Raw texts to index")
    paths: Optional[List[str]] = Field(None, description="Files or globs to load, e.g., ['docs/**/*.md']")
    file_extensions: Optional[List[str]] = Field(
        default=None,
        description="If provided, only load files with these extensions (e.g., ['.md', '.txt', '.py'])."
    )
    max_files: int = Field(500, ge=1, le=50_000, description="Cap number of files to load")
    chunk_size: int = Field(800, ge=200, le=4000, description="Target chunk size (characters)")
    chunk_overlap: int = Field(100, ge=0, le=1000, description="Overlap between chunks (characters)")
    model_name: str = Field("sentence-transformers/all-MiniLM-L6-v2", description="Embedding model name")


class RagIndexOutput(BaseModel):
    added_chunks: int = Field(..., description="Number of chunks indexed")
    total_files: int = Field(..., description="Number of files processed")
    index_dir: str = Field(..., description="Index directory path")


class RagIndexTool(BaseTool[RagIndexInput, RagIndexOutput]):
    name = "rag.index"
    description = "Index texts and/or local files into a vector store for retrieval."
    input_model = RagIndexInput
    output_model = RagIndexOutput

    requires_network = False
    requires_filesystem = True
    timeout_seconds = 120.0
    max_concurrency = 2
    tags = frozenset({"rag", "index", "local"})

    async def execute(self, params: RagIndexInput, *, context: Optional[dict] = None) -> RagIndexOutput:
        texts: List[str] = []
        files_count = 0

        # Collect texts from files if specified
        if params.paths:
            seen = set()
            for pattern in params.paths:
                for p in glob.glob(pattern, recursive=True):
                    if len(seen) >= params.max_files:
                        break
                    if os.path.isdir(p):
                        continue
                    if params.file_extensions and not any(p.lower().endswith(ext.lower()) for ext in params.file_extensions):
                        continue
                    if p in seen:
                        continue
                    seen.add(p)
                    try:
                        with open(p, "r", encoding="utf-8", errors="ignore") as f:
                            texts.append(f.read())
                            files_count += 1
                    except Exception:
                        continue

        # Add raw texts if provided
        if params.texts:
            texts.extend([t for t in params.texts if t and t.strip()])

        # Chunk
        chunks: List[str] = []
        for t in texts:
            chunks.extend(split_text(t, chunk_size=params.chunk_size, chunk_overlap=params.chunk_overlap))

        if not chunks:
            return RagIndexOutput(added_chunks=0, total_files=files_count, index_dir=params.index_dir)

        # Embed
        embedder = EmbeddingProvider(model_name=params.model_name)
        embeddings = embedder.embed_texts(chunks)

        # Upsert
        store = LocalNumpyVectorStore(params.index_dir)
        items = [{"text": chunk, "metadata": {}} for chunk in chunks]
        added = store.add(embeddings, items)

        return RagIndexOutput(added_chunks=added, total_files=files_count, index_dir=params.index_dir)


# Register
registry.register_tool(RagIndexTool())