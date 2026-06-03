from __future__ import annotations

from io import StringIO
from typing import Optional, Tuple
import pandas as pd
import requests


def fetch_fred_series(series_id: str) -> pd.DataFrame:
    """Fetch a public FRED CSV series without requiring an API key."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text))
    df.columns = ["Date", "Value"]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    return df.dropna().sort_values("Date")


def fetch_stooq_daily(symbol: str) -> pd.DataFrame:
    """Fetch public daily OHLC data from Stooq. Example symbols: tlt.us, gld.us."""
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.text))
    if df.empty or "Date" not in df.columns:
        raise ValueError(f"No Stooq data returned for {symbol}")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Close"], errors="coerce")
    return df[["Date", "Value"]].dropna().sort_values("Date")


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
