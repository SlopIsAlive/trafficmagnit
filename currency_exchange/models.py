from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from iso4217 import Currency


def validate_iso_code(value):
    try:
        Currency(value)
    except ValueError:
        raise ValidationError(f"{value} is not a valid iso 4217 currency code")


class TrackedCurrency(models.Model):
    iso_code = models.PositiveSmallIntegerField(unique=True, validators=[validate_iso_code,])
    is_active = models.BooleanField(default=True)

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tracked_currency"

    def __str__(self):
        return f"{Currency(self.iso_code).code} active={self.is_active}"

    def save(self, *args, **kwargs):
        validate_iso_code(self.iso_code)
        super().save(*args, **kwargs)

# All currencies exchange rates are stored with respect to uah
class ExchangeRate(models.Model):
    currency = models.ForeignKey(TrackedCurrency, on_delete=models.CASCADE, related_name="rates")
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6)

    # not auto_now_add in case we wanna backfill this
    fetched_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "exchange_rate"

    @classmethod
    def latest_rate_query(cls):
        return cls.objects.filter(currency=models.OuterRef("pk")).order_by("-fetched_at").values("exchange_rate")[:1]
