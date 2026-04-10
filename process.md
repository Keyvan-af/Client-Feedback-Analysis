# Process and System Explanation

## System Architecture
The Client Feedback Analysis tool is a Flask-based web application that utilizes LLMs to transform unstructured text into structured insights.

## Data Flow
1. **Input:** Users provide data via CSV upload or direct text input (app.py).
2. **Preprocessing:** Data is converted into Pydantic `FeedbackItem` objects for type safety (analysis.py).
3. **Batch Processing:** To handle large datasets without hitting token limits, feedback is split into batches of 15 items (llm_client.py).
4. **AI Analysis:** Each batch is sent to the LLM for classification and tagging.
5. **Executive Summarization:** A second specialized prompt analyzes the aggregated results to generate a prioritized management summary.
6. **Output:** Results are displayed in a web UI and available for export as CSV or PDF (report.html).

## Classification Logic
- **Categorization:** Uses a zero-shot classification approach where the model maps text to the four required project categories based on semantic intent.
- **Sentiment Analysis:** Determined at the item level to help weight the priority of recommended actions.
- **Actionability:** The system uses a "Senior Product Manager" persona in the summary prompt to ensure insights are directly usable by product teams.

## Key Decisions and Trade-offs
* **Methodology Selection (LLM vs. Traditional NLP):**  For extremely large datasets (thousands of rows), traditional techniques like **LDA (Latent Dirichlet Allocation)** or **Clustering** are standard as they avoid the high latency and significant costs of repeated LLM API calls.
    * However, LDA and Clustering are often less accurate for specific classification tasks and do not inherently support pre-determined, rigid categories.
    * For this task, **LLM Prompt Engineering** was chosen because the dataset is of a manageable size (30–60+ rows) and requires high precision against four specific, mandatory categories. This ensures "decision-ready" accuracy that unsupervised clustering cannot guarantee.

* **Batch Size Strategy:** The system utilizes a **Batch Size of 15**. While the model can technically accept more, larger batches frequently resulted in "Unterminated string" errors due to output token limits. 
    * Reducing the size ensures every item is successfully validated by the Pydantic schema, maintaining 100% data integrity for the management report.

* **Hyperparameter Tuning:**
    * The **Temperature was set to 0.1** to prioritize reliability. In a classification system, "creativity" from the AI is a risk that leads to malformed JSON; a near-zero temperature ensures the model remains focused on the provided instructions and schema.

* **Token-Efficient Summarization:** To generate the `ManagementSummary`, the system strips out the raw feedback text and only sends categories, sentiments, and tags to the model.
This trade-off prioritizes the model's "reasoning space" for analysis over redundant data processing, preventing response truncation.
