from __future__ import annotations

from typing import Optional, Tuple
from datetime import datetime, timezone
import os
import time

import pandas as pd
import requests


def _headers() -> dict:
    return {"User-Agent": "Mozilla/5.0 ai-macro-regime-dashboard/1.0"}


def get_json_with_retries(
    url: str,
    params: dict,
    attempts: int = 2,
    sleep_seconds: int = 2,
    timeout_seconds: int = 20,
) -> dict:
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout_seconds, headers=_headers())
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_error = e
            if attempt < attempts:
                time.sleep(sleep_seconds)

    raise RuntimeError(f"JSON fetch failed for {url}: {last_error}")


def get_text_with_retries(
    url: str,
    attempts: int = 1,
    sleep_seconds: int = 1,
    timeout_seconds: int = 8,
) -> str:
    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=timeout_seconds, headers=_headers())
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_error = e
            if attempt < attempts:
                time.sleep(sleep_seconds)

    raise RuntimeError(f"Text fetch failed for {url}: {last_error}")


def _window_start(target_date: str, days_back: int = 180) -> str:
    target = pd.to_datetime(target_date)
    start = target - pd.Timedelta(days=days_back)
    return start.strftime("%Y-%m-%d")


def fetch_fred_series(series_id: str, target_date: str | None = None) -> pd.DataFrame:
    """Fetch a FRED series through the official FRED API.

    Requires FRED_API_KEY to be set as an environment variable.
    """
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FRED_API_KEY is missing. Add it as a GitHub Actions repository secret."
        )

    if target_date:
        observation_start = _window_start(target_date, days_back=180)
        observation_end = target_date
    else:
        observation_start = "2025-01-01"
        observation_end = datetime.now().strftime("%Y-%m-%d")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
        "observation_end": observation_end,
    }

    payload = get_json_with_retries(url, params=params)

    observations = payload.get("observations", [])
    if not observations:
        raise ValueError(f"No FRED observations returned for {series_id}: {payload}")

    df = pd.DataFrame(observations)
    df["Date"] = pd.to_datetime(df["date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["Date", "Value"]].dropna().sort_values("Date")


def _unix_timestamp(date_str: str) -> int:
    dt = pd.to_datetime(date_str).to_pydatetime()
    return int(datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc).timestamp())


def fetch_yahoo_chart(
    symbol: str,
    start_date: str = "2025-01-01",
    end_date: str = "2030-01-01",
) -> pd.DataFrame:
    """Fetch daily adjusted close data from Yahoo's public chart endpoint."""
    period1 = _unix_timestamp(start_date)
    period2 = _unix_timestamp(end_date)

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={period1}&period2={period2}&interval=1d"
        f"&events=history&includeAdjustedClose=true"
    )

    r = requests.get(url, timeout=10, headers=_headers())
    r.raise_for_status()
    payload = r.json()

    result = payload.get("chart", {}).get("result", [])
    if not result:
        raise ValueError(f"No Yahoo chart result for {symbol}: {payload}")

    result = result[0]
    timestamps = result.get("timestamp", [])
    adjclose = (
        result.get("indicators", {})
        .get("adjclose", [{}])[0]
        .get("adjclose", [])
    )

    if not timestamps or not adjclose:
        raise ValueError(f"Missing timestamp/adjclose data for {symbol}")

    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                timestamps,
                unit="s",
                utc=True,
            ).tz_convert(None).normalize(),
            "Value": adjclose,
        }
    )

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    return df.dropna().sort_values("Date")


def fetch_stooq_daily(symbol: str) -> pd.DataFrame:
    """Legacy fallback retained for compatibility."""
    from io import StringIO

    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d&d1=20250101"
    text = get_text_with_retries(url)

    if not text.lstrip().startswith("Date,"):
        raise ValueError(f"Stooq returned non-CSV content for {symbol}: {text[:200]}")

    df = pd.read_csv(StringIO(text))
    if df.empty or "Date" not in df.columns:
        raise ValueError(f"No Stooq data returned for {symbol}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Close"], errors="coerce")
    return df[["Date", "Value"]].dropna().sort_values("Date")


def latest_on_or_before(
    df: pd.DataFrame,
    target_date: str,
) -> Tuple[Optional[str], Optional[float]]:
    target = pd.to_datetime(target_date)
    tmp = df[df["Date"] <= target].dropna().sort_values("Date")

    if tmp.empty:
        return None, None

    row = tmp.iloc[-1]
    return row["Date"].strftime("%Y-%m-%d"), float(row["Value"])


def prior_month_value(
    df: pd.DataFrame,
    target_date: str,
) -> Tuple[Optional[str], Optional[float]]:
    target = pd.to_datetime(target_date)
    prior_cutoff = target - pd.DateOffset(months=1)
    tmp = df[df["Date"] <= prior_cutoff].dropna().sort_values("Date")

    if tmp.empty:
        return None, None

    row = tmp.iloc[-1]
    return row["Date"].strftime("%Y-%m-%d"), float(row["Value"])
