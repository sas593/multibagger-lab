# Multibagger Lab

Complete production-oriented investment decision engine using deterministic DEMO/DUMMY data.

Run:
    pip install -r requirements.txt
    streamlit run frontend/app.py

The data provider is an adapter. Replace DummyDataProvider with a licensed provider later without changing the core engines.

Modules:
- investment_engine: normalized fundamentals, scoring, technicals, thesis
- portfolio_engine: holdings, thesis status, capital allocation
- ath_engine: market-cap/liquidity universe and strict new-ATH detection
- backtest_engine: point-in-time framework and signal backtest
- wealth_engine: ₹25L → ₹50L → ₹1Cr
- news_engine: material news and threat classification
- database: SQLAlchemy models
- api: FastAPI service
- workers: refresh-job entry point
- frontend: Streamlit application
- tests: deterministic tests

Demo tickers: DODLA, KEI, HDFCBANK.
