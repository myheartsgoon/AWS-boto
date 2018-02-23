# coding=utf-8
from flask import Flask, render_template, request, redirect, session, url_for, flash
from forms import Credentials, Credentials_EC2, Add_Customer
from datetime import timedelta
from s3_all import Assume_s3_bucket
from ec2_all import Get_instances_info
import fileinput

app = Flask(__name__)

@app.before_request
def make_session_permant():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)

app.secret_key = 'development-key'

@app.route('/', methods=['GET', 'POST'])
def home():
    form = Credentials()
    if request.method == 'POST':
        if not form.validate():
            return render_template('home.html', form=form)
        else:
            account_info = get_account_info(form.account.data)
            if account_info == None:
                flash("No such customer, please enter another one.")
                return render_template('home.html', form=form)
            account_id = account_info[0]
            key_id, key_secret= form.key_id.data, form.key_secret.data
            session['key_id'], session['key_secret'], session['account'] = key_id, key_secret, account_id
            new_s3 = Assume_s3_bucket(key_id, key_secret , account_id)
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


@app.route('/ec2', methods=['GET', 'POST'])
def ec2():
    form = Credentials_EC2()
    if request.method == 'POST':
        if not form.validate():
            return render_template('ec2.html', form=form)
        else:
            account_info = get_account_info(form.account.data)
            if account_info == None:
                flash("No such customer, please enter another one.")
                return render_template('ec2.html', form=form)
            account_id = account_info[0]
            region = get_account_info(form.account.data)[1]
            key_id, key_secret= form.key_id.data, form.key_secret.data
            session['key_id'], session['key_secret'], session['account'], session['region'] = key_id, key_secret, account_id, region
            new_ec2 = Get_instances_info(key_id, key_secret , account_id, region)
            new_ec2.assumeRole()
            instacnes = new_ec2.list_instances()
            if new_ec2.error == None:
                if len(instacnes) > 0:
                    return render_template('ec2.html', form=form, instacnes=instacnes)
                else:
                    flash("There is no instances in this region.")
                    return render_template('ec2.html', form=form)
            else:
                return render_template('ec2.html', form=form, return_error=new_ec2.error)
    elif request.method == 'GET':
        return render_template('ec2.html', form=form)

@app.route('/create_snapshots')
def create_snapshots():
    if not session.get('key_id') or not session.get('region'):
        return '<p>You are not authenticated or your credential has been expired!</p>'
    else:
        instance_id = request.args.get('id')
        region = session.get('region')
        new_ec2 = Get_instances_info(session['key_id'], session['key_secret'], session['account'], session['region'])
        new_ec2.assumeRole()
        new_ec2.create_snapshots(instance_id)
        if new_ec2.error == None:
            return '<p>Snapshots created successfully, Click <a target="_blank" href="https://console.aws.amazon.com/ec2/v2/home?region={region}#Snapshots:sort=desc:startTime"> here </a> to go to AWS console</p>'.format(region=region)
        else:
            return '<p>Snapshots created failed, Click <a target="_blank" href="https://console.aws.amazon.com/ec2/v2/home?region={region}"> here </a> to create manually</p>'.format(region=region)


@app.route('/details/<instance_id>')
def details(instance_id):
    if not session.get('key_id') or not session.get('region'):
        flash('You are not authenticated or your credential has been expired!')
        return render_template('details.html')
    else:
        new_ec2 = Get_instances_info(session['key_id'], session['key_secret'], session['account'], session['region'])
        new_ec2.assumeRole()
        details = new_ec2.instance_details(instance_id)
        if new_ec2.error == None:
            return render_template('details.html', details=details)
        else:
            return render_template('details.html')


def get_account_info(customer_name):
    with open("customers", 'r') as f:
        for line in f:
            if customer_name.capitalize() in line:
                account_id = line.split()[1]
                region = line.split()[2]
                return (account_id, region)
    return None


@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    form = Add_Customer()
    if request.method == 'POST':
        if not form.validate():
            return render_template('add_customer.html', form=form)
        else:
            region_list = ['us-east-1', 'us-west-2','eu-west-1', 'ap-northeast-1']
            if form.region.data not in region_list:
                flash("Please enter a valid region")
                return render_template('add_customer.html', form=form)
            name, account_id, region = form.name.data, form.account_id.data, form.region.data
            with open("customers", "a") as f:
                content = " ".join([name, account_id, region])
                f.write('\n' + content)
            return redirect(url_for('show_all_customers'))
    elif request.method == 'GET':
        return render_template('add_customer.html', form=form)


@app.route('/remove_customer')
def remove_customer():
    account_id = request.args.get("account_id")
    for line in fileinput.input("customers", inplace=True):
        if account_id in line:
            print(end="")
        else:
            print(line)
    return redirect(url_for('show_all_customers'))


@app.route('/show_all_customers')
def show_all_customers():
    account = []
    with open("customers", 'r') as f:
        for line in f:
            each = line.split()
            if len(each) == 0:
                continue
            account.append((each[0], each[1], each[2]))
    if len(account) == 0:
        flash("No customer in the list. ")
        return render_template('customers_list.html')
    return render_template('customers_list.html', account=account)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
