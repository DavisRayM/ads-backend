import os

from flask import Blueprint, current_app, flash, g, redirect, request, url_for
from werkzeug.utils import secure_filename

from ads.auth import login_required
from ads.db import add_prediction

bp = Blueprint("prediction", __name__, url_prefix="/predict")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@bp.route(
    "/request",
    methods=(
        "POST",
        "GET",
    ),
)
@login_required
def request_prediction():
    if request.method == "POST":
        if "file" not in request.files:
            flash("no file uploaded")
            return redirect(url_for("health_check"))

        file = request.files["file"]
        if file.filename == "":
            flash("no selected file")
            return redirect(url_for("health_check"))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = (
                f"{os.path.join(current_app.config.get('UPLOAD_FOLDER'), filename)}"
            )
            file.save(file_path)
            add_prediction(g._user["username"], file_path)

            return redirect(url_for("health_check", name=filename))

    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """
