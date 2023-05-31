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

levels = airquality.json()["list"][0]["components"]

aqi = airquality.json()["list"][0]["main"]["aqi"]

print(
    "Timestamp: " + str(datetime.now().isoformat()),
    "\n",
    "Air Quality Index: " + str(aqi),
    "\n",
    "\n",
    "PM2.5: " + str(levels["pm2_5"]) + "μg/m3",
    "\n",
    "PM10: " + str(levels["pm10"]) + "μg/m3",
    "\n",
    "Carbon Monoxide: " + str(levels["co"]) + "μg/m3",
    "\n",
    "Nitrogen Dioxide: " + str(levels["no2"]) + "μg/m3",
    "\n",
    "Ozone: " + str(levels["o3"]) + "μg/m3",
    "\n",
    "Sulphur Dioxide: " + str(levels["so2"]) + "μg/m3",
    "\n\n",
    "(μg/m3 = Micrograms per meter cubed)"
)
