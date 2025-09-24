from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .tool_calling_agent import ToolCallingAgent
from ..tools.registry import registry


class AdaptiveToolAgent(ToolCallingAgent):
    """
    Tool-calling agent that adapts over time:
      - Tracks per-tool success/failure counts (simple scoring).
      - Prefers tools with higher historical success.
      - Can adjust autonomy or temperature over time.

    Memory keys (per agent):
      - f\"{self.name}:tool_stats\" -> { tool_name: {\"success\": int, \"failure\": int} }

    Note: Determining \"success\" is domain-specific. This class exposes `record_outcome`.
    Call it after evaluating the result externally, or override `evaluate_success`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Warm-up tool stats from memory
        self._tool_stats = self._load_tool_stats()

        # Reorder tools based on stats (higher success ratio first)
        self._prioritize_tools()

    # ------------------------- Adaptation methods ------------------------------

    def record_outcome(self, success: bool, tools_used: Optional[List[str]] = None) -> None:
        """
        Record success/failure outcome for the tools used in the last task.
        If tools_used is None, tries to infer from memory 'last_dialog'.
        """
        if not tools_used:
            tools_used = self._infer_tools_from_last_dialog()

        if not tools_used:
            return

        for t in tools_used:
            stats = self._tool_stats.setdefault(t, {"success": 0, "failure": 0})
            if success:
                stats["success"] += 1
            else:
                stats["failure"] += 1

        self._persist_tool_stats()
        self._prioritize_tools()

    def evaluate_success(self, result: Dict[str, Any]) -> Optional[bool]:
        """
        Optional heuristic to auto-evaluate success. Default: None (no auto evaluation).
        Override this method for domain-specific success checks.
        """
        return None

    def on_task_complete(self, task: str, result: Dict[str, Any]) -> None:
        # Optionally perform auto evaluation
        auto = self.evaluate_success(result)
        if auto is not None:
            self.record_outcome(success=auto, tools_used=self._infer_tools_from_messages(result.get("messages")))

    # -------------------------- Internals -------------------------------------

    def _tool_stats_key(self) -> str:
        return f"{self.name}:tool_stats"

    def _load_tool_stats(self) -> Dict[str, Dict[str, int]]:
        try:
            if self.memory:
                stats = self.memory.retrieve(self._tool_stats_key())
                if isinstance(stats, dict):
                    return stats
        except Exception:
            pass
        return {}

    def _persist_tool_stats(self) -> None:
        try:
            if self.memory:
                self.memory.store(self._tool_stats_key(), self._tool_stats)
        except Exception:
            pass

    def _prioritize_tools(self) -> None:
        """Reorder self._tool_names in-place based on success ratio (desc)."""
        def ratio(s: Dict[str, int]) -> float:
            wins = s.get("success", 0)
            losses = s.get("failure", 0)
            total = wins + losses
            return (wins / total) if total > 0 else 0.0

        # Ensure all listed tools have an entry
        for n in list(self._tool_names):
            self._tool_stats.setdefault(n, {"success": 0, "failure": 0})

        self._tool_names.sort(key=lambda n: ratio(self._tool_stats.get(n, {})), reverse=True)

    def _infer_tools_from_last_dialog(self) -> List[str]:
        if not self.memory:
            return []
        try:
            dlg = self.memory.retrieve("last_dialog")
            return self._infer_tools_from_messages((dlg or {}).get("messages"))
        except Exception:
            return []

    @staticmethod
    def _infer_tools_from_messages(messages: Any) -> List[str]:
        """Extract tool names used from a messages transcript structure, if present."""
        used = []
        if not isinstance(messages, list):
            return used
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "tool":
                name = msg.get("name")
                if isinstance(name, str):
                    used.append(name)
        # Deduplicate preserving order
        seen = set()
        out: List[str] = []
        for n in used:
            if n not in seen:
                out.append(n)
                seen.add(n)
        return out