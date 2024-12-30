from flask import Blueprint, request, jsonify
from app.models import db, ChargingStation, Slot

energy_provider_bp = Blueprint('energy_provider', __name__)

# ✅ Add Charging Station
@energy_provider_bp.route('/api/provider/add-station', methods=['POST'])
def add_station():
    data = request.get_json()
    station_name = data.get('station_name')
    location = data.get('location')
    station_type = data.get('station_type')
    
    if not station_name or not location or not station_type:
        return jsonify({"message": "Station Name, Location, and Type are required"}), 400
    
    new_station = ChargingStation(
        name=station_name,
        location=location,
        station_type=station_type,
        status="available"
    )
    db.session.add(new_station)
    db.session.commit()
    
    return jsonify({"message": "Charging Station Added Successfully"}), 201


# ✅ Manage Charging Slots
@energy_provider_bp.route('/api/provider/manage-slots', methods=['POST'])
def manage_slots():
    data = request.get_json()
    action = data.get('action')  # Add/Edit/Delete
    slot_details = data.get('slot_details')
    
    if action not in ['Add', 'Edit', 'Delete'] or not slot_details:
        return jsonify({"message": "Invalid action or missing slot details"}), 400
    
    if action == 'Add':
        new_slot = Slot(
            station_id=slot_details['station_id'],
            start_time=slot_details['start_time'],
            end_time=slot_details['end_time'],
            status="available"
        )
        db.session.add(new_slot)
        message = "Slot added successfully"
    
    elif action == 'Edit':
        slot = Slot.query.get(slot_details['slot_id'])
        if not slot:
            return jsonify({"message": "Slot not found"}), 404
        slot.start_time = slot_details['start_time']
        slot.end_time = slot_details['end_time']
        message = "Slot updated successfully"
    
    elif action == 'Delete':
        slot = Slot.query.get(slot_details['slot_id'])
        if not slot:
            return jsonify({"message": "Slot not found"}), 404
        db.session.delete(slot)
        message = "Slot deleted successfully"
    
    db.session.commit()
    return jsonify({"message": message}), 200


# ✅ Slot Availability
@energy_provider_bp.route('/api/provider/slot-availability', methods=['GET'])
def slot_availability():
    station_id = request.args.get('station_id')
    if not station_id:
        return jsonify({"message": "Station ID is required"}), 400
    
    slots = Slot.query.filter_by(station_id=station_id).all()
    slot_data = [
        {"slot_id": slot.id, "status": slot.status}
        for slot in slots
    ]
    return jsonify({"slots": slot_data}), 200


# ✅ Send Notification
from app.utils.notifications import send_notification

@energy_provider_bp.route('/api/provider/send-notification', methods=['POST'])
def send_notification_route():
    data = request.get_json()
    booking_id = data.get('booking_id')
    user_info = data.get('user_info')
    
    if not booking_id or not user_info:
        return jsonify({"message": "Booking ID and User Info are required"}), 400
    
    send_notification(user_info, f"Your slot booking with ID {booking_id} is confirmed!")
    return jsonify({"message": f"Notification sent for booking {booking_id}"}), 200
