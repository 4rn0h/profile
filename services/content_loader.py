from models import Project, BlogPost

def get_featured_projects():
    return Project.query.order_by(Project.id.desc()).limit(3).all()

def get_all_projects():
    return Project.query.order_by(Project.id.desc()).all()

def get_recent_blog_posts():
    return BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(3).all()

def get_all_blog_posts():
    return BlogPost.query.order_by(BlogPost.date_posted.desc()).all()