from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from datetime import datetime
from auth import generate_token, verify_token, generate_credentials
from email_service import send_credentials_email
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:5174", 
            "https://sampark-frontend-beta.vercel.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

from models import db  # import the unbound db
db.init_app(app)       # bind it to the Flask app
migrate = Migrate(app, db)


# Import models after db initialization
from models import User, Connection, Theme

# ==================== REGISTRATION ROUTES ====================

@app.route('/api/register', methods=['POST'])
def register_user():
    """Receive registration data (from Google Form webhook or direct)"""
    data = request.json
    
    try:
        # Create new user with pending status
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            organization=data.get('organization'),
            registration_number=User.generate_registration_number(),
            status='pending'
        )
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration submitted successfully',
            'registration_number': user.registration_number
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/admin/pending-registrations', methods=['GET', 'OPTIONS'])
def get_pending_registrations():
    """Admin: Get all pending registrations"""
    
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data or not user_data.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        pending_users = User.query.filter_by(status='pending').all()
        print(f"✅ Found {len(pending_users)} pending users")
        return jsonify([user.to_dict() for user in pending_users]), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/approve/<int:user_id>', methods=['POST'])
def approve_registration(user_id):
    """Admin: Approve a registration and send credentials"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data or not user_data.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate credentials
    password = generate_credentials()
    user.set_password(password)
    user.status = 'approved'
    db.session.commit()
    
    # Send email with credentials
    try:
        send_credentials_email(user.email, user.registration_number, password)
        print("Email sent successfully")
    except Exception as e:
        print("EMAIL ERROR:", e)

    
    return jsonify({'message': 'User approved and credentials sent'}), 200

@app.route('/api/admin/reject/<int:user_id>', methods=['POST', 'OPTIONS'])
def reject_registration(user_id):
    """Admin: Reject a registration"""
    
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data or not user_data.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update status to rejected
    user.status = 'rejected'
    db.session.commit()
    
    return jsonify({'message': 'User registration rejected'}), 200

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/login', methods=['POST'])
def login():
    """User login with registration number and password"""
    data = request.json
    reg_number = data.get('registration_number')
    password = data.get('password')
    
    user = User.query.filter_by(registration_number=reg_number).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if user.status != 'approved':
        return jsonify({'error': 'Account not approved yet'}), 403
    
    token = generate_token(user.id, user.is_admin)
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 200

# ==================== USER PROFILE ROUTES ====================

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get current user's profile"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_data['user_id'])
    return jsonify(user.to_dict(include_themes=True)), 200

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_data['user_id'])
    data = request.json
    
    # Update basic fields
    user.bio = data.get('bio', user.bio)
    user.interests = data.get('interests', user.interests)
    user.linkedin = data.get('linkedin', user.linkedin)
    user.twitter = data.get('twitter', user.twitter)
    
    # Update themes
    if 'themes' in data:
        # Remove old themes
        Theme.query.filter_by(user_id=user.id).delete()
        # Add new themes
        for theme_name in data['themes']:
            theme = Theme(user_id=user.id, name=theme_name)
            db.session.add(theme)
    
    db.session.commit()
    return jsonify(user.to_dict(include_themes=True)), 200

# ==================== NFC/SCAN ROUTES ====================

@app.route('/api/scan/<registration_number>', methods=['GET'])
def scan_profile(registration_number):
    """Get user profile by registration number (NFC scan)"""
    user = User.query.filter_by(registration_number=registration_number).first()
    
    if not user or user.status != 'approved':
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict(include_themes=True)), 200

@app.route('/api/connect', methods=['POST'])
def create_connection():
    """Create a connection between two users"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    scanned_reg_number = data.get('scanned_registration_number')
    
    scanned_user = User.query.filter_by(registration_number=scanned_reg_number).first()
    if not scanned_user:
        return jsonify({'error': 'Scanned user not found'}), 404
    
    # Check if connection already exists
    existing = Connection.query.filter(
        ((Connection.user_id == user_data['user_id']) & (Connection.connected_user_id == scanned_user.id)) |
        ((Connection.user_id == scanned_user.id) & (Connection.connected_user_id == user_data['user_id']))
    ).first()
    
    if existing:
        return jsonify({'message': 'Connection already exists'}), 200
    
    # Create bidirectional connection
    connection1 = Connection(user_id=user_data['user_id'], connected_user_id=scanned_user.id)
    connection2 = Connection(user_id=scanned_user.id, connected_user_id=user_data['user_id'])
    
    db.session.add(connection1)
    db.session.add(connection2)
    db.session.commit()
    
    return jsonify({'message': 'Connection created successfully'}), 201

@app.route('/api/connections', methods=['GET'])
def get_connections():
    """Get all connections for current user"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'error': 'Unauthorized'}), 401
    
    connections = Connection.query.filter_by(user_id=user_data['user_id']).all()
    
    result = []
    for conn in connections:
        connected_user = User.query.get(conn.connected_user_id)
        result.append({
            'id': conn.id,
            'connected_at': conn.connected_at.isoformat(),
            'user': connected_user.to_dict()
        })
    
    return jsonify(result), 200

# ==================== ANALYTICS ROUTES ====================

@app.route('/api/analytics/themes', methods=['GET'])
def get_theme_participants():
    """Get all participants grouped by themes"""
    theme_name = request.args.get('theme')
    
    if theme_name:
        themes = Theme.query.filter_by(name=theme_name).all()
        users = [User.query.get(t.user_id).to_dict() for t in themes]
        return jsonify({'theme': theme_name, 'participants': users}), 200
    
    # Get all themes with count
    themes_count = db.session.query(Theme.name, db.func.count(Theme.user_id)).group_by(Theme.name).all()
    result = [{'name': name, 'count': count} for name, count in themes_count]
    
    return jsonify(result), 200

@app.route('/api/analytics/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_data['user_id'])
    connection_count = Connection.query.filter_by(user_id=user.id).count()
    
    return jsonify({
        'total_connections': connection_count,
        'registration_number': user.registration_number,
        'themes': [t.name for t in user.themes]
    }), 200

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Admin: Get all users"""
    token = request.headers.get('Authorization')
    user_data = verify_token(token)
    
    if not user_data or not user_data.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200




# ==================== RUN APP ====================



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
