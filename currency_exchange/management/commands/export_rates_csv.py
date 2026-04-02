import csv
from django.core.management.base import BaseCommand
from django.db.models import Subquery
from currency_exchange.models import ExchangeRate, TrackedCurrency
from core.utility.currency import currency_by_code


class Command(BaseCommand):
    help = "Export tracked currencies and their current exchange rates to a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="exchange_rates.csv",
            help="Output file path (default: exchange_rates.csv)",
        )

    def handle(self, *args, **options):
        output = options["output"]

        currencies = (
            TrackedCurrency.objects.filter(is_active=True)
            .annotate(current_rate=Subquery(ExchangeRate.latest_rate_query()))
        )

        with open(output, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["iso_code", "code", "name", "rate_to_uah"])
            for c in currencies:
                currency = currency_by_code(c.iso_code)
                writer.writerow([c.iso_code, currency.code, currency.currency_name, c.current_rate])

        self.stdout.write(self.style.SUCCESS(f"Exported to {output}"))
