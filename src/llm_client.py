import json
from typing import List

from decouple import config
from openai import OpenAI
from pydantic import ValidationError

from models import ActionItem, FeedbackItem, AnalyzedFeedbackItem, ManagementSummary

api_key = config("GROQ_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

BATCH_SIZE = 15

SYSTEM_PROMPT = """
You are an AI that analyzes customer feedback and returns STRICT JSON.
You will receive a batch of feedback items. You MUST analyze EVERY item.

For each item, produce:
- id: integer
- category: MUST be one of ["Repeated issues or bugs", "Suggestions/feature requests", "Complaints or dissatisfaction", "Neutral or positive feedback"]
- sentiment: one of ["negative", "neutral", "positive"]
- summary: 1–2 sentence summary
- tags: list of 2–5 short key phrases

Output format:
[
  {"id": 1, "category": "Repeated issues or bugs", "sentiment": "negative", "summary": "...", "tags": [...]},
  ...
]

Rules:
- Output ONLY the JSON array.
- Do NOT use backticks or markdown formatting.
- Ensure the number of items in output matches the input.
""".strip()

SUMMARY_SYSTEM_PROMPT = """
You are a Senior Product Manager. You are provided with a list of classified customer feedback.
Your goal is to provide a DECISION-READY report for leadership.

Analyze the frequencies of categories, sentiments, and tags.

Output **EXACTLY** this JSON structure (no extra text, no markdown, no backticks):

{
  "overall_summary": "2-3 paragraphs. Start with high-level sentiment trend. Use specific volumes (e.g. '42% of feedback items are...')",
  "key_themes": ["Theme 1 here", "Theme 2 here", "Theme 3 here", "Theme 4 here", "Theme 5 here"],
  "recommended_actions": [
    {
      "action": "Specific actionable task",
      "priority": "High",
      "rationale": "Data-backed reason mentioning exact numbers or tags"
    }
  ]
}

STRICT RULES:
- key_themes MUST be a plain list of 5 strings (only the theme name, NO counts, NO objects, NO dictionaries).
- recommended_actions must contain 4-6 items.
- overall_summary must be 2-3 full paragraphs.
- Use real numbers from the data (e.g. "8 items tagged with 'login-fail'").
- Output ONLY valid JSON. Nothing else.
""".strip()

def _call_model_for_batch(items: List[FeedbackItem]) -> str:
    user_payload = {"feedback_items": [{"id": it.id, "text": it.text} for it in items]}

    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()


def _call_model_for_summary(analyzed_items: List[AnalyzedFeedbackItem]) -> str:
    payload = [item.model_dump() for item in analyzed_items]

    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()

def analyze_feedback_items(items: List[FeedbackItem]) -> List[AnalyzedFeedbackItem]:
    all_results: List[AnalyzedFeedbackItem] = []
    text_lookup = {item.id: item.text for item in items} # Map text back to IDs

    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        raw_content = _call_model_for_batch(batch)

        try:
            parsed_list = json.loads(raw_content)
            for item_data in parsed_list:
                # Re-attach the text field before validation
                item_id = item_data.get("id")
                item_data["text"] = text_lookup.get(item_id, "Text not found")
                
                # Validate and add to results
                all_results.append(AnalyzedFeedbackItem.model_validate(item_data))
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"❌ Batch failed: {e}")

    return all_results

def generate_management_summary(items: List[AnalyzedFeedbackItem]) -> ManagementSummary:
    print(f"Generating decision-ready summary for {len(items)} items...")
    raw_content = _call_model_for_summary(items)

    try:
        parsed = json.loads(raw_content)
        # The new structure will be validated here
        summary = ManagementSummary.model_validate(parsed)
        print("✓ Decision-ready summary generated")
        return summary
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"❌ Summary generation failed: {e}")
        # Robust Fallback for the new structure
        return ManagementSummary(
            overall_summary="Analysis failed. Please check technical logs.",
            key_themes=["Error"],
            recommended_actions=[
                ActionItem(action="Check API Logs", priority="High", rationale="System failed to parse LLM output")
            ]
        )