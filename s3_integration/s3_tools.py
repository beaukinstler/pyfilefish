import boto3



class S3Connection:

    def __init__(self):
        self.active_bucket_name = ""
        self.s3 = "" # intended to store a boto3.client
        self.s3Resource = "" # intedted to store a boto3.resource, as an alternative
        self.cached_bucket_names = "" # store bucket names so calls to AWS aren't always needed.
        

    def connect(self):
        if not self.s3:
            self.s3 = boto3.client('s3')
        else:
            print('already initialized the s3 client.  No new value needed')
    
    def connect_resource(self):
        """original way I tried.  Might still have value, but eaiser to 
        use the "connect" method instead for basic upload command, listing
        objects, and listing buckets.
        """

        if not self.s3Resource:
            self.s3Resource = boto3.resource('s3')
        else:
            print('already initialized the s3 resource.  No new value needed')

    def get_buckets(self):
        self.connect()
        if not self.cached_bucket_names:
            bucket_names = [ bucket['Name'] for bucket in self.s3.list_buckets()['Buckets'] ]
            self.cached_bucket_names = bucket_names
        return self.cached_bucket_names

    def get_resource_buckets(self):
        self.connect_resource()
        return self.s3Resource.buckets.all()

    def get_objects_from_bucket(self, bucket_name=""):
        if not bucket_name:
            bucket_name = self.active_bucket_name
        objects = self.s3.list_objects(bucket_name)
        return objects

    def print_all_buckets(self):
        buckets = self.get_buckets()
        for bucket in buckets:
            print(f"{bucket}-{bucket.name}")

    def print_all_resource_buckets(self):
        buckets = self.get_resource_buckets()
        for bucket in buckets:
            print(f"{bucket}-{bucket.name}")

    def set_active_bucket(self, bucket_name ):
        if bucket_name:
            self.active_bucket_name = bucket_name
        else:
            self.choose_bucket()
    
    def choose_bucket(self):
        """print list of bucktes and ask for selected 
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
    
    def upload_file(self, filepath, s3_file_name_key):
        """upload a file in the active bucket. If there isn't an active bucket
        selected, prompt for a choice
        
        Arguments:
            filepath {string} -- full or relative path from the current working directory
            s3_file_name_key {string} -- name that the file will have in the bucket
        """

        if self.active_bucket_name:
            self.s3.upload_file(filepath, self.active_bucket_name, s3_file_name_key)
        else:
            print("Sorry, you need to activate a bucket first.  Afterwards, please redo the last attempt.")
            self.choose_bucket()
        





