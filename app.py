import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API! <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/start_date <br/>"
        f"/api/v1.0/start_date/end_date <br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    results = session.query(Measurement.prcp, Measurement.date).all()

    session.close()

    precipitation = []
    for prpc, date in results:
        temp = {}
        temp[date] = prpc
        precipitation.append(temp)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)
    
    results = session.query(distinct(Station.station)).all()

    session.close()
    
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()[0][0]

    latest_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    formated_latest_date = dt.datetime.strptime(latest_date,"%Y-%m-%d").date()

    year_ago = formated_latest_date - dt.timedelta(days=365)
    
    one_year_temperature = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.date <= formated_latest_date).\
                        filter(Measurement.date >= year_ago).\
                        filter(Measurement.station == most_active_station)

    session.close()
   
    all_temperatures = []
    for date, temperature in one_year_temperature:
        temp = {}
        temp["date"] = date
        temp["temperature"] = temperature
        all_temperatures.append(temp)

    return jsonify(all_temperatures)


@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    formated_date = dt.datetime.strptime(start,"%Y-%m-%d").date()

    normals = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= formated_date).all()

    session.close()

    all_temperatures = []
    for min, avg, max in normals:
        temp = {}
        temp["min"] = min
        temp["avg"] = avg
        temp["max"] = max
        all_temperatures.append(temp)

    return jsonify(all_temperatures)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    formated_start_date = dt.datetime.strptime(start,"%Y-%m-%d").date()
    formated_end_date = dt.datetime.strptime(end,"%Y-%m-%d").date()

    normals = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= formated_start_date).\
                filter(Measurement.date <= formated_end_date).all()


    session.close()

    all_temperatures = []
    for min, avg, max in normals:
        temp = {}
        temp["min"] = min
        temp["avg"] = avg
        temp["max"] = max
        all_temperatures.append(temp)

    return jsonify(all_temperatures)

if __name__ == "__main__":
    app.run(debug=True)
