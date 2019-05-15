import pytest
from conftest import pui
import sys

@pytest.mark.skipif(sys.platform == "linux", reason="does not run on linux")
def test_prompt_windows_folder():
    ui_folder = pui.prompt_windows_folder(drive_ui="c")
    assert ui_folder == 'c:\\'
            
@pytest.mark.skipif(sys.platform == "linux", reason="does not run on linux")
def test_prompt_windows_folder_with_sub():
    ui_folder = pui.prompt_windows_folder(drive_ui="c", folder_ui='Users')
    assert ui_folder == 'c:\\Users'

@pytest.mark.skipif(sys.platform == "linux", reason="does not run on linux")
def test_prompt_windows_folder_throw_error_bad_drive():
    with pytest.raises(ValueError):
        ui_folder = pui.prompt_windows_folder(drive_ui="e", folder_ui='Users')
    
