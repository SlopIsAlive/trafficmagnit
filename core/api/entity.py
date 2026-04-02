from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ExchangeRateData:
    currency_code_a: int
    currency_code_b: int
    rate: Decimal
    fetched_at: datetime
