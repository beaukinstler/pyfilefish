from pyfi_filestore.pyfish_file import PyfishFile
import pytest
# from filetypes import FilePropertySet

@pytest.mark.pyfile
def test_new_from_dict(pyfish_file_set):
    # set up dict object, using the dictionary from a fixture with one item.
    myobj = pyfish_file_set.list
    key = list(myobj.keys())[0]
    assert myobj[key][0].md5hash == key
    tmp_dict = myobj[key][0].__dict__
    assert type(tmp_dict) is dict
    # test the creation of the PyfishFise using the dict object

    myPyfile:PyfishFile = PyfishFile.from_dict(tmp_dict)
    myPyfile.open_and_get_info()
    assert myPyfile.md5hash == tmp_dict['md5hash']

    