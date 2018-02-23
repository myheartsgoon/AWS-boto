from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class Credentials(Form):
    key_id = StringField('Key ID', validators=[DataRequired('Please enter an Key ID')])
    key_secret = PasswordField('Key Secret', validators=[DataRequired('Please enter an Key Secret')])
    account = StringField('Customer Name', validators=[DataRequired('Please enter customer name')])
    submit = SubmitField('List Buckets')

class Credentials_EC2(Form):
    key_id = StringField('Key ID', validators=[DataRequired('Please enter an Key ID')])
    key_secret = PasswordField('Key Secret', validators=[DataRequired('Please enter an Key Secret')])
    account = StringField('Customer Name', validators=[DataRequired('Please enter customer name')])
    submit = SubmitField('Get Instances')


class Add_Customer(Form):
    name = StringField('Name', validators=[DataRequired('Please enter the customer name')])
    account_id = StringField('Account ID', validators=[DataRequired('Please enter the account ID')])
    region = StringField('Region', validators=[DataRequired('Please enter the region')])
    submit = SubmitField('Add Customer')