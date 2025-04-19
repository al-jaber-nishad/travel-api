from rest_framework.test import APITestCase
from unittest.mock import patch
from django.urls import reverse
from datetime import date

class DestinationCheckTests(APITestCase):
    def setUp(self):
        self.url = reverse('destination_check')
        self.valid_params = {
            "current_lat": 23.8103,
            "current_lon": 90.4125,
            "destination": "Sylhet",
            "travel_date": date.today().isoformat()
        }

    @patch("travel.views.travel_recommendation_views.get_temp_and_pm25")
    @patch("travel.views.travel_recommendation_views.load_local_districts")
    def test_recommendation_success(self, mock_load_districts, mock_get_data):
        mock_load_districts.return_value = {
            "districts": [
                {"name": "Sylhet", "lat": 24.8949, "long": 91.8687}
            ]
        }

        mock_get_data.side_effect = [
            (35.0, 80.0),  # current
            (30.0, 50.0)   # destination
        ]

        response = self.client.get(self.url, self.valid_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recommendation'], "Recommended")
        self.assertIn("cooler and has better air quality", response.data['reason'])

    @patch("travel.views.travel_recommendation_views.get_temp_and_pm25")
    @patch("travel.views.travel_recommendation_views.load_local_districts")
    def test_not_recommended(self, mock_load_districts, mock_get_data):
        mock_load_districts.return_value = {
            "districts": [
                {"name": "Sylhet", "lat": 24.8949, "long": 91.8687}
            ]
        }

        mock_get_data.side_effect = [
            (30.0, 40.0),  # current
            (35.0, 60.0)   # destination
        ]

        response = self.client.get(self.url, self.valid_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['recommendation'], "Not Recommended")
        self.assertIn("warmer or has worse air quality", response.data['reason'])

    @patch("travel.views.travel_recommendation_views.load_local_districts")
    def test_invalid_destination(self, mock_load_districts):
        mock_load_districts.return_value = {
            "districts": []
        }
        response = self.client.get(self.url, self.valid_params)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], "Destination district not found")

    def test_invalid_params(self):
        response = self.client.get(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("current_lat", response.data)
        self.assertIn("destination", response.data)
