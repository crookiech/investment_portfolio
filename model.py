from datetime import date
from pydantic import BaseModel

class Security(BaseModel):
    name: str
    isin: str
    currency: str
    number: int
    nominal_val: float | None
    price: float # цена
    value: float # стоимость

class Report(BaseModel):
    start_reporting_period: date
    end_reporting_period: date
    creation_date: date
    securities: list[Security]