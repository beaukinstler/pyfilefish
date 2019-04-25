# from pyfi import load_saved_file_list
# from pyfi  JSON_FILE_PATH
from s3_integration.s3_tools import S3Connection
from dotenv import load_dotenv
import os
import logging as utilLogger
from collections import defaultdict
import json
from settings import *
from hashlib import md5
import datetime
from filetypes.file_types import FileProperySet
from shutil import copyfile
from pathlib import Path

ignore_dirs = IGNORE_DIRS
# LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
# utilLogger.basicConfig( filename='./logs/pyfi_util_log.txt', level=utilLogger.DEBUG,
        # format=LOG_FORMAT)
# utilLogger = utilLogger.getLogger()
utilLogger = logger

def _load_saved_file_list(json_file_path):
    """
    loads the json file that has previously found files
    """
    external_file_list = {}
    try:
        with open(json_file_path, 'r') as json_data:
            external_file_list = json.load(json_data)
            utilLogger.info(f"found the json file and loaded saved data from {json_file_path}")
    except FileNotFoundError as e:
        print(f"Warning: {e.strerror}")
        print(f"warning: Missing {json_file_path}")
        print("Info: This is normal, if this is a first run of the program.")
        utilLogger.info(f"{json_file_path} was not found. A new file will be created")
    return external_file_list

def load_pyfish_data():
    file_list = _load_saved_file_list(JSON_FILE_PATH)
    return file_list


def get_current_volumes():
    """From a File-list, parse and look for volumes that have been
    used.
    
    Returns:
        set -- a set of unique strings of names of volumes
    """

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

    return (path, pyfish_file_ref['filetype'], pyfish_file_ref['md5hash'])


def sync_to_another_drive(most_recent_file_added, target):
    """Copy file to a local drive.
    
    Arguments:
        most_recent_file_added {dict} -- a referecne to a record (dict) 
        from the pyfile_file lsit.  This will be used to referece the file
        that must be coppied
    """
    # set the variables
    
    # make sure the target is the real path, not a symlink
    # BUG: the target is getting tranlated to the relative temp folder, not the "temp" folder
    # that I passed it.  
    target = os.path.realpath(target)

    # relative path on destination, ./type/hash/
    # sub_path = build_relative_destination_path(most_recent_file_added)
    
    # get all paths in the file ref record to add to manifest.
    all_paths = sorted([ i['full_path'] for i in most_recent_file_added ])
    # just choose one of the paths to sync
    data_file_ref = most_recent_file_added[0]
    sub_path,extention,md5hash = build_relative_destination_path(data_file_ref)
    temp_folder = 'temp/'
    os.makedirs(temp_folder, exist_ok=True)
    volume_name = f"{data_file_ref['volume']}"
    full_path = f"{data_file_ref['full_path']}"
    name_to_store = f"{md5hash}.{extention}"
    relative_dst_file = os.path.join(sub_path, name_to_store)
    manifest_file_name = f"{md5hash}.manifest.json"
    relative_manifest_file = f"{os.path.join(sub_path, manifest_file_name)}"
    full_path_mainfest = f"{os.path.join(target, relative_manifest_file)}"
    full_path_dest_file  = f"{os.path.join(target, relative_dst_file)}"
    
    # make the dir, incase is doesn't exists.
    os.makedirs(os.path.join(target,sub_path), exist_ok=True)

    # copy the file if doesn't already exist
    if os.path.exists(full_path_dest_file):
        logger.debug(f"{name_to_store} already exists.  Not updating")
    else:
        copyfile(os.path.realpath(full_path), full_path_dest_file)
        
    if os.path.exists(full_path_mainfest):
        utilLogger.debug("file mainifest exists. will copy to local temp, update the paths, and copy back to destination")
        copyfile(full_path_mainfest, os.path.join(temp_folder, manifest_file_name))
        add_location_to_file_manifest(os.path.join(temp_folder, manifest_file_name),volume_name, all_paths)
        copyfile(os.path.join(temp_folder, manifest_file_name), full_path_mainfest)
    else:
        temp_manifest = create_manifest(volume_name, all_paths)
        with open(os.path.join(temp_folder,manifest_file_name), 'w+') as temp_json:
            json.dump(temp_manifest, temp_json)
        copyfile(os.path.join(temp_folder, manifest_file_name), full_path_mainfest)


def sync_file_to_s3(most_recent_file_added, meta=None):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file 
        that will need to checked and possibly uploaded
    """
    
    file_path = most_recent_file_added['full_path']

    sub_path,extention,name_to_store = build_relative_destination_path(most_recent_file_added)
    temp_folder = 'temp/'
    volume_name = f"{most_recent_file_added['volume']}"
    full_path = f"{most_recent_file_added['full_path']}"
    # name_to_store = f"{most_recent_file_added['md5hash']}"
    # extention = f"{most_recent_file_added['filetype']}"
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

def create_manifest(volume_name:str, locations, path=""):
    """make a file that contains all known locations of a file.
    To be stored with the file.


    """
    path_list = list(locations) #  if it's just one string, make it a list for the loop
    mainifest = {}
    volume_name = volume_name
    mainifest['locations'] = {}
    mainifest['locations'][volume_name] = []
    for file_name in path_list:
        mainifest['locations'][volume_name].append(os.path.join(path, file_name))
    return mainifest


def add_location_to_file_manifest(
        manifest_file_name, location_volume, location_paths):
    """take details of a file, the location of it's manifest, download it,
    update the details, and reupload it. 
    """
    manifest_file_data = manifest_file_name
    all_paths = list(location_paths)
    manifest = None
    # if s3client:
    #     s3client.download_file_to_temp(
    #             manifest_file_data, os.path.join(manifest_path, manifest_file_name), 'temp')
    try:
        with open(manifest_file_data, 'r') as tmpjson:
            manifest = json.load(tmpjson)
        try:
            for location_path in all_paths:
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


def get_md5(fileObjectToHash, block_size=40960):
    """A wrapper around the hashlib md5 functions. This is 
    used to read and hash a block at a time, in the event of 
    a very large file being checked. 
    
    Arguments:
        fileObjectToHash {fp} -- File-like object data.
    
    Keyword Arguments:
        block_size {int} -- [description] (default: {2048*20})
    
    Returns:
        str -- md5 sum of the file as a string
    """

    file_hash = md5()
    while True:
        data = fileObjectToHash.read(block_size)
        if not data:
            break
        file_hash.update(data)
    # hex digest is better than digest, for standart use.
    return file_hash.hexdigest()

def modification_date(filename):
    time_of_mod = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(time_of_mod)

def only_sync_file( local_target="temp", volume_name="", file_types=[] ):
    file_list = load_pyfish_data()
    new_file_list = {}
    file_type_list = [ i.extension for i in file_types.ft_list ]

    if file_type_list:
        for ref in file_list:
            temp_list = list(filter(lambda x: x['filetype'] in file_type_list, file_list[ref]))
            if temp_list:
                new_file_list[ref] = temp_list
    
    if volume_name:
        for ref in file_list:
            temp_list = list(filter(lambda x: x['volume'] == volume_name, file_list[ref]))
            if temp_list:
                new_file_list[ref] = temp_list   

    for file_ref in new_file_list:
        # for each item in new_file_list, git pass only the first file, since only one copy is needed
        # of a file with copies found.  The manifest, however, will show all the copies
        # found on the volume.
        sync_to_another_drive(new_file_list[file_ref], local_target)




def build_file_reference():
    pass


def scan_for_files(pyfi_file_list:list, folder, file_types:FileProperySet, volume_name, sync_to_s3, sync_to_local_drive, load_external:bool=LOAD_EXTERNAL, local_target=None):
        
        print(f"Start Time: {str(datetime.datetime.now().time())}")
        for (paths, dirs, files) in os.walk(folder, topdown=True):
            for ignore_dir in ignore_dirs:
                if ignore_dir in dirs:
                    dirs.remove(ignore_dir)

            # dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file_to_check in files:
                file_type = file_types.find_extension(file_to_check)
                # for file_type in file_types.ft_list:
                if file_type:
                    if (file_to_check.lower()).endswith(f".{file_type.extension}"):
                        temp_outfile = file_type.extension + FLAT_FILE_SUFFIX
                        temp_outfile = os.path.join(FLAT_FILE_DATA_DIR, temp_outfile)
                        if not os.path.exists(temp_outfile):
                            startFile = open(temp_outfile, 'w+')
                            startFile.write(
                                    "Filename\t"
                                    "Hash\t"
                                    "FileSize\t"
                                    "Date\t"
                                    "FileType\t"
                                    "VolumeName\n")
                            startFile.close()
                        filename = os.path.join(paths, file_to_check)
                        with open(filename, 'rb') as file_to_hash:
                            file_hash = get_md5(file_to_hash)
                            file_stat = os.stat(filename)
                            timestamp = str(modification_date(filename))
                            file_size = str(file_stat.st_size/(1024*1024.0))
                            full_path = os.path.realpath(file_to_hash.name)
                            path_tags = [tag for tag in filter(None,full_path.split("/"))]
                            if float(file_type.min_size/(1024*1024.0)) < int(float(file_size)) or ALL_SIZES:
                                if file_hash not in pyfi_file_list.keys():
                                    pyfi_file_list[file_hash] = []
                                file_ref = pyfi_file_list[file_hash]
                                # filter if the same tags are found on same volume.
                                # indicating same file
                                existing =  [  (i['tags'],i['volume']) for i in file_ref ]
                                matches = [ tags for tags, volume in existing if path_tags == tags and volume_name == volume ]
                                if not matches:
                                # if file_list[file_hash]['tags'] != path_tags and file_list[file_hash]['volume'] == volume_name:
                                    file_ref.append({
                                            'tags': path_tags,
                                            'filename': str(path_tags[-1]),
                                            'md5hash': file_hash,
                                            'full_path': full_path,
                                            'volume': volume_name,
                                            'file_size': file_size,
                                            'timestamp': timestamp,
                                            'filetype': file_type[0],
                                            })
                                if sync_to_s3:
                                    # sync to s3 if option was selected.
                                    # use the file just added, since it's likely accessible
                                    # meta = pfu.parse_location_metadata(file_ref)
                                    sync_file_to_s3(file_ref[-1]) 
                                if sync_to_local_drive:
                                    # TODO
                                    # 
                                    # 
                                    # Add a sync to another drive here
                                    #
                                    sync_to_another_drive(file_ref[-1], local_target)
                                # if file_stat.st_size > min_file_size:
                                with open(temp_outfile, 'a+') as out_put_file:
                                    out_put_file.writelines(
                                        "{}\t{}\t{}\t{}\t{}\t{}\t{}\t\n".format(
                                            str(path_tags[-1]),
                                            filename,
                                            file_hash,
                                            file_size,
                                            timestamp,
                                            file_type[0],
                                            volume_name,

                                                )
                                )