import json
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestGetTopDistrictsView:

    @patch("travel.views.district_recommendation_views.cache.get")
    def test_returns_cached_data(self, mock_cache_get):
        mock_data = [{"district": "Dhaka", "average_temperature": 25, "average_pm2_5": 30}]
        mock_cache_get.return_value = json.dumps(mock_data)

        client = APIClient()
        response = client.get(reverse("top_districts"))

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_data
        mock_cache_get.assert_called_once_with("top_districts")

    @patch("travel.views.district_recommendation_views.cache.set")
    @patch("travel.views.district_recommendation_views.calculate_top_districts")
    @patch("travel.views.district_recommendation_views.cache.get", return_value=None)
    def test_calculates_and_caches_if_no_cache(self, mock_cache_get, mock_calculate, mock_cache_set):
        mock_data = [{"district": "Sylhet", "average_temperature": 24.2, "average_pm2_5": 28.5}]
        mock_calculate.return_value = mock_data

        client = APIClient()
        response = client.get(reverse("top_districts"))

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_data
        mock_calculate.assert_called_once()
        mock_cache_set.assert_called_once_with("top_districts", json.dumps(mock_data), timeout=3600)
