from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class Credentials(Form):
    key_id = StringField('Key ID', validators=[DataRequired('Please enter an Key ID')])
    key_secret = PasswordField('Key Secret', validators=[DataRequired('Please enter an Key Secret')])
    account = StringField('Account', validators=[DataRequired('Please enter an account')])
    submit = SubmitField('List')

class Credentials_EC2(Form):
    key_id = StringField('Key ID', validators=[DataRequired('Please enter an Key ID')])
    key_secret = PasswordField('Key Secret', validators=[DataRequired('Please enter an Key Secret')])
    account = StringField('Account', validators=[DataRequired('Please enter an account')])
    region = StringField('Region', validators=[DataRequired('Please enter an region')])
    submit = SubmitField('Get EC2')