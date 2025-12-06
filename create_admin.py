from app import app, db
from models import User

with app.app_context():
    db.create_all()  # ensures tables exist

    admin_email = 'admin@sampark.com'
    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        print("Admin already exists!")
    else:
        admin = User(
            name='Admin User',
            email=admin_email,
            phone='1234567890',
            organization='Sampark',
            registration_number='ADMIN001',
            status='approved',
            is_admin=True
        )
        admin.set_password('xd62oum3mt')
        db.session.add(admin)
        db.session.commit()
        print("Admin created! Login: ADMIN001 / xd62oum3mt")
    