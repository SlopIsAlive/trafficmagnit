from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class TaggedTokenObtainPairView(TokenObtainPairView):
    @extend_schema(tags=["auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaggedTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=["auth"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TaggedTokenObtainPairView.as_view(), name="token-obtain"),
    path("api/auth/token/refresh/", TaggedTokenRefreshView.as_view(), name="token-refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("currency_exchange.urls")),
]
