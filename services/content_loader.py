from models import Project, BlogPost

def get_featured_projects(limit=3):
    return Project.query.limit(limit).all()

def get_all_projects():
    return Project.query.all()

def get_recent_blog_posts(limit=2):
    return BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(limit).all()

def get_all_blog_posts():
    return BlogPost.query.order_by(BlogPost.date_posted.desc()).all()

