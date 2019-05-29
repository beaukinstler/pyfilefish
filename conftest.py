import s3_integration
from pyfi_util import pyfish_util as pfu
import pytest
from pyfi_ui import pyfi_cli as pui
from dotenv import load_dotenv
from os import getenv
from collections import namedtuple
from s3_integration.s3_tools import S3Connection
from filetypes import FilePropertySet


ACTIVE_BUCKET_NAME='backups.beaukinstler.com' ## TODO: create a test bucket and change this
PYFI_S3_SALT='test'
PYFI_S3_ENCRYPTION_KEY='T3stK3yF04Fun'
SMALL_TEST_FILE='tests/test_files/test.mp3'
SMALL_TEST_FILE_KEY='tests/test.mp3'
MED_TEST_FILE='tests/test_files/test.wav'
MED_TEST_FILE_KEY='tests/test.wav'



@pytest.fixture()
def file_property_set(blank=False):
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()

    file_types = FilePropertySet()
    if blank:
            file_types.clear()
    return file_types

@pytest.fixture()
def file_list():
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()
    result = pfu._load_saved_file_list('tests/test_json_data.json')
    return result

@pytest.fixture()
def file_list_only_one_volume():
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()
    result = pfu._load_saved_file_list('tests/test_json_data_one_vol.json')
    return result

@pytest.fixture()
def test_env():
    EnvBuilder = namedtuple(
            "env", 
            ['ACTIVE_BUCKET_NAME','PYFI_S3_SALT','PYFI_S3_ENCRYPTION_KEY',
             'SMALL_TEST_FILE', 'SMALL_TEST_FILE_KEY', 'MED_TEST_FILE',
             'MED_TEST_FILE_KEY']
        )
    env = EnvBuilder._make(
            [ACTIVE_BUCKET_NAME,PYFI_S3_SALT,PYFI_S3_ENCRYPTION_KEY,
             SMALL_TEST_FILE, SMALL_TEST_FILE_KEY, MED_TEST_FILE, MED_TEST_FILE_KEY]
        )

    return env

@pytest.fixture()
def s3conn():
    s3conn = S3Connection()
    s3conn.connect()
    s3conn.active_bucket_name = ACTIVE_BUCKET_NAME
    return s3conn


@pytest.fixture()
def test_sm_fileobj():
    data = None
    with open(SMALL_TEST_FILE, 'rb') as file_to_get:
        yield file_to_get


@pytest.fixture()
def test_med_fileobj():
    data = None
    with open(MED_TEST_FILE, 'rb') as file_to_get:
        yield file_to_get

@pytest.fixture()
def pyfishfile():
    return pfu.PyfishFile('test', 'tests/test_files/test.wav')

@pytest.fixture()
def pyfish_file_set():
    test_file = pfu.PyfishFile('test', 'tests/test_files/test.wav')
    test_file.open_and_get_info()
    fs =  pfu.PyfishFileSet()
    fs.add(test_file)
    return fs


