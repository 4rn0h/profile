# check_admin.py
from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f"✅ Admin user exists:")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Created: {admin.created_at}")
    else:
        print("❌ No admin user found")