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
            key_id, key_secret, account = form.key_id.data, form.key_secret.data, form.account.data
            session['key_id'], session['key_secret'], session['account'] = key_id, key_secret, account
            new_s3 = Assume_s3_bucket(key_id, key_secret , account)
            new_s3.assumeRole()
            new_s3.getallbucket()
            bucketlist = new_s3.bucketlist
            if new_s3.error == None:
                return render_template('home.html', form=form, bucketlist=bucketlist)
            else:
                return render_template('home.html', form=form, return_error=new_s3.error)

    elif request.method == 'GET':
        return render_template('home.html', form=form)

@app.route('/bucket/<bucket>')
def listfiles(bucket):
    if not session.get('key_id'):
        flash('You are not authenticated or your credential has been expired!')
        return render_template('bucket.html')
    else:
        new_s3 = Assume_s3_bucket(session['key_id'], session['key_secret'], session['account'])
        new_s3.assumeRole()
        if new_s3.error == None:
            files = new_s3.listfiles(bucket)
            return render_template('bucket.html', bucket=bucket, files=files)
        else:
            return render_template('bucket.html', return_error=new_s3.error)

@app.route('/download/<bucket>/<path:file>')
def download(bucket, file):
    if not session.get('key_id'):
        flash('You are not authenticated or your credential has been expired!')
        return render_template('bucket.html')
    else:
        new_s3 = Assume_s3_bucket(session['key_id'], session['key_secret'], session['account'])
        new_s3.assumeRole()
        url = new_s3.get_download_url(bucket, file)
        if new_s3.error == None:
            return redirect(url)
        else:
            return render_template('bucket.html', return_error=new_s3.error)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
