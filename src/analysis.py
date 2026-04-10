# analysis.py
import pandas as pd
from collections import Counter
from typing import List, Dict, Tuple

from models import FeedbackItem, AnalyzedFeedbackItem, ManagementSummary
from llm_client import analyze_feedback_items as llm_analyze_feedback_items   # ← renamed import
from llm_client import generate_management_summary


def load_feedback_from_csv(path: str) -> List[FeedbackItem]:
    df = pd.read_csv(path)
    df["id"] = range(1, len(df) + 1)
    return [
        FeedbackItem(id=int(row.id), text=str(row.feedback_text))
        for _, row in df.iterrows()
    ]


def process_feedback(items: List[FeedbackItem]) -> Tuple[List[AnalyzedFeedbackItem], ManagementSummary]:
    """
    High-level function: batch-classify items + generate executive summary
    This is the function that should be called from app.py
    """
    analyzed = llm_analyze_feedback_items(items)           # now calls the LLM batch function
    summary  = generate_management_summary(analyzed)
    return analyzed, summary


def aggregate_stats(analyzed_items: List[AnalyzedFeedbackItem]) -> Dict:
    categories = Counter(i.category for i in analyzed_items)
    sentiments = Counter(i.sentiment for i in analyzed_items)
    
    tag_counter = Counter()
    for i in analyzed_items:
        tag_counter.update(i.tags)
    
    return {
        "total_count": len(analyzed_items),
        "categories": dict(categories),
        "sentiments": dict(sentiments),
        "top_tags": tag_counter.most_common(10),
    }