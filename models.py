#from app import db
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    organization = db.Column(db.String(100))
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    
    # Profile fields
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)
    linkedin = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    
    # Status and role
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_admin = db.Column(db.Boolean, default=False)
    is_dignitary = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    themes = db.relationship('Theme', backref='user', lazy=True, cascade='all, delete-orphan')
    connections = db.relationship('Connection', foreign_keys='Connection.user_id', 
                                  backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_registration_number():
        """Generate unique registration number like SAMP2024001"""
        year = datetime.now().year
        count = User.query.count() + 1
        return f"SAMP{year}{count:04d}"
    
    def to_dict(self, include_themes=False):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'organization': self.organization,
            'registration_number': self.registration_number,
            'bio': self.bio,
            'interests': self.interests,
            'linkedin': self.linkedin,
            'twitter': self.twitter,
            'status': self.status,
            'is_admin': self.is_admin,
            'is_dignitary': self.is_dignitary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_themes:
            data['themes'] = [theme.name for theme in self.themes]
        
        return data


class Theme(db.Model):
    __tablename__ = 'themes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }


class Connection(db.Model):
    __tablename__ = 'connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    connected_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional: metadata about the connection
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'connected_user_id': self.connected_user_id,
            'connected_at': self.connected_at.isoformat()
        }