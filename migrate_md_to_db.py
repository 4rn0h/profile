from app import create_app
from models import db, BlogPost
import os
from datetime import datetime

app = create_app()

with app.app_context():
    blog_dir = 'static/blog'
    for filename in os.listdir(blog_dir):
        if filename.endswith('.md'):
            path = os.path.join(blog_dir, filename)
            with open(path, 'r') as f:
                content = f.read()

            title = content.split('\n')[0].replace('# ', '').strip()
            slug = filename.replace('.md', '')
            post = BlogPost(title=title, slug=slug, content=content, date_posted=datetime.utcnow())
            db.session.add(post)

    db.session.commit()
    print("✅ Markdown blog posts migrated to the database.")
