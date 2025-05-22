from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Send Message')

class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    body = TextAreaField('Comment', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Post Comment')
