#!/usr/bin/env python
""" This script is used for get all instances information from an AWS account
    Author: Shi, Weiwen
"""
import boto3
import botocore
import time


class Get_instances_info(object):
    def __init__(self, key_id, key_secret, account, region):
        self.KEY_ID = key_id
        self.KEY_SECRET = key_secret
        self.account = str(account).strip()
        self.region = region
        self.credentials = None
        self.ec2_resource = None
        self.instances_list = []
        self.details = []
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
            self.ec2_resource = boto3.resource(
                'ec2',
                aws_access_key_id=self.credentials['AccessKeyId'],
                aws_secret_access_key=self.credentials['SecretAccessKey'],
                aws_session_token=self.credentials['SessionToken'],
                region_name=self.region
            )

        #Catch exceptions
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "InvalidClientTokenId":
                self.error = 'Invalid Key ID or Key Secret!'
            else:
                self.error = "Failed to get instances, please check your Key ID and Key Secret."


    #Get all bucket name list
    def list_instances(self):
        try:
            for i in self.ec2_resource.instances.all():
                ins_name = ''
                if i.tags != None:
                    for tag in i.tags:
                        if tag['Key'] == 'Name':
                            ins_name = tag['Value']
                if i.state.get('Name') == 'running':
                    instance_checks, system_checks = [self.ec2_resource.meta.client.describe_instance_status(InstanceIds=[i.id])\
                        ['InstanceStatuses'][0][each]['Details'][0]['Status'] for each in ['InstanceStatus', 'SystemStatus'] ]
                else:
                    instance_checks, system_checks = '--', '--'
                self.instances_list.append((ins_name, i.id, i.instance_type, i.private_ip_address, i.state.get('Name'), instance_checks, system_checks))
            return self.instances_list
        except Exception as e:
            self.error = "Failed to get instances, please check your Key ID and Key Secret."
            return None


    def instance_details(self, instance_id):
        try:
            instance = self.ec2_resource.Instance(instance_id)
            if instance.tags != None:
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        ins_name = tag['Value']
            if instance.state.get('Name') == 'running':
                instance_checks, system_checks = [
                    self.ec2_resource.meta.client.describe_instance_status(InstanceIds=[instance.id]) \
                        ['InstanceStatuses'][0][each]['Details'][0]['Status'] for each in ['InstanceStatus', 'SystemStatus']]
            else:
                instance_checks, system_checks = '--', '--'
            self.details.extend((ins_name, instance.id, instance.instance_type, instance.private_ip_address, instance.state.get('Name'),
                                        instance.public_dns_name, instance.security_groups, instance.block_device_mappings, instance_checks, system_checks))
            return self.details
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "InvalidClientTokenId":
                self.error = 'Invalid Key ID or Key Secret!'
            else:
                self.error = "Failed to get instances, please check your Key ID and Key Secret."


    def create_snapshots(self, instance_id):
        try:
            cur_time = time.strftime('%Y-%m-%d')
            instance = self.ec2_resource.Instance(instance_id)
            if instance.tags != None:
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        ins_name = tag['Value']
            for v in instance.volumes.all():
                snapshot = v.create_snapshot(Description='Backup created from' + v.id)
                snapshot.create_tags(Tags=[{'Key': 'Name', 'Value': v.id + ' - ' + cur_time + ' - Snapshots'}])
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "InvalidClientTokenId":
                self.error = 'Invalid Key ID or Key Secret!'
            else:
                self.error = "Failed to get instances, please check your Key ID and Key Secret."

