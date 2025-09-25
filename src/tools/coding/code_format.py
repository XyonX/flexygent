from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class CodeFormatInput(BaseModel):
    """Input for code formatting."""
    code: str = Field(..., description="The code to format")
    language: str = Field(default="python", description="Programming language")
    style: str = Field(default="pep8", description="Code style to apply (pep8, black, prettier)")


class CodeFormatOutput(BaseModel):
    """Output from code formatting."""
    formatted_code: str = Field(..., description="The formatted code")
    changes_made: list = Field(default_factory=list, description="List of changes made")
    success: bool = Field(..., description="Whether formatting was successful")


class CodeFormatTool(BaseTool[CodeFormatInput, CodeFormatOutput]):
    """Tool for formatting code according to style guidelines."""
    
    name = "code.format"
    description = "Format code according to style guidelines (PEP8, Black, Prettier)"
    tags = {"coding", "formatting", "style"}
    timeout_seconds = 30.0
    input_model = CodeFormatInput
    output_model = CodeFormatOutput
    
    def execute(self, params: CodeFormatInput, context: Optional[Dict[str, Any]] = None) -> CodeFormatOutput:
        """Format code according to style guidelines."""
        try:
            changes_made = []
            formatted_code = params.code
            
            if params.language.lower() == "python":
                # Basic PEP8 formatting
                lines = formatted_code.split('\n')
                formatted_lines = []
                
                for i, line in enumerate(lines):
                    original_line = line
                    
                    # Remove trailing whitespace
                    line = line.rstrip()
                    if original_line != line:
                        changes_made.append(f"Line {i+1}: Removed trailing whitespace")
                    
                    # Fix indentation (basic)
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                        # This is a top-level statement
                        pass
                    
                    formatted_lines.append(line)
                
                formatted_code = '\n'.join(formatted_lines)
                
                # Add spacing around operators
                formatted_code = re.sub(r'(\w)([+\-*/=<>!]+)(\w)', r'\1 \2 \3', formatted_code)
                if re.search(r'(\w)([+\-*/=<>!]+)(\w)', params.code):
                    changes_made.append("Added spacing around operators")
                
                # Fix import statements
                import_lines = []
                other_lines = []
                in_imports = False
                
                for line in formatted_code.split('\n'):
                    if line.strip().startswith(('import ', 'from ')):
                        import_lines.append(line)
                        in_imports = True
                    elif in_imports and line.strip() == '':
                        import_lines.append(line)
                    else:
                        if in_imports:
                            other_lines.append('')  # Add blank line after imports
                            in_imports = False
                        other_lines.append(line)
                
                if import_lines and other_lines:
                    formatted_code = '\n'.join(import_lines + other_lines)
                    changes_made.append("Organized import statements")
            
            elif params.language.lower() == "javascript":
                # Basic JavaScript formatting
                formatted_code = formatted_code.replace(';', ';\n')
                formatted_code = re.sub(r'(\w)([+\-*/=<>!]+)(\w)', r'\1 \2 \3', formatted_code)
                changes_made.append("Applied basic JavaScript formatting")
            
            return CodeFormatOutput(
                formatted_code=formatted_code,
                changes_made=changes_made,
                success=True
            )
            
        except Exception as e:
            return CodeFormatOutput(
                formatted_code=params.code,
                changes_made=[f"Formatting error: {str(e)}"],
                success=False
            )
