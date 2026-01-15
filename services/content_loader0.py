# migrate_admin.py - FIXED VERSION
from app import create_app
from models import db, User, BlogPost
from datetime import datetime
import os
from sqlalchemy import text  # ADD THIS IMPORT

def migrate_database():
    app = create_app()
    
    with app.app_context():
        print("🚀 Starting database migration...")
        
        try:
            # Check current schema - USE text() function
            result = db.session.execute(text("PRAGMA table_info(blog_post)")).fetchall()
            existing_columns = [row[1] for row in result]
            print(f"📋 Existing columns in blog_post: {existing_columns}")
            
            # Columns to add
            columns_to_add = [
                ('is_published', 'BOOLEAN DEFAULT 1'),
                ('excerpt', 'TEXT'),
                ('meta_description', 'VARCHAR(300)'),
                ('cover_image', 'VARCHAR(200)'),
                ('updated_at', 'DATETIME'),
                ('author_id', 'INTEGER')
            ]
            
            # Add missing columns - USE text() for SQL
            for column, data_type in columns_to_add:
                if column not in existing_columns:
                    try:
                        db.session.execute(text(f'ALTER TABLE blog_post ADD COLUMN {column} {data_type}'))
                        print(f"✅ Added column: {column}")
                    except Exception as e:
                        print(f"⚠️ Could not add {column}: {e}")
            
            # Check if user table exists
            try:
                db.session.execute(text("SELECT 1 FROM user LIMIT 1"))
                print("✅ User table exists")
                user_table_exists = True
            except Exception as e:
                print(f"❌ User table doesn't exist: {e}")
                user_table_exists = False
            
            if not user_table_exists:
                # Create user table
                db.session.execute(text('''
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
                '''))
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
            
            # Check if activity_log table exists
            try:
                db.session.execute(text("SELECT 1 FROM activity_log LIMIT 1"))
                print("✅ Activity log table exists")
            except:
                db.session.execute(text('''
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
                '''))
                print("✅ Created activity_log table")
            
            # Also update Comment table with is_approved column
            try:
                result = db.session.execute(text("PRAGMA table_info(comment)")).fetchall()
                comment_columns = [row[1] for row in result]
                print(f"📋 Existing columns in comment: {comment_columns}")
                
                if 'is_approved' not in comment_columns:
                    db.session.execute(text('ALTER TABLE comment ADD COLUMN is_approved BOOLEAN DEFAULT 1'))
                    print("✅ Added is_approved column to comment table")
            except Exception as e:
                print(f"⚠️ Could not check/update comment table: {e}")
            
            # Also update ContactMessage table with new columns
            try:
                result = db.session.execute(text("PRAGMA table_info(contact_message)")).fetchall()
                contact_columns = [row[1] for row in result]
                print(f"📋 Existing columns in contact_message: {contact_columns}")
                
                columns_to_add_contact = [
                    ('is_read', 'BOOLEAN DEFAULT 0'),
                    ('responded', 'BOOLEAN DEFAULT 0')
                ]
                
                for column, data_type in columns_to_add_contact:
                    if column not in contact_columns:
                        db.session.execute(text(f'ALTER TABLE contact_message ADD COLUMN {column} {data_type}'))
                        print(f"✅ Added {column} column to contact_message table")
            except Exception as e:
                print(f"⚠️ Could not check/update contact_message table: {e}")
            
            db.session.commit()
            print("🎉 Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    migrate_database()