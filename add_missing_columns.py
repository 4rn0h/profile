# add_missing_columns.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys

def add_missing_columns():
    # Create SQLAlchemy engine directly
    db_path = os.path.join('instance', 'app.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("🔧 Adding missing columns...")
    
    try:
        # Add is_approved to comment table
        try:
            result = session.execute(text("PRAGMA table_info(comment)")).fetchall()
            comment_columns = [row[1] for row in result]
            print(f"📋 Existing columns in comment: {comment_columns}")
            
            if 'is_approved' not in comment_columns:
                session.execute(text('ALTER TABLE comment ADD COLUMN is_approved BOOLEAN DEFAULT 1'))
                print("✅ Added is_approved column to comment table")
        except Exception as e:
            print(f"⚠️ Could not check/update comment table: {e}")
        
        # Add is_read and responded to contact_message table
        try:
            result = session.execute(text("PRAGMA table_info(contact_message)")).fetchall()
            contact_columns = [row[1] for row in result]
            print(f"📋 Existing columns in contact_message: {contact_columns}")
            
            columns_to_add = [
                ('is_read', 'BOOLEAN DEFAULT 0'),
                ('responded', 'BOOLEAN DEFAULT 0')
            ]
            
            for column, data_type in columns_to_add:
                if column not in contact_columns:
                    session.execute(text(f'ALTER TABLE contact_message ADD COLUMN {column} {data_type}'))
                    print(f"✅ Added {column} column to contact_message table")
        except Exception as e:
            print(f"⚠️ Could not check/update contact_message table: {e}")
        
        # Also check blog_post columns
        try:
            result = session.execute(text("PRAGMA table_info(blog_post)")).fetchall()
            blog_columns = [row[1] for row in result]
            print(f"📋 Existing columns in blog_post: {blog_columns}")
            
            # Check for any missing columns from the updated model
            expected_columns = ['is_published', 'excerpt', 'meta_description', 
                              'cover_image', 'updated_at', 'author_id']
            
            for column in expected_columns:
                if column not in blog_columns:
                    print(f"⚠️ Missing column in blog_post: {column}")
        except Exception as e:
            print(f"⚠️ Could not check blog_post table: {e}")
        
        session.commit()
        print("🎉 Missing columns added successfully!")
        
    except Exception as e:
        print(f"❌ Failed to add columns: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    add_missing_columns()