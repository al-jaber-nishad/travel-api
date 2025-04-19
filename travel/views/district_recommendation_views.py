from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
import requests
from datetime import datetime, timedelta
import os
import json
from django.conf import settings


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
    try:
        districts_data = load_local_districts()
        districts = districts_data["districts"]
        today = datetime.today().date()
        results = []

        for district in districts:
            print("district", district)
            name = district["name"]
            lat = district["lat"]
            long = district["long"]

            # Weather API
            weather_resp = requests.get(WEATHER_API, params={
                "latitude": lat,
                "longitude": long,
                "hourly": "temperature_2m",
                "timezone": "Asia/Dhaka"
            }).json()

            # Filter for 2 PM over the next 7 days
            temps = []
            times = weather_resp["hourly"]["time"]
            values = weather_resp["hourly"]["temperature_2m"]

            for i, ts in enumerate(times):
                dt = datetime.fromisoformat(ts)
                if dt.hour == 14 and today <= dt.date() <= today + timedelta(days=6):
                    temps.append(values[i])

            avg_temp = round(sum(temps) / len(temps), 2) if temps else 999

            # Air Quality API
            air_resp = requests.get(AIR_QUALITY_API, params={
                "latitude": lat,
                "longitude": long,
                "hourly": "pm2_5",
                "timezone": "Asia/Dhaka"
            }).json()
            print("air_resp", air_resp)
            pm_values = air_resp["hourly"]["pm2_5"][:7 * 24]  # First 7 days
            # print("pm_values", pm_values)
            valid_pm_values = [v for v in pm_values if v is not None]
            avg_pm2_5 = round(sum(valid_pm_values) / len(valid_pm_values), 2) if valid_pm_values else 999

            
            results.append({
                "district": name,
                "average_temperature": avg_temp,
                "average_pm2_5": avg_pm2_5
            })

        # Sort by temperature (ASC), then PM2.5 (ASC)
        sorted_results = sorted(results, key=lambda x: (x["average_temperature"], x["average_pm2_5"]))
        return Response(sorted_results[:10], status=status.HTTP_200_OK)

    except Exception as e:
        print("Error fetching data:", e)
        return Response({'error': 'Failed to fetch data', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    