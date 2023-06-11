from datetime import datetime
import json
import time
import requests
import psycopg2

# Create lists for Rain and Snow weather IDs
with open("precip_id.txt", 'r', encoding="utf-8") as data:
    content = data.read()
data_sets = content.split("\n\n")
rainids = []
snowids = []

for item in data_sets[0].split("\n"):
    rainids.append(int(item))
for item in data_sets[1].split("\n"):
    snowids.append(int(item))

# Setup connection configs

with open('config.json', 'r', encoding="utf-8") as f:
    config = json.load(f)

# Setup database connection
conn = psycopg2.connect(database=config['database']['name'],
                        host=config['database']['host'],
                        user=config['database']['username'],
                        password=config['database']['password'],
                        port=config['database']['port'])
db = conn.cursor()

# Set API parameters
parameters = {
    "appid": config['api']['apikey'],
    "lat": config['api']['latitude'],
    "lon": config['api']['longitude'],
    "units": config['api']['units']
}

while True:
    # Make API Requests
    print("Making API Requests...")
    weather = requests.get(
        "https://api.openweathermap.org/data/2.5/weather", params=parameters, timeout=20)
    airquality = requests.get(
        "https://api.openweathermap.org/data/2.5/air_pollution", params=parameters, timeout=20)

    # Check status code for errors
    if weather.status_code != 200 or airquality.status_code != 200:
        print("\nAPI error. Status:\n"
              + "Weather: " + str(weather.status_code) + "\n" + weather.text
              + "\nAir Qual.: " +
              str(airquality.status_code) + "\n" + weather.text
              )
        conn.close()
        exit()
    else:
        print("Done.\n")

    # Sort through data
    timestamp = "'" + datetime.now().isoformat() + "'"
    location = weather.json()["name"]
    weatherID = weather.json()["weather"][0]["id"]
    envData = weather.json()["main"]
    windData = weather.json()["wind"]
    aqi = airquality.json()["list"][0]["main"]["aqi"]
    airData = airquality.json()["list"][0]["components"]

    # Set precip flag
    if weatherID in rainids or weatherID in snowids:
        PRECIP = True
    else:
        PRECIP = False

    # Compile weather database command
    db.execute("INSERT INTO weather VALUES ("
               + timestamp
               + "," + str(weatherID)
               + "," + str(envData["temp"])
               + "," + str(envData["temp_max"])
               + "," + str(envData["temp_min"])
               + "," + str(envData["humidity"])
               + "," + str(windData["speed"])
               + "," + str(windData["deg"])
               + "," + str(envData["pressure"])
               + "," + str(PRECIP) + ");"
               )

    # Check if precip database command needs to be made
    if PRECIP is True:
        print("Precipitation data will be included.\n ")
        if weatherID in rainids:
            precipData = weather.json()["rain"]
        else:
            precipData = weather.json()["snow"]
        if "1h" in precipData.keys():
            H1PRECIP = precipData["1h"]
        else:
            H1PRECIP = "NULL"
        if "3h" in precipData.keys():
            H3PRECIP = precipData["3h"]
        else:
            H3PRECIP = "NULL"

        db.execute("INSERT INTO precipitation VALUES ("
                   + timestamp
                   + "," + str(weatherID)
                   + "," + str(H1PRECIP)
                   + "," + str(H3PRECIP) + ");"
                   )

    # Compile air quality database command
    db.execute("INSERT INTO air VALUES ("
               + timestamp
               + "," + str(aqi)
               + "," + str(airData["pm2_5"])
               + "," + str(airData["pm10"])
               + "," + str(airData["co"])
               + "," + str(airData["no2"])
               + "," + str(airData["o3"])
               + "," + str(airData["so2"]) + ");")

    # Commit changes to database and wait
    conn.commit()
    print("Data stored. Timestamp: " + timestamp + "\n")
    time.sleep(config['program']['waittimer'])