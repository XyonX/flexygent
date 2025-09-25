from __future__ import annotations

import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class ContentGenerateInput(BaseModel):
    """Input for content generation."""
    topic: str = Field(..., description="Topic for content generation")
    content_type: str = Field(default="article", description="Type of content: article, blog_post, email, social_media")
    length: str = Field(default="medium", description="Length: short, medium, long")
    tone: str = Field(default="professional", description="Tone: professional, casual, formal, friendly")


class ContentGenerateOutput(BaseModel):
    """Output from content generation."""
    content: str = Field(..., description="Generated content")
    word_count: int = Field(default=0, description="Word count of generated content")
    structure: list = Field(default_factory=list, description="Content structure/outline")
    suggestions: list = Field(default_factory=list, description="Improvement suggestions")


class ContentGenerateTool(BaseTool[ContentGenerateInput, ContentGenerateOutput]):
    """Tool for generating various types of content."""
    
    name = "content.generate"
    description = "Generate various types of content (articles, blog posts, emails, social media)"
    tags = {"writing", "content", "generation"}
    timeout_seconds = 30.0
    input_model = ContentGenerateInput
    output_model = ContentGenerateOutput
    
    def execute(self, params: ContentGenerateInput, context: Optional[Dict[str, Any]] = None) -> ContentGenerateOutput:
        """Generate content based on specifications."""
        try:
            # Determine target word count based on length
            word_counts = {
                "short": 150,
                "medium": 500,
                "long": 1000
            }
            target_words = word_counts.get(params.length, 500)
            
            # Generate content structure
            structure = self._generate_structure(params.content_type, params.topic)
            
            # Generate content based on type
            if params.content_type == "article":
                content = self._generate_article(params.topic, params.tone, target_words)
            elif params.content_type == "blog_post":
                content = self._generate_blog_post(params.topic, params.tone, target_words)
            elif params.content_type == "email":
                content = self._generate_email(params.topic, params.tone, target_words)
            elif params.content_type == "social_media":
                content = self._generate_social_media(params.topic, params.tone, target_words)
            else:
                content = self._generate_generic_content(params.topic, params.tone, target_words)
            
            word_count = len(content.split())
            suggestions = self._generate_suggestions(content, params.content_type)
            
            return ContentGenerateOutput(
                content=content,
                word_count=word_count,
                structure=structure,
                suggestions=suggestions
            )
            
        except Exception as e:
            return ContentGenerateOutput(
                content=f"Content generation error: {str(e)}",
                word_count=0,
                structure=[],
                suggestions=[]
            )
    
    def _generate_structure(self, content_type: str, topic: str) -> list:
        """Generate content structure."""
        structures = {
            "article": ["Introduction", "Main Points", "Supporting Evidence", "Conclusion"],
            "blog_post": ["Hook", "Introduction", "Main Content", "Call to Action"],
            "email": ["Subject Line", "Greeting", "Body", "Closing"],
            "social_media": ["Hook", "Main Message", "Call to Action"]
        }
        return structures.get(content_type, ["Introduction", "Body", "Conclusion"])
    
    def _generate_article(self, topic: str, tone: str, target_words: int) -> str:
        """Generate article content."""
        return f"""# {topic.title()}

## Introduction
This article explores the key aspects of {topic.lower()}, providing comprehensive insights and practical information.

## Main Content
{topic.title()} is a fascinating subject that encompasses multiple dimensions. Understanding its core principles is essential for anyone looking to gain deeper knowledge in this area.

The primary considerations include:
- Key concepts and definitions
- Practical applications
- Current trends and developments
- Future implications

## Supporting Evidence
Research shows that {topic.lower()} plays a crucial role in various contexts. Studies have demonstrated its effectiveness and importance across different domains.

## Conclusion
In conclusion, {topic.lower()} represents a significant area of study with broad applications and implications for the future."""

    def _generate_blog_post(self, topic: str, tone: str, target_words: int) -> str:
        """Generate blog post content."""
        return f"""# {topic.title()}: A Complete Guide

Hey there! 👋

Today, I want to dive deep into {topic.lower()} and share everything you need to know about this fascinating topic.

## Why {topic.title()} Matters

{topic.title()} isn't just another trend - it's a game-changer that's reshaping how we think about [related concepts]. Whether you're a beginner or an expert, there's always something new to learn.

## Key Takeaways

Here are the most important things to remember about {topic.lower()}:

1. **Fundamental Principles**: Understanding the basics is crucial
2. **Practical Applications**: How to apply this knowledge in real-world scenarios
3. **Common Pitfalls**: What to avoid when working with {topic.lower()}

## Final Thoughts

{topic.title()} continues to evolve, and staying updated is key to success. What are your thoughts on this topic? Let me know in the comments below!

# {topic.replace(' ', '')} #Learning #Guide"""

    def _generate_email(self, topic: str, tone: str, target_words: int) -> str:
        """Generate email content."""
        return f"""Subject: Update on {topic.title()}

Dear [Recipient],

I hope this email finds you well. I wanted to reach out regarding {topic.lower()} and share some important updates.

## Key Points

• **Current Status**: We've made significant progress on {topic.lower()}
• **Next Steps**: Here's what we need to focus on moving forward
• **Timeline**: We're on track to meet our deadlines

## Action Items

Please review the attached materials and let me know if you have any questions or concerns.

Best regards,
[Your Name]"""

    def _generate_social_media(self, topic: str, tone: str, target_words: int) -> str:
        """Generate social media content."""
        return f"""🚀 Excited to share insights about {topic.title()}!

{topic.title()} is changing the game in ways we never imagined. Here's what you need to know:

✅ Key benefits
✅ Practical applications  
✅ Future implications

What's your take on {topic.lower()}? Drop a comment below! 👇

#{topic.replace(' ', '')} #Innovation #Future"""

    def _generate_generic_content(self, topic: str, tone: str, target_words: int) -> str:
        """Generate generic content."""
        return f"""# {topic.title()}

{topic.title()} is an important subject that deserves careful consideration. This comprehensive overview covers the essential aspects you need to understand.

## Overview

{topic.title()} encompasses various elements that work together to create meaningful outcomes. Understanding these components is crucial for success.

## Key Considerations

When exploring {topic.lower()}, it's important to consider:
- Historical context
- Current applications
- Future potential
- Practical implications

## Conclusion

{topic.title()} represents a significant area of study with broad implications for various fields and applications."""

    def _generate_suggestions(self, content: str, content_type: str) -> list:
        """Generate improvement suggestions."""
        suggestions = []
        
        if len(content.split()) < 100:
            suggestions.append("Consider expanding the content with more details and examples")
        
        if content_type == "article" and not re.search(r'##', content):
            suggestions.append("Add more subheadings to improve readability")
        
        if not re.search(r'[.!?]$', content):
            suggestions.append("Ensure the content has proper conclusion")
        
        return suggestions
