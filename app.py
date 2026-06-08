# app.py - UPDATED (remove imports from content_loader and add functions directly)
from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, abort
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import db, Project, BlogPost, Comment, ContactMessage, User, ActivityLog
from forms import ContactForm, CommentForm, LoginForm, BlogPostForm, SettingsForm
import markdown
from datetime import datetime
import os

load_dotenv()

# Initialize Login Manager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize db
    db.init_app(app)
    
    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ----------------------
    # Content Loader Functions (moved here)
    # ----------------------
    
    def get_blog_markdown_html(slug):
        """Load a markdown file and convert to HTML"""
        md_path = os.path.join('static', 'blog', f"{slug}.md")
        if os.path.exists(md_path):
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_text = f.read()
                html = markdown.markdown(md_text, extensions=['fenced_code', 'codehilite', 'tables', 'toc'])
                return html
            except Exception as e:
                print(f"Error reading markdown file {slug}.md: {e}")
        return None
    
    def html_to_excerpt(html_text, words=30):
        """Convert HTML to text excerpt"""
        import re
        import html as _html
        
        if not html_text:
            return ''
        
        # remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        # unescape HTML entities
        text = _html.unescape(text).strip()
        if not text:
            return ''
        
        parts = text.split()
        if len(parts) <= words:
            excerpt_text = ' '.join(parts)
        else:
            excerpt_text = ' '.join(parts[:words]) + '...'
        
        return f"<p>{excerpt_text}</p>"
    
    def get_featured_projects():
        """Get featured projects for homepage"""
        try:
            return Project.query.order_by(Project.id.desc()).limit(3).all()
        except Exception as e:
            print(f"Error loading featured projects: {e}")
            return []
    
    def get_all_projects():
        """Get all projects"""
        try:
            return Project.query.order_by(Project.id.desc()).all()
        except Exception as e:
            print(f"Error loading all projects: {e}")
            return []
    
    def get_recent_blog_posts():
        """Get recent blog posts for homepage - SAFE VERSION"""
        try:
            # First try the normal query
            posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(3).all()
            
            # If is_published column exists, filter out unpublished posts
            # Check if the column exists by trying to access it
            if posts:
                first_post = posts[0]
                if hasattr(first_post, 'is_published'):
                    posts = [p for p in posts if getattr(p, 'is_published', True)]
            
            return posts
        except Exception as e:
            print(f"Error loading recent blog posts: {e}")
            # If there's an error, try a simpler query without new columns
            try:
                # Use raw SQL to get basic columns only
                result = db.session.execute(
                    "SELECT id, title, content, slug, date_posted FROM blog_post ORDER BY date_posted DESC LIMIT 3"
                )
                posts = []
                for row in result:
                    post = BlogPost(
                        id=row[0],
                        title=row[1],
                        content=row[2],
                        slug=row[3],
                        date_posted=row[4]
                    )
                    posts.append(post)
                return posts
            except Exception as e2:
                print(f"Error with fallback query: {e2}")
                return []
    
    def get_all_blog_posts():
        """Get all blog posts - SAFE VERSION"""
        try:
            # First try the normal query
            posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
            
            # If is_published column exists, filter out unpublished posts
            if posts:
                first_post = posts[0]
                if hasattr(first_post, 'is_published'):
                    posts = [p for p in posts if getattr(p, 'is_published', True)]
            
            return posts
        except Exception as e:
            print(f"Error loading all blog posts: {e}")
            # If there's an error, try a simpler query without new columns
            try:
                # Use raw SQL to get basic columns only
                result = db.session.execute(
                    "SELECT id, title, content, slug, date_posted, category, tags FROM blog_post ORDER BY date_posted DESC"
                )
                posts = []
                for row in result:
                    post = BlogPost(
                        id=row[0],
                        title=row[1],
                        content=row[2],
                        slug=row[3],
                        date_posted=row[4]
                    )
                    # Add optional fields if they exist
                    if len(row) > 5:
                        post.category = row[5] if row[5] else None
                    if len(row) > 6:
                        post.tags = row[6] if row[6] else None
                    posts.append(post)
                return posts
            except Exception as e2:
                print(f"Error with fallback query: {e2}")
                return []

    # ----------------------
    # Helper Functions
    # ----------------------
    
    def create_default_admin():
        """Create default admin user if none exists"""
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_active=True,
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created")
            print("⚠️ WARNING: Change default password immediately!")
    
    def log_activity(action, details=None):
        """Log admin activity"""
        if current_user.is_authenticated:
            activity = ActivityLog(
                user_id=current_user.id,
                action=action,
                details=details,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(activity)
            db.session.commit()

    # Create tables and admin user
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
            
            # Create admin user if it doesn't exist
            create_default_admin()
        except Exception as e:
            print(f"Error creating tables: {e}")

    # ----------------------
    # Routes
    # ----------------------

    @app.route('/')
    def index():
        return render_template(
            'index.html',
            projects=get_featured_projects(),
            posts=get_recent_blog_posts()
        )

    @app.route('/about_me')
    def about_me():
        return render_template('about_me.html')

    @app.route('/projects')
    def projects():
        return render_template('projects.html', projects=get_all_projects())

    @app.route('/blog')
    def blog():
        try:
            # Only show published posts to public
            posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.date_posted.desc()).all()
            
            # For each post, prefer content from markdown file if available.
            for post in posts:
                # Ensure model attributes exist / provide defaults
                if not getattr(post, 'read_time', None):
                    try:
                        _ = post.read_time
                    except Exception:
                        post.read_time = '5 min read'
                if not getattr(post, 'slug', None):
                    post.slug = f"post-{post.id}"
                if not hasattr(post, 'category'):
                    post.category = None
                if not hasattr(post, 'tags'):
                    post.tags = None

                # Load markdown file content if present and convert to HTML
                md_html = get_blog_markdown_html(post.slug)
                if md_html:
                    # Use the HTML from the markdown file for preview/content
                    post.content_html = md_html
                    # Generate a short excerpt for index view (30 words)
                    post.excerpt = html_to_excerpt(md_html, words=30)
                else:
                    # Fallback: use excerpt from model or generate from content
                    if hasattr(post, 'excerpt') and post.excerpt:
                        # Use custom excerpt if available
                        pass
                    else:
                        # Generate excerpt from content
                        try:
                            post.excerpt = html_to_excerpt(post.content, words=30)
                        except Exception:
                            post.excerpt = None

                # Ensure post.content remains the DB content for safety
                if not hasattr(post, 'content_html'):
                    post.content_html = None
                    
            return render_template('blog.html', posts=posts)
        except Exception as e:
            print(f"Error loading blog posts: {e}")
            return render_template('blog.html', posts=[])

    @app.route('/blog/<slug>', methods=['GET', 'POST'])
    def blog_post(slug):
        try:
            # Find post by slug
            post = BlogPost.query.filter_by(slug=slug).first()
            
            # Fallback: try by ID if slug starts with 'post-'
            if not post and slug.startswith('post-'):
                try:
                    post_id = int(slug.split('-')[1])
                    post = BlogPost.query.get(post_id)
                except (ValueError, IndexError):
                    abort(404)
            
            if not post:
                abort(404)
            
            # Check if post is published (unless user is admin)
            if not post.is_published and not (current_user.is_authenticated and current_user.is_admin):
                abort(404)

            # If markdown file exists for this slug, prefer file content (rendered HTML)
            md_html = get_blog_markdown_html(post.slug if post.slug else (f"post-{post.id}"))
            if md_html:
                post.content = md_html
            elif getattr(post, 'content_html', None):
                # If we previously stored content_html on the object, use it
                post.content = post.content_html

            form = CommentForm()
            if form.validate_on_submit():
                comment = Comment(
                    post_id=post.id,
                    author=form.author.data,
                    body=form.body.data
                )
                db.session.add(comment)
                db.session.commit()
                flash('Your comment has been posted!', 'success')
                return redirect(url_for('blog_post', slug=slug))

            return render_template('blog_post.html', post=post, form=form)
        except Exception as e:
            print(f"Error loading blog post: {e}")
            abort(500)

    @app.route('/blog/post/<int:post_id>', methods=['GET', 'POST'])
    def blog_post_by_id(post_id):
        try:
            post = BlogPost.query.get_or_404(post_id)
            return redirect(url_for('blog_post', slug=post.slug if post.slug else f"post-{post.id}"))
        except Exception as e:
            print(f"Error loading blog post by ID: {e}")
            abort(404)

    @app.route('/blog/<slug>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_blog(slug):
        """Legacy edit route - will be replaced by admin interface"""
        # Check if user is admin
        if not current_user.is_admin:
            abort(403)
        
        post = BlogPost.query.filter_by(slug=slug).first_or_404()
        
        if request.method == 'POST':
            content = request.form['content']
            post.content = content
            post.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log activity
            log_activity('edit_blog', f'Edited blog post: {post.title}')
            
            flash('Blog post updated.', 'success')
            return redirect(url_for('blog_post', slug=slug))

        return render_template('edit_blog.html', slug=slug, content=post.content)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            message = ContactMessage(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data
            )
            db.session.add(message)
            db.session.commit()
            flash('Your message has been sent!', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html', form=form)

    @app.route('/migrate-db')
    @login_required
    def migrate_db():
        """Database migration endpoint (admin only)"""
        if not current_user.is_admin:
            abort(403)
            
        try:
            # ⚠️ This works only with SQLite. Replace for Postgres if needed.
            result = db.session.execute("PRAGMA table_info(blog_post)").fetchall()
            existing_columns = [row[1] for row in result]
            
            columns_to_add = {
                'read_time': 'VARCHAR(50)',
                'slug': 'VARCHAR(200)',
                'category': 'VARCHAR(100)',
                'tags': 'VARCHAR(300)',
                'is_published': 'BOOLEAN DEFAULT 1',
                'excerpt': 'TEXT',
                'meta_description': 'VARCHAR(300)',
                'cover_image': 'VARCHAR(200)',
                'updated_at': 'DATETIME',
                'author_id': 'INTEGER'
            }
            
            added_columns = []
            for column, data_type in columns_to_add.items():
                if column not in existing_columns:
                    db.session.execute(f'ALTER TABLE blog_post ADD COLUMN {column} {data_type}')
                    added_columns.append(column)
                    print(f"Added column: {column}")
            
            # Also create user table if it doesn't exist
            try:
                db.session.execute("SELECT 1 FROM user LIMIT 1")
            except:
                # Create user table
                db.session.execute('''
                    CREATE TABLE user (
                        id INTEGER PRIMARY KEY,
                        username VARCHAR(64) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(256),
                        is_active BOOLEAN DEFAULT 1,
                        is_admin BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_login DATETIME
                    )
                ''')
                print("Created user table")
            
            db.session.commit()
            
            # Log activity
            log_activity('migrate_db', f'Added columns: {", ".join(added_columns)}')
            
            flash(f'Database migration completed successfully! Added columns: {", ".join(added_columns)}', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Migration error: {str(e)}', 'error')
            return redirect(url_for('index'))

    # ----------------------
    # Admin Routes
    # ----------------------
    
    from admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/admin-init')
    def admin_init():
        """Initialize admin user (one-time setup)"""
        create_default_admin()
        flash('Admin user initialized. Default credentials: admin/admin123', 'info')
        return redirect(url_for('index'))

    # ----------------------
    # Error Handlers
    # ----------------------

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app


# Import admin blueprint (circular import handled at bottom)
from admin import admin_bp

# Expose globally for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)