from __future__ import annotations

import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class GrammarCheckInput(BaseModel):
    """Input for grammar checking."""
    text: str = Field(..., description="Text to check for grammar")
    language: str = Field(default="en", description="Language code (en, es, fr, etc.)")
    check_type: str = Field(default="all", description="Type of check: grammar, spelling, style, all")


class GrammarCheckOutput(BaseModel):
    """Output from grammar checking."""
    corrected_text: str = Field(..., description="Text with corrections applied")
    issues_found: list = Field(default_factory=list, description="List of issues found")
    suggestions: list = Field(default_factory=list, description="Improvement suggestions")
    score: float = Field(default=0.0, description="Grammar score (0-100)")


class GrammarCheckTool(BaseTool[GrammarCheckInput, GrammarCheckOutput]):
    """Tool for checking grammar and providing writing suggestions."""
    
    name = "writing.grammar_check"
    description = "Check grammar, spelling, and style in text"
    tags = {"writing", "grammar", "editing"}
    timeout_seconds = 30.0
    input_model = GrammarCheckInput
    output_model = GrammarCheckOutput
    
    def execute(self, params: GrammarCheckInput, context: Optional[Dict[str, Any]] = None) -> GrammarCheckOutput:
        """Check grammar and provide suggestions."""
        try:
            corrected_text = params.text
            issues_found = []
            suggestions = []
            
            # Basic grammar and style checks
            lines = corrected_text.split('\n')
            
            for i, line in enumerate(lines):
                original_line = line
                
                # Check for common grammar issues
                if re.search(r'\bi\b', line) and not line.strip().startswith('I'):
                    line = re.sub(r'\bi\b', 'I', line)
                    issues_found.append(f"Line {i+1}: Capitalize 'I'")
                
                # Check for double spaces
                if '  ' in line:
                    line = re.sub(r' +', ' ', line)
                    issues_found.append(f"Line {i+1}: Remove double spaces")
                
                # Check for missing periods
                if line.strip() and not line.strip().endswith(('.', '!', '?', ':', ';')):
                    line = line.rstrip() + '.'
                    issues_found.append(f"Line {i+1}: Add period at end")
                
                # Check for common misspellings (basic)
                common_misspellings = {
                    'recieve': 'receive',
                    'seperate': 'separate',
                    'occured': 'occurred',
                    'definately': 'definitely',
                    'accomodate': 'accommodate'
                }
                
                for misspelling, correction in common_misspellings.items():
                    if misspelling in line.lower():
                        line = re.sub(misspelling, correction, line, flags=re.IGNORECASE)
                        issues_found.append(f"Line {i+1}: Corrected '{misspelling}' to '{correction}'")
                
                lines[i] = line
            
            corrected_text = '\n'.join(lines)
            
            # Generate suggestions
            word_count = len(corrected_text.split())
            sentence_count = len(re.findall(r'[.!?]+', corrected_text))
            
            if sentence_count > 0:
                avg_sentence_length = word_count / sentence_count
                if avg_sentence_length > 20:
                    suggestions.append("Consider shortening some sentences for better readability")
                elif avg_sentence_length < 10:
                    suggestions.append("Consider combining some short sentences for better flow")
            
            # Check for passive voice (basic)
            passive_patterns = [
                r'\b(was|were|been|being)\s+\w+ed\b',
                r'\b(is|are|was|were)\s+\w+ed\b'
            ]
            
            passive_count = sum(len(re.findall(pattern, corrected_text, re.IGNORECASE)) for pattern in passive_patterns)
            if passive_count > word_count * 0.1:  # More than 10% passive voice
                suggestions.append("Consider using more active voice for better engagement")
            
            # Calculate grammar score
            total_issues = len(issues_found)
            score = max(0, 100 - (total_issues * 5))  # Deduct 5 points per issue
            
            return GrammarCheckOutput(
                corrected_text=corrected_text,
                issues_found=issues_found,
                suggestions=suggestions,
                score=score
            )
            
        except Exception as e:
            return GrammarCheckOutput(
                corrected_text=params.text,
                issues_found=[f"Grammar check error: {str(e)}"],
                suggestions=[],
                score=0.0
            )
