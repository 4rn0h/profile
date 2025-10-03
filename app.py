from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, jsonify, request, abort
from config import Config
from models import db, Project, BlogPost, Comment, ContactMessage, CVDownload
from forms import ContactForm, CommentForm
from services.content_loader import (
    get_featured_projects,
    get_all_projects,
    get_recent_blog_posts,
    get_all_blog_posts
)
import markdown
from datetime import datetime

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize db
    db.init_app(app)

    # Create tables within app context
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")

    # Routes
    @app.route('/')
    def index():
        return render_template('index.html',
                               projects=get_featured_projects(),
                               posts=get_recent_blog_posts())

    @app.route('/about_me')
    def about_me():
        return render_template('about_me.html')

    @app.route('/projects')
    def projects():
        return render_template('projects.html', projects=get_all_projects())

    @app.route('/blog')
    def blog():
        try:
            posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()
            
            # Ensure each post has the required attributes with fallbacks
            for post in posts:
                if not hasattr(post, 'read_time') or post.read_time is None:
                    post.read_time = '5 min read'
                if not hasattr(post, 'slug') or post.slug is None:
                    # Generate a simple slug from ID as fallback
                    post.slug = f"post-{post.id}"
                if not hasattr(post, 'category'):
                    post.category = None
                if not hasattr(post, 'tags'):
                    post.tags = None
                    
            return render_template('blog.html', posts=posts)
            
        except Exception as e:
            print(f"Error loading blog posts: {e}")
            # Return empty posts list if there's an error
            return render_template('blog.html', posts=[])

    @app.route('/blog/<slug>', methods=['GET', 'POST'])
    def blog_post(slug):
        try:
            # Try to find post by slug first, then by ID as fallback
            if slug.startswith('post-'):
                try:
                    post_id = int(slug.split('-')[1])
                    post = BlogPost.query.get_or_404(post_id)
                except (ValueError, IndexError):
                    abort(404)
            else:
                post = BlogPost.query.filter_by(slug=slug).first_or_404()

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

    # Alternative route using post ID for backward compatibility
    @app.route('/blog/post/<int:post_id>', methods=['GET', 'POST'])
    def blog_post_by_id(post_id):
        try:
            post = BlogPost.query.get_or_404(post_id)
            return redirect(url_for('blog_post', slug=post.slug if post.slug else f"post-{post.id}"))
        except Exception as e:
            print(f"Error loading blog post by ID: {e}")
            abort(404)

    @app.route('/blog/<slug>/edit', methods=['GET', 'POST'])
    def edit_blog(slug):
        path = f'static/blog/{slug}.md'

        if request.method == 'POST':
            content = request.form['content']
            with open(path, 'w') as f:
                f.write(content)
            flash('Blog post updated.', 'success')
            return redirect(url_for('blog_post', slug=slug))

        try:
            with open(path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            abort(404)

        return render_template('edit_blog.html', slug=slug, content=content)

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

    # CV Download Tracking Endpoint
    @app.route('/log-cv-download', methods=['POST'])
    def log_cv_download():
        try:
            data = request.get_json()
            
            download = CVDownload(
                email=data['email'],
                name=data.get('name', 'Anonymous'),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            db.session.add(download)
            db.session.commit()
            
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Database migration endpoint for adding missing columns
    @app.route('/migrate-db')
    def migrate_db():
        try:
            with app.app_context():
                # This is a simple migration approach
                # In production, use proper migrations like Flask-Migrate
                
                # Get existing table info
                result = db.engine.execute("PRAGMA table_info(blog_post)")
                existing_columns = [row[1] for row in result]
                
                columns_to_add = {
                    'read_time': 'VARCHAR(50)',
                    'slug': 'VARCHAR(200)',
                    'category': 'VARCHAR(100)',
                    'tags': 'VARCHAR(300)'
                }
                
                for column, data_type in columns_to_add.items():
                    if column not in existing_columns:
                        db.engine.execute(f'ALTER TABLE blog_post ADD COLUMN {column} {data_type}')
                        print(f"Added column: {column}")
                
                flash('Database migration completed successfully!', 'success')
                return redirect(url_for('blog'))
                
        except Exception as e:
            flash(f'Migration error: {str(e)}', 'error')
            return redirect(url_for('blog'))

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)