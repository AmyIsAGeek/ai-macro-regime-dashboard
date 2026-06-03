from __future__ import annotations

from io import StringIO
from typing import Optional, Tuple
from datetime import datetime, timezone
import time

import pandas as pd
import requests


def get_with_retries(url: str, attempts: int = 5, sleep_seconds: int = 5) -> str:
    """Fetch URL text with retries. Helps with temporary DNS/network hiccups."""
    last_error = None

    headers = {
        "User-Agent": "Mozilla/5.0 ai-macro-regime-dashboard/1.0"
    }

    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=75, headers=headers)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_error = e
            if attempt < attempts:
                time.sleep(sleep_seconds)

    raise RuntimeError(f"Failed after {attempts} attempts for {url}: {last_error}")


def fetch_fred_series(series_id: str) -> pd.DataFrame:
    """Fetch a public FRED CSV series without an API key.

    Uses a recent observation window instead of full-history downloads.
    This avoids timeouts for daily series such as Treasury yields.
    """
    url = (
        f"https://fred.stlouisfed.org/graph/fredgraph.csv"
        f"?id={series_id}&cosd=2025-01-01"
    )

    text = get_with_retries(url)

    df = pd.read_csv(StringIO(text))
    df.columns = ["Date", "Value"]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    return df.dropna().sort_values("Date")


def fetch_stooq_daily(symbol: str) -> pd.DataFrame:
    """Legacy fallback.

    Stooq sometimes returns malformed content in cloud environments.
    This function is kept for compatibility, but the dashboard should now use
    YAHOO for ETF proxies.
    """
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d&d1=20250101"
    text = get_with_retries(url)

    if not text.lstrip().startswith("Date,"):
        raise ValueError(f"Stooq returned non-CSV content for {symbol}: {text[:200]}")

    df = pd.read_csv(StringIO(text))
    if df.empty or "Date" not in df.columns:
        raise ValueError(f"No Stooq data returned for {symbol}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Close"], errors="coerce")
    return df[["Date", "Value"]].dropna().sort_values("Date")


def _unix_timestamp(date_str: str) -> int:
    dt = pd.to_datetime(date_str).to_pydatetime()
    return int(datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc).timestamp())


def fetch_yahoo_chart(
    symbol: str,
    start_date: str = "2025-01-01",
    end_date: str = "2030-01-01"
) -> pd.DataFrame:
    """Fetch daily adjusted close data from Yahoo's public chart endpoint.

    This avoids the fragile CSV/crumb download path.
    """
    period1 = _unix_timestamp(start_date)
    period2 = _unix_timestamp(end_date)

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={period1}&period2={period2}&interval=1d"
        f"&events=history&includeAdjustedClose=true"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 ai-macro-regime-dashboard/1.0"
    }

    last_error = None

    for attempt in range(1, 6):
        try:
            r = requests.get(url, timeout=75, headers=headers)
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

            df = pd.DataFrame({
                "Date": pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
                "Value": adjclose,
            })

            df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
            return df.dropna().sort_values("Date")

        except Exception as e:
            last_error = e
            if attempt < 5:
                time.sleep(5)

    raise RuntimeError(f"Failed Yahoo chart fetch after 5 attempts for {symbol}: {last_error}")


def latest_on_or_before(df: pd.DataFrame, target_date: str) -> Tuple[Optional[str], Optional[float]]:
    target = pd.to_datetime(target_date)
    tmp = df[df["Date"] <= target].dropna().sort_values("Date")

    if tmp.empty:
        return None, None

    row = tmp.iloc[-1]
    return row["Date"].strftime("%Y-%m-%d"), float(row["Value"])


def prior_month_value(df: pd.DataFrame, target_date: str) -> Tuple[Optional[str], Optional[float]]:
    target = pd.to_datetime(target_date)
    prior_cutoff = target - pd.DateOffset(months=1)
    tmp = df[df["Date"] <= prior_cutoff].dropna().sort_values("Date")

    if tmp.empty:
        return None, None

    row = tmp.iloc[-1]
    return row["Date"].strftime("%Y-%m-%d"), float(row["Value"])
