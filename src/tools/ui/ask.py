from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry


class AskInput(BaseModel):
    question: str = Field(..., description="Question to present to the user")
    options: Optional[List[str]] = Field(None, description="Optional multiple-choice options")
    allow_free_text: bool = Field(True, description="Whether to allow arbitrary text answers")


class AskOutput(BaseModel):
    answer: str = Field(..., description="User's answer")
    selected_option: Optional[str] = Field(None, description="If options were provided and one was selected")


class AskUserTool(BaseTool[AskInput, AskOutput]):
    """
    Virtual tool. The orchestrator intercepts calls to 'ui.ask' and routes them to the UI adapter.
    This tool exists to expose a schema to the LLM; its execute() is not used.
    """
    name = "ui.ask"
    description = "Ask the user for input when the LLM needs a preference or missing info."
    input_model = AskInput
    output_model = AskOutput

    async def execute(self, params: AskInput, *, context: Optional[dict] = None) -> AskOutput:
        # This should be intercepted by the orchestrator. If executed directly, return a placeholder.
        return AskOutput(answer="", selected_option=None)


registry.register_tool(AskUserTool())