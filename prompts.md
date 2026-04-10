# Prompt Engineering Documentation

## 1. Initial Prompt Design
The first iteration focused on simple classification.
**Prompt:** "Classify this feedback as bug, feature_request, or neutral."
**Result:** Too simplistic. Failed to capture sentiment or provide the actionable insights required by management.

## 2. Iteration: Structured Output (JSON)
To integrate with the Python backend, the prompt was updated to enforce JSON formatting.
**Refinement:** Added Pydantic-compatible schemas and the requirement for `tags` and `summary`.
**Goal:** Ensure technical robustness and data consistency.

## 3. Iteration: Category Alignment
Based on v1.1 of the task requirements, categories were updated to:
- Repeated issues or bugs
- Suggestions/feature requests
- Complaints or dissatisfaction
- Neutral or positive feedback
**Goal:** To meet the specific classification standards set by the agency.

## 4. Final Refinement: Decision-Ready Summary
The final summary prompt was designed to move beyond "superficial insights."
**Refinement:** Added `ActionItem` models with `priority` and `rationale`.
**Logic:** Forced the LLM to justify recommendations using data frequencies (e.g., "Recommended because 15 items were tagged as login-fail").