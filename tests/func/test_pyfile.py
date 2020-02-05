import pytest
from pyfi_util import pyfish_util as pfu
from pyfi_filestore.pyfish_file import PyfishFileSet, PyfishFile
from filetypes import file_types


@pytest.mark.pfile
def test_pyfishfile_builder_valid_dict():
    x = {
        "filename": "test.wav",
        "md5hash": "",
        "remote_name_hash": "",
        "tags": [
            "home",
            "cloud_files",
            "github",
            "pyfilefish",
            "tests",
            "test_files",
            "test.wav",
        ],
        "full_path": "tests/test_files/test.wav",
        "volume": "test2",
        "drive": "",
        "file_size": 94.885,
        "timestamp": "2005-05-07 13:38:20",
        "filetype": "",
        "inode": 3569854,
        "keep": True,
        "encrypt_remote": True,
    }

    pf = pfu.pyfi_file_builder(x)

    print(pf)

    assert pf.remote_name_hash is not None


@pytest.mark.pfile
def test_pyfishfile_builder_file_not_accessible():
    x = {
        "filename": "test.wav",
        "md5hash": "",
        "remote_name_hash": "",
        "tags": [
            "home",
            "cloud_files",
            "github",
            "pyfilefish",
            "tests",
            "test_files",
            "test.wav",
        ],
        "full_path": "a_not_real_path/test.wav",
        "volume": "test2",
        "drive": "",
        "file_size": 94.885,
        "timestamp": "2005-05-07 13:38:20",
        "filetype": "",
        "inode": 3569854,
        "keep": True,
        "encrypt_remote": True,
    }

    pf = pfu.pyfi_file_builder(x)

    print(pf)

    assert pf.remote_name_hash == ""


@pytest.mark.pfile
def test_add_pyfishfile_to_pfy_set():
    pyfishfile = pfu.PyfishFile("test", "tests/test_files/test.wav")
    pset = PyfishFileSet()
    pset.add(pyfishfile)

    assert len(pset.list) == 1


@pytest.mark.pfile
def test_add_pyfishfile_twice_not_duplicated():
    pyfishfile = pfu.PyfishFile("test", "tests/test_files/test.wav")
    pset = PyfishFileSet()
    pset.add(pyfishfile)
    pset.add(pyfishfile)
    assert len(pset.list) == 1


@pytest.mark.pfile
def test_pset_made_with_list_works_with_new_PfishFiles(file_list):
    pyfishfile = pfu.PyfishFile("test", "tests/test_files/test.wav")
    # print("\n")
    # pp(type(file_list))
    pset = PyfishFileSet()
    pset.load_from_dict(file_list)
    before_len = len(pset.list)
    pset.add(pyfishfile)
    after_len = len(pset.list)
    assert before_len == after_len - 1


@pytest.mark.pfile
def test_PyfishFile_from_dict(file_list):
    first_key = list(file_list.keys())[0]
    test_file = PyfishFile.from_dict(file_list[first_key][0])
    assert "PyfishFile" in str(type(test_file))


@pytest.mark.pfile
def test_file_types_in_mb():
    test_types = file_types.FilePropertySet('mb')
    ext = test_types.find_extension('wav')
    assert round(ext.min_size) in range(0,2)
    test_types = file_types.FilePropertySet('b')
    ext = test_types.find_extension('wav')
    assert ext.min_size >= 10000


@pytest.mark.pfileset
def test_pset_loaded_from_json_same_len_as_json(file_list):

    pset = PyfishFileSet()
    pset.load_from_dict(file_list)
    assert len(pset.list) == len(file_list)


@pytest.mark.pfileset
def test_pset_lists_of_files_same_len_as_json_dict_items(file_list):
    total_file_list = 0
    total_pset_list = 0
    pset = PyfishFileSet()
    pset.load_from_dict(file_list)
    for i in file_list:
        files_list_files = file_list[i]
        pset_files = pset.list[i]
        total_file_list += len(files_list_files)
        total_pset_list += len(pset_files)

    assert total_file_list == total_pset_list


@pytest.mark.pfileset
def test_pset_pyfish_file_added_correctly(file_list):

    pyfishfile = pfu.PyfishFile("test", "tests/test_files/test.wav")
    pyfishfile.open_and_get_info()
    print("\n\n")
    print(f"filehash: {pyfishfile.md5hash}")
    pset = PyfishFileSet()
    pset.load_from_dict(file_list)
    print("\n\n")
    print(pset.list.keys())
    pset.add(pyfishfile)
    print(pset.list.keys())
    assert pyfishfile.md5hash in pset.list.keys()


@pytest.mark.pfileset
def test_get_a_file_list_from_only_one_volume(file_list):
    pset = PyfishFileSet()
    pset.load_from_dict(file_list)
    pset.generate_cached_files_list_from_one_vol(volume="test")
    pset.generate_cached_files_list_from_one_vol(volume="test2")
    first_key = list(pset.list.keys())[0]
    assert len(pset.cache_test[first_key]) == len(pset.cache_test2[first_key]) 
