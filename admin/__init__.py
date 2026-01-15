# admin/__init__.py - ALTERNATIVE VERSION
from flask import Blueprint

# Create blueprint
admin_bp = Blueprint('admin', __name__, 
                     template_folder='templates/admin',
                     static_folder='static/admin',
                     url_prefix='/admin')

# Manually import and register routes
def register_routes():
    from . import routes
    
    # Explicitly register each route (for debugging)
    routes_to_check = [
        ('/', 'dashboard'),
        ('/login', 'login'),
        ('/logout', 'logout'),
        ('/posts', 'posts'),
        ('/posts/new', 'new_post'),
    ]
    
    print("Registering admin routes...")
    for path, endpoint in routes_to_check:
        print(f"  {path} -> {endpoint}")

# Call register_routes when module is imported
register_routes()

# Import routes at the end
from . import routes