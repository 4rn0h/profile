# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo
from flask_wtf.file import FileField, FileAllowed

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')

class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    body = TextAreaField('Comment', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Post Comment')

# ADMIN FORMS
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    slug = StringField('URL Slug', validators=[Optional(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = TextAreaField('Excerpt (Optional)', validators=[Optional(), Length(max=500)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    tags = StringField('Tags (comma-separated)', validators=[Optional(), Length(max=300)])
    meta_description = StringField('Meta Description (SEO)', validators=[Optional(), Length(max=300)])
    is_published = BooleanField('Publish', default=True)
    is_featured = BooleanField('Featured', default=False)
    cover_image = FileField('Cover Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    submit = SubmitField('Save Post')

class SettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        Optional(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Settings')