# run_migration.py - STANDALONE MIGRATION SCRIPT
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_migration():
    # Create SQLAlchemy engine directly (not through Flask)
    db_path = os.path.join('instance', 'app.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🚀 Starting standalone migration...")
    
    try:
        # Check current schema
        result = session.execute(text("PRAGMA table_info(blog_post)")).fetchall()
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
        
        # Add missing columns
        for column, data_type in columns_to_add:
            if column not in existing_columns:
                try:
                    session.execute(text(f'ALTER TABLE blog_post ADD COLUMN {column} {data_type}'))
                    print(f"✅ Added column: {column}")
                except Exception as e:
                    print(f"⚠️ Could not add {column}: {e}")
        
        # Check if user table exists
        try:
            session.execute(text("SELECT 1 FROM user LIMIT 1"))
            print("✅ User table exists")
            user_table_exists = True
        except Exception:
            print("❌ User table doesn't exist")
            user_table_exists = False
        
        if not user_table_exists:
            # Create user table
            session.execute(text('''
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
            password_hash = generate_password_hash('admin123')
            session.execute(text(
                "INSERT INTO user (username, email, password_hash, is_active, is_admin, created_at) "
                "VALUES (:username, :email, :password_hash, :is_active, :is_admin, :created_at)"
            ), {
                'username': 'admin',
                'email': 'admin@example.com',
                'password_hash': password_hash,
                'is_active': True,
                'is_admin': True,
                'created_at': datetime.utcnow()
            })
            print("✅ Created admin user (admin/admin123)")
        
        # Check if activity_log table exists
        try:
            session.execute(text("SELECT 1 FROM activity_log LIMIT 1"))
            print("✅ Activity log table exists")
        except:
            session.execute(text('''
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
        
        session.commit()
        print("🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    run_migration()