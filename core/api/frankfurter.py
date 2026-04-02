from datetime import datetime, timezone

from iso4217 import Currency
from core.api.base_client import BaseAPIClient
from core.api.entity import ExchangeRate
from core.utility.currency import currency_by_code


class FrankfurterAPI(BaseAPIClient):
    def __init__(self, timeout: float = 5.0, base_url: str = "https://api.frankfurter.dev/v2"):
        super().__init__(timeout, base_url)

    def get_exchange_rates(self, iso_code=Currency.uah.number, **kwargs) -> list[ExchangeRate]:  # pyright: ignore[reportAttributeAccessIssue]
        now = datetime.now(timezone.utc)
        response = self.request(
            self.client.get,
            url=f"{self.base_url}/rates/",
            params={"base": currency_by_code(iso_code).name.upper(),},
            **kwargs,
        )
        return [
            ExchangeRate(
                currency_code_a=r["base"],
                currency_code_b=r["quote"],
                rate=r["rate"],
                fetched_at=now,
            )
            for r in response
        ]


frankfurter_client = FrankfurterAPI()
