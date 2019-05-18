import pytest
from pyfi_util import pyfish_util as pfu

@pytest.mark.pfile
def test_pyfishfile_builder_valid_dict(pyfishfile):
     x = {'filename': 'test.wav', 'md5FileHash': '',
          'md5hash': '', 
          'tags': ['home', 'cloud_files', 'github', 'pyfilefish', 'tests', 'test_files', 'test.wav'],
          'full_path': 'tests/test_files/test.wav', 'volume': 'test2', 'drive': '',
          'file_size': 94.885, 'timestamp': '2005-05-07 13:38:20', 'filetype': '',
          'inode': 3569854, 'keep': True, 'encrypt_remote': True}

     pf = pfu.pyfi_file_builder(x)

     print(pf)

     assert pf.md5Name is not None

@pytest.mark.pfile
def test_pyfishfile_builder_file_not_accessible(pyfishfile):
     x = {'filename': 'test.wav', 'md5FileHash': '',
          'md5hash': '', 
          'tags': ['home', 'cloud_files', 'github', 'pyfilefish', 'tests', 'test_files', 'test.wav'],
          'full_path': 'a_not_real_path/test.wav', 'volume': 'test2', 'drive': '',
          'file_size': 94.885, 'timestamp': '2005-05-07 13:38:20', 'filetype': '',
          'inode': 3569854, 'keep': True, 'encrypt_remote': True}

     pf = pfu.pyfi_file_builder(x)

     print(pf)

     assert pf.md5Name == ""