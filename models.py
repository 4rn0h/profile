# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import math
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    project_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Project {self.title}>'

# NEW: User model for admin authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=True)  # All users are admins in this setup
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Password handling methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(100))
    tags = db.Column(db.String(300))
    
    # NEW FIELDS for admin features
    is_published = db.Column(db.Boolean, default=True, nullable=False)  # Show/hide posts
    excerpt = db.Column(db.Text)  # Custom excerpt/summary
    meta_description = db.Column(db.String(300))  # For SEO
    cover_image = db.Column(db.String(200))  # URL for cover image
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)  # Auto-update on edit
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Link to user
    author = db.relationship('User', backref='posts')  # Relationship to author
    
    # Property to get formatted update date (if updated)
    @property
    def last_updated(self):
        return self.updated_at or self.date_posted
    
    @property
    def read_time(self) -> str:
        """
        Estimate read time based on word count (200 words per minute).
        Returns formatted string like "5 min read"
        """
        if not self.content:
            return "1 min read"
        
        words = len(self.content.split())
        minutes = max(1, math.ceil(words / 200))
        return f"{minutes} min read"
    
    # NEW: Property to get formatted tags as list
    @property
    def tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    # NEW: Property to check if post has been updated
    @property
    def was_updated(self):
        return self.updated_at is not None
    
    # NEW: Method to generate slug from title
    @classmethod
    def generate_slug(cls, title):
        """Generate URL-friendly slug from title"""
        import re
        from unicodedata import normalize
        
        # Normalize unicode characters
        slug = normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return slug
    
    # NEW: Method to update slug from title
    def update_slug(self):
        """Update slug based on current title"""
        base_slug = self.generate_slug(self.title)
        slug = base_slug
        counter = 1
        
        # Check if slug already exists (excluding current post)
        while True:
            existing = BlogPost.query.filter(
                BlogPost.slug == slug,
                BlogPost.id != self.id
            ).first()
            if not existing:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        self.slug = slug
    
    # NEW: Method to save as markdown file
    def save_as_markdown(self, directory='static/blog'):
        """Save blog post as markdown file"""
        import os
        import html2text
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Convert HTML to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # No line wrapping
        
        # Get markdown content (add title as header)
        markdown_content = f"# {self.title}\n\n"
        markdown_content += h.handle(self.content)
        
        # Save to file
        filename = f"{self.slug}.md"
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def __repr__(self):
        status = "Published" if self.is_published else "Draft"
        return f'<BlogPost "{self.title}" ({status})>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)  # NEW: Comment moderation
    post = db.relationship('BlogPost', backref=db.backref('comments', lazy=True))
    
    def __repr__(self):
        return f'<Comment by {self.author}>'

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)  # NEW: Mark as read/unread
    responded = db.Column(db.Boolean, default=False)  # NEW: Track if responded
    
    def __repr__(self):
        return f'<ContactMessage from {self.name}>'

class CVDownload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(80))
    downloaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CVDownload {self.email}>'

# NEW: Activity log for admin dashboard
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # e.g., 'create_post', 'edit_post'
    details = db.Column(db.Text)  # JSON or text details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')
    
    def __repr__(self):
        return f'<ActivityLog {self.action} by User {self.user_id}>'