from pyfi_util import pyfish_util as pfu
from pathlib import Path
from datetime import datetime as dt
from hashlib import md5
from settings import HASH_KEY
from settings import logger


class PyfishFile(object):

    # implemented attributes
    _attributes = [
        "volume",
        "full_path",
        "md5hash",
        "remote_name_hash",
        "filetype",
        "filename",
        "file_size",
        "keep",
        "encrypt_remote",
        "inode",
        "timestamp",
        "tags",
        "drive",
        "repr_cache",
        "refresh_repr",
    ]

    def __init__(
        self,
        volume,
        full_path,
        md5hash="",
        remote_name_hash="",
        filetype="",
        filename="",
        file_size=0,
        keep=True,
        encrypt_remote=True,
        inode="",
        timestamp="",
        tags=[],
    ):

        self.volume = volume
        self.full_path = full_path
        self.md5hash = md5hash
        self.remote_name_hash = remote_name_hash
        self.filetype = filetype
        self.filename = filename
        self.file_size = file_size
        self.keep = keep
        self.encrypt_remote = encrypt_remote
        self.inode = inode
        self.timestamp = timestamp
        self.tags = tags
        self.drive = ""
        self.repr_cache = None
        self.refresh_repr = False
        if md5hash:
            self.repr_cache = {
                "filename": self.filename,
                "md5hash": self.md5hash,
                "remote_name_hash": self.build_remote_name_hash(),
                "tags": self.tags,
                "full_path": self.full_path,
                "volume": self.volume,
                "drive": self.drive,
                "file_size": round(self.file_size, 3),
                "timestamp": str(self.timestamp),
                "filetype": self.filetype.lower(),
                "inode": self.inode,
                "keep": self.keep,
                "encrypt_remote": self.encrypt_remote,
            }

    @classmethod
    def from_dict(cls, pfil_dict):
        self = 1
        self = cls(
            volume=pfil_dict["volume"], full_path=pfil_dict["full_path"]
        )
        self.__dict__.update(pfil_dict)
        return self

    def update_representation_cache(self):
        self.repr_cache = {
            "filename": self.filename,
            "md5hash": self.md5hash,
            "remote_name_hash": self.remote_name_hash,
            "tags": self.tags,
            "full_path": self.full_path,
            "volume": self.volume,
            "drive": self.drive,
            "file_size": round(self.file_size, 3),
            "timestamp": str(self.timestamp),
            "filetype": self.filetype.lower(),
            "inode": self.inode,
            "keep": self.keep,
            "encrypt_remote": self.encrypt_remote,
        }

    def __repr__(self):
        if self.repr_cache is None or self.refresh_repr is True:
            self.open_and_get_info()
            self.update_representation_cache()
        return str(self.repr_cache)

    def __iter__(self):
        if self.repr_cache is None or self.refresh_repr is True:
            self.open_and_get_info()
            self.update_representation_cache()
        return iter(self.repr_cache)

    def build_remote_name_hash(self):
        if not self.remote_name_hash:
            return md5(
                bytearray(str.join(self.md5hash, HASH_KEY), "utf-8")
            ).hexdigest()  # noqa
        else:
            return self.remote_name_hash

    def open_and_get_info(self):
        absolute = Path(self.full_path).absolute()
        if absolute.exists():
            with absolute.open(mode="rb") as file_to_read:
                self.md5hash = pfu.get_md5(file_to_read)
                self.tags = (
                    list(absolute.parts)[1:] if self.tags == [] else self.tags
                )  # noqa
                self.file_size = absolute.stat().st_size / 1024 / 1024
                self.timestamp = dt.fromtimestamp(absolute.stat().st_mtime)
                self.filetype = (
                    self.filename.split(".")[-1]
                    if self.filetype == ""
                    else self.filetype
                )  # noqa
                self.inode = absolute.stat().st_ino
                self.filename = absolute.name
                self.drive = absolute.drive
                self.remote_name_hash = self.build_remote_name_hash()
        else:
            print(
                "file doesn't exists, or isn't accessible\
                   in the current process"
            )

    def is_file_type(self, file_type, advanced=False):
        if advanced:
            return self.parse_file_for_type == file_type.lower()
        else:
            return self.get_file_type == file_type.lower()

    def parse_file_for_type(self):
        pass

    def get_file_type(self):
        if self.filetype == "":
            self.open_and_get_info()
        return self.filetype

    def __eq__(self, value):
        return self.inode == value.inode and self.volume == value.volume


class PyfishFileSet:
    def __init__(self, file_record: PyfishFile = None):
        self.list = {}
        if file_record:
            self.list[file_record.md5hash] = [file_record]

    def add(self, file_record: PyfishFile, volume=None):
        """add the file. If a volume is provided, first check if its a \
           duplicate inode on the same volume

        Arguments:
            file_record {PyfishFile} -- A file-representation in the \
                                        form a PyfishFile
        """
        # if a volume is provided, check to make sure the file
        # isn't already on it using the inode
        # if a volume isn't provided, assume just load it into
        # the list, and do not check for duplicated entries.
        if volume:
            inodes_found = self.get_list_inodes_of_a_file_location_for_one_volume(  # noqa
                file_record, volume
            )  # noqa
            if inodes_found:
                print("duplicate file, will not add")
                logger.info(
                    "duplicate file found, will not add any data \
                             to the dictionary"
                )
            else:
                print("file not found on volume, so add it")
                self.list[file_record.md5hash].append(file_record)
        else:
            try:
                self.list[file_record.md5hash].append(file_record)
            except KeyError:
                print("New item found, will add to the set")
                self.list[file_record.md5hash] = [file_record]

    def load_from_dict(self, external_dict):
        # clear the list
        self.list = {}

        # loop through the external dict (probably from json)
        for hashsum in external_dict:
            # loop over the list of files for each key
            for file_item in external_dict[hashsum]:
                # if already there, append else make a new list
                # if type(self.list[md5]) is list:
                #     self.list[md5].append(file_item)
                # else:
                #     self.list[md5] = [file_item]
                temp = pfu.pyfi_file_builder(file_item)
                self.add(temp)

    def get_list_of_a_file_location(self, md5hash):
        if md5hash in self.list.keys():
            return [i for i in self.list[md5hash]]
        else:
            return None

    def get_list_of_a_file_location_for_one_volume(
        self, file_record: PyfishFile, volume
    ):  # noqa
        files = self.generate_cached_files_list_from_one_vol(volume)
        if file_record.md5hash in files.keys():
            return [i for i in files[file_record.md5hash]]
        else:
            return None

    def get_list_inodes_of_a_file_location_for_one_volume(
        self, file_record: PyfishFile, volume
    ):  # noqa
        files = self.generate_cached_files_list_from_one_vol(volume)
        if file_record.md5hash in files.keys():
            return [i.inode for i in files[file_record.md5hash]]
        else:
            return None

    def get_list_of_a_file_volumes(self, md5hash):
        file_refs = self.get_list_of_a_file_location(md5hash)
        if file_refs:
            return list(set([i.volume for i in file_refs])), file_refs
        else:
            return [], None

    def __iter__(self):
        return iter(self.list)

    def generate_cached_files_list_from_one_vol(self, volume):
        new_data = {}
        try:
            new_data = self.__getattribute__(f"cache_{volume}")
        except AttributeError as e:
            print(e)
            print("no existing cache was found")

        if new_data:
            return new_data
        else:
            data = (
                self.list
                if self.list
                else self.load_from_dict(pfu.load_pyfish_data())
            )  # noqa
            for hashsum in data.keys():
                new_data[hashsum] = [ files for files in data[hashsum]  if files.volume == volume ]

        self.__setattr__(f"cache_{volume}", new_data)
        return new_data
