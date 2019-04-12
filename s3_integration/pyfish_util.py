from pyfi import load_saved_file_list
from pyfi import JSON_FILE_PATH
from s3_integration.s3_tools import S3Connection
from dotenv import load_dotenv
import os
import logging as utilLogger
from collections import defaultdict
import json


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


def parse_location_metadata(file_ref):
    """get the meta location data from the file_ref
    
    Arguments:
        file_ref {dict} -- complex dict, based on the pyfish 
        file_list items
    
    Returns:
        dict -- converted defaultdict, grouped by voulme. Will have at least one
        full path name for the file on the volume, but could be a list of them per
        volume if there is more than one on a volume.
    """

    try:
        volumes_and_files = [ (i['volume'], i['full_path']) for i in file_ref]
        if volumes_and_files:
            files_grouped_by_volume = defaultdict(list)
            [ files_grouped_by_volume[volumeName].append(filename) \
                    for volumeName,filename in volumes_and_files ]
            [ i.encode('utf-8') for i in files_grouped_by_volume ]
            locations = dict(files_grouped_by_volume.items())
            result = {'Metadata' : { 'Locations': locations }}
            
    except KeyError as e:
        utilLogger.error(f"Encountered error parsing location metadata. Error: {e}")
        result = None
    return result

def build_relative_destination_path(pyfish_file_ref):
    """form the path used to store the file, including shared sub
    directories based on file_type. The files being synced from any 
    volume should be able to use this path to see if the file, named
    as <md5hashOfFile>.<extension> exists already. 
    
    Arguments:
        pyfish_file_ref {[type]} -- [description]
    """

    path = f"{pyfish_file_ref['filetype']}/{pyfish_file_ref['md5hash']}/"
    return path


def sync_file_to_s3(most_recent_file_added, meta=None):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file 
        that will need to checked and possibly uploaded
    """
    
    file_path = most_recent_file_added['full_path']

    sub_path = build_relative_destination_path(most_recent_file_added)
    temp_folder = 'temp/'
    volume_name = f"{most_recent_file_added['volume']}"
    full_path = f"{most_recent_file_added['full_path']}"
    name_to_store = f"{most_recent_file_added['md5hash']}"
    extention = f"{most_recent_file_added['filetype']}"
    s3_key = f"{sub_path}{name_to_store}.{extention}"
    s3_manifest_file = f"{name_to_store}.manifest.json"
    s3_key_manifest = f"{sub_path}{s3_manifest_file}"

    # make sure the files is there, or upload it if not
    s3client = S3Connection()
    bucket_name = os.getenv("ACTIVE_BUCKET_NAME")
    s3client.set_active_bucket(bucket_name)
    if s3_key in s3client.get_keynames_from_objects(bucket_name):
        utilLogger.warning(msg="key found in objects already. Will not upload by default")
    else:
        try:
            s3client.upload_file(file_path, s3_key, 
                    metadata=meta)
        except Exception as e:
            utilLogger.error(e)

    # update or create a manifest to store as well
    if s3_key_manifest in s3client.get_keynames_from_objects(bucket_name):
        utilLogger.info(msg="manifest files exsists. Will download, update, and upload")
        s3client.download_file_to_temp(s3_manifest_file, s3_key_manifest, temp_folder)
        add_location_to_file_manifest(os.path.join(temp_folder, s3_manifest_file),volume_name, full_path)
        # s3client.upload_file(os.path.join(temp_folder,s3_manifest_file), s3_key_manifest)
    else:
        # no manifest found.  Create and upload it
        temp_manifest = create_manifest(volume_name, full_path)
        with open(os.path.join(temp_folder,s3_manifest_file), 'w+') as temp_json:
            json.dump(temp_manifest, temp_json)
        # s3client.upload_file(os.path.join(temp_folder,s3_manifest_file), s3_key_manifest)
    # in either case, upload the file
    s3client.upload_file(os.path.join(temp_folder,s3_manifest_file), s3_key_manifest)

def create_manifest(volume_name:str, file_name, path=""):
    """make a file that contains all known locations of a file.
    To be stored with the file.


    """
    mainifest = {}
    volume_name = volume_name
    mainifest['locations'] = {}
    mainifest['locations'][volume_name] = []
    mainifest['locations'][volume_name].append(os.path.join(path, file_name))
    return mainifest


def add_location_to_file_manifest(
        manifest_file_name, location_volume, location_path):
    """take details of a file, the location of it's manifest, download it,
    update the details, and reupload it. 
    """
    manifest_file_data = manifest_file_name
    manifest = None
    # if s3client:
    #     s3client.download_file_to_temp(
    #             manifest_file_data, os.path.join(manifest_path, manifest_file_name), 'temp')
    try:
        with open(manifest_file_data, 'r') as tmpjson:
            manifest = json.load(tmpjson)
        try:
            files = manifest['locations'][location_volume]
            try: 
                files.remove(location_path)
            except ValueError as e:
                # path doesn't already exists
                pass
            files.append(location_path)
            files.sort()
            manifest['locations'][location_volume] = files

        except KeyError as e:
            manifest['locations'][location_volume] = [location_path]
        
        # after the key for the volume has been updated, write the file over again
        with open(manifest_file_data, 'w+') as temp_out:
            json.dump(manifest, temp_out)
        
    except FileExistsError as e:
        print(e)
    







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