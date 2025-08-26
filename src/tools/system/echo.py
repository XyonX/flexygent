from __future__ import annotations

import asyncio
from typing import Optional

from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry


class EchoInput(BaseModel):
    text: str = Field(..., description="Text to echo back.")
    uppercase: bool = Field(False, description="If true, return the text in uppercase.")
    repeat: int = Field(1, ge=1, le=10, description="Number of times to repeat the text (1-10).")
    delay_ms: Optional[int] = Field(
        None,
        ge=0,
        le=5_000,
        description="Optional artificial delay in milliseconds (for testing timeouts/latency).",
    )


class EchoOutput(BaseModel):
    result: str = Field(..., description="Echoed result string.")
    length: int = Field(..., ge=0, description="Length of the result string in characters.")


class EchoTool(BaseTool[EchoInput, EchoOutput]):
    name = "system.echo"
    description = "Echo a string with optional uppercasing and repetition."
    input_model = EchoInput
    output_model = EchoOutput

    # Operational settings
    timeout_seconds = 5.0
    max_concurrency = None  # unlimited
    requires_network = False
    requires_filesystem = False
    tags = frozenset({"utility", "testing", "example"})

    async def execute(self, params: EchoInput, *, context: Optional[dict] = None) -> EchoOutput:
        if params.delay_ms and params.delay_ms > 0:
            await asyncio.sleep(params.delay_ms / 1000.0)

        text = params.text.upper() if params.uppercase else params.text
        result = " ".join([text] * params.repeat)
        return EchoOutput(result=result, length=len(result))


# Register the tool at import-time so it's available once this module is imported
registry.register_tool(EchoTool())