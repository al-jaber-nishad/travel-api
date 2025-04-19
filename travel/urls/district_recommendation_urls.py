
from django.urls import path
from travel.views import district_recommendation_views as views


urlpatterns = [
    path('top_districts/', views.get_top_districts, name='top_districts'),

]