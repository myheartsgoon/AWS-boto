from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(Form):
    first_name = StringField('First name', validators=[DataRequired('Please enter your first name')])
    last_name = StringField('Last name', validators=[DataRequired('Please enter your last name')])
    email = StringField('Email', validators=[DataRequired('Please enter your email address'), Email('Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter your password'), Length(min=6, message='Password must be at least 6 character')])
    submit = SubmitField('Sign up')

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired('Please enter your email address'), Email('Please enter a valid email address')])
    password = PasswordField('Password', validators=[DataRequired('Please enter your password')])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')

class Credentials(Form):
    key_id = StringField('Key ID', validators=[DataRequired('Please enter an Key ID')])
    key_secret = StringField('Key Secret', validators=[DataRequired('Please enter an Key Secret')])
    account = StringField('Account', validators=[DataRequired('Please enter an account')])
    submit = SubmitField('List')