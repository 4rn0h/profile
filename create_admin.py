# create_admin.py
from app import create_app
from models import db, User
from datetime import datetime

app = create_app()

with app.app_context():
    try:
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Admin already exists: {admin.username}")
        else:
            # Create admin
            from werkzeug.security import generate_password_hash
            
            admin = User(
                username='admin',
                email='admin@example.com',
                is_active=True,
                is_admin=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   ⚠️ Change password in production!")
    except Exception as e:
        print(f"Error: {e}")