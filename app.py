from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")

        # 1. GET LAT-LON
        geo_params = {"name": city, "count": 1}
        geo_response = requests.get(GEOCODE_URL, params=geo_params).json()

        if "results" not in geo_response:
            error = "City not found!"
            return render_template("index.html", weather=weather, error=error)

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]
        city_name = geo_response["results"][0]["name"]

        # 2. GET WEATHER
        weather_params = {"latitude": lat, "longitude": lon, "current_weather": True}
        weather_response = requests.get(WEATHER_URL, params=weather_params).json()

        weather = {
            "city": city_name,
            "temperature": weather_response["current_weather"]["temperature"],
            "windspeed": weather_response["current_weather"]["windspeed"],
            "weathercode": weather_response["current_weather"]["weathercode"]
        }

    return render_template("index.html", weather=weather, error=error)


if __name__ == "__main__":
    app.run(debug=True)
