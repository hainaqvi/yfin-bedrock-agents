from pydantic import BaseModel
from typing import Optional, Dict
from decimal import Decimal

class Ticker(BaseModel):
    symbol: str  # ticker symbol

class TickerMetrics(Ticker):
    list_name: str  # list name (dow, sp500, nasdaq)
    shortName: Optional[str] = None
    sector: Optional[str] = None
    marketCap: Optional[Decimal] = None
    trailingPE: Optional[Decimal] = None
    forwardPE: Optional[Decimal] = None
    revenueGrowth: Optional[Decimal] = None
    grossMargins: Optional[Decimal] = None
    operatingMargins: Optional[Decimal] = None
    returnOnAssets: Optional[Decimal] = None
    returnOnEquity: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    debtToEquity: Optional[Decimal] = None
    recommendationKey: Optional[str] = None
    compositeScore: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    weightBySector: Optional[Decimal] = None


class TickerInfo(Ticker):
    pass

class TickerDetail(Ticker):
    stock_info: Optional[Dict] = None
    recommendations: Optional[list] = None
    holders: Optional[Dict] = None
    data: Optional[Dict] = None

    class Config:
        from_attributes = True


