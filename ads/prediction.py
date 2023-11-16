import os

from ads.tasks import process_prediction

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
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
            flash("image is required")

        file = request.files["file"]
        session = request.cookies.get("userSession")
        print(file.filename)
        if file.filename == "":
            flash("image is required")
        elif not allowed_file(file.filename):
            flash("image is required; unsupported file type")
        else:
            filename = secure_filename(file.filename)

            file_path = (
                f"{os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename)}"
            )
            file.save(file_path)
            prediction = Prediction.create(session, file_path, "N/A")
            if prediction:
                process_prediction.delay(prediction.id)
            else:
                flash("error encountered")

    return redirect(url_for("index"))
