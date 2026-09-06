from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.permissions import IsAdmin
from .models import SiteSettings
from .serializers import SiteSettingsSerializer


class SiteSettingsView(APIView):
    """Public read (privacy policy, contact info, social links); admin-only edit."""

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAdmin()]
        return [AllowAny()]

    @extend_schema(responses={200: SiteSettingsSerializer})
    def get(self, request):
        return Response(SiteSettingsSerializer(SiteSettings.get_solo()).data)

    @extend_schema(request=SiteSettingsSerializer, responses={200: SiteSettingsSerializer})
    def patch(self, request):
        serializer = SiteSettingsSerializer(SiteSettings.get_solo(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
