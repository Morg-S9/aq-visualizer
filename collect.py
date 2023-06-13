from datetime import datetime
import time
import simplejson as json
import pytz
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

# Database connection function
def db_connect():
    conn = psycopg2.connect(database=config['database']['name'],
                            host=config['database']['host'],
                            user=config['database']['logins']['collect']['username'],
                            password=config['database']['logins']['collect']['password'],
                            port=config['database']['port'])
    db = conn.cursor()
    return conn, db


# Set API parameters
parameters = {
    "appid": config['openweatherapi']['apikey'],
    "lat": config['openweatherapi']['latitude'],
    "lon": config['openweatherapi']['longitude'],
    "units": config['openweatherapi']['units']
}

# Compile database query templates
weatherTemplate = """
    INSERT INTO weather
    (timestamp, weather_id, temp, temp_high, temp_low, humidity, wind_speed, wind_dir, pressure, precipitation)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
aqTemplate = """
    INSERT INTO air
    (timestamp, aqi, pm2_5, pm10, co, no2, o3, so2)
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
"""
precipTemplate = """
    INSERT INTO precipitation (
    (timestamp, weather_id, volume, volume_3h)
    VALUES
    (%s, %s, %s, %s)
"""

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
        exit(1)
    else:
        print("Done.\n")

    # Sort through data
    timestamp = "'" + datetime.now(pytz.UTC).isoformat() + "'"
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

    # Tupilize (is that even a word?) data to send to database
    weatherQuery = (
        timestamp,
        weatherID,
        envData["temp"],
        envData["temp_max"],
        envData["temp_min"],
        envData["humidity"],
        windData["speed"],
        windData["deg"],
        envData["pressure"],
        PRECIP
    )
    aqQuery = (
        timestamp,
        aqi,
        airData["pm2_5"],
        airData["pm10"],
        airData["co"],
        airData["no2"],
        airData["o3"],
        airData["so2"]
    )
    # Check precip data and tupilize if necessary
    if PRECIP is True:
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

        precipQuery = (
            timestamp,
            weatherID,
            H1PRECIP,
            H3PRECIP
        )

    # Initiate database connection
    conn, db = db_connect()

    # Execute database commands
    db.execute(weatherTemplate, weatherQuery)
    db.execute(aqTemplate, aqQuery)
    if PRECIP is True:
        print("Precipitation data will be included.\n")
        db.execute(precipTemplate, precipQuery)

    # Commit changes to database and wait
    conn.commit()
    conn.close()
    print("Data stored. Timestamp: " + timestamp + "\n")
    time.sleep(config['program']['waittimer'])
