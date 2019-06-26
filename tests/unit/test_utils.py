import pytest
from pyfi_util import pyfish_util as pfu
from pyfi_filestore.pyfish_file import PyfishFile

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


@pytest.mark.s3_slow
def test_sync_s3_new(pyfishfile:PyfishFile):
    pyfishfile.open_and_get_info()
    pyfishfile.encrypt_remote = True
    pfu.sync_file_to_s3_new(pyfishfile)

@pytest.mark.s3_slow
def test_sync_s3_new_no_encrypt(pyfishfile:PyfishFile):
    pyfishfile.open_and_get_info()
    pyfishfile.encrypt_remote = False
    pfu.sync_file_to_s3_new(pyfishfile)


@pytest.mark.gzip
def test_gzip(pyfishfile:PyfishFile):
    pyfishfile.open_and_get_info()
    fl = pyfishfile.full_path
    before:bytes = None
    after:bytes = None
    with open(fl, 'rb') as data:
        before = data.read()
    
    with open(fl, 'rb') as data:
        import gzip
        after = gzip.compress(data.read())

    assert before.__sizeof__()/1024/1024.0 > after.__sizeof__()/1024/1024.0

@pytest.mark.utils
def test_create_a_manifest():
    # test_manifest_decrypted = 'tests/test_files/test.manifest.json'
    manifest_data = pfu.create_manifest('test',['test_folder/1/not_real', 'test_folder/2/not_real'])
    assert len(manifest_data['locations']['test']) == 2
    assert type(manifest_data['locations']['test']) is list
    assert 'test_folder/1/not_real' in manifest_data['locations']['test']

@pytest.mark.utils
def test_add_files_to_manifest():
    test_manifest_decrypted = 'tests/test_files/data/test.manifest.json'
    pfu.add_location_to_file_manifest(test_manifest_decrypted,'test',["made/up/path"])

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
