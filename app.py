import simplejson as json
import psycopg2
from flask import Flask

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

with open('config.json', 'r', encoding="utf-8") as f:
    config = json.load(f)

def db_connect():
    conn = psycopg2.connect(database=config['database']['name'],
                        host=config['database']['host'],
                        user=config['database']['logins']['api']['username'],
                        password=config['database']['logins']['api']['password'],
                        port=config['database']['port'])
    db = conn.cursor()
    return conn, db

@app.route('/dbtest')
def dbtest():
    conn, db = db_connect()
    db.execute("SELECT version();")
    data = {
        "return": db.fetchone()[0]
    }
    conn.close()
    return data

@app.route('/weather/latest')
def get_latest():
    conn, db = db_connect()
    db.execute("SELECT * from weather;")
    db_response = db.fetchone()
    data = {
        "timestamp": str(db_response[0]),
        "data" : {
            "weather_id": db_response[1],
            "temp": {
                "cur": db_response[2],
                "high": db_response[3],
                "low": db_response[4]
            },
            "humidity": db_response[5],
            "wind": {
                "speed": db_response[6],
                "direction": db_response[7]
            },
            "pressure": db_response[8],
            "precipitation": db_response[9]
        }
    }
    conn.close()
    return json.dumps(data)