from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Links the trip to the user
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # This establishes a relationship so you can easily find all stops in a trip
    stops = db.relationship('Stop', backref='trip', lazy=True, cascade="all, delete-orphan")

class Stop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False) # Links the stop to a trip
    city_name = db.Column(db.String(100), nullable=False)
    arrival_date = db.Column(db.Date, nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    
    # Relationship to activities in this city
    activities = db.relationship('Activity', backref='stop', lazy=True, cascade="all, delete-orphan")

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stop.id'), nullable=False) # Links activity to a stop
    name = db.Column(db.String(150), nullable=False)
    cost = db.Column(db.Float, default=0.0)
    activity_date = db.Column(db.Date, nullable=False)