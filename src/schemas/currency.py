from pydantic import BaseModel


class CurrencySchema(BaseModel):
    code: str
    name: str
    rate: float
