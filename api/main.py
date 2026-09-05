from fastapi import FastAPI,HTTPException
from investment_engine.data_provider import DummyDataProvider
from investment_engine.scoring import score_company
from database.session import init_db
app=FastAPI(title="Multibagger Lab API",version="1.0.0")
provider=DummyDataProvider(); init_db()
@app.get("/health")
def health(): return {"status":"ok","data_mode":"DEMO"}
@app.get("/companies/{ticker}/analysis")
def analysis(ticker:str):
    try:f=provider.fundamentals(ticker)
    except KeyError as e:raise HTTPException(404,str(e))
    return {"data_mode":"DEMO","fundamentals":f.__dict__,"score":score_company(f).__dict__}
