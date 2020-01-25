import pytest
from pyfi_util import pyfish_util as pfu
from pyfi_filestore.pyfish_file import PyfishFile
import os
DATA_FOLDER = "data" if os.name != 'nt' else "data_nt"

@pytest.mark.utils
def test_build_relative_destination_path(pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    first_item = pyfish_file_set.list[first_key][0]
    path, ft, md5hash = pfu.build_relative_destination_path(first_item)
    testpath = f"{first_item.filetype}/{first_item.md5hash}/"
    assert (path, ft, md5hash) == (
        testpath,
        first_item.filetype,
        first_item.md5hash,
    )


@pytest.mark.utils
def test_build_relative_destination_path_remote(pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    first_item = pyfish_file_set.list[first_key][0]
    path, ft, remote_name_hash = pfu.build_relative_destination_path_remote(
        first_item
    )
    testpath = f"{first_item.filetype}/{first_item.remote_name_hash}/"
    assert (path, ft, remote_name_hash) == (
        testpath,
        first_item.filetype,
        first_item.remote_name_hash,
    )


@pytest.mark.s3_slow
def test_sync_s3_new(pyfishfile: PyfishFile):
    pyfishfile.open_and_get_info()
    pyfishfile.encrypt_remote = True
    pfu.sync_file_to_s3_new(pyfishfile)


@pytest.mark.s3_slow
def test_sync_s3_new_no_encrypt(pyfishfile: PyfishFile):
    pyfishfile.open_and_get_info()
    pyfishfile.encrypt_remote = False
    pfu.sync_file_to_s3_new(pyfishfile)


@pytest.mark.gzip
def test_gzip(pyfishfile: PyfishFile):
    pyfishfile.open_and_get_info()
    fl = pyfishfile.full_path
    before: bytes = b''
    after: bytes = b''
    with open(fl, "rb") as data:
        before = data.read()
    with open(fl, "rb") as data:
        import gzip

        after = gzip.compress(data.read())

    assert (
        before.__sizeof__() / 1024 / 1024.0
        > after.__sizeof__() / 1024 / 1024.0
    )


@pytest.mark.utils
def test_create_a_manifest():
    # test_manifest_decrypted = 'tests/test_files/test.manifest.json'
    manifest_data = pfu.create_manifest(
        "test", ["test_folder/1/not_real", "test_folder/2/not_real"]
    )
    assert len(manifest_data["locations"]["test"]) == 2
    assert type(manifest_data["locations"]["test"]) is list
    assert "test_folder/1/not_real" in manifest_data["locations"]["test"]


@pytest.mark.utils
@pytest.mark.skip(msg='This logic isn\'t clear at the moment')
def test_add_files_to_manifest():
    test_manifest_decrypted = f"tests/test_files/{DATA_FOLDER}/test.manifest.json"
    pfu.add_location_to_file_manifest(
        test_manifest_decrypted, "test", ["made/up/path"]
    )


@pytest.mark.tbd
def test_add_to_tbd_list(tbd_path, pyfish_file_set):
    first_key = list(pyfish_file_set.list.keys())[0]
    pfu.add_to_tbd_list(first_key)
    with open(tbd_path) as tbd_file:
        hash_read = tbd_file.readline().rstrip()
    assert hash_read == first_key


@pytest.mark.tbd
def test_add_multiple_to_tbd_list(tbd_path, pyfish_file_set_multiple):
    test_list = list(pyfish_file_set_multiple.list.keys())
    test_list.sort()
    for i in range(2):
        pfu.add_to_tbd_list(test_list[i])
    with open(tbd_path) as tbd_file:
        found_list = []
        found_list.append(tbd_file.readline().rstrip())
        found_list.append(tbd_file.readline().rstrip())
    found_list.sort()
    assert found_list == test_list


@pytest.mark.utils
def test_get_files():
    path = 'tests/test_files'
    files = pfu.get_all_files_from_target(path)
    linkfile = [f for f in files if 'link' in f.name][0]
    filefile = [f for f in files if linkfile.name.split(".")[0] in f.name][0]
    assert filefile.exists() is True
    assert linkfile.exists() is False
    assert filefile.is_file() is True


@pytest.mark.vhd_support
def test_find_vhd_list():
    # given a test path with many files but two that end in vhd
    path = 'tests/test_files'

    # when calling the funciton to get the vhd list
    vhd_list = pfu.get_vhd_list(path)

    # then
    # the list will return two strings
    assert len(vhd_list) == 2

    # one ends in vhd
    vhds = [v for v in vhd_list if '.vhd' == v.suffix]
    assert len(vhds) == 1

    # one ends in vhdx
    vhdxs = [v for v in vhd_list if '.vhdx' == v.suffix]
    assert len(vhdxs) == 1
