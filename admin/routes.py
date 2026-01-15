# admin/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import markdown

# Import admin_bp from current module's parent
from . import admin_bp

# Import models and forms
from models import db, BlogPost, User, ActivityLog, Comment, ContactMessage, Project
from forms import LoginForm, BlogPostForm, SettingsForm

@admin_bp.route('/test')
def test():
    return "Admin blueprint is working!"

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    stats = {
        'total_posts': BlogPost.query.count(),
        'published_posts': BlogPost.query.filter_by(is_published=True).count(),
        'draft_posts': BlogPost.query.filter_by(is_published=False).count(),
        'total_comments': Comment.query.count(),
        'pending_messages': ContactMessage.query.filter_by(is_read=False).count(),
        'total_projects': Project.query.count(),
    }
    
    # Get recent activities
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    # Get recent posts
    recent_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_activities=recent_activities,
                         recent_posts=recent_posts,
                         now=datetime.utcnow())

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember.data)
            user.update_last_login()
            
            # Log activity
            log_activity('login', f'User {user.username} logged in')
            
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    # Log activity
    log_activity('logout', f'User {current_user.username} logged out')
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/posts')
@login_required
def posts():
    """List all blog posts"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    status = request.args.get('status', 'all')
    
    # Filter by status
    query = BlogPost.query
    if status == 'published':
        query = query.filter_by(is_published=True)
    elif status == 'drafts':
        query = query.filter_by(is_published=False)
    
    posts = query.order_by(BlogPost.date_posted.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('admin/posts.html', posts=posts, status=status)

@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create new blog post"""
    form = BlogPostForm()
    
    if form.validate_on_submit():
        # Generate slug if not provided
        slug = form.slug.data
        if not slug:
            slug = BlogPost.generate_slug(form.title.data)
        
        # Check if slug already exists
        existing = BlogPost.query.filter_by(slug=slug).first()
        if existing:
            flash('A post with this slug already exists. Please choose a different one.', 'error')
            return render_template('admin/edit_post.html', form=form, action='new')
        
        # Handle file upload
        cover_image_filename = None
        if form.cover_image.data:
            cover_image_filename = save_uploaded_file(form.cover_image.data)
        
        # Create post
        post = BlogPost(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            excerpt=form.excerpt.data,
            category=form.category.data,
            tags=form.tags.data,
            meta_description=form.meta_description.data,
            is_published=form.is_published.data,
            is_featured=form.is_featured.data,
            cover_image=cover_image_filename,
            author_id=current_user.id,
            date_posted=datetime.utcnow()
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Save as markdown file
        try:
            post.save_as_markdown()
        except Exception as e:
            print(f"Warning: Could not save as markdown: {e}")
        
        # Log activity
        log_activity('create_post', f'Created post: {post.title}')
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/edit_post.html', form=form, action='new')

@admin_bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit existing blog post"""
    post = BlogPost.query.get_or_404(post_id)
    form = BlogPostForm(obj=post)
    
    if form.validate_on_submit():
        # Update slug if title changed significantly
        if post.title != form.title.data:
            post.update_slug()
        
        # Handle file upload
        if form.cover_image.data:
            # Delete old cover image if exists
            if post.cover_image:
                delete_uploaded_file(post.cover_image)
            post.cover_image = save_uploaded_file(form.cover_image.data)
        
        # Update post
        post.title = form.title.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.category = form.category.data
        post.tags = form.tags.data
        post.meta_description = form.meta_description.data
        post.is_published = form.is_published.data
        post.is_featured = form.is_featured.data
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update markdown file
        try:
            post.save_as_markdown()
        except Exception as e:
            print(f"Warning: Could not update markdown: {e}")
        
        # Log activity
        log_activity('edit_post', f'Edited post: {post.title}')
        
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.posts'))
    
    return render_template('admin/edit_post.html', form=form, action='edit', post=post)

@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Delete blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    # Delete cover image if exists
    if post.cover_image:
        delete_uploaded_file(post.cover_image)
    
    # Delete markdown file
    try:
        md_path = os.path.join('static', 'blog', f"{post.slug}.md")
        if os.path.exists(md_path):
            os.remove(md_path)
    except Exception as e:
        print(f"Warning: Could not delete markdown file: {e}")
    
    # Log activity before deleting
    log_activity('delete_post', f'Deleted post: {post.title}')
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.posts'))

@admin_bp.route('/posts/<int:post_id>/toggle-publish', methods=['POST'])
@login_required
def toggle_publish(post_id):
    """Toggle post publish status"""
    post = BlogPost.query.get_or_404(post_id)
    post.is_published = not post.is_published
    
    action = 'published' if post.is_published else 'unpublished'
    log_activity('toggle_publish', f'{action.capitalize()} post: {post.title}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_published': post.is_published,
        'message': f'Post {action} successfully!'
    })

@admin_bp.route('/posts/<int:post_id>/preview')
@login_required
def preview_post(post_id):
    """Preview blog post"""
    post = BlogPost.query.get_or_404(post_id)
    return render_template('admin/preview_post.html', post=post)

@admin_bp.route('/comments')
@login_required
def comments():
    """Manage comments"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    comments = Comment.query.order_by(Comment.date_posted.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('admin/comments.html', comments=comments)

@admin_bp.route('/comments/<int:comment_id>/toggle-approve', methods=['POST'])
@login_required
def toggle_approve_comment(comment_id):
    """Toggle comment approval"""
    comment = Comment.query.get_or_404(comment_id)
    comment.is_approved = not comment.is_approved
    
    action = 'approved' if comment.is_approved else 'unapproved'
    log_activity('toggle_comment', f'{action.capitalized()} comment by {comment.author}')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'is_approved': comment.is_approved,
        'message': f'Comment {action} successfully!'
    })

@admin_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Delete comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    log_activity('delete_comment', f'Deleted comment by {comment.author}')
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('admin.comments'))

@admin_bp.route('/messages')
@login_required
def messages():
    """View contact messages"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status = request.args.get('status', 'unread')
    
    # Filter by status
    query = ContactMessage.query
    if status == 'unread':
        query = query.filter_by(is_read=False)
    elif status == 'read':
        query = query.filter_by(is_read=True)
    
    messages = query.order_by(ContactMessage.date_sent.desc()).paginate(page=page, per_page=per_page)
    
    return render_template('admin/messages.html', messages=messages, status=status)

@admin_bp.route('/messages/<int:message_id>/mark-read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark message as read"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    
    log_activity('mark_message_read', f'Marked message from {message.name} as read')
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Message marked as read!'
    })

@admin_bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete contact message"""
    message = ContactMessage.query.get_or_404(message_id)
    
    log_activity('delete_message', f'Deleted message from {message.name}')
    
    db.session.delete(message)
    db.session.commit()
    
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('admin.messages'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Admin settings"""
    form = SettingsForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username changed
        if current_user.username != form.username.data:
            existing = User.query.filter_by(username=form.username.data).first()
            if existing and existing.id != current_user.id:
                flash('Username already taken!', 'error')
                return render_template('admin/settings.html', form=form)
            current_user.username = form.username.data
        
        # Check if email changed
        if current_user.email != form.email.data:
            existing = User.query.filter_by(email=form.email.data).first()
            if existing and existing.id != current_user.id:
                flash('Email already registered!', 'error')
                return render_template('admin/settings.html', form=form)
            current_user.email = form.email.data
        
        # Update password if provided
        if form.new_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect!', 'error')
                return render_template('admin/settings.html', form=form)
            
            if form.new_password.data != form.confirm_password.data:
                flash('New passwords do not match!', 'error')
                return render_template('admin/settings.html', form=form)
            
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        
        log_activity('update_settings', 'Updated admin settings')
        
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html', form=form)

@admin_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Upload image for blog post content"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid collisions
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Log activity
        log_activity('upload_image', f'Uploaded image: {filename}')
        
        # Return URL for editor
        image_url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({'url': image_url})
    
    return jsonify({'error': 'Invalid file type'}), 400

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid collisions
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        return filename
    return None

def delete_uploaded_file(filename):
    """Delete uploaded file"""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)

def log_activity(action, details=None):
    """Log admin activity"""
    activity = ActivityLog(
        user_id=current_user.id,
        action=action,
        details=details,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity)
    db.session.commit()