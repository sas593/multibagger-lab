from datetime import date, timedelta
import numpy as np
from .models import CompanyFundamentals, NewsItem

class DummyDataProvider:
    def __init__(self, seed=42):
        self.seed = seed
        self.companies = {
            "DODLA": CompanyFundamentals(
                "DODLA","Dodla Dairy",7800,1180,42.5,27.8,.145,.235,.205,.18,.22,
                .1734,.127,.03,310,210,.012,.30,.00,1.5,False),
            "KEI": CompanyFundamentals(
                "KEI","KEI Industries",35000,3950,82.0,48.2,.18,.25,.23,.21,.24,
                .215,.235,.08,1250,900,-.008,.38,.00,2.0,False),
            "HDFCBANK": CompanyFundamentals(
                "HDFCBANK","HDFC Bank",1250000,1780,82.5,21.6,.145,.125,.16,.145,.13,
                .155,.018,.55,180000,140000,.006,.00,.00,.4,True),
        }

    def fundamentals(self, ticker):
        ticker=ticker.upper().replace(".NS","")
        if ticker not in self.companies:
            raise KeyError(f"No dummy company configured for {ticker}")
        return self.companies[ticker]

    def price_history(self, ticker, years=12):
        ticker=ticker.upper().replace(".NS","")
        f=self.fundamentals(ticker)
        end=np.datetime64("2026-09-04")
        start=end-np.timedelta64(years,"Y")
        idx=np.busday_offset(np.arange(start.astype("datetime64[D]"),end.astype("datetime64[D]")+1,dtype="datetime64[D]"),0,roll="forward")
        idx=np.unique(idx)
        rng=np.random.default_rng(self.seed+sum(map(ord,ticker)))
        base=f.price*.18
        drift=max(.00012,(f.eps_cagr_5y or .12)/252*.65)
        shocks=rng.normal(drift,.018,len(idx))
        values=base*np.exp(np.cumsum(shocks))
        values*=f.price/values[-1]
        volume=rng.integers(150_000,4_000_000,len(idx))
        import pandas as pd
        return pd.DataFrame({"close":values,"volume":volume},index=pd.to_datetime(idx))

    def news(self,tickers,days=45):
        cutoff=date(2026,9,4)-timedelta(days=days)
        items=[
            NewsItem("KEI",date(2026,8,28),"New large wire & cable capacity announced by competitor",
                     "Competitive intensity could pressure pricing and valuation multiples.","Material","Competitive","Negative / monitor"),
            NewsItem("HDFCBANK",date(2026,8,20),"CEO succession transition remains a key governance variable",
                     "Leadership transition requires monitoring of continuity and execution.","Material","Governance","Monitor"),
            NewsItem("DODLA",date(2026,8,14),"Dairy procurement remains stable in key regions",
                     "Input availability remains supportive for the operating thesis.","Material","Operations","Positive / thesis intact"),
        ]
        wanted={x.upper().replace(".NS","") for x in tickers}
        return [n for n in items if n.ticker in wanted and n.published_at>=cutoff]
