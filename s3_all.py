# coding: utf-8
import boto3
import botocore
import threading


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            # sys.stdout.write(
            #     "\r%s --> %s bytes transferred" % (
            #         self._filename, self._seen_so_far))
            # sys.stdout.flush()
            print(self._seen_so_far)
            return self._seen_so_far

class Assume_s3_bucket(object):
    def __init__(self, key_id, key_secret, account):
        self.KEY_ID = key_id
        self.KEY_SECRET = key_secret
        self.account = str(account).strip()
        self.credentials = None
        self.s3_resource = None
        self.bucketlist = []
        self.error = None
    #Assume role to another account
    def assumeRole(self):
        # create an STS client object that represents a live connection to the
        # STS service
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=self.KEY_ID,
            aws_secret_access_key=self.KEY_SECRET
        )

        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        try:
            assumedRoleObject = sts_client.assume_role(
                RoleArn="arn:aws:iam::" + self.account + ":role/aws-crossaccount-admin",
                RoleSessionName="AssumeRoleSession1"
            )

            # From the response that contains the assumed role, get the temporary
            # credentials that can be used to make subsequent API calls
            self.credentials = assumedRoleObject['Credentials']

            # Use the temporary credentials that AssumeRole returns to make a
            # connection to Amazon S3
            self.s3_resource = boto3.resource(
                's3',
                aws_access_key_id=self.credentials['AccessKeyId'],
                aws_secret_access_key=self.credentials['SecretAccessKey'],
                aws_session_token=self.credentials['SessionToken'],
            )

        #Catch exceptions
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "InvalidClientTokenId":
                self.error = 'Invalid Key ID or Key Secret!'
            else:
                self.error = "Failed to list buckets, please check your Key ID and Key Secret."


    #Get all bucket name list
    def getallbucket(self):
        try:
            for bucket in self.s3_resource.buckets.all():
                self.bucketlist.append(bucket.name)
        except Exception as e:
            self.error = "Failed to list buckets, please check your Key ID and Key Secret."

    #List all files in a bucket
    # def listfiles(self,bucket_name):
    #     filecount = 0
    #     if bucket_name not in self.bucketlist:
    #         print("Bucket doesn't exist")
    #     else:
    #         bucket = self.s3_resource.Bucket(bucket_name)
    #         for file in bucket.objects.all():
    #             print(file.key)
    #             filecount += 1
    #         print('\n Total file number:', filecount)
    def listfiles(self, bucket_name):
        s3_client = boto3.client('s3', aws_access_key_id=self.credentials['AccessKeyId'],
                                 aws_secret_access_key=self.credentials['SecretAccessKey'],
                                 aws_session_token=self.credentials['SessionToken'])
        paginator = s3_client.get_paginator('list_objects')
        count = 0
        # Create a PageIterator from the Paginator
        try:
            operation_parameters = {'Bucket': bucket_name,
                                    'PaginationConfig': {'PageSize': 20, 'MaxItems': 20},
                                    #                         'StartAfter': 'before-nesting/'
                                    }
            page_iterator = paginator.paginate(**operation_parameters)

            for page in page_iterator:
                marker = page['Marker']
                try:
                    return page['Contents']
                except:
                    return None
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "InvalidClientTokenId":
                self.error = 'Invalid Key ID or Key Secret!'
            else:
                self.error = "Failed to list buckets, please check your Key ID and Key Secret."
            return None
        print(count)

    #Download a file in bucket
    def download(self, bucketname, filename):
        try:
            self.s3_resource.Bucket(bucketname).download_file(filename, filename, Callback=ProgressPercentage(filename))

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                print('Error: ' + e.response['Error']['Code'])

    def get_download_url(self, bucketname, filename):
        try:
            # Get the service client.
            s3_client = boto3.client('s3',
                                     aws_access_key_id=self.credentials['AccessKeyId'],
                                     aws_secret_access_key=self.credentials['SecretAccessKey'],
                                     aws_session_token=self.credentials['SessionToken'], )

            # Generate the URL to get 'key-name' from 'bucket-name'
            url = s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucketname,
                    'Key': filename
                }
            )

            return url


        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "InvalidClientTokenId":
                self.error = 'Invalid Key ID or Key Secret!'
            else:
                self.error = "Failed to list buckets, please check your Key ID and Key Secret."
            return None

#-----------------------------Test part----------------------------------------------
# new_s3 = Assume_s3_bucket('', '', '')
# new_s3.assumeRole()

