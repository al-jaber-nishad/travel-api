from rest_framework import serializers

class TravelRecommendationSerializer(serializers.Serializer):
    current_lat = serializers.FloatField()
    current_lon = serializers.FloatField()
    destination = serializers.CharField()
    travel_date = serializers.DateField()
