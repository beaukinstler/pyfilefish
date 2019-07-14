# import s3_integration
from pyfi_util import pyfish_util as pfu
from pyfi_filestore.pyfish_file import PyfishFileSet
import pytest

# from pyfi_ui import pyfi_cli as pui
from os import getenv
from collections import namedtuple
from s3_integration.s3_tools import S3Connection
from filetypes import FilePropertySet

import tempfile
from flaskr import create_app
from flaskr.db import get_db
from flaskr.db import init_db
import os
from settings import TBD_PATH

os.environ["FLASK_ENV"] = "testing"

ACTIVE_BUCKET_NAME = getenv("ACTIVE_BUCKET_NAME")
PYFI_S3_SALT = getenv("PYFI_S3_SALT")
PYFI_S3_ENCRYPTION_KEY = getenv("PYFI_S3_ENCRYPTION_KEY")
SMALL_TEST_FILE = "tests/test_files/test.mp3"
SMALL_TEST_FILE_KEY = "tests/test.mp3"
MED_TEST_FILE = "tests/test_files/test.wav"
MED_TEST_FILE_KEY = "tests/test.wav"


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
    result = pfu._load_saved_file_list("tests/test_files/data/test_json_data.json")
    return result


@pytest.fixture()
def file_list_only_one_volume():
    """primary data set and structure used in pyfi, at least in
    active time. Basically a dict, loaded and saved to and from json
    files
    """
    # import pdb; pdb.set_trace()
    result = pfu._load_saved_file_list(
        "tests/test_files/data/test_json_data_one_vol.json"
    )
    return result


@pytest.fixture()
def test_env():
    EnvBuilder = namedtuple(
        "env",
        [
            "ACTIVE_BUCKET_NAME",
            "PYFI_S3_SALT",
            "PYFI_S3_ENCRYPTION_KEY",
            "SMALL_TEST_FILE",
            "SMALL_TEST_FILE_KEY",
            "MED_TEST_FILE",
            "MED_TEST_FILE_KEY",
        ],
    )
    env = EnvBuilder._make(
        [
            ACTIVE_BUCKET_NAME,
            PYFI_S3_SALT,
            PYFI_S3_ENCRYPTION_KEY,
            SMALL_TEST_FILE,
            SMALL_TEST_FILE_KEY,
            MED_TEST_FILE,
            MED_TEST_FILE_KEY,
        ]
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
    with open(SMALL_TEST_FILE, "rb") as file_to_get:
        yield file_to_get


@pytest.fixture()
def test_med_fileobj():
    with open(MED_TEST_FILE, "rb") as file_to_get:
        yield file_to_get


@pytest.fixture()
def pyfishfile():
    return pfu.PyfishFile("test", "tests/test_files/test.wav")


@pytest.fixture()
def pyfish_file_set():
    test_file = pfu.PyfishFile("test", "tests/test_files/test.wav")
    test_file.open_and_get_info()
    fs = PyfishFileSet()
    fs.add(test_file)
    return fs


@pytest.fixture()
def pyfish_file_set_multiple():
    test_file = pfu.PyfishFile("test", "tests/test_files/test.wav")
    test_file.open_and_get_info()
    test_file2 = pfu.PyfishFile("test", "tests/test_files/test.mp3")
    test_file2.open_and_get_info()
    fs = PyfishFileSet()
    fs.add(test_file)
    fs.add(test_file2)
    return fs


@pytest.fixture()
def tbd_path():
    try:
        os.remove(TBD_PATH)
    except FileNotFoundError:
        pass
    yield TBD_PATH
    os.remove(TBD_PATH)


####
# FROM FLASK TUTORIAL
###
"""Copyright © 2010 by the Pallets team.

Some rights reserved.

Redistribution and use in source and binary forms of the software as
well as documentation, with or without modification, are permitted
provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE."""


# read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), "flaskr/data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # create the database and load test data
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
