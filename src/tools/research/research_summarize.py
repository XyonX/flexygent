from __future__ import annotations

import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class ResearchSummarizeInput(BaseModel):
    """Input for research summarization."""
    content: str = Field(..., description="Content to summarize")
    summary_type: str = Field(default="brief", description="Type of summary: brief, detailed, bullet_points")
    max_length: int = Field(default=500, description="Maximum length of summary")


class ResearchSummarizeOutput(BaseModel):
    """Output from research summarization."""
    summary: str = Field(..., description="Generated summary")
    key_points: list = Field(default_factory=list, description="Key points extracted")
    word_count: int = Field(default=0, description="Word count of summary")
    confidence: float = Field(default=0.0, description="Confidence score of summary")


class ResearchSummarizeTool(BaseTool[ResearchSummarizeInput, ResearchSummarizeOutput]):
    """Tool for summarizing research content."""
    
    name = "research.summarize"
    description = "Summarize research content and extract key points"
    tags = {"research", "summarization", "analysis"}
    timeout_seconds = 30.0
    input_model = ResearchSummarizeInput
    output_model = ResearchSummarizeOutput
    
    def execute(self, params: ResearchSummarizeInput, context: Optional[Dict[str, Any]] = None) -> ResearchSummarizeOutput:
        """Summarize research content."""
        try:
            # Basic text summarization logic
            sentences = params.content.split('. ')
            key_points = []
            
            # Extract key sentences (simplified algorithm)
            important_sentences = []
            for sentence in sentences:
                if len(sentence) > 20 and any(word in sentence.lower() for word in ['important', 'key', 'main', 'primary', 'significant']):
                    important_sentences.append(sentence)
                    key_points.append(sentence.strip())
            
            # Generate summary based on type
            if params.summary_type == "bullet_points":
                summary = "\n".join([f"• {point}" for point in key_points[:5]])
            elif params.summary_type == "detailed":
                summary = ". ".join(important_sentences[:3]) + "."
            else:  # brief
                summary = ". ".join(important_sentences[:2]) + "." if important_sentences else sentences[0] + "."
            
            # Truncate if too long
            if len(summary) > params.max_length:
                summary = summary[:params.max_length] + "..."
            
            word_count = len(summary.split())
            confidence = min(0.9, len(key_points) / 5.0)  # Simple confidence metric
            
            return ResearchSummarizeOutput(
                summary=summary,
                key_points=key_points[:5],
                word_count=word_count,
                confidence=confidence
            )
            
        except Exception as e:
            return ResearchSummarizeOutput(
                summary=f"Summarization error: {str(e)}",
                key_points=[],
                word_count=0,
                confidence=0.0
            )
