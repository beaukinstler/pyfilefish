import pytest
from pyfi_filestore.pyfish_file import PyfishFile
from pyfi_util import pyfish_util as pfu


@pytest.mark.pfile_dev
def test_write_to_local_as_if_remote(pyfishfile: PyfishFile):
    pyfishfile.open_and_get_info()
    remote_save_path = pfu.build_relative_destination_path_remote(
        pyfish_file_ref=pyfishfile
    )
    local_save_path = pfu.build_relative_destination_path(pyfish_file_ref=pyfishfile)
