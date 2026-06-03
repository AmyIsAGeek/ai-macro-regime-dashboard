from __future__ import annotations

from typing import Dict, Tuple
import math


def pct_change(value: float | None, prior: float | None) -> float | None:
    if value is None or prior is None or prior == 0:
        return None
    return (value - prior) / abs(prior) * 100.0


def bps_change(value: float | None, prior: float | None) -> float | None:
    if value is None or prior is None:
        return None
    return (value - prior) * 100.0


def classify_metric(metric_id: str, value: float | None, prior: float | None) -> Dict[str, object]:
    """Return scenario tilt and strength from simple transparent first-pass rules.

    Strength scale:
      0 = neutral/no data
      1 = weak
      2 = moderate
      3 = strong
    """
    if value is None:
        return {"tilt": "Neutral", "strength": 0, "notes": "No public auto value available."}

    change_pct = pct_change(value, prior)
    change_bps = bps_change(value, prior)

    # Rates and inflation.
    if metric_id == "M01":  # 30Y nominal yield
        if value >= 5.25 and (change_bps is None or change_bps <= 25):
            return {"tilt": "Green", "strength": 2, "notes": "High 30Y nominal yield supports Green's income/duration valuation case."}
        if change_bps is not None and change_bps >= 40:
            return {"tilt": "Alden", "strength": 2, "notes": "Disorderly long-yield rise can indicate term-premium/fiscal pressure."}
        return {"tilt": "Neutral", "strength": 1, "notes": "30Y yield is informative but not decisive this month."}

    if metric_id == "M02":  # 30Y TIPS real yield
        if value >= 2.75:
            return {"tilt": "Green", "strength": 3, "notes": "Very high 30Y real yield supports Green's long-TIPS valuation case."}
        if value >= 2.25:
            return {"tilt": "Green", "strength": 2, "notes": "High 30Y real yield supports Green."}
        if change_bps is not None and change_bps >= 30:
            return {"tilt": "Alden", "strength": 1, "notes": "Rising real yields may reflect higher risk premium; confirm against gold and auctions."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Real yield not strong enough alone."}

    if metric_id in ("M03", "M04"):  # breakevens
        if value >= 3.00:
            return {"tilt": "Alden", "strength": 3, "notes": "High breakeven inflation supports Alden's debasement/inflation concern."}
        if value >= 2.75:
            return {"tilt": "Alden", "strength": 2, "notes": "Elevated breakeven inflation supports Alden."}
        if value <= 2.10:
            return {"tilt": "Green", "strength": 2, "notes": "Contained breakevens support Green's real-yield opportunity."}
        if value <= 2.40:
            return {"tilt": "Green", "strength": 1, "notes": "Breakevens remain broadly contained."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Breakeven is mid-range."}

    if metric_id == "M05":  # term premium
        if change_bps is not None and change_bps >= 20:
            return {"tilt": "Alden", "strength": 2, "notes": "Rising term premium supports fiscal/supply-risk concern."}
        if change_bps is not None and change_bps <= -20:
            return {"tilt": "Green", "strength": 2, "notes": "Term-premium compression supports long-duration demand."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Term-premium move is not decisive."}

    # ETF prices.
    if metric_id == "M06":  # TLT
        if change_pct is not None and change_pct >= 5:
            return {"tilt": "Green", "strength": 3, "notes": "Strong long-bond rally supports Green or early Citrini; check labor/credit data."}
        if change_pct is not None and change_pct >= 2:
            return {"tilt": "Green", "strength": 2, "notes": "Long-bond rally supports Green."}
        if change_pct is not None and change_pct <= -5:
            return {"tilt": "Other", "strength": 2, "notes": "Long bonds fell; likely higher real-rate/liquidity/fiscal pressure. Check gold to distinguish Alden."}
        return {"tilt": "Neutral", "strength": 1, "notes": "TLT price action is small."}

    if metric_id == "M07":  # GLD
        if change_pct is not None and change_pct >= 5:
            return {"tilt": "Alden", "strength": 3, "notes": "Gold rally supports Alden; confirm against real yields and dollar."}
        if change_pct is not None and change_pct >= 2:
            return {"tilt": "Alden", "strength": 2, "notes": "Gold strength supports Alden."}
        if change_pct is not None and change_pct <= -5:
            return {"tilt": "Green", "strength": 1, "notes": "Gold weakness may support Green if real yields remain high."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Gold move is small."}

    if metric_id == "M08":  # UUP / dollar proxy
        return {"tilt": "Neutral", "strength": 1, "notes": "Dollar proxy is a context metric; interpret with gold."}

    # Labor.
    if metric_id in ("M13", "M14"):
        if change_bps is not None and change_bps >= 30:
            return {"tilt": "Citrini", "strength": 3, "notes": "Unemployment/underemployment jumped materially."}
        if change_bps is not None and change_bps >= 10:
            return {"tilt": "Citrini", "strength": 2, "notes": "Unemployment/underemployment rose."}
        return {"tilt": "Neutral", "strength": 1, "notes": "No decisive labor deterioration."}

    if metric_id in ("M15", "M16", "M17", "M19", "M20", "M21"):
        if change_pct is not None and change_pct <= -2.0:
            return {"tilt": "Citrini", "strength": 3, "notes": "Labor/income metric deteriorated sharply."}
        if change_pct is not None and change_pct <= -0.75:
            return {"tilt": "Citrini", "strength": 2, "notes": "Labor/income metric deteriorated."}
        return {"tilt": "Neutral", "strength": 1, "notes": "No decisive labor/income deterioration."}

    if metric_id == "M18":  # initial claims
        if change_pct is not None and change_pct >= 15:
            return {"tilt": "Citrini", "strength": 3, "notes": "Initial claims rose sharply."}
        if change_pct is not None and change_pct >= 7.5:
            return {"tilt": "Citrini", "strength": 2, "notes": "Initial claims rose."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Claims are not sending a strong Citrini signal."}

    # Credit.
    if metric_id == "M22":
        if value >= 6.0:
            return {"tilt": "Citrini", "strength": 3, "notes": "High-yield spreads indicate substantial credit stress."}
        if value >= 4.5:
            return {"tilt": "Citrini", "strength": 2, "notes": "High-yield spreads are widening into stress range."}
        if value <= 3.25:
            return {"tilt": "Other", "strength": 2, "notes": "Tight credit spreads argue against active Citrini crisis."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Credit spreads are mid-range."}

    if metric_id == "M23":
        if value >= 40:
            return {"tilt": "Citrini", "strength": 3, "notes": "Loan standards are tightening materially."}
        if value >= 20:
            return {"tilt": "Citrini", "strength": 2, "notes": "Loan standards are tightening."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Loan standards are not decisively tight."}

    if metric_id == "M24":
        if change_pct is not None and change_pct <= -1.0:
            return {"tilt": "Citrini", "strength": 2, "notes": "Bank credit contracted."}
        return {"tilt": "Neutral", "strength": 1, "notes": "Bank credit did not contract materially."}

    return {"tilt": "Neutral", "strength": 0, "notes": "Manual or unclassified metric."}


def score_from_tilt(tilt: str, strength: int, row) -> Dict[str, float]:
    c = g = a = other = 0.0
    if tilt == "Citrini":
        c = strength * float(row.get("Weight_Citrini", 0))
    elif tilt == "Green":
        g = strength * float(row.get("Weight_Green", 0))
    elif tilt == "Alden":
        a = strength * float(row.get("Weight_Alden", 0))
    elif tilt == "Other":
        other = strength * 4.0
    return {"CitriniScore": c, "GreenScore": g, "AldenScore": a, "OtherScore": other}
