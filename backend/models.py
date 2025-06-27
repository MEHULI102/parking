from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ===================== USER INFO =====================
class User_Info(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True)
    pwd = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(10))
    role = db.Column(db.Integer, default=1)

    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'user_name': self.user_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'pincode': self.pincode,
            'role': self.role
        }

# ===================== PARKING LOT =====================
class ParkingLot(db.Model):
    __tablename__ = "parking_lot"
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(10))
    price_per_hour = db.Column(db.Float, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(255))

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)  # relationship to ParkingSpot

    @property
    def available_spots(self):
        return ParkingSpot.query.filter_by(lot_id=self.id, status='A').count()
 

    def to_dict(self):
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'name': self.name,
            'address': self.address,
            'pincode': self.pincode,
            'price_per_hour': self.price_per_hour,
            'total_spots': self.total_spots,
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'location': self.location,
            'available_spots': self.available_spots
        }

# ===================== PARKING SPOT =====================
class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A')

    reservations = db.relationship('Reservation', backref='spot', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'status': self.status
        }
    
    

# ===================== RESERVATION =====================
class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    vehicle_no = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_no': self.vehicle_no,
            'parking_timestamp': self.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'leaving_timestamp': self.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.leaving_timestamp else None,
            'cost': self.cost
        }
    @property
    def lot(self):
        return self.spot.lot if self.spot else None
