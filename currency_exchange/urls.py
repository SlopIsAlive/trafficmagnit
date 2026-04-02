from django.urls import path
from .views import (
    AddTrackedCurrencyView,
    AvailableCurrenciesView,
    DisableCurrencyMonitoringView,
    EnableCurrencyMonitoringView,
    ExchangeRateHistoryView,
    TrackedCurrencyListView,
)

urlpatterns = [
    path("currencies/", TrackedCurrencyListView.as_view(), name="currency-list"),
    path("currencies/available/", AvailableCurrenciesView.as_view(), name="currency-available"),
    path("currencies/add/", AddTrackedCurrencyView.as_view(), name="currency-add"),
    path("currencies/<int:iso_code>/history/", ExchangeRateHistoryView.as_view(), name="currency-history"),
    path("currencies/<int:iso_code>/enable/", EnableCurrencyMonitoringView.as_view(), name="currency-enable"),
    path("currencies/<int:iso_code>/disable/", DisableCurrencyMonitoringView.as_view(), name="currency-disable"),
]
