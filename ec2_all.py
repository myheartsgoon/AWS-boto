#!/usr/bin/env python
""" This script is used for get all instances information from an AWS account
    Author: Shi, Weiwen
"""
from boto.sts import STSConnection
from boto.regioninfo import RegionInfo


class Get_instances_info(object):
    def __init__(self, key_id, key_secret, account, region):
        self.KEY_ID = key_id
        self.KEY_SECRET = key_secret
        self.account = str(account).strip()
        self.region = region
        self.credentials = None
        self.s3_resource = None
        self.error = None

    def list_instance(self):
        try:
            sts_connection = STSConnection(aws_access_key_id=self.KEY_ID,
                                           aws_secret_access_key=self.KEY_SECRET)

            assumedRoleObject = sts_connection.assume_role(
                role_arn="arn:aws:iam::" + self.account + ":role/aws-crossaccount-admin",
                role_session_name="AssumeRoleSession1"
            )
            from boto.ec2.connection import EC2Connection
            connection = EC2Connection(
                aws_access_key_id=assumedRoleObject.credentials.access_key,
                aws_secret_access_key=assumedRoleObject.credentials.secret_key,
                security_token=assumedRoleObject.credentials.session_token,
                region=RegionInfo(name=self.region,
                                  endpoint='ec2.' + self.region + '.amazonaws.com')
            )
            reservation = connection.get_all_instances()
            return reservation
        except Exception as e:
            self.error = e
