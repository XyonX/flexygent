from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class CreativeIdeasInput(BaseModel):
    """Input for creative idea generation."""
    topic: str = Field(..., description="Topic or theme for creative ideas")
    idea_type: str = Field(default="general", description="Type of ideas: general, marketing, product, design, campaign")
    quantity: int = Field(default=5, description="Number of ideas to generate")
    constraints: Optional[List[str]] = Field(None, description="Constraints or requirements")


class CreativeIdeasOutput(BaseModel):
    """Output from creative idea generation."""
    ideas: List[Dict[str, Any]] = Field(default_factory=list, description="Generated creative ideas")
    themes: List[str] = Field(default_factory=list, description="Key themes identified")
    inspiration_sources: List[str] = Field(default_factory=list, description="Sources of inspiration")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")


class CreativeIdeasTool(BaseTool[CreativeIdeasInput, CreativeIdeasOutput]):
    """Tool for generating creative ideas and concepts."""
    
    name = "creative.ideas"
    description = "Generate creative ideas, concepts, and innovative solutions"
    tags = {"creative", "ideas", "innovation"}
    timeout_seconds = 30.0
    input_model = CreativeIdeasInput
    output_model = CreativeIdeasOutput
    
    def execute(self, params: CreativeIdeasInput, context: Optional[Dict[str, Any]] = None) -> CreativeIdeasOutput:
        """Generate creative ideas."""
        try:
            ideas = []
            themes = []
            inspiration_sources = []
            next_steps = []
            
            # Generate ideas based on type
            if params.idea_type == "marketing":
                ideas = self._generate_marketing_ideas(params.topic, params.quantity)
                themes = ["Brand awareness", "Customer engagement", "Digital presence"]
            elif params.idea_type == "product":
                ideas = self._generate_product_ideas(params.topic, params.quantity)
                themes = ["User experience", "Innovation", "Market fit"]
            elif params.idea_type == "design":
                ideas = self._generate_design_ideas(params.topic, params.quantity)
                themes = ["Visual appeal", "Usability", "Accessibility"]
            elif params.idea_type == "campaign":
                ideas = self._generate_campaign_ideas(params.topic, params.quantity)
                themes = ["Storytelling", "Engagement", "Impact"]
            else:  # general
                ideas = self._generate_general_ideas(params.topic, params.quantity)
                themes = ["Innovation", "Problem-solving", "Creativity"]
            
            # Generate inspiration sources
            inspiration_sources = self._generate_inspiration_sources(params.topic, params.idea_type)
            
            # Generate next steps
            next_steps = self._generate_next_steps(params.idea_type, len(ideas))
            
            return CreativeIdeasOutput(
                ideas=ideas,
                themes=themes,
                inspiration_sources=inspiration_sources,
                next_steps=next_steps
            )
            
        except Exception as e:
            return CreativeIdeasOutput(
                ideas=[{"error": f"Idea generation error: {str(e)}"}],
                themes=[],
                inspiration_sources=[],
                next_steps=[]
            )
    
    def _generate_marketing_ideas(self, topic: str, quantity: int) -> List[Dict[str, Any]]:
        """Generate marketing ideas."""
        ideas = [
            {
                "title": f"Interactive {topic} Experience",
                "description": f"Create an immersive, interactive experience that allows customers to engage with {topic} in a unique way",
                "key_elements": ["User engagement", "Brand interaction", "Memorable experience"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Social Media {topic} Challenge",
                "description": f"Launch a viral social media challenge related to {topic} that encourages user-generated content",
                "key_elements": ["Viral potential", "User-generated content", "Social sharing"],
                "feasibility": "high",
                "impact": "high"
            },
            {
                "title": f"Collaborative {topic} Campaign",
                "description": f"Partner with influencers, artists, or other brands to create collaborative content around {topic}",
                "key_elements": ["Partnerships", "Cross-promotion", "Authentic content"],
                "feasibility": "medium",
                "impact": "medium"
            },
            {
                "title": f"Educational {topic} Series",
                "description": f"Create educational content series that teaches audiences about {topic} while subtly promoting your brand",
                "key_elements": ["Educational value", "Brand authority", "Long-term engagement"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"Gamified {topic} Experience",
                "description": f"Develop a gamification strategy that makes interacting with {topic} fun and rewarding",
                "key_elements": ["Gamification", "User retention", "Engagement"],
                "feasibility": "medium",
                "impact": "high"
            }
        ]
        return ideas[:quantity]
    
    def _generate_product_ideas(self, topic: str, quantity: int) -> List[Dict[str, Any]]:
        """Generate product ideas."""
        ideas = [
            {
                "title": f"Smart {topic} Solution",
                "description": f"Develop an intelligent, AI-powered solution that enhances {topic} with automation and personalization",
                "key_elements": ["AI integration", "Automation", "Personalization"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Mobile-First {topic} App",
                "description": f"Create a mobile application that makes {topic} accessible and convenient on-the-go",
                "key_elements": ["Mobile optimization", "Convenience", "Accessibility"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"Sustainable {topic} Alternative",
                "description": f"Design an eco-friendly alternative to traditional {topic} solutions",
                "key_elements": ["Sustainability", "Environmental impact", "Innovation"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Community-Driven {topic} Platform",
                "description": f"Build a platform that connects people around {topic} and enables community collaboration",
                "key_elements": ["Community", "Collaboration", "Social features"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"AR/VR {topic} Experience",
                "description": f"Create an augmented or virtual reality experience that revolutionizes how people interact with {topic}",
                "key_elements": ["AR/VR technology", "Immersive experience", "Innovation"],
                "feasibility": "low",
                "impact": "high"
            }
        ]
        return ideas[:quantity]
    
    def _generate_design_ideas(self, topic: str, quantity: int) -> List[Dict[str, Any]]:
        """Generate design ideas."""
        ideas = [
            {
                "title": f"Minimalist {topic} Design",
                "description": f"Create a clean, minimalist design approach for {topic} that focuses on simplicity and clarity",
                "key_elements": ["Simplicity", "Clean aesthetics", "User focus"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"Bold {topic} Visual Identity",
                "description": f"Develop a striking, memorable visual identity for {topic} that stands out in the market",
                "key_elements": ["Visual impact", "Brand recognition", "Memorability"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Accessible {topic} Design",
                "description": f"Design {topic} with accessibility as a core principle, ensuring it's usable by everyone",
                "key_elements": ["Accessibility", "Inclusivity", "Universal design"],
                "feasibility": "high",
                "impact": "high"
            },
            {
                "title": f"Adaptive {topic} Interface",
                "description": f"Create an interface that adapts to different user preferences and contexts",
                "key_elements": ["Adaptability", "Personalization", "Flexibility"],
                "feasibility": "medium",
                "impact": "medium"
            },
            {
                "title": f"Emotional {topic} Design",
                "description": f"Design {topic} to evoke specific emotions and create meaningful user connections",
                "key_elements": ["Emotional design", "User connection", "Brand personality"],
                "feasibility": "medium",
                "impact": "high"
            }
        ]
        return ideas[:quantity]
    
    def _generate_campaign_ideas(self, topic: str, quantity: int) -> List[Dict[str, Any]]:
        """Generate campaign ideas."""
        ideas = [
            {
                "title": f"Storytelling {topic} Campaign",
                "description": f"Create a narrative-driven campaign that tells compelling stories around {topic}",
                "key_elements": ["Storytelling", "Emotional connection", "Narrative arc"],
                "feasibility": "high",
                "impact": "high"
            },
            {
                "title": f"User-Generated {topic} Content",
                "description": f"Encourage users to create and share their own content related to {topic}",
                "key_elements": ["User participation", "Authentic content", "Community building"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"Seasonal {topic} Campaign",
                "description": f"Develop a campaign that ties {topic} to seasonal events, holidays, or cultural moments",
                "key_elements": ["Seasonal relevance", "Cultural connection", "Timing"],
                "feasibility": "medium",
                "impact": "medium"
            },
            {
                "title": f"Behind-the-Scenes {topic} Campaign",
                "description": f"Show the process, people, and passion behind {topic} to build authenticity",
                "key_elements": ["Transparency", "Authenticity", "Human connection"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"Interactive {topic} Campaign",
                "description": f"Create an interactive campaign that allows audiences to participate and influence the outcome",
                "key_elements": ["Interactivity", "Participation", "Engagement"],
                "feasibility": "medium",
                "impact": "high"
            }
        ]
        return ideas[:quantity]
    
    def _generate_general_ideas(self, topic: str, quantity: int) -> List[Dict[str, Any]]:
        """Generate general creative ideas."""
        ideas = [
            {
                "title": f"Innovative {topic} Approach",
                "description": f"Develop a completely new way of thinking about and approaching {topic}",
                "key_elements": ["Innovation", "Fresh perspective", "Disruption"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Cross-Industry {topic} Solution",
                "description": f"Apply solutions from other industries to solve {topic} challenges",
                "key_elements": ["Cross-pollination", "Industry insights", "Innovation"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Community-Centric {topic} Initiative",
                "description": f"Create initiatives that put community needs and values at the center of {topic}",
                "key_elements": ["Community focus", "Social impact", "Collaboration"],
                "feasibility": "high",
                "impact": "medium"
            },
            {
                "title": f"Technology-Enhanced {topic}",
                "description": f"Leverage emerging technologies to enhance and improve {topic}",
                "key_elements": ["Technology integration", "Future-focused", "Efficiency"],
                "feasibility": "medium",
                "impact": "high"
            },
            {
                "title": f"Sustainable {topic} Model",
                "description": f"Develop a sustainable approach to {topic} that considers long-term impact",
                "key_elements": ["Sustainability", "Long-term thinking", "Responsibility"],
                "feasibility": "high",
                "impact": "high"
            }
        ]
        return ideas[:quantity]
    
    def _generate_inspiration_sources(self, topic: str, idea_type: str) -> List[str]:
        """Generate inspiration sources."""
        sources = [
            f"Industry leaders in {topic}",
            "Successful case studies from similar domains",
            "User feedback and pain points",
            "Emerging technology trends",
            "Cultural and social movements"
        ]
        
        if idea_type == "marketing":
            sources.extend(["Viral campaigns", "Social media trends", "Influencer strategies"])
        elif idea_type == "product":
            sources.extend(["User research", "Competitive analysis", "Technology innovations"])
        elif idea_type == "design":
            sources.extend(["Design trends", "Art movements", "User experience research"])
        
        return sources
    
    def _generate_next_steps(self, idea_type: str, idea_count: int) -> List[str]:
        """Generate recommended next steps."""
        steps = [
            "Prioritize ideas based on feasibility and impact",
            "Develop detailed concepts for top 2-3 ideas",
            "Conduct market research and validation",
            "Create prototypes or mockups",
            "Gather stakeholder feedback"
        ]
        
        if idea_type == "marketing":
            steps.extend(["Define target audience", "Set campaign objectives", "Plan budget allocation"])
        elif idea_type == "product":
            steps.extend(["Technical feasibility study", "User testing plan", "Development roadmap"])
        elif idea_type == "design":
            steps.extend(["Design system creation", "Usability testing", "Accessibility audit"])
        
        return steps
