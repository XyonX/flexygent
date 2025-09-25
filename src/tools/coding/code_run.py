from __future__ import annotations

import subprocess
import tempfile
import os
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class CodeRunInput(BaseModel):
    """Input for running code snippets."""
    code: str = Field(..., description="The code to execute")
    language: str = Field(default="python", description="Programming language (python, javascript, bash)")
    timeout: int = Field(default=30, description="Execution timeout in seconds")


class CodeRunOutput(BaseModel):
    """Output from code execution."""
    success: bool = Field(..., description="Whether execution was successful")
    output: str = Field(..., description="Standard output from execution")
    error: Optional[str] = Field(None, description="Error output if any")
    exit_code: int = Field(..., description="Exit code of the process")


class CodeRunTool(BaseTool[CodeRunInput, CodeRunOutput]):
    """Tool for executing code snippets safely."""
    
    name = "code.run"
    description = "Execute code snippets in various programming languages safely"
    tags = {"coding", "development", "execution"}
    timeout_seconds = 60.0
    requires_filesystem = True
    input_model = CodeRunInput
    output_model = CodeRunOutput
    
    def execute(self, params: CodeRunInput, context: Optional[Dict[str, Any]] = None) -> CodeRunOutput:
        """Execute code snippet safely."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(params.language), delete=False) as f:
                f.write(params.code)
                temp_file = f.name
            
            # Execute based on language
            if params.language.lower() == "python":
                result = subprocess.run(
                    ["python", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=params.timeout
                )
            elif params.language.lower() == "javascript":
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=params.timeout
                )
            elif params.language.lower() == "bash":
                result = subprocess.run(
                    ["bash", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=params.timeout
                )
            else:
                return CodeRunOutput(
                    success=False,
                    output="",
                    error=f"Unsupported language: {params.language}",
                    exit_code=1
                )
            
            # Clean up
            os.unlink(temp_file)
            
            return CodeRunOutput(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.stderr else None,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return CodeRunOutput(
                success=False,
                output="",
                error=f"Code execution timed out after {params.timeout} seconds",
                exit_code=124
            )
        except Exception as e:
            return CodeRunOutput(
                success=False,
                output="",
                error=f"Execution error: {str(e)}",
                exit_code=1
            )
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "bash": ".sh"
        }
        return extensions.get(language.lower(), ".txt")
