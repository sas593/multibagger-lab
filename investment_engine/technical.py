def technical_snapshot(prices):
    c=prices["close"].astype(float)
    ma50=c.rolling(50).mean().iloc[-1] if len(c)>=50 else None
    ma200=c.rolling(200).mean().iloc[-1] if len(c)>=200 else None
    momentum=c.pct_change(126).iloc[-1] if len(c)>=127 else None
    entry=ma200 is not None and momentum is not None and c.iloc[-1]>ma200 and ma50>ma200 and momentum>0
    exit_=ma200 is not None and ma50 is not None and c.iloc[-1]<ma200 and ma50<ma200
    return {"price":float(c.iloc[-1]),"ma50":ma50,"ma200":ma200,"momentum_6m":momentum,
            "entry_trigger":bool(entry),"exit_trigger":bool(exit_)}
