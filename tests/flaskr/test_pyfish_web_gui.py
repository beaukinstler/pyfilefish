import pytest

# from flaskr.db import get_db

@pytest.mark.pyfish_web_gui
def test_Pyfish_link_only_when_authenticated(client, auth):
    response = client.get("/")
    assert b"Pyfish" not in response.data
    auth.login()
    response = client.get("/")
    assert b"Pyfish" in response.data

@pytest.mark.pyfish_web_gui
@pytest.mark.parametrize("path", ("/pyfi", ))
def test_login_required(client, path):
    response = client.get(path)
    assert b"Full Path" not in response.data
    assert response.headers["Location"] == "http://localhost/auth/login"

@pytest.mark.pyfish_web_gui
def test_pyfi_accesible_when_authenticated(client, auth):
    auth.login()
    response = client.get("/pyfi")
    assert b"Full Path" in response.data

@pytest.mark.pyfish_web_gui
def test_wav_file_found(client, auth):
    auth.login()
    response = client.get("/pyfi/test/3b01b3abec70519b00b9738b1336cddc.wav")
    assert response.status_code == 200
    assert response.content_type == 'audio/x-wav'