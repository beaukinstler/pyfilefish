import pytest
from pyfi_util import pyfish_util as pfu

@pytest.mark.utils
def test_build_relative_destination_path(pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    first_item = pyfish_file_set.list[first_key][0]
    path, ft, md5hash = pfu.build_relative_destination_path(first_item)
    testpath = f"{first_item.filetype}/{first_item.md5hash}/"
    assert (path, ft, md5hash) == (testpath, first_item.filetype, first_item.md5hash)


@pytest.mark.utils
def test_build_relative_destination_path_remote(pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    first_item = pyfish_file_set.list[first_key][0]
    path, ft, remote_name_hash = pfu.build_relative_destination_path_remote(first_item)
    testpath = f"{first_item.filetype}/{first_item.remote_name_hash}/"
    assert (path, ft, remote_name_hash) == (testpath, first_item.filetype, first_item.remote_name_hash)