from datetime import datetime
import json
import requests

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

parameters = {
    "apikey": "bc1321f88951a4ba65bc02e181d4ca60",
    "lat": "39.144379",
    "lon": "-76.528839",
    "units": "imperial"
}

weather = requests.get(
    "https://api.openweathermap.org/data/2.5/weather", params=parameters, timeout=20)
airquality = requests.get(
    "https://api.openweathermap.org/data/2.5/air_pollution", params=parameters, timeout=20)

location = weather.json()["name"]
weatherData = weather.json()["main"]

aqi = airquality.json()["list"][0]["main"]["aqi"]
airData = airquality.json()["list"][0]["components"]

print(
    "Timestamp: " + str(datetime.now().isoformat()),
    "\n",
    "Location: " + location,
    "\n\n",
    "Air Quality Index: " + str(aqi),
    "\n",
    "PM2.5: " + str(airData["pm2_5"]) + "μg/m3",
    "\n",
    "PM10: " + str(airData["pm10"]) + "μg/m3",
    "\n",
    "Carbon Monoxide: " + str(airData["co"]) + "μg/m3",
    "\n",
    "Nitrogen Dioxide: " + str(airData["no2"]) + "μg/m3",
    "\n",
    "Ozone: " + str(airData["o3"]) + "μg/m3",
    "\n",
    "Sulphur Dioxide: " + str(airData["so2"]) + "μg/m3",
    "\n\n",
    "(μg/m3 = Micrograms per meter cubed)\n",
)

print(
    "Weather:\nTemprature: " + str(round(weatherData["temp"])) + "°F",
    "\nHumidity: " + str(round(weatherData["humidity"])) + "°F"
)