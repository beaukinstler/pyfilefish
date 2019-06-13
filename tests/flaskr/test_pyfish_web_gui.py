import pytest

# from flaskr.db import get_db

@pytest.mark.pyfish_web_gui
def test_Pyfish_link_only_when_authenticated(client, auth):
    response = client.get("/")
    assert b"Pyfish" not in response
    auth.login()
    response = client.get("/")
    assert b"Pyfish" in response.data

@pytest.mark.pyfish_web_gui
@pytest.mark.parametrize("path", ("/pyfi", ))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"

@pytest.mark.pyfish_web_gui
def test_pyfi_accesible_when_authenticated(client, auth):
    response = client.get("/")
    assert b"Full Path" in response.data
    assert response.headers["Location"] == "http://localhost/pyfi"


# def test_author_required(app, client, auth):
#     # change the post author to another user
#     with app.app_context():
#         db = get_db()
#         db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
#         db.commit()

#     auth.login()
#     # current user can't modify other user's post
#     assert client.post("/1/update").status_code == 403
#     assert client.post("/1/delete").status_code == 403
#     # current user doesn't see edit link
#     assert b'href="/1/update"' not in client.get("/").data


# @pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
# def test_exists_required(client, auth, path):
#     auth.login()
#     assert client.post(path).status_code == 404
