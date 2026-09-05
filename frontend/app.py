import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
from investment_engine.data_provider import DummyDataProvider
from investment_engine.models import Holding
from investment_engine.scoring import score_company
from investment_engine.technical import technical_snapshot
from portfolio_engine.engine import analyze_portfolio,rank_deployment
from ath_engine.scanner import detect_new_ath_events,breakout_quality
from backtest_engine.engine import backtest_price_signal,summarize_backtest
from wealth_engine.engine import build_milestones,deployment_impact
from news_engine.engine import classify_threat

st.set_page_config(page_title="Multibagger Lab",layout="wide")
provider=DummyDataProvider()
st.sidebar.title("Multibagger Lab")
st.sidebar.warning("DATA MODE: DEMO / DUMMY")
page=st.sidebar.radio("Module",["Dashboard","Stock Analysis","Portfolio","Capital Allocation","ATH Scanner","Backtest","Wealth Engine","Portfolio News & Threats"])

def money(x): return f"₹{x:,.0f}"

def dashboard():
    st.title("Multibagger Lab"); st.warning("DEMO / DUMMY DATA — NOT LIVE MARKET DATA")
    st.markdown("### Decision engine")
    st.markdown("""**Where is my money?** Portfolio + thesis monitor.\n\n**Where should I deploy more?** Capital allocation ranking.\n\n**Can earnings double in 3 years?** Forward earnings hurdle.\n\n**Is the thesis intact?** Material threats + hard gates.\n\n**Are ATH breakouts real?** Market-cap universe + strict prior-ATH logic.\n\n**Does it work?** Backtest framework.""")

def stock():
    st.title("Stock Analysis"); ticker=st.selectbox("Company",list(provider.companies))
    f=provider.fundamentals(ticker); px=provider.price_history(ticker); s=score_company(f); t=technical_snapshot(px)
    c=st.columns(4); c[0].metric("Price",money(t["price"])); c[1].metric("Score",f"{s.total}/100"); c[2].metric("3Y EPS Multiple",f"{s.projected_3y_earnings_multiple:.2f}×"); c[3].metric("Decision",s.decision)
    l,r=st.columns(2)
    with l: st.subheader("Hard Gates"); st.dataframe(pd.DataFrame({"Gate":list(s.hard_gates),"Result":["PASS" if x else "FAIL" for x in s.hard_gates.values()]}),hide_index=True,use_container_width=True); st.metric("Thesis",s.thesis_status)
    with r: st.subheader("100-Point Score"); st.dataframe(pd.DataFrame({"Factor":list(s.factors),"Score":list(s.factors.values())}),hide_index=True,use_container_width=True)
    st.subheader("Fundamentals"); st.dataframe(pd.DataFrame([{"Market Cap ₹Cr":f.market_cap_cr,"EPS ₹":f.eps,"P/E":f.pe,"EPS CAGR 3Y %":f.eps_cagr_3y*100,"Forward EPS Growth %":f.forward_eps_growth*100,"ROE %":f.roe*100,"ROCE %":f.roce*100,"Debt/Equity":f.debt_to_equity,"OCF ₹Cr":f.ocf_cr,"FCF ₹Cr":f.fcf_cr}]),hide_index=True,use_container_width=True)
    st.subheader("Price"); st.line_chart(px["close"].tail(750))

def portfolio():
    st.title("Portfolio")
    raw=st.text_area("TICKER,QUANTITY,AVERAGE BUY PRICE (one per line)","DODLA,100,850\nKEI,50,3000\nHDFCBANK,100,1650")
    st.number_input("Portfolio XIRR / expected annual return %",value=15.0)
    holdings=[]
    for line in raw.splitlines():
        try:a,b,c=[x.strip() for x in line.split(",")]; holdings.append(Holding(a.upper().replace(".NS",""),float(b),float(c)))
        except: pass
    rows,_=analyze_portfolio(holdings,provider)
    if not rows:return
    df=pd.DataFrame(rows); total=df["Current Value"].sum(); invested=df["Invested"].sum(); df["Allocation %"]=df["Current Value"]/total*100
    q=st.columns(5); q[0].metric("Invested",money(invested)); q[1].metric("Current Value",money(total)); q[2].metric("P&L",money(df["P&L"].sum())); q[3].metric("Return",f"{(total/invested-1)*100:.1f}%"); q[4].metric("Holdings",len(df))
    st.dataframe(df,hide_index=True,use_container_width=True); st.bar_chart(df.set_index("Ticker")["Allocation %"])

def allocation():
    st.title("Capital Allocation"); candidates=[]
    for t,f in provider.companies.items():
        s=score_company(f); candidates.append({"Ticker":t,"Company":f.company,"score":s.total,"quality":((f.roe+f.roce)/2*100),"earnings":min(100,(f.forward_eps_growth/.30)*100),"valuation":max(0,100-(f.pe/75)*100)})
    ranked=rank_deployment(candidates); st.dataframe(pd.DataFrame(ranked),hide_index=True,use_container_width=True)
    amount=st.number_input("New capital ₹",value=100000,min_value=0)
    if ranked: st.success(f"Highest priority: {ranked[0]['Ticker']} | Deployment score {ranked[0]['deployment_score']:.1f}")

def ath():
    st.title("ATH Scanner"); rows=[]
    for t,f in provider.companies.items():
        if f.market_cap_cr<5000: continue
        events=detect_new_ath_events(provider.price_history(t),t,730)
        if events:
            e=events[-1]; rows.append({"Ticker":t,"Company":f.company,"Breakout":e.breakout_date,"Previous ATH":e.previous_ath,"Breakout Price":e.breakout_price,"Days Above Prior ATH":e.days_above_previous_ath,"Max % Above":e.max_pct_above_previous_ath,"Current % Above":e.current_pct_above_previous_ath,"Retests":e.retests,"Quality":breakout_quality(e,f)})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)

def backtest():
    st.title("Backtest — Cornerstone"); ticker=st.selectbox("Company",list(provider.companies),key="bt")
    r=backtest_price_signal(provider.price_history(ticker),5); st.json(summarize_backtest(r)); st.dataframe(r,hide_index=True,use_container_width=True)
    st.info("Demo signal backtest. Production fundamental backtests must use point-in-time financial, valuation and news snapshots.")

def wealth():
    st.title("Wealth Engine"); current=st.number_input("Current portfolio value ₹",value=1000000,min_value=0); ret=st.number_input("Expected annual return %",value=15.0,min_value=.1)/100; deployment=st.number_input("Additional deployment now ₹",value=100000,min_value=0)
    impact=deployment_impact(current,2500000,deployment); a,b,c=st.columns(3); a.metric("Next milestone gap",money(impact["current_gap"])); b.metric("Gap after deployment",money(impact["new_gap"])); c.metric("Progress after",f"{impact['progress_after']:.1f}%")
    st.dataframe(pd.DataFrame(build_milestones(current,ret,deployment)),hide_index=True,use_container_width=True)

def news():
    st.title("Portfolio News & Threats"); st.dataframe(pd.DataFrame(classify_threat(provider.news(list(provider.companies)))),hide_index=True,use_container_width=True)

{"Dashboard":dashboard,"Stock Analysis":stock,"Portfolio":portfolio,"Capital Allocation":allocation,"ATH Scanner":ath,"Backtest":backtest,"Wealth Engine":wealth,"Portfolio News & Threats":news}[page]()
