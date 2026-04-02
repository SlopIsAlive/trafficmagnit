from datetime import datetime, timezone

from iso4217 import Currency
from core.api.base_client import BaseAPIClient
from core.api.entity import ExchangeRateData


class MonoAPI(BaseAPIClient):
    def __init__(self, timeout: float = 5, base_url: str = "https://api.monobank.ua"):
        super().__init__(timeout, base_url)

    def get_exchange_rate_to_uah(self, **kwargs) -> list[ExchangeRateData]:
        now = datetime.now(timezone.utc)
        response = self.request(self.client.get, url=f"{self.base_url}/bank/currency", **kwargs)
        # cause mono always returns uah as codeB if uah is present
        uah_values = [r for r in response if r["currencyCodeB"] == Currency.uah.number]  # pyright: ignore[reportAttributeAccessIssue]
        return [
            ExchangeRateData(
                currency_code_a=r["currencyCodeA"],
                currency_code_b=r["currencyCodeB"],
                rate=r.get("rateCross") or (r["rateBuy"] + r["rateSell"]) / 2,
                fetched_at=now,
            )
            for r in uah_values
        ]

mono_client = MonoAPI()
