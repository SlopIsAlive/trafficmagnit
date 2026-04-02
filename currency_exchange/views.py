from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from drf_spectacular.types import OpenApiTypes
from iso4217 import Currency
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExchangeRate, TrackedCurrency
from .serializers import (
    AddTrackedCurrencySerializer,
    AvailableCurrencySerializer,
    ExchangeRateHistoryQuerySerializer,
    ExchangeRateHistorySerializer,
    TrackedCurrencySerializer,
)

@extend_schema(tags=["currencies"])
class TrackedCurrencyListView(generics.ListAPIView):
    serializer_class = TrackedCurrencySerializer

    def get_queryset(self):
        return TrackedCurrency.objects.annotate(current_rate=Subquery(ExchangeRate.latest_rate_query()))


@extend_schema(tags=["currencies"])
class AvailableCurrenciesView(APIView):
    @extend_schema(responses=AvailableCurrencySerializer(many=True))
    def get(self, request):
        tracked = set(TrackedCurrency.objects.values_list("iso_code", flat=True))
        available = [
            {"iso_code": c.value, "code": c.code, "name": c.currency_name}
            for c in Currency
            if c.value is not None and c.value not in tracked
        ]
        return Response(AvailableCurrencySerializer(available, many=True).data)


@extend_schema(tags=["currencies"])
class AddTrackedCurrencyView(generics.CreateAPIView):
    serializer_class = AddTrackedCurrencySerializer

    @extend_schema(responses={
        201: TrackedCurrencySerializer,
        409: OpenApiResponse(description="Currency is already being tracked"),
    })
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance, created = TrackedCurrency.objects.get_or_create(
            iso_code=serializer.validated_data["iso_code"],
            defaults={"is_active": True},
        )
        if not created:
            if instance.is_active:
                return Response(
                    {"detail": "Currency is already being tracked."},
                    status=status.HTTP_409_CONFLICT,
                )
            instance.is_active = True
            instance.save(update_fields=["is_active", "updated_at"])
        return Response(TrackedCurrencySerializer(instance).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["rates"])
class ExchangeRateHistoryView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter("from_date", OpenApiTypes.DATETIME, OpenApiParameter.QUERY, required=True),
            OpenApiParameter("to_date", OpenApiTypes.DATETIME, OpenApiParameter.QUERY, required=True),
        ],
        responses={
            200: ExchangeRateHistorySerializer(many=True),
            400: OpenApiResponse(description="Invalid or missing query parameters"),
        },
    )
    def get(self, request, iso_code):
        currency = get_object_or_404(TrackedCurrency, iso_code=iso_code)
        query_serializer = ExchangeRateHistoryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        rates = (
            ExchangeRate.objects.filter(
                currency=currency,
                fetched_at__range=(
                    query_serializer.validated_data["from_date"],
                    query_serializer.validated_data["to_date"],
                ),
            )
            .order_by("fetched_at")
        )
        return Response(ExchangeRateHistorySerializer(rates, many=True).data)


@extend_schema(tags=["monitoring"])
class EnableCurrencyMonitoringView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: TrackedCurrencySerializer,
            409: OpenApiResponse(description="Currency is already active"),
        },
    )
    def post(self, request, iso_code):
        currency = get_object_or_404(TrackedCurrency, iso_code=iso_code)
        if currency.is_active:
            return Response(
                {"detail": "Currency is already active."},
                status=status.HTTP_409_CONFLICT,
            )
        currency.is_active = True
        currency.save(update_fields=["is_active", "updated_at"])
        return Response(TrackedCurrencySerializer(currency).data)


@extend_schema(tags=["monitoring"])
class DisableCurrencyMonitoringView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: TrackedCurrencySerializer,
            409: OpenApiResponse(description="Currency is already inactive"),
        },
    )
    def post(self, request, iso_code):
        currency = get_object_or_404(TrackedCurrency, iso_code=iso_code)
        if not currency.is_active:
            return Response(
                {"detail": "Currency is already inactive."},
                status=status.HTTP_409_CONFLICT,
            )
        currency.is_active = False
        currency.save(update_fields=["is_active", "updated_at"])
        return Response(TrackedCurrencySerializer(currency).data)
