"""
Backend server implementation for the Automated Diagnosis System
"""
__version__ = "0.0.1"

import os
from flask import Flask, abort


from typing import Any, Optional, Mapping

from pymongo.errors import ServerSelectionTimeoutError

from ads.db import db


def create_app(test_config: Optional[Mapping[str, Any]] = None):
    """
    Flask application factory
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", MONGO_URI="mongodb://dev:dev@mongo/ads")

    if not test_config:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/healthz")
    def health_check():
        try:
            resp = db.command("ping")
        except Exception:
            abort(503)
        else:
            if resp.get("ok") == 1.0:
                return "200"
            else:
                abort(503)

    return app
