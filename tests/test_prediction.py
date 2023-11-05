import pytest
import io

from ads.prediction import allowed_file


@pytest.mark.parametrize(
    ("file", "filename", "message"),
    (
        (None, None, "file required"),
        (io.BytesIO(b"some initial data"), None, "file required"),
        (io.BytesIO(b"some initial data"), "some.pdf", "unsupported file type"),
    ),
)
def test_predict_request_validation(client, auth, file, filename, message):
    auth.login()
    resp = client.post("/predict/request", data={"file": (file, filename)})
    assert resp.status_code == 400
    assert resp.json.get("error") == message


def test_allowed_file(app):
    with app.app_context():
        assert not allowed_file("some.pdf")
        assert allowed_file("some.png")


def test_get_prediction_not_found(client, auth):
    auth.login()
    resp = client.get("/predict/25")
    assert resp.status_code == 404
    assert resp.json["error"] == "not found"


def test_request_prediction(client, auth):
    auth.login()
    resp = client.post(
        "/predict/request",
        data={"file": (io.BytesIO(b"some initial data"), "sample_image.jpg")},
    )
    print(resp.headers)
    assert resp.status_code == 302

    resp = client.get(resp.headers["Location"])
    assert resp.status_code == 200
    assert resp.json["status"] == "pending"
