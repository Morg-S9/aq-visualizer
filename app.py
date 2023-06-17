# pylint: disable=redefined-outer-name, invalid-name, line-too-long


"""
AcQuire Database API
This is a work in progress, pardon my spaghetti code.
"""

import sys
import datetime as dt
import pytz
import simplejson as json
import psycopg2
from flask import Flask, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

with open('config.json', 'r', encoding="utf-8") as f:
    config = json.load(f)

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[str(config["program"]["apilimit"]) + " per minute"],
    storage_uri="memory://"  # Change this to something more reliable
)


def db_connect():
    """Simplifies database connection flow"""
    conn = psycopg2.connect(database=config['database']['name'],
                            host=config['database']['host'],
                            user=config['database']['logins']['api']['username'],
                            password=config['database']['logins']['api']['password'],
                            port=config['database']['port'])
    database = conn.cursor()
    return conn, database


# Grabs PSQL version, and also acts as a connection test, making sure everything works properly.
try:
    conn, database = db_connect()
    database.execute('SELECT version();')
    pql_ver = str(database.fetchone()[0])
    database.close()
    conn.close()
    del database, conn
except psycopg2.Error as e:
    print("An error occurred on connection with the database. Check your config.json for proper credentials and try again.\n" + str(e))
    exit(1)


@app.errorhandler(429)
@limiter.exempt
def rate_limit(e): # pylint: disable=unused-argument
    response = {
        "error": "Too Many Requests",
        "msg": "API Rate Limit exceeded. Please try again later.",
        "code": 429
    }
    return Response(json.dumps(response), mimetype='application/json'), 429


@app.errorhandler(psycopg2.Error)
@limiter.exempt
def psycopg2_handler(e):
    match str(e.pgcode):
        case '22007':
            response = {
                "error": "Bad Request",
                "msg": "An invalid date format was provided. Please try again.",
                "code": 400
            }
            return Response(json.dumps(response), mimetype='application/json'), 400
        case _:
            response = {
                "error": "Internal Server Error",
                "msg": "An unexpected error occurred. Please open an issue on GitHub containing this JSON Response, and the request you made to generate it.",
                "exception": str(e),
                "pqlcode": str(e.pgcode),
                "py_version": sys.version,
                "pg2_version": psycopg2.__version__,
                "pql_version": str(pql_ver),
                "code": 500,
                "github": "https://github.com/Morg-S9/aq-visualizer/issues/new/choose"
            }
            print("Unhandled Error Occurred.\nError: " + str(e))

            return Response(json.dumps(response), mimetype='application/json'), 500


@app.route('/ping')
@app.route('/ping/')
def ping():
    return "Pong!"


@app.route('/weather')
@app.route('/weather/')
def weather():
    """
    Endpoint: /weather/
    Parameters:
        "date": ISO Standard Date in UTC (Default: Current Date)
    Description:
        Returns Weather data on a provided date, or if none provided, the current date.
    """
    conn, database = db_connect()
    try:
        query = "SELECT * FROM weather WHERE timestamp::date = %s"
        date = (request.args.get('date', dt.datetime.now(pytz.UTC).date()),)
        data_list = []
        database.execute(query, date)
        db_response = database.fetchall()
        for i in db_response:
            if i[9] is True:
                query = "SELECT * FROM precipitation WHERE timestamp::date = %s"
                database.execute(query, (i[0].isoformat(),))
                db_response2 = database.fetchone()
                precip_data = {
                    "volume_1h": db_response2[2],
                    "volume_3h": db_response2[3]
                }
            else:
                precip_data = False
            data = {
                "timestamp": i[0].isoformat(),
                "data": {
                    "weather_id": i[1],
                    "humidity": i[5],
                    "pressure": i[8],
                    "temperature": {
                        "current": i[2],
                        "high": i[3],
                        "low": i[4]
                    },
                    "wind": {
                        "speed": i[6],
                        "direction": i[7]
                    },
                    "precip": precip_data
                }
            }
            data_list.append(data)
        if len(data_list) == 0:
            response = {
                "error": "Not Found",
                "message": "There is no data available for the date provided. Please try again.",
                "code": 404
            }
            return Response(json.dumps(response), mimetype='application/json'), 404
        return Response(json.dumps(data_list), mimetype='application/json')
    finally:
        database.close()
        conn.close()


@app.route('/airquality')
@app.route('/airquality/')
def airquality():
    """
    Endpoint: /airquality/
    Parameters:
        "date": ISO Standard Date in UTC (Default: Current Date)
    Description:
        Returns Air quality data on a provided date, or if none provided, the current date.
    """
    conn, database = db_connect()
    try:
        query = "SELECT * FROM air WHERE timestamp::date = %s"
        date = (request.args.get('date', dt.datetime.now(pytz.UTC).date()),)
        data_list = []
        database.execute(query, date)
        db_response = database.fetchall()
        for i in db_response:
            data = {
                "timestamp": i[0].isoformat(),
                "data": {
                    "aqi": i[1],
                    "pm2_5": i[2],
                    "pm10": i[3],
                    "co": i[4],
                    "no2": i[5],
                    "o3": i[6],
                    "so2": i[7]
                }
            }
            data_list.append(data)
        return Response(json.dumps(data_list), mimetype='application/json')
    finally:
        database.close()
        conn.close()


if __name__ == '__main__':
    app.run()
