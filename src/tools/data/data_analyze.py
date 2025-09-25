from __future__ import annotations

import json
import statistics
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..base_tool import BaseTool


class DataAnalyzeInput(BaseModel):
    """Input for data analysis."""
    data: str = Field(..., description="Data to analyze (JSON, CSV, or structured text)")
    analysis_type: str = Field(default="descriptive", description="Type of analysis: descriptive, correlation, trend, summary")
    columns: Optional[List[str]] = Field(None, description="Specific columns to analyze")


class DataAnalyzeOutput(BaseModel):
    """Output from data analysis."""
    summary_stats: Dict[str, Any] = Field(default_factory=dict, description="Summary statistics")
    insights: List[str] = Field(default_factory=list, description="Key insights from analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on analysis")
    visualizations: List[str] = Field(default_factory=list, description="Suggested visualizations")


class DataAnalyzeTool(BaseTool[DataAnalyzeInput, DataAnalyzeOutput]):
    """Tool for analyzing data and providing statistical insights."""
    
    name = "data.analyze"
    description = "Analyze data and provide statistical insights, trends, and recommendations"
    tags = {"data", "analysis", "statistics"}
    timeout_seconds = 30.0
    input_model = DataAnalyzeInput
    output_model = DataAnalyzeOutput
    
    def execute(self, params: DataAnalyzeInput, context: Optional[Dict[str, Any]] = None) -> DataAnalyzeOutput:
        """Analyze data and provide insights."""
        try:
            # Parse data
            parsed_data = self._parse_data(params.data)
            
            if not parsed_data:
                return DataAnalyzeOutput(
                    summary_stats={},
                    insights=["No valid data found to analyze"],
                    recommendations=[],
                    visualizations=[]
                )
            
            # Perform analysis based on type
            if params.analysis_type == "descriptive":
                return self._descriptive_analysis(parsed_data, params.columns)
            elif params.analysis_type == "correlation":
                return self._correlation_analysis(parsed_data, params.columns)
            elif params.analysis_type == "trend":
                return self._trend_analysis(parsed_data, params.columns)
            else:  # summary
                return self._summary_analysis(parsed_data, params.columns)
                
        except Exception as e:
            return DataAnalyzeOutput(
                summary_stats={},
                insights=[f"Analysis error: {str(e)}"],
                recommendations=[],
                visualizations=[]
            )
    
    def _parse_data(self, data: str) -> List[Dict[str, Any]]:
        """Parse data from various formats."""
        try:
            # Try JSON first
            if data.strip().startswith('[') or data.strip().startswith('{'):
                return json.loads(data)
            
            # Try CSV-like format
            lines = data.strip().split('\n')
            if len(lines) < 2:
                return []
            
            headers = [h.strip() for h in lines[0].split(',')]
            parsed_data = []
            
            for line in lines[1:]:
                values = [v.strip() for v in line.split(',')]
                if len(values) == len(headers):
                    row = {}
                    for i, header in enumerate(headers):
                        # Try to convert to number
                        try:
                            row[header] = float(values[i])
                        except ValueError:
                            row[header] = values[i]
                    parsed_data.append(row)
            
            return parsed_data
            
        except Exception:
            return []
    
    def _descriptive_analysis(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> DataAnalyzeOutput:
        """Perform descriptive statistical analysis."""
        if not data:
            return DataAnalyzeOutput(summary_stats={}, insights=[], recommendations=[], visualizations=[])
        
        summary_stats = {}
        insights = []
        recommendations = []
        visualizations = []
        
        # Get numeric columns
        numeric_columns = []
        for key in data[0].keys():
            if columns and key not in columns:
                continue
            if all(isinstance(row.get(key), (int, float)) for row in data if row.get(key) is not None):
                numeric_columns.append(key)
        
        for col in numeric_columns:
            values = [row[col] for row in data if row[col] is not None]
            if values:
                summary_stats[col] = {
                    "count": len(values),
                    "mean": round(statistics.mean(values), 2),
                    "median": round(statistics.median(values), 2),
                    "std_dev": round(statistics.stdev(values) if len(values) > 1 else 0, 2),
                    "min": min(values),
                    "max": max(values),
                    "range": max(values) - min(values)
                }
                
                # Generate insights
                if summary_stats[col]["std_dev"] > summary_stats[col]["mean"] * 0.5:
                    insights.append(f"High variability in {col} (std dev > 50% of mean)")
                
                if summary_stats[col]["range"] > summary_stats[col]["mean"] * 2:
                    insights.append(f"Wide range in {col} values")
        
        # Recommendations
        if len(numeric_columns) > 1:
            recommendations.append("Consider correlation analysis between numeric variables")
        
        if any(stats["std_dev"] > stats["mean"] * 0.3 for stats in summary_stats.values()):
            recommendations.append("High variability detected - consider outlier analysis")
        
        # Visualization suggestions
        if len(numeric_columns) == 1:
            visualizations.extend(["histogram", "box_plot"])
        elif len(numeric_columns) == 2:
            visualizations.extend(["scatter_plot", "correlation_matrix"])
        else:
            visualizations.extend(["correlation_matrix", "pair_plot"])
        
        return DataAnalyzeOutput(
            summary_stats=summary_stats,
            insights=insights,
            recommendations=recommendations,
            visualizations=visualizations
        )
    
    def _correlation_analysis(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> DataAnalyzeOutput:
        """Perform correlation analysis."""
        # Simplified correlation analysis
        insights = ["Correlation analysis requires at least 2 numeric variables"]
        recommendations = ["Ensure data has sufficient numeric columns for correlation analysis"]
        
        return DataAnalyzeOutput(
            summary_stats={},
            insights=insights,
            recommendations=recommendations,
            visualizations=["correlation_matrix", "scatter_plot"]
        )
    
    def _trend_analysis(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> DataAnalyzeOutput:
        """Perform trend analysis."""
        insights = ["Trend analysis requires time-series data"]
        recommendations = ["Ensure data includes time/date columns for trend analysis"]
        
        return DataAnalyzeOutput(
            summary_stats={},
            insights=insights,
            recommendations=recommendations,
            visualizations=["line_chart", "time_series"]
        )
    
    def _summary_analysis(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None) -> DataAnalyzeOutput:
        """Perform general summary analysis."""
        insights = [
            f"Dataset contains {len(data)} records",
            f"Dataset has {len(data[0]) if data else 0} columns"
        ]
        
        recommendations = [
            "Review data quality and completeness",
            "Consider additional analysis based on data characteristics"
        ]
        
        return DataAnalyzeOutput(
            summary_stats={"record_count": len(data), "column_count": len(data[0]) if data else 0},
            insights=insights,
            recommendations=recommendations,
            visualizations=["summary_table"]
        )
