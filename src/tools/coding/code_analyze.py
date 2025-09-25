from __future__ import annotations

import re
import ast
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class CodeAnalyzeInput(BaseModel):
    """Input for code analysis."""
    code: str = Field(..., description="The code to analyze")
    language: str = Field(default="python", description="Programming language")
    analysis_type: str = Field(default="all", description="Type of analysis: syntax, style, complexity, all")


class CodeAnalyzeOutput(BaseModel):
    """Output from code analysis."""
    syntax_valid: bool = Field(..., description="Whether syntax is valid")
    style_issues: list = Field(default_factory=list, description="Style issues found")
    complexity_score: Optional[int] = Field(None, description="Cyclomatic complexity score")
    suggestions: list = Field(default_factory=list, description="Improvement suggestions")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Code metrics")


class CodeAnalyzeTool(BaseTool[CodeAnalyzeInput, CodeAnalyzeOutput]):
    """Tool for analyzing code quality and providing suggestions."""
    
    name = "code.analyze"
    description = "Analyze code for syntax, style, complexity, and provide improvement suggestions"
    tags = {"coding", "analysis", "quality"}
    timeout_seconds = 30.0
    input_model = CodeAnalyzeInput
    output_model = CodeAnalyzeOutput
    
    def execute(self, params: CodeAnalyzeInput, context: Optional[Dict[str, Any]] = None) -> CodeAnalyzeOutput:
        """Analyze code and provide insights."""
        try:
            syntax_valid = True
            style_issues = []
            suggestions = []
            metrics = {}
            
            if params.language.lower() == "python":
                # Syntax validation
                try:
                    ast.parse(params.code)
                except SyntaxError as e:
                    syntax_valid = False
                    suggestions.append(f"Syntax error: {e}")
                
                # Basic style analysis
                lines = params.code.split('\n')
                for i, line in enumerate(lines, 1):
                    if len(line) > 100:
                        style_issues.append(f"Line {i}: Line too long ({len(line)} characters)")
                    if line.strip().startswith('import ') and ',' in line:
                        style_issues.append(f"Line {i}: Multiple imports on one line")
                    if 'print(' in line and not line.strip().startswith('#'):
                        style_issues.append(f"Line {i}: Consider using logging instead of print")
                
                # Basic metrics
                metrics = {
                    "lines_of_code": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
                    "total_lines": len(lines),
                    "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
                    "function_count": len(re.findall(r'def\s+\w+', params.code)),
                    "class_count": len(re.findall(r'class\s+\w+', params.code))
                }
                
                # Complexity estimation (simplified)
                complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with']
                complexity_score = sum(params.code.lower().count(keyword) for keyword in complexity_keywords)
                metrics["complexity_score"] = complexity_score
                
                # Suggestions
                if complexity_score > 10:
                    suggestions.append("High complexity detected. Consider breaking down into smaller functions.")
                if metrics["lines_of_code"] > 50:
                    suggestions.append("Long function detected. Consider splitting into smaller functions.")
                if metrics["comment_lines"] < metrics["lines_of_code"] * 0.1:
                    suggestions.append("Consider adding more comments for better documentation.")
            
            return CodeAnalyzeOutput(
                syntax_valid=syntax_valid,
                style_issues=style_issues,
                complexity_score=metrics.get("complexity_score"),
                suggestions=suggestions,
                metrics=metrics
            )
            
        except Exception as e:
            return CodeAnalyzeOutput(
                syntax_valid=False,
                style_issues=[],
                complexity_score=None,
                suggestions=[f"Analysis error: {str(e)}"],
                metrics={}
            )
