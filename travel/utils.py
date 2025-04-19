from django.conf import settings
import requests
import json
import os
from datetime import datetime, timedelta

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"

def calculate_top_districts(limit=10):
    try:
        # Load districts from local JSON
        districts = load_local_districts()

        today = datetime.today().date()
        results = []

        for district in districts:
            print("name", district["name"])
            name = district["name"]
            lat = district["lat"]
            long = district["long"]

            # --- Fetch temperature data ---
            weather_resp = requests.get(WEATHER_API, params={
                "latitude": lat,
                "longitude": long,
                "hourly": "temperature_2m",
                "timezone": "Asia/Dhaka"
            }).json()

            temps = []
            times = weather_resp.get("hourly", {}).get("time", [])
            values = weather_resp.get("hourly", {}).get("temperature_2m", [])

            for i, ts in enumerate(times):
                dt = datetime.fromisoformat(ts)
                if dt.hour == 14 and today <= dt.date() <= today + timedelta(days=6):
                    temps.append(values[i])

            avg_temp = round(sum(temps) / len(temps), 2) if temps else 999

            # --- Fetch air quality data ---
            air_resp = requests.get(AIR_QUALITY_API, params={
                "latitude": lat,
                "longitude": long,
                "hourly": "pm2_5",
                "timezone": "Asia/Dhaka"
            }).json()

            pm_values = air_resp.get("hourly", {}).get("pm2_5", [])[:7 * 24]
            valid_pm = [v for v in pm_values if v is not None]
            avg_pm2_5 = round(sum(valid_pm) / len(valid_pm), 2) if valid_pm else 999

            results.append({
                "district": name,
                "average_temperature": avg_temp,
                "average_pm2_5": avg_pm2_5
            })

        # Sort by coolest first, then cleanest
        sorted_results = sorted(results, key=lambda x: (x["average_temperature"], x["average_pm2_5"]))
        print("sorted_results", sorted_results)
        return sorted_results[:limit]

    except Exception as e:
        print("Error in calculate_top_districts:", e)
        return []



def load_local_districts():
    path = os.path.join(settings.BASE_DIR, "data", "bd-districts.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    


def get_temp_and_pm25(lat, long, travel_date):
    if isinstance(travel_date, str):
        travel_date = datetime.fromisoformat(travel_date).date()
    # Fetch weather data
    weather_resp = requests.get(WEATHER_API, params={
        "latitude": lat,
        "longitude": long,
        "hourly": "temperature_2m",
        "timezone": "Asia/Dhaka",
    }).json()
    
    times = weather_resp.get("hourly", {}).get("time", [])
    temps = weather_resp.get("hourly", {}).get("temperature_2m", [])
    temp_at_2pm = None

            
    for i, ts in enumerate(times):
        dt = datetime.fromisoformat(ts)
        if dt.date() == travel_date and dt.hour == 14:
            temp_at_2pm = temps[i]
            break

    # Fetch air quality
    air_resp = requests.get(AIR_QUALITY_API, params={
        "latitude": lat,
        "longitude": long,
        "hourly": "pm2_5",
        "timezone": "Asia/Dhaka",
        "start_date": travel_date,
        "end_date": travel_date
    }).json()

    pm_values = air_resp.get("hourly", {}).get("pm2_5", [])
    valid_pm_values = [v for v in pm_values if v is not None]
    avg_pm2_5 = round(sum(valid_pm_values) / len(valid_pm_values), 2) if valid_pm_values else 999

    return temp_at_2pm or 999, avg_pm2_5