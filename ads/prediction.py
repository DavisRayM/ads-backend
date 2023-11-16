import os

from ads.tasks import process_prediction

from flask import Blueprint, current_app, g, redirect, request, url_for
from werkzeug.utils import secure_filename

from ads.auth import login_required
from ads.db import Prediction

bp = Blueprint("prediction", __name__, url_prefix="/predict")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@bp.route("/<int:prediction_id>", methods=("GET",))
def get_prediction(prediction_id: int):
    obj = Prediction.get(prediction_id)
    if obj is not None:
        return obj.dict()
    else:
        return {"error": "not found"}, 404


@bp.route(
    "/request",
    methods=(
        "POST",
        "GET",
    ),
)
def request_prediction():
    if request.method == "POST":
        if "file" not in request.files:
            return {"error": "file required"}, 400

        file = request.files["file"]
        print(file.filename)
        if file.filename == "":
            return {"error": "file required"}, 400
        elif not allowed_file(file.filename):
            return {"error": "unsupported file type"}, 400
        else:
            filename = secure_filename(file.filename)

            file_path = (
                f"{os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename)}"
            )
            file.save(file_path)
            prediction = Prediction.create(g._user, file_path, "N/A")
            if prediction:
                process_prediction.delay(prediction.id)
                return redirect(
                    url_for("prediction.get_prediction", prediction_id=prediction.id)
                )
            else:
                return {"error": "failed to create prediction request"}, 500

    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """
