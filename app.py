import requests
import json
import math
import convertepoch
from datetime import datetime, timedelta

# Constants for Stefan Model
K_ICE = 2.2  
L_FUSION = 334000  
ICE_DENSITY = 917  
SECONDS_PER_DAY = 86400  
T_WATER = -1.8  

# API Keys
OPENWEATHER_API_KEY = "1b1ac42ec05617c8187b79dfae918fae"
WORLDTIDES_API_KEY = "4ea10d76-6b6e-4cc8-a704-24b93076328e"

def fetch_tide_data(lat, lon):
    tide_data = {}
    for days_ago in range(6, -1, -1):
        date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        url = f"https://www.worldtides.info/api/v3?heights&lat={lat}&lon={lon}&start={date}&key={WORLDTIDES_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if "heights" in data and data["heights"]:
            avg_tide_height = sum(h["height"] for h in data["heights"]) / len(data["heights"])
            tide_data[date] = round(avg_tide_height, 2)
        else:
            tide_data[date] = 0.0
    return tide_data

def fetch_past_weather(lat, lon):
    past_weather = []
    for days_ago in range(6, 0, -1):
        date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={date}&end_date={date}&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max,snowfall_sum&timezone=UTC"
        response = requests.get(url)
        data = response.json()
        if "daily" in data:
            min_temp = float(data["daily"].get("temperature_2m_min", [None])[0] or 0.0)
            max_temp = float(data["daily"].get("temperature_2m_max", [None])[0] or 0.0)
            wind_speed = float(data["daily"].get("wind_speed_10m_max", [None])[0] or 0.0) * 3.6
            snowfall = float(data["daily"].get("snowfall_sum", [None])[0] or 0.0)
            past_weather.append({
                "date": date, "min_temp": min_temp, "max_temp": max_temp,
                "wind_speed": wind_speed, "snowfall": snowfall
            })
    return past_weather

def fetch_current_weather(lat, lon):
    base_url = "https://api.openweathermap.org/data/3.0/onecall?"
    url = f"{base_url}&appid={OPENWEATHER_API_KEY}&lat={lat}&lon={lon}&units=metric&exclude=hourly,minutely,current,alerts"
    response = requests.get(url)
    data = json.loads(response.text)
    dt = data["daily"][0]["dt"]
    min_temp = float(data["daily"][0]["temp"].get("min", 0.0))
    max_temp = float(data["daily"][0]["temp"].get("max", 0.0))
    wind_speed = float(data["daily"][0].get("wind_speed", 0.0)) * 3.6
    sunlight = data["daily"][0].get("uvi", 0)
    snowfall = float(data["daily"][0].get("snow", 0.0))
    return [{
        "date": convertepoch.convert(dt), "min_temp": min_temp, "max_temp": max_temp,
        "wind_speed": wind_speed, "sunlight": sunlight, "snowfall": snowfall
    }]

def calculate_ice_formation(weather_data, tide_data, lat, lon):
    total_ice_m = 0
    report_data = []
    for day_data in weather_data:
        date = day_data["date"]
        min_temp = day_data["min_temp"]
        max_temp = day_data["max_temp"]
        avg_temp = (min_temp + max_temp) / 2
        wind_speed = day_data["wind_speed"]
        sunlight = day_data.get("sunlight", 0)
        snowfall = day_data.get("snowfall", 0)
        tide_level = tide_data.get(date, 0.0)
        if avg_temp >= 0:
            report_data.append([date, min_temp, max_temp, wind_speed, snowfall, tide_level, "No Ice Growth"])
            continue
        temp_difference = T_WATER - avg_temp
        stefan_ice_growth = math.sqrt((2 * K_ICE * temp_difference * SECONDS_PER_DAY) / (L_FUSION * ICE_DENSITY))
        ice_growth_factor = math.exp(-0.1 * wind_speed) * (1.0 - 0.1 * sunlight) * (1.0 - 0.15 * tide_level)
        snow_insulation_factor = max(0.1, 1.0 - (0.05 * snowfall))
        ice_growth_factor *= snow_insulation_factor
        daily_ice_growth = stefan_ice_growth * ice_growth_factor
        total_ice_m += daily_ice_growth
        report_data.append([date, min_temp, max_temp, wind_speed, snowfall, tide_level, round(daily_ice_growth * 39.37, 2)])
    total_ice_inches = round(total_ice_m * 39.37, 2)
    return total_ice_inches, report_data
