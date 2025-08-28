# from __future__ import annotations

# from dataclasses import dataclass, field
# from enum import Enum
# from typing import List, Optional, Set


# class AutonomyLevel(str, Enum):
#     auto = "auto"        # run tools without user confirmation
#     confirm = "confirm"  # ask for confirmation based on lists
#     never = "never"      # never execute tools (LLM must answer without tools)


# @dataclass
# class ToolUsePolicy:
#     autonomy: AutonomyLevel = AutonomyLevel.auto
#     # Allow/deny/confirm lists operate on tool names
#     allow_tools: Optional[Set[str]] = None        # if set, only these tools are permitted
#     deny_tools: Set[str] = field(default_factory=set)
#     confirm_tools: Set[str] = field(default_factory=set)  # always confirm these (if autonomy=confirm)

#     # Limits
#     max_steps: int = 8
#     max_tool_calls: Optional[int] = None  # overall cap on tool calls
#     parallel_tool_calls: bool = True
#     tool_result_truncate: int = 8000

#     # Optional wall-time budget could be enforced by caller
#     max_wall_time_s: Optional[float] = None

# 02

# from __future__ import annotations

# from dataclasses import dataclass, field
# from enum import Enum
# from typing import Optional, Set


# class AutonomyLevel(str, Enum):
#     auto = "auto"        # run tools without user confirmation
#     confirm = "confirm"  # ask for confirmation (all or per tool)
#     never = "never"      # do not expose tools to the LLM


# @dataclass
# class ToolUsePolicy:
#     autonomy: AutonomyLevel = AutonomyLevel.auto
#     # Lists operate on tool names
#     allow_tools: Optional[Set[str]] = None  # if set, only these are allowed
#     deny_tools: Set[str] = field(default_factory=set)
#     confirm_tools: Set[str] = field(default_factory=set)  # confirm these in confirm mode; empty means "confirm all"

#     # Limits
#     max_steps: int = 8
#     max_tool_calls: Optional[int] = None
#     parallel_tool_calls: bool = True
#     tool_result_truncate: int = 8000

#     # Optional: wall-time budgets could be implemented by caller
#     max_wall_time_s: Optional[float] = None

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Set


class AutonomyLevel(str, Enum):
    auto = "auto"        # run tools without user confirmation
    confirm = "confirm"  # ask for confirmation (all or per tool)
    never = "never"      # do not expose tools to the LLM


@dataclass
class ToolUsePolicy:
    autonomy: AutonomyLevel = AutonomyLevel.auto
    # Lists operate on tool names
    allow_tools: Optional[Set[str]] = None  # if set, only these are allowed
    deny_tools: Set[str] = field(default_factory=set)
    confirm_tools: Set[str] = field(default_factory=set)  # confirm these in confirm mode; empty means "confirm all"

    # Limits
    max_steps: int = 8
    max_tool_calls: Optional[int] = None
    parallel_tool_calls: bool = True
    tool_result_truncate: int = 8000

    # Optional: wall-time budgets could be implemented by caller
    max_wall_time_s: Optional[float] = None