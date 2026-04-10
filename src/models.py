from pydantic import BaseModel, Field
from typing import List, Literal

class FeedbackItem(BaseModel):
    id: int
    text: str

class AnalyzedFeedbackItem(BaseModel):
    id: int
    text: str 
    category: Literal[
        "Repeated issues or bugs", 
        "Suggestions/feature requests", 
        "Complaints or dissatisfaction", 
        "Neutral or positive feedback"
    ]
    sentiment: Literal["negative", "neutral", "positive"]
    summary: str = Field(..., max_length=400)
    tags: List[str]
    
class ActionItem(BaseModel):
    action: str
    priority: Literal["High", "Medium", "Low"]
    rationale: str = Field(..., description="Why this action is recommended based on data")

class ManagementSummary(BaseModel):
    overall_summary: str
    key_themes: List[str]
    recommended_actions: List[ActionItem]