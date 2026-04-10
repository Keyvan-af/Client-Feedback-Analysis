import os
import io
import datetime
from flask import Flask, render_template, request, send_file
import pandas as pd
from weasyprint import HTML

from analysis import process_feedback, aggregate_stats
from models import FeedbackItem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

analyzed_cache = None
stats_cache = None
summary_cache = None

@app.route("/", methods=["GET", "POST"])
def index():
    global analyzed_cache, stats_cache, summary_cache

    if request.method == "POST":
        df = None
        error = None

        # === FILE UPLOAD (CSV or TXT) ===
        if "file" in request.files and request.files["file"].filename:
            f = request.files["file"]
            filename = f.filename.lower()

            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(f)
                elif filename.endswith('.txt'):
                    # TXT: one feedback per line (exactly like textarea)
                    content = f.read().decode('utf-8')
                    lines = [line.strip() for line in content.splitlines() if line.strip()]
                    df = pd.DataFrame({"feedback_text": lines})
                else:
                    error = "Only .csv or .txt files are allowed."
            except Exception as e:
                error = f"Error reading file: {str(e)}"

        # === DIRECT TEXT INPUT (textarea) ===
        else:
            text = request.form.get("feedback_text", "").strip()
            if text:
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                df = pd.DataFrame({"feedback_text": lines})

        if error:
            return render_template("index.html", error=error)

        if df is None or df.empty:
            return render_template("index.html", error="No feedback provided. Please upload a CSV/TXT or paste text.")

        # Convert to FeedbackItem objects
        items = [
            FeedbackItem(id=i+1, text=row["feedback_text"])
            for i, row in df.iterrows()
        ]

        print(f"→ POST received — {len(items)} items from {'file' if 'file' in request.files else 'textarea'}")

        analyzed_cache, summary_cache = process_feedback(items)
        stats_cache = aggregate_stats(analyzed_cache)

        return render_template(
            "index.html",
            table=analyzed_cache,
            stats=stats_cache,
            summary=summary_cache.model_dump() if summary_cache else {},
            today=datetime.date.today().strftime("%d %B %Y")
        )

    return render_template("index.html")

@app.route("/download/csv")
def download_csv():
    if not analyzed_cache:
        return "No data available", 400
    df = pd.DataFrame([a.model_dump() for a in analyzed_cache])
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(
        io.BytesIO(buf.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="classified_feedback.csv",
    )


@app.route("/download/report")
def download_report():
    if not analyzed_cache:
        return "No data available", 400
    html = render_template(
        "report.html",
        stats=stats_cache,
        items=analyzed_cache[:10],
        summary=summary_cache.model_dump() if summary_cache else {},
        today=datetime.date.today().strftime("%d %B %Y")
    )
    pdf = HTML(string=html).write_pdf()
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="management_report.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)