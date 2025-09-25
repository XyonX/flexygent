from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class ProjectPlanInput(BaseModel):
    """Input for project planning."""
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Project description")
    duration_days: int = Field(default=30, description="Project duration in days")
    team_size: int = Field(default=5, description="Team size")
    complexity: str = Field(default="medium", description="Project complexity: low, medium, high")


class ProjectPlanOutput(BaseModel):
    """Output from project planning."""
    phases: List[Dict[str, Any]] = Field(default_factory=list, description="Project phases")
    timeline: Dict[str, Any] = Field(default_factory=dict, description="Project timeline")
    milestones: List[Dict[str, Any]] = Field(default_factory=list, description="Key milestones")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    recommendations: List[str] = Field(default_factory=list, description="Planning recommendations")


class ProjectPlanTool(BaseTool[ProjectPlanInput, ProjectPlanOutput]):
    """Tool for creating project plans and timelines."""
    
    name = "project.plan"
    description = "Create comprehensive project plans with phases, timelines, and milestones"
    tags = {"project", "planning", "management"}
    timeout_seconds = 30.0
    input_model = ProjectPlanInput
    output_model = ProjectPlanOutput
    
    def execute(self, params: ProjectPlanInput, context: Optional[Dict[str, Any]] = None) -> ProjectPlanOutput:
        """Create project plan."""
        try:
            # Generate project phases based on complexity
            phases = self._generate_phases(params.complexity, params.duration_days)
            
            # Create timeline
            timeline = self._create_timeline(phases, params.duration_days)
            
            # Generate milestones
            milestones = self._generate_milestones(phases, params.duration_days)
            
            # Identify risks
            risks = self._identify_risks(params.complexity, params.team_size, params.duration_days)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(params.complexity, params.team_size)
            
            return ProjectPlanOutput(
                phases=phases,
                timeline=timeline,
                milestones=milestones,
                risks=risks,
                recommendations=recommendations
            )
            
        except Exception as e:
            return ProjectPlanOutput(
                phases=[],
                timeline={},
                milestones=[],
                risks=[f"Planning error: {str(e)}"],
                recommendations=[]
            )
    
    def _generate_phases(self, complexity: str, duration_days: int) -> List[Dict[str, Any]]:
        """Generate project phases based on complexity."""
        base_phases = [
            {
                "name": "Planning & Setup",
                "description": "Project initialization, requirements gathering, and team setup",
                "duration_days": max(3, duration_days // 8),
                "tasks": ["Requirements analysis", "Team formation", "Tool setup", "Initial planning"]
            },
            {
                "name": "Development",
                "description": "Core development and implementation work",
                "duration_days": duration_days // 2,
                "tasks": ["Core development", "Testing", "Integration", "Documentation"]
            },
            {
                "name": "Testing & Quality Assurance",
                "description": "Comprehensive testing and quality control",
                "duration_days": max(5, duration_days // 6),
                "tasks": ["Unit testing", "Integration testing", "User acceptance testing", "Bug fixes"]
            },
            {
                "name": "Deployment & Launch",
                "description": "Final deployment and project launch",
                "duration_days": max(3, duration_days // 8),
                "tasks": ["Deployment", "Launch preparation", "Go-live", "Post-launch monitoring"]
            }
        ]
        
        if complexity == "high":
            # Add additional phases for complex projects
            base_phases.insert(2, {
                "name": "Design & Architecture",
                "description": "System design and architecture planning",
                "duration_days": max(5, duration_days // 6),
                "tasks": ["System design", "Architecture review", "Technical specifications", "Design validation"]
            })
        
        return base_phases
    
    def _create_timeline(self, phases: List[Dict[str, Any]], duration_days: int) -> Dict[str, Any]:
        """Create project timeline."""
        start_date = datetime.now()
        timeline = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": (start_date + timedelta(days=duration_days)).strftime("%Y-%m-%d"),
            "total_duration_days": duration_days,
            "phases": []
        }
        
        current_date = start_date
        for phase in phases:
            phase_end = current_date + timedelta(days=phase["duration_days"])
            timeline["phases"].append({
                "name": phase["name"],
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": phase_end.strftime("%Y-%m-%d"),
                "duration_days": phase["duration_days"]
            })
            current_date = phase_end
        
        return timeline
    
    def _generate_milestones(self, phases: List[Dict[str, Any]], duration_days: int) -> List[Dict[str, Any]]:
        """Generate key project milestones."""
        milestones = []
        
        for i, phase in enumerate(phases):
            milestone = {
                "name": f"{phase['name']} Complete",
                "description": f"Completion of {phase['name'].lower()} phase",
                "phase": phase["name"],
                "priority": "high" if i == 0 or i == len(phases) - 1 else "medium"
            }
            milestones.append(milestone)
        
        # Add project-specific milestones
        milestones.append({
            "name": "Project Kickoff",
            "description": "Official project start",
            "phase": "Planning & Setup",
            "priority": "high"
        })
        
        milestones.append({
            "name": "Project Completion",
            "description": "All deliverables completed and project closed",
            "phase": "Deployment & Launch",
            "priority": "high"
        })
        
        return milestones
    
    def _identify_risks(self, complexity: str, team_size: int, duration_days: int) -> List[str]:
        """Identify potential project risks."""
        risks = [
            "Resource availability and team member conflicts",
            "Scope creep and changing requirements",
            "Technical challenges and integration issues"
        ]
        
        if complexity == "high":
            risks.extend([
                "Complex system integration challenges",
                "High technical risk due to complexity",
                "Extended testing and debugging phases"
            ])
        
        if team_size > 10:
            risks.append("Communication overhead with large team")
        elif team_size < 3:
            risks.append("Limited bandwidth and single points of failure")
        
        if duration_days > 90:
            risks.extend([
                "Long project duration increases risk of scope changes",
                "Team member availability over extended period"
            ])
        
        return risks
    
    def _generate_recommendations(self, complexity: str, team_size: int) -> List[str]:
        """Generate project management recommendations."""
        recommendations = [
            "Establish clear communication channels and regular check-ins",
            "Implement agile methodology with short sprints",
            "Set up proper project tracking and monitoring tools"
        ]
        
        if complexity == "high":
            recommendations.extend([
                "Consider breaking down into smaller sub-projects",
                "Implement comprehensive testing strategy early",
                "Plan for additional buffer time in timeline"
            ])
        
        if team_size > 8:
            recommendations.append("Consider team structure with sub-teams and leads")
        elif team_size < 4:
            recommendations.append("Ensure clear role definitions and cross-training")
        
        return recommendations
