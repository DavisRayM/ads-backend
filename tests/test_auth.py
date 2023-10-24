import pytest
from flask import g, session

from ads.db import get_db


def test_register_works(app, client):
    resp = client.get("/auth/register")
    assert resp.status_code == 200

    resp = client.post("/auth/register", data={"username": "bob", "password": "test"})
    assert resp.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().users.find_one({"username": "bob"}) is not None


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required"),
        ("bob", "", b"Password is required"),
    ),
)
def test_register_validation(client, username, password, message):
    resp = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in resp.data


def test_login_works(client, auth):
    resp = client.post("/auth/register", data={"username": "bob", "password": "test"})
    assert resp.headers["Location"] == "/auth/login"

    resp = auth.login("bob", "test")
    assert resp.headers["Location"] == "/healthz"

    with client:
        client.get("/healthz")
        assert session["user"] == "bob"
        assert g._user["username"] == "bob"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required"),
        ("bob", "", b"Password is required"),
        ("random", "pass", b"invalid username/password"),
    ),
)
def test_login_validation(client, username, password, message):
    resp = client.post("/auth/login", data={"username": username, "password": password})
    assert message in resp.data


def test_logout(client, auth):
    resp = client.post("/auth/register", data={"username": "bob", "password": "test"})
    assert resp.headers["Location"] == "/auth/login"

    resp = auth.login("bob", "test")
    assert resp.headers["Location"] == "/healthz"

    client.post("/auth/logout")
    with client:
        client.get("/auth/login")
        assert session == {}
        assert g._user is None
