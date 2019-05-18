from pyfi_util import pyfish_util as pfu
from pathlib import Path
from datetime import datetime as dt
from hashlib import md5
from settings import HASH_KEY


class PyfishFile():

    # implemented attributes
    _attributes = [
            'volume',
            'full_path',
            'md5FileHash',
            'md5Name',
            'file_type',
            'known_name',
            'size_in_MB',
            'keep',
            'encrypt_remote',
            'inode',
            'timestamp',
            'tags',
            'drive',
            'repr_cache',
            'refresh_repr',
        ]


    def __init__(self, volume, full_path,
                 md5FileHash:str="", md5Name:str="", file_type:str="", known_name="",
                 size_in_MB=0, keep=True, encrypt_remote=True, 
                 inode="", timestamp="", tags=[]):
        
        self.volume = volume
        self.full_path = full_path
        self.md5FileHash = md5FileHash
        self.md5Name = md5Name
        self.file_type = file_type
        self.known_name = known_name
        self.size_in_MB = size_in_MB
        self.keep = keep
        self.encrypt_remote = encrypt_remote
        self.inode = inode
        self.timestamp = timestamp
        self.tags = tags
        self.drive = ""
        self.repr_cache = None
        self.refresh_repr = False
        if md5FileHash:
            self.repr_cache = {'filename': self.known_name, 
                        'md5FileHash': self.md5FileHash,
                        'md5hash': self.buildMd5Name(),
                        'tags': self.tags, 'full_path': self.full_path,
                        'volume': self.volume, 'drive':self.drive,
                        'file_size': round(self.size_in_MB,3),
                        'timestamp': str(self.timestamp), 'filetype': self.file_type.lower(),
                        'inode': self.inode, 'keep': self.keep,
                        'encrypt_remote': self.encrypt_remote}

    def __repr__(self):
        if self.repr_cache == None or self.refresh_repr is True:
            self.open_and_get_info()
            self.repr_cache = {'filename': self.known_name, 
                    'md5FileHash': self.md5FileHash,
                    'md5hash': self.md5Name,
                    'tags': self.tags, 'full_path': self.full_path,
                    'volume': self.volume, 'drive':self.drive,
                    'file_size': round(self.size_in_MB,3),
                    'timestamp': str(self.timestamp), 'filetype': self.file_type.lower(),
                    'inode': self.inode, 'keep': self.keep,
                    'encrypt_remote': self.encrypt_remote}
        return str(self.repr_cache)

    def buildMd5Name(self):
        if not self.md5Name:
            return md5(bytearray(str.join(self.md5FileHash, HASH_KEY),'utf-8')).hexdigest()
        else:
            return self.md5Name


    def open_and_get_info(self):
        absolute = Path(self.full_path).absolute()
        if absolute.exists():
            with absolute.open(mode='rb') as file_to_read:
                self.md5FileHash = pfu.get_md5(file_to_read)
                self.tags = list(absolute.parts)[1:] if self.tags == [] else self.tags
                self.size_in_MB = absolute.stat().st_size / 1024 / 1024
                self.timestamp = dt.fromtimestamp(absolute.stat().st_mtime)
                self.inode = absolute.stat().st_ino
                self.known_name = absolute.name
                self.drive = absolute.drive
                self.md5Name = self.buildMd5Name()
        else:
            print("file doesn't exists, or isn't accessible in the current process")

    def is_file_type(self, type:str, advanced=False):
        if advanced:
            return self.parse_file_for_type == type.lower()
        else:
            return self.get_file_type == type.lower()

    def parse_file_for_type(self):
        pass

    def get_file_type(self):
        if self.file_type == "":
            self.open_and_get_info()
        return self.file_type

    def __eq__(self, value):
        return self.inode == value.inode and self.volume == value.volume


class PyfishFileSet():
    def __init__(self, file_record:PyfishFile = None):
        self.list = {}
        if file_record:
            self.list[file_record.md5FileHash] = [file_record]


    def add(self, file_record:PyfishFile):
        
        try:
            for i in self.list[file_record.md5FileHash]:
                if i.inode == file_record.inode and i.volume == file_record.volume:
                    print('duplicate file, will not add')
                else:
                    i.append(file_record)
        except KeyError as e:
            print(e)
            print("New item found, will add to the set")
            self.list[file_record.md5FileHash] = [file_record]
    
    def add_from_dict(self, external_dict):
        self.list = external_dict