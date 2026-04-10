# Client Feedback Analysis – AI-Powered System

An end-to-end Python web app that ingests raw customer feedback (CSV upload or pasted text), uses an LLM to classify and summarize it, and produces structured outputs (CSV export, and a management-ready PDF report).

---

## Features

- Upload CSV or paste text feedback (30+ recommended). 
- Automatic per-item analysis:
  - Category: bug, feature_request, complaint, neutral.
  - Sentiment: positive, neutral, negative.
  - Short summary and tags (key phrases).
- Aggregate insights:
  - Overall sentiment and main themes.
  - Key patterns and trends.
  - Recommended action items for product/management.
- Outputs:
  - Web dashboard with table and stats.
  - Downloadable classified CSV.
  - Downloadable PDF management report.

---

## Tech Stack

- Python 3.10+  
- Flask – web server and templates  
- OpenAI API – LLM-powered analysis  
- Pandas – CSV handling  
- Pydantic – data models  
- WeasyPrint – HTML → PDF export  
- python-dotenv – environment variable loading

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url> client-feedback-ai
cd client-feedback-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=put_shared_API_key_here
```


---

## Project structure

```text
client-feedback-ai/
  app.py
  analysis.py
  llm_client.py
  models.py
  templates/
    index.html
    report.html
  static/
    style.css
  data/
    sample_feedback.csv
  outputs/
    (generated files: CSV, PDF)
  prompts.md
  PROCESS.md
  README.md
  requirements.txt
```

---

## Running the app

From the project root (with the virtual env activated):

```bash
python src/app.py
```

By default, Flask will start on `http://127.0.0.1:5000`.

Open that URL in your browser.

---

## Using the app

1. Open `http://127.0.0.1:5000` in a browser.  
2. Choose one input method:
   - Upload a CSV file with a `feedback_text` column. 
   - Or paste feedback lines into the textarea (one feedback per line).
   - Data directory in the root project contains samples for both methods. 
3. Click “Analyze”.  
4. After processing:
   - View the overall summary, category counts, and sentiment distribution.
   - See a table with each feedback item, its category, sentiment, summary, and tags.
   - Download the classified CSV.
   - Download the management report as PDF (once wired in).

---

## Sample data

Add a CSV file at `data/sample_feedback.csv` with at least:

```csv
feedback_text
"The app keeps logging me out every 5 minutes."
"I would love a dark mode option."
"Support was very helpful, thanks!"
...
```

You can use this to quickly test the system by loading it through the UI.

---

## Documentation (required by the task)

- `prompts.md`  
  - Contains the exact prompts used for:
    - Per-item analysis (classification, sentiment, tags).
    - Global management summary and action items.
  - Includes brief notes on prompt iterations and reasoning.

- `PROCESS.md`  
  - 1–2 pages describing:
    - Data flow from input to output.
    - Classification logic and categories.
    - Key design decisions and trade-offs.

These files are part of the evaluation deliverables for the task.

---

## Notes and limitations

- Analysis quality depends on the LLM; keep prompts strict and use JSON output to reduce errors.
- For larger datasets, consider batching and basic retry logic to handle API limits.
- This project is designed as a compact, reviewable demonstration of end-to-end AI application for client feedback analysis, not a production system.
- **API Key**: Free Groq API key is used (via Groq Cloud).
- **Current Model**: `gpt-oss-120b` (fast and cost-effective).  
  Using a more powerful model (such as Llama 3.3 70B, Mixtral, or Gemma2) would deliver even higher classification accuracy, better summaries, and more insightful recommendations.
---

## Next steps

- Implement `llm_client.py`, `analysis.py`, and `app.py` according to the design.
- Add charts (optional) for category and sentiment distribution on the dashboard.
- Refine prompts based on a few test runs and document the changes in `prompts.md`.
