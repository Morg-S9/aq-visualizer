from datetime import datetime
import json
import requests
import psycopg2

precip_id = list(map(int, open("precip_id.txt", encoding="utf-8").read().splitlines()))

conn = psycopg2.connect(database="data",
                        host="192.168.1.9",
                        user="root",
                        password="1234",
                        port="5432")
db = conn.cursor()


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

timestamp = "\"" + datetime.now().isoformat() + "\""

weatherID = weather.json()["weather"][0]["id"]

location = weather.json()["name"]

envData = weather.json()["main"]
windData = weather.json()["wind"]

aqi = airquality.json()["list"][0]["main"]["aqi"]
airData = airquality.json()["list"][0]["components"]

if weatherID in precip_id:
    PRECIP = True
else:
    PRECIP = False

# Figure out how to auto-null when wind gusts aren't present.


print("INSERT INTO weather VALUES ("
      + str(timestamp)
      + "," + str(weatherID)
      + "," + str(envData["temp"])
      + "," + str(envData["temp_max"])
      + "," + str(envData["temp_min"])
      + "," + str(envData["humidity"])
      + "," + str(windData["speed"])
      + "," + str(windData["deg"])
      + "," + "null"
      + "," + str(envData["pressure"])
      + "," + str(PRECIP) + ");"
      )
