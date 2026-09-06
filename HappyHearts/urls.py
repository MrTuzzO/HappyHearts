from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),

    path('healthz/', health_check, name='health-check'),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # App URLs
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/onboarding/", include("onboarding.urls")),
    path("api/v1/community/", include("community.urls")),
]
