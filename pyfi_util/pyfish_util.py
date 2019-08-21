# from pyfi import load_saved_file_list
# from pyfi  JSON_FILE_PATH
from s3_integration.s3_tools import S3Connection
import os

# import logging as logger
from collections import defaultdict
import json
from settings import (
    TEMP_FOLDER,
    IGNORE_DIRS,
    logger,
    JSON_FILE_PATH,
    FLAT_FILE_DATA_DIR,
    ALL_SIZES,
    WRITE_OUT_FLAT,
    FLAT_FILE_SUFFIX,
    JSON_FILE_PATH_TEMP,
    TBD_PATH,
    LOAD_EXTERNAL,
)
from hashlib import md5
import datetime
from filetypes.file_types import FilePropertySet
from shutil import copyfile
from pathlib import Path
import codecs
from pyfi_util.system_check import is_fs_case_sensitive
from pyfi_filestore.pyfish_file import PyfishFile
from collections import OrderedDict

from pyfi_util import pyfi_crypto as cr

ignore_dirs = IGNORE_DIRS
# LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
# logger.basicConfig( filename='./logs/pyfi_util_log.txt', level=logger.DEBUG,
#                     format=LOG_FORMAT)
# logger = logger.getLogger()
# logger = logger


def get_all_files_from_target(target_folder="tests/test_files"):
    """A new method of gathering all the files, instead of os.walk. Will only
    find names of files with a period in the name.
    TODO: find a way to use this to speed up the scan functions

    Keyword Arguments:
        target_folder {str} -- a folder on a volume to
                               start from (default: {"test"})

    Returns:
        list -- list of Path based objects. of full path names.
        NOTE: str(result[x]) will reveal a string of the file's name for
        each file found.
    """
    if not target_folder:
        target_folder = "test"
    result = []
    result = list(Path(target_folder).glob("**/*.*"))
    return result


def _load_saved_file_list(json_file_path):
    """
    loads the json file that has previously found files
    """
    external_file_list = OrderedDict()
    try:
        with open(json_file_path, "r") as json_data:
            external_file_list = json.load(json_data)
            logger.info(
                f"found the json file and loaded saved data \
                          from {json_file_path}"
            )
    except FileNotFoundError as e:
        logger.info(f"Warning: {e.strerror}")
        logger.info(f"Info: Missing {json_file_path}")
        logger.info(
            "Info: This is normal, if this is a first run of \
            the program."
        )
        logger.info(
            f"{json_file_path} was not found. A new file will \
            be created"
        )
    return external_file_list


def pyfi_file_builder(dict_record: dict):
    result = None
    try:
        md5hash = dict_record["md5hash"]  # noqa
        remote_name_hash = dict_record["remote_name_hash"]  # noqa
    except KeyError:
        logger.debug("File hash keys not present or not named correctly")
    try:
        full_path = Path(dict_record["full_path"]).absolute()
        newPifiFile = PyfishFile(str(dict_record["volume"]), str(full_path))
        clsAttributes = get_class_var_attributes(PyfishFile)
        for item in dict_record:
            try:
                if item in clsAttributes:
                    newPifiFile.__setattr__(str(item), dict_record[item])
            except KeyError as e:
                logger.debug(f"Key not found.  Will skip :{e}")
            except TypeError as e:
                logger.debug(
                    f"Type in dictionary doesn't match the type \
                               the PyfishFile wants.  Will skip :{e}"
                )
        if not newPifiFile.md5hash or not newPifiFile.remote_name_hash:
            newPifiFile.open_and_get_info()
        result = newPifiFile
    except KeyError:
        logger.warn(
            "required fields weren't provided.  Will return a type of None"
        )

    return None if result is None else result


def load_pyfish_data(md5hash=""):
    """Load all data from the JSON data file

    Keyword Arguments:
        md5hash {str} -- If a hash is provided, us it to filter only for \
                         that file (default: {""})

    Returns:
        dict -- The whole list of files
    """

    file_list = _load_saved_file_list(JSON_FILE_PATH)
    if md5hash:
        try:
            return file_list[md5hash]
        except KeyError as e:
            logger.debug(e)
            logger.debug(f"MD5 value {md5hash} couldn't be found in data")
            file_list = None
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
        stats[key]["files"] = file_list[key]
        stats[key]["copies"] = len(file_list[key])
        stats[key]["md5"] = key
    return stats


def build_multiple_dict(file_list):
    """Filter the stats data, so that only hashes with multiple locations are found

    Arguments:
        file_list {dict} -- the primary json-like dict that pyfy creates

    Returns:
        stats file with only duplicates.
    """
    stats = build_stats_dict(file_list)
    multi = [stats[dups] for dups in stats if stats[dups]["copies"] > 1]
    return multi


def get_files_missing_from_a_volume(file_list: dict, vol: str):
    data = file_list if file_list else load_pyfish_data()
    unique_set = [(i, set([v["volume"] for v in data[i]])) for i in data]
    set_minus_volume = [i for i in unique_set if str(vol) not in i[1]]
    return set_minus_volume


def get_files_from_one_vol(
    file_list: dict, vol: str, file_types: FilePropertySet = None
):  # noqa
    new_data = {}
    data = file_list if file_list else load_pyfish_data()
    for hashsum in data:
        for i in range(0, len(data[hashsum])):
            if file_types:
                if data[hashsum][i][
                    "volume"
                ] == vol and file_types.find_extension(
                    data[hashsum][i]["filetype"]
                ):  # noqa
                    try:
                        new_data[hashsum].append(data[hashsum][i])
                    except KeyError:
                        new_data[hashsum] = []
                        new_data[hashsum].append(data[hashsum][i])
            else:
                if data[hashsum][i]["volume"] == vol:
                    try:
                        new_data[hashsum].append(data[hashsum][i])
                    except KeyError:
                        new_data[hashsum] = []
                        new_data[hashsum].append(data[hashsum][i])
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
        dict -- converted defaultdict, grouped by volume. Will have at
                least one full path name for the file on the volume,
                but could be a list of them per
                volume if there is more than one on a volume.
    """

    try:
        volumes_and_files = [(i["volume"], i["full_path"]) for i in file_ref]
        if volumes_and_files:
            files_grouped_by_volume = defaultdict(list)
            [
                files_grouped_by_volume[volumeName].append(filename)
                for volumeName, filename in volumes_and_files
            ]
            [i.encode("utf-8") for i in files_grouped_by_volume]
            locations = dict(files_grouped_by_volume.items())
            result = {"Metadata": {"Locations": locations}}

    except KeyError as e:
        logger.error(
            f"Encountered error parsing location metadata. Error: {e}"
        )
        result = None
    return result


def build_relative_destination_path(pyfish_file_ref):
    """form the path used to store the file, including shared sub
    directories based on file_type. The files being synced from any
    volume should be able to use this path to see if the file, named
    as <remote_name_hashOfFile>.<extension> exists already.

    Arguments:
        pyfish_file_ref {[type]} -- [description]

    Returns:
        [tuple] -- relative path to use for building a
                   destination form the root of the store,
                   file type,
                   md5 name, for local storage, unencrypted storage.
    """
    if isinstance(pyfish_file_ref, dict):
        pyfish_file_ref: PyfishFile = PyfishFile.from_dict(pyfish_file_ref)
    path = f"{pyfish_file_ref.filetype}/{pyfish_file_ref.md5hash}/"

    return (path, pyfish_file_ref.filetype, pyfish_file_ref.md5hash)


def build_relative_destination_path_remote(pyfish_file_ref):
    """form the path used to store the file, including shared sub
    directories based on file_type. The files being synced from any
    volume should be able to use this path to see if the file, named
    as <remote_name_hashOfFile>.<extension> exists already.

    Arguments:
        pyfish_file_ref {[type]} -- [description]

    Returns:
        [tuple] -- relative path to use for building a destination form
                   the root of the store,
                   file type,
                   remote hash name, not the name of the hash.
    """

    path = f"{pyfish_file_ref.filetype}/{pyfish_file_ref.remote_name_hash}/"

    return (path, pyfish_file_ref.filetype, pyfish_file_ref.remote_name_hash)


def sync_to_another_drive(file_ref_to_add, target):
    """Copy file to a local drive.

    Arguments:
        file_ref_to_add {dict} -- a reference to a record (dict)
        from the pyfile_file list.  This will be used to reference the file
        that must be coppied
    """
    # set the variables

    # make sure the target is the real path, not a symlink
    # BUG: the target is getting tranlated to the relative temp folder,
    # not the "temp" folder
    # that I passed it.
    target = os.path.realpath(target)

    # just choose one of the paths to sync
    data_file_ref = file_ref_to_add[-1]

    # get all paths in the file ref record to add to manifest.
    all_paths = sorted([i["full_path"] for i in file_ref_to_add])

    sub_path, extention, remote_name_hash = build_relative_destination_path(
        data_file_ref
    )
    temp_folder = TEMP_FOLDER
    os.makedirs(temp_folder, exist_ok=True)
    volume_name = f"{data_file_ref['volume']}"
    full_path = f"{data_file_ref['full_path']}"
    name_to_store = f"{remote_name_hash}.{extention}"
    relative_dst_file = os.path.join(sub_path, name_to_store)
    manifest_file_name = f"{remote_name_hash}.manifest.json"
    relative_manifest_file = f"{os.path.join(sub_path, manifest_file_name)}"
    full_path_mainfest = f"{os.path.join(target, relative_manifest_file)}"
    full_path_dest_file = f"{os.path.join(target, relative_dst_file)}"

    # make the dir, incase is doesn't exists.
    os.makedirs(os.path.join(target, sub_path), exist_ok=True)

    # copy the file if doesn't already exist
    if os.path.exists(full_path_dest_file):
        logger.debug(f"{name_to_store} already exists.  Not updating")
    else:
        try:
            copyfile(os.path.realpath(full_path), full_path_dest_file)
        except FileNotFoundError:
            logger.warn(
                f"The file '{full_path}' could not be found.  \
                Skipping the sync to local drive"
            )
            pass

    if os.path.exists(full_path_mainfest):
        logger.debug(
            "file manifest exists. will copy to local temp, update \
                      the paths, and copy back to destination"
        )
        copyfile(
            full_path_mainfest, os.path.join(temp_folder, manifest_file_name)
        )
        add_location_to_file_manifest(
            os.path.join(temp_folder, manifest_file_name),
            volume_name,
            all_paths,
        )
        copyfile(
            os.path.join(temp_folder, manifest_file_name), full_path_mainfest
        )
        os.remove(os.path.join(temp_folder, manifest_file_name))
    else:
        temp_manifest = create_manifest(volume_name, all_paths)
        with open(
            os.path.join(temp_folder, manifest_file_name), "w+"
        ) as temp_json:
            json.dump(temp_manifest, temp_json)
        copyfile(
            os.path.join(temp_folder, manifest_file_name), full_path_mainfest
        )
        os.remove(os.path.join(temp_folder, manifest_file_name))


def sync_file_to_s3(file_record: dict, meta=None):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file
        that will need to checked and possibly uploaded
    """

    file_path = file_record["full_path"]

    sub_path, extention, name_to_store = build_relative_destination_path(
        file_record
    )
    temp_folder = TEMP_FOLDER
    volume_name = f"{file_record['volume']}"
    full_path = f"{file_record['full_path']}"
    # name_to_store = f"{file_record['remote_name_hash']}"
    # extention = f"{file_record['filetype']}"
    s3_key = f"{sub_path}{name_to_store}.{extention}"
    s3_manifest_file = f"{name_to_store}.manifest.json"
    s3_key_manifest = f"{sub_path}{s3_manifest_file}"

    # make sure the files is there, or upload it if not
    s3client = S3Connection()
    bucket_name = os.getenv("ACTIVE_BUCKET_NAME")
    s3client.set_active_bucket(bucket_name)
    if s3_key in s3client.get_keynames_from_objects(bucket_name):
        logger.warning(
            msg="key found in objects already. Will not upload by default"
        )
    else:
        try:
            s3client.upload_file(file_path, s3_key, metadata=meta)
        except Exception as e:
            logger.error(e)

    # update or create a manifest to store as well
    if s3_key_manifest in s3client.get_keynames_from_objects(bucket_name):
        logger.info(
            msg="manifest files exists. Will download, update, and upload"
        )
        s3client.download_file_to_temp(
            s3_manifest_file, s3_key_manifest, temp_folder
        )
        add_location_to_file_manifest(
            os.path.join(temp_folder, s3_manifest_file), volume_name, full_path
        )
    else:
        # no manifest found.  Create and upload it
        temp_manifest = create_manifest(volume_name, full_path)
        with open(
            os.path.join(temp_folder, s3_manifest_file), "w+"
        ) as temp_json:
            json.dump(temp_manifest, temp_json)
    # in either case, upload the file
    s3client.upload_file(
        os.path.join(temp_folder, s3_manifest_file), s3_key_manifest
    )


def sync_file_to_s3_new(file_record: PyfishFile, meta=None, encrypt_all=True):
    """take the object used by pyfish, and translate for S3 upload

    Arguments:
        file_ref {dict} -- dictionary with details of the file
        that will need to checked and possibly uploaded
    """
    if isinstance(file_record, dict):
        try:
            file_record = PyfishFile.from_dict(file_record)
            file_record.open_and_get_info()
        except TypeError as e:
            logger(e)
            logger.error(
                "quiting due to type problem.  dict can't be converted"
            )
            logger.error(
                f"file {file_record.full_path} is not going \
                    to be synced to s3"
            )
    elif not isinstance(file_record, PyfishFile):
        logger.critical(
            f"this is not good. attempt to use type \
                {type(file_record)} as a PyfishFile. \
                Something has gone very wrong"
        )
        raise TypeError(
            f"Attempted to use type of {type(file_record)} as a PyfishFile"
        )
    else:
        file_record.open_and_get_info()
    use_encryption = False
    try:
        use_encryption = file_record.encrypt_remote
        logger.info("Encrypting the remote file was requested")
    except KeyError:
        logger.info("File record doesn't have a 'encrypt_remote' directive")
    if encrypt_all:
        # overide the file record setting and encrypt
        use_encryption = True
        logger.info("'encrypt all' setting used, overriding file settings")
    else:
        pass  # use the preference of the file.

    # Setup variables
    temp_folder = TEMP_FOLDER
    volume_name = file_record.volume
    tmp_file_path = file_record.full_path
    filename = file_record.filename
    extention = f"{file_record.filetype}"
    name_to_store = f"{file_record.remote_name_hash}"
    sub_path = f"{extention}/{name_to_store}"
    enc = ".encrypted" if use_encryption else ""
    s3_key = f"{sub_path}/{name_to_store}.{extention}{enc}"
    s3_manifest_file = f"{name_to_store}.manifest.json"
    s3_key_manifest = f"{sub_path}/{s3_manifest_file}{enc}"
    s3client = S3Connection()
    bucket_name = os.getenv("ACTIVE_BUCKET_NAME")
    s3client.set_active_bucket(bucket_name)

    # make sure the files is there, or upload it
    # using preferred encryption setting if not found.
    # Note: this is the heart of the syncing logic
    if s3_key in s3client.get_keynames_from_objects(bucket_name):
        logger.warning(
            msg="key found in objects already. \
                            Will not upload by default"
        )
    else:
        try:
            if use_encryption:
                encrypt_file(file_record.full_path, TEMP_FOLDER)
                tmp_file_path = "".join(
                    [TEMP_FOLDER, "/", filename, ".encrypted"]
                )
            else:
                pass  # no encryption
            s3client.upload_file(tmp_file_path, s3_key, metadata=meta)
        except Exception as e:
            logger.error(e)

    # update or create a manifest to store as well f"{s3_manifest_file}{enc}"
    if s3_key_manifest in s3client.get_keynames_from_objects(bucket_name):
        logger.info(
            msg="manifest files exists. Will download, update,\
                         and upload"
        )
        s3client.download_file_to_temp(
            f"{s3_manifest_file}{enc}", s3_key_manifest, TEMP_FOLDER
        )
        if use_encryption:
            decrypt_file(f"{s3_manifest_file}{enc}", TEMP_FOLDER)
        add_location_to_file_manifest(
            os.path.join(TEMP_FOLDER, s3_manifest_file),
            volume_name,
            [file_record.full_path],
        )
    else:
        # no manifest found.  Create and upload it
        temp_manifest = create_manifest(volume_name, [file_record.full_path])
        with open(
            os.path.join(TEMP_FOLDER, s3_manifest_file), "w+"
        ) as temp_json:
            json.dump(temp_manifest, temp_json)

    # in either case, upload the file
    if use_encryption:
        encrypt_file(os.path.join(TEMP_FOLDER, s3_manifest_file), TEMP_FOLDER)
        s3_manifest_file = f"{s3_manifest_file}{enc}"
    s3client.upload_file(
        os.path.join(temp_folder, s3_manifest_file), s3_key_manifest
    )


def decrypt_file(
    file, source_folder, dest_folder="", compression=True, remove_src=False
):
    dest_folder = dest_folder if dest_folder else source_folder
    dest_path = Path(dest_folder).absolute()
    src_path = Path(source_folder).absolute()
    full_path = src_path.joinpath(f"{file}")
    # the file may not end with the encrypted string, so check first
    if str(file).endswith(".encrypted"):
        file = "".join(str(file).split(".encrypted")[:-1])
    out_file = dest_path.joinpath(file)
    dcrypt_data = cr.convert_encrypted_file_into_decrypted_data(
        full_path, compression=compression
    )
    with open(out_file, "wb+") as ofile:

        ofile.write(dcrypt_data)
    if remove_src:
        os.remove(full_path)


def encrypt_file(file, dest_folder, compression=True):

    dest_path = Path(dest_folder).absolute()
    full_path = Path(file).absolute()
    file_name = full_path.name
    out_file = dest_path.joinpath(f"{file_name}.encrypted")
    ncrypt_data = cr.convert_file_into_encrypted_data(
        full_path, compression=compression
    )
    with open(out_file, "wb+") as ofile:
        ofile.write(ncrypt_data)


def create_manifest(volume_name, locations, added_path=""):
    """make a dict that contains all known locations of a file.
    To be stored with the file. Data will come from an existing record,
    so this is just meant to format for the json file to store.

    Arguments:
        volume_name {str} -- volume or drive where data is found
        locations {[type]} -- ll the locations already known

    Keyword Arguments:
        path {str} -- Path to join to each location. Will be relative if not provided. (default: {""})

    Returns:
        [dict] -- dict of file locations, grouped by volume


    Returns:

    """
    path_list = []
    if isinstance(locations, list):
        path_list = locations
    else:
        # if it's just one string, make it a list for the loop
        path_list = list([locations])
    manifest = {}
    volume_name = volume_name
    manifest["locations"] = {}
    manifest["locations"][volume_name] = []
    for file_name in path_list:
        manifest["locations"][volume_name].append(
            os.path.join(added_path, file_name)
        )
    return manifest


def add_location_to_file_manifest(
    manifest_file_name, location_volume, location_paths
):
    """take details of a files location, the location of it's temporary  manifest, read the manifest
    into a dict, update wih new location, and save a new version of the manifest.
    """
    manifest_file_data = manifest_file_name
    all_paths = list(location_paths)
    manifest = None
    try:
        with open(manifest_file_data, "rb") as tmpjson:
            manifest = json.load(tmpjson)
        try:
            for location_path in all_paths:
                files = manifest["locations"][location_volume]
                try:
                    files.remove(location_path)
                except ValueError as e:
                    # path doesn't already exists
                    pass
                files.append(location_path)
                files.sort()
                manifest["locations"][location_volume] = files

        except KeyError as e:
            manifest["locations"][location_volume] = [location_path]

        # after the key for the volume has been updated, write the file over
        # again
        with open(manifest_file_data, "w+") as temp_out:
            json.dump(manifest, temp_out)

    except FileExistsError as e:
        logger.warn(e)
        logger.warn("unable to access the file path provided")


def get_unique_volumes_from_data(data: list = None):
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
            volumes.add(item["volume"])

    return volumes


def get_unique_files_totalsize(data=None, vol="", file_type=""):
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
        filelist = get_files_from_one_vol(data, vol, file_type)
    else:
        filelist = data

    return sum([float(filelist[i][0]["file_size"]) for i in filelist])


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


def only_sync_file(local_target="temp", volume_name="", file_types=[]):
    file_list = load_pyfish_data()
    new_file_list = {}
    file_type_list = [i.extension for i in file_types.ft_list]

    # fill a new  file list with only records with the chosen volume and types
    for md5 in file_list:
        for record in file_list[md5]:
            if (
                record["volume"] == volume_name
                and record["filetype"] in file_type_list
            ):
                try:
                    new_file_list[md5].append(record)
                except KeyError:
                    new_file_list[md5] = [record]

    for md5 in new_file_list:
        # for each item in new_file_list, sync to the target
        sync_to_another_drive(new_file_list[md5], local_target)


def build_file_reference():
    pass


def write_data_to_json_log(
    pyfi_file_list: list, json_file_path=JSON_FILE_PATH_TEMP
):
    """dump the file list to a file

    Arguments:
        pyfi_file_list {list} -- list of files and details

    Keyword Arguments:
        json_file_path {string} -- path defaults to the temp location.
        so that if the app stops while writing, the primary json data
        will not be lost (default: {JSON_FILE_PATH_TEMP})
    """
    with codecs.open(json_file_path, "w+", encoding="utf-8") as json_out:
        json_out.write(
            json.dumps(pyfi_file_list, sort_keys=True, ensure_ascii=False)
        )


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
            existing.append(
                (i["tags"], i["volume"], i["inode"], file_ref.index(i))
            )
        except KeyError:
            existing.append((i["tags"], i["volume"], -1, file_ref.index(i)))

    if not existing:
        existing = [([], "", -1, 0)]
    return existing


def scan_for_files(
    pyfi_file_list: list,
    folder,
    file_types: FilePropertySet,
    volume_name,
    sync_to_s3,
    sync_to_local_drive,
    load_external: bool = LOAD_EXTERNAL,
    local_target=None,
):
    """
    scan a drive and location for files
    """
    print(f"Start Time: {str(datetime.datetime.now().time())}")
    logger.info(f"Start Time: {str(datetime.datetime.now().time())}")

    # setup some environment stuff
    os.makedirs(FLAT_FILE_DATA_DIR, exist_ok=True)
    file_list_changed = False
    case_sensitive = is_fs_case_sensitive()
    # loop over the designated folder, and but stop to remove dirs that are
    # not to be searched.
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
                    with open(filename, "rb") as file_to_hash:
                        file_hash = get_md5(file_to_hash)
                        file_stat = os.stat(filename)
                        timestamp = str(modification_date(filename))
                        file_size = str(
                            round(file_stat.st_size / (1024 * 1024.0), 5)
                        )
                        file_inode = str(file_stat.st_ino)
                        # account for sloppy case sensitivity practices in
                        # windows
                        full_path_for_parts = (
                            str(os.path.realpath(file_to_hash.name)).lower()
                            if not case_sensitive
                            else str(os.path.realpath(file_to_hash.name))
                        )
                        full_path = str(os.path.realpath(file_to_hash.name))
                        # path_tags = [tag for tag in filter(None,full_path.split("/"))]
                        path_tags = [
                            tag
                            for tag in filter(
                                None, Path(full_path_for_parts).parts
                            )
                        ]
                        if (
                            float(file_type.min_size) / (1024 * 1024.0)
                            < int(float(file_size))
                            or ALL_SIZES
                        ):
                            if file_hash not in pyfi_file_list.keys():
                                pyfi_file_list[file_hash] = []
                                file_list_changed = True
                            file_ref = pyfi_file_list[file_hash]
                            # filter if the same tags are found on same volume.
                            # indicating same file
                            if file_ref:
                                existing = get_match_details(file_ref)

                                matches = [
                                    tags
                                    for tags, volume, inode, index in existing
                                    if path_tags == tags
                                    and volume_name == volume
                                    and inode == file_inode
                                ]
                                missing_inode_indexes = [
                                    index
                                    for tags, volume, inode, index in existing
                                    if path_tags == tags
                                    and volume_name == volume
                                ]
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
                                    file_ref[index]["inode"] = file_inode
                            elif not matches:
                                # assume that the file locations is brand new,
                                # and add it to the list.
                                file_ref.append(
                                    {
                                        "tags": path_tags,
                                        "filename": str(path_tags[-1]),
                                        "md5hash": file_hash,
                                        "full_path": full_path,
                                        "volume": volume_name,
                                        "file_size": file_size,
                                        "timestamp": timestamp,
                                        "filetype": file_type[0],
                                        "inode": file_inode,
                                    }
                                )
                            if sync_to_s3:
                                # sync to s3 if option was selected.
                                # use the file just added, since it's likely accessible
                                # meta = pfu.parse_location_metadata(file_ref)
                                sync_file_to_s3_new(file_ref[-1])
                            if sync_to_local_drive:
                                # TODO
                                #
                                #
                                # Add a sync to another drive here
                                #
                                sync_to_another_drive(file_ref, local_target)
                            # if file_stat.st_size > min_file_size:

                            if WRITE_OUT_FLAT:
                                temp_outfile = (
                                    file_type.extension + FLAT_FILE_SUFFIX
                                )
                                temp_outfile = os.path.join(
                                    FLAT_FILE_DATA_DIR, temp_outfile
                                )
                                if not os.path.exists(temp_outfile):
                                    """create a header row if file doesn't exist
                                    """
                                    startFile = open(temp_outfile, "w+")
                                    startFile.write(
                                        "Filename\t"
                                        "Hash\t"
                                        "FileSize\t"
                                        "Date\t"
                                        "FileType\t"
                                        "inode\t"
                                        "VolumeName\n"
                                    )
                                    startFile.close()

                                with open(temp_outfile, "a+") as out_put_file:
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


def get_class_var_attributes(cls: object):
    clsItems = cls._attributes
    # filtered_attributes = [i[0] for i in clsItems if not i[0].startswith('__') and not callable(i[1])]
    return clsItems


def add_to_tbd_list(hashsum):
    lines = []
    try:
        with open(TBD_PATH, "r") as textfile:
            lines = textfile.readlines()
    except FileExistsError as e:
        logger.debug(e)
    except FileNotFoundError as e:
        logger.debug(e)

    lines.append(f"{hashsum}\n")
    with open(TBD_PATH, "w+") as outfile:
        outfile.writelines(set(lines))


def get_vhd_list(path):
    vhdlist = [v for v in get_all_files_from_target(path) if 'vhd' in v.suffix.lower()]
    return vhdlist
