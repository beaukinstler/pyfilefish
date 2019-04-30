from s3_integration import pyfish_util as pfu
import pytest



def test_filtering_with_non_existant_name_gets_all(file_list):
    list_with_all_data = pfu.get_files_missing_from_a_volume(file_list,'x')
    assert len(list_with_all_data) > 1
    assert list_with_all_data[0][1] == {'test'}
    assert len(list_with_all_data) == len(file_list)

def test_filtering_out_the_only_volume_in_data(file_list):
    list_with_no_data = pfu.get_files_missing_from_a_volume(file_list,'test')
    assert len(list_with_no_data) == 0




