# app.py - COMPLETE VERSION (ALL FIXES APPLIED)
from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, abort
from flask_login import LoginManager, login_required, current_user
from config import Config
from models import db, Project, BlogPost, Comment, ContactMessage, User, ActivityLog
from forms import ContactForm, CommentForm, LoginForm, BlogPostForm, SettingsForm
import markdown
from datetime import datetime
import os
import sys
import re
import html as _html

load_dotenv()

# Initialize Login Manager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ---- FREEZE MODE DETECTION ----
    IS_FREEZING = 'freeze' in sys.argv[0] or 'flask_frozen' in sys.modules
    if IS_FREEZING:
        print("🔧 Running in freeze mode - using static content only")
        app.config['FREEZING'] = True
    # ---- END ----
    
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
    # Content Loader Functions
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
        if not html_text:
            return ''
        
        text = re.sub(r'<[^>]+>', '', html_text)
        text = _html.unescape(text).strip()
        if not text:
            return ''
        
        parts = text.split()
        if len(parts) <= words:
            excerpt_text = ' '.join(parts)
        else:
            excerpt_text = ' '.join(parts[:words]) + '...'
        
        return f"<p>{excerpt_text}</p>"
    
    def calculate_read_time(content, words_per_minute=200):
        """Calculate estimated reading time from content."""
        text = re.sub(r'<[^>]+>', '', content)
        words = len(text.split())
        minutes = max(1, round(words / words_per_minute))
        
        if minutes < 2:
            return f"{minutes} min read"
        elif minutes < 60:
            return f"{minutes} min read"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hour read"
            return f"{hours} hour {remaining_minutes} min read"
    
    # ---- HELPER FUNCTION FOR STATIC GENERATION ----
    def get_blog_posts_from_markdown():
        """Load blog posts from markdown files for static generation"""
        posts = []
        blog_dir = os.path.join('static', 'blog')
        if os.path.exists(blog_dir):
            for filename in os.listdir(blog_dir):
                if filename.endswith('.md'):
                    slug = filename.replace('.md', '')
                    md_html = get_blog_markdown_html(slug)
                    if md_html:
                        posts.append({
                            'id': len(posts) + 1,
                            'slug': slug,
                            'title': ' '.join(word.capitalize() for word in slug.replace('_', ' ').split()),
                            'content': md_html,
                            'excerpt': html_to_excerpt(md_html, words=30),
                            'date_posted': datetime.now(),
                            'is_published': True,
                            'read_time': calculate_read_time(md_html),
                            'category': None,
                            'tags': None
                        })
        posts.sort(key=lambda x: x['date_posted'], reverse=True)
        return posts
    # ---- END ----
    
    def get_featured_projects():
        """Get featured projects for homepage"""
        if IS_FREEZING:
            return []
        
        try:
            return Project.query.order_by(Project.id.desc()).limit(3).all()
        except Exception as e:
            print(f"Error loading featured projects: {e}")
            return []
    
    def get_all_projects():
        """Get all projects"""
        if IS_FREEZING:
            return []
        
        try:
            return Project.query.order_by(Project.id.desc()).all()
        except Exception as e:
            print(f"Error loading all projects: {e}")
            return []
    
    def get_recent_blog_posts():
        """Get recent blog posts for homepage"""
        if IS_FREEZING:
            return get_blog_posts_from_markdown()[:3]
        
        try:
            posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(3).all()
            if posts and hasattr(posts[0], 'is_published'):
                posts = [p for p in posts if getattr(p, 'is_published', True)]
            return posts
        except Exception as e:
            print(f"Error loading recent blog posts: {e}")
            try:
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
        """Get all blog posts"""
        if IS_FREEZING:
            return get_blog_posts_from_markdown()
        
        try:
            posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
            if posts and hasattr(posts[0], 'is_published'):
                posts = [p for p in posts if getattr(p, 'is_published', True)]
            return posts
        except Exception as e:
            print(f"Error loading all blog posts: {e}")
            try:
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
            admin.set_password('admin123')
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
            if not IS_FREEZING:
                db.create_all()
                print("Database tables created successfully")
                create_default_admin()
            else:
                print("🔧 Skipping database creation in freeze mode")
        except Exception as e:
            print(f"Error creating tables: {e}")

    # ----------------------
    # ROUTES
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
            if IS_FREEZING:
                posts = get_blog_posts_from_markdown()
                return render_template('blog.html', posts=posts)
            
            posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.date_posted.desc()).all()
            
            for post in posts:
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

                md_html = get_blog_markdown_html(post.slug)
                if md_html:
                    post.content_html = md_html
                    post.excerpt = html_to_excerpt(md_html, words=30)
                else:
                    if hasattr(post, 'excerpt') and post.excerpt:
                        pass
                    else:
                        try:
                            post.excerpt = html_to_excerpt(post.content, words=30)
                        except Exception:
                            post.excerpt = None

                if not hasattr(post, 'content_html'):
                    post.content_html = None
                    
            return render_template('blog.html', posts=posts)
        except Exception as e:
            print(f"Error loading blog posts: {e}")
            return render_template('blog.html', posts=[])

    @app.route('/blog/<slug>', methods=['GET', 'POST'])
    def blog_post(slug):
        try:
            if IS_FREEZING:
                # Load from markdown directly
                md_html = get_blog_markdown_html(slug)
                if md_html:
                    post = {
                        'slug': slug,
                        'title': ' '.join(word.capitalize() for word in slug.replace('_', ' ').split()),
                        'content': md_html,
                        'date_posted': datetime.now(),
                        'read_time': calculate_read_time(md_html),
                        'category': None,
                        'tags': None
                    }
                    recent_posts = get_blog_posts_from_markdown()[:5]
                    return render_template('blog_post.html', post=post, form=None, recent_posts=recent_posts)
                abort(404)
            
            post = BlogPost.query.filter_by(slug=slug).first()
            
            if not post and slug.startswith('post-'):
                try:
                    post_id = int(slug.split('-')[1])
                    post = BlogPost.query.get(post_id)
                except (ValueError, IndexError):
                    abort(404)
            
            if not post:
                abort(404)
            
            if not post.is_published and not (current_user.is_authenticated and current_user.is_admin):
                abort(404)

            md_html = get_blog_markdown_html(post.slug if post.slug else (f"post-{post.id}"))
            if md_html:
                post.content = md_html
            elif getattr(post, 'content_html', None):
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

            # Convert database posts to dict format for the template
            recent_posts_data = []
            db_recent_posts = get_recent_blog_posts()[:5]
            for p in db_recent_posts:
                recent_posts_data.append({
                    'slug': p.slug if hasattr(p, 'slug') and p.slug else f"post-{p.id}",
                    'title': p.title,
                    'date_posted': p.date_posted.strftime('%B %d, %Y') if p.date_posted else None
                })
            
            return render_template('blog_post.html', post=post, form=form, recent_posts=recent_posts_data)
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
        if not current_user.is_admin:
            abort(403)
        
        post = BlogPost.query.filter_by(slug=slug).first_or_404()
        
        if request.method == 'POST':
            content = request.form['content']
            post.content = content
            post.updated_at = datetime.utcnow()
            db.session.commit()
            
            log_activity('edit_blog', f'Edited blog post: {post.title}')
            
            flash('Blog post updated.', 'success')
            return redirect(url_for('blog_post', slug=slug))

        return render_template('edit_blog.html', slug=slug, content=post.content)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        # Always create a form instance, even in freeze mode
        form = ContactForm()
        
        if IS_FREEZING:
            # In freeze mode, just render the template with an empty form
            return render_template('contact.html', form=form)
        
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
            
            try:
                db.session.execute("SELECT 1 FROM user LIMIT 1")
            except:
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

    # ----------------------
    # Context Processor for Footer Year
    # ----------------------
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app


# Expose globally for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)