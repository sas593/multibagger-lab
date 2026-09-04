import os, math, statistics
from datetime import date, timedelta
from typing import Any
import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title='Multibagger Lab')
API_KEY = os.getenv('TWELVE_DATA_API_KEY','').strip()
BASE='https://api.twelvedata.com'

WEIGHTS={'growth':25,'quality':20,'opportunity':15,'valuation':15,'management':10,'technicals':10,'catalysts':5}

def td(path:str, params:dict[str,Any]):
    if not API_KEY: raise HTTPException(503,'Live data is not connected. Add TWELVE_DATA_API_KEY to the server.')
    p=dict(params); p['apikey']=API_KEY
    try:
        r=requests.get(BASE+path,params=p,timeout=30); r.raise_for_status(); data=r.json()
    except requests.RequestException as e: raise HTTPException(502,f'Data provider error: {e}')
    if data.get('status')=='error' or data.get('code') not in (None,200): raise HTTPException(502,data.get('message','Provider error'))
    return data

def sym(s): return s.strip().upper()
def td_symbol(s): return f'{sym(s)}:NSE'

def fnum(v):
    try: return float(v)
    except: return None

def series(s, years=5):
    end=date.today(); start=end-timedelta(days=365*years)
    d=td('/time_series',{'symbol':td_symbol(s),'interval':'1day','start_date':str(start),'end_date':str(end),'outputsize':5000,'adjust':'all'})
    vals=list(reversed(d.get('values',[])))
    return [{k:(v[k] if k=='datetime' else fnum(v.get(k))) for k in ['datetime','open','high','low','close','volume']} for v in vals]

def profile(s): return td('/profile',{'symbol':td_symbol(s)})
def stats(s): return td('/statistics',{'symbol':td_symbol(s)})
def earnings(s): return td('/earnings',{'symbol':td_symbol(s),'outputsize':20})
def income(s): return td('/income_statement',{'symbol':td_symbol(s),'period':'annual','outputsize':8})
def balance(s): return td('/balance_sheet',{'symbol':td_symbol(s),'period':'annual','outputsize':8})
def cashflow(s): return td('/cash_flow',{'symbol':td_symbol(s),'period':'annual','outputsize':8})

def latest_val(obj,*keys):
    for k in keys:
        v=obj.get(k) if isinstance(obj,dict) else None
        if isinstance(v,dict):
            for kk in ('value','raw','amount','total'):
                if kk in v and fnum(v[kk]) is not None: return fnum(v[kk])
        elif fnum(v) is not None: return fnum(v)
    return None

def clamp(x): return max(0,min(100,x))

def score_stock(s, h, st, inc, bal, cf):
    # Transparent model: only award points where the provider supplies usable inputs.
    growth=50; quality=50; valuation=50; management=50; opportunity=55; catalysts=50
    if len(inc)>=2:
        rev=[]; ni=[]
        for r in inc:
            rev.append(latest_val(r,'sales','revenue','total_revenue'))
            ni.append(latest_val(r,'net_income','net_income_continuous_operations'))
        rev=[x for x in rev if x is not None]; ni=[x for x in ni if x is not None]
        if len(rev)>=2 and rev[0]:
            rg=(rev[0]/rev[-1])**(1/max(1,len(rev)-1))-1
            growth=clamp(50+rg*400)
        if len(ni)>=2 and ni[-1] is not None and ni[-1]>0: quality=60
    stats0=st.get('statistics',{}) if isinstance(st,dict) else {}
    vm=stats0.get('valuations_metrics',{}) if isinstance(stats0,dict) else {}
    fm=stats0.get('financials',{}) if isinstance(stats0,dict) else {}
    pe=fnum(vm.get('trailing_pe')); roe=fnum(fm.get('return_on_equity_ttm'))
    if roe is not None: quality=clamp(40+roe*1.5)
    if pe is not None:
        valuation=85 if pe<15 else 75 if pe<20 else 60 if pe<28 else 45 if pe<40 else 25
    if h:
        closes=[x['close'] for x in h if x['close']]
        if len(closes)>60:
            ma20=sum(closes[-20:])/20; ma100=sum(closes[-100:])/100
            technicals=70 if closes[-1]>ma20>ma100 else 55 if closes[-1]>ma100 else 35
        else: technicals=50
    else: technicals=50
    score=(growth*25+quality*20+opportunity*15+valuation*15+management*10+technicals*10+catalysts*5)/100
    hard=[]
    # Debt check where provider exposes it.
    if bal:
        latest=bal[0]; li=latest.get('liabilities',{}) if isinstance(latest,dict) else {}
        debt=latest_val(li,'long_term_debt','total_debt')
        if debt is not None and debt<0: hard.append('Invalid debt value')
    decision='Exceptional' if score>=90 else 'High Conviction' if score>=80 else 'Accumulate' if score>=70 else 'Watch' if score>=60 else 'Avoid'
    ten='Exceptional' if score>=90 and valuation>=60 and growth>=65 else 'Strong Candidate' if score>=80 and growth>=60 else 'Possible' if score>=65 else 'No'
    return {'overall':round(score,1),'decision':decision,'ten_x':ten,'components':{'growth':round(growth,1),'quality':round(quality,1),'opportunity':round(opportunity,1),'valuation':round(valuation,1),'management':round(management,1),'technicals':round(technicals,1),'catalysts':round(catalysts,1)},'hard_flags':hard,'pe':pe,'roe':roe}

@app.get('/',response_class=HTMLResponse)
def home(): return open('index.html',encoding='utf-8').read()

@app.get('/api/health')
def health(): return {'live':bool(API_KEY),'provider':'Twelve Data','app':'Multibagger Lab','date':str(date.today())}

@app.get('/api/stock/{symbol}')
def stock(symbol:str):
    s=sym(symbol); h=series(s,5)
    st=stats(s); pf=profile(s); inc=income(s); bal=balance(s); cf=cashflow(s); er=earnings(s)
    latest=h[-1] if h else {}; prev=h[-2]['close'] if len(h)>1 else None
    if prev: latest={**latest,'previous_close':prev,'change_pct':(latest['close']/prev-1)*100}
    sc=score_stock(s,h,st,inc.get('income_statement',[]),bal.get('balance_sheet',[]),cf.get('cash_flow',[]))
    stat=st.get('statistics',{}) if isinstance(st,dict) else {}
    return {'symbol':s,'profile':pf,'latest':latest,'history':h,'statistics':stat,'income':inc.get('income_statement',[]),'balance':bal.get('balance_sheet',[]),'cashflow':cf.get('cash_flow',[]),'earnings':er.get('earnings',[]),'score':sc}

@app.get('/api/scan')
def scan(symbols:str=Query(...), min_score:float=0):
    out=[]
    for raw in symbols.split(',')[:20]:
        s=sym(raw)
        try:
            x=stock(s); sc=x['score']
            if sc['overall']<min_score: continue
            p=x['latest'].get('close'); h=x['history']; r=(p/h[-252]['close']-1)*100 if p and len(h)>252 else None
            out.append({'symbol':s,'name':x.get('profile',{}).get('name',s),'price':p,'return_1y':r,'score':sc['overall'],'decision':sc['decision'],'ten_x':sc['ten_x'],'pe':sc['pe'],'roe':sc['roe']})
        except HTTPException: continue
    return {'results':sorted(out,key=lambda z:z['score'],reverse=True)}

@app.get('/api/backtest')
def backtest(symbols:str=Query(...), years:int=7, entry_score:float=70, holding_years:int=3):
    # Point-in-time price cohort study. Scores are current/provider fundamentals when available; not a survivorship-bias-free institutional backtest.
    rows=[]
    for raw in symbols.split(',')[:20]:
        s=sym(raw)
        try:
            h=series(s,max(years,holding_years+1));
            if len(h)<250: continue
            # Evaluate rolling 1-year entries at monthly-ish points; report max future multiple within holding window.
            step=21; trades=[]
            for i in range(100,len(h)-252,step):
                entry=h[i]['close']; future=h[i:min(len(h),i+252*holding_years)]
                if not entry or not future: continue
                max_mult=max(x['high']/entry for x in future if x.get('high'))
                end_mult=future[-1]['close']/entry
                dd=0; peak=entry
                for x in future:
                    c=x['close']; peak=max(peak,c); dd=min(dd,c/peak-1)
                trades.append({'entry_date':h[i]['datetime'],'entry_price':entry,'max_multiple':max_mult,'end_multiple':end_mult,'max_drawdown_pct':dd*100})
            if trades:
                rows.append({'symbol':s,'observations':len(trades),'hit_3x':sum(t['max_multiple']>=3 for t in trades),'hit_5x':sum(t['max_multiple']>=5 for t in trades),'hit_10x':sum(t['max_multiple']>=10 for t in trades),'worst_drawdown_pct':min(t['max_drawdown_pct'] for t in trades),'avg_end_multiple':statistics.mean(t['end_multiple'] for t in trades)})
        except Exception: continue
    n=sum(r['observations'] for r in rows)
    return {'summary':{'stocks':len(rows),'observations':n,'hit_3x':sum(r['hit_3x'] for r in rows),'hit_5x':sum(r['hit_5x'] for r in rows),'hit_10x':sum(r['hit_10x'] for r in rows),'win_rate_pct':round(sum(r['hit_3x'] for r in rows)/n*100,1) if n else 0,'max_drawdown_pct':round(min([r['worst_drawdown_pct'] for r in rows] or [0]),1)},'rows':sorted(rows,key=lambda r:r['hit_10x'],reverse=True),'method':'Rolling historical price-cohort study; not survivorship-bias-free and not a full point-in-time fundamental backtest.'}

@app.get('/api/portfolio')
def portfolio(capital:float=1000000,target:float=10000000,years:int=5):
    if capital<=0 or target<=0 or years<=0: raise HTTPException(400,'Capital, target and years must be positive')
    cagr=(target/capital)**(1/years)-1
    return {'capital':capital,'target':target,'years':years,'required_cagr_pct':cagr*100,'annual_path':[capital*(1+cagr)**i for i in range(years+1)]}
