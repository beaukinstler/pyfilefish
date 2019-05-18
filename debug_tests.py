import os
# from hashlib import md5
# import datetime
import json
import codecs
from pprint import pprint
import logging
from pyfi_util import pyfish_util as pfu
from settings import *
import pyfi_ui as pui


from tests.func import test_pyfile

from conftest import pyfishfile

test_pyfile.test_pyfishfile_builder_valid_dict(pyfishfile)
test_pyfile.test_pyfishfile_builder_file_not_accessible(pyfishfile)