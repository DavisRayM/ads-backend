"""
Backend server implementation for the Automated Diagnosis System
"""
__version__ = "0.0.1"

import os
from typing import Any, Mapping, Optional

from celery.app import Celery
from celery.app.task import Task
from flask import Flask, abort

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
        app.config.from_pyfile("config.py", silent=True)
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
            resp = get_db().command("ping")
        except Exception:
            abort(503)
        else:
            if resp.get("ok") == 1.0:
                return "200"
            else:
                abort(503)

    if app.config.get("CELERY"):
        celery_init(app)
    # Register blueprints
    from .auth import bp

    app.register_blueprint(bp)
    from .prediction import bp

    app.register_blueprint(bp)

    return app
