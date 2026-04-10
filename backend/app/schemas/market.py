from pydantic import BaseModel


class MarketPriceItem(BaseModel):
    province_code: str
    market_date: str
    timeslot: str
    price: float
    source: str | None = None
