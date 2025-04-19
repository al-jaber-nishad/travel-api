from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from travel.serializers import TravelRecommendationSerializer
from travel.utils import get_temp_and_pm25, load_local_districts
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

@extend_schema(
    summary="Travel Recommendation",
    description="Checks if it's a good idea to travel based on temperature and air quality.",
    parameters=[
        OpenApiParameter(name="current_lat", type=OpenApiTypes.FLOAT, required=True, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="current_lon", type=OpenApiTypes.FLOAT, required=True, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="destination", type=OpenApiTypes.STR, required=True, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="travel_date", type=OpenApiTypes.DATE, required=True, location=OpenApiParameter.QUERY),
    ],
    responses={
        200: OpenApiTypes.OBJECT,  # or a serializer if you want a strict schema
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT
    },
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def destination_check(request):
    serializer = TravelRecommendationSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    current_lat = data['current_lat']
    current_lon = data['current_lon']
    destination_name = data['destination']
    travel_date = data['travel_date'].isoformat()

    # Load destination lat/lon
    districts = load_local_districts()
    destination_info = next((d for d in districts["districts"] if d["name"].lower() == destination_name.lower()), None)

    if not destination_info:
        return Response({"error": "Destination district not found"}, status=404)

    dest_lat = destination_info["lat"]
    dest_lon = destination_info["long"]

    # Fetch weather + air data
    cur_temp, cur_pm = get_temp_and_pm25(current_lat, current_lon, travel_date)
    dest_temp, dest_pm = get_temp_and_pm25(dest_lat, dest_lon, travel_date)

    print("dest_temp", dest_temp, cur_temp)

    # Recommendation logic
    if dest_temp < cur_temp and dest_pm < cur_pm:
        status_text = "Recommended"
        reason = f"Your destination is {round(cur_temp - dest_temp, 1)}°C cooler and has better air quality (PM2.5 {cur_pm} → {dest_pm}). Enjoy your trip!"
    else:
        status_text = "Not Recommended"
        reason = f"Your destination is warmer or has worse air quality (PM2.5 {cur_pm} → {dest_pm}). Better to stay where you are."

    return Response({
        "recommendation": status_text,
        "reason": reason,
        "comparison": {
            "current_location": {"temp": cur_temp, "pm2_5": cur_pm},
            "destination": {"temp": dest_temp, "pm2_5": dest_pm}
        }
    })
