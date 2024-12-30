from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, ChargingStation, ChargingSession
from datetime import datetime

routes_bp = Blueprint('routes', __name__)

# Get all Charging Stations
@routes_bp.route('/api/stations', methods=['GET'])
def get_stations():
    stations = ChargingStation.query.all()
    return jsonify([{"id": s.id, "name": s.name, "location": s.location, "status": s.status} for s in stations]), 200

# Create a Charging Station
@routes_bp.route('/api/stations', methods=['POST'])
@jwt_required()
def create_station():
    data = request.get_json()
    station = ChargingStation(
        name=data['name'],
        location=data['location'],
        capacity=data['capacity']
    )
    db.session.add(station)
    db.session.commit()
    return jsonify({"message": "Charging station created!"}), 201

# Start a Charging Session
@routes_bp.route('/api/sessions/start', methods=['POST'])
@jwt_required()
def start_session():
    data = request.get_json()
    user_id = get_jwt_identity()
    station = ChargingStation.query.get(data['station_id'])
    
    if not station or station.status != "available":
        return jsonify({"message": "Station not available!"}), 400
    
    station.status = "occupied"
    session = ChargingSession(
        user_id=user_id,
        station_id=station.id,
        start_time=datetime.utcnow()
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({"message": "Session started!"}), 201

# End a Charging Session
@routes_bp.route('/api/sessions/end/<int:session_id>', methods=['POST'])
@jwt_required()
def end_session(session_id):
    session = ChargingSession.query.get(session_id)
    if not session:
        return jsonify({"message": "Session not found!"}), 404
    
    session.end_time = datetime.utcnow()
    session.status = "completed"
    session.station.status = "available"
    db.session.commit()
    return jsonify({"message": "Session ended!"}), 200
