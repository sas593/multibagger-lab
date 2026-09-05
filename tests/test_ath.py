import pandas as pd
from ath_engine.scanner import detect_new_ath_events
def test_strict_new_ath():
    idx=pd.bdate_range("2025-01-01",periods=8)
    df=pd.DataFrame({"close":[10,12,12,11,13,13,14,13],"volume":[1]*8},index=idx)
    assert [e.breakout_price for e in detect_new_ath_events(df,"TEST",7300)]==[12,13,14]
