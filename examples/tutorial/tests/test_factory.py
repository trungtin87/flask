from flaskr import create_app


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client):
    response = client.get("/hello")
    assert response.data == b"Xin ch\xc3\xa0o, Th\xe1\xba\xbf gi\xe1\xbb\x9bi!"
