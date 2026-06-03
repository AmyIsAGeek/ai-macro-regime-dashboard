from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from fetch_data import (
    fetch_fred_series,
    fetch_stooq_daily,
    fetch_yahoo_chart,
    latest_on_or_before,
    prior_month_value,
)
from score_scenarios import classify_metric, score_from_tilt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG = DATA / "metrics_config.csv"
OBS = DATA / "monthly_observations.csv"
SCORES = DATA / "scenario_scores.csv"


def update_for_month(target_date: str) -> None:
    config = pd.read_csv(CONFIG)
    obs = pd.read_csv(OBS)

    # Ensure all metric rows exist for target date.
    existing = set(zip(obs["Date"].astype(str), obs["MetricID"].astype(str)))

    new_rows = []
    for _, metric in config.iterrows():
        metric_id = str(metric["MetricID"])

        if (target_date, metric_id) not in existing:
            new_rows.append(
                {
                    "Date": target_date,
                    "MetricID": metric_id,
                    "Value": "",
                    "PriorValue": "",
                    "MonthlyChange": "",
                    "Unit": metric["Unit"],
                    "CitriniScore": 0,
                    "GreenScore": 0,
                    "AldenScore": 0,
                    "OtherScore": 0,
                    "Tilt": "Neutral",
                    "Strength": 0,
                    "WeightUsed": "",
                    "Notes": "Placeholder created by updater.",
                    "SourceURL": metric["PublicSourceURL"],
                    "LastUpdated": date.today().strftime("%Y-%m-%d"),
                    "IsManual": "Yes" if metric["AutoStatus"] == "Manual" else "No",
                }
            )

    if new_rows:
        obs = pd.concat([obs, pd.DataFrame(new_rows)], ignore_index=True)

    # Update automatable metrics.
    for _, metric in config.iterrows():
        metric_id = str(metric["MetricID"])
        source_type = str(metric["SourceType"]).upper()
        source_id = str(metric.get("SourceID", "") or "")

        mask = (obs["Date"].astype(str) == target_date) & (
            obs["MetricID"].astype(str) == metric_id
        )

        # Manual metrics remain placeholders unless user edits CSV.
        if source_type == "MANUAL":
            continue

        value = None
        prior = None
        obs_date = None

        if source_type == "FRED":
            try:
                series = fetch_fred_series(source_id)
                obs_date, value = latest_on_or_before(series, target_date)
                prior_date, prior = prior_month_value(series, target_date)
            except Exception as e:
                obs.loc[mask, "Notes"] = f"Auto-update failed for FRED {source_id}: {e}"
                obs.loc[mask, "LastUpdated"] = date.today().strftime("%Y-%m-%d")
                continue

        elif source_type == "YAHOO":
            try:
                series = fetch_yahoo_chart(
                    source_id,
                    start_date="2025-01-01",
                    end_date="2030-01-01",
                )
                obs_date, value = latest_on_or_before(series, target_date)
                prior_date, prior = prior_month_value(series, target_date)
            except Exception as e:
                obs.loc[mask, "Notes"] = f"Auto-update failed for Yahoo {source_id}: {e}"
                obs.loc[mask, "LastUpdated"] = date.today().strftime("%Y-%m-%d")
                continue

        elif source_type == "STOOQ":
            try:
                series = fetch_stooq_daily(source_id)
                obs_date, value = latest_on_or_before(series, target_date)
                prior_date, prior = prior_month_value(series, target_date)
            except Exception as e:
                obs.loc[mask, "Notes"] = f"Auto-update failed for Stooq {source_id}: {e}"
                obs.loc[mask, "LastUpdated"] = date.today().strftime("%Y-%m-%d")
                continue

        elif source_type == "DERIVED" and source_id == "DGS30-DFII30":
            try:
                nominal = fetch_fred_series("DGS30")
                real = fetch_fred_series("DFII30")

                n_date, n_value = latest_on_or_before(nominal, target_date)
                r_date, r_value = latest_on_or_before(real, target_date)

                pn_date, pn_value = prior_month_value(nominal, target_date)
                pr_date, pr_value = prior_month_value(real, target_date)

                obs_date = min(n_date, r_date) if n_date and r_date else None
                value = None if n_value is None or r_value is None else n_value - r_value
                prior = None if pn_value is None or pr_value is None else pn_value - pr_value

            except Exception as e:
                obs.loc[mask, "Notes"] = (
                    f"Auto-update failed for derived DGS30-DFII30: {e}"
                )
                obs.loc[mask, "LastUpdated"] = date.today().strftime("%Y-%m-%d")
                continue

        else:
            obs.loc[mask, "Notes"] = (
                f"No updater available for SourceType={source_type}, SourceID={source_id}."
            )
            obs.loc[mask, "LastUpdated"] = date.today().strftime("%Y-%m-%d")
            continue

        # Classify and score.
        classification = classify_metric(metric_id, value, prior)
        score = score_from_tilt(
            classification["tilt"],
            int(classification["strength"]),
            metric,
        )

        monthly_change = "" if value is None or prior is None else value - prior

        obs.loc[mask, "Value"] = "" if value is None else round(float(value), 4)
        obs.loc[mask, "PriorValue"] = "" if prior is None else round(float(prior), 4)
        obs.loc[mask, "MonthlyChange"] = (
            "" if monthly_change == "" else round(float(monthly_change), 4)
        )
        obs.loc[mask, "Unit"] = metric["Unit"]
        obs.loc[mask, "CitriniScore"] = score["CitriniScore"]
        obs.loc[mask, "GreenScore"] = score["GreenScore"]
        obs.loc[mask, "AldenScore"] = score["AldenScore"]
        obs.loc[mask, "OtherScore"] = score["OtherScore"]
        obs.loc[mask, "Tilt"] = classification["tilt"]
        obs.loc[mask, "Strength"] = classification["strength"]
        obs.loc[mask, "WeightUsed"] = max(
            float(metric["Weight_Citrini"]),
            float(metric["Weight_Green"]),
            float(metric["Weight_Alden"]),
        )
        obs.loc[mask, "Notes"] = (
            f"Auto observation date {obs_date}. {classification['notes']}"
        )
        obs.loc[mask, "SourceURL"] = metric["PublicSourceURL"]
        obs.loc[mask, "LastUpdated"] = date.today().strftime("%Y-%m-%d")
        obs.loc[mask, "IsManual"] = "No"

    # Sort and save observations.
    obs = obs.sort_values(["Date", "MetricID"])
    obs.to_csv(OBS, index=False)

    # Recalculate scenario summary for all available dates.
    grouped = obs.groupby("Date", as_index=False)[
        ["CitriniScore", "GreenScore", "AldenScore", "OtherScore"]
    ].sum()

    rows = []
    for _, r in grouped.iterrows():
        values = {
            "Citrini": float(r["CitriniScore"]),
            "Green": float(r["GreenScore"]),
            "Alden": float(r["AldenScore"]),
            "Other": float(r["OtherScore"]),
        }

        leader = max(values, key=values.get)
        sorted_values = sorted(values.values(), reverse=True)
        top_score = sorted_values[0]
        gap = sorted_values[0] - sorted_values[1] if len(sorted_values) > 1 else top_score

        if top_score <= 0:
            leader_label = "Insufficient data"
            confidence = "Low"
        else:
            leader_label = leader
            confidence = "High" if gap >= 20 else "Medium" if gap >= 10 else "Low"

        rows.append(
            {
                "Date": r["Date"],
                "Citrini": values["Citrini"],
                "Green": values["Green"],
                "Alden": values["Alden"],
                "Other": values["Other"],
                "Leader": leader_label,
                "Confidence": confidence,
            }
        )

    pd.DataFrame(rows).to_csv(SCORES, index=False)

    print(f"Updated dashboard data for {target_date}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        default=date.today().strftime("%Y-%m-%d"),
        help="Target date, YYYY-MM-DD. For month-end tracking, use the month-end date.",
    )
    args = parser.parse_args()

    update_for_month(args.date)
