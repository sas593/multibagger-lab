from investment_engine.scoring import score_company
from investment_engine.technical import technical_snapshot
from investment_engine.thesis import thesis_monitor

def analyze_portfolio(holdings,provider):
    rows=[]
    news=provider.news([h.ticker for h in holdings])
    for h in holdings:
        f=provider.fundamentals(h.ticker)
        px=provider.price_history(h.ticker,2)
        s=score_company(f)
        t=technical_snapshot(px)
        thesis=thesis_monitor(s,[n for n in news if n.ticker==h.ticker])
        invested=h.quantity*h.average_buy_price
        value=h.quantity*t["price"]
        rows.append({
            "Ticker":h.ticker,"Company":f.company,"Quantity":h.quantity,"Avg Buy":h.average_buy_price,
            "Price":t["price"],"Invested":invested,"Current Value":value,"P&L":value-invested,
            "P&L %":(value/invested-1)*100 if invested else None,"Score":s.total,"Decision":s.decision,
            "Thesis":thesis["status"],"Risk Flags":", ".join(s.risk_flags) or "None",
            "3Y EPS Multiple":s.projected_3y_earnings_multiple,"Entry":t["entry_trigger"],"Exit":t["exit_trigger"],
            "ROE %":f.roe*100 if f.roe is not None else None,"D/E":f.debt_to_equity})
    return rows,news

def rank_deployment(candidates):
    ranked=[]
    for c in candidates:
        priority=c["score"]*.45+c["quality"]*.15+c["earnings"]*.25+c["valuation"]*.15
        ranked.append({**c,"deployment_score":round(priority,2)})
    return sorted(ranked,key=lambda x:x["deployment_score"],reverse=True)
