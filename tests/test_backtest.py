import pandas as pd
from backtest_engine.engine import backtest_price_signal
def test_backtest_returns_dataframe():
    idx=pd.bdate_range("2015-01-01",periods=1500)
    df=pd.DataFrame({"close":range(100,1600),"volume":[1]*1500},index=idx)
    assert hasattr(backtest_price_signal(df),"columns")
