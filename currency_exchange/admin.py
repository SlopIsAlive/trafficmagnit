from django.contrib import admin
from currency_exchange.models import ExchangeRate, TrackedCurrency


@admin.register(TrackedCurrency)
class TrackedCurrencyAdmin(admin.ModelAdmin):
    list_display = ["iso_code", "is_active", "added_at", "updated_at"]
    list_filter = ["is_active"]
    readonly_fields = ["added_at", "updated_at"]


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ["currency", "exchange_rate", "fetched_at"]
    list_filter = ["currency"]
    readonly_fields = ["fetched_at"]
