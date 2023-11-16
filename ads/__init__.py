"""
Backend server implementation for the Automated Diagnosis System
"""
__version__ = "0.0.1"

import os
from typing import Any, Mapping, Optional

from celery.app import Celery
from celery.app.task import Task
from flask import Flask, abort, render_template

from ads.db import get_db


def celery_init(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.name, task_cls=FlaskTask, broker=app.config["CELERY"].get("broker_url")
    )
    celery_app.conf.update(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app(test_config: Optional[Mapping[str, Any]] = None):
    """
    Flask application factory
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        UPLOAD_FOLDER=f"{app.instance_path}/media",
        ALLOWED_EXTENSIONS={"png", "jpg", "jpeg"},
    )

    if not test_config:
        app.config.from_object("ads.default_settings.Settings")
        app.config.from_pyfile("local_settings.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config["UPLOAD_FOLDER"])
    except OSError:
        pass

    @app.route("/healthz")
    def health_check():
        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        except Exception:
            abort(503)
        else:
            return "OK"

    @app.route("/")
    def index():
        """
        Home page
        """
        return render_template("index.html")

    @app.route("/ourteam")
    def team_page():
        """
        Our team page
        """
        return render_template("ourteam.html")

    from . import db

    db.init_app(app)

    if app.config.get("CELERY"):
        celery_init(app)
    # Register blueprints
    from .auth import bp

    app.register_blueprint(bp)
    from .prediction import bp

    app.register_blueprint(bp)

    return app
