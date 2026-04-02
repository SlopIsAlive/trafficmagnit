from celery import shared_task
from django.core.cache import cache
from iso4217 import Currency

from core.api import entity
from core.api.monobank import mono_client
from currency_exchange.models import ExchangeRate, TrackedCurrency

MONO_RATES_CACHE_KEY = "monobank_rates"
MONO_RATES_CACHE_TTL = 65

@shared_task(name="currency.fetch_rates", bind=True, max_retries=3)
def fetch_rates(self, iso_code: int | None = None):
    try:
        rates = cache.get(MONO_RATES_CACHE_KEY)
        if rates is None:
            rates = mono_client.get_exchange_rate_to_uah()
            cache.set(MONO_RATES_CACHE_KEY, rates, MONO_RATES_CACHE_TTL)
        if iso_code:
            rates = [r for r in rates if r.currency_code_a == iso_code or r.currency_code_b == iso_code]
        save_exchange_rates(rates)
    except Exception as e:
        self.retry(exc=e, countdown=60)

def save_exchange_rates(rates: list[entity.ExchangeRateData]):
    UAH_ISO = Currency.uah.number
    tracked = {
        tc.iso_code: tc
        for tc in TrackedCurrency.objects.filter(is_active=True)
    }

    to_create = []
    for rate in rates:
        if UAH_ISO not in (rate.currency_code_a, rate.currency_code_b):
            continue
        uah_is_base = rate.currency_code_a == UAH_ISO
        non_uah_code = rate.currency_code_b if uah_is_base else rate.currency_code_a

        if non_uah_code not in tracked:
            continue

        to_create.append(
            ExchangeRate(
                currency=tracked[non_uah_code],
                exchange_rate= 1 / rate.rate if uah_is_base else rate.rate,
                fetched_at=rate.fetched_at,
            )
        )
    ExchangeRate.objects.bulk_create(to_create)
