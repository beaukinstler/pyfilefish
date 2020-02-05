from pyfi_util import pyfish_util as pfu
import pytest
from filetypes import FilePropertySet


@pytest.mark.data_parse
def test_get_volumes_from_data(file_list):
    assert len(pfu.get_current_volumes(file_list)) == 3


@pytest.mark.data_parse
def test_create_stats(file_list):
    stats = pfu.build_stats_dict(file_list)
    assert stats["28e0ad05a7b95446bf59e77deb14d1ca"]["copies"] == 3


@pytest.mark.data_parse
def test_create_multiples_finds_copies(file_list):
    multi = pfu.build_multiple_dict(file_list)
    print(multi[0])
    assert multi[0]["copies"] > 1


@pytest.mark.data_parse
def test_create_multiples_filters_out_singles(file_list):
    multi = pfu.build_multiple_dict(file_list)
    found_single = False
    for _ in multi:
        if _["md5"] == "edc900745c5d15d773fbcdc0b376f00c":
            found_single = True
    assert not found_single


@pytest.mark.data_parse
def test_sum_file_size(file_list):
    value = pfu.get_unique_files_totalsize(file_list, vol="Pytest_Test_Files")
    val_in_MB = round(value, 0)
    assert val_in_MB == 96


@pytest.mark.data_parse
def test_sum_file_size_wrong_volume(file_list):
    value = pfu.get_unique_files_totalsize(file_list, vol="")
    val_in_MB = value
    assert val_in_MB > 20


@pytest.mark.data_parse
def test_file_type_filter_from_one_volume(file_list):
    file_types = FilePropertySet()
    file_types.clear()
    file_types.add(file_types.file_properties("single", 0))
    files = pfu.get_files_from_one_vol(
        file_list, vol="Pytest_Test_Files", file_types=file_types
    )
    assert len(files) == 1
