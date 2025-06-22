from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User_Info(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    pwd = db.Column(db.String(100))
    role = db.Column(db.Integer, default=1)  # 0=admin, 1=user

    reservations = db.relationship('Reservation', backref='user', lazy=True)


class ParkingLot(db.Model):
    __tablename__ = "parking_lot"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    price_per_hour = db.Column(db.Float, nullable=False)   
    total_spots = db.Column(db.Integer, nullable=False)    



class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')  # A=Available, O=Occupied

    reservations = db.relationship('Reservation', backref='spot', lazy=True)


class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float)


# Optional: Extra Card model if you're using it elsewhere
class Card(db.Model):
    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_dt = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_dt = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="active")
    color = db.Column(db.String(20), default="primary")
    icon = db.Column(db.String(100))
    priority = db.Column(db.Integer)
    link_url = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=True)
