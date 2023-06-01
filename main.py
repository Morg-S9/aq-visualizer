from datetime import datetime
import json
import requests
import psycopg2

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

location = weather.json()["name"]
weatherData = weather.json()["main"]

aqi = airquality.json()["list"][0]["main"]["aqi"]
airData = airquality.json()["list"][0]["components"]

timestamp = "\"" + datetime.now().isoformat() + "\""
print("INSERT INTO weather VALUES ("
      + timestamp
      + "," + weatherData["temp"]
      )