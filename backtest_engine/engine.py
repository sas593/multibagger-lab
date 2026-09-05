def backtest_price_signal(prices,holding_years=5,cooldown_days=90):
    import pandas as pd
    c=prices["close"].astype(float).sort_index()
    bt=pd.DataFrame(index=c.index)
    bt["close"]=c; bt["ma50"]=c.rolling(50).mean(); bt["ma200"]=c.rolling(200).mean(); bt["momentum6m"]=c.pct_change(126)
    bt["entry"]=(bt.close>bt.ma200)&(bt.ma50>bt.ma200)&(bt.momentum6m>0)
    signals=[]; last=None
    for d in bt.index[bt.entry.fillna(False)]:
        if last is None or (d-last).days>=cooldown_days: signals.append(d); last=d
    rows=[]
    for d in signals:
        future=c[c.index>=d+pd.DateOffset(years=holding_years)]
        mult=float(future.iloc[0]/c.loc[d]) if len(future) else None
        w=c[(c.index>=d)&(c.index<=d+pd.DateOffset(years=holding_years))]
        dd=float(((w/w.cummax())-1).min()*100) if len(w) else None
        rows.append({"entry_date":d.date(),"entry_price":float(c.loc[d]),"multiple":mult,"max_drawdown_pct":dd,
                     "outcome":"TOO EARLY" if mult is None else "10x+" if mult>=10 else "5x-<10x" if mult>=5 else "3x-<5x" if mult>=3 else "<3x"})
    return pd.DataFrame(rows)

def summarize_backtest(r):
    if r.empty:return {"signals":0}
    m=r[r.multiple.notna()]
    return {"signals":len(r),"matured":len(m),
            "3x_win_rate":float((m.multiple>=3).mean()) if len(m) else None,
            "5x_win_rate":float((m.multiple>=5).mean()) if len(m) else None,
            "10x_win_rate":float((m.multiple>=10).mean()) if len(m) else None,
            "median_multiple":float(m.multiple.median()) if len(m) else None,
            "worst_drawdown":float(m.max_drawdown_pct.min()) if len(m) else None}
