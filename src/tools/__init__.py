# from .base_tool import BaseTool, ToolExecutionError, ToolDescriptor
# from .registry import ToolRegistry, registry

# def load_builtin_tools() -> None:
#     """
#     Import modules that auto-register their tools at import time.
#     Call this during app startup if you want built-ins available.
#     """
#     # System tools (if you created one like Echo)
#     try:
#         from .system import echo  # noqa: F401
#     except Exception:
#         # It's okay if system tools aren't present yet
#         pass

#     # Web tools
#     from .web import search as _search  # noqa: F401
#     from .web import scraper as _scraper  # noqa: F401


# __all__ = [
#     "BaseTool",
#     "ToolExecutionError",
#     "ToolDescriptor",
#     "ToolRegistry",
#     "registry",
#     "load_builtin_tools",
# ]

from .base_tool import BaseTool, ToolExecutionError, ToolDescriptor
from .registry import ToolRegistry, registry

def load_builtin_tools() -> None:
    """
    Import modules that auto-register their tools at import time.
    Call this during app startup if you want built-ins available.
    """
    # System tools (if you created one like Echo)
    try:
        from .system import echo  # noqa: F401
    except Exception:
        pass

    # Web tools
    from .web import search as _search  # noqa: F401
    from .web import scraper as _scraper  # noqa: F401
    try:
        from .web import fetch as _fetch  # noqa: F401
    except Exception:
        pass

    # UI tools
    try:
        from .ui import ask as _ask  # noqa: F401
    except Exception:
        pass

    # RAG tools (optional; require sentence-transformers + numpy)
    try:
        from .rag import index as _rag_index  # noqa: F401
        from .rag import query as _rag_query  # noqa: F401
    except Exception:
        # It's okay if RAG deps aren't installed yet
        pass


__all__ = [
    "BaseTool",
    "ToolExecutionError",
    "ToolDescriptor",
    "ToolRegistry",
    "registry",
    "load_builtin_tools",
]