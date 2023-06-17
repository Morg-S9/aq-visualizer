# AcQuire
AcQuire is a three part project I'm working on that takes weather data from OpenWeatherMap's API and stores it for later use in a way that I'm not entirely set on yet.

### Project Goal
In the end, I want this project to bring awareness to major environmental issues, like climate change and air pollution. Currently, I will be collecting data with this project and then hopefully using the data it collects to educate and motivate people to make changes and take action against these issues for a better tomorrow.

## Programs
### `collect.py`
It does what it sounds like! It collects weather data! I chose to make it very modifiable, being able to change the timeout between requests, and the lat/long coordinates it gets data from. It takes all of this and stores it in a PostgreSQL database in table formats that I provided. 

### `app.py`
This is one of the many ways I wish to use this info to help others.
This is a very basic RESTful API written with Flask that allows you to recieve the collected data from the PSQL database.
This is still very work in progress, and is in it's very basic stages.

## Dependent Programs
### [PostgreSQL](https://postgresql.org)
The majority of this project revolves around PostgreSQL. Their work on making their software very easy to learn and interact with has been immensely helpful for me working on this project. Thanks guys!

### [Psycopg2](https://www.psycopg.org)
Of course, I needed a way to actually interface my program with my database, and psycpog2 has been great for me.

### [Flask](https://flask.palletsprojects.com)
Flask is the framework I used to write the RESTful API for this project. Props to them.
