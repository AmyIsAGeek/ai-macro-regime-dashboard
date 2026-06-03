# AI Macro Regime Dashboard

A Streamlit dashboard for tracking whether public market and macro data point toward:

1. **Citrini** — AI labor-displacement / Ghost GDP / credit-stress scenario.
2. **Green** — long-duration Treasury mispricing / high-real-yield opportunity scenario.
3. **Alden** — fiscal-dominance / debasement / gold-reserve-diversification scenario.
4. **Other/Mixed** — regimes that do not cleanly fit the three named scenarios.

## What is included

- `app.py` — the Streamlit dashboard.
- `data/metrics_config.csv` — metric definitions and source links.
- `data/monthly_observations.csv` — monthly metric values and scores.
- `data/scenario_scores.csv` — monthly scenario totals.
- `scripts/fetch_data.py` — public data fetch helpers.
- `scripts/score_scenarios.py` — transparent scenario scoring rules.
- `scripts/update_monthly.py` — monthly update script.
- `.github/workflows/monthly_update.yml` — scheduled GitHub Actions workflow.

## Quick launch on Streamlit Community Cloud

1. Create a GitHub account.
2. Create a private repository named `ai-macro-regime-dashboard`.
3. Upload all files in this folder to the repository.
4. Go to Streamlit Community Cloud.
5. Create a new app from your GitHub repository.
6. Set the app file to `app.py`.
7. Deploy.

## Run the monthly updater manually

In GitHub, go to:

Actions → Monthly data update → Run workflow

## Local test, optional

```bash
pip install -r requirements.txt
python scripts/update_monthly.py --date 2026-05-31
streamlit run app.py
```

## Notes

The first version automates the easiest public data sources, mostly FRED and Stooq. Some metrics remain manual because the cleanest public data are quarterly, semi-structured, or not available without paid sources.

Manual metrics include Treasury auction quality, FDIC unrealized securities losses, World Gold Council central-bank gold purchases, Treasury TIC details, and fiscal receipt breakdowns.
