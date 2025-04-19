from django.urls import path
from travel.views import travel_recommendation_views as views

urlpatterns = [
    path("destination_check/", views.destination_check),
]
