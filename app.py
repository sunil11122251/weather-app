from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
REV_GEO_URL = "https://geocoding-api.open-meteo.com/v1/reverse"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_DESC = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Heavy Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    71: "Snowfall",
    80: "Rain Showers",
    81: "Moderate Showers",
    82: "Violent Showers",
    95: "Thunderstorm",
    96: "Thunder w/ Hail",
    99: "Severe Thunderstorm"
}

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def weather():
    data = request.json

    # If searching by city
    if "city" in data:
        city = data["city"]
        geo = requests.get(GEO_URL, params={"name": city, "count": 1}).json()
        if "results" not in geo:
            return jsonify({"error": "City not found"})
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        city_name = geo["results"][0]["name"]

    # If using GPS → reverse geocode city
    else:
        lat = data["lat"]
        lon = data["lon"]

        rev = requests.get(REV_GEO_URL, params={
            "latitude": lat,
            "longitude": lon
        }).json()

        if "results" in rev:
            city_name = rev["results"][0]["name"]
        else:
            city_name = "Current Location"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto",
        "daily": ["weathercode", "temperature_2m_max", "temperature_2m_min"],
        "hourly": ["temperature_2m"]
    }

    w = requests.get(WEATHER_URL, params=params).json()

    if "current_weather" not in w:
        return jsonify({"error": "Weather unavailable", "raw": w})

    cur = w["current_weather"]
    code = cur["weathercode"]

    return jsonify({
        "city": city_name,
        "temp": cur["temperature"],
        "windspeed": cur["windspeed"],
        "weathercode": code,
        "description": WEATHER_DESC.get(code, "Unknown"),
        "time": cur["time"],
        "daily": w.get("daily", {}),
        "hourly": w.get("hourly", {})
    })


if __name__ == "__main__":
    app.run(debug=True)
