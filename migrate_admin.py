# migrate_admin.py
from app import create_app
from models import db, User, BlogPost
from datetime import datetime
import os

def migrate_database():
    app = create_app()
    
    with app.app_context():
        print("🚀 Starting database migration...")
        
        try:
            # Check current schema
            result = db.session.execute("PRAGMA table_info(blog_post)").fetchall()
            existing_columns = [row[1] for row in result]
            print(f"📋 Existing columns: {existing_columns}")
            
            # Columns to add
            columns_to_add = [
                ('is_published', 'BOOLEAN DEFAULT 1'),
                ('excerpt', 'TEXT'),
                ('meta_description', 'VARCHAR(300)'),
                ('cover_image', 'VARCHAR(200)'),
                ('updated_at', 'DATETIME'),
                ('author_id', 'INTEGER')
            ]
            
            # Add missing columns
            for column, data_type in columns_to_add:
                if column not in existing_columns:
                    try:
                        db.session.execute(f'ALTER TABLE blog_post ADD COLUMN {column} {data_type}')
                        print(f"✅ Added column: {column}")
                    except Exception as e:
                        print(f"⚠️ Could not add {column}: {e}")
            
            # Check if user table exists
            try:
                db.session.execute("SELECT 1 FROM user LIMIT 1")
                print("✅ User table exists")
            except:
                # Create user table
                db.session.execute('''
                    CREATE TABLE user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(64) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(256),
                        is_active BOOLEAN DEFAULT 1,
                        is_admin BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME
                    )
                ''')
                print("✅ Created user table")
                
                # Create admin user
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
                print("✅ Created admin user (admin/admin123)")
            
            # Create activity_log table if it doesn't exist
            try:
                db.session.execute("SELECT 1 FROM activity_log LIMIT 1")
                print("✅ Activity log table exists")
            except:
                db.session.execute('''
                    CREATE TABLE activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action VARCHAR(100) NOT NULL,
                        details TEXT,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user (id)
                    )
                ''')
                print("✅ Created activity_log table")
            
            db.session.commit()
            print("🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate_database()