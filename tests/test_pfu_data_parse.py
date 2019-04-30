from tests.conftest import pfu
import pytest

def test_get_volumes_from_data(file_list):
    assert len(pfu.get_current_volumes(file_list)) == 3


def test_create_stats(file_list):
    stats = pfu.build_stats_dict(file_list)
    assert stats['notrealhash']['copies'] == 1

def test_create_multiples_finds_copies(file_list):
    multi = pfu.build_multiple_dict(file_list)
    print(multi[0])
    assert multi[0]['copies'] > 1
    # assert multi['notrealhash']['copies'] == 1

def test_create_multiples_filters_out_singles(file_list):
    multi = pfu.build_multiple_dict(file_list)
    found_single = False
    for _ in multi:
        if _['md5'] == 'notrealhash':
            found_single = True
    assert not found_single
    