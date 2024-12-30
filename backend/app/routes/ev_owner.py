from flask import Blueprint, request, jsonify
from app.models import db, ChargingStation, Booking, Slot
from datetime import datetime
from app.services.payment_service import process_payment
from flask_jwt_extended import jwt_required, get_jwt_identity

ev_owner_bp = Blueprint('ev_owner', __name__)

# ✅ Find Nearby Energy Providers (Protected Endpoint)
@ev_owner_bp.route('/api/ev/find-providers', methods=['GET'])
@jwt_required()
def find_providers():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({"message": "Latitude and Longitude are required"}), 400
    
    try:
        providers = ChargingStation.query.all()
        response = [
            {"id": provider.id, "name": provider.name, "location": provider.location}
            for provider in providers
        ]
        return jsonify({"providers": response}), 200
    except Exception as e:
        return jsonify({"message": "Error fetching providers", "error": str(e)}), 500


# ✅ Filter Charging Stations
@ev_owner_bp.route('/api/ev/filter-stations', methods=['GET'])
@jwt_required()
def filter_stations():
    pricing = request.args.get('pricing')
    speed = request.args.get('speed')
    availability = request.args.get('availability')
    
    try:
        query = ChargingStation.query
        if pricing:
            query = query.filter_by(pricing=pricing)  # Correct attribute
        if speed:
            query = query.filter_by(speed=speed)      # Correct attribute
        if availability:
            query = query.filter_by(status=availability)
        
        stations = query.all()
        response = [
            {
                "id": station.id,
                "name": station.name,
                "pricing": station.pricing,
                "speed": station.speed,
                "status": station.status
            }
            for station in stations
        ]
        return jsonify({"stations": response}), 200
    except AttributeError as e:
        return jsonify({"message": "Invalid filter parameters", "error": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Error filtering stations", "error": str(e)}), 500



# ✅ Book Slot
@ev_owner_bp.route('/api/ev/book-slot', methods=['POST'])
@jwt_required()
def book_slot():
    data = request.get_json()
    slot_id = data.get('slot_id')
    payment_details = data.get('payment_details')
    
    if not slot_id or not payment_details:
        return jsonify({"message": "Slot ID and Payment Details are required"}), 400
    
    if 'amount' not in payment_details:
        return jsonify({"message": "Payment amount is required"}), 400
    
    try:
        payment_result = process_payment(payment_details)
        if payment_result['status'] != 'success':
            return jsonify({"message": "Payment failed"}), 400
        
        slot = Slot.query.get(slot_id)
        if not slot or slot.status != 'available':
            return jsonify({"message": "Slot not available"}), 400
        
        slot.status = 'occupied'
        booking = Booking(
            slot_id=slot.id,
            booking_time=datetime.utcnow(),
            amount=payment_details['amount']
        )
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({"message": "Booking Confirmed", "booking_id": booking.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error booking slot", "error": str(e)}), 500


# ✅ Charging History
@ev_owner_bp.route('/api/ev/history', methods=['GET'])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    try:
        history = Booking.query.filter_by(user_id=user_id).all()
        response = [
            {
                "booking_id": booking.id,
                "date": booking.booking_time.strftime('%Y-%m-%d'),
                "amount": booking.amount
            }
            for booking in history
        ]
        return jsonify({"history": response}), 200
    except Exception as e:
        return jsonify({"message": "Error fetching history", "error": str(e)}), 500
