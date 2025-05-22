from flask import Flask, render_template, flash, redirect, url_for
from config import Config
from models import db, Project, BlogPost, Comment, ContactMessage
from forms import ContactForm, CommentForm
from services.content_loader import (
    get_featured_projects,
    get_all_projects,
    get_recent_blog_posts,
    get_all_blog_posts
)
import markdown
from flask import abort
from flask import request


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

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
        return render_template('blog.html', posts=get_all_blog_posts())

    @app.route('/blog/<slug>', methods=['GET', 'POST'])
    def blog_post(slug):
        try:
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
            abort(500)

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
