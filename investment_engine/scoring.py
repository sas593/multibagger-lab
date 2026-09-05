from .models import ScoreResult

def score_company(f):
    g=f.forward_eps_growth if f.forward_eps_growth is not None else f.eps_cagr_3y
    growth=25 if g is not None and g>=.30 else 23 if g is not None and g>=.26 else 19 if g is not None and g>=.20 else 14 if g is not None and g>=.15 else 8 if g is not None and g>=.08 else 0
    quality=0
    if f.roe is not None: quality+=10 if f.roe>=.20 else 8 if f.roe>=.15 else 5 if f.roe>=.10 else 2
    if f.roce is not None: quality+=10 if f.roce>=.20 else 8 if f.roce>=.15 else 5 if f.roce>=.10 else 2
    opportunity=15 if (f.eps_cagr_5y or 0)>=.22 and (g or 0)>=.20 else 11 if (f.eps_cagr_5y or 0)>=.16 else 7 if (f.eps_cagr_5y or 0)>=.10 else 3
    valuation=15 if f.pe is not None and f.pe<=22 else 12 if f.pe and f.pe<=30 else 8 if f.pe and f.pe<=40 else 4 if f.pe else 0
    management=4 if f.governance_risk else 8
    technical=7
    catalysts=3
    total=min(100,int(growth+quality+opportunity+valuation+management+technical+catalysts))
    gates={
        "Debt/Equity": f.debt_to_equity is None or f.debt_to_equity<=1,
        "ROE": f.roe is None or f.roe>=.12,
        "Valuation": f.pe is None or 0<f.pe<=75,
        "Governance": not f.governance_risk,
        "Cash Flow": f.ocf_cr is None or f.ocf_cr>=0,
        "Dilution": f.dilution_pct is None or f.dilution_pct<=.10,
        "Promoter Pledge": f.promoter_pledge is None or f.promoter_pledge<=.05,
    }
    risks=[k for k,v in gates.items() if not v]
    passed=all(gates.values())
    cls="Exceptional" if total>=90 else "Strong Candidate" if total>=80 else "Accumulate Candidate" if total>=70 else "Possible" if total>=60 else "No"
    if not passed: decision="REDUCE / EXIT" if ("Governance" in risks or "Cash Flow" in risks) else "WAIT"
    elif total>=85: decision="BUY / ACCUMULATE"
    elif total>=70: decision="ACCUMULATE"
    elif total>=60: decision="HOLD / WATCH"
    else: decision="WAIT"
    multiple=(1+g)**3 if g is not None else None
    thesis="INTACT" if passed and (g or 0)>=.15 else "UNDER REVIEW"
    return ScoreResult(f.ticker,total,
        {"Earnings Growth":growth,"Business Quality":quality,"Future Opportunity":opportunity,
         "Valuation":valuation,"Management & Governance":management,"Technical Setup":technical,"Catalysts":catalysts},
        gates,decision,cls,multiple,thesis,risks)
