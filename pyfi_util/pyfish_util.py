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
from filetypes.file_types import FilePropertySet
from shutil import copyfile
from pathlib import Path
import codecs
from pyfi_util.system_check import is_fs_case_sensitive
from pyfi_filestore.pyfish_file import PyfishFile, PyfishFileSet

from pyfi_util import pyfi_crypto as cr
ignore_dirs = IGNORE_DIRS
# LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
# utilLogger.basicConfig( filename='./logs/pyfi_util_log.txt', level=utilLogger.DEBUG,
        # format=LOG_FORMAT)
# utilLogger = utilLogger.getLogger()
utilLogger = logger

def get_all_files_from_target(target_folder="test"):
    """A new method of gathering all the files, instead of os.walk. Will only
    find names of files with a period in the name.
    TODO: find a way to use this to speed up the scan functions

    Keyword Arguments:
        target_folder {str} -- a folder on a volume to start from (default: {"test"})

    Returns:
        list -- list of Path based objects. of full path names.
        NOTE: str(result[x]) will reveal a string of the file's name for
        each file found.
    """
    if not target_folder:
        target_folder = 'test'
    result = []
    result = list(Path(target_folder).glob('**/*.*'))
    return result


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


def pyfi_file_builder(dict_record:dict):
    result = None
    try:
        md5Filehash = dict_record['md5FileHash']
        md5Name = dict_record['md5hash']
    except KeyError as e:
        print('File hash keys not present or not named correctly')
        md5Filehash = ""
        md5Name = ""

    try:
        full_path = Path(dict_record['full_path']).absolute()
        newPifiFile = PyfishFile(str(dict_record['volume']), str(full_path))
        clsAttributes = get_class_var_attributes(PyfishFile)
        for item in dict_record:
            try:
                if item in clsAttributes:
                    newPifiFile.__setattr__(str(item), dict_record[item])
            except KeyError as e:
                print(f"Key not found.  Will skip :{e}")
            except TypeError as e:
                print(f"Type in dictionary doesn't match the type the PyfishFile wants.  Will skip :{e}")
        if not newPifiFile.md5FileHash or not newPifiFile.md5Name:
            newPifiFile.open_and_get_info()
        result = newPifiFile
    except KeyError as e:
        print("required fields weren't provided.  Will return a type of None")

    return None if result is None else result

# def pyfi_file_builder(dict_record:dict):
#     try:
#         md5Filehash = dict_record['md5FileHash']
#         md5Name = dict_record['md5hash']
#     except KeyError as e:
#         print('File hash keys not present or not named correctly')
#         md5Filehash = ""
#         md5Name = ""

#     if md5Filehash:
#         try:
#             pfile = PyfishFile(
#                     volume=dict_record['volume'],
#                     full_path=dict_record['full_path'],
#                     md5FileHash=dict_record['md5FileHash'],
#                     md5Name=dict_record['md5Name'],
#                     file_type=dict_record['file_type'],
#                     known_name=dict_record['filename'],
#                     size_in_MB=dict_record['file_size'],
#                     inode=dict_record['inode'],
#                     tags=dict_record['tags'],
#                     timestamp=dict_record['timestamp'],
#             )
#         except KeyError as e:
#             print("Format of dictionary isn't compatible")
#     else:
#         try:
#             pfile = PyfishFile(
#                     volume=dict_record['volume'],
#                     full_path=dict_record['full_path'],
#                     md5FileHash=dict_record['md5FileHash']
#             )
#         except KeyError as e:
#             print(e)
#             print("Format of dictionary isn't compatible")
            


def load_pyfish_data():
    file_list = _load_saved_file_list(JSON_FILE_PATH)
    return file_list


def build_stats_dict(file_list):
    """function to take the pyfi data and return a dict grouped on
    elements, mainly the md5 sum

    Arguments:
        file_list {dict} -- the primary json-like dict that pyfy creates

    Returns:
        dict - a dictionary of stats for each md5 sum
    """
    stats = {}
    for key in file_list:
        stats[key] = stats.pop(key, None)
        if stats[key] is None:
            stats[key] = {}
        stats[key]['files'] = file_list[key]
        stats[key]['copies'] = len(file_list[key])
        stats[key]['md5'] = key
    return stats

def build_multiple_dict(file_list):
    """Filter the stats data, so that only hashes with multiple locations are found

    Arguments:
        file_list {dict} -- the primary json-like dict that pyfy creates

    Returns:
        stats file with only duplicates.
    """
    stats = build_stats_dict(file_list)
    multi = [
            stats[dups] for dups in stats if stats[dups]['copies'] > 1
        ]
    return multi


def get_files_missing_from_a_volume(file_list:dict, vol:str):
    data = file_list if file_list else load_pyfish_data()
    unique_set = [ (i, set([v['volume'] for v in data[i] ])) for i in data ]
    set_minus_volume = [ i for i in unique_set if str(vol) not in i[1] ]
    return set_minus_volume

def get_files_from_one_vol(file_list:dict, vol:str):
    new_data = {}
    data = file_list if file_list else load_pyfish_data()
    for md5 in data:
        for i in range(0,len(data[md5])):
            if data[md5][i]['volume'] == vol:
                try:
                    new_data[md5].append(data[md5][i])
                except KeyError:
                    new_data[md5] = []
                    new_data[md5].append(data[md5][i])


    return new_data


def get_current_volumes(data=None):
    """From a File-list, parse and look for volumes that have been
    used.

    Returns:
        set -- a set of unique strings of names of volumes
    """

    return get_unique_volumes_from_data(data)


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


def sync_to_another_drive(file_ref_to_add, target):
    """Copy file to a local drive.

    Arguments:
        file_ref_to_add {dict} -- a referecne to a record (dict)
        from the pyfile_file lsit.  This will be used to referece the file
        that must be coppied
    """
    # set the variables

    # make sure the target is the real path, not a symlink
    # BUG: the target is getting tranlated to the relative temp folder, not the "temp" folder
    # that I passed it.
    target = os.path.realpath(target)

    # just choose one of the paths to sync
    data_file_ref = file_ref_to_add[-1]

    # get all paths in the file ref record to add to manifest.
    all_paths = sorted([ i['full_path'] for i in file_ref_to_add ])

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
        try:
            copyfile(os.path.realpath(full_path), full_path_dest_file)
        except FileNotFoundError:
            logger.warn(f"The file '{full_path}' could not be found.  Skipping the sync to local drive")
            pass

    if os.path.exists(full_path_mainfest):
        utilLogger.debug("file mainifest exists. will copy to local temp, update the paths, and copy back to destination")
        copyfile(full_path_mainfest, os.path.join(temp_folder, manifest_file_name))
        add_location_to_file_manifest(os.path.join(temp_folder, manifest_file_name),volume_name, all_paths)
        copyfile(os.path.join(temp_folder, manifest_file_name), full_path_mainfest)
        os.remove(os.path.join(temp_folder, manifest_file_name))
    else:
        temp_manifest = create_manifest(volume_name, all_paths)
        with open(os.path.join(temp_folder,manifest_file_name), 'w+') as temp_json:
            json.dump(temp_manifest, temp_json)
        copyfile(os.path.join(temp_folder, manifest_file_name), full_path_mainfest)
        os.remove(os.path.join(temp_folder, manifest_file_name))


def sync_file_to_s3(file_record:dict, meta=None):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file
        that will need to checked and possibly uploaded
    """


    file_path = file_record['full_path']

    sub_path,extention,name_to_store = build_relative_destination_path(file_record)
    temp_folder = 'temp/'
    volume_name = f"{file_record['volume']}"
    full_path = f"{file_record['full_path']}"
    # name_to_store = f"{file_record['md5hash']}"
    # extention = f"{file_record['filetype']}"
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

def sync_file_to_s3_new(file_record:PyfishFile, meta=None):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file
        that will need to checked and possibly uploaded
    """
    use_encryption = False
    try:
        use_encryption = file_record.encrypt_remote
        logger.info('Encrypting the remote file was requested')
    except KeyError as e:
        logger.info("File record doesn't have a 'encrypt_remote' directive")
    
    temp_folder = 'temp/'
    volume_name = file_record.volume
    
    if use_encryption:
        pass
    else:
        file_path = file_record.full_path
        # sub_path,extention,name_to_store = build_relative_destination_path(file_record)
        
        extention = f"{file_record.file_type}"
        name_to_store = f"{file_record.md5Name}"
        sub_path = f"{extention}/{name_to_store}"
    
    
    
    
    # name_to_store = f"{file_record['md5hash']}"
    # extention = f"{file_record['filetype']}"
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
        utilLogger.info(msg="manifest files exists. Will download, update, and upload")
        s3client.download_file_to_temp(s3_manifest_file, s3_key_manifest, temp_folder)
        decrypt_file(s3_manifest_file, temp_folder)
        add_location_to_file_manifest(os.path.join(
                temp_folder, s3_manifest_file),volume_name, file_record.full_path)
        # s3client.upload_file(os.path.join(temp_folder,s3_manifest_file), s3_key_manifest)
    else:
        # no manifest found.  Create and upload it
        temp_manifest = create_manifest(volume_name, file_record.full_path)
        with open(os.path.join(temp_folder,s3_manifest_file), 'w+') as temp_json:
            json.dump(temp_manifest, temp_json)
        # s3client.upload_file(os.path.join(temp_folder,s3_manifest_file), s3_key_manifest)
    # in either case, upload the file
    s3client.upload_file(os.path.join(temp_folder,s3_manifest_file), s3_key_manifest)

def decrypt_file(file, source_folder, compression=True):
    path = Path(source_folder).absolute()
    full_path = path.joinpath(f"{file}.encrypted")
    out_file = path.joinpath(file)
    dcrypt_data = cr.convert_encrypted_file_into_decrypted_data(full_path, compression=compression)
    with open(out_file, 'wb+') as manifest:
        manifest.write(dcrypt_data)
    os.remove(full_path)

def encrypt_file(file, dest_folder, compression=True):
    path = Path(dest_folder).absolute()
    full_path = path.joinpath(file)
    out_file = path.joinpath(f"{file}.encrypted")
    ncrypt_data = cr.convert_file_into_encrypted_data(full_path, compression=compression)
    with open(out_file, 'wb+') as manifest:
        manifest.write(ncrypt_data)
    


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
    update the details, and re-upload it.
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






def get_unique_volumes_from_data(data:list=None):
    """Get all the volume names stored in a data_set

    Arguments:
        file_list {list of dict} -- pyfi data from json store

    Returns:
        list -- list of string names of volumes found.
    """
    file_list = data if data else load_pyfish_data()
    volumes = set()
    for md5 in file_list:
        for item in file_list[md5]:
            volumes.add(item['volume'])

    return volumes


def get_unique_files_totalsize(data=None, vol=""):
    """return the sum of MB stored in a pyfish file list

    Arguments:
        filelist {dict} -- file_list as created by pyfish.
        may also be loaded form a json_data.json that is
        created and loaded by pyfish

    Returns:
        float -- sum of only the first instace for each unique
        file.
    """

    if not data:
        data = load_pyfish_data()

    filelist = []
    if vol:
        filelist = get_files_from_one_vol(data,vol)
    else:
        filelist = data

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

    # fill a new  file list with only records with the chosen volume and types
    for md5 in file_list:
        for record in file_list[md5]:
            if record['volume'] == volume_name and record['filetype'] in file_type_list:
                try:
                    new_file_list[md5].append(record)
                except KeyError:
                    new_file_list[md5] = [record]


    for md5 in new_file_list:
        # for each item in new_file_list, sync to the target
        sync_to_another_drive(new_file_list[md5], local_target)




def build_file_reference():
    pass

def write_data_to_json_log(pyfi_file_list:list, json_file_path=JSON_FILE_PATH_TEMP):
    """dump the file list to a file

    Arguments:
        pyfi_file_list {list} -- list of files and details

    Keyword Arguments:
        json_file_path {string} -- path defaults to the temp location.
        so that if the app stops while writing, the primary json data
        will not be lost (default: {JSON_FILE_PATH_TEMP})
    """
    with codecs.open(
            json_file_path, 'w+', encoding='utf-8'
            ) as json_out:
        json_out.write(
                json.dumps(pyfi_file_list, sort_keys=True, ensure_ascii=False))


def get_match_details(file_ref):
    """gernate a list of tuples to use to check against a file being checked
    to see if it has already been added.  inode was added in a later version
    , so this accounts for a KeyError, and returns a -1 if there is no key.
    Also, contains the index for the data, so that it can be updated.
    TODO: ensure this works on Windows OS.

    Arguments:
        file_ref {list of dict} -- file data loaded from pyfi json files

    Returns:
        tuple -- tags(represending a file path), volume the file is found on,
        and if available in the data, the inode. -1 if inode key isn't in the dict.
    """
    existing = []
    for i in file_ref:
        try:
            existing.append((i['tags'],i['volume'],i['inode'], file_ref.index(i)))
        except KeyError:
            existing.append((i['tags'],i['volume'],-1, file_ref.index(i)))

    if not existing:
        existing = [([],"",-1, 0)]
    return existing



def scan_for_files(pyfi_file_list:list, folder, file_types:FilePropertySet, volume_name, sync_to_s3, sync_to_local_drive, load_external:bool=LOAD_EXTERNAL, local_target=None):

        print(f"Start Time: {str(datetime.datetime.now().time())}")

        ## setup some environment stuff
        os.makedirs(FLAT_FILE_DATA_DIR, exist_ok=True)
        file_list_changed = False
        case_sensitive = is_fs_case_sensitive()
        # loop over the designated folder, and but stop to remove dirs that are not to be searched.
        for (paths, dirs, files) in os.walk(folder, topdown=True):
            if file_list_changed:
                write_data_to_json_log(pyfi_file_list=pyfi_file_list)
                file_list_changed = False
            for ignore_dir in ignore_dirs:
                if ignore_dir in dirs:
                    dirs.remove(ignore_dir)

            # dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file_to_check in files:
                file_type = file_types.find_extension(file_to_check)
                # for file_type in file_types.ft_list:
                if file_type:
                    if (file_to_check.lower()).endswith(f".{file_type.extension}"):
                        filename = os.path.join(paths, file_to_check)
                        with open(filename, 'rb') as file_to_hash:
                            file_hash = get_md5(file_to_hash)
                            file_stat = os.stat(filename)
                            timestamp = str(modification_date(filename))
                            file_size = str(file_stat.st_size/(1024*1024.0))
                            file_inode = str(file_stat.st_ino)
                            # account for slopy case sesitivity practices in windows
                            full_path_for_parts = str(os.path.realpath(file_to_hash.name)).lower() if not case_sensitive else str(os.path.realpath(file_to_hash.name))
                            full_path = str(os.path.realpath(file_to_hash.name))
                            # path_tags = [tag for tag in filter(None,full_path.split("/"))]
                            path_tags = [ tag for tag in filter(None, Path(full_path_for_parts).parts)]
                            if float(file_type.min_size)/(1024*1024.0) < int(float(file_size)) or ALL_SIZES:
                                if file_hash not in pyfi_file_list.keys():
                                    pyfi_file_list[file_hash] = []
                                    file_list_changed = True
                                file_ref = pyfi_file_list[file_hash]
                                # filter if the same tags are found on same volume.
                                # indicating same file
                                if file_ref:
                                    existing = get_match_details(file_ref)

                                    matches = [ tags for tags, volume, inode, index in existing if path_tags == tags and volume_name == volume and inode == file_inode  ]
                                    missing_inode_indexes = [ index for tags,volume,inode,index in existing if path_tags == tags and volume_name == volume ]
                                else:
                                    # don't bother if no data in file_ref
                                    existing = []
                                    matches = []
                                    missing_inode_indexes = []
                                if not matches and missing_inode_indexes:
                                    # update the file where indexes are found for matching volumes and tags but
                                    # the inode wasn't stored.  Assmuming a lot about the user, and the knowledge here.
                                    # this should be removed in the future, since it shouldn't be needed.
                                    # just  patch for fixing old data that's already been generated, so I don't need
                                    # to go back and rescan volumes for now.
                                    for index in missing_inode_indexes:
                                        file_ref[index]['inode'] = file_inode
                                elif not matches:
                                    # assume that the file locations is brand new, and add it to the list.
                                    file_ref.append({
                                            'tags': path_tags,
                                            'filename': str(path_tags[-1]),
                                            'md5hash': file_hash,
                                            'full_path': full_path,
                                            'volume': volume_name,
                                            'file_size': file_size,
                                            'timestamp': timestamp,
                                            'filetype': file_type[0],
                                            'inode': file_inode,
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
                                    sync_to_another_drive(file_ref, local_target)
                                # if file_stat.st_size > min_file_size:
                            
                                if WRITE_OUT_FLAT:
                                    temp_outfile = file_type.extension + FLAT_FILE_SUFFIX
                                    temp_outfile = os.path.join(FLAT_FILE_DATA_DIR, temp_outfile)
                                    if not os.path.exists(temp_outfile):
                                        """create a header row if file doesn't exist
                                        """
                                        startFile = open(temp_outfile, 'w+')
                                        startFile.write(
                                                "Filename\t"
                                                "Hash\t"
                                                "FileSize\t"
                                                "Date\t"
                                                "FileType\t"
                                                "inode\t"
                                                "VolumeName\n")
                                        startFile.close()
                                    
                                    with open(temp_outfile, 'a+') as out_put_file:
                                        out_put_file.writelines(
                                            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t\n".format(
                                                str(path_tags[-1]),
                                                filename,
                                                file_hash,
                                                file_size,
                                                timestamp,
                                                file_type[0],
                                                file_inode,
                                                volume_name,
                                                    )
                                        )


def get_class_var_attributes(cls:object):
    clsItems = cls._attributes
    # filtered_attributes = [ i[0] for i in clsItems if not i[0].startswith('__') and not callable(i[1]) ]
    return clsItems