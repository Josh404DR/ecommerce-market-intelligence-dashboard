# assets/

This folder holds preview images referenced by the main `README.md`. They are
**not auto-generated** by the pipeline (no headless browser is available in
this environment), so two screenshots need to be added manually:

## 1. `dashboard_preview.png`

1. Run the pipeline once (`python src/generate_mock_data.py && python src/clean_data.py && python src/analyze_data.py`).
2. Open `dashboard/index.html` directly in a browser.
3. Take a screenshot of the full dashboard view.
4. Save it as `assets/dashboard_preview.png` (PNG, ~1200–1600px wide looks best on GitHub).

## 2. `summary_report_preview.png`

1. Open `outputs/summary_report.md` in a Markdown previewer (VS Code preview,
   GitHub's own render, or any Markdown-to-HTML viewer).
2. Screenshot the Executive Summary + Insight 1–2 section (enough to show the
   report's business-report style at a glance).
3. Save it as `assets/summary_report_preview.png`.

Once both files exist, the image references already in `README.md` will
render automatically — no further README edits are needed.
