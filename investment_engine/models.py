from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

@dataclass(frozen=True)
class CompanyFundamentals:
    ticker: str
    company: str
    market_cap_cr: Optional[float]
    price: Optional[float]
    eps: Optional[float]
    pe: Optional[float]
    revenue_cagr_3y: Optional[float]
    eps_cagr_3y: Optional[float]
    eps_cagr_5y: Optional[float]
    forward_eps_growth: Optional[float]
    pat_cagr_3y: Optional[float]
    roe: Optional[float]
    roce: Optional[float]
    debt_to_equity: Optional[float]
    ocf_cr: Optional[float]
    fcf_cr: Optional[float]
    margin_trend: Optional[float]
    promoter_holding: Optional[float]
    promoter_pledge: Optional[float]
    dilution_pct: Optional[float]
    governance_risk: bool = False

@dataclass(frozen=True)
class Holding:
    ticker: str
    quantity: float
    average_buy_price: float

@dataclass(frozen=True)
class NewsItem:
    ticker: str
    published_at: date
    headline: str
    summary: str
    materiality: str
    category: str
    thesis_impact: str

@dataclass(frozen=True)
class ScoreResult:
    ticker: str
    total: int
    factors: dict
    hard_gates: dict
    decision: str
    multibagger_class: str
    projected_3y_earnings_multiple: Optional[float]
    thesis_status: str
    risk_flags: list[str]

@dataclass(frozen=True)
class AthEvent:
    ticker: str
    breakout_date: date
    previous_ath: float
    breakout_price: float
    days_above_previous_ath: int
    max_pct_above_previous_ath: float
    current_pct_above_previous_ath: float
    retests: int
