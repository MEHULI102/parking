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

class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User_Info.id), nullable=False)

class ParkingLot(db.Model):
    __tablename__ = "parking_lot"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))

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

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey(User_Info.id), nullable=True)
    lot_id = db.Column(db.Integer, db.ForeignKey(ParkingLot.id), nullable=True)
