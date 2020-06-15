# Import all libraries and dependencies
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Database Setup
#################################################

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)


#################################################
# Flask Routes
#################################################

# Setup homepage route
@app.route("/")
def home():
    # List all the routes
    return (
        "Welcome to my home page!"
        f"<br/><br/><br/>"
        "Please see the available api routes:"
        f"<br/><br/>"
        "/api/v1.0/precipitation"
        f"<br/>"
        "/api/v1.0/stations"
        f"<br/>"
        "/api/v1.0/tobs"
        f"<br/>"
        "/api/v1.0/start"
        f"<br/>"
        "/api/v1.0/start/end"
        f"<br/>"
    )


# Setup precipitation page route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results to a dictionary using date as the key and prcp as the value
    # Calculate the date 1 year ago from the last data point in the database
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores, order by date
    data_prec = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>year_ago, Measurement.prcp!=None).\
        order_by(Measurement.date).all()

    # Return the query as a dictionary in json
    return jsonify(dict(data_prec))


# Setup stations page route
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    active_station_list = session.query(Station.station, Station.name).all()
    return jsonify(dict(active_station_list))


# Setup tobs page route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.
    active_station_list = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    active_station = active_station_list[0][0]

    # Using the station id from the previous query, calculate the lowest temperature recorded, 
    # highest temperature recorded, and average temperature of the most active station?
    id_temp = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date>year_ago).filter(Measurement.station==active_station).all()

    return jsonify(dict(id_temp))


# Setup start date page route
@app.route(f"/api/v1.0/<start>")
def user_control_start(start):
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    # start_date = dt.date.strftime(start, "%y-%m-%d")
    temp_ob = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temp_ob_list = list(np.ravel(temp_ob))
    temp_ob_dict={"Min Temp": temp_ob_list[0], "Avg Temp": temp_ob_list[1], "Max Temp": temp_ob_list[2]}

    return jsonify(temp_ob_dict)

# Setup start and end date page route
@app.route(f"/api/v1.0/<start>/<end>")
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start, end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    temp_ob2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temp_ob_list2 = list(np.ravel(temp_ob2))
    temp_ob_dict2={"Min Temp": temp_ob_list2[0], "Avg Temp": temp_ob_list2[1], "Max Temp": temp_ob_list2[2]}

    return jsonify(temp_ob_dict2)


if __name__=="__main__":
    app.run(debug=True)