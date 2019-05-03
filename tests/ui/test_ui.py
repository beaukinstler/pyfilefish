import pytest
from conftest import pui

def test_prompt_windows_folder():
    ui_folder = pui.prompt_windows_folder(drive_ui="c")
    assert ui_folder == 'c:\\'

def test_prompt_windows_folder_with_sub():
    ui_folder = pui.prompt_windows_folder(drive_ui="c", folder_ui='Users')
    assert ui_folder == 'c:\\Users'


def test_prompt_windows_folder_throw_error_bad_drive():
    with pytest.raises(ValueError):
        ui_folder = pui.prompt_windows_folder(drive_ui="e", folder_ui='Users')
    
