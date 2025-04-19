from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.cache import cache
import os
import json
from django.conf import settings

from travel.utils import calculate_top_districts


WEATHER_API = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"


def load_local_districts():
    path = os.path.join(settings.BASE_DIR, "data", "bd-districts.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    

@extend_schema(
    parameters=[
        OpenApiParameter("page"),
        OpenApiParameter("size"),
    ],
    summary="Get Top 10 Coolest & Cleanest Districts",
    description="Returns the top 10 districts ranked by lowest average temperature at 2 PM and PM2.5 air quality over the next 7 days."
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_top_districts(request):
    print("recieved the req")
    data = cache.get("top_districts")
    if data:
        return Response(json.loads(data), status=status.HTTP_200_OK)
    else:
        data = calculate_top_districts()
        print("data", data)
        cache.set("top_districts", json.dumps(data), timeout=3600)

        return Response(data, status=status.HTTP_200_OK)
        # return Response({"error": "Data not ready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    