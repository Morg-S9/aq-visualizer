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
    "http://api.openweathermap.org/data/2.5/air_pollution", params=parameters, timeout=20)

aqlevels = airquality.json()["list"][0]

aqi = aqlevels["main"]["aqi"]

pm2_5 = aqlevels["components"]["pm2_5"]
pm10 = aqlevels["components"]["pm10"]
co = aqlevels["components"]["co"]
no2 = aqlevels["components"]["no2"]
o3 = aqlevels["components"]["o3"]
so2 = aqlevels["components"]["so2"]

print(
    "Air Quality Index: " + str(aqi),
    "\n",
    "\n",
    "PM2.5: " + str(pm2_5) + "μg/m3",
    "\n",
    "PM10: " + str(pm10) + "μg/m3",
    "\n",
    "Carbon Monoxide: " + str(co) + "μg/m3",
    "\n",
    "Nitrogen Dioxide: " + str(no2) + "μg/m3",
    "\n",
    "Ozone: " + str(o3) + "μg/m3",
    "\n",
    "Sulphur Dioxide: " + str(so2) + "μg/m3",
    "\n\n",
    "(μg/m3 = Micrograms per meter cubed)"
)
