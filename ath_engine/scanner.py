from investment_engine.models import AthEvent

def detect_new_ath_events(prices,ticker,lookback_days=730):
    c=prices["close"].astype(float).sort_index()
    cutoff=c.index.max()-__import__("pandas").Timedelta(days=lookback_days)
    prior=c.shift(1).cummax()
    new=c>prior
    events=[]
    for d in c.index[(new)&(c.index>=cutoff)]:
        p=float(prior.loc[d]); after=c.loc[d:]
        above=after>p
        retests=int(((after.iloc[1:]<=p)&(after.iloc[:-1]>p).values).sum())
        events.append(AthEvent(ticker,d.date(),p,float(c.loc[d]),int(above.sum()),
            (float(after.max())/p-1)*100,(float(c.iloc[-1])/p-1)*100,retests))
    return events

def breakout_quality(event,f):
    if event.days_above_previous_ath>=20 and event.max_pct_above_previous_ath>=10 and f.market_cap_cr>=5000: return "STRONG"
    if event.days_above_previous_ath>=5 and f.market_cap_cr>=5000: return "MEDIUM"
    return "WEAK"
