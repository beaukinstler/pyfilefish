from pyfi import load_saved_file_list
from pyfi import JSON_FILE_PATH
from s3_integration.s3_tools import S3Connection
from dotenv import load_dotenv
import os
import logging as utilLogger


LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
utilLogger.basicConfig( filename='./logs/pyfi_util_log.txt', level=utilLogger.DEBUG,
        format=LOG_FORMAT)
utilLogger = utilLogger.getLogger()



def load_pyfish_data():
    file_list = load_saved_file_list(JSON_FILE_PATH)
    return file_list


def get_current_volumes():
    file_list = load_pyfish_data()
    volumes = set()
    for md5 in file_list:
        for item in file_list[md5]:
            volumes.add(item['volume'])
    return volumes


def sync_file_to_s3(file_ref):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file 
        that will need to checked and possibly uploaded
    """

    file_path = file_ref['full_path']
    s3_key = file_ref['md5hash']

    s3client = S3Connection()
    bucket_name = os.getenv("ACTIVE_BUCKET_NAME")
    s3client.set_active_bucket(bucket_name)
    if s3_key in s3client.get_keynames_from_objects(bucket_name):
        utilLogger.warning(msg="key found in objects already. Will not upload by default")
    else:
        s3client.upload_file(file_path, s3_key)



def get_unique_files_totalsize(filelist=None):
    """return the sum of MB stored in a pyfish file list

    Arguments:
        filelist {dict} -- file_list as created by pyfish.
        may also be loaded form a json_data.json that is 
        created and loaded by pyfish

    Returns:
        float -- sum of only the first instace for each unique
        file.
    """
    if not filelist:
        filelist = load_pyfish_data()

    return sum([ float(filelist[i][0]['file_size']) for i in filelist ])