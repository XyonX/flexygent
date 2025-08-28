from __future__ import annotations

from typing import Iterable, List, Tuple


def split_text(text: str, *, chunk_size: int = 800, chunk_overlap: int = 100) -> List[str]:
    """
    Simple chunker: splits by paragraphs then merges into ~chunk_size with overlap.
    """
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: List[str] = []

    cur: List[str] = []
    cur_len = 0
    for p in paras:
        if cur_len + len(p) + 1 > chunk_size and cur:
            chunks.append("\n".join(cur))
            # start new with overlap
            if chunk_overlap > 0 and chunks:
                tail = chunks[-1][-chunk_overlap:]
                cur = [tail, p]
                cur_len = len(tail) + len(p) + 1
            else:
                cur = [p]
                cur_len = len(p)
        else:
            cur.append(p)
            cur_len += len(p) + 1

    if cur:
        chunks.append("\n".join(cur))

    # Ensure not empty
    return [c for c in chunks if c.strip()]