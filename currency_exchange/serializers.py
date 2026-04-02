from rest_framework import serializers
from iso4217 import Currency
from .models import ExchangeRate, TrackedCurrency


class TrackedCurrencySerializer(serializers.ModelSerializer):
    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    current_rate = serializers.DecimalField(
        max_digits=18, decimal_places=6, read_only=True, allow_null=True
    )

    class Meta:
        model = TrackedCurrency
        fields = ["id", "iso_code", "code", "name", "is_active", "current_rate", "added_at"]

    def get_code(self, obj) -> str:
        return Currency(obj.iso_code).code

    def get_name(self, obj) -> str:
        return Currency(obj.iso_code).currency_name


class AddTrackedCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedCurrency
        fields = ["iso_code"]


class AvailableCurrencySerializer(serializers.Serializer):
    iso_code = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()


class ExchangeRateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ["exchange_rate", "fetched_at"]


class ExchangeRateHistoryQuerySerializer(serializers.Serializer):
    from_date = serializers.DateTimeField()
    to_date = serializers.DateTimeField()

    def validate(self, attrs):
        if attrs["from_date"] >= attrs["to_date"]:
            raise serializers.ValidationError("from_date must be before to_date")
        return attrs


class ToggleMonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackedCurrency
        fields = ["is_active"]
