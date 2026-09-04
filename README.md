# Multibagger Lab — Live Browser App

This is the deployable application package for the real-data version of Multibagger Lab.

## What it does
- Browser-based NSE stock search
- Real daily price history through Twelve Data
- Company profile, statistics, earnings and financial statements when available on the provider plan
- Explainable 100-point score
- Scanner
- Historical 3× / 5× / 10× price-cohort study
- Drawdown and hit-rate statistics
- ₹10 lakh → ₹1 crore CAGR hurdle calculator

## Run locally

Windows PowerShell:
```powershell
$env:TWELVE_DATA_API_KEY="YOUR_KEY"
pip install -r requirements.txt
uvicorn backend:app --host 0.0.0.0 --port 8000
```

Mac/Linux:
```bash
export TWELVE_DATA_API_KEY="YOUR_KEY"
pip install -r requirements.txt
uvicorn backend:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in Chrome.

## Deploy

The included Dockerfile can be deployed to a normal container web host. Set the environment variable `TWELVE_DATA_API_KEY` in the host's secret/environment settings. Do not put the key in `index.html`.

## Data note
Twelve Data supports time series and a fundamentals API including profile, earnings, income statement, balance sheet, cash flow and statistics. Some fundamentals and historical-depth features depend on the subscription plan.

NSE separately provides licensed real-time, EOD/historical and corporate-data products. Production use of exchange data should comply with the applicable data agreement/licensing terms.

## Important backtest limitation
The current backtest is a rolling historical price-cohort study. It is **not** yet survivorship-bias-free and does not reconstruct point-in-time fundamentals for every historical date. Do not interpret its 3×/5×/10× counts as a validated trading strategy.

## Next engine layer
- point-in-time fundamental snapshots
- survivorship-bias-free NSE universe
- corporate-action-aware historical database
- true entry/exit signals using the score at the entry date
- transaction costs/slippage
- portfolio position sizing
- CAGR and equity curve from actual trades
- failed high-score candidates
- HDFC Bank deep-dive with source-linked thesis
