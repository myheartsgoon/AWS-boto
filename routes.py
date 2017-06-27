# coding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash
from forms import SignupForm, LoginForm, Credentials
from datetime import timedelta
from s3_all import Assume_s3_bucket


app = Flask(__name__)

@app.before_request
def make_session_permant():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

app.secret_key = 'development-key'

@app.route('/', methods=['GET', 'POST'])
def home():
    form = Credentials()
    if request.method == 'POST':
        if not form.validate():
            return render_template('home.html', form=form)
        else:
            new_s3 = Assume_s3_bucket(form.key_id.data, form.key_secret.data, form.account.data)
            new_s3.assumeRole()
            new_s3.getallbucket()
            bucketlist = new_s3.bucketlist
            return render_template('home.html', form=form, bucketlist=bucketlist)

    elif request.method == 'GET':
        return render_template('home.html', form=form)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)
