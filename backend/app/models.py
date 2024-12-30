from . import db
from datetime import datetime

# ✅ User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # EV Owner or Energy Provider

# ✅ Charging Station Model
class ChargingStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="available")
    pricing = db.Column(db.String(50), nullable=True)  # Ensure this field exists
    speed = db.Column(db.String(50), nullable=True)    # Ensure this field exists


# ✅ Slot Model (NEW)
class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('charging_station.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="available")
    
    station = db.relationship('ChargingStation', backref='slots')

# ✅ Charging Session Model
class ChargingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('charging_station.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="in_progress")

    user = db.relationship('User', backref='sessions')
    station = db.relationship('ChargingStation', backref='sessions')

# ✅ Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref='bookings')
    slot = db.relationship('Slot', backref='bookings')
