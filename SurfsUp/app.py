# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
# Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#Convert the query results from your precipitation analysis 
#(i.e. retrieve only the last 12 months of data) 
#to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation (prcp)and date (date) data"""
    prcp_query = session.query(measurement.prcp, measurement.date).all()

    #Create a dictionary from the row data
    prcp_values = []
    for prcp, date in prcp_query:
        prcp_dict = {}
        prcp_dict["precipitation"] = prcp
        prcp_dict["date"] = date
        prcp_values.append(prcp_dict)

    #Return JSON of dictionary
    return jsonify(prcp_values)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations from the dataset"""
    stations_query = session.query(station.station,station.id).all()

    stations_values = []
    for station, id in stations_query:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['id'] = id
        stations_values.append(stations_dict)

    #Return JSON
    return jsonify (stations_values) 

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of dates and temps observed for the most active station for the last year of data from the database"""
    tobs_query = session.query(measurement.date,  measurement.tobs,measurement.prcp).\
                filter(measurement.date >= '2016-08-23').\
                filter(measurement.station=='USC00519281').\
                order_by(measurement.date).all()

    all_tobs = []
    for prcp, date,tobs in tobs_query:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#Create start and start/end route
#Find min, average, and max temps for a given date range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temps(start=None, end=None):
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    # Check if there is an end date then do the task accordingly
    if end == None: 
        start_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                            filter(measurement.date >= start).all()
        
        # Convert list of tuples into normal list
        start_list = list(np.ravel(start_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start date
        return jsonify(start_list)
    
    else:
        # Query the data from start date to the end date
        start_end_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                            filter(measurement.date >= start).\
                            filter(measurement.date <= end).all()
        
        # Convert list of tuples into normal list
        start_end_list = list(np.ravel(start_end_data))

        # Return a list of jsonified minimum, average and maximum temperatures for a specific start-end date range
        return jsonify(start_end_list)

session.close()