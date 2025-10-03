# migrate_md_to_db.py
from app import create_app
from models import db, BlogPost
import os
from datetime import datetime
import markdown

def estimate_read_time(content):
    """Estimate read time based on word count"""
    words_per_minute = 200
    word_count = len(content.split())
    read_time = max(1, round(word_count / words_per_minute))
    return f"{read_time} min read"

def get_category_from_filename(filename):
    """Extract category from filename"""
    category_map = {
        'etl-pipeline': 'Data Engineering',
        'flask-api': 'Backend Development', 
        'jenkins-devops': 'DevOps'
    }
    
    base_name = filename.replace('.md', '')
    return category_map.get(base_name, 'General')

def get_tags_from_filename(filename):
    """Extract tags based on filename"""
    tags_map = {
        'etl-pipeline': 'Python, ETL, Data Pipelines, Apache Airflow',
        'flask-api': 'Python, Flask, REST API, Backend',
        'jenkins-devops': 'Jenkins, CI/CD, DevOps, Automation'
    }
    
    base_name = filename.replace('.md', '')
    return tags_map.get(base_name, 'General')

def convert_markdown_to_html(content):
    """Convert markdown content to HTML"""
    try:
        return markdown.markdown(content)
    except:
        return f"<pre>{content}</pre>"

app = create_app()

with app.app_context():
    try:
        # Clear existing blog posts to avoid duplicates
        BlogPost.query.delete()
        print("Cleared existing blog posts")
        
        blog_dir = 'static/blog'
        migrated_count = 0
        
        for filename in os.listdir(blog_dir):
            if filename.endswith('.md'):
                path = os.path.join(blog_dir, filename)
                print(f"Processing: {filename}")
                
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract title from first line
                    first_line = content.split('\n')[0]
                    title = first_line.replace('# ', '').strip()
                    slug = filename.replace('.md', '')
                    
                    # Convert markdown to HTML
                    html_content = convert_markdown_to_html(content)
                    
                    # Create blog post with all required fields
                    post = BlogPost(
                        title=title, 
                        slug=slug, 
                        content=html_content, 
                        date_posted=datetime.utcnow(),
                        read_time=estimate_read_time(content),
                        category=get_category_from_filename(filename),
                        tags=get_tags_from_filename(filename)
                    )
                    
                    db.session.add(post)
                    migrated_count += 1
                    print(f"✅ Migrated: {title}")
                    
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")
                    continue

        # Commit all changes
        db.session.commit()
        print(f"✅ Successfully migrated {migrated_count} blog posts to the database.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.session.rollback()