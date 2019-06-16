import boto3
from os.path import join
import pyfi_util
from settings import logger
import sys
import threading
import os

class ProgressMonitor:

    def __init__(self, filename):
        self.progress = 0
        
        if type(filename) is str:
            with open(filename, 'rb') as fl:
                self.filename = fl.name
        else:
            self.filename = filename.name
            
        self.size = os.stat(self.filename).st_size / 1024 / 1024
        self._lock = threading.Lock()
        

    def __call__(self,num:float):
        """used for callback of S3 boto3 client operations

        Arguments:
            data {float} -- number of bytes transferred to be periodically called during the operation
        """
        with self._lock:
            self.progress += num
            sys.stdout.write(f"S3 Progress: {round(self.progress/1024/1024,3)} of {round(self.size)}  MBs")
            logger.debug(f"S3 Progress: {self.progress} bytes")
            sys.stdout.write("\r\n")
            sys.stdout.flush()

class S3Connection:

    def __init__(self):
        self.active_bucket_name = ""
        self.s3 = "" # intended to store a boto3.client
        self.s3Resource = "" # intended to store a boto3.resource, as an alternative
        self.cached_bucket_names = "" # store bucket names so calls to AWS aren't always needed.
        self.cached_bucket_objects = {}
        self.connect()
        self.upload_progress = 0

    def connect(self):
        if not self.s3:
            self.s3 = boto3.client('s3')
        else:
            print('already initialized the s3 client.  No new value needed')

    def connect_resource(self):
        """original way I tried.  Might still have value, but easier to
        use the "connect" method instead for basic upload command, listing
        objects, and listing buckets.
        """

        if not self.s3Resource:
            self.s3Resource = boto3.resource('s3')
        else:
            print('already initialized the s3 resource.  No new value needed')

    def get_buckets(self, update_from_aws=False):
        if (not self.cached_bucket_names) or update_from_aws:
            self.connect()
            bucket_names = [ bucket['Name'] for bucket in self.s3.list_buckets()['Buckets'] ]
            self.cached_bucket_names = bucket_names
        return self.cached_bucket_names

    def get_resource_buckets(self):
        self.connect_resource()
        return self.s3Resource.buckets.all()

    def _get_objects_from_bucket(self, bucket_name="", update_from_aws=True):
        if not bucket_name:
            bucket_name = self.active_bucket_name

        if (('Name', bucket_name) not in self.cached_bucket_objects.items()) \
                    or update_from_aws:
            self.connect()
            objects = self.s3.list_objects(Bucket=bucket_name)
            self.cached_bucket_objects = objects
        return self.cached_bucket_objects

    def get_keynames_from_objects(self, bucket_name=""):
        obs = self._get_objects_from_bucket(bucket_name)
        if 'Contents' in obs.keys():
            return [ item['Key'] for item in obs['Contents'] ]
        else:
            return []

    def print_all_buckets(self):
        buckets = self.get_buckets()
        for bucket in buckets:
            print(f"{bucket}-{bucket.name}")

    def print_all_resource_buckets(self):
        buckets = self.get_resource_buckets()
        for bucket in buckets:
            print(f"{bucket}-{bucket.name}")

    def set_active_bucket(self, bucket_name="" ):
        if bucket_name:
            self.active_bucket_name = bucket_name
        else:
            self.choose_bucket()

    def choose_bucket(self):
        """print list of buckets and ask for selected
        index number from user
        """
        prompt = "Please choose a bucket to make your active bucket: "

        buckets_list = self.get_buckets()
        for i in range(len(buckets_list)):
            print(f"{str(i+1)} - {buckets_list[i]}")

        # get choice and make sure its valid before using the name
        choice = int(input(prompt))
        choice = choice if choice > 0 and choice <= len(buckets_list) \
                else None
        # set the name if choice if valid
        if choice:
            self.active_bucket_name = buckets_list[choice-1]
            print(f"You have now activated '{self.active_bucket_name}'")
        else:
            print("Aborting: no valid choice was made.  Please try again.")


    def make_bucket_list_from_resource(self):
        buckets = self.get_resource_buckets()
        return [ bucket.name for bucket in buckets ]

    def put_file(self, filepath, s3_file_name_key):
        """put a file in the active bucket. If there isn't an active bucket
        selected, prompt for a choice

        Arguments:
            filepath {string} -- full or relative path from the current working directory
            s3_file_name_key {string} -- name that the file will have in the bucket
        """

        if self.active_bucket_name:
            with open(filepath, 'rb') as data:
                self.s3Resource.Bucket(
                    self.active_bucket_name).put_object(
                        Key=s3_file_name_key,Body=data)
        else:
            self.choose_bucket()

    def upload_file(self, filepath, s3_file_name_key, metadata=None):
        """upload a file in the active bucket. If there isn't an active bucket
        selected, prompt for a choice

        Arguments:
            filepath {string} -- full or relative path from the current working directory
            s3_file_name_key {string} -- name that the file will have in the bucket
        """

        if self.active_bucket_name:
            self.s3.upload_file(filepath, self.active_bucket_name, s3_file_name_key,
                    ExtraArgs=metadata, Callback=ProgressMonitor(filepath), Config=None)
        else:
            print("Sorry, you need to activate a bucket first.  Afterwards, please redo the last attempt.")
            self.choose_bucket()

    def upload_fileobj(self, fileobj, s3_file_name_key="", metadata=None):
        """upload a fileobj in the active bucket. If there isn't an active bucket
        selected, prompt for a choice

        Arguments:
            filepath {string} -- full or relative path from the current working directory
            s3_file_name_key {string} -- name that the file will have in the bucket
        """
        response = ""
        if self.active_bucket_name:
            response = self.s3.upload_fileobj(fileobj, self.active_bucket_name, s3_file_name_key,
                    ExtraArgs=metadata, Callback=ProgressMonitor(fileobj), Config=None)
        else:
            print("Sorry, you need to activate a bucket first.  Afterwards, please redo the last attempt.")
            self.choose_bucket()
        return response

    def download_file_to_temp(self, filepath, s3_file_name_key, temp_location='temp/'):
        """Use s3.client.download_fileobj to get a binary file like object.

        Arguments:
            filepath {string} -- name of dest file
            s3_file_name_key {string} -- key in s3 bucket

        Keyword Arguments:
            temp_location {string} -- temp folder location (default: {'temp/'})
        """
        try:
            self.s3.download_file(self.active_bucket_name, s3_file_name_key, join(temp_location,filepath))
        except Exception as e:
            print('File not found')
            print(e.args)



    def download_file_obj(self, file, s3_file_name_key):
        """Use s3.client.download_fileobj to get a binary file like object.

        Arguments:
            filepath {string} -- name of dest file
            s3_file_name_key {string} -- key in s3 bucket

        Keyword Arguments:
            temp_location {string} -- temp folder location (default: {'temp/'})
        """
        data = None
        self.s3.client.download_fileobj(self.active_bucket_name, s3_file_name_key, data)
        return data











