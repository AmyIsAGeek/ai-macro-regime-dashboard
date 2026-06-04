# Manual Data Entry Guide

This guide explains how to update the dashboard metrics that are not currently automated and provides direct public-source URLs for each metric.

## Manual Metrics and Direct Source URLs

| Metric ID | Metric | Primary Public Source | Direct URL | Update Frequency |
|---|---|---|---|---|
| M09 | 30Y Treasury auction tail | TreasuryDirect auction results plus a separate when-issued yield source | https://www.treasurydirect.gov/auctions/results/ | Monthly |
| M10 | 30Y Treasury bid-to-cover | TreasuryDirect recent auction results | https://www.treasurydirect.gov/auctions/results/ | Monthly |
| M11 | 30Y Treasury indirect bidder share | TreasuryDirect auction result release | https://www.treasurydirect.gov/auctions/auction-query/ | Monthly |
| M12 | 30Y Treasury primary dealer takedown | TreasuryDirect auction result release | https://www.treasurydirect.gov/auctions/auction-query/ | Monthly |
| M25 | FDIC unrealized securities losses | FDIC Quarterly Banking Profile | https://www.fdic.gov/analysis/quarterly-banking-profile | Quarterly |
| M26 | Central-bank gold purchases | World Gold Council Gold Demand Trends | https://www.gold.org/goldhub/research/gold-demand-trends | Quarterly |
| M27 | Foreign Treasury holdings | Treasury TIC Table 5 | https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html | Monthly |
| M28 | Federal deficit trailing 12 months | Treasury Fiscal Data Monthly Treasury Statement | https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/ | Monthly |
| M29 | Net interest outlays | Treasury Fiscal Data Monthly Treasury Statement | https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/ | Monthly |
| M30 | Individual income and payroll tax receipts | Treasury Fiscal Data Monthly Treasury Statement | https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/ | Monthly |

---

# Monthly Manual-Entry Workflow

## 1. Run the automated monthly update first

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

## 2. Open the observations file

In GitHub:

1. Click **Code**.
2. Open the `data` folder.
3. Open `monthly_observations.csv`.
4. Click the pencil icon to edit the file.

## 3. Find the manual rows for the target date

Use your browser search command:

```text
Command + F
```

Search for a row such as:

```text
2026-06-30,M09
```

Then update the manual rows for the same target date.

## 4. Enter the required fields

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

## 5. Use the scoring rule

```text
Scenario score = Strength × relevant scenario weight
```

The three related fields answer different questions:

| Field | Question it answers |
|---|---|
| `Tilt` | Which scenario does this metric favor? |
| `Strength` | How convincing is the current observation as evidence for that scenario? |
| `WeightUsed` | How important is this metric in the overall scoring model? |

Strength is the confidence level of the current observation. It is **not** the importance of the metric.

### Strength = 0 — Neutral, missing, or inconclusive

Use `0` when:

- no reliable value is available;
- the metric is essentially unchanged;
- the signal is mixed;
- the value does not clearly favor any scenario; or
- the source is not reliable enough to score.

Example:

```text
30Y bid-to-cover = 2.31
Prior value = 2.30
```

That change is too small to support a meaningful scenario score.

### Strength = 1 — Weak signal

Use `1` when:

- the metric leans toward a scenario;
- the move is modest;
- only one component supports the conclusion; or
- the signal has not persisted long enough to be convincing.

Example:

```text
Central-bank gold purchases = 175 tonnes
```

That supports Alden, but it is not unusually high.

### Strength = 2 — Moderate signal

Use `2` when:

- the move is clearly meaningful;
- the metric crosses a useful threshold;
- several related data points agree; or
- the trend has persisted for more than one period.

Example:

```text
30Y bid-to-cover = 2.17
Indirect bidder share = 58%
Primary dealer takedown = 20%
```

Several auction measures indicate weak long-end demand, so the auction cluster reasonably favors Alden with moderate strength.

### Strength = 3 — Strong signal

Use `3` only when:

- the move is large;
- the reading is historically unusual;
- the trend is persistent; or
- multiple related indicators strongly confirm the same scenario.

Example:

```text
Central-bank gold purchases > 250 tonnes
```

That would be a strong Alden signal.

Another example:

```text
Labor-linked tax receipts decline sharply
Unemployment rises
JOLTS hires fall
```

That would support a strong Citrini signal.

### Practical rule

Use `1` freely, `2` selectively, and `3` rarely. A good scoring system should not assign many metrics a strength of `3`, because that would make the dashboard overreact to normal monthly noise.

### Strength versus Weight

Suppose two metrics both favor Alden:

| Metric | Strength | WeightUsed | AldenScore |
|---|---:|---:|---:|
| Central-bank gold purchases | 2 | 5 | 10 |
| Primary dealer takedown | 2 | 4 | 8 |

Both signals are equally strong this month, but central-bank gold purchases has more impact because it is considered more important to the Alden thesis.

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

## 6. Commit the CSV edit

Commit with a message such as:

```text
Add June manual metric data
```

## 7. Re-run the monthly workflow

Run the same target date again:

```text
Actions → Monthly data update → Run workflow
```

The updater will preserve the manual rows and recalculate:

```text
data/scenario_scores.csv
```

## 8. Refresh the Streamlit app

1. Open the Streamlit dashboard.
2. Refresh or reboot the app.
3. Select the target date.
4. Check the Metric table and scenario scores.

---

# Metric-Specific Source Instructions

## M09 — 30Y Treasury Auction Tail

### TreasuryDirect URLs

Recent auction results:

https://www.treasurydirect.gov/auctions/results/

Historical auction search:

https://www.treasurydirect.gov/auctions/auction-query/

Announcements and results press releases:

https://www.treasurydirect.gov/auctions/announcements-data-results/announcement-results-press-releases/

### Important limitation

TreasuryDirect publishes the **auction high yield**, but it does **not** publish the pre-auction **when-issued yield** needed to calculate the auction tail.

Formula:

```text
Auction tail =
Auction high yield
− When-issued yield immediately before the auction
```

- Positive value = tail
- Negative value = stop-through

Use TreasuryDirect for the auction high yield. Use a reputable contemporaneous market report for the when-issued yield. If you cannot obtain a reliable when-issued yield, leave M09 blank rather than guessing.

Recommended `SourceURL`:

```text
https://www.treasurydirect.gov/auctions/results/
```

---

## M10 — 30Y Treasury Bid-to-Cover

### Direct URLs

Recent auction results:

https://www.treasurydirect.gov/auctions/results/

Historical auction search:

https://www.treasurydirect.gov/auctions/auction-query/

### Where to find it

1. Open the recent auction results page.
2. Locate the most recent **30-Year Bond** auction.
3. Open the result release.
4. Copy the published **Bid-to-Cover Ratio**.

Example:

```text
Value: 2.30
Unit: ratio
```

Recommended `SourceURL`:

```text
https://www.treasurydirect.gov/auctions/results/
```

---

## M11 — 30Y Treasury Indirect Bidder Share

### Direct URLs

Historical auction search:

https://www.treasurydirect.gov/auctions/auction-query/

Recent auction results:

https://www.treasurydirect.gov/auctions/results/

### Where to find it

1. Open the auction search page.
2. Search for the most recent **30-Year Bond** auction.
3. Open or download the result.
4. Find:
   - Indirect bidder competitive accepted amount
   - Total competitive accepted amount

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

Recommended `SourceURL`:

```text
https://www.treasurydirect.gov/auctions/auction-query/
```

---

## M12 — 30Y Treasury Primary Dealer Takedown

### Direct URLs

Historical auction search:

https://www.treasurydirect.gov/auctions/auction-query/

Recent auction results:

https://www.treasurydirect.gov/auctions/results/

### Where to find it

1. Open the auction search page.
2. Search for the most recent **30-Year Bond** auction.
3. Open or download the result.
4. Find:
   - Primary dealer competitive accepted amount
   - Total competitive accepted amount

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

Recommended `SourceURL`:

```text
https://www.treasurydirect.gov/auctions/auction-query/
```

---

## M25 — FDIC Unrealized Securities Losses

### Direct URLs

FDIC Quarterly Banking Profile landing page:

https://www.fdic.gov/analysis/quarterly-banking-profile

FDIC research and analysis page:

https://www.fdic.gov/analysis

### Where to find it

1. Open the Quarterly Banking Profile page.
2. Open the latest quarter.
3. Search the report or release for:
   ```text
   unrealized losses
   ```
4. Enter the FDIC-reported total unrealized losses on available-for-sale and held-to-maturity securities.

Recommended entry format:

```text
Value: total unrealized losses
Unit: $ billions
PriorValue: prior quarter total
MonthlyChange: current quarter total minus prior quarter total
```

Use the latest available quarterly value until the next Quarterly Banking Profile is released.

Recommended `SourceURL`:

```text
https://www.fdic.gov/analysis/quarterly-banking-profile
```

---

## M26 — Central-Bank Gold Purchases

### Direct URLs

World Gold Council Gold Demand Trends landing page:

https://www.gold.org/goldhub/research/gold-demand-trends

Current-quarter report pages are linked from the landing page. For example:

https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q1-2026

### Where to find it

1. Open the Gold Demand Trends landing page.
2. Open the latest quarterly report.
3. Search the report for:
   ```text
   Central banks
   ```
4. Enter the latest net central-bank gold purchases in tonnes.

Recommended entry format:

```text
Value: current quarter net purchases
Unit: tonnes
PriorValue: prior quarter net purchases
MonthlyChange: current quarter minus prior quarter
```

Use the latest available quarterly value until the next report is published.

Recommended `SourceURL`:

```text
https://www.gold.org/goldhub/research/gold-demand-trends
```

---

## M27 — Foreign Treasury Holdings

### Direct URLs

Treasury TIC Table 5 HTML:

https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html

Treasury TIC Table 5 plain-text file:

https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt

Treasury TIC system landing page:

https://home.treasury.gov/data/treasury-international-capital-tic-system

### Where to find it

1. Open TIC Table 5.
2. Use the **Total** row for the latest available month.
3. Record the prior month total.
4. Calculate the monthly change.

Recommended entry format:

```text
Value: latest total foreign Treasury holdings
PriorValue: prior month total
MonthlyChange: latest total minus prior month total
Unit: $ billions
```

TIC data are lagged. Use the latest available month rather than estimating the current month.

Recommended `SourceURL`:

```text
https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html
```

---

## M28 — Federal Deficit Trailing 12 Months

### Direct URLs

Monthly Treasury Statement dataset:

https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/

Fiscal Data API documentation:

https://fiscaldata.treasury.gov/api-documentation/

### Where to find it

1. Open the Monthly Treasury Statement dataset.
2. Use the downloadable data or data preview.
3. Extract the monthly surplus or deficit values.
4. Sum the latest 12 months.

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

Recommended `SourceURL`:

```text
https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/
```

---

## M29 — Net Interest Outlays

### Direct URLs

Monthly Treasury Statement dataset:

https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/

Fiscal Data API documentation:

https://fiscaldata.treasury.gov/api-documentation/

### Where to find it

1. Open the Monthly Treasury Statement dataset.
2. Locate the outlay category:
   ```text
   Net Interest
   ```
3. Sum the latest 12 monthly net-interest outlays.

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

Recommended `SourceURL`:

```text
https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/
```

---

## M30 — Individual Income and Payroll Tax Receipts

### Direct URLs

Monthly Treasury Statement dataset:

https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/

Fiscal Data API documentation:

https://fiscaldata.treasury.gov/api-documentation/

### Where to find it

1. Open the Monthly Treasury Statement dataset.
2. Locate the receipt categories:
   ```text
   Individual Income Taxes
   Social Insurance and Retirement Receipts
   ```
3. Add the two categories for each month.
4. Sum the latest 12 months.

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

Recommended `SourceURL`:

```text
https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/
```

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
2026-06-30,M10,2.18,2.32,-0.14,ratio,0,0,10,0,Alden,2,5,Weak 30Y bid-to-cover suggests soft long-end demand.,https://www.treasurydirect.gov/auctions/results/,2026-07-03,Yes
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
