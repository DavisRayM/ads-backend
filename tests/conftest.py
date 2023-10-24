from flask import Flask
from flask.testing import FlaskCliRunner, FlaskClient
import pytest

from ads import create_app
from ads.db import get_db


class AuthActions(object):
    def __init__(self, client: FlaskClient):
        self._client: FlaskClient = client

    def login(self, username: str = "test", password: str = "test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        pass


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "MONGO_URI": "mongodb://127.0.0.1/test"})

    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture(autouse=True, scope="function")
def cleanup_db(app):
    yield

    with app.app_context():
        db = get_db()
        db.users.drop()


@pytest.fixture
def auth(client: FlaskClient) -> AuthActions:
    return AuthActions(client)
