from pyfi_util import pyfish_util as pfu
import pytest



def test_filtering_with_non_existant_name_gets_all(file_list):
    list_with_all_data = pfu.get_files_missing_from_a_volume(file_list,'x')
    assert len(list_with_all_data) > 1
    assert list_with_all_data[0][1] == {'test', 'test3'}
    assert len(list_with_all_data) == len(file_list)

def test_filtering_out_the_only_volume_in_data(file_list_only_one_volume):
    list_with_no_data = pfu.get_files_missing_from_a_volume(file_list_only_one_volume,'test')
    assert len(list_with_no_data) == 0

def test_filter_out_one_volume_should_result_in_one_less(file_list):
    total_count = len(pfu.get_files_missing_from_a_volume(file_list,'x')) # since there is no vol x, total number
    filter_should_make_one_less = len(pfu.get_files_missing_from_a_volume(file_list,'test2')) 
    assert total_count - filter_should_make_one_less == 1




