# Manual Data Entry Guide

This guide explains how to update the dashboard metrics that are not currently automated.

## Manual Metrics

The current manual or semi-manual metrics are:

| Metric ID | Metric | Update Frequency |
|---|---|---|
| M09 | 30Y Treasury auction tail | Monthly |
| M10 | 30Y Treasury bid-to-cover | Monthly |
| M11 | 30Y Treasury indirect bidder share | Monthly |
| M12 | 30Y Treasury primary dealer takedown | Monthly |
| M25 | FDIC unrealized securities losses | Quarterly |
| M26 | Central-bank gold purchases | Quarterly |
| M27 | Foreign Treasury holdings | Monthly |
| M28 | Federal deficit trailing 12 months | Monthly |
| M29 | Net interest outlays | Monthly |
| M30 | Individual income and payroll tax receipts | Monthly |

## Monthly Workflow

### 1. Run the automated monthly update first

In GitHub:

1. Open the repository.
2. Click **Actions**.
3. Click **Monthly data update**.
4. Click **Run workflow**.
5. Enter the target date in `YYYY-MM-DD` format.
6. Wait for the workflow to finish successfully.

This creates placeholder rows for the manual metrics in:

```text
data/monthly_observations.csv
```

### 2. Open the observations file

In GitHub:

1. Click **Code**.
2. Open the `data` folder.
3. Open `monthly_observations.csv`.
4. Click the pencil icon to edit the file.

### 3. Find the manual rows for the target date

Use your browser search command:

```text
Command + F
```

Search for a row such as:

```text
2026-06-30,M09
```

Then update the manual rows for the same target date.

### 4. Enter the required fields

For each manual metric, update at least:

- `Value`
- `PriorValue`
- `MonthlyChange`
- `Tilt`
- `Strength`
- the appropriate scenario score
- `WeightUsed`
- `Notes`
- `SourceURL`
- `LastUpdated`

Leave:

```text
IsManual
```

as:

```text
Yes
```

### 5. Use the scoring rule

```text
Scenario score = Strength × relevant scenario weight
```

Strength scale:

| Strength | Meaning |
|---:|---|
| 0 | Neutral, missing, or inconclusive |
| 1 | Weak signal |
| 2 | Moderate signal |
| 3 | Strong signal |

Only one scenario score should normally be positive for a manual metric. The other scenario score fields should usually be zero.

Example:

```text
Tilt = Alden
Strength = 2
WeightUsed = 5
AldenScore = 10
CitriniScore = 0
GreenScore = 0
OtherScore = 0
```

### 6. Commit the CSV edit

Commit with a message such as:

```text
Add June manual metric data
```

### 7. Re-run the monthly workflow

Run the same target date again:

```text
Actions → Monthly data update → Run workflow
```

The updater will preserve the manual rows and recalculate:

```text
data/scenario_scores.csv
```

### 8. Refresh the Streamlit app

1. Open the Streamlit dashboard.
2. Refresh or reboot the app.
3. Select the target date.
4. Check the Metric table and scenario scores.

---

# Public Sources and Calculation Instructions

## M09–M12: 30-Year Treasury Auction Metrics

Primary source:

- TreasuryDirect Announcements, Data & Results  
  https://www.treasurydirect.gov/auctions/announcements-data-results/

Use the most recent **30-Year Bond** auction result.

### M09 — 30Y Treasury auction tail

Formula:

```text
Auction tail =
Auction high yield
− When-issued yield immediately before the auction
```

- Positive value = tail
- Negative value = stop-through

TreasuryDirect publishes the auction high yield but does not publish the pre-auction when-issued yield. Use a reputable market report for the when-issued yield.

If you cannot obtain a reliable when-issued yield, leave M09 blank rather than guessing.

### M10 — 30Y Treasury bid-to-cover

Copy the published **Bid-to-Cover Ratio** directly from the auction result.

Example:

```text
Value: 2.30
Unit: ratio
```

### M11 — 30Y Treasury indirect bidder share

Formula:

```text
Indirect bidder share =
Indirect bidder competitive accepted amount
÷ Total competitive accepted amount
× 100
```

Example:

```text
Indirect accepted amount: $16.6 billion
Total competitive accepted amount: $24.9 billion

Indirect bidder share = 16.6 ÷ 24.9 × 100 = 66.7%
```

### M12 — 30Y Treasury primary dealer takedown

Formula:

```text
Primary dealer takedown =
Primary dealer competitive accepted amount
÷ Total competitive accepted amount
× 100
```

Example:

```text
Primary dealer accepted amount: $2.9 billion
Total competitive accepted amount: $24.9 billion

Primary dealer takedown = 2.9 ÷ 24.9 × 100 = 11.6%
```

---

## M25 — FDIC Unrealized Securities Losses

Primary source:

- FDIC Quarterly Banking Profile  
  https://www.fdic.gov/analysis/quarterly-banking-profile

Enter the FDIC-reported total unrealized losses on available-for-sale and held-to-maturity securities.

Recommended entry format:

```text
Value: total unrealized losses
Unit: $ billions
PriorValue: prior quarter total
MonthlyChange: current quarter total minus prior quarter total
```

Use the latest available quarterly value until the next Quarterly Banking Profile is released.

---

## M26 — Central-Bank Gold Purchases

Primary source:

- World Gold Council Gold Demand Trends  
  https://www.gold.org/goldhub/research/gold-demand-trends

Enter the latest net central-bank gold purchases in tonnes.

Recommended entry format:

```text
Value: current quarter net purchases
Unit: tonnes
PriorValue: prior quarter net purchases
MonthlyChange: current quarter minus prior quarter
```

Use the latest available quarterly value until the next report is published.

---

## M27 — Foreign Treasury Holdings

Primary sources:

- Treasury International Capital System  
  https://home.treasury.gov/data/treasury-international-capital-tic-system

- TIC Table 5: Major Foreign Holders of Treasury Securities  
  https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html

Enter the total foreign holdings of U.S. Treasury securities in billions of dollars.

Recommended entry format:

```text
Value: latest total foreign Treasury holdings
PriorValue: prior month total
MonthlyChange: latest total minus prior month total
Unit: $ billions
```

TIC data are lagged. Use the latest available month rather than estimating the current month.

---

## M28–M30: Fiscal Metrics

Primary source:

- Monthly Treasury Statement through Fiscal Data  
  https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/

For consistency, use trailing 12-month totals. This reduces seasonal distortion.

### M28 — Federal deficit trailing 12 months

Formula:

```text
Trailing 12-month federal deficit =
Sum of the latest 12 monthly deficits
```

Enter the deficit as a positive number.

Recommended entry format:

```text
Value: trailing 12-month deficit
Unit: $ billions
```

### M29 — Net interest outlays

Use the Monthly Treasury Statement category for **Net Interest**.

Formula:

```text
Trailing 12-month net interest =
Sum of the latest 12 monthly net-interest outlays
```

Recommended entry format:

```text
Value: trailing 12-month net interest
Unit: $ billions
```

### M30 — Individual income and payroll tax receipts

Use:

```text
Individual Income Taxes
+
Social Insurance and Retirement Receipts
```

Formula:

```text
Trailing 12-month labor-linked tax receipts =
Sum of the latest 12 months of
Individual Income Taxes
+
Social Insurance and Retirement Receipts
```

Recommended entry format:

```text
Value: trailing 12-month labor-linked tax receipts
Unit: $ billions
```

This metric is especially relevant to the Citrini scenario because it tracks the government's labor-income tax base.

---

# Tilt and Strength Guidance

## M09–M12: Treasury Auction Metrics

| Signal | Green | Alden |
|---|---|---|
| Auction tail | Stop-through or near-zero tail | Repeated positive tails |
| Bid-to-cover | Strong, roughly above 2.40 | Weak, roughly below 2.20 |
| Indirect bidder share | Strong, roughly above 68% | Weak, roughly below 60% |
| Primary dealer takedown | Low, roughly below 12% | High, roughly above 18% |

Use:

- Strength 1 when only one component is mildly supportive.
- Strength 2 when multiple components agree.
- Strength 3 when the signal is large or repeats across several auctions.

## M25: FDIC Unrealized Losses

| Pattern | Tilt |
|---|---|
| Large losses persist and impair bank balance sheets | Green |
| Losses trigger broad rescue, QE, or monetization concerns | Alden |
| Losses decline or remain non-systemic | Neutral |

## M26: Central-Bank Gold Purchases

| Quarterly Purchases | Tilt | Strength |
|---:|---|---:|
| Less than 50 tonnes or net selling | Green or Neutral | 2–3 |
| 50–150 tonnes | Neutral | 1 |
| 150–250 tonnes | Alden | 1–2 |
| More than 250 tonnes | Alden | 3 |

## M27: Foreign Treasury Holdings

| Monthly Change | Tilt | Strength |
|---:|---|---:|
| Increase of more than 1% | Green | 2 |
| Change between -0.5% and +0.5% | Neutral | 0–1 |
| Decline of more than 1% | Alden | 2 |
| Persistent multi-month decline | Alden | 3 |

## M28–M30: Fiscal Metrics

| Pattern | Tilt |
|---|---|
| Deficit and net interest rise while receipts weaken | Alden |
| Labor-linked tax receipts decline materially | Citrini |
| Fiscal burden stabilizes or improves | Green or Neutral |

---

# Example Manual CSV Rows

## Example: Weak 30Y bid-to-cover

```csv
2026-06-30,M10,2.18,2.32,-0.14,ratio,0,0,10,0,Alden,2,5,Weak 30Y bid-to-cover suggests soft long-end demand.,https://www.treasurydirect.gov/auctions/announcements-data-results/,2026-07-03,Yes
```

## Example: Strong central-bank gold demand

```csv
2026-06-30,M26,260,220,40,tonnes,0,0,15,0,Alden,3,5,Strong quarterly central-bank gold demand.,https://www.gold.org/goldhub/research/gold-demand-trends,2026-07-03,Yes
```

## Example: Falling labor-linked tax receipts

```csv
2026-06-30,M30,3150,3250,-100,$ billions,15,0,0,0,Citrini,3,5,Trailing 12-month labor-linked tax receipts declined.,https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/,2026-07-03,Yes
```

---

# CSV Editing Cautions

A CSV file treats commas as column separators.

To avoid breaking the file:

- Keep each metric row on a single line.
- Avoid commas in the `Notes` field.
- If a note must contain commas, wrap the entire note in double quotation marks.
- Do not add extra commas at the end of a row.
- Do not delete columns.
- Do not change `IsManual` from `Yes` for manual metrics.
- Do not guess missing values.
- Use blank fields and a neutral score when reliable data are unavailable.

Safe note:

```text
Weak bid-to-cover suggests soft long-end demand.
```

Risky note unless quoted:

```text
Weak bid-to-cover, low indirect demand, and high dealer takedown.
```

Quoted safe version:

```text
"Weak bid-to-cover, low indirect demand, and high dealer takedown."
```

---

# Final Checklist

Before committing a manual update:

- [ ] Correct target date
- [ ] Correct MetricID
- [ ] Value entered
- [ ] PriorValue entered
- [ ] MonthlyChange calculated
- [ ] Unit unchanged
- [ ] Tilt selected
- [ ] Strength selected
- [ ] Scenario score calculated
- [ ] Other scenario scores set to zero
- [ ] WeightUsed entered
- [ ] Notes entered without unsafe commas
- [ ] SourceURL verified
- [ ] LastUpdated entered
- [ ] IsManual remains `Yes`
- [ ] Monthly workflow rerun after the manual edit
- [ ] Streamlit dashboard refreshed
