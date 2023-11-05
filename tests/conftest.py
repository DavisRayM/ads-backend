import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from ads import create_app
from ads.db import drop_db, init_db


class AuthActions(object):
    def __init__(self, client: FlaskClient):
        self._client: FlaskClient = client

    def register(self, username: str = "test", password: str = "test"):
        return self._client.post(
            "/auth/register", data={"username": username, "password": password}
        )

    def login(self, username: str = "test", password: str = "test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        pass


@pytest.fixture
def app():
    app = create_app()

    with app.app_context():
        drop_db()
        init_db()

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    auth = AuthActions(client)
    auth.register()
    return auth
